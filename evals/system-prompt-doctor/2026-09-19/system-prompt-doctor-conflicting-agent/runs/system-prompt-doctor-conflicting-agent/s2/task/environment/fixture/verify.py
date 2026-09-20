from __future__ import annotations

import json
import sys
from pathlib import Path

bad = []
for name in ("audit.json", "optimized-prompt.md", "eval-manifest.json", "behavioral-diff.md"):
    if not Path("out", name).is_file(): bad.append("missing " + name)
if not bad:
    prompt = Path("out/optimized-prompt.md").read_text()
    lower = prompt.lower()
    if len(prompt) >= len(Path("current-prompt.md").read_text()): bad.append("prompt not compacted")
    for invariant in ("production", "authorization", "unrelated", "test", "secret"):
        if invariant not in lower: bad.append("lost invariant " + invariant)
    for phrase in ("think step by step", "reveal your reasoning", "be helpful and smart", "always act immediately", "never act without asking"):
        if phrase in lower: bad.append("retained defective phrase")
    if not ("diagnos" in lower and "change" in lower): bad.append("diagnose versus change boundary missing")
    if not ("read" in lower and "permission" in lower): bad.append("read-only permission rule missing")
    try:
        manifest = json.loads(Path("out/eval-manifest.json").read_text())
    except Exception:
        manifest = {}
        bad.append("invalid eval manifest")
    cases = manifest.get("cases", [])
    if len(cases) < 8: bad.append("too few eval cases")
    if sum(1 for case in cases if case.get("split") == "holdout") < 2: bad.append("missing holdout")
    if not all(case.get("expected") for case in cases): bad.append("missing expected behaviors")
    try:
        audit = json.loads(Path("out/audit.json").read_text())
    except Exception:
        audit = {}
        bad.append("invalid audit")
    if not audit.get("diagnostic_only"): bad.append("audit presented as score")
print(bad)
sys.exit(1 if bad else 0)
