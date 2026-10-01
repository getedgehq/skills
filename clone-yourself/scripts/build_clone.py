#!/usr/bin/env python3
"""Build a local <name>-clone skill folder from confirmed rules. Local only, no network.

usage: build_clone.py --rules clone-work/rules.json --name Sam [--persona persona.json] [--tasks "startup tasks"]
                      [--pronoun they|he|she] [--voice-skill my-voice] [--out ~/.claude/skills] [--force]
                      [--assume-confirmed]

Only rules with "confirmed": true are used (pass --assume-confirmed only after the user approved the whole list).
persona.json is optional: {"talk": [...], "phrases": [...], "annoys": [...], "cares": [...]}, written from the
user's own confirmed answers and their my-voice profile. Writes:
  <out>/<name>-clone/SKILL.md, references/rules.md, references/persona.md
then runs check_clone.py on the result and exits with its status.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
ORDER = [("decide", "How I decide"), ("judge", "How I judge work"), ("report", "How I report"),
         ("bans", "What I never do"), ("format", "Format"), ("persona", "How I sound")]
PRONOUNS = {"they": ("they", "their", "them", "do"), "he": ("he", "his", "him", "does"),
            "she": ("she", "her", "her", "does")}


def fill(template: str, values: dict) -> str:
    out = template
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{\w+\}\}", out)
    if left:
        raise ValueError(f"unfilled placeholders: {sorted(set(left))}")
    return out


def bullets(items, empty="- (none yet: add your own)"):
    items = [str(i).strip() for i in items if str(i).strip()]
    return "\n".join(f"- {i}" for i in items) if items else empty


def build(rules_path: Path, name: str, out: Path, *, persona: dict | None = None, tasks: str = "their work",
          pronoun: str = "they", voice_skill: str = "my-voice", force: bool = False,
          assume_confirmed: bool = False) -> Path:
    if not re.fullmatch(r"[A-Za-z][A-Za-z-]{0,30}", name):
        raise ValueError("name must be a first name: letters and hyphens only")
    slug = name.lower() + "-clone"
    data = json.loads(rules_path.read_text(encoding="utf-8"))
    rules = data["rules"] if isinstance(data, dict) else data
    keep = [r for r in rules if r.get("confirmed") or assume_confirmed]
    if not keep:
        raise ValueError("no confirmed rules: set \"confirmed\": true on the rules the user approved")
    dest = out / slug
    if dest.exists() and not force:
        raise FileExistsError(f"{dest} exists; pass --force to overwrite")
    they, their, them, does = PRONOUNS[pronoun]
    Name = name[0].upper() + name[1:]
    persona = persona or {}
    by = {b: [r for r in keep if r.get("bucket") == b] for b, _ in ORDER}
    top = sorted(keep, key=lambda r: -int(r.get("count", 1)))[:7]
    base = {"Name": Name, "slug": slug, "tasks": tasks, "pronoun_they": they, "pronoun_their": their,
            "pronoun_them": them, "does": does, "voice_skill": voice_skill}
    example = persona.get("example") or (
        f"> **User:** should we add one more feature before launch?\n>\n"
        f"> **{Name}:** (answer in {Name}'s words, using the rules above. Replace this synthetic example.)")
    skill = fill((TEMPLATES / "SKILL.template.md").read_text(), {**base, "top_rules": bullets(r["text"] for r in top),
                                                               "example": example})
    sections = "\n\n".join(f"## {title}\n\n{bullets(r['text'] for r in by[b])}" for b, title in ORDER if by[b])
    rules_md = fill((TEMPLATES / "rules.template.md").read_text(), {**base, "sections": sections})
    talk = persona.get("talk") or [r["text"] for r in by["persona"]]
    persona_md = fill((TEMPLATES / "persona.template.md").read_text(), {
        **base, "talk": bullets(talk), "phrases": bullets(persona.get("phrases", [])),
        "annoys": bullets(persona.get("annoys", [])), "cares": bullets(persona.get("cares", []))})
    (dest / "references").mkdir(parents=True, exist_ok=True)
    (dest / "SKILL.md").write_text(skill, encoding="utf-8")
    (dest / "references" / "rules.md").write_text(rules_md, encoding="utf-8")
    (dest / "references" / "persona.md").write_text(persona_md, encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build <name>-clone from confirmed rules (local only).")
    ap.add_argument("--rules", required=True)
    ap.add_argument("--name", required=True, help="first name, e.g. Sam")
    ap.add_argument("--persona")
    ap.add_argument("--tasks", default="their work", help='e.g. "startup tasks" or "client projects"')
    ap.add_argument("--pronoun", choices=PRONOUNS, default="they")
    ap.add_argument("--voice-skill", default="my-voice")
    ap.add_argument("--out", default="~/.claude/skills")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--assume-confirmed", action="store_true")
    ap.add_argument("--allow", action="append", default=[], help="words check_clone may allow (e.g. your own name)")
    a = ap.parse_args(argv)
    persona = json.loads(Path(a.persona).read_text(encoding="utf-8")) if a.persona else None
    try:
        dest = build(Path(a.rules), a.name, Path(os.path.expanduser(a.out)), persona=persona, tasks=a.tasks,
                     pronoun=a.pronoun, voice_skill=a.voice_skill, force=a.force,
                     assume_confirmed=a.assume_confirmed)
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"wrote {dest}")
    spec = importlib.util.spec_from_file_location("check_clone", HERE / "check_clone.py")
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)
    return cc.main([str(dest)] + [x for w in a.allow for x in ("--allow", w)] + ["--allow", a.name])


if __name__ == "__main__":
    sys.exit(main())
