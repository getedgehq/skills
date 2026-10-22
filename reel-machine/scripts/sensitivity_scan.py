#!/usr/bin/env python3
"""sensitivity_scan.py FILE [FILE ...] [--text "hook or post caption"] [--posted YYYY-MM-DD]

Pre-screen for references/sensitivity-rules.md. Reads Scribe transcripts (words with times)
or caps.json files (text + times) and free text, and prints every line that touches a rule:

  R1 raise talk        R2 crime speculation   R3 distress
  R4 private data      R5 dated promise       S  swearing (cut by default)

It flags; it never cuts. Each hit needs a decision: cut the segment, keep it (and say why),
or show the owner. --posted adds a reminder to check every R5 line against the post date,
since a promise filmed weeks ago can be false by the time the reel goes out.
Exit 0 with no hits, 3 with hits.
"""
import argparse, json, re

RULES = {
    "R1 raise": r"\b(investors?|investing|invest(ed)? in us|raising|our round|the round|pre-?seed|seed round|series [a-c]|"
                r"term ?sheets?|valuation|cap table|safe note|fundrais\w*|vcs?|angels?|lead investor|check size|close the round)\b",
    "R2 crime": r"\b(drugs?|dealer|dealing|fentanyl|crack|meth|stolen|stealing|steal|thief|thieves|robb\w*|shoplift\w*|"
                r"criminal|illegal|arrest\w*|cops?|police)\b",
    "R3 distress": r"\b(fight|fighting|overdos\w*|passed out|homeless|unhoused|tent|crying|screaming|ambulance|bleeding)\b",
    "R4 private": r"([\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s().-]{8,}\d|\b(password|api key|token|secret|customer|client name|"
                  r"address|social security|unannounced|not public yet|under nda)\b)",
    "R5 dated": r"\b(tomorrow|tonight|next (week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
                r"this (week|weekend|month|friday|saturday|sunday)|in (two|three|a few) (days|weeks)|"
                r"i('m| am) going to|i will|we will|we're launching|launching (soon|next))\b",
    "S swear": r"\b(fuck\w*|shit\w*|bitch\w*|asshole|damn|crap|bullshit|wtf)\b",
}
RX = {k: re.compile(v, re.I) for k, v in RULES.items()}


def lines_from(path):
    j = json.load(open(path))
    if isinstance(j, list):  # caps.json
        return [(c.get("start", 0), c.get("text", "") + (" / " + c["en"] if c.get("en") else "")) for c in j]
    out, cur, t0 = [], [], None
    for w in j.get("words", []):
        if w.get("type") != "word":
            continue
        t0 = w["start"] if t0 is None else t0
        cur.append(w["text"])
        if w["text"].endswith((".", "?", "!")) or len(cur) >= 18:
            out.append((t0, " ".join(cur))); cur, t0 = [], None
    if cur:
        out.append((t0, " ".join(cur)))
    return out


ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="*")
ap.add_argument("--text", action="append", default=[])
ap.add_argument("--posted", help="post date, to remind you to check dated words against it")
a = ap.parse_args()
src = [(f, lines_from(f)) for f in a.files] + [("text", [(0, t) for t in a.text])]
hits = 0
for name, lines in src:
    for t, ln in lines:
        tags = [k for k, rx in RX.items() if rx.search(ln)]
        if tags:
            hits += 1
            print(f"{name} @{t:6.2f}s [{', '.join(tags)}] {ln}")
print(f"\n{hits} line(s) flagged." + (f" Check every R5 line against the post date {a.posted}." if a.posted else "")
      + " Decide each: cut, keep with a reason, or show the owner.")
raise SystemExit(3 if hits else 0)
