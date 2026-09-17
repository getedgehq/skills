Done! Here's the situation:

**Three of your four images were carrying the metadata that triggers LinkedIn's content credentials label:**

1. **carousel_01.png** - Full ChatGPT/DALL-E C2PA manifest (the big one - 1,251 bytes of provenance data)
2. **carousel_02.png** - Midjourney metadata embedded in the PNG text chunks
3. **portrait_final.jpg** - This one might surprise you - it had 635 bytes of AI-related metadata hidden in an APP1 segment. Even though it's yours, something in your workflow (maybe an editor or export tool) added AI attribution

**stage_shot.jpg** was completely clean - no metadata at all.

All four cleaned images are now in `output/` and they're verified clean. They'll open looking exactly the same as what's in `queue/` right now - same dimensions, same pixels, no recompression. I just surgically removed the metadata chunks that LinkedIn reads. The originals in `queue/` are untouched.

The cleaned files are slightly smaller (because the metadata is gone), but the image quality is identical. You're good to post these on LinkedIn without triggering that label.