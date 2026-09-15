#!/usr/bin/env python3
"""Check whether a video is ready to be scrubbed on scroll.

Usage: check-scrub.py <video> [--budget-mb 12] [--max-keyframe-gap 4]

Reports keyframe spacing, audio, moov position (faststart), size and duration.
Exits 1 if any check fails, so it can gate a build.
"""
import argparse
import json
import os
import subprocess
import sys


def ffprobe(args):
    out = subprocess.run(["ffprobe", "-v", "error", *args], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"error: ffprobe failed: {out.stderr.strip()}")
    return out.stdout


def moov_before_mdat(path):
    """Walk top-level MP4 boxes and report whether moov comes before mdat."""
    with open(path, "rb") as f:
        while True:
            header = f.read(8)
            if len(header) < 8:
                return None
            size = int.from_bytes(header[:4], "big")
            kind = header[4:8]
            if kind == b"moov":
                return True
            if kind == b"mdat":
                return False
            if size == 1:
                size = int.from_bytes(f.read(8), "big")
                f.seek(size - 16, 1)
            elif size == 0:
                return None
            else:
                f.seek(size - 8, 1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--budget-mb", type=float, default=12)
    p.add_argument("--max-keyframe-gap", type=int, default=4)
    a = p.parse_args()

    info = json.loads(ffprobe(["-show_streams", "-show_format", "-of", "json", a.video]))
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if not video:
        sys.exit("error: no video stream")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])

    flags = ffprobe(["-select_streams", "v:0", "-show_entries", "packet=flags",
                     "-of", "csv=p=0", a.video]).split()
    key_idx = [i for i, fl in enumerate(flags) if "K" in fl]
    gaps = [b - a_ for a_, b in zip(key_idx, key_idx[1:])] or [len(flags)]
    max_gap = max(gaps)

    size_mb = os.path.getsize(a.video) / 1e6
    duration = float(info["format"].get("duration", 0))
    faststart = moov_before_mdat(a.video)

    checks = [
        (f"keyframe gap <= {a.max_keyframe_gap} frames", max_gap <= a.max_keyframe_gap, f"max gap {max_gap} over {len(flags)} frames"),
        ("no audio track", not has_audio, "audio present" if has_audio else "none"),
        ("moov before mdat (faststart)", faststart is True, str(faststart)),
        (f"size <= {a.budget_mb:g} MB", size_mb <= a.budget_mb, f"{size_mb:.1f} MB"),
    ]
    print(f"{a.video}: {video['width']}x{video['height']} {video.get('codec_name')} "
          f"{video.get('avg_frame_rate')} fps, {duration:.1f}s")
    ok = True
    for name, passed, detail in checks:
        ok &= passed
        print(f"  {'PASS' if passed else 'FAIL'}  {name}  ({detail})")
    if max_gap > a.max_keyframe_gap:
        print("  fix: run encode-scrub.sh on this file")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
