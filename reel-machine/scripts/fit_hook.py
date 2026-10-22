#!/usr/bin/env python3
"""Largest HOOK_SIZE (<= 78) at which a 2-line hook fits the frame width.

  fit_hook.py $'I made Claude ask ChatGPT\\nfor a second opinion'

Prints HOOK_SIZE=<n>. Without "\\n" it tries every 2-line split and prints the best one.
Inline icons are not measured here; keep icon lines a few words shorter.
Derived from video-use (MIT, see THIRD_PARTY_NOTICES.md).
"""
import sys
from pathlib import Path
from PIL import ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

W, MARGIN, CAP, FLOOR = 1080, 174, 78, 60
FONT = rmconf.hook_font()


def width(lines, size):
    f = rmconf.bold(ImageFont.truetype(FONT, size))
    return max(f.getlength(l) for l in lines)


def best_size(lines):
    for size in range(CAP, 20, -1):  # measure, don't extrapolate (kerning isn't linear)
        if width(lines, size) <= W - MARGIN:
            return size
    return 20


text = sys.argv[1]
if "\n" in text:
    cands = [[l.strip() for l in text.split("\n") if l.strip()]]
else:
    ws = text.split()
    cands = [[" ".join(ws[:i]), " ".join(ws[i:])] for i in range(1, len(ws))] or [[text]]
lines = max(cands, key=best_size)
size = best_size(lines)
print(f"lines: {lines}")
print(f"HOOK_SIZE={size}")
if len(lines) > 2:
    print("WARNING: more than 2 lines. Keep the hook to exactly 2.")
if size < FLOOR:
    print(f"WARNING: {size}px is barely bigger than captions (44px). Shorten the text instead of shrinking it.")
