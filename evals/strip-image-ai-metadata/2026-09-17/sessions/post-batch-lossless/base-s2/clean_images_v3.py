import os
import struct

def clean_png(input_path, output_path):
    """Remove C2PA and metadata chunks from PNG while preserving image data"""
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            # Write PNG signature
            signature = f_in.read(8)
            f_out.write(signature)
            
            # Critical chunks we must keep for the image to work
            critical_chunks = [b'IHDR', b'PLTE', b'IDAT', b'IEND']
            # Ancillary chunks that affect rendering
            keep_chunks = critical_chunks + [b'tRNS', b'gAMA', b'sRGB', b'iCCP', b'pHYs', b'sBIT']
            
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
                    # Skip C2PA chunks (caBX, caMA, caMS) and metadata (tEXt, iTXt, zTXt, eXIf)
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
    """Remove only C2PA and XMP metadata from JPEG"""
    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    
    with open(output_path, 'wb') as f_out:
        pos = 0
        
        # Write SOI
        if data[pos:pos+2] != b'\xff\xd8':
            raise ValueError("Not a valid JPEG")
        f_out.write(data[pos:pos+2])
        pos += 2
        
        while pos < len(data):
            # Check for marker
            if data[pos] != 0xff:
                # Not a marker, must be image data or error
                # Write rest of file
                f_out.write(data[pos:])
                break
            
            marker = data[pos:pos+2]
            
            # EOI
            if marker[1] == 0xd9:
                f_out.write(marker)
                break
            
            # Standalone markers
            if marker[1] in [0x00, 0x01] or (0xd0 <= marker[1] <= 0xd7):
                f_out.write(marker)
                pos += 2
                continue
            
            # SOS - start of scan, followed by compressed data
            if marker[1] == 0xda:
                # Write SOS marker and its segment
                length = struct.unpack('>H', data[pos+2:pos+4])[0]
                f_out.write(data[pos:pos+2+length])
                pos += 2 + length
                
                # Now comes compressed image data until we hit a marker
                # Find next marker (0xFF followed by non-0x00)
                while pos < len(data):
                    if data[pos] == 0xff and pos + 1 < len(data) and data[pos+1] != 0x00:
                        # Found next marker, don't consume it
                        break
                    f_out.write(data[pos:pos+1])
                    pos += 1
                continue
            
            # Regular segment with length
            if pos + 4 > len(data):
                break
                
            length = struct.unpack('>H', data[pos+2:pos+4])[0]
            segment_data = data[pos+4:pos+2+length]
            
            # Check if this segment should be skipped
            skip = False
            
            # APP11 (often used for C2PA)
            if marker[1] == 0xeb:
                skip = True
            
            # Check for C2PA/XMP content
            if len(segment_data) > 0:
                check_bytes = segment_data[:100].lower()
                if (b'c2pa' in check_bytes or 
                    b'contentcredentials' in check_bytes or
                    b'http://ns.adobe.com/xap' in segment_data or
                    b'http://ns.adobe.com/c2pa' in segment_data):
                    skip = True
            
            if not skip:
                # Write this segment
                f_out.write(data[pos:pos+2+length])
            
            pos += 2 + length

# Create output directory
os.makedirs('output', exist_ok=True)

# Process all files
queue_dir = 'queue'
output_dir = 'output'

for filename in sorted(os.listdir(queue_dir)):
    filepath = os.path.join(queue_dir, filename)
    if not os.path.isfile(filepath):
        continue
    
    output_path = os.path.join(output_dir, filename)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.png':
            clean_png(filepath, output_path)
            print(f"✓ {filename}")
        elif ext in ['.jpg', '.jpeg']:
            clean_jpeg(filepath, output_path)
            print(f"✓ {filename}")
    except Exception as e:
        print(f"✗ {filename}: {e}")

