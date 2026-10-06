#!/usr/bin/env python3
"""Pre-pass: person matte with Robust Video Matting (PeterL1n/RobustVideoMatting, mobilenetv3, GPL-3.0 model code
fetched by torch.hub at run time, not shipped here). Writes an RGBA PNG sequence whose alpha is the person, one
file per SOURCE frame, named like the A-roll stack (<frame index>.png), so the engine's Matte beat can lay the
person back over the far half of a TypeRing or OrbitCards (layer "back" under the matte, layer "front" over it).

  python3 matte_rvm.py footage/interview.mp4 --first 1650 --last 1990 --out stacks/matte/s0 [--width 720]

Then add a beat {"component": "Matte", "t0": ..., "t1": ...} between the "back" and "front" beats and pass
--matte stacks/matte to build.py. CPU is fine; it decodes from the start of the file to the last frame, so run it detached.
Needs: torch, numpy, pillow, ffmpeg.
"""
import argparse, json, os, subprocess
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
# decoded size: ffmpeg auto-rotates phone footage, so swap the stream size on a 90 degree rotation (same as build.py)
j = json.loads(subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation", "-of", "json", a.src], capture_output=True, text=True, check=True).stdout)["streams"][0]
w0, h0 = j["width"], j["height"]
if any(abs(int(sd.get("rotation", 0))) % 180 == 90 for sd in j.get("side_data_list", []) or []):
    w0, h0 = h0, w0
W = a.width; H = int(round(h0 * W / w0 / 2) * 2)
os.makedirs(a.out, exist_ok=True)
cmd = [FF, "-nostdin", "-v", "error", "-i", a.src, "-frames:v", str(a.last + 1), "-vsync", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
pr = subprocess.Popen(cmd, stdout=subprocess.PIPE)
torch.set_num_threads(os.cpu_count() or 4)
model = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3", trust_repo=True).eval()
rec, n, size = [None] * 4, 0, w0 * h0 * 3  # full-resolution frames: the model sees a W-wide copy
# the recurrent state needs a short warm-up before the first wanted frame
warm = max(0, a.first - 15)
with torch.no_grad():
    while n <= a.last:
        buf = pr.stdout.read(size)
        if len(buf) < size: break
        if n >= warm:
            full = np.frombuffer(buf, np.uint8).reshape(h0, w0, 3)
            f = np.asarray(Image.fromarray(full).resize((W, H), Image.BILINEAR))
            x = torch.from_numpy(f.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0)
            fgr, pha, *rec = model(x, *rec, downsample_ratio=0.4)
            if n >= a.first:
                al = Image.fromarray((pha[0, 0].clamp(0, 1).numpy() * 255).astype(np.uint8)).resize((w0, h0), Image.BILINEAR)
                # the person's own full-resolution pixels under the alpha, so the matte copy matches the A-roll exactly
                Image.fromarray(np.dstack([full, np.asarray(al)]), "RGBA").save(f"{a.out}/{n}.png", compress_level=1)
        n += 1
pr.stdout.close(); pr.wait()
print(a.out, a.last - a.first + 1, "frames")
