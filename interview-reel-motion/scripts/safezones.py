#!/usr/bin/env python3
"""Playback safe zones: no graphic pixel in the top 220, bottom 420 or right 150 px (platform UI), every frame.

Input: the --gfx render (graphics and captions alone on magenta #FF00FF). Exit 1 on any hit outside --exclude.
  python3 safezones.py --gfx gfx.mp4 --exclude 26.8-27.9,41.8-42.2
"""
import argparse, sys
import numpy as np
from common import frames, runs, spans, FPS

ap = argparse.ArgumentParser()
ap.add_argument("--gfx", required=True); ap.add_argument("--top", type=int, default=220)
ap.add_argument("--bottom", type=int, default=420); ap.add_argument("--right", type=int, default=150)
ap.add_argument("--exclude", default="")
a = ap.parse_args(); EXCL = spans(a.exclude); rows = []
for i, gx in frames(a.gfx, 540, 960):
    t = round(i / FPS, 3); g = np.abs(gx.astype(int) - [255, 0, 255]).sum(2) > 90
    top, bot, rt = int(g[: a.top // 2].sum()), int(g[960 - a.bottom // 2:].sum()), int(g[:, 540 - a.right // 2:].sum())
    if top + bot + rt and not any(x - 0.002 <= t < y for x, y in EXCL): rows.append((t, top + bot + rt))
print("safe-zone hits (half-res px):", runs(rows) or "none")
sys.exit(1 if rows else 0)
