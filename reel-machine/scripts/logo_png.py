#!/usr/bin/env python3
"""logo_png.py SLUG COLOR OUT [--height 300] [--plate] [--no-shadow]

Brand logo as a transparent PNG for the hook's inline signal or a bare card: fetches the
Simple Icons SVG (pinned version), fills it with COLOR (hex, e.g. "#D97757" or "white"),
renders with rsvg-convert, trims, adds a soft drop shadow. --plate puts it on a white
square first (for marks that vanish on dark footage).

  logo_png.py claude "#D97757" sig/claude.png
  logo_png.py ycombinator "#FF6600" sig/yc.png --plate

Needs rsvg-convert (librsvg). Check the brand's usage guidelines before you publish its mark.
"""
import argparse, subprocess, tempfile, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SI = "https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{}.svg"
ap = argparse.ArgumentParser()
ap.add_argument("slug"); ap.add_argument("color"); ap.add_argument("out")
ap.add_argument("--height", type=int, default=300)
ap.add_argument("--plate", action="store_true"); ap.add_argument("--no-shadow", action="store_true")
a = ap.parse_args()

svg = urllib.request.urlopen(SI.format(a.slug), timeout=30).read().decode()
svg = svg.replace("<svg ", f'<svg fill="{a.color}" ', 1)
with tempfile.TemporaryDirectory() as td:
    sp, pp = Path(td) / "l.svg", Path(td) / "l.png"
    sp.write_text(svg)
    subprocess.run(["rsvg-convert", "-h", str(a.height), str(sp), "-o", str(pp)], check=True)
    im = Image.open(pp).convert("RGBA")
im = im.crop(im.getbbox())
if a.plate:
    bg = Image.new("RGBA", im.size, (0, 0, 0, 0)); m = im.width // 8
    ImageDraw.Draw(bg).rectangle((m, m, im.width - m, im.height - m), fill="white"); bg.alpha_composite(im); im = bg
if not a.no_shadow:
    p = 24
    st = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); st.alpha_composite(im, (p, p))
    sh = Image.new("RGBA", st.size, (0, 0, 0, 0)); sh.putalpha(st.getchannel("A").point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    o = Image.new("RGBA", st.size, (0, 0, 0, 0)); o.alpha_composite(sh, (0, 4)); o.alpha_composite(st); im = o
im.save(a.out); print(a.out, im.size)
