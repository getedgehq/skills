import sys
import struct

def strip_png_chunks(input_path, output_path):
    """
    Strip C2PA and metadata chunks from PNG while preserving image data exactly.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Verify PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a valid PNG file")
    
    # Start with PNG signature
    output_data = bytearray(data[:8])
    pos = 8
    
    chunks_to_remove = ['jumb', 'cICP', 'eXIf', 'tEXt', 'iTXt', 'zTXt']
    
    # Parse and filter chunks
    while pos < len(data):
        if pos + 8 > len(data):
            break
            
        # Read chunk length and type
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        # Total chunk size: length + type (4) + data (length) + CRC (4)
        chunk_size = 4 + 4 + length + 4
        
        if pos + chunk_size > len(data):
            break
        
        chunk_type_str = chunk_type.decode('latin-1', errors='ignore')
        
        # Check if chunk should be removed
        should_keep = True
        for remove_chunk in chunks_to_remove:
            if chunk_type_str.lower() == remove_chunk.lower():
                should_keep = False
                print(f"Removing chunk: {chunk_type_str} ({length} bytes)")
                break
        
        # Also check chunk data for c2pa content
        if should_keep and length > 0 and length < 100000:
            chunk_data = data[pos+8:pos+8+length]
            if b'c2pa' in chunk_data.lower() or b'jumb' in chunk_data.lower():
                print(f"Removing chunk {chunk_type_str} containing C2PA data ({length} bytes)")
                should_keep = False
        
        if should_keep:
            output_data.extend(data[pos:pos+chunk_size])
        
        pos += chunk_size
        
        # Stop after IEND
        if chunk_type_str == 'IEND':
            break
    
    with open(output_path, 'wb') as f:
        f.write(output_data)
    
    print(f"PNG cleaned: {input_path} -> {output_path}")

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
    removed_segments = []
    
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
        segment_name = f"APP{marker - 0xe0}" if 0xe0 <= marker <= 0xef else f"Marker 0x{marker:02x}"
        
        # APP1 markers for XMP, EXIF
        if marker == 0xe1:  # APP1
            if b'http://ns.adobe.com/xap/1.0/' in segment_data:
                removed_segments.append(f"XMP ({seg_length} bytes)")
                should_keep = False
            elif b'c2pa' in segment_data.lower():
                removed_segments.append(f"C2PA in {segment_name} ({seg_length} bytes)")
                should_keep = False
        
        # APP2 markers
        elif marker == 0xe2:  # APP2
            if b'c2pa' in segment_data.lower() or b'jumb' in segment_data.lower():
                removed_segments.append(f"C2PA in APP2 ({seg_length} bytes)")
                should_keep = False
        
        # APP3-APP15
        elif 0xe3 <= marker <= 0xef:
            # Check for C2PA in any APP segment
            if b'c2pa' in segment_data.lower() or b'jumb' in segment_data.lower():
                removed_segments.append(f"C2PA in {segment_name} ({seg_length} bytes)")
                should_keep = False
        
        # APP13 for Photoshop data
        if marker == 0xed:  # APP13
            if b'Adobe' in segment_data or b'Photoshop' in segment_data:
                removed_segments.append(f"Photoshop data ({seg_length} bytes)")
                should_keep = False
        
        # COM comments
        if marker == 0xfe:
            if b'c2pa' in segment_data.lower():
                removed_segments.append(f"C2PA in comment ({seg_length} bytes)")
                should_keep = False
        
        if should_keep:
            output_data.extend(segment_data)
        
        pos = seg_end
    
    with open(output_path, 'wb') as f:
        f.write(output_data)
    
    if removed_segments:
        for seg in removed_segments:
            print(f"Removed: {seg}")
    print(f"JPEG cleaned: {input_path} -> {output_path}")

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
