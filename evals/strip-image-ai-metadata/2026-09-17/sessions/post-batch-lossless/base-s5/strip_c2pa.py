import sys
from PIL import Image
import struct

def strip_png_chunks(input_path, output_path, chunks_to_remove=['cICP', 'jumb', 'JUMB']):
    """
    Strip specific chunks from PNG while preserving image data exactly.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Verify PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a valid PNG file")
    
    # Start with PNG signature
    output_data = bytearray(data[:8])
    pos = 8
    
    # Parse and filter chunks
    while pos < len(data):
        if pos + 8 > len(data):
            break
            
        # Read chunk length and type
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8].decode('latin-1')
        
        # Total chunk size: length + type (4) + data (length) + CRC (4)
        chunk_size = 4 + 4 + length + 4
        
        if pos + chunk_size > len(data):
            break
        
        # Keep chunk if it's not in the removal list
        # Also handle case-insensitive matching for JUMBF
        should_keep = True
        for remove_chunk in chunks_to_remove:
            if chunk_type.lower() == remove_chunk.lower():
                should_keep = False
                print(f"Removing chunk: {chunk_type} ({length} bytes)")
                break
        
        if should_keep:
            output_data.extend(data[pos:pos+chunk_size])
        
        pos += chunk_size
        
        # Stop after IEND
        if chunk_type == 'IEND':
            break
    
    with open(output_path, 'wb') as f:
        f.write(output_data)

def strip_jpeg_metadata(input_path, output_path):
    """
    Strip problematic metadata from JPEG while preserving image quality.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Verify JPEG signature
    if data[:2] != b'\xff\xd8':
        raise ValueError("Not a valid JPEG file")
    
    output_data = bytearray(b'\xff\xd8')  # Start with JPEG SOI
    pos = 2
    
    while pos < len(data):
        if data[pos] != 0xff:
            # Copy rest of the file (image data)
            output_data.extend(data[pos:])
            break
        
        marker = data[pos+1]
        
        # Handle special markers
        if marker == 0xd8:  # SOI
            pos += 2
            continue
        elif marker == 0xd9:  # EOI
            output_data.extend(data[pos:pos+2])
            break
        elif marker == 0x00 or (marker >= 0xd0 and marker <= 0xd7):  # Padding or RST
            output_data.extend(data[pos:pos+2])
            pos += 2
            continue
        elif marker == 0xda:  # SOS - Start of Scan, followed by image data
            # Copy SOS marker and everything after
            output_data.extend(data[pos:])
            break
        
        # Read segment length
        if pos + 4 > len(data):
            break
        
        seg_length = struct.unpack('>H', data[pos+2:pos+4])[0]
        seg_end = pos + 2 + seg_length
        
        if seg_end > len(data):
            break
        
        # Check if this is a problematic metadata segment
        segment_data = data[pos:seg_end]
        should_keep = True
        
        # APP1 markers for XMP, EXIF
        if marker == 0xe1:  # APP1
            if b'http://ns.adobe.com/xap/1.0/' in segment_data:
                print(f"Removing XMP metadata segment ({seg_length} bytes)")
                should_keep = False
            elif b'c2pa' in segment_data.lower():
                print(f"Removing C2PA metadata segment ({seg_length} bytes)")
                should_keep = False
            # Keep EXIF but check for problematic tags
            elif b'Exif\x00\x00' in segment_data:
                # For now, keep EXIF but we might need to filter it
                should_keep = True
        
        # APP2 markers for ICC, but also check for C2PA
        elif marker == 0xe2:  # APP2
            if b'c2pa' in segment_data.lower() or b'jumb' in segment_data.lower():
                print(f"Removing C2PA APP2 segment ({seg_length} bytes)")
                should_keep = False
        
        # APP13 for Photoshop data
        elif marker == 0xed:  # APP13
            if b'Adobe' in segment_data or b'Photoshop' in segment_data:
                print(f"Removing Photoshop metadata segment ({seg_length} bytes)")
                should_keep = False
        
        if should_keep:
            output_data.extend(segment_data)
        
        pos = seg_end
    
    with open(output_path, 'wb') as f:
        f.write(output_data)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python strip_c2pa.py input output")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if input_file.lower().endswith('.png'):
        strip_png_chunks(input_file, output_file)
    elif input_file.lower().endswith(('.jpg', '.jpeg')):
        strip_jpeg_metadata(input_file, output_file)
    else:
        print("Unsupported file format")
        sys.exit(1)
    
    print(f"Cleaned: {input_file} -> {output_file}")
