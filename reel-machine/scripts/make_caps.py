#!/usr/bin/env python3
"""Draft caption chunks for build_reel.py, or validate a curated caption file.

Draft (prints a numbered list, writes JSON in EDITED seconds = cut timeline):
  make_caps.py draft --transcript T.json --segments '[{"start":..,"end":..}]' --out caps.json

Validate (every caption must be a one-liner, every second-language line must fit, no periods,
in order, no banned words from REEL_BANNED_WORDS, no em or en dashes):
  make_caps.py check caps.json

Curate by hand from the draft: merge/split chunks on phrase boundaries, keep the spoken words
(filler may go), add (parentheticals) for jargon, optionally add "en" per cap for a translation line.
Derived from video-use (MIT, see THIRD_PARTY_NOTICES.md).
"""
import argparse, json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

FILLER = {"ähm", "äh", "ähm,", "äh,", "em", "uh", "um", "uh,", "um,", "hm", "ähmm"}
CAP_MAX, EN_MAX = 815, 780  # px at 44px / 30px caption font (W-260 / W-300)


def draft(a):
    segs = sorted((float(s["start"]), float(s["end"])) for s in json.loads(a.segments))

    def to_edited(t):
        c = 0.0
        for s, e in segs:
            if t < s:
                return c
            if t <= e:
                return c + t - s
            c += e - s
        return c

    def seg_of(t):
        for i, (s, e) in enumerate(segs):
            if s - 0.001 <= t < e:
                return i

    words = [w for w in json.load(open(a.transcript))["words"] if w.get("type") == "word"]
    cw = []
    for w in words:
        si = seg_of(w["start"])
        if si is None or w["text"].strip().lower() in FILLER:
            continue
        cw.append((w["text"].strip(), to_edited(w["start"]), to_edited(min(w["end"], segs[si][1])), si))
    caps, cur = [], []

    def flush():
        if cur:
            t = re.sub(r"\s+", " ", " ".join(x[0] for x in cur).replace(".", "")).strip()
            caps.append({"text": t, "en": "", "start": round(cur[0][1], 2), "end": round(cur[-1][2], 2)})
        cur.clear()

    for i, (raw, s, e, si) in enumerate(cw):
        cur.append((raw, s, e, si))
        n = cw[i + 1] if i + 1 < len(cw) else None
        if raw.endswith((".", "!", "?")) or not n or n[1] - e > 0.35 or len(cur) >= 3 or n[3] != si:
            flush()
    json.dump(caps, open(a.out, "w"), ensure_ascii=False, indent=1)
    for i, c in enumerate(caps):
        print(f"{i:3d} {c['start']:7.2f} {c['end']:7.2f}  {c['text']}")
    print(f"\n{len(caps)} chunks -> {a.out}  (edited duration {sum(e - s for s, e in segs):.2f}s)")


def check(a):
    path, idx = rmconf.caption_font()
    d = ImageDraw.Draw(Image.new("RGBA", (9, 9)))
    main = rmconf.bold(ImageFont.truetype(path, 44, index=idx))
    en = rmconf.bold(ImageFont.truetype(path, 30, index=idx))
    banned = [w.strip().lower() for w in rmconf.get("REEL_BANNED_WORDS").split(",") if w.strip()]
    caps, bad = json.load(open(a.file)), 0
    for i, c in enumerate(caps):
        for key, font, mx in (("text", main, CAP_MAX), ("en", en, EN_MAX)):
            if c.get(key) and d.textlength(c[key], font=font) > mx:
                bad += 1
                print(f"TOO WIDE #{i} {key}: {c[key]!r} ({d.textlength(c[key], font=font):.0f}px > {mx})")
            if c.get(key) and ("—" in c[key] or "–" in c[key]):
                bad += 1
                print(f"DASH #{i} {key}: {c[key]!r}")
            for w in banned:
                if c.get(key) and re.search(r"\b" + re.escape(w) + r"\b", c[key].lower()):
                    bad += 1
                    print(f"BANNED #{i} {key}: {w!r} in {c[key]!r}")
        if "." in re.sub(r"\.(com|ai|io|cc|\d)", "", c["text"]):
            print(f"period #{i}: {c['text']!r} (captions carry no periods)")
        if i and c["start"] < caps[i - 1]["start"]:
            bad += 1
            print(f"OUT OF ORDER #{i}")
    print(f"{len(caps)} caps, {bad} problems")
    sys.exit(1 if bad else 0)


p = argparse.ArgumentParser()
sp = p.add_subparsers(dest="cmd", required=True)
d1 = sp.add_parser("draft")
d1.add_argument("--transcript", required=True)
d1.add_argument("--segments", required=True)
d1.add_argument("--out", required=True)
d2 = sp.add_parser("check")
d2.add_argument("file")
a = p.parse_args()
draft(a) if a.cmd == "draft" else check(a)
