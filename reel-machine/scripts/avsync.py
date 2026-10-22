#!/usr/bin/env python3
"""avsync.py SOURCE MASTER [--rot 1] [--min-sim 0.85] [--max-drift-ms 80]

Lip-sync check of a rendered reel against its source clip. For each 1 s window of the
master's audio (every 1.5 s) it finds where that audio sits in the source (cross-correlation),
then finds which source video frame best matches the master's frame at that moment (center
crop, normalised grayscale). offset = source time by audio - source time by video, in ms
(+ = video late). Rows whose frame match has sim < --min-sim are printed but ignored: a
cutaway, card or face turn makes the frame match meaningless there.

Verdict uses only rows with sim >= min-sim: PASS when the offset does not grow across the reel
(last-third median minus first-third median within --max-drift-ms). A drifting offset is the
failure that matters; a small constant offset is the encoder's and usually invisible.

--rot: quarter turns applied to SOURCE frames. Phone portrait .mov files often decode
landscape with a rotation flag that PyAV ignores; 1 fixes that. Use 0 for already-upright files.
"""
import argparse
import av, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("source"); ap.add_argument("master")
ap.add_argument("--rot", type=int, default=1)
ap.add_argument("--min-sim", type=float, default=0.85)
ap.add_argument("--max-drift-ms", type=float, default=80)
a = ap.parse_args()


def audio(p):
    c = av.open(p); s = c.streams.audio[0]; r = av.AudioResampler("s16", "mono", 8000); out = []
    for f in c.decode(s):
        for g in r.resample(f):
            out.append(g.to_ndarray().ravel())
    return np.concatenate(out).astype(np.float32)


def frames(p, rot=0):
    c = av.open(p); s = c.streams.video[0]; T = []; F = []
    for f in c.decode(s):
        im = f.to_ndarray(format="gray")
        if rot:
            im = np.rot90(im, -rot)
        h, w = im.shape; x0 = (w - h * 1080 // 1920) // 2 + int(h * 1080 / 1920 * .2); x1 = x0 + int(h * 1080 / 1920 * .6)
        im = im[int(h * .25):int(h * .72):8, x0:x1:8].astype(np.float32)
        im = (im - im.mean()) / (im.std() + 1e-6); T.append(float(f.pts * s.time_base)); F.append(im.ravel())
    return np.array(T), F


As, Am = audio(a.source), audio(a.master)
Ts, Fs = frames(a.source, a.rot); Tm, Fm = frames(a.master)
m = min(len(Fs[0]), len(Fm[0]))
dur = len(Am) / 8000
rows = []
for t in np.arange(1, dur - 1.5, 1.5):
    w = Am[int(t * 8000):int((t + 1) * 8000)]
    if len(w) < 8000 or w.std() < 1e-3:
        continue
    corr = np.correlate(As, w, "valid")
    ta = int(np.argmax(corr)) / 8000  # master t maps to source ta
    i = int(np.argmin(abs(Tm - (t + 0.5))))
    cand = np.where(abs(Ts - (ta + 0.5)) < 0.6)[0]
    if len(cand) == 0:
        continue
    sims = [float(np.dot(Fm[i][:m], Fs[j][:m]) / m) for j in cand]
    j = cand[int(np.argmax(sims))]
    off = (ta + 0.5 - Ts[j]) * 1000
    rows.append((t, off, max(sims)))
    print(f"m={t:5.1f}s  src_audio={ta + 0.5:6.2f}  src_video={Ts[j]:6.2f}  offset={off:+5.0f}ms sim={max(sims):.2f}")

good = [(t, o) for t, o, s in rows if s >= a.min_sim]
if len(good) < 3:
    print(f"UNDECIDED: only {len(good)} rows with sim >= {a.min_sim}; look at the reel yourself")
    raise SystemExit(2)
k = max(1, len(good) // 3)
first = float(np.median([o for _, o in good[:k]])); last = float(np.median([o for _, o in good[-k:]]))
med = float(np.median([o for _, o in good]))
drift = last - first
verdict = "PASS" if abs(drift) <= a.max_drift_ms else "FAIL"
print(f"{verdict}: {len(good)}/{len(rows)} rows sim>={a.min_sim}, median offset {med:+.0f}ms, drift {drift:+.0f}ms "
      f"(first third {first:+.0f}, last third {last:+.0f}, limit {a.max_drift_ms:.0f})")
raise SystemExit(0 if verdict == "PASS" else 1)
