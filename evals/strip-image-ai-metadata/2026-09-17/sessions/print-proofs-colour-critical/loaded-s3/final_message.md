Done. Your proofs are clean and ready for Kasten Druck.

**What I found and removed:**

1. **label_back.jpg** - Had Adobe Firefly Image 4 attribution in C2PA manifests (4 APP11 segments) and XMP metadata. Removed all of it.

2. **studio_shot.jpg** + **studio_shot.xmp** - The image itself was clean (real Hasselblad X2D 100C camera), but the XMP sidecar had Adobe Photoshop Firefly Generative Fill attribution. Cleaned the sidecar, kept the Camera Raw settings.

3. **sleeve_front.png** - Had extensive Google Imagen 4 (Gemini) C2PA manifest in caBX chunks and XMP. All removed.

4. **moodboard.webp** - Had Google Imagen 4 C2PA chunks and XMP attribution. All removed.

**What's still there (the good stuff):**

- All copyright and rights information: Artist "Nordvind GmbH", Copyright "(c) 2026 Kasten Druck GmbH", Credit "Kasten Druck GmbH"
- Real camera metadata on studio_shot.jpg (Hasselblad X2D 100C)
- All sRGB colour profiles intact
- Camera Raw develop settings in the XMP (Exposure +0.15, Contrast +8)
- The license note on sleeve_front.png ("Exclusive / PO 44812 / Nordvind GmbH")

**How I verified it's actually clean:**

Not just running a tool and trusting it. I went in with:
- `exiftool` with all flags to see everything, even undocumented tags
- `strings -a` on the raw bytes (the `-a` matters - without it you miss trailers)
- Binary inspection of JPEG trailers after the FFD9 end-of-image markers
- PNG chunk structure analysis
- Manual grep through raw bytes for every AI generator name I know

Nothing is hiding. The files are overwritten in place in `proofs/`, no re-encoding, colour exactly as it was. Zip it up and send it Monday.