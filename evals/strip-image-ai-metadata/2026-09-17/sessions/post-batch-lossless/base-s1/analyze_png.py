#!/usr/bin/env python3
import sys
import struct

def analyze_png(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        print("Not a PNG file")
        return
    
    pos = 8
    print(f"Analyzing: {path}")
    print(f"File size: {len(data)} bytes\n")
    
    while pos < len(data):
        if pos + 8 > len(data):
            break
            
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        
        total_size = 4 + 4 + length + 4
        
        if pos + total_size > len(data):
            break
        
        print(f"Chunk: {chunk_type.decode('ascii', errors='replace')} - {length} bytes")
        
        pos += total_size
        
        if chunk_type == b'IEND':
            break
    
    print(f"\nEnd position: {pos}, File size: {len(data)}")

if __name__ == "__main__":
    analyze_png(sys.argv[1])
