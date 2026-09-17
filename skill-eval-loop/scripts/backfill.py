#!/usr/bin/env python3
"""Give already-adopted skills something the production recheck can measure them by.

Usage: backfill.py [--ledger PATH] [--apply]

Early knowledge-gap skills were forged from hand-written briefs, so their ledger
rows carry no failure record at all. The recheck refuses to guess, which is right,
but it means those adoptions would SKIP forever: adopted on a blind win and then
never checked against real sessions.

The theme is not lost, though. It is written down in the skill itself: the
front-matter description says which situations it fires in, and the body quotes
the user's own words verbatim. This lifts both out of the installed SKILL.md and
writes them onto the ledger row as:

    "failure": {"kind": "correction", "signature": <description>,
                "user_rules": [...], "derived_from": "skill_md:<path>"}

That is a matcher, not a measurement: it says what to count, never how often it
happened. The recheck still refuses the row unless it finds at least 10 sessions
on each side of the adoption and at least two matching sessions before it, so a
weak description produces a SKIP rather than a verdict.

Prints what it would change; --apply rewrites the ledger after backing it up.
"""
import argparse
import json
import os
import re
import shutil
import time

SKILL_DIRS = ("~/skill-forge/adopted", "~/.agents/skills", "~/.claude/skills")


def find_skill_md(skill, root):
    for d in (os.path.join(root, "adopted"),) + tuple(os.path.expanduser(p) for p in SKILL_DIRS):
        p = os.path.join(d, skill, "SKILL.md")
        if os.path.isfile(p):
            return p
    return None


def extract(path):
    """description (what it fires on) + the user's own quoted words (what to count)."""
    text = open(path, errors="replace").read()
    desc = ""
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    if m:
        d = re.search(r"^description:\s*(.+?)(?=\n\w+:|\Z)", m.group(1), re.S | re.M)
        if d:
            desc = " ".join(d.group(1).split())
    body = text[m.end():] if m else text
    rules = []
    # Verbatim corrections are quoted in the body; they are the best matcher tokens
    # because they are literally what the user typed when the agent got it wrong.
    # Short quotes only. A whole paragraph of the user's words carries dozens of
    # ordinary tokens, and a matcher built from those matches every correction
    # rather than this theme; the recheck refuses such a signature outright.
    for q in re.findall(r"[\"“]([^\"“”]{20,90})[\"”]", body):
        q = " ".join(q.split())
        if q not in rules:
            rules.append(q)
    for b in re.findall(r"^\s*(?:[-*]|\d+\.)\s+\*\*(.+?)\*\*", body, re.M):
        b = " ".join(b.split())
        if len(b) <= 60 and b not in rules:
            rules.append(b)
    # The description's first sentence names the situation; the rest lists variants.
    desc = re.split(r"(?<=[.!?])\s", desc)[0] if desc else desc
    return desc, rules[:3]


def main():
    ap = argparse.ArgumentParser()
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    ap.add_argument("--ledger", default=os.path.join(root, "ledger.jsonl"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--redo", action="store_true",
                    help="re-derive signatures this script wrote before, after changing how")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.ledger) if l.strip()]
    changed = 0
    for r in rows:
        if r.get("decision") not in ("adopt", "probation"):
            continue
        f = r.get("failure") or {}
        if (f.get("signature") or "").strip():
            if not (args.redo and str(f.get("derived_from", "")).startswith("skill_md:")):
                continue
        skill = r.get("skill")
        md = find_skill_md(skill, root) if skill else None
        if not md:
            print(f"SKIP {skill}: no installed SKILL.md to read the theme from")
            continue
        desc, rules = extract(md)
        if len(desc.split()) < 6:
            print(f"SKIP {skill}: description too thin to match corrections ({desc!r})")
            continue
        r["failure"] = {"kind": "correction", "signature": desc, "user_rules": rules,
                        "derived_from": f"skill_md:{md}"}
        changed += 1
        print(f"{skill}: {len(rules)} rules, signature {desc[:70]}...")
    if not changed:
        print("nothing to backfill")
        return
    if not args.apply:
        print(f"\n{changed} rows would change; rerun with --apply")
        return
    bak = args.ledger + ".bak-" + time.strftime("%Y%m%d%H%M%S")
    shutil.copy2(args.ledger, bak)
    with open(args.ledger, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"\n{changed} rows updated; previous ledger kept at {bak}")


if __name__ == "__main__":
    main()
