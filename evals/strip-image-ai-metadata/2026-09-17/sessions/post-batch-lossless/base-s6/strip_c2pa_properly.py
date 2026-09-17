#!/usr/bin/env python3
"""
Strip C2PA/Content Credentials from PNG files without re-encoding.
Removes caBX (C2PA Box) chunks while preserving all image data and other metadata.
"""
import struct
import sys
import os

def strip_c2pa_from_png(input_path, output_path):
    """Strip C2PA/JUMBF chunks from PNG without re-encoding"""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f"Not a valid PNG file: {input_path}")
    
    # Keep signature
    output = bytearray(data[:8])
    pos = 8
    stripped_count = 0
    stripped_bytes = 0
    
    while pos < len(data):
        if pos + 8 > len(data):
            # Not enough data for a chunk header, copy rest
            output.extend(data[pos:])
            break
            
        # Read chunk length and type
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        # Total chunk size: 4 (length) + 4 (type) + length (data) + 4 (CRC)
        chunk_size = 12 + length
        
        if pos + chunk_size > len(data):
            # Incomplete chunk, just copy the rest
            output.extend(data[pos:])
            break
        
        # Skip caBX chunks (C2PA Box) which contain JUMBF/C2PA data
        if chunk_type == b'caBX':
            stripped_count += 1
            stripped_bytes += chunk_size
            print(f"  Stripped caBX chunk: {length:,} bytes of C2PA data")
            pos += chunk_size
            continue
        
        # Copy all other chunks unchanged
        output.extend(data[pos:pos+chunk_size])
        pos += chunk_size
    
    # Write output
    with open(output_path, 'wb') as f:
        f.write(output)
    
    orig_size = len(data)
    new_size = len(output)
    
    print(f"✓ Processed: {os.path.basename(input_path)}")
    print(f"  Original: {orig_size:,} bytes")
    print(f"  Cleaned:  {new_size:,} bytes") 
    print(f"  Removed:  {stripped_bytes:,} bytes ({stripped_count} C2PA chunks)")
    print(f"  Output: {output_path}")
    
    return stripped_count > 0

def main():
    input_file = "queue/carousel_01.png"
    output_file = "output/carousel_01.png"
    
    if not os.path.exists(input_file):
        print(f"ERROR: {input_file} not found!")
        print(f"\nPlease restore carousel_01.png to the queue/ directory first.")
        print(f"This is the file that contained C2PA metadata from OpenAI ChatGPT.")
        sys.exit(1)
    
    os.makedirs("output", exist_ok=True)
    
    print("Stripping Content Credentials from carousel_01.png...")
    print()
    
    had_c2pa = strip_c2pa_from_png(input_file, output_file)
    
    print()
    if had_c2pa:
        print("✓ Content Credentials successfully removed!")
        print("  The image data is unchanged - no re-encoding occurred.")
    else:
        print("⚠ No Content Credentials found (file may already be clean)")
        print("  File copied to output anyway.")

if __name__ == '__main__':
    main()
