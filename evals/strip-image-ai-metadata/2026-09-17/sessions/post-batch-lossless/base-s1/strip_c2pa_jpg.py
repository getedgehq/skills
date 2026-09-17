#!/usr/bin/env python3
import sys
import struct

def strip_c2pa_jpeg(input_path, output_path):
    """Strip C2PA data from JPEG while preserving image"""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check JPEG signature
    if data[:2] != b'\xff\xd8':
        raise ValueError("Not a JPEG file")
    
    output = bytearray()
    pos = 0
    removed_segments = []
    
    while pos < len(data):
        # Check for marker
        if data[pos] != 0xff:
            # If we're not at a marker, something's wrong or we hit image data
            # Copy rest of file
            output.extend(data[pos:])
            break
        
        marker = data[pos+1]
        
        # SOI (Start of Image) and EOI (End of Image) have no length
        if marker == 0xd8 or marker == 0xd9:
            output.extend(data[pos:pos+2])
            pos += 2
            continue
        
        # RST markers (0xd0-0xd7) and SOI have no length
        if 0xd0 <= marker <= 0xd7:
            output.extend(data[pos:pos+2])
            pos += 2
            continue
        
        # TEM marker
        if marker == 0x01:
            output.extend(data[pos:pos+2])
            pos += 2
            continue
        
        # SOS (Start of Scan) - after this comes compressed image data
        if marker == 0xda:
            # Copy SOS marker and its data, then the rest of the file
            if pos + 4 > len(data):
                break
            length = struct.unpack('>H', data[pos+2:pos+4])[0]
            # Copy SOS and everything after
            output.extend(data[pos:])
            break
        
        # All other markers have a length field
        if pos + 4 > len(data):
            break
        
        length = struct.unpack('>H', data[pos+2:pos+4])[0]
        segment_size = 2 + length  # marker (2 bytes) + length field + data
        
        if pos + segment_size > len(data):
            break
        
        segment_data = data[pos:pos+segment_size]
        
        # Check for C2PA data
        # APP11 (0xEB) is commonly used for C2PA/JUMBF
        # Also check APP2 (0xE2) and others for c2pa mentions
        skip = False
        
        if marker == 0xeb:  # APP11 - often used for JUMBF/C2PA
            removed_segments.append(f"APP11/JUMBF ({length} bytes)")
            skip = True
        elif 0xe0 <= marker <= 0xef:  # APP markers
            # Check if segment contains C2PA identifiers
            segment_content = data[pos+4:pos+segment_size]
            if b'c2pa' in segment_content.lower() or b'jumbf' in segment_content or b'urn:uuid' in segment_content:
                removed_segments.append(f"APP{marker-0xe0} with C2PA ({length} bytes)")
                skip = True
        
        if not skip:
            output.extend(segment_data)
        
        pos += segment_size
    
    with open(output_path, 'wb') as f:
        f.write(output)
    
    if removed_segments:
        print(f"Removed segments: {', '.join(removed_segments)}")
    else:
        print("No C2PA segments found")
    print(f"Cleaned JPEG saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: strip_c2pa_jpg.py input.jpg output.jpg")
        sys.exit(1)
    
    strip_c2pa_jpeg(sys.argv[1], sys.argv[2])
