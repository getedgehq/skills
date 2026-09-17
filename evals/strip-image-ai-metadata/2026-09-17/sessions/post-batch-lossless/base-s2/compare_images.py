from PIL import Image
import os

print("Comparing original vs cleaned images...\n")

queue_dir = 'queue'
output_dir = 'output'

for filename in sorted(os.listdir(queue_dir)):
    orig_path = os.path.join(queue_dir, filename)
    clean_path = os.path.join(output_dir, filename)
    
    if not os.path.isfile(orig_path) or not os.path.isfile(clean_path):
        continue
    
    print(f"=== {filename} ===")
    
    # Open both images
    orig = Image.open(orig_path)
    clean = Image.open(clean_path)
    
    # Compare dimensions
    print(f"  Original: {orig.size} mode={orig.mode}")
    print(f"  Cleaned:  {clean.size} mode={clean.mode}")
    
    if orig.size != clean.size:
        print(f"  ⚠ WARNING: Size mismatch!")
    
    if orig.mode != clean.mode:
        print(f"  ⚠ WARNING: Mode mismatch!")
    
    # Compare pixel data
    orig_data = list(orig.getdata())
    clean_data = list(clean.getdata())
    
    if orig_data == clean_data:
        print(f"  ✓ Pixel data IDENTICAL")
    else:
        # Check if they're visually similar (allow for minor compression differences)
        differences = sum(1 for a, b in zip(orig_data, clean_data) if a != b)
        print(f"  ⚠ {differences} pixels differ (may be OK for JPEG)")
    
    orig_size = os.path.getsize(orig_path)
    clean_size = os.path.getsize(clean_path)
    reduction = ((orig_size - clean_size) / orig_size) * 100
    
    print(f"  File size: {orig_size} → {clean_size} bytes ({reduction:.1f}% reduction)")
    print()

