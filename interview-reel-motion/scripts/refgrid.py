#!/usr/bin/env python3
"""Same-timestamp reference grid: sample two videos at the same times and tile them as pairs (A over B), with
the PSNR of each pair. Use it to compare a new cut against a reference reel, or a rebuild against the original.
  python3 refgrid.py ref.mp4 new.mp4 --times 0,1.5,4,9.9,15,19,25,29,35,41 --out refgrid.jpg [--min-psnr 40]
"""
import argparse, subprocess, sys, os, tempfile, math
import numpy as np
from common import FFMPEG, probe

ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b")
ap.add_argument("--times", required=True); ap.add_argument("--out", default="refgrid.jpg")
ap.add_argument("--min-psnr", type=float, default=None)
x = ap.parse_args(); T = [float(t) for t in x.times.split(",")]


def grab(v, t):
    i = probe(v)
    raw = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-ss", f"{t:.4f}", "-i", v, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(i["h"], i["w"], 3)


def psnr(p, q):
    m = np.mean((p.astype(np.float64) - q.astype(np.float64)) ** 2)
    return 99.0 if m == 0 else 10 * math.log10(255 ** 2 / m)


vals, tmp = [], tempfile.mkdtemp(); raw = open(f"{tmp}/pairs.rgb", "wb")
for k, t in enumerate(T):
    A, B = grab(x.a, t), grab(x.b, t); v = psnr(A, B); vals.append(v)
    print(f"t {t:7.3f}  PSNR {v:6.2f} dB")
    raw.write(np.concatenate([A, B], 0).tobytes())
raw.close(); h, w = A.shape[:2]
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{2 * h}", "-framerate", "1", "-i", f"{tmp}/pairs.rgb", "-vf", f"scale=180:-2,tile={len(T)}x1", "-frames:v", "1", "-q:v", "3", x.out], check=True)
print(f"min {min(vals):.2f} mean {sum(vals) / len(vals):.2f} dB -> {x.out}")
if x.min_psnr is not None and min(vals) < x.min_psnr: sys.exit(1)
