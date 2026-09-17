import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import shutil

def check_metadata(filepath):
    """Check for problematic metadata that triggers Content Credentials"""
    img = Image.open(filepath)
    issues = []
    
    # Check for common AI/generative metadata
    if hasattr(img, 'info'):
        info = img.info
        for key in info:
            key_lower = str(key).lower()
            value_str = str(info[key]).lower() if info[key] else ""
            
            # Check for problematic keys
            if any(x in key_lower for x in ['c2pa', 'contentcredentials', 'software', 'generator', 'comment']):
                issues.append(f"  {key}: {info[key][:100] if len(str(info[key])) > 100 else info[key]}")
            
            # Check for AI-related values
            elif any(x in value_str for x in ['midjourney', 'stable diffusion', 'dall-e', 'firefly', 
                                               'algorithmic', 'trainedAlgorithmic', 'generative']):
                issues.append(f"  {key}: {info[key][:100] if len(str(info[key])) > 100 else info[key]}")
    
    # Check EXIF for JPEGs
    if hasattr(img, '_getexif') and img._getexif():
        exif = img._getexif()
        for tag, value in exif.items():
            value_str = str(value).lower() if value else ""
            if any(x in value_str for x in ['midjourney', 'firefly', 'algorithmic', 'generative']):
                issues.append(f"  EXIF {tag}: {str(value)[:100]}")
    
    return issues

def clean_png(input_path, output_path):
    """Clean PNG by removing all text chunks and metadata"""
    img = Image.open(input_path)
    
    # Get the raw image data
    if img.mode in ('RGBA', 'LA', 'PA'):
        # Keep transparency
        img_clean = img.copy()
    else:
        img_clean = img.copy()
    
    # Save without any metadata
    img_clean.save(output_path, 'PNG', optimize=False, compress_level=6)
    img.close()
    img_clean.close()

def clean_jpeg(input_path, output_path):
    """Clean JPEG by removing EXIF and other metadata"""
    img = Image.open(input_path)
    
    # Create new image without metadata
    img_clean = img.copy()
    
    # Determine subsampling
    if hasattr(img, 'layers') or img.mode == 'RGB':
        subsampling = 0  # 4:4:4 (best quality)
    else:
        subsampling = 0
    
    # Save without metadata, preserve quality
    img_clean.save(output_path, 'JPEG', quality=95, optimize=False, subsampling=subsampling)
    img.close()
    img_clean.close()

# Create output directory
os.makedirs('output', exist_ok=True)

# Process all images
results = []
for filename in sorted(os.listdir('queue')):
    filepath = os.path.join('queue', filename)
    if not os.path.isfile(filepath):
        continue
    
    print(f"\n{'='*60}")
    print(f"Checking: {filename}")
    print('='*60)
    
    issues = check_metadata(filepath)
    
    if issues:
        print(f"❌ FOUND PROBLEMATIC METADATA:")
        for issue in issues:
            print(issue)
        results.append((filename, True, issues))
    else:
        print(f"✓ Clean - no problematic metadata detected")
        results.append((filename, False, []))
    
    # Clean the image
    output_path = os.path.join('output', filename)
    
    if filename.lower().endswith('.png'):
        clean_png(filepath, output_path)
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        clean_jpeg(filepath, output_path)
    else:
        # Just copy if unknown format
        shutil.copy2(filepath, output_path)
    
    print(f"→ Cleaned version saved to: {output_path}")

print(f"\n{'='*60}")
print("SUMMARY")
print('='*60)

had_issues = [r for r in results if r[1]]
was_clean = [r for r in results if not r[1]]

if had_issues:
    print(f"\n🔴 Images with Content Credentials metadata ({len(had_issues)}):")
    for filename, _, issues in had_issues:
        print(f"  • {filename}")
        
if was_clean:
    print(f"\n🟢 Images that were already clean ({len(was_clean)}):")
    for filename, _, _ in was_clean:
        print(f"  • {filename}")

print(f"\n✓ All {len(results)} images cleaned and saved to output/")
