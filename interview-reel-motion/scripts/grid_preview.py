#!/usr/bin/env python3
"""Frame 0 is the thumbnail. Writes frame0.jpg and frame0_grid.jpg: the 3:4 centre crop a feed grid shows
(y 240 to 1680 of a 1080x1920 frame) scaled to 360 px wide. Read the hook at that size before shipping.
  python3 grid_preview.py reel.mp4 [outdir]
"""
import subprocess, sys, os
from common import FFMPEG, probe

v = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "."
os.makedirs(out, exist_ok=True); i = probe(v)
ch = round(i["w"] * 4 / 3); y = (i["h"] - ch) // 2
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-i", v, "-frames:v", "1", "-q:v", "2", f"{out}/frame0.jpg"], check=True)
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-i", v, "-frames:v", "1", "-vf", f"crop={i['w']}:{ch}:0:{y},scale=360:-2", "-q:v", "2", f"{out}/frame0_grid.jpg"], check=True)
print(f"{out}/frame0.jpg {out}/frame0_grid.jpg (grid crop y {y} to {y + ch})")
