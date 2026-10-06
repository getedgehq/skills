#!/usr/bin/env python3
"""The ending: a 6 fps strip of the last 2 s (12 tiles). Check for a natural expression, a held frame with a slow
eased push, a 10 to 15 frame fade, and no outro or branding frame.
  python3 last2s.py reel.mp4 [last2s.jpg]
"""
import subprocess, sys
from common import FFMPEG

v = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "last2s.jpg"
subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-sseof", "-2", "-i", v, "-vf", "fps=6,scale=216:-2,tile=6x2", "-frames:v", "1", "-q:v", "3", out], check=True)
print(out)
