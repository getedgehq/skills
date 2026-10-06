#!/usr/bin/env python3
"""Speed ramp with interpolated frames (never a snap and freeze).

One continuous ramp 1.0x -> vmin -> 1.0x with a sine-eased speed, v(u) = 1 - (1 - vmin) * sin^2(pi u), u in [0, 1].
The source span it consumes is out_dur * rate * (1 + vmin) / 2, so the ramp lags the voice by
out_dur * (1 - vmin) / 2: insert that much pause (covered by room tone or a whoosh) at a word boundary inside the ramp,
and start every later clip that much later. Frames come from motion interpolation (ffmpeg minterpolate mci at
--fps-hi), not from duplicated frames. Output is all-intra H.264 for exact seeking in the editor.
  python3 ramp.py source.mov ramp.mp4 --src-start 2.46 --out-dur 1.0 --rate 1.2 --vmin 0.4
Slow: minterpolate at 1440x1920 runs about 2 minutes per second of source; run it detached and poll.
"""
import argparse, math, os, shutil, subprocess, tempfile

ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--src-start", type=float, required=True, help="source second where the ramp begins")
ap.add_argument("--out-dur", type=float, default=1.0); ap.add_argument("--rate", type=float, default=1.0, help="the reel's playback rate")
ap.add_argument("--vmin", type=float, default=0.4); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--fps-hi", type=int, default=120)
a = ap.parse_args()
FF = os.environ.get("IRM_FFMPEG") or shutil.which("ffmpeg") or "/usr/bin/ffmpeg"
n = round(a.out_dur * a.fps); span = a.out_dur * a.rate * (1 + a.vmin) / 2
pos = lambda u: a.out_dur * a.rate * (u - (1 - a.vmin) * (u / 2 - math.sin(2 * math.pi * u) / (4 * math.pi)))
pad = 0.06; s0 = max(0.0, a.src_start - pad)
tmp = tempfile.mkdtemp(); hi = f"{tmp}/hi.mp4"
subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-ss", f"{s0:.4f}", "-i", a.src, "-t", f"{span + 2 * pad:.4f}", "-an", "-vf", f"minterpolate=fps={a.fps_hi}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-c:v", "libx264", "-crf", "12", "-preset", "fast", hi], check=True)
idx = [round((a.src_start + pos(i / n) - s0) * a.fps_hi) for i in range(n)]
sel = "+".join(f"eq(n\\,{k})" for k in idx)
subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", hi, "-vf", f"select='{sel}',setpts=N/{a.fps}/TB", "-r", str(a.fps), "-c:v", "libx264", "-crf", "14", "-g", "1", "-pix_fmt", "yuv420p", a.dst], check=True)
print(f"{a.dst}: {n} frames, source {a.src_start:.3f} + {span:.3f} s; voice lag to cover {a.out_dur * (1 - a.vmin) / 2:.3f} s; frame indices {idx}")
