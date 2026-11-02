#!/usr/bin/env python3
"""Post draft gate: deterministic checks on a LinkedIn or X post draft. Standard library only, no network.

  python3 gate.py --channel linkedin|x draft.txt [--rules my-rules.json] [--comment "first comment"] [--original theirs.txt] [--asked N]

Exit 0 = PASS, 1 = FAIL. One line per check."""
import argparse
import json
import os
import re
import sys

DEFAULTS = {"max_words_linkedin": 180, "max_chars_x": 280, "max_line1_words": 12, "max_number_lines": 3,
            "allow_dashes": False, "link_param": "", "banned_phrases": [], "jargon": [], "custom": []}
HEDGES = r"\b(almost|probably|maybe|basically|kind of|sort of|perhaps|i think|somewhat)\b"
DISCLAIMERS = r"(to be fair|the honest part|caveat|take it for what it is|take it with a grain|disclaimer|not a (general|scientific) (benchmark|study))"
SCAFFOLD = r"(here(?:'s| is) what nobody (mentions|tells you)|the (real )?question is not|everyone (gives the same advice|tells you)|the part nobody (mentions|tells you)|let that sink in)"


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s.lower())).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--channel", required=True, choices=["linkedin", "x"])
    ap.add_argument("--rules", default="")
    ap.add_argument("--comment", default="", help="first comment or reply text")
    ap.add_argument("--original", default="", help="the author's own text when this is an edit")
    ap.add_argument("--asked", type=int, default=0, help="extra changed lines the author asked for")
    a = ap.parse_args()

    R = dict(DEFAULTS)
    if a.rules:
        R.update({k: v for k, v in json.load(open(a.rules)).items() if not k.startswith("_")})
    T = open(a.file).read().replace("\u2028", "\n").strip()
    lines = [l for l in T.splitlines() if l.strip()]
    L1 = lines[0].strip() if lines else ""
    allt = T + "\n" + a.comment
    res = []

    def chk(name, ok, why=""):
        res.append((name, bool(ok), why))

    if a.original:
        O = [l.strip() for l in open(a.original).read().replace("\u2028", "\n").splitlines() if l.strip()]
        on = {norm(x) for x in O}
        joined = " | ".join(on)
        changed = [l for l in lines if norm(l) not in on and norm(l) not in joined]
        chk("edit keeps their line 1", O and norm(L1) == norm(O[0]), "line 1 changed: keep their opener")
        chk("edit changes at most 3 lines", len(changed) <= 3 + a.asked, f"{len(changed)} new lines: this is a rewrite, not an edit")

    if not R["allow_dashes"]:
        chk("no em or en dash", not re.search("[—–]", allt), "replace with a period, comma, colon or parentheses")
    if a.channel == "linkedin":
        n = len(T.split())
        chk(f"LinkedIn at most {R['max_words_linkedin']} words", n <= R["max_words_linkedin"], f"{n} words")
        low = [l for l in lines if re.match(r"^[a-z]", l.strip()) and not l.strip().startswith(("http", ">"))]
        chk("LinkedIn lines start with a capital", not low, f"lowercase line: {low[:1]}")
    else:
        chk(f"X main post at most {R['max_chars_x']} characters", len(T) <= R["max_chars_x"], f"{len(T)} characters")
    chk(f"line 1 at most {R['max_line1_words']} words", len(L1.split()) <= R["max_line1_words"], f"{len(L1.split())} words")
    d = re.findall(DISCLAIMERS, T, re.I)
    chk("no disclaimers", not d, f"{[x[0] if isinstance(x, tuple) else x for x in d]}")
    h = sorted(set(m.lower() for m in re.findall(HEDGES, T, re.I)))
    chk("no hedge words", not h, ", ".join(h))
    if not a.original:
        nl = [l for l in lines if re.search(r"\d", re.sub(r"^\s*\d{1,2}[).]\s", "", l))]
        chk(f"no stat stack (at most {R['max_number_lines']} lines with numbers)", len(nl) <= R["max_number_lines"], f"{len(nl)} lines with numbers")
    s = re.findall(SCAFFOLD, T, re.I)
    chk("no essay scaffold", not s, "everyone-says / nobody-tells-you scaffold reads as generated")
    for label, key in (("no banned phrases", "banned_phrases"), ("no insider jargon", "jargon")):
        hits = [p for p in R[key] if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", T, re.I)]
        chk(label, not hits, f"{hits}")
    if R["link_param"]:
        urls = re.findall(r"https?://\S+", allt)
        bare = [u for u in urls if R["link_param"] not in u]
        chk(f"links carry {R['link_param']}", not bare, f"{bare[:2]}")
    for c in R["custom"]:
        chk(c["name"], not re.search(c["pattern"], T, re.I | re.M), c.get("why", ""))

    fails = [r for r in res if not r[1]]
    for n, ok, w in res:
        print(("PASS " if ok else "FAIL ") + n + ("" if ok else "  -> " + w))
    print("\nGATE: " + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    print("Next: run the cold reader on line 1 (see SKILL.md).")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
