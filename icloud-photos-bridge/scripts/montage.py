"""Tile the first N thumbnails of a picks JSON into one JPEG so an agent can look at them in a single image read,
and write the same picks as a self-contained HTML contact sheet next to it (out.html) for the user.
Usage: python montage.py picks.json out.jpg [--n 24] [--cols 6] [--title "Selfies"]"""
import sys, json
from PIL import Image, ImageDraw
picks, out = json.load(open(sys.argv[1])), sys.argv[2]
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 24
cols = int(sys.argv[sys.argv.index("--cols") + 1]) if "--cols" in sys.argv else 6
picks = [r for r in picks if r.get("thumb")][:n]
W, H = 240, 320; rows = (len(picks) + cols - 1) // cols
M = Image.new("RGB", (W * cols, H * rows), "white"); d = ImageDraw.Draw(M)
for i, r in enumerate(picks):
    im = Image.open(r["thumb"]).convert("RGB"); im.thumbnail((W, H))
    x, y = (i % cols) * W, (i // cols) * H; M.paste(im, (x, y))
    d.rectangle([x, y, x + 34, y + 20], fill="black"); d.text((x + 4, y + 4), f"#{i+1}", fill="white")
M.save(out, quality=72); print(out, len(picks))
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import sheet
title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else "Picks"
print(sheet.write(picks, os.path.splitext(out)[0] + ".html", title))
