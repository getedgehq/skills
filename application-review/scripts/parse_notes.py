#!/usr/bin/env python3
"""Parse the notes a reviewer sent back from the review page ("Send my notes") into JSON.

Usage: python3 parse_notes.py notes.txt [app.json]   (or pipe the text on stdin with "-")
Several reviewers' texts can be pasted into one file; each starts with a "Review notes" line.
With app.json, each question block is matched back to its question and the answer text.
"""
import json, re, sys
from pathlib import Path

HEAD = re.compile(r"^Review notes(?: from (?P<name>.+?))? on (?P<what>.+?) \(draft (?P<draft>[0-9a-f]{8})\)\s*$")
QH = re.compile(r"^## (?:Q(?P<n>\d+)\. (?P<q>.+)|(?P<gen>General))\s*$")


def parse(text):
    reviews, cur, block = [], None, None
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        m = HEAD.match(line.strip())
        if m:
            cur = {"reviewer": m["name"], "about": m["what"], "draft": m["draft"], "questions": [], "general": []}
            reviews.append(cur); block = None; continue
        if cur is None:
            continue
        m = QH.match(line.strip())
        if m:
            if m["gen"]:
                block = cur["general"]
            else:
                q = {"n": int(m["n"]), "q": m["q"], "notes": []}
                cur["questions"].append(q); block = q["notes"]
            continue
        if block is None:
            continue
        if line.lstrip().startswith("- ") and not raw.startswith("  "):
            block.append(line.lstrip()[2:])
        elif raw.startswith("  ") and block:
            block[-1] += "\n" + raw[2:]
    return reviews


def main():
    src = sys.stdin.read() if len(sys.argv) < 2 or sys.argv[1] == "-" else Path(sys.argv[1]).read_text()
    out = parse(src)
    if len(sys.argv) > 2:
        items = json.loads(Path(sys.argv[2]).read_text())["items"]
        for r in out:
            for q in r["questions"]:
                it = items[q["n"] - 1] if 0 < q["n"] <= len(items) else None
                q["matches_question"] = bool(it and it["q"].strip() == q["q"].strip())
                if it:
                    q["answer"] = it["a"]
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
