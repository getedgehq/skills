#!/usr/bin/env python3
"""cta_png.py OUT.png "getyourapp.com" [--logo logo.png] [--y 300]

1080x1920 transparent end layer for product reels: the product logo and one call to action
(usually the landing page) at the hook position, soft shadow, no plate. Spec key "cta" puts it
on the last seconds instead of the handle closer. Put the same landing link in the post caption:
on Instagram and TikTok the caption link is the one people copy.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

args = sys.argv[1:]
opt = {}
for k in ("--logo", "--y"):
    if k in args:
        i = args.index(k); opt[k] = args[i + 1]; del args[i:i + 2]
if len(args) < 2:
    sys.exit(__doc__)
out, text = args[0], args[1]; y = int(opt.get("--y", 300))
W, H = 1080, 1920
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
size = 96
f = rmconf.bold(ImageFont.truetype(rmconf.hook_font(), size))
while d.textlength(text, font=f) > W - 160 and size > 48:
    size -= 4; f = rmconf.bold(ImageFont.truetype(rmconf.hook_font(), size))
tw = d.textlength(text, font=f)
if opt.get("--logo"):
    lg = Image.open(opt["--logo"]).convert("RGBA"); lh = 150
    lg = lg.resize((max(1, int(lg.width * lh / lg.height)), lh), Image.LANCZOS)
    L.alpha_composite(lg, ((W - lg.width) // 2, y)); y += lh + 36
d.text(((W - tw) / 2, y), text, font=f, fill="white")
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh.putalpha(L.getchannel("A").point(lambda a: int(a * 0.55)).filter(ImageFilter.GaussianBlur(14)))
o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o.alpha_composite(sh, (0, 6)); o.alpha_composite(L); o.save(out)
print(out, text)
