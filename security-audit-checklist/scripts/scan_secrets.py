#!/usr/bin/env python3
"""Quick regex scanner for common secrets in a codebase."""

import argparse
import os
import re
import sys
from pathlib import Path

PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret Key": re.compile(r"['\"][0-9a-zA-Z/+]{40}['\"]"),
    "GitHub Token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
    "GitHub OAuth": re.compile(r"[0-9a-fA-F]{40}"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
    "Stripe Live Key": re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
    "Stripe Test Key": re.compile(r"sk_test_[0-9a-zA-Z]{24,}"),
    "OpenAI Key": re.compile(r"sk-[a-zA-Z0-9]{48}"),
    "Generic API Key": re.compile(r"[aA][pP][iI][_-]?[kK][eE][yY]\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"),
    "Generic Secret": re.compile(r"[sS][eE][cC][rR][eE][tT]\s*[:=]\s*['\"][a-zA-Z0-9_\-]{8,}['\"]"),
    "Password in URL": re.compile(r"[a-zA-Z]{3,10}://[^/\s:@]{3,20}:[^/\s:@]{3,20}@.{1,100}[\"'\s]"),
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", ".next", ".turbo", ".cache", ".mypy_cache", ".egg-info",
}

IGNORE_EXTS = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".woff", ".woff2", ".ttf", ".eot"}


def should_scan(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    if path.suffix.lower() in IGNORE_EXTS:
        return False
    return True


def scan_file(path: Path) -> list[dict]:
    findings = []
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return findings
    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line_num = text[: match.start()].count("\n") + 1
            snippet = text[match.start() : match.end()]
            # Heuristic: skip if it looks like a placeholder/example
            lower = snippet.lower()
            if any(p in lower for p in ("example", "placeholder", "your_", "xxx", "changeme")):
                continue
            findings.append(
                {
                    "file": str(path),
                    "line": line_num,
                    "type": name,
                    "match": snippet,
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a directory for common secrets.")
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--max-file-size", type=int, default=5_000_000, help="Skip files larger than N bytes")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 1

    all_findings: list[dict] = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if not should_scan(item):
            continue
        if item.stat().st_size > args.max_file_size:
            continue
        all_findings.extend(scan_file(item))

    if not all_findings:
        print("No obvious secrets found. ✅")
        return 0

    # Deduplicate by file+line+type
    seen = set()
    for f in all_findings:
        key = (f["file"], f["line"], f["type"])
        if key in seen:
            continue
        seen.add(key)
        print(f"{f['file']}:{f['line']}  [{f['type']}]  {f['match']}")

    print(f"\nTotal potential secrets: {len(seen)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
