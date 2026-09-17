#!/usr/bin/env python3
"""Find candidate skills for a failure cluster.

Usage: match.py <cluster.json | failures.json --index N> [--out candidates.json]

Searches three pools and ranks by token overlap with the failure signature:
  1. Local installed skills: ~/.claude/skills, ~/.agents/skills
  2. getedgehq skills source repo (GETEDGE_SKILLS env or default path)
  3. Floom skills registry via `npx -y @floomhq/skills search` (best effort)
"""
import argparse
import json
import os
import re
import subprocess
import sys

STOP = set("the a an and or of to in for on with without is are be not no never do does dont "
           "this that it its you your we our".split())


def tokens(text):
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2 and t not in STOP}


def read_frontmatter(path):
    """Cheap YAML frontmatter scrape: name + description only."""
    try:
        text = open(path, errors="replace").read(4000)
    except OSError:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    name = re.search(r"^name:\s*(.+)$", m.group(1), re.MULTILINE)
    desc = re.search(r"^description:\s*(.+?)(?=^\w+:|\Z)", m.group(1), re.MULTILINE | re.DOTALL)
    return {
        "name": name.group(1).strip() if name else os.path.basename(os.path.dirname(path)),
        "description": " ".join(desc.group(1).split()) if desc else "",
    }


def local_skills():
    pools = []
    for root in (os.path.expanduser("~/.claude/skills"), os.path.expanduser("~/.agents/skills"),
                 os.environ.get("GETEDGE_SKILLS", "/home/federicodeponte/getedgehq-skills-source")):
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            sk = os.path.join(root, entry, "SKILL.md")
            if os.path.isfile(sk):
                fm = read_frontmatter(sk)
                if fm:
                    fm["path"] = os.path.dirname(sk)
                    fm["pool"] = root
                    pools.append(fm)
    return pools


def floom_search(query):
    try:
        out = subprocess.run(["npx", "-y", "@floomhq/skills", "search", query],
                             capture_output=True, text=True, timeout=90)
        if out.returncode != 0:
            return []
        results = []
        for line in out.stdout.splitlines():
            m = re.match(r"\s*([\w.-]+/[\w.-]+)\s+[-–]\s+(.+)", line)
            if m:
                results.append({"name": m.group(1), "description": m.group(2).strip(),
                                "path": None, "pool": "floom-registry"})
        return results[:10]
    except (OSError, subprocess.TimeoutExpired):
        return []


def skills_sh_search(query):
    """Discovery via skills.sh (Vercel): `npx skills find <query>`.
    Parses 'owner/repo@skill' + install count. Non-interactive when stdin is closed."""
    try:
        out = subprocess.run(["npx", "-y", "skills", "find", query],
                             capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        if out.returncode != 0:
            return []
        results = []
        # owner/repo@skill   N installs
        pat = re.compile(r"([\w.-]+/[\w.-]+)@([\w.-]+)\D+(\d+)\s+installs")
        for m in pat.finditer(out.stdout):
            results.append({
                "name": f"{m.group(1)}@{m.group(2)}",
                "description": "",
                "installs": int(m.group(3)),
                "path": None,
                "pool": "skills.sh",
            })
        return results[:10]
    except (OSError, subprocess.TimeoutExpired):
        return []


def rank(cluster, candidates):
    sig_tokens = tokens(cluster["signature"] + " " + " ".join(cluster.get("evidence", [])))
    scored = []
    seen = set()
    for c in candidates:
        if c["name"] in seen:  # same skill installed in multiple pools
            continue
        seen.add(c["name"])
        ct = tokens(c["name"] + " " + c["description"])
        if not ct:
            continue
        overlap = len(sig_tokens & ct) / max(1, len(sig_tokens))
        scored.append({**c, "score": round(overlap, 3)})
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()

    data = json.load(open(args.source))
    cluster = data["clusters"][args.index] if "clusters" in data else data
    candidates = local_skills()
    query = " ".join(list(tokens(cluster["signature"]))[:6])
    if query:
        candidates += skills_sh_search(query)
        candidates += floom_search(query)
    ranked = rank(cluster, candidates)[:args.top]
    result = {"failure": {k: cluster[k] for k in ("kind", "signature")}, "candidates": ranked}
    out = args.out or f"candidates-{abs(hash(cluster['signature'])) % 10**6}.json"
    json.dump(result, open(out, "w"), indent=1)
    print(f"{len(ranked)} candidates -> {out}")
    for c in ranked:
        print(f"  {c['score']:.2f}  {c['name']}  ({c['pool']})")


if __name__ == "__main__":
    main()
