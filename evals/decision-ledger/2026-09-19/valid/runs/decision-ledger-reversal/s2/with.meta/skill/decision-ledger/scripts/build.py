#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

VALID_STATES = {"decided", "reversed", "proposed", "open", "action"}


def validate(source: Path, records: list[dict]) -> dict:
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    ids = {row.get("id") for row in records}
    if None in ids or len(ids) != len(records):
        raise ValueError("every record needs a unique id")
    for row in records:
        if row.get("state") not in VALID_STATES:
            raise ValueError(f"invalid state for {row['id']}")
        line = row.get("line")
        quote = row.get("evidence")
        if not isinstance(line, int) or not 1 <= line <= len(lines):
            raise ValueError(f"invalid line for {row['id']}")
        if not isinstance(quote, str) or quote not in lines[line - 1]:
            raise ValueError(f"evidence mismatch for {row['id']}")
        target = row.get("supersedes")
        if target is not None and target not in ids:
            raise ValueError(f"unknown superseded id for {row['id']}")
        row.setdefault("owner", "unknown")
        row.setdefault("due", "unknown")
    return {"schema": "edge-decision-ledger/1.0", "source": source.name, "records": records}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("records", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.source, json.loads(args.records.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
