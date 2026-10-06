#!/usr/bin/env python3
"""Pre-pass: per-frame face no-go boxes from the picture-only render (MediaPipe Face Landmarker, up to 3 faces).
A box is brow - 65 to chin + 65 px, sides +- 65 px, in output pixels. Use it to place captions (below faces with
the centre at most 1455, else above with the centre at least 265) and to feed OrbitCards `noGo` rows.

  python3 faceboxes.py foot.mp4 --model face_landmarker.task --out faceboxes.json
  -> [[t, [[y0, y1, x0, x1], ...]], ...]   one row per frame

Needs: mediapipe, numpy, ffmpeg. facezone.py runs the same detector and then checks the gfx render against it.
"""
import argparse, json
import numpy as np
from common import frames, probe, FPS

ap = argparse.ArgumentParser()
ap.add_argument("foot"); ap.add_argument("--model", required=True); ap.add_argument("--out", default="faceboxes.json")
ap.add_argument("--margin", type=int, default=65)
a = ap.parse_args()
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=a.model), num_faces=3))
info = probe(a.foot); W, H, M = info["w"], info["h"], a.margin
out = []
for i, fr in frames(a.foot):
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)))
    bx = []
    for f in r.face_landmarks:
        xs = [q.x * W for q in f]
        if max(xs) - min(xs) < 60:  # ignore tiny background faces
            continue
        brow = min(f[k].y * H for k in (105, 334, 66, 296, 107, 336, 70, 300))
        bx.append([round(brow - M), round(f[152].y * H + M), round(min(xs) - M), round(max(xs) + M)])
    out.append([round(i / FPS, 3), bx])
json.dump(out, open(a.out, "w"))
print(a.out, len(out), "frames")
