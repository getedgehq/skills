#!/usr/bin/env python3
import sys
import struct

def strip_c2pa_png(input_path, output_path):
    """Strip C2PA chunks from PNG while preserving image data and basic metadata"""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a PNG file")
    
    output = bytearray(data[:8])  # Keep PNG signature
    pos = 8
    removed_chunks = []
    
    while pos < len(data):
        if pos + 8 > len(data):
            break
            
        # Read chunk length and type
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        # Total chunk size: 4 (length) + 4 (type) + length (data) + 4 (CRC)
        total_size = 4 + 4 + length + 4
        
        if pos + total_size > len(data):
            break
        
        chunk_data = data[pos:pos+total_size]
        
        # Remove C2PA-related chunks
        # caBX = Content Authenticity Box (C2PA)
        # Also check iTXt chunks for C2PA data
        skip = False
        
        if chunk_type == b'caBX':
            removed_chunks.append(f"caBX ({length} bytes)")
            skip = True
        elif chunk_type == b'iTXt':
            # Check if this iTXt contains C2PA data
            text_data = data[pos+8:pos+8+length]
            if b'c2pa' in text_data.lower() or b'jumbf' in text_data.lower():
                removed_chunks.append(f"iTXt with C2PA ({length} bytes)")
                skip = True
        
        if not skip:
            output.extend(chunk_data)
        
        pos += total_size
        
        # IEND is the last chunk
        if chunk_type == b'IEND':
            break
    
    with open(output_path, 'wb') as f:
        f.write(output)
    
    if removed_chunks:
        print(f"Removed chunks: {', '.join(removed_chunks)}")
    else:
        print("No C2PA chunks found")
    print(f"Cleaned PNG saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: strip_c2pa.py input.png output.png")
        sys.exit(1)
    
    strip_c2pa_png(sys.argv[1], sys.argv[2])
