Perfect! Done. Here's what I found:

## Summary

**Only `carousel_01.png` was actually carrying Content Credentials** - that's the one tripping LinkedIn's label. The other three were clean.

All four cleaned images are now in `output/` - they're pixel-perfect identical to your originals, just with the metadata stripped out. I didn't re-export or recompress anything, just surgically removed the problematic chunks/segments:

- **carousel_01.png** - Removed C2PA chunks (this was the culprit)
- **carousel_02.png** - Cleaned metadata just to be safe
- **portrait_final.jpg** - Stripped XMP data 
- **stage_shot.jpg** - Already clean, minimal changes

The images will open looking exactly like what's in queue/ right now. Your originals are untouched in queue/, and the cleaned versions are ready to post from output/.

Full details are in `CLEANING_REPORT.md` if you want to see exactly what was removed from each file.