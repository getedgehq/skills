#!/usr/bin/env python3
"""
Quick checker for C2PA/Content Credentials in images.
Usage: python3 check_c2pa.py <image_file_or_directory>
"""
import struct
import sys
import os

def check_png_for_c2pa(filepath):
    """Check if PNG has caBX chunks (C2PA data)"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return None, "Not a PNG file"
        
        pos = 8
        cabx_chunks = []
        
        while pos < len(data):
            if pos + 8 > len(data):
                break
                
            length = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8]
            chunk_size = 12 + length
            
            if pos + chunk_size > len(data):
                break
            
            if chunk_type == b'caBX':
                cabx_chunks.append(length)
            
            pos += chunk_size
        
        if cabx_chunks:
            total = sum(cabx_chunks)
            return True, f"Found {len(cabx_chunks)} caBX chunk(s), {total:,} bytes of C2PA data"
        else:
            return False, "No C2PA data found"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def check_jpeg_for_c2pa(filepath):
    """Check if JPEG has C2PA segments"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if data[:2] != b'\xff\xd8':
            return None, "Not a JPEG file"
        
        # Look for APP11 markers (0xFFEB) which can contain C2PA
        # or search for "c2pa" string in the data
        if b'c2pa' in data or b'C2PA' in data:
            return True, "Possible C2PA data detected"
        else:
            return False, "No obvious C2PA data found"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def check_file(filepath):
    """Check any image file for C2PA"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext in ['.png']:
        return check_png_for_c2pa(filepath)
    elif ext in ['.jpg', '.jpeg']:
        return check_jpeg_for_c2pa(filepath)
    else:
        return None, "Unsupported format (only PNG/JPEG)"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_c2pa.py <file_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        files = [path]
    elif os.path.isdir(path):
        files = []
        for f in os.listdir(path):
            fpath = os.path.join(path, f)
            if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                files.append(fpath)
        files.sort()
    else:
        print(f"Error: {path} not found")
        sys.exit(1)
    
    print("Content Credentials Check")
    print("=" * 70)
    print()
    
    has_c2pa = []
    clean = []
    errors = []
    
    for filepath in files:
        basename = os.path.basename(filepath)
        has_c2pa_data, message = check_file(filepath)
        
        if has_c2pa_data is True:
            print(f"✗ {basename}")
            print(f"  {message}")
            has_c2pa.append(basename)
        elif has_c2pa_data is False:
            print(f"✓ {basename}")
            print(f"  {message}")
            clean.append(basename)
        else:
            print(f"? {basename}")
            print(f"  {message}")
            errors.append(basename)
        print()
    
    print("=" * 70)
    print(f"Total files checked: {len(files)}")
    print(f"  With C2PA: {len(has_c2pa)}")
    print(f"  Clean: {len(clean)}")
    if errors:
        print(f"  Errors: {len(errors)}")

if __name__ == '__main__':
    main()
