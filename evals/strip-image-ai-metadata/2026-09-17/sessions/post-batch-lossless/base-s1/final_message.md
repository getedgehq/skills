## Done!

**Short answer:** Only **carousel_01.png** had Content Credentials. It was carrying OpenAI ChatGPT's C2PA signature. The other three were clean.

**What I did:**
- Scanned all 4 images for C2PA/Content Credentials metadata
- Found carousel_01.png had a 643-byte caBX chunk with OpenAI ChatGPT's signature
- Stripped the C2PA chunk without touching the actual image data
- Verified all files are pixel-perfect identical (0% difference)
- Copied the other 3 files (they were already clean)

**Results in output/:**
- ✓ carousel_01.png - cleaned (5.3KB → 4.7KB, C2PA removed)
- ✓ carousel_02.png - clean copy
- ✓ portrait_final.jpg - clean copy  
- ✓ stage_shot.jpg - clean copy

All images open identically to the originals - no visual changes, no re-compression. The queue/ folder is untouched as requested.