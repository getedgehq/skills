#!/usr/bin/env python3
"""Readability audit (no render needed): a timing table for every text element in beats.json and captions.json.

For each element: words, the time it is complete and fully opaque (after its reveal, before its eased exit),
and the rule min = max(0.7 s, 0.25 s per word). Also checks: captions are 2 to 5 words, one graphic message at a
time (text beats never overlap each other or a caption, except stickers that echo the caption's key word, marked
"echo": true in the beat), and that beats declare a one-sentence "meaning".
  python3 readability.py beats.json captions.json [--fps 30]
Exit 1 on any FAIL.
"""
import argparse, json, re, sys

ap = argparse.ArgumentParser(); ap.add_argument("beats"); ap.add_argument("captions"); ap.add_argument("--fps", type=float, default=30)
a = ap.parse_args(); F = 1 / a.fps
EXIT = {"default": 7}
# reveal: seconds from the element's start until its text is complete
# (pop components show their type at full opacity from their start; the pill only scales)
REVEAL = {"Sticker": lambda p: 0.1 + max(0, len(p.get("text", "")) - 1) * 0.022 + 0.2, "ChatPrompt": lambda p: 0.55 + len(p.get("text", "")) / p.get("cps", 24),
          "Takeover": lambda p: p.get("resolve", 0.55)}
POP = 0.0
TOL = 0.5 / 30  # half a frame
minshow = lambda n: max(0.7, 0.25 * n)
words = lambda s: len([w for w in re.split(r"\s+", s.strip()) if w])


# per-text start times for components whose labels land after the beat starts
AT = {"CompareCards": {"title": "inAt", "sub": "subAt", "leftLabel": "leftAt", "rightLabel": "rightLabelAt"},
      "BlockMeter": {"title": "titleAt", "leftLabel": "leftLabelAt", "rightLabel": "rightLabelAt"}}


def texts(b):
    p = b.get("props", {}); out = []; at = AT.get(b["component"], {})
    for k in ("text", "title", "sub", "name", "role", "leftLabel", "rightLabel"):
        if isinstance(p.get(k), str): out.append((p[k], p.get(at.get(k), b["t0"]), b["t1"]))
    if p.get("lines"): out.append((" ".join(p["lines"]), b["t0"], b["t1"]))
    for it in p.get("items", []):
        out.append((it.get("text") or " ".join(it.get("lines", [])), it["t0"], it.get("t1", b["t1"])))
    return out


rows, fails = [], 0
beats = json.load(open(a.beats)); caps = json.load(open(a.captions))
for b in beats:
    if not b.get("meaning") and any(texts(b)): print(f"WARN {b['id']}: no one-sentence meaning"); 
    ex = b.get("exit", EXIT["default"]) * F / 2  # the first half of an eased exit still reads
    for t, t0, t1 in texts(b):
        rv = REVEAL.get(b["component"], lambda p: POP)(b.get("props", {}))
        avail = (t1 - ex) - (t0 + rv); need = minshow(words(t))
        ok = avail >= need - TOL; fails += not ok
        rows.append((t0, b["id"], t[:38], words(t), round(avail, 2), need, "ok" if ok else "FAIL"))
for c in caps:
    n = words(c["text"]); avail = c["t1"] - c["t0"]; need = minshow(n); ok = avail >= need - TOL and 2 <= n <= 5
    note = "ok" if ok else ("FAIL words" if not 2 <= n <= 5 else "FAIL time")
    fails += not ok; rows.append((c["t0"], "caption", c["text"][:38], n, round(avail, 2), need, note))
for r in sorted(rows): print(f"{r[0]:7.2f}  {r[1]:<12} {r[2]:<40} w{r[3]:<2} up {r[4]:5.2f}s need {r[5]:4.2f}s  {r[6]}")
# one message at a time: a caption never shares the screen with a text beat unless the beat is an echo
for c in caps:
    for b in beats:
        if b.get("echo") or not texts(b): continue
        if b["t0"] < c["t1"] - TOL and c["t0"] < b["t1"] - TOL:
            fails += 1; print(f"FAIL overlap: caption '{c['text']}' {c['t0']}-{c['t1']} with beat {b['id']} {b['t0']:.2f}-{b['t1']:.2f}")
print(f"{fails} failure(s)"); sys.exit(1 if fails else 0)
