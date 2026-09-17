#!/usr/bin/env python3
import struct
import sys

def strip_c2pa_from_png(input_path, output_path):
    """Strip C2PA/JUMBF chunks from PNG without re-encoding"""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Check PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Not a valid PNG file")
    
    # Keep signature
    output = bytearray(data[:8])
    pos = 8
    
    while pos < len(data):
        if pos + 8 > len(data):
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
        
        # Skip caBX chunks (C2PA Box) which contain JUMBF
        if chunk_type == b'caBX':
            print(f"Stripped caBX chunk ({length} bytes)")
            pos += chunk_size
            continue
        
        # Copy all other chunks
        output.extend(data[pos:pos+chunk_size])
        pos += chunk_size
    
    with open(output_path, 'wb') as f:
        f.write(output)
    
    print(f"Processed: {input_path} -> {output_path}")

if __name__ == '__main__':
    strip_c2pa_from_png(sys.argv[1], sys.argv[2])
