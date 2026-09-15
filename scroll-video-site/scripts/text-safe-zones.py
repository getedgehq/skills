#!/usr/bin/env python3
"""Find where text can sit on a background video without an overlay.

Usage: text-safe-zones.py <video> [--samples 24]

Samples frames across the clip, splits each into a 3x3 grid and measures, per
cell, mean brightness and busyness (local contrast). A cell is "calm" when it
stays low-contrast in every sampled frame. Brightness picks the text color.
"""
import argparse
import json
import subprocess
import sys

GRID = 3
SUB = 8  # sub-samples per cell side
NAMES = [["top-left", "top-center", "top-right"],
         ["middle-left", "center", "middle-right"],
         ["bottom-left", "bottom-center", "bottom-right"]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--samples", type=int, default=24)
    a = p.parse_args()

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", a.video],
        capture_output=True, text=True)
    if probe.returncode != 0:
        sys.exit(f"error: ffprobe could not read {a.video}: {probe.stderr.strip()}")
    dur = float(json.loads(probe.stdout)["format"]["duration"])
    side = GRID * SUB
    stats = [[{"luma": [], "busy": []} for _ in range(GRID)] for _ in range(GRID)]

    for i in range(a.samples):
        t = dur * (i + 0.5) / a.samples
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1",
             "-vf", f"scale={side}:{side},format=gray", "-f", "rawvideo", "-"],
            capture_output=True).stdout
        if len(raw) < side * side:
            continue
        for gy in range(GRID):
            for gx in range(GRID):
                px = [raw[(gy * SUB + y) * side + gx * SUB + x] for y in range(SUB) for x in range(SUB)]
                mean = sum(px) / len(px)
                std = (sum((v - mean) ** 2 for v in px) / len(px)) ** 0.5
                stats[gy][gx]["luma"].append(mean)
                stats[gy][gx]["busy"].append(std)

    if not stats[0][0]["luma"]:
        sys.exit("error: could not decode frames")

    print(f"{a.video}: {len(stats[0][0]['luma'])} frames sampled\n")
    print(f"{'cell':<14}{'brightness':>11}{'worst busy':>12}  verdict")
    rows = []
    for gy in range(GRID):
        for gx in range(GRID):
            s = stats[gy][gx]
            luma = sum(s["luma"]) / len(s["luma"])
            lo, hi = min(s["luma"]), max(s["luma"])
            busy = max(s["busy"])
            calm = busy < 28
            if hi < 110:
                color = "white text"
            elif lo > 150:
                color = "dark text"
            else:
                color = "mixed: white + soft shadow"
            verdict = ("calm, " if calm else "busy, avoid, ") + color
            rows.append((busy, NAMES[gy][gx], color, calm))
            print(f"{NAMES[gy][gx]:<14}{luma:>11.0f}{busy:>12.0f}  {verdict}")

    calm = sorted([r for r in rows if r[3]])
    print()
    if calm:
        print(f"headline: {calm[0][1]} ({calm[0][2]})")
    else:
        best = sorted(rows)[0]
        print(f"no calm cell. least busy: {best[1]}. Consider a calmer clip before adding any overlay.")


if __name__ == "__main__":
    main()
