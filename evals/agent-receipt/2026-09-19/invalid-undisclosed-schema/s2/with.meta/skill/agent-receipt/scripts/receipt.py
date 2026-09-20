#!/usr/bin/env python3
"""Create a public-safe agent receipt from a local evidence manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = ("project", "agent")
PUBLIC_FIELDS = (
    "project", "agent", "duration_minutes", "interventions", "files_changed",
    "tests_passed", "tests_total", "verification", "deployed", "skills_used",
    "artifacts", "started_at", "completed_at", "source_commit", "demo",
)


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_receipt(manifest: dict) -> dict:
    missing = [key for key in REQUIRED if not manifest.get(key)]
    if missing:
        raise ValueError("Missing: " + ", ".join(missing))

    for key in ("duration_minutes", "interventions", "files_changed", "tests_passed", "tests_total"):
        value = manifest.get(key, "unknown")
        if value != "unknown" and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
            raise ValueError(f"{key} must be a non-negative number or 'unknown'")

    passed, total = manifest.get("tests_passed", "unknown"), manifest.get("tests_total", "unknown")
    if passed != "unknown" and total != "unknown" and passed > total:
        raise ValueError("tests_passed cannot exceed tests_total")

    evidence = manifest.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")

    public = {key: manifest[key] for key in PUBLIC_FIELDS if key in manifest}
    public["schema"] = "edge-agent-receipt/1.0"
    public["demo"] = bool(manifest.get("demo", False))
    public["evidence_count"] = len(evidence)
    public["evidence_digests"] = [digest(item) for item in evidence]
    public["manifest_digest"] = digest(manifest)
    public["privacy"] = "summary_only"
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = build_receipt(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
