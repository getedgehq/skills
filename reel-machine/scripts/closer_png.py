#!/usr/bin/env python3
"""closer_png.py OUT [Y] [--handle @name]

1080x1920 transparent closer layer: white Instagram glyph + the handle, soft shadow,
centered at the hook position (Y=300 by default). The reel spec puts it on the last
~0.9 s and it stays through the end hold. Handle default: REEL_HANDLE from config.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

args = sys.argv[1:]
handle = rmconf.get("REEL_HANDLE")
if "--handle" in args:
    i = args.index("--handle"); handle = args[i + 1]; del args[i:i + 2]
out = args[0]; y = int(args[1]) if len(args) > 1 else 300
if not handle.startswith("@"):
    handle = "@" + handle

W, H = 1080, 1920
L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
f = rmconf.bold(ImageFont.truetype(rmconf.hook_font(), 96))
tw = d.textlength(handle, font=f); g = 96; gap = 28; x0 = int((W - (g + gap + tw)) / 2)
# Instagram glyph: rounded square outline, ring, dot (drawn 4x, downsampled)
s = 4; G = Image.new("RGBA", (g * s, g * s), (0, 0, 0, 0)); gd = ImageDraw.Draw(G); lw = int(g * s * 0.085)
gd.rounded_rectangle([lw // 2, lw // 2, g * s - lw // 2, g * s - lw // 2], radius=int(g * s * 0.28), outline="white", width=lw)
c = g * s / 2; r = g * s * 0.22; gd.ellipse([c - r, c - r, c + r, c + r], outline="white", width=lw)
dr = g * s * 0.06; gd.ellipse([g * s * 0.74 - dr, g * s * 0.26 - dr, g * s * 0.74 + dr, g * s * 0.26 + dr], fill="white")
G = G.resize((g, g), Image.LANCZOS)
L.alpha_composite(G, (x0, y + 8)); d.text((x0 + g + gap, y), handle, font=f, fill="white")
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh.putalpha(L.getchannel("A").point(lambda a: int(a * 0.55)).filter(ImageFilter.GaussianBlur(14)))
o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o.alpha_composite(sh, (0, 6)); o.alpha_composite(L); o.save(out)
print(out, handle)
