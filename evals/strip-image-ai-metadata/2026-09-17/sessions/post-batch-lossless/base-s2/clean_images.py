import os
import struct
import shutil

def clean_png(input_path, output_path):
    """Remove C2PA and other metadata chunks from PNG while preserving image data"""
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            # Write PNG signature
            signature = f_in.read(8)
            f_out.write(signature)
            
            # Critical chunks we must keep for the image to work
            critical_chunks = [b'IHDR', b'PLTE', b'IDAT', b'IEND']
            # Ancillary chunks that affect rendering
            keep_chunks = critical_chunks + [b'tRNS', b'gAMA', b'sRGB', b'iCCP']
            
            while True:
                try:
                    length_bytes = f_in.read(4)
                    if len(length_bytes) < 4:
                        break
                        
                    length = struct.unpack('>I', length_bytes)[0]
                    chunk_type = f_in.read(4)
                    
                    if not chunk_type:
                        break
                    
                    chunk_data = f_in.read(length)
                    crc = f_in.read(4)
                    
                    # Keep only essential and rendering-related chunks
                    if chunk_type in keep_chunks:
                        f_out.write(length_bytes)
                        f_out.write(chunk_type)
                        f_out.write(chunk_data)
                        f_out.write(crc)
                    
                    # Stop after IEND
                    if chunk_type == b'IEND':
                        break
                        
                except Exception as e:
                    print(f"Error processing PNG: {e}")
                    break

def clean_jpeg(input_path, output_path):
    """Remove C2PA and metadata from JPEG while preserving image data"""
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            # Write JPEG start marker
            soi = f_in.read(2)
            if soi != b'\xff\xd8':
                raise ValueError("Not a valid JPEG")
            f_out.write(soi)
            
            while True:
                try:
                    marker = f_in.read(2)
                    if len(marker) < 2:
                        break
                        
                    if marker[0] != 0xff:
                        break
                    
                    # End of image - write and finish
                    if marker[1] == 0xd9:
                        f_out.write(marker)
                        break
                    
                    # Standalone markers (no length field)
                    if marker[1] in [0x00, 0x01] or (0xd0 <= marker[1] <= 0xd7):
                        f_out.write(marker)
                        continue
                    
                    # Segments with length
                    length_bytes = f_in.read(2)
                    if len(length_bytes) < 2:
                        break
                    length = struct.unpack('>H', length_bytes)[0]
                    segment_data = f_in.read(length - 2)
                    
                    # Skip metadata segments but keep essential ones
                    # APP0 (JFIF), APP2 (ICC), SOFn, DHT, DQT, DRI, SOS, COM
                    skip_markers = [
                        0xe1,  # APP1 - EXIF/XMP
                        0xeb,  # APP11 - C2PA
                        0xec,  # APP12
                        0xed,  # APP13 - IPTC
                        0xee,  # APP14 (sometimes)
                    ]
                    
                    # Check if segment contains C2PA data
                    has_c2pa = (b'c2pa' in segment_data.lower() or 
                               b'contentcredentials' in segment_data.lower() or
                               b'adobe' in segment_data.lower() or
                               b'xmp' in segment_data.lower())
                    
                    if marker[1] in skip_markers or has_c2pa:
                        # Skip this segment
                        continue
                    else:
                        # Keep this segment
                        f_out.write(marker)
                        f_out.write(length_bytes)
                        f_out.write(segment_data)
                        
                except Exception as e:
                    print(f"Error processing JPEG: {e}")
                    break

# Create output directory
os.makedirs('output', exist_ok=True)

# Process all files
queue_dir = 'queue'
output_dir = 'output'

results = []

for filename in sorted(os.listdir(queue_dir)):
    filepath = os.path.join(queue_dir, filename)
    if not os.path.isfile(filepath):
        continue
    
    output_path = os.path.join(output_dir, filename)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.png':
            clean_png(filepath, output_path)
            results.append(f"✓ {filename} - cleaned")
        elif ext in ['.jpg', '.jpeg']:
            clean_jpeg(filepath, output_path)
            results.append(f"✓ {filename} - cleaned")
        else:
            shutil.copy2(filepath, output_path)
            results.append(f"✓ {filename} - copied")
    except Exception as e:
        results.append(f"✗ {filename} - error: {e}")

for result in results:
    print(result)

