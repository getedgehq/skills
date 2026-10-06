#!/usr/bin/env python3
"""Pre-pass: person matte with Robust Video Matting (PeterL1n/RobustVideoMatting, mobilenetv3, GPL-3.0 model code
fetched by torch.hub at run time, not shipped here). Writes an RGBA PNG sequence whose alpha is the person, one
file per SOURCE frame, named like the A-roll stack (<frame index>.png), so the engine's Matte beat can lay the
person back over the far half of a TypeRing or OrbitCards (layer "back" under the matte, layer "front" over it).

  python3 matte_rvm.py footage/interview.mp4 --first 1650 --last 1990 --out stacks/matte/s0 [--width 720]

Then add a beat {"component": "Matte", "t0": ..., "t1": ...} between the "back" and "front" beats and pass
--matte stacks/matte to build.py. CPU is fine (about 6 frames/s at 720 px wide on 8 threads); run it detached.
Needs: torch, numpy, pillow, ffmpeg.
"""
import argparse, os, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("--first", type=int, required=True); ap.add_argument("--last", type=int, required=True)
ap.add_argument("--out", required=True); ap.add_argument("--width", type=int, default=720)
ap.add_argument("--fps", type=float, default=30)
a = ap.parse_args()
import torch
from PIL import Image

FF = os.environ.get("IRM_FFMPEG", "ffmpeg")
FP = os.environ.get("IRM_FFPROBE", "ffprobe")
w0, h0 = [int(v) for v in subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", a.src], capture_output=True, text=True, check=True).stdout.strip().split(",")[:2]]
# ffmpeg auto-rotates; probe the decoded size from one frame instead of trusting the stream header
probe = subprocess.run([FF, "-nostdin", "-v", "error", "-i", a.src, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
if len(probe) != w0 * h0:
    w0, h0 = h0, w0
W = a.width; H = int(round(h0 * W / w0 / 2) * 2)
os.makedirs(a.out, exist_ok=True)
cmd = [FF, "-nostdin", "-v", "error", "-i", a.src, "-frames:v", str(a.last + 1), "-vsync", "passthrough", "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
pr = subprocess.Popen(cmd, stdout=subprocess.PIPE)
torch.set_num_threads(os.cpu_count() or 4)
model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3", trust_repo=True).eval()
rec, n, size = [None] * 4, 0, W * H * 3
# the recurrent state needs a short warm-up before the first wanted frame
warm = max(0, a.first - 15)
with torch.no_grad():
    while n <= a.last:
        buf = pr.stdout.read(size)
        if len(buf) < size: break
        if n >= warm:
            f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            x = torch.from_numpy(f.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0)
            fgr, pha, *rec = model(x, *rec, downsample_ratio=0.4)
            if n >= a.first:
                al = (pha[0, 0].clamp(0, 1).numpy() * 255).astype(np.uint8)
                rgba = np.dstack([f, al])  # the person's own pixels, so the matte copy can sit over graphics
                Image.fromarray(rgba, "RGBA").resize((w0, h0), Image.BILINEAR).save(f"{a.out}/{n}.png", optimize=True)
        n += 1
pr.stdout.close(); pr.wait()
print(a.out, a.last - a.first + 1, "frames")
