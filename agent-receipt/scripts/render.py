#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def value(result: dict, key: str, suffix: str = "") -> str:
    item = result.get(key, "unknown")
    return f"{item}{suffix}" if item != "unknown" else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--png", type=Path)
    args = parser.parse_args()
    result = json.loads(args.result.read_text(encoding="utf-8"))
    data = {
        "eyebrow": "EDGE / AGENT RECEIPT",
        "title": result.get("project", "Agent run"),
        "subtitle": f"{result.get('agent', 'agent')} | evidence-backed run summary",
        "badge": "DEMO" if result.get("demo") else "VERIFIED FIELDS ONLY",
        "metrics": [
            {"label": "Duration", "value": value(result, "duration_minutes", "m")},
            {"label": "Interventions", "value": value(result, "interventions")},
            {"label": "Files changed", "value": value(result, "files_changed")},
            {"label": "Tests", "value": f"{result.get('tests_passed', '?')}/{result.get('tests_total', '?')}"},
        ],
        "findings": [
            f"Verification: {result.get('verification', 'unknown')}",
            f"Deployed: {result.get('deployed', 'unknown')}",
            f"Evidence records: {result.get('evidence_count', 0)}",
        ],
        "footer": "Unknown stays unknown | private evidence stays local",
    }
    with tempfile.TemporaryDirectory() as temporary:
        card = Path(temporary) / "card.json"
        card.write_text(json.dumps(data), encoding="utf-8")
        command = [sys.executable, str(HERE / "render_card.py"), str(card), "--svg", str(args.svg)]
        if args.png:
            command.extend(("--png", str(args.png)))
        subprocess.check_call(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
