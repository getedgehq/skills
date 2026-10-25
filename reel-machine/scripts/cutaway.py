#!/usr/bin/env python3
"""cutaway.py OUT.png IMAGE "Title" ["subtitle"] [--crop top]

Full-screen 1080x1920 cutaway card for a named place, product or thing: blurred dark ground
from the photo itself, the title (and an optional subtitle) above, the photo across the frame
width (max 700 px high). It hard-cuts in while the thing is named (spec "cuts"), and the
caption track is drawn over it, so captions stay readable.
Photos from Wikimedia Commons: fetch them with commons.py, which also records the credit line.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

args = sys.argv[1:]
crop_top = False
if "--crop" in args:
    i = args.index("--crop"); crop_top = args[i + 1] == "top"; del args[i:i + 2]
if len(args) < 3:
    sys.exit(__doc__)
out, img, title = args[:3]; sub = args[3] if len(args) > 3 else ""
W, H, BOX = 1080, 1920, 700
font, idx = rmconf.caption_font()
src = Image.open(img).convert("RGB")
bg = src.resize((W, H)).filter(ImageFilter.GaussianBlur(60))
bg = Image.blend(bg, Image.new("RGB", (W, H), (14, 16, 20)), 0.72)
d = ImageDraw.Draw(bg)
tf = rmconf.bold(ImageFont.truetype(font, 66, index=idx)); sf = ImageFont.truetype(font, 34, index=idx)
im = src.copy(); im.thumbnail((W, BOX))
if im.width < W:  # fill the width when possible, crop the height to the box
    im = src.resize((W, int(src.height * W / src.width)))
    if im.height > BOX:
        top = 0 if crop_top else (im.height - BOX) // 2
        im = im.crop((0, top, W, top + BOX))
y0 = 600
bg.paste(im, ((W - im.width) // 2, y0))
ty = y0 - 150 if sub else y0 - 110
d.text(((W - d.textlength(title, font=tf)) / 2, ty), title, font=tf, fill=(255, 255, 255))
if sub:
    d.text(((W - d.textlength(sub, font=sf)) / 2, ty + 82), sub, font=sf, fill=(200, 204, 210))
bg.save(out)
print(out, im.size)
