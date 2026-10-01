#!/usr/bin/env python3
"""Validate a generated <name>-clone folder and scan it for private details. Local only.

usage: check_clone.py CLONE_DIR [--allow WORD ...] [--json]

Checks: SKILL.md exists; front matter has name and description; name equals the folder name and ends in
"-clone"; the description is 40 to 1024 characters and says when to use the skill; no unfilled {{placeholders}}.
Then scans every text file for emails, URLs, phone numbers, @handles, money amounts, file paths and
capitalised multi-word names (the same patterns extract_rules.py redacts). Exit 1 on any problem.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("extract_rules", HERE / "extract_rules.py")
er = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(er)


def front_matter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fm, key, out = text[4:end].splitlines(), None, {}
    for line in fm:
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = "" if val in (">-", ">", "|", "|-") else val.strip("\"'")
        elif key and line.startswith("  "):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def check(folder: Path, allow: set[str] | None = None) -> list[dict]:
    allow = {a.lower() for a in (allow or set())}
    problems: list[dict] = []

    def add(kind, file, line, detail):
        problems.append({"kind": kind, "file": file, "line": line, "detail": detail})

    skill = folder / "SKILL.md"
    if not skill.is_file():
        add("structure", "SKILL.md", 0, "missing SKILL.md")
        return problems
    fm = front_matter(skill.read_text(encoding="utf-8"))
    if fm is None:
        add("frontmatter", "SKILL.md", 1, "no front matter block")
    else:
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != folder.name:
            add("frontmatter", "SKILL.md", 1, f"name '{name}' does not match folder '{folder.name}'")
        if not re.fullmatch(r"[a-z][a-z-]*-clone", name or ""):
            add("frontmatter", "SKILL.md", 1, "name must look like <first-name>-clone")
        if not 40 <= len(desc) <= 1024:
            add("frontmatter", "SKILL.md", 1, f"description is {len(desc)} characters; keep it 40 to 1024")
        if "use when" not in desc.lower():
            add("frontmatter", "SKILL.md", 1, "description should say when to use it ('Use when ...')")
    for f in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = str(f.relative_to(folder))
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"\{\{\w+\}\}", line):
                add("placeholder", rel, i, "unfilled placeholder")
            if line.lstrip().startswith("#"):
                continue
            for kind, pat in er.REDACT:
                for m in pat.finditer(line):
                    if kind == "path" and (folder / m.group(0).strip("./")).exists():
                        continue
                    if kind == "name":
                        hit = er._name(m)
                        if hit is None or all(w.lower() in allow for w in hit.split()):
                            continue
                    add("pii:" + kind, rel, i, f"looks like a {kind}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a <name>-clone folder and scan it for private details.")
    ap.add_argument("folder")
    ap.add_argument("--allow", action="append", default=[], help="a word that is fine, e.g. your own first name")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    problems = check(Path(a.folder).expanduser(), set(a.allow))
    if a.json:
        print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    else:
        for p in problems:
            print(f"{p['file']}:{p['line']}: {p['kind']}: {p['detail']}")
        print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
