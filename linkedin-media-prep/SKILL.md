---
name: linkedin-media-prep
description: Convert, crop, resize, and compress images and videos for optimal LinkedIn upload quality and file size. Use when the user wants to prepare a photo, image, or video for LinkedIn (profile picture, cover photo, post image, article featured image, post video, or video ad), optimize file size for LinkedIn, crop and resize for LinkedIn dimensions, convert HEIC/RAW/PNG/MOV to LinkedIn-ready JPEG or MP4, or mentions LinkedIn media requirements, specs, or limits.
---

# LinkedIn Media Prep

Prepare any image or video for LinkedIn with correct dimensions, cropping, and compression.

---

## Image Specs

| Use Case | Dimensions | Ratio | Notes |
|---|---|---|---|
| Post (portrait, max feed space) | 1080 × 1350 | 4:5 | **Default choice** for photos |
| Post (landscape) | 1200 × 627 | 1.91:1 | Good for banners, screenshots |
| Post (square) | 1080 × 1080 | 1:1 | Safe universal choice |
| Post (4:3) | 1440 × 1080 | 4:3 | Good for camera-native photos |
| Profile photo | 400 × 400 min | 1:1 | Recommend 800 × 800 |
| Cover photo | 1584 × 396 | 4:1 | |
| Article featured | 1200 × 627 | 1.91:1 | |
| **Max file size** | **8 MB** | — | Target < 1 MB for fast upload |
| **Formats** | JPEG, PNG, GIF | — | **JPEG preferred** for photos |

## Video Specs

| Use Case | Dimensions | Ratio | Notes |
|---|---|---|---|
| Post (square) | 1080 × 1080 | 1:1 | Safe universal choice |
| Post (landscape) | 1920 × 1080 | 16:9 | Standard feed video |
| Post (vertical) | 1080 × 1920 | 9:16 | Mobile/Reels-style; pad if source is not 9:16 |
| **Max file size** | **5 GB** | — | Target < 200 MB for fast upload |
| **Max duration** | **30 minutes** | — | 3 seconds minimum |
| **Formats** | MP4 (H.264 + AAC) | — | **MP4 required** for best compatibility |
| **Frame rate** | 30 fps | — | Match source or standardise to 30 fps |
| **Pixel format** | yuv420p | — | Required for broad playback support |

---

## Image Workflow

### 1. Inspect source

```bash
sips -g pixelWidth -g pixelHeight "<input>"
ls -lh "<input>"
```

### 2. Fix EXIF orientation (if needed)

iPhone and mobile photos often store portrait images with an EXIF orientation tag rather than rotated pixels. ImageMagick usually respects this automatically, but if the image appears sideways after conversion you can force it upright before cropping.

```bash
magick "<input>" -auto-orient "<input>-upright.png"
```

Use the upright version as your working copy for cropping.

### 3. Convert to editable format

If source is HEIC or other non-PNG:

```bash
sips -s format png "<input>" --out "<input>.png"
```

Use the PNG as the working copy for cropping.

### 4. Crop (iterative with user)

**First crop:** center, choose dimensions based on target ratio.

For a 4:5 portrait post from a portrait photo:
- Crop width = full width of image
- Crop height = width × 5 / 4
- Y-offset = (original_height − crop_height) / 2

Example for 3024 × 4032 source:
```bash
magick "source.png" -crop 3024x3780+0+126 "cropped.png"
```

**Iterative adjustments:**
- "More zoomed in" → reduce crop WxH (e.g. 2000×2500 instead of 3024×3780). Keep same ratio.
- "Too much space at top" → increase Y-offset (shift crop down).
- "Too much space at bottom" → decrease Y-offset (shift crop up).
- "Need wider/narrower" → adjust W and H maintaining ratio.

**Crop formula:**
```bash
magick "source.png" -crop <W>x<H>+<X>+<Y> "cropped.png"
# X = (original_width − W) / 2  (centered)
# Y = adjust based on subject position
```

### 5. Resize & compress for LinkedIn

```bash
magick "cropped.png" -resize 1080x1350 -quality 85 "<name>-linkedin.jpg"
```

For profile photos:
```bash
magick "cropped.png" -resize 800x800 -quality 85 "<name>-linkedin-profile.jpg"
```

For cover photos:
```bash
magick "cropped.png" -resize 1584x396 -quality 85 "<name>-linkedin-cover.jpg"
```

For 4:3 posts:
```bash
magick "source.png" -resize 1440x1080 -quality 85 "<name>-linkedin-4by3.jpg"
```

### 6. Verify output

```bash
ls -lh "<output>.jpg"
sips -g pixelWidth -g pixelHeight "<output>.jpg"
```

Ensure:
- Dimensions match target
- File size < 8 MB (preferably < 1 MB)
- Quality is acceptable

---

### Which video format should I choose?

| Source orientation | Your goal | Recommended target |
|---|---|---|
| Portrait (phone video) | Maximum mobile feed space | **Vertical 1080×1920** (pad with black if source is 3:4 or 4:5) |
| Portrait (phone video) | Safe universal compatibility | **Square 1080×1080** (centre-crop) |
| Landscape (screen-recording, camera) | Standard feed video | **Landscape 1920×1080** |
| Landscape | Safe universal compatibility | **Square 1080×1080** (centre-crop) |
| Not sure | — | **Square 1080×1080** |

> **Rule of thumb:** Square works everywhere. Vertical gets the most mobile screen real estate but can letterbox on desktop. Landscape is best for demos, interviews, and cinematic content.

---

## Video Workflow

### 1. Inspect source

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,duration,bit_rate \
  -show_entries format=duration,size,bit_rate \
  -of csv=p=0 "<input>"
```

Also check for rotation metadata:
```bash
ffprobe -v error -select_streams v:0 -show_entries stream_side_data=display_matrix \
  -of default=nk=1:nw=1 "<input>"
```

### 2. Handle rotation (iPhone / mobile sources)

Mobile videos often store frames in landscape with a rotation tag. Apply `transpose` in the filter chain before cropping/scaling.

| Display Matrix | Transpose value | Meaning |
|---|---|---|
| `-90°` (270°) | `1` | 90° clockwise |
| `+90°` | `2` | 90° counter-clockwise |
| `180°` | `3` | 180° |
| No rotation | omit | — |

### 3. Choose target and build filter chain

**Square (1080×1080)** — centre-crop after rotation:
```
transpose=1,crop=1080:1080:(in_w-1080)/2:(in_h-1080)/2,format=yuv420p
```

**Landscape (1920×1080)** — scale to fit then pad, or centre-crop:
```
transpose=1,scale=1920:-2,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p
```

**Vertical (1080×1920)** — scale to width then pad top/bottom:
```
transpose=1,scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p
```

If the source aspect ratio already matches the target, you can omit `pad` and just `scale=1080:1080` or `scale=1920:1080`.

### 4. Common one-liner (portrait iPhone → square)

The most frequent request: a portrait iPhone video converted to a LinkedIn-ready square MP4.

```bash
ffmpeg -y -i "IMG_xxxx.MOV" \
  -vf "transpose=1,crop=1080:1080:(in_w-1080)/2:(in_h-1080)/2,format=yuv420p" \
  -c:v libx264 -profile:v main -level 4.2 -preset medium -crf 23 -r 30 \
  -c:a aac -b:a 128k -movflags +faststart \
  "output_linkedin_square.mp4"
```

Swap `transpose=1` for the correct rotation value from Step 2, or omit `transpose=1,` if the source has no rotation metadata.

### 5. Transcode

```bash
ffmpeg -y -i "<input>" \
  -vf "<filter_chain>" \
  -c:v libx264 -profile:v main -level 4.2 -preset medium -crf 23 -r 30 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  "<output>.mp4"
```

Parameter notes:
- `-profile:v main -level 4.2` — broad device compatibility
- `-crf 23` — good quality / size balance (lower = higher quality)
- `-r 30` — standardise frame rate
- `-movflags +faststart` — moov atom at beginning for web streaming

### 6. Verify output

```bash
ls -lh "<output>.mp4"
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,duration,bit_rate \
  -show_entries format=duration,size,bit_rate \
  -of csv=p=0 "<output>.mp4"
```

Ensure:
- Dimensions match target
- File size reasonable for upload (< 200 MB ideally)
- No rotation metadata remains (players should not rotate it again)

---

## Tools

- **Images:** Prefer `magick` (ImageMagick 7) or `convert` (ImageMagick 6). Fallback to `sips` on macOS for basic format conversion. Install via `brew install imagemagick`.
- **Videos:** `ffmpeg` + `ffprobe`. Install via `brew install ffmpeg`.
