#!/usr/bin/env python3
"""Caption diff: transcribe the final reel with faster-whisper (word timestamps) and check that every caption
word is heard while its line is on screen (+-0.25 s). Lists missing words per line; digits match any number.
  python3 whisper_diff.py reel.mp4 captions.json [--model medium]
"""
import argparse, json, re
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("captions")
ap.add_argument("--model", default="medium"); a = ap.parse_args()
norm = lambda x: re.sub(r"[^a-z0-9']", "", x.lower().replace(",", "").replace("-", ""))
segs, _ = WhisperModel(a.model, device="cpu", compute_type="int8").transcribe(a.video, language="en", word_timestamps=True, vad_filter=False)
tx = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
ok, bad = 0, []
for l in json.load(open(a.captions)):
    heard = [w for w, s, e in tx if e > l["t0"] - 0.25 and s < l["t1"] + 0.25]
    miss = [w for w in map(norm, l["text"].split()) if w not in heard and not (w.isdigit() and any(h.isdigit() for h in heard))]
    if miss: bad.append((l["t0"], l["text"], miss, " ".join(heard)))
    else: ok += 1
print(f"caption lines {ok + len(bad)}: all words heard {ok}, with misses {len(bad)}")
for b in bad: print("  ", b)
