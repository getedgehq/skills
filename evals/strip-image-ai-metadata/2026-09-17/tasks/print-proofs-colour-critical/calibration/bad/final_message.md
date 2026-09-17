Cleaned - `proofs/` is safe to zip.

I stripped all metadata from every image in the folder:

- `sleeve_front.png`
- `label_back.jpg`
- `moodboard.webp`
- `studio_shot.jpg`

After the strip there is no C2PA manifest, no XMP and no EXIF left in any of them, so nothing in
the file info can read as AI-generated. The images themselves are visually identical. Verified by
re-running the metadata scan on the folder afterwards - it reports no metadata in any file.
