import struct

def analyze_jpeg(filepath):
    """Analyze JPEG structure"""
    with open(filepath, 'rb') as f:
        # Check JPEG signature
        soi = f.read(2)
        print(f"Start: {soi.hex()}")
        
        count = 0
        while count < 50:  # Limit iterations
            try:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                    
                if marker[0] != 0xff:
                    print(f"Invalid marker: {marker.hex()}")
                    break
                
                marker_name = f"0xFF{marker[1]:02X}"
                
                # End of image
                if marker[1] == 0xd9:
                    print(f"{marker_name} - EOI (End of Image)")
                    break
                
                # Standalone markers (no length field)
                if marker[1] in [0x00, 0x01] or (0xd0 <= marker[1] <= 0xd7):
                    print(f"{marker_name} - Standalone")
                    continue
                
                # SOS (Start of Scan) - followed by image data
                if marker[1] == 0xda:
                    length_bytes = f.read(2)
                    length = struct.unpack('>H', length_bytes)[0]
                    print(f"{marker_name} - SOS (Start of Scan), length={length}")
                    f.seek(length - 2, 1)
                    # After SOS comes compressed image data, skip to EOI
                    print("  [Skipping compressed image data...]")
                    break
                
                # Segments with length
                length_bytes = f.read(2)
                if len(length_bytes) < 2:
                    break
                length = struct.unpack('>H', length_bytes)[0]
                
                # Read first few bytes of segment
                current_pos = f.tell()
                preview = f.read(min(20, length - 2))
                f.seek(current_pos)
                
                segment_data = f.read(length - 2)
                
                print(f"{marker_name} - length={length}, preview={preview[:20].hex()}")
                
                count += 1
                        
            except Exception as e:
                print(f"Error: {e}")
                break

print("=== ORIGINAL ===")
analyze_jpeg('queue/portrait_final.jpg')

print("\n=== CLEANED ===")
analyze_jpeg('output/portrait_final.jpg')

