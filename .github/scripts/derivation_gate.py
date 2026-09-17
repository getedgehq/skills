#!/usr/bin/env python3
"""Fail if any skill bundle's DERIVATION.json disagrees with the bytes next to it.

Usage (from the repository root):
  python .github/scripts/derivation_gate.py                 # every skill bundle
  python .github/scripts/derivation_gate.py opendraft ...   # only these slugs
  python .github/scripts/derivation_gate.py --quiet         # print findings only

A bundle is any top-level directory holding a SKILL.md. Other top-level directories
(for example evals/, which holds published eval reports) are not bundles and are skipped.

Exit 0 clean, 1 on any finding. Read-only: this never edits a record.

Why this exists. `opendraft` shipped publicly with a recorded hash that did not match its
own `scripts/integrity.py`, and nobody noticed because nothing ever checked. A bundle whose
integrity record is wrong is a correctness bug in the artifact we are asking people to
trust, so the check belongs in the publish path rather than in somebody's memory.

It checks BOTH directions on purpose. Hashing only the listed files misses the other failure
mode we actually hit: `people-search/tests/fixtures/people.csv` is on disk and shipping while
absent from `copy_files` entirely, so a one-directional gate calls that bundle clean.

`source_files` is deliberately not checked. It records the private original at
the author's private skills directory, which is historical provenance about where a file came from, not a
claim about the bytes in the repo. Recomputing it from repo bytes would fabricate provenance.
"""
import argparse
import hashlib
import json
import os
import sys

# Standard library only, so it runs in CI with no dependencies and no credentials.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", "node_modules"}
SKIP_FILES = {"DERIVATION.json", ".DS_Store"}


def on_disk(bundle):
    out = set()
    for r, ds, fs in os.walk(bundle):
        ds[:] = [d for d in ds if d not in SKIP_DIRS]
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), bundle)
            if rel not in SKIP_FILES:
                out.add(rel)
    return out


def rollup(copy_files):
    """sha256 over "{path}:{sha256}\\n" lines in path order. Reverse-engineered from the
    bundles that carry one and confirmed against all of them before it was ever written."""
    lines = "".join(f"{e['path']}:{e['sha256']}\n"
                    for e in sorted(copy_files, key=lambda e: e["path"]))
    return hashlib.sha256(lines.encode()).hexdigest()


def audit(bundle):
    """Return a list of human-readable findings. Empty list means clean."""
    bad = []
    rec = json.load(open(os.path.join(bundle, "DERIVATION.json")))
    cf = rec.get("copy_files", [])
    if not cf:
        return ["copy_files is empty or absent"]

    for e in sorted(cf, key=lambda e: e["path"]):
        p = os.path.join(bundle, e["path"])
        if not os.path.exists(p):
            bad.append(f"listed but missing from disk: {e['path']}")
            continue
        b = open(p, "rb").read()
        h = hashlib.sha256(b).hexdigest()
        if h != e.get("sha256"):
            # Show heads only: the full pair adds nothing a reader can act on.
            bad.append(f"sha256 mismatch: {e['path']} recorded {e.get('sha256','?')[:12]} "
                       f"actual {h[:12]}")
        elif len(b) != e.get("size_bytes"):
            bad.append(f"size mismatch: {e['path']} recorded {e.get('size_bytes')} "
                       f"actual {len(b)}")

    for rel in sorted(on_disk(bundle) - {e["path"] for e in cf}):
        bad.append(f"on disk but unlisted in copy_files: {rel}")

    recorded = rec.get("copy_files_sha256")
    if recorded is None:
        # Not every bundle carries one yet. A bundle without a rollup has no single value to
        # quote, which is a weaker record rather than a wrong one, so it is named but does
        # not by itself fail the gate.
        bad.append("NOTE no copy_files_sha256 rollup recorded")
    elif recorded != rollup(cf):
        bad.append(f"rollup mismatch: recorded {recorded[:12]} computed {rollup(cf)[:12]}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*", help="bundles to check (default: every top-level SKILL.md directory)")
    ap.add_argument("--quiet", action="store_true", help="print findings only, not clean bundles")
    args = ap.parse_args()

    skills = ROOT
    slugs = args.slugs or sorted(
        s for s in os.listdir(skills)
        if not s.startswith(".") and os.path.isfile(os.path.join(skills, s, "SKILL.md")))
    failed = notes = 0
    for slug in slugs:
        bundle = os.path.join(skills, slug)
        if not os.path.isdir(bundle):
            continue
        if not os.path.exists(os.path.join(bundle, "DERIVATION.json")):
            print(f"FAIL {slug}: no DERIVATION.json")
            failed += 1
            continue
        bad = audit(bundle)
        hard = [b for b in bad if not b.startswith("NOTE ")]
        if hard:
            failed += 1
        notes += len(bad) - len(hard)
        if bad:
            print(f"{'FAIL' if hard else 'NOTE'} {slug}")
            for b in bad:
                print(f"       {b}")
        elif not args.quiet:
            print(f"ok   {slug}")

    print(f"\n{failed} bundle(s) failed, {notes} note(s)", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
