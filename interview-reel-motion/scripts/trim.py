#!/usr/bin/env python3
"""Trim the export by frame count (the editor may append an outro frame): keeps exactly round(duration * fps)
frames, re-encodes H.264 yuv420p with AAC and faststart, then writes the last-2s strip.
  python3 trim.py export.mp4 final.mp4 --duration 42.167 [--crf 16]
"""
import argparse, subprocess
from common import FFMPEG, FFPROBE

ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--duration", type=float, required=True); ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--crf", type=int, default=16)
a = ap.parse_args(); n = round(a.duration * a.fps)
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-i", a.src, "-frames:v", str(n), "-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.dst], check=True)
got = subprocess.run([FFPROBE, "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", a.dst], capture_output=True, text=True).stdout.strip()
print(f"{a.dst}: {got} frames (wanted {n})")
subprocess.run(["python3", __file__.replace("trim.py", "last2s.py"), a.dst, a.dst.rsplit(".", 1)[0] + "_last2s.jpg"], check=True)
