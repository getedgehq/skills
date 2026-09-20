#!/usr/bin/env python3
"""Fail-closed static release check for an Edge skill package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

VALID_STATES = {"supported", "inconclusive", "negative", "not_run", "invalid"}
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "node_modules"}
SKIP_FILES = {".DS_Store", "DERIVATION.json"}
SECRET_PATTERNS = (
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"gh" rb"[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"sk-[A-Za-z0-9]{20,}"),
    re.compile(rb"-----" rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(bundle: Path) -> list[str]:
    failures: list[str] = []
    for name in ("SKILL.md", "DERIVATION.json", "LICENSE", "EVALS.md"):
        if not (bundle / name).is_file():
            failures.append(f"missing {name}")
    if failures:
        return failures

    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")
    header = ""
    if skill.startswith("---\n") and "\n---\n" in skill[4:]:
        header = skill[4:].split("\n---\n", 1)[0]
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line and not line[:1].isspace():
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip("'\"")
    if not header or not fields.get("name") or not fields.get("description"):
        failures.append("invalid SKILL.md front matter")

    try:
        record = json.loads((bundle / "DERIVATION.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return failures + [f"invalid DERIVATION.json: {exc}"]
    listed = {entry.get("path"): entry for entry in record.get("copy_files", [])}
    disk = {
        str(path.relative_to(bundle))
        for path in bundle.rglob("*")
        if path.is_file() and path.name not in SKIP_FILES and not any(part in SKIP_DIRS for part in path.parts)
    }
    if disk != set(listed):
        failures.append("DERIVATION.json file inventory does not match disk")
    for relative, entry in listed.items():
        path = bundle / relative
        if path.is_file() and sha256(path) != entry.get("sha256"):
            failures.append(f"hash mismatch: {relative}")
    rollup_material = "".join(
        f'{relative}:{listed[relative].get("sha256", "")}\n' for relative in sorted(listed)
    )
    rollup = hashlib.sha256(rollup_material.encode()).hexdigest()
    if record.get("copy_files_sha256") != rollup:
        failures.append("DERIVATION.json rollup mismatch")

    summary = bundle / "eval-results" / "summary.json"
    if summary.is_file():
        try:
            state = json.loads(summary.read_text(encoding="utf-8")).get("status")
        except json.JSONDecodeError as exc:
            failures.append(f"invalid eval summary: {exc}")
        else:
            if state not in VALID_STATES:
                failures.append(f"invalid eval status: {state!r}")

    for path in bundle.rglob("*"):
        if (
            not path.is_file()
            or any(part in SKIP_DIRS for part in path.parts)
            or path.stat().st_size > 2_000_000
        ):
            continue
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            failures.append(f"possible secret in {path.relative_to(bundle)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    failures = check(args.bundle.resolve())
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("release contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
