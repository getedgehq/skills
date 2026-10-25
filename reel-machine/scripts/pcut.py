#!/usr/bin/env python3
"""pcut.py IN.mp4 OUT.mp4 [--speed X] [--caps caps.json] [--headfreeze S] [--tailmax S]

Jump cuts on speech found by Silero VAD: every inner silence shrinks to ~0.10 s (0.05 s pad each
side), the lead-in to 0.05 s (under 0.15 s), and the tail after the last word keeps up to
--tailmax (1.0 s) so the closer still lands. 10 ms audio fades at every splice, no clicks.

Speed: --speed sets it. With --caps (the bundle's caps.json) and no --speed, the words per second
after cutting are measured; below REEL_MIN_WPS (2.6) the reel is sped up to reach it, between
1.1x and REEL_MAX_TEMPO (1.15x) with atempo (pitch kept). --headfreeze holds a later frame over
the first S seconds (a blink on frame 0 would otherwise be the thumbnail).

One seeked input per kept piece: a single input split into many trims buffers every frame and
runs out of memory on long reels. Run vadgaps.py on OUT afterwards.
"""
import argparse, json, subprocess, sys
from pathlib import Path
import av, numpy as np
from faster_whisper.vad import get_speech_timestamps, VadOptions

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

PAD, FADE = 0.05, 0.01
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--speed", type=float); ap.add_argument("--caps")
ap.add_argument("--headfreeze", type=float, default=0.0); ap.add_argument("--tailmax", type=float, default=1.0)
ap.add_argument("--plan-only", action="store_true", help="write OUT.json and OUT.fc, do not encode")
a = ap.parse_args()

c = av.open(a.src); dur = float(c.duration) / 1e6; st = c.streams.audio[0]
rs = av.AudioResampler(format="flt", layout="mono", rate=16000); buf = []
for f in c.decode(st):
    for r in rs.resample(f):
        buf.append(r.to_ndarray().reshape(-1))
x = np.concatenate(buf).astype(np.float32)
ts = get_speech_timestamps(x, VadOptions(threshold=0.5, min_silence_duration_ms=90, speech_pad_ms=0))
sp = [(t["start"] / 16000, t["end"] / 16000) for t in ts]
if not sp:
    sys.exit("pcut: no speech found")
keep = []
for s, e in sp:
    s, e = max(0, s - PAD), min(dur, e + PAD)
    if keep and s <= keep[-1][1] + 0.02:
        keep[-1][1] = e
    else:
        keep.append([s, e])
keep[-1][1] = min(dur, sp[-1][1] + a.tailmax)
cut_dur = sum(e - s for s, e in keep)

speed = a.speed
if speed is None:
    speed = 1.0
    if a.caps:
        nw = sum(len(cp["text"].split()) for cp in json.load(open(a.caps)))
        wps = nw / max(0.1, cut_dur)
        want = float(rmconf.get("REEL_MIN_WPS"))
        if wps < want:
            speed = round(min(float(rmconf.get("REEL_MAX_TEMPO")), max(1.1, want / wps)), 3)
        print(f"pcut: {nw} words, {wps:.2f} words/s after cuts -> speed {speed}")

fc, inputs = [], []
for i, (s, e) in enumerate(keep):
    L = e - s
    inputs += ["-ss", f"{s:.3f}", "-t", f"{L:.3f}", "-i", a.src]
    if i == 0 and a.headfreeze:
        fc.append(f"[{i}:v]trim={a.headfreeze:.3f},setpts=PTS-STARTPTS,tpad=start_duration={a.headfreeze}:start_mode=clone[v{i}];")
    else:
        fc.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];")
    fc.append(f"[{i}:a]asetpts=PTS-STARTPTS,afade=t=in:d={FADE},afade=t=out:st={max(0, L - FADE):.3f}:d={FADE}[a{i}];")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[vc][ac];")
fc.append(f"[vc]setpts=PTS/{speed}[vo];[ac]atempo={speed}[ao]" if speed != 1.0 else "[vc]null[vo];[ac]anull[ao]")
plan = Path(a.out).with_suffix("")
Path(f"{plan}.fc").write_text("\n".join(fc))
json.dump({"keep": keep, "dur": dur, "newdur": cut_dur / speed, "speech": sum(e - s for s, e in sp), "speed": speed},
          open(f"{plan}.json", "w"))
print(f"pcut: {dur:.1f}s -> {cut_dur / speed:.1f}s, {len(keep)} pieces, lead-in {sp[0][0] - keep[0][0]:.2f}s (was {sp[0][0]:.2f}), speed {speed}")
if a.plan_only:
    sys.exit(0)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex_script", f"{plan}.fc",
                "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], check=True)
print(f"pcut ok {a.out}")
