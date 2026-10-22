#!/usr/bin/env python3
"""precut.py SRC SEGMENTS.json OUT.mov  -> prints [{"start":0,"end":<dur>}] for build_reel.py

One pass, one seeked input per segment + a concat filter: every segment's audio and video
start together, so there is no drift and memory stays flat however many segments you keep.
A segment may name another clip with "src": it is looked up as clips/<src>.mov (or
<src>_cut.mov, .mp4) relative to the current directory. Mixed clips are normalised to
1080x1920. Fails loudly if the output duration differs from the segment sum by > 0.5 s.
"""
import json, os, subprocess, sys

src, segf, out = sys.argv[1], sys.argv[2], sys.argv[3]
segs = json.load(open(segf)); args = []; fc = []; ins = ""


def clip(name):
    if not name:
        return src
    for p in (f"clips/{name}.mov", f"clips/{name}_cut.mov", f"clips/{name}.mp4", f"clips/{name}.MOV"):
        if os.path.exists(p):
            return p
    sys.exit(f"precut: no clip for src={name}")


mixed = len({s.get("src") for s in segs}) > 1
norm = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1," if mixed else ""
for k, s in enumerate(segs):
    args += ["-ss", str(s["start"]), "-to", str(s["end"]), "-i", clip(s.get("src"))]
    fc.append(f"[{k}:v]{norm}setpts=PTS-STARTPTS[v{k}]")
    fc.append(f"[{k}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono[a{k}]")
    ins += f"[v{k}][a{k}]"
fc.append(f"{ins}concat=n={len(segs)}:v=1:a=1[cv][ca];[cv]fps=30[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[ca]",
                "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "pcm_s16le", "-ac", "1", out], check=True)
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                         capture_output=True, text=True).stdout)
want = sum(s["end"] - s["start"] for s in segs)
if abs(d - want) > 0.5:
    sys.exit(f"precut: duration {d:.2f}s but segments sum to {want:.2f}s")
print(json.dumps([{"start": 0, "end": round(d, 3)}]))
