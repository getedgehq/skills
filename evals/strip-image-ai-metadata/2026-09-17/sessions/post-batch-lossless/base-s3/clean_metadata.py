#!/usr/bin/env python3
"""
Remove Content Credentials (C2PA) metadata from images while preserving visual quality.
C2PA data is stored in specific chunks/segments that can be identified and removed.
"""
import os
import struct
from pathlib import Path

def check_and_clean_png(input_path, output_path):
    """
    Remove C2PA data from PNG files.
    C2PA uses the 'caBX' chunk type in PNG files.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return False, "Not a valid PNG"
    
    found_c2pa = False
    cleaned_data = bytearray(data[:8])  # Keep PNG signature
    pos = 8
    
    while pos < len(data):
        if pos + 8 > len(data):
            break
            
        # Read chunk length and type
        chunk_length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        # Check for C2PA chunks (caBX) and other potential C2PA markers
        if chunk_type in [b'caBX', b'caSG', b'caHD']:
            found_c2pa = True
            print(f"  Found C2PA chunk: {chunk_type.decode('latin-1')}")
            # Skip this chunk (length + type + data + CRC)
            pos += 12 + chunk_length
        else:
            # Keep this chunk
            chunk_total = 12 + chunk_length  # 4(length) + 4(type) + data + 4(CRC)
            cleaned_data.extend(data[pos:pos+chunk_total])
            pos += chunk_total
            
            # Break if we hit IEND
            if chunk_type == b'IEND':
                break
    
    with open(output_path, 'wb') as f:
        f.write(cleaned_data)
    
    return found_c2pa, "PNG cleaned"

def check_and_clean_jpeg(input_path, output_path):
    """
    Remove C2PA data from JPEG files.
    C2PA uses APP11 segments with 'c2pa' marker in JPEG files.
    Also check for JUMBF boxes which contain C2PA data.
    """
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check JPEG signature
    if data[:2] != b'\xff\xd8':
        return False, "Not a valid JPEG"
    
    found_c2pa = False
    cleaned_data = bytearray(data[:2])  # Keep JPEG SOI marker
    pos = 2
    
    while pos < len(data) - 1:
        # Look for marker
        if data[pos] != 0xFF:
            # If we're past markers, copy rest of file (image data)
            cleaned_data.extend(data[pos:])
            break
        
        marker = data[pos+1]
        
        # Handle markers without length field
        if marker in [0x00, 0x01] or (0xD0 <= marker <= 0xD7):
            cleaned_data.extend(data[pos:pos+2])
            pos += 2
            continue
        
        # SOS marker - start of scan, rest is image data
        if marker == 0xDA:
            cleaned_data.extend(data[pos:])
            break
        
        # EOI marker
        if marker == 0xD9:
            cleaned_data.extend(data[pos:pos+2])
            break
        
        if pos + 4 > len(data):
            break
            
        # Read segment length
        seg_length = struct.unpack('>H', data[pos+2:pos+4])[0]
        segment_data = data[pos+4:pos+2+seg_length]
        
        # Check for C2PA markers
        skip_segment = False
        
        # APP11 with c2pa marker
        if marker == 0xEB:  # APP11
            if segment_data.startswith(b'c2pa'):
                found_c2pa = True
                skip_segment = True
                print(f"  Found C2PA in APP11 segment")
        
        # APP2 with MPF (Multi-Picture Format) that might contain C2PA
        if marker == 0xE2:  # APP2
            if b'c2pa' in segment_data or b'JUMBF' in segment_data:
                found_c2pa = True
                skip_segment = True
                print(f"  Found C2PA in APP2 segment")
        
        # Check other APP segments for c2pa markers
        if 0xE0 <= marker <= 0xEF:  # APP0-APP15
            if b'c2pa' in segment_data or b'JUMBF' in segment_data or b'urn:uuid' in segment_data:
                # Check more carefully - could be legitimate data
                if b'c2pa' in segment_data[:50] or b'contentauth' in segment_data:
                    found_c2pa = True
                    skip_segment = True
                    print(f"  Found C2PA in APP{marker-0xE0} segment")
        
        if not skip_segment:
            # Keep this segment
            cleaned_data.extend(data[pos:pos+2+seg_length])
        
        pos += 2 + seg_length
    
    with open(output_path, 'wb') as f:
        f.write(cleaned_data)
    
    return found_c2pa, "JPEG cleaned"

def process_image(input_path, output_path):
    """Process an image file to remove C2PA metadata."""
    ext = input_path.suffix.lower()
    
    if ext == '.png':
        return check_and_clean_png(input_path, output_path)
    elif ext in ['.jpg', '.jpeg']:
        return check_and_clean_jpeg(input_path, output_path)
    else:
        return False, f"Unsupported format: {ext}"

def main():
    queue_dir = Path('queue')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for img_file in sorted(queue_dir.iterdir()):
        if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            print(f"\nProcessing: {img_file.name}")
            output_path = output_dir / img_file.name
            
            had_c2pa, message = process_image(img_file, output_path)
            results.append((img_file.name, had_c2pa, message))
            
            # Verify file sizes
            orig_size = img_file.stat().st_size
            new_size = output_path.stat().st_size
            size_diff = orig_size - new_size
            
            print(f"  Original: {orig_size:,} bytes")
            print(f"  Cleaned:  {new_size:,} bytes")
            if size_diff > 0:
                print(f"  Removed:  {size_diff:,} bytes")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for filename, had_c2pa, message in results:
        status = "✓ HAD C2PA METADATA" if had_c2pa else "✗ No C2PA found"
        print(f"{filename:30s} - {status}")
    
    print("\nAll cleaned files saved to output/")

if __name__ == '__main__':
    main()
