#!/usr/bin/env python3
"""Build a self-contained review page (one HTML file) from an application JSON.

Usage: python3 build_review_page.py app.json out.html
app.json: {"program": "yc" | "speedrun", "company": "...", "founder_name": "...", "founder_email": "..." (optional),
           "items": [{"q": "...", "a": "...", "sec": "FOUNDERS" (optional), "tl": "one-line summary" (optional)}]}
Standard library only. The page needs no server: reviewers' notes stay in their browser until they press
"Send my notes", which gives them plain text (and a mailto: link when founder_email is set).
"""
import hashlib, html, json, re, sys
from pathlib import Path

PROGRAMS = {"yc": "YC", "speedrun": "a16z Speedrun"}


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48].rstrip("-")
    return s or "q"


def clean(app):
    if app.get("program") not in PROGRAMS:
        sys.exit("program must be yc or speedrun")
    items = app.get("items")
    if not isinstance(items, list) or not items or len(items) > 80:
        sys.exit("items must be a list of 1-80 {q, a} objects")
    out, used = [], set()
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not isinstance(it.get("q"), str) or not isinstance(it.get("a"), str) or not it["q"].strip():
            sys.exit(f"item {i + 1}: q and a must be strings")
        qid, k = slug(it["q"]), 2
        while qid in used:
            qid, k = f"{slug(it['q'])[:44]}-{k}", k + 1
        used.add(qid)
        o = {"qid": qid, "q": it["q"].strip(), "a": it["a"].replace("\r\n", "\n").strip()}
        if isinstance(it.get("sec"), str) and it["sec"].strip():
            o["sec"] = it["sec"].strip()[:60]
        if isinstance(it.get("tl"), str) and it["tl"].strip() and it["tl"].strip() != o["a"]:
            o["tl"] = it["tl"].strip()[:400]
        out.append(o)
    email = app.get("founder_email")
    if email is not None and not (isinstance(email, str) and re.fullmatch(r"[^\s@<>\"]{1,64}@[^\s@<>\"]{1,190}", email)):
        sys.exit("founder_email is not an email address")
    s = lambda k: app[k].strip()[:80] if isinstance(app.get(k), str) and app[k].strip() else None
    d = {"program": app["program"], "program_label": PROGRAMS[app["program"]], "company": s("company"),
         "founder_name": s("founder_name"), "founder_email": email, "items": out}
    # draft id = content hash: a new draft gets a fresh notes store, so notes never mix across drafts
    d["draft_id"] = hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:8]
    return d


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    d = clean(json.loads(Path(sys.argv[1]).read_text()))
    tpl = (Path(__file__).resolve().parent.parent / "assets" / "review-template.html").read_text()
    data = json.dumps(d, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    title = html.escape(" ".join(x for x in [d["company"] and d["company"] + ":", d["program_label"], "application, for review"] if x))
    Path(sys.argv[2]).write_text(tpl.replace("__TITLE__", title, 1).replace("__DATA__", data, 1))
    print(f"wrote {sys.argv[2]} (draft {d['draft_id']}, {len(d['items'])} questions)")


if __name__ == "__main__":
    main()
