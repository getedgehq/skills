#!/usr/bin/env python3
"""Rank posts by engagement and compare groups with medians and n. Standard library only, no network.

  python3 signals.py posts.csv [more.csv] --out signals

Input header: platform,author,url,date,text,views,likes,comments,reposts,saves,followers,format,source
Writes <out>/signals.md and <out>/signals.json."""
import argparse
import csv
import json
import os
import re
import statistics as st

SMALL = 5


def num(x):
    x = (x or "").strip().replace(",", "")
    if not x:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kKmM]?)", x)
    if not m:
        return None
    v = float(m.group(1))
    return v * {"k": 1e3, "m": 1e6}.get(m.group(2).lower(), 1)


def opener(line):
    l = line.strip().lower()
    if not l:
        return "empty"
    if re.match(r'^[\$€£]?\d', l):
        return "number"
    if l.startswith(('"', "“", "'")):
        return "quote"
    if l.rstrip().endswith("?"):
        return "question"
    if re.match(r"^(how|why|what)\b", l):
        return "how/why"
    return "statement"


def load(paths):
    rows, notes = [], []
    for p in paths:
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                eng_parts = [num(r.get(k)) for k in ("likes", "comments", "reposts", "saves")]
                if all(v is None for v in eng_parts):
                    notes.append(f"no engagement numbers: {r.get('url') or (r.get('text') or '')[:40]!r} (skipped)")
                    continue
                eng = sum(v or 0 for v in eng_parts)
                views, fol = num(r.get("views")), num(r.get("followers"))
                if views:
                    rate, base = 1000 * eng / views, "views"
                elif fol:
                    rate, base = 1000 * eng / fol, "followers"
                else:
                    notes.append(f"no views or followers: {r.get('url') or (r.get('text') or '')[:40]!r} (skipped)")
                    continue
                text = (r.get("text") or "").strip()
                line1 = text.splitlines()[0] if text else ""
                rows.append({"platform": (r.get("platform") or "?").lower(), "author": r.get("author") or "",
                             "url": r.get("url") or "", "date": r.get("date") or "", "line1": line1,
                             "format": (r.get("format") or "?").lower(), "source": r.get("source") or "?",
                             "opener": opener(line1), "line1_words": len(line1.split()),
                             "link": "link" if re.search(r"https?://", text) else "no link",
                             "eng": eng, "views": views, "rate": round(rate, 2), "base": base})
    return rows, notes


def groups(rows, key):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r["rate"])
    return {k: {"n": len(v), "median": round(st.median(v), 2), "small": len(v) < SMALL} for k, v in sorted(out.items())}


def bucket_words(n):
    return "1-6 words" if n <= 6 else "7-12 words" if n <= 12 else "13+ words"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--out", default="signals")
    a = ap.parse_args()
    rows, notes = load(a.csv)
    os.makedirs(a.out, exist_ok=True)
    rep = {"n": len(rows), "notes": notes, "bases": {}}
    md = ["# Post signals", ""]
    if not rows:
        md.append("No usable rows. Each post needs engagement numbers plus views or followers.")
    for base in ("views", "followers"):
        rs = [r for r in rows if r["base"] == base]
        if not rs:
            continue
        for r in rs:
            r["line1_len"] = bucket_words(r["line1_words"])
        g = {k: groups(rs, k) for k in ("platform", "format", "opener", "line1_len", "link", "author")}
        top = sorted(rs, key=lambda r: -r["rate"])
        rep["bases"][base] = {"n": len(rs), "groups": g, "top": top[:10], "bottom": top[-5:][::-1]}
        md += [f"## Engagements per 1,000 {base} (n={len(rs)})", ""]
        if len(rs) >= 3:
            med = st.median(r["rate"] for r in rs)
            if top[0]["rate"] > 5 * med:
                md.append(f"Note: the top post ({top[0]['rate']}) is over 5x the median ({round(med, 2)}). Treat it as a lead, not a rule.")
                md.append("")
        for k, label in (("platform", "Platform"), ("format", "Format"), ("opener", "Opener type"),
                         ("line1_len", "First line length"), ("link", "Link in post"), ("author", "Author")):
            md += [f"### {label}", "", "| group | median | n |", "|---|---|---|"]
            for name, s in g[k].items():
                md.append(f"| {name} | {s['median']} | {s['n']}{' (small n, not a finding)' if s['small'] else ''} |")
            md.append("")
        md += ["### Top 10", "", "| rate | platform | format | author | line 1 | source |", "|---|---|---|---|---|---|"]
        for r in top[:10]:
            md.append(f"| {r['rate']} | {r['platform']} | {r['format']} | {r['author']} | {r['line1'][:90].replace('|', '/')} | {r['source']} |")
        md += ["", "### Bottom 5", "", "| rate | platform | format | line 1 |", "|---|---|---|---|"]
        for r in top[-5:][::-1]:
            md.append(f"| {r['rate']} | {r['platform']} | {r['format']} | {r['line1'][:90].replace('|', '/')} |")
        md.append("")
    md += ["## Notes from reading the file", ""] + ([f"- {n}" for n in notes] or ["- none"])
    md += ["", "Rates on views and on followers are different bases and are never compared with each other."]
    open(os.path.join(a.out, "signals.md"), "w").write("\n".join(md) + "\n")
    json.dump(rep, open(os.path.join(a.out, "signals.json"), "w"), indent=1, ensure_ascii=False)
    print(f"{len(rows)} posts ranked, {len(notes)} notes -> {a.out}/signals.md")


if __name__ == "__main__":
    main()
