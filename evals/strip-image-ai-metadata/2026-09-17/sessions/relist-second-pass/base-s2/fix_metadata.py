#!/usr/bin/env python3
import piexif
from PIL import Image, PngImagePlugin
import os

def clean_and_add_credit_jpg(filepath):
    """Remove all metadata and add back only Artist and Copyright for JPG"""
    # Open image
    img = Image.open(filepath)
    
    # Get image data without metadata
    img_clean = img.copy()
    
    # Create minimal EXIF with only Artist and Copyright
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Artist: b"Roos Keramiek",
            piexif.ImageIFD.Copyright: b"(c) 2026 Roos Keramiek"
        }
    }
    
    exif_bytes = piexif.dump(exif_dict)
    
    # Save with only the credit info
    img_clean.save(filepath, quality=95, exif=exif_bytes)
    print(f"✓ Cleaned {filepath} and added credit")

def clean_and_add_credit_png(filepath):
    """Remove all metadata and add back only Author and Copyright for PNG"""
    img = Image.open(filepath)
    
    # Create clean copy
    img_clean = img.copy()
    
    # PNG metadata as text chunks
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("Author", "Roos Keramiek")
    pnginfo.add_text("Copyright", "(c) 2026 Roos Keramiek")
    
    # Save with only the credit info
    img_clean.save(filepath, pnginfo=pnginfo, optimize=True)
    print(f"✓ Cleaned {filepath} and added credit")

# Process all files in relist/
relist_dir = "relist"
for filename in os.listdir(relist_dir):
    filepath = os.path.join(relist_dir, filename)
    if filename.endswith('.jpg'):
        clean_and_add_credit_jpg(filepath)
    elif filename.endswith('.png'):
        clean_and_add_credit_png(filepath)

print("\n✅ All files processed!")
