#!/usr/bin/env python3
"""Face-zone sweep: zero graphic pixels inside any face box, every frame.

Inputs are two renders of the same reel: --foot (picture only, no graphics) and --gfx (graphics and captions
alone on a magenta #FF00FF ground). Faces (up to 3) come from MediaPipe Face Landmarker on the foot render; the
face box is brow-65 to chin+65 px, sides +-65 px. A graphic pixel is any gfx pixel that is not magenta.
Exit 1 if any frame outside --exclude has overlap. --exclude takes the intentional full-frame spans (a takeover,
the final fade): report them, never hide a real overlap with them.
  python3 facezone.py --foot foot.mp4 --gfx gfx.mp4 --model face_landmarker.task --exclude 26.8-27.9
"""
import argparse, json, sys
import numpy as np
from common import frames, runs, spans, FPS

ap = argparse.ArgumentParser()
ap.add_argument("--foot", required=True); ap.add_argument("--gfx", required=True)
ap.add_argument("--model", required=True, help="MediaPipe face_landmarker.task")
ap.add_argument("--margin", type=int, default=65); ap.add_argument("--exclude", default="")
ap.add_argument("--json", default="facezone.json")
a = ap.parse_args()
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=a.model), num_faces=3))
EXCL = spans(a.exclude); M = a.margin
rows, boxes = [], []
for (i, ft), (_, gx) in zip(frames(a.foot), frames(a.gfx)):
    t = round(i / FPS, 3); H, W = ft.shape[:2]
    g = np.abs(gx.astype(int) - [255, 0, 255]).sum(2) > 90
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(ft)))
    tot, bx = 0, []
    for f in r.face_landmarks:
        xs = [q.x * W for q in f]
        if max(xs) - min(xs) < 60: continue
        brow = min(f[k].y * H for k in (105, 334, 66, 296, 107, 336, 70, 300)); chin = f[152].y * H
        y0, y1, x0, x1 = int(max(0, brow - M)), int(min(H, chin + M)), int(max(0, min(xs) - M)), int(min(W, max(xs) + M))
        bx.append([y0, y1, x0, x1]); tot += int(g[y0:y1, x0:x1].sum())
    boxes.append([t, bx])
    if tot and not any(x - 0.002 <= t < y for x, y in EXCL): rows.append((t, tot))
json.dump(boxes, open(a.json, "w"))
R = runs(rows)
print(f"frames {len(boxes)} overlapping frames {len(rows)} runs {R}")
print(f"face boxes per frame written to {a.json} (use them to place captions above or below faces)")
sys.exit(1 if rows else 0)
