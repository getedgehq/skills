#!/usr/bin/env python3
"""Refresh the exact file inventory and rollup in a skill DERIVATION.json."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", "node_modules"}
SKIP_FILES = {".DS_Store", "DERIVATION.json"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(bundle: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in bundle.rglob("*"):
        if not path.is_file() or path.name in SKIP_FILES or any(part in SKIP_DIRS for part in path.parts):
            continue
        entries.append(
            {
                "path": str(path.relative_to(bundle)),
                "sha256": digest(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return sorted(entries, key=lambda entry: str(entry["path"]))


def refresh(bundle: Path) -> dict[str, object]:
    derivation_path = bundle / "DERIVATION.json"
    record = json.loads(derivation_path.read_text(encoding="utf-8"))
    entries = inventory(bundle)
    record["copy_files"] = entries
    material = "".join(f'{entry["path"]}:{entry["sha256"]}\n' for entry in entries)
    record["copy_files_sha256"] = hashlib.sha256(material.encode()).hexdigest()
    derivation_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    record = refresh(args.bundle.resolve())
    print(f'refreshed {len(record["copy_files"])} files: {record["copy_files_sha256"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
