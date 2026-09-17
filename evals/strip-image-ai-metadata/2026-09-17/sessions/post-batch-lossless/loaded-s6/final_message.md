Done! Here's what I found:

## **Images with AI/C2PA metadata (cleaned):**

1. **carousel_01.png** - Had a C2PA manifest (caBX chunk, 643 bytes) plus Adobe XMP metadata. This was definitely triggering the label.

2. **carousel_02.png** - Had Software tag and Description metadata that likely referenced an AI generator.

3. **portrait_final.jpg** - Had APP1 AI metadata (635 bytes) embedded in the JPEG.

## **Clean from the start:**

4. **stage_shot.jpg** - No AI/C2PA metadata found at all. Copied as-is to output/.

All cleaned files are in **output/** and they're pixel-identical to the originals - no re-encoding, no compression, no quality loss. The images will open looking exactly the same, just without the metadata that trips LinkedIn's content credentials detector.

The three that had metadata are now completely stripped and verified clean. You're good to post all four.