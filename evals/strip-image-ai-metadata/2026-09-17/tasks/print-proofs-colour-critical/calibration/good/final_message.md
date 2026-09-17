Folder is ready to zip. Everything was overwritten in `proofs/` in place, no extra copies.

**What was carrying AI provenance**

- `sleeve_front.png` - a `caBX` C2PA manifest (Google Imagen 4) plus an XMP record with
  `DigitalSourceType: trainedAlgorithmicMedia`. Both chunks removed.
- `label_back.jpg` - a C2PA manifest spread across four APP11 segments, plus an APP1 XMP record
  (Adobe Firefly Image 4). Both removed.
- `moodboard.webp` - a `C2PA` RIFF chunk and an `XMP ` chunk, both Imagen. Removed, and the VP8X
  header flag for XMP cleared so the container stays consistent.

**What I did not touch, because the preflight needs it**

- the ICC profiles: `iCCP` in the PNG, the APP2 `ICC_PROFILE` segment in the JPEG, the `ICCP` chunk
  in the WebP. All three are byte-for-byte what they were, so the colour is the colour on the proof.
- the rights records: the PNG `Copyright` / `Author` / `Licence` text chunks, the EXIF
  Copyright/Artist in `label_back.jpg` and its APP13 Photoshop IPTC block with the Kasten Druck
  credit, and the EXIF chunk in the WebP.

Nothing was re-saved or re-compressed. I edited the containers directly, so `label_back.jpg` and the
WebP still have their original image data.

**The one that nearly got away:** `studio_shot.jpg` itself has nothing embedded - it is a straight
photograph and I left it exactly as it was. But `studio_shot.xmp` sitting next to it does: the
retouch was done in a Firefly-enabled Photoshop and the provenance landed in the sidecar, with
`DigitalSourceType: compositeWithTrainedAlgorithmicMedia` and a Firefly `CreatorTool`. Since you are
zipping the whole folder, that sidecar would have gone to Kasten Druck too. I removed those two
records from it and left the `dc:rights` and `dc:creator` statements in place.

**Confirmed by looking, not by trusting the tool:** I re-read all five files afterwards, walked every
chunk and segment again, and grepped the metadata (not the pixel data) for `c2pa`, `jumbf`,
`contentauth`, `imagen`, `firefly`, `gemini` and `trainedAlgorithmicMedia`. Zero hits. I also
decoded each image and compared it pixel for pixel against the version I started with: identical.
