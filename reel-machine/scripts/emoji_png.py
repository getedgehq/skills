#!/usr/bin/env python3
"""emoji_png.py EMOJI OUT [--font PATH]

Renders one color emoji (a flag is the usual hook signal: "🇺🇸") to a trimmed transparent PNG.
Uses Apple Color Emoji on macOS, else Noto Color Emoji (install fonts-noto-color-emoji),
or --font. Bitmap emoji fonts only render at their native size (160 for Apple, 109 for Noto).
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("emoji"); ap.add_argument("out"); ap.add_argument("--font")
a = ap.parse_args()
cands = [(a.font, 160)] if a.font else [
    ("/System/Library/Fonts/Apple Color Emoji.ttc", 160),
    ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
    ("/usr/share/fonts/noto/NotoColorEmoji.ttf", 109),
]
for path, size in cands:
    if path and os.path.exists(path):
        f = ImageFont.truetype(path, size); break
else:
    raise SystemExit("no color emoji font found: pass --font")
im = Image.new("RGBA", (size * 3, size * 2), (0, 0, 0, 0))
ImageDraw.Draw(im).text((size // 2, size // 4), a.emoji, font=f, embedded_color=True)
im = im.crop(im.getbbox()); im.save(a.out); print(a.out, im.size)
