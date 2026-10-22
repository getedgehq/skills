#!/usr/bin/env python3
"""statcard.py OUT "BIG" "small line" : bare stat card (white text, no background, soft shadow).

Place it with a "cards" entry in the reel spec, timed to the spoken number, above the head.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

out, big, small = sys.argv[1], sys.argv[2], sys.argv[3]
F = rmconf.hook_font()
fb = rmconf.bold(ImageFont.truetype(F, 230)); fs = rmconf.bold(ImageFont.truetype(F, 62))
d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
W = int(max(d0.textlength(big, font=fb), d0.textlength(small, font=fs))) + 80; H = 230 + 62 + 90
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.text(((W - d.textlength(big, font=fb)) / 2, 10), big, font=fb, fill="white")
d.text(((W - d.textlength(small, font=fs)) / 2, 265), small, font=fs, fill="white")
sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda a: int(a * 0.7)))
sh = sh.filter(ImageFilter.GaussianBlur(10))
o = Image.new("RGBA", im.size, (0, 0, 0, 0)); o.alpha_composite(sh, (0, 5)); o.alpha_composite(im)
o.save(out); print(out, o.size)
