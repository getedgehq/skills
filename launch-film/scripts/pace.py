#!/usr/bin/env python3
"""Pace audit for a rendered film: how much it moves, frame to frame.

Decodes with PyAV (no ffmpeg binary needed), grey 320x180, mean absolute frame difference (0-255).
static: difference < 0.4; cuts: > 28; flashes: frame X differs > 20 from both neighbours, which
agree within 6. See references/pace-and-digestibility.md for how to read the numbers.

python scripts/pace.py <video> [t0 t1] [--fps N (resample grid)] [--json out]
"""
import json
import sys

import av
import numpy as np
from PIL import Image


def grey_frames(path, t0=0.0, t1=1e9, fps=None):
    """Frames in [t0, t1). With fps, resample to that grid (latest frame at or before k/fps)."""
    c = av.open(path)
    v = c.streams.video[0]
    src = []
    for f in c.decode(v):
        t = float(f.pts * v.time_base)
        if t < t0 - 0.05:
            continue
        if t >= t1 - 1e-3:
            break
        src.append((t, np.asarray(f.to_image().convert('L').resize((320, 180), Image.BILINEAR), np.int16)))
    native = float(v.average_rate)
    if not fps or abs(fps - native) < 1e-6:
        return np.stack([a for t, a in src if t >= t0 - 1e-3]), native
    out, j = [], 0
    for k in range(int(round((min(t1, src[-1][0] + 1 / native) - t0) * fps))):
        tk = t0 + k / fps
        while j + 1 < len(src) and src[j + 1][0] <= tk + 1e-4:
            j += 1
        out.append(src[j][1])
    return np.stack(out), fps


def audit(path, t0=0.0, t1=1e9, fps=None):
    f, fps = grey_frames(path, t0, t1, fps)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    flashes = []
    for i in range(1, len(f) - 1):
        a, x, b = f[i - 1], f[i], f[i + 1]
        if np.abs(x - a).mean() > 20 and np.abs(x - b).mean() > 20 and np.abs(a - b).mean() < 6:
            flashes.append(round(t0 + i / fps, 2))
    return {
        'file': path.split('/')[-1], 'fps': fps, 'window': [t0, round(t0 + len(f) / fps, 2)], 'frames': int(len(f)),
        'mean_motion': round(float(d.mean()), 2), 'p50': round(float(np.median(d)), 2),
        'p90': round(float(np.percentile(d, 90)), 2), 'static_pct': round(100 * float((d < 0.4).mean()), 1),
        'cuts': [round(t0 + (i + 1) / fps, 2) for i in np.where(d > 28)[0]], 'flashes': flashes,
        'per_second': [round(float(d[i:i + int(fps)].mean()), 2) for i in range(0, len(d), int(fps))],
    }


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    js = fps = None
    if '--fps' in args:
        k = args.index('--fps'); fps = float(args[k + 1]); del args[k:k + 2]
    if '--json' in args:
        k = args.index('--json'); js = args[k + 1]; del args[k:k + 2]
    path = args[0]
    t0, t1 = (float(args[1]), float(args[2])) if len(args) >= 3 else (0.0, 1e9)
    r = audit(path, t0, t1, fps)
    print(json.dumps(r))
    if js:
        open(js, 'w').write(json.dumps(r, indent=1))
