#!/usr/bin/env python3
"""voiceclean.py IN.mp4 OUT.mp4

Keeps the real voice. Gentle EQ (rumble and mud cut, presence lift) + loudness normalisation;
the video stream is copied untouched. EQ and loudness come from config:
  REEL_VOICE_EQ   ffmpeg filter chain (default: highpass 90 Hz, -3 dB at 220 Hz, +2 dB at 3.3 kHz)
  REEL_LOUDNORM   loudnorm target (default I=-15:TP=-2:LRA=7)
Tune the EQ to the voice and the mic; the defaults suit a phone mic held at arm's length.

There is deliberately no voice isolation or denoise step. Model-based isolation made voices
sound robotic: a robotic-voice detector scored raw phone audio about 0.002 and the isolated
versions 0.27 to 1.0, and listeners agreed. Raw voice with light EQ wins.
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, out = sys.argv[1], sys.argv[2]
af = ",".join(x for x in (rmconf.get("REEL_VOICE_EQ"), "loudnorm=" + rmconf.get("REEL_LOUDNORM")) if x)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print(f"voiceclean ok {out}")
