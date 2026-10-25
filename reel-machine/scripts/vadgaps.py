#!/usr/bin/env python3
"""vadgaps.py VIDEO [VIDEO ...]   pace gate

Finds speech with Silero VAD (bundled with faster-whisper) and measures the pauses between
speech. Word timestamps from a transcriber are not enough: they stretch words over pauses and
hide them. FAIL when any inner gap is longer than REEL_MAX_GAP (0.35 s) or dead air (gaps over
0.2 s plus a lead-in over 0.15 s) is more than REEL_MAX_DEAD (8%) of the reel.
Exit code 1 if any file fails. Fix a fail with pcut.py, never by loosening the gate.
"""
import os, sys
from pathlib import Path
import av, numpy as np
from faster_whisper.vad import get_speech_timestamps, VadOptions

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

MAXGAP, MAXDEAD = float(rmconf.get("REEL_MAX_GAP")), float(rmconf.get("REEL_MAX_DEAD"))


def pcm(path):
    c = av.open(path); a = c.streams.audio[0]
    rs = av.AudioResampler(format="flt", layout="mono", rate=16000); buf = []
    for f in c.decode(a):
        for r in rs.resample(f):
            buf.append(r.to_ndarray().reshape(-1))
    return np.concatenate(buf).astype(np.float32)


bad = 0
for v in sys.argv[1:]:
    x = pcm(v); dur = len(x) / 16000
    ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_silence_duration_ms=200, speech_pad_ms=60))
    segs = [(t["start"] / 16000, t["end"] / 16000) for t in ts]
    gaps = [(round(b[0] - a[1], 2), round(a[1], 1)) for a, b in zip(segs, segs[1:]) if b[0] - a[1] > 0.2]
    lead = segs[0][0] if segs else dur
    tail = dur - segs[-1][1] if segs else 0
    dead = sum(g[0] for g in gaps) + max(0, lead - 0.15)
    worst = max([g[0] for g in gaps], default=0)
    ok = bool(segs) and worst <= MAXGAP and dead / dur <= MAXDEAD
    bad += not ok
    print(f"{'PASS' if ok else 'FAIL'} {Path(v).stem[:24]:24} dur {dur:4.1f}s dead {dead:4.1f}s ({100 * dead / dur:3.0f}%) "
          f"lead {lead:.2f} tail {tail:.2f} worst {worst:.2f}  " + " ".join(f"{g[1]}:{g[0]}" for g in gaps if g[0] > 0.3))
sys.exit(1 if bad else 0)
