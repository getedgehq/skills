#!/usr/bin/env python3
"""Flash and jump detector: per-frame mean |dY| at quarter resolution. Frames above 3x the median are spikes;
spikes within 0.02 s of a listed cut are expected. Report non-cut events (a flash, a snap, a pop).
  python3 lumaspikes.py reel.mp4 --cuts 0.3,7.233,11.567
"""
import argparse
import numpy as np
from common import frames, runs, FPS

ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--cuts", default="")
a = ap.parse_args(); C = [float(x) for x in a.cuts.split(",") if x]
prev, d = None, []
for i, y in frames(a.video, 270, 480, "gray"):
    y = y.astype(np.int16)
    if prev is not None: d.append(float(np.abs(y - prev).mean()))
    prev = y
med = float(np.median(d)); thr = 3 * med
sp = [(i + 1) for i, v in enumerate(d) if v > thr]
non = [((i) / FPS, d[i - 1]) for i in sp if not any(abs(i / FPS - c) < 0.02 for c in C)]
print(f"frames {len(d) + 1} median {med:.2f} spikes {len(sp)} non-cut events (t0, t1, max dY):")
for r in runs(non, 0.1): print(f"  {r[0]:.2f} {r[1]:.2f} {r[2]:.1f}")
print(f"max non-cut dY {max([v for _, v in non], default=0):.1f}")
