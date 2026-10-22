#!/usr/bin/env python3
"""Print word timings from a Scribe transcript, so you can pick segment boundaries.

  words.py CLIP_STEM_OR_TRANSCRIPT              whole transcript, one line per sentence with times
  words.py CLIP_STEM_OR_TRANSCRIPT a-b [a-b]    every word with start-end inside those ranges

A stem prefix is resolved in $REEL_WORK/transcripts/.
"""
import glob, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf


def load(arg):
    if os.path.exists(arg):
        return json.load(open(arg))
    hits = glob.glob(str(rmconf.work() / "transcripts" / f"{arg}*.json"))
    if not hits:
        sys.exit(f"no transcript for {arg}")
    return json.load(open(hits[0]))


j = load(sys.argv[1])
ws = [x for x in j["words"] if x.get("type") == "word"]
if len(sys.argv) == 2:
    line, t0 = [], None
    for x in ws:
        t0 = x["start"] if t0 is None else t0
        line.append(x["text"])
        if x["text"].endswith((".", "?", "!")):
            print(f"{t0:7.2f}-{x['end']:7.2f}  {' '.join(line)}"); line, t0 = [], None
    if line:
        print(f"{t0:7.2f}-{ws[-1]['end']:7.2f}  {' '.join(line)}")
else:
    for r in sys.argv[2:]:
        a, b = map(float, r.split("-"))
        print(r, ": " + " ".join("%s@%.2f-%.2f" % (x["text"], x["start"], x["end"]) for x in ws if a <= x["start"] <= b))
