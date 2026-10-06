#!/usr/bin/env python3
"""Same-timestamp reference grid: sample two videos at the same times and tile them as pairs (A over B), with
the PSNR and SSIM (luma, Gaussian 11 px window, sigma 1.5) of each pair. Use it to compare a new cut against a
reference reel, or a rebuild against the original (an engine port passes at SSIM >= 0.95 on every sampled frame).
  python3 refgrid.py ref.mp4 new.mp4 --times 0,1.5,4,9.9,15,19,25,29,35,41 --out refgrid.jpg [--min-psnr 40] [--min-ssim 0.95]
"""
import argparse, subprocess, sys, os, tempfile, math
import numpy as np
from common import FFMPEG, probe

ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b")
ap.add_argument("--times", required=True); ap.add_argument("--out", default="refgrid.jpg")
ap.add_argument("--min-psnr", type=float, default=None); ap.add_argument("--min-ssim", type=float, default=None)
x = ap.parse_args(); T = [float(t) for t in x.times.split(",")]


def grab(v, t):
    i = probe(v)
    raw = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-ss", f"{t:.4f}", "-i", v, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(i["h"], i["w"], 3)


def psnr(p, q):
    m = np.mean((p.astype(np.float64) - q.astype(np.float64)) ** 2)
    return 99.0 if m == 0 else 10 * math.log10(255 ** 2 / m)


def _blur(x):
    g = np.exp(-0.5 * (np.arange(-5, 6) / 1.5) ** 2); g /= g.sum()
    x = np.apply_along_axis(lambda r: np.convolve(r, g, "valid"), 1, x)
    return np.apply_along_axis(lambda c: np.convolve(c, g, "valid"), 0, x)


def ssim(p, q):
    """mean SSIM of the BT.601 luma planes (Wang et al. 2004 constants)"""
    Y = lambda a: a.astype(np.float64) @ np.array([0.299, 0.587, 0.114])
    x, y = Y(p), Y(q); C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mx, my = _blur(x), _blur(y)
    sxx, syy, sxy = _blur(x * x) - mx * mx, _blur(y * y) - my * my, _blur(x * y) - mx * my
    return float(np.mean(((2 * mx * my + C1) * (2 * sxy + C2)) / ((mx * mx + my * my + C1) * (sxx + syy + C2))))


vals, svals, tmp = [], [], tempfile.mkdtemp(); raw = open(f"{tmp}/pairs.rgb", "wb")
for k, t in enumerate(T):
    A, B = grab(x.a, t), grab(x.b, t); v = psnr(A, B); sv = ssim(A, B); vals.append(v); svals.append(sv)
    print(f"t {t:7.3f}  PSNR {v:6.2f} dB  SSIM {sv:.4f}")
    raw.write(np.concatenate([A, B], 0).tobytes())
raw.close(); h, w = A.shape[:2]
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{2 * h}", "-framerate", "1", "-i", f"{tmp}/pairs.rgb", "-vf", f"scale=180:-2,tile={len(T)}x1", "-frames:v", "1", "-q:v", "3", x.out], check=True)
print(f"PSNR min {min(vals):.2f} mean {sum(vals) / len(vals):.2f} dB | SSIM min {min(svals):.4f} mean {sum(svals) / len(svals):.4f} -> {x.out}")
if x.min_psnr is not None and min(vals) < x.min_psnr: sys.exit(1)
if x.min_ssim is not None and min(svals) < x.min_ssim: sys.exit(1)
