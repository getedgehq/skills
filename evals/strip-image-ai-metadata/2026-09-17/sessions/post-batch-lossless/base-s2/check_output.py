import os
import struct

def check_png_c2pa(filepath):
    """Check PNG file for C2PA chunks"""
    with open(filepath, 'rb') as f:
        # Check PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            return False
        
        # Read chunks
        while True:
            try:
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    break
                    
                length = struct.unpack('>I', length_bytes)[0]
                chunk_type = f.read(4)
                
                if not chunk_type:
                    break
                
                # Check for C2PA-related chunks
                if chunk_type in [b'caBX', b'caMA', b'caMS']:
                    return True
                    
                # Skip chunk data and CRC
                f.seek(length + 4, 1)
                
            except:
                break
    
    return False

def check_jpeg_c2pa(filepath):
    """Check JPEG file for C2PA metadata"""
    with open(filepath, 'rb') as f:
        # Check JPEG signature
        if f.read(2) != b'\xff\xd8':
            return False
        
        while True:
            try:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                    
                if marker[0] != 0xff:
                    break
                
                # End of image
                if marker[1] == 0xd9:
                    break
                
                # Segments with length
                if marker[1] not in [0x00, 0x01] and not (0xd0 <= marker[1] <= 0xd7):
                    length_bytes = f.read(2)
                    if len(length_bytes) < 2:
                        break
                    length = struct.unpack('>H', length_bytes)[0]
                    
                    # APP11 segment used for C2PA
                    if marker[1] == 0xeb:
                        return True
                        
                    # Check segment data for C2PA markers
                    segment_data = f.read(min(length - 2, 1000))
                    if b'c2pa' in segment_data.lower() or b'contentcredentials' in segment_data.lower():
                        return True
                    # Skip rest if we didn't read it all
                    if length - 2 > 1000:
                        f.seek(length - 2 - 1000, 1)
            except Exception as e:
                break
    
    return False

def check_file(filepath):
    """Check if file has C2PA content credentials"""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.png':
        has_c2pa = check_png_c2pa(filepath)
    elif ext in ['.jpg', '.jpeg']:
        has_c2pa = check_jpeg_c2pa(filepath)
    else:
        has_c2pa = False
    
    return has_c2pa

# Check all files in output
output_dir = 'output'
for filename in sorted(os.listdir(output_dir)):
    filepath = os.path.join(output_dir, filename)
    if os.path.isfile(filepath):
        has_c2pa = check_file(filepath)
        print(f"{filename}: {'HAS C2PA' if has_c2pa else 'Clean'}")

