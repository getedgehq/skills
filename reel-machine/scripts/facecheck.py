#!/usr/bin/env python3
"""facecheck.py REEL.mp4 [--head 0.5] [--tail 2.0] [--strip out.jpg]

Checks the frames people judge the reel by: the first 0.5 s (the thumbnail and the first
impression) and the last 2 s (where the reel lands). Samples 8 frames per second there and
flags each frame with:
  noface    no face found
  half      the face box touches the frame edge or is cut off (half a face in shot)
  blur      the face is soft (Laplacian variance of the face crop under --blur, default 60)
  eyes      no open eye found in the upper half of the face (closed eyes, mid-blink)
FAIL when the first frame or the last frame is flagged, or when more than half of the
sampled frames in either window are. Exit code 1 on FAIL. It is a heuristic (OpenCV Haar
cascades, no network, no model download): always look at the --strip contact sheet too, and
for a reel without a face on purpose (b-roll ending, product shot) skip it and say why.
Fix a fail by moving the cut (another word boundary), pcut.py --headfreeze for a blink on frame
0, or a shorter tail_max in the spec.
"""
import argparse, subprocess, sys
import cv2

if not hasattr(cv2, "CascadeClassifier"):
    sys.exit("facecheck: this OpenCV has no Haar cascades (OpenCV 5 moved them): pip install 'opencv-python-headless>=4.8,<5'")

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--head", type=float, default=0.5); ap.add_argument("--tail", type=float, default=2.0)
ap.add_argument("--blur", type=float, default=60.0); ap.add_argument("--fps", type=float, default=8.0)
ap.add_argument("--strip")
a = ap.parse_args()

FACES = [cv2.CascadeClassifier(cv2.data.haarcascades + f) for f in
         ("haarcascade_frontalface_default.xml", "haarcascade_frontalface_alt2.xml")]
EYE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                           capture_output=True, text=True).stdout)
cap = cv2.VideoCapture(a.video)


def frame_at(t):
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000)
    ok, f = cap.read()
    return f if ok else None


def flags(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    g = cv2.equalizeHist(cv2.resize(g, (480, int(g.shape[0] * 480 / g.shape[1]))))  # selfie close-ups detect better small
    h, w = g.shape
    faces = []
    for fc in FACES:
        faces = fc.detectMultiScale(g, 1.05, 4, minSize=(w // 6, w // 6))
        if len(faces):
            break
    if len(faces) == 0:
        return ["noface"]
    x, y, fw, fh = max(faces, key=lambda r: r[2] * r[3]); out = []
    m = int(0.01 * w)
    if x <= m or y <= m or x + fw >= w - m or y + fh >= h - m:
        out.append("half")
    crop = g[y:y + fh, x:x + fw]
    if cv2.Laplacian(cv2.resize(crop, (256, 256)), cv2.CV_64F).var() < a.blur:
        out.append("blur")
    upper = crop[: fh // 2]
    if len(EYE.detectMultiScale(upper, 1.05, 5, minSize=(fw // 10, fw // 10))) == 0:
        out.append("eyes")
    return out


step = 1 / a.fps
head = [round(i * step, 3) for i in range(int(a.head * a.fps) + 1) if i * step <= a.head]
tail = [round(dur - 0.05 - i * step, 3) for i in range(int(a.tail * a.fps) + 1)][::-1]
res, shots = {}, []
for name, ts in (("head", head), ("tail", tail)):
    rows = []
    for t in ts:
        f = frame_at(t)
        if f is None:
            continue
        fl = flags(f); rows.append((t, fl)); shots.append(cv2.resize(f, (135, 240)))
    res[name] = rows
cap.release()

fail = []
for name, rows in res.items():
    bad = [r for r in rows if r[1]]
    for t, fl in rows:
        print(f"{name} {t:6.2f}s {' '.join(fl) or 'ok'}")
    if rows and len(bad) > len(rows) / 2:
        fail.append(f"{name}: {len(bad)}/{len(rows)} frames flagged")
if res["head"] and res["head"][0][1]:
    fail.append("first frame: " + " ".join(res["head"][0][1]))
if res["tail"] and res["tail"][-1][1]:
    fail.append("last frame: " + " ".join(res["tail"][-1][1]))
if a.strip and shots:
    cv2.imwrite(a.strip, cv2.hconcat(shots))
print(("FAIL " + "; ".join(fail)) if fail else "PASS face check", a.video)
sys.exit(1 if fail else 0)
