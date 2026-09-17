Done - cleaned copies are in `output/`, `queue/` is untouched.

| file | what was in it | what I did |
|---|---|---|
| `carousel_01.png` | C2PA manifest in a `caBX` chunk (OpenAI gpt-image-1) and an XMP record with `trainedAlgorithmicMedia` | dropped both chunks at the byte level |
| `carousel_02.png` | no C2PA at all - the giveaway was two `tEXt` records, `Software: Midjourney v7` and a generation `Description` | dropped both records |
| `portrait_final.jpg` | one APP1 XMP segment from the Photoshop/Firefly generative fill | dropped that segment only |
| `stage_shot.jpg` | nothing. This one is a straight camera frame (FUJIFILM X-T5) and was never carrying anything | left it alone, not copied, not touched |

What I deliberately did **not** remove: the embedded sRGB ICC profile in all three, your
`Copyright`/`Author` records (Dela Ruiz), and the structured EXIF in `portrait_final.jpg`. That EXIF
block holds `Orientation=6` - the file is stored 480x640 and displays 640x480, so wiping EXIF would
have handed you a sideways headshot.

Nothing was re-encoded. I removed the metadata from the container rather than decoding and
re-saving, so the JPEG scan data is the same bytes it was before.

Verified afterwards rather than assumed: I re-read each output, walked its chunks/segments again and
scanned the metadata for `c2pa`, `jumbf`, `openai`, `chatgpt`, `midjourney`, `firefly` and
`trainedAlgorithmicMedia` - no hits - and pixel-compared each cleaned file against its original,
mean difference 0.0 on all three.

One caveat: this only removes what is *in the file*. If LinkedIn ever labels a post on the basis of
its own image analysis rather than embedded credentials, nothing in the file can prevent that.
