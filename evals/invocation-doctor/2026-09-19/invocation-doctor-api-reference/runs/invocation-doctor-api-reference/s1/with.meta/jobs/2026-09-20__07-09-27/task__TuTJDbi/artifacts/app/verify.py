from __future__ import annotations

import json
import sys
from pathlib import Path

bad=[]
for name in ("revised-skill.md", "trigger-report.json"):
    if not Path("out",name).is_file(): bad.append("missing "+name)
if not bad:
    text=Path("out/revised-skill.md").read_text()
    if not text.startswith("---\n"): bad.append("missing front matter")
    try:
        head=text.split("---\n",2)[1]
    except Exception:
        head=""
    description=next((line.split(":",1)[1].strip() for line in head.splitlines() if line.startswith("description:")),"")
    low=description.lower()
    if not 50 <= len(description) <= 350: bad.append("description length")
    if not any(term in low for term in ("openapi","swagger","api specification")): bad.append("positive trigger missing")
    if not all(term in low for term in ("marketing","blog")): bad.append("near-miss exclusions missing")
    original=Path("source-skill.md").read_text().split("---\n",2)[2]
    revised=text.split("---\n",2)[2] if text.count("---\n")>=2 else ""
    if revised.strip()!=original.strip(): bad.append("body changed")
    try: report=json.loads(Path("out/trigger-report.json").read_text())
    except Exception: report={}; bad.append("invalid report")
    expected={row["id"]:row["expected"] for row in json.loads(Path("cases.json").read_text()) if row["split"]=="holdout"}
    predictions={row.get("id"):row.get("invoke") for row in report.get("heldout_predictions",[])}
    if predictions!=expected: bad.append("heldout predictions wrong")
    if report.get("tuned_on")!="train" or report.get("reported_on")!="holdout": bad.append("split disclosure missing")
    if report.get("heldout_accuracy")!=1.0: bad.append("heldout accuracy wrong")
print(bad); sys.exit(1 if bad else 0)
