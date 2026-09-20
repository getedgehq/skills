from __future__ import annotations

import json
import sys
from pathlib import Path

bad = []
root = Path("launch-pack")
required = ["facts.json", "x.md", "linkedin.md", "product-hunt.md", "reddit.md", "hn.md", "asset-brief.md"]
for name in required:
    if not (root / name).is_file() or not (root / name).read_text().strip():
        bad.append("missing " + name)
combined = "\n".join((root / name).read_text(errors="replace") for name in required if (root / name).is_file())
for invented in ("customer", "revenue", "award-winning", "cloud sync", "browser extension", "app store"):
    if invented in combined.lower() and not (invented in ("cloud sync", "browser extension") and "no " + invented in combined.lower()):
        bad.append("invented claim: " + invented)
if root.joinpath("facts.json").is_file():
    try:
        facts = json.loads((root / "facts.json").read_text())
    except Exception:
        facts = {}
        bad.append("invalid facts JSON")
    if facts.get("title") != "QuietQueue": bad.append("wrong title")
    if facts.get("version") != "0.3.0": bad.append("wrong version")
    if sorted(facts.get("capabilities", [])) != sorted(["Save a URL from the clipboard", "Tag saved links locally", "Export the queue as JSON"]): bad.append("wrong capabilities")
    if facts.get("release_status") != "unsigned beta": bad.append("release limitation missing")
if "unsigned beta" not in combined.lower(): bad.append("beta limitation omitted")
if not any(term in combined.lower() for term in ("local-first", "local first")): bad.append("core positioning omitted")
print(bad)
sys.exit(1 if bad else 0)
