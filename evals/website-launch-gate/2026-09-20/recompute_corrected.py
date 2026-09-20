#!/usr/bin/env python3
"""Recompute the checker correction from frozen attempt artifacts.

The original checker scanned output/launch-report.md as if it were production code. That made
remediation notes containing removed insecure URLs or secret prefixes count as live defects. This
script excludes output/ through the corrected published checkers, without rerunning any agent.
"""

import json
import math
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS = sorted((ROOT / "tasks").iterdir())
ARMS = {"baseline": "base", "runs": "skill", "control": "skill"}


def check(task: Path, attempt: Path) -> dict:
    raw = subprocess.check_output(
        ["python3", str(task / "check.py"), str(attempt / "collected")], text=True
    )
    return json.loads(raw)


def interval(values: list[float]) -> list[float]:
    mean = statistics.mean(values)
    half = 2.5705818366 * statistics.stdev(values) / math.sqrt(len(values))
    return [round(mean - half, 4), round(mean + half, 4)]


results = {}
for arm, prefix in ARMS.items():
    results[arm] = {}
    for task in TASKS:
        task_id = f"website-launch-gate.{task.name}"
        results[arm][task_id] = []
        for sample in (1, 2):
            attempt = ROOT / arm / task_id / f"{prefix}-s{sample}"
            verdict = check(task, attempt)
            (attempt / "check.corrected.json").write_text(
                json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
            )
            results[arm][task_id].append(verdict)


def task_means(arm: str) -> list[float]:
    return [
        statistics.mean(v["score"] for v in results[arm][f"website-launch-gate.{t.name}"])
        for t in TASKS
    ]


base = task_means("baseline")
skill = task_means("runs")
control = task_means("control")
delta_base = [a - b for a, b in zip(skill, base)]
delta_control = [a - b for a, b in zip(skill, control)]

raw_summary = json.loads((ROOT / "summary.json").read_text())
for pair in raw_summary["pairs"]:
    task_id = pair["task_id"]
    index = pair["sample"] - 1
    pair["base_check"] = results["baseline"][task_id][index]
    pair["skill_check"] = results["runs"][task_id][index]

corrected = {
    "schema_version": "getedge-direct-ab-corrected/0.1",
    "source_summary": "summary.json",
    "correction": {
        "issue": "The original checker included output/launch-report.md in production-code scans.",
        "fix": "Exclude output/ from whole-project insecure-URL and exposed-secret scans.",
        "agents_rerun": False,
        "outputs_changed": False,
    },
    "tasks": [t.name for t in TASKS],
    "means": {
        "skill": round(statistics.mean(skill), 4),
        "baseline": round(statistics.mean(base), 4),
        "irrelevant_control": round(statistics.mean(control), 4),
    },
    "skill_minus_baseline": {
        "delta": round(statistics.mean(delta_base), 4),
        "ci95": interval(delta_base),
    },
    "skill_minus_control": {
        "delta": round(statistics.mean(delta_control), 4),
        "ci95": interval(delta_control),
    },
    "task_results": [
        {
            "id": task.name,
            "baseline": round(base[i], 4),
            "skill": round(skill[i], 4),
            "irrelevant_control": round(control[i], 4),
        }
        for i, task in enumerate(TASKS)
    ],
    "pairs": raw_summary["pairs"],
}
(ROOT / "summary.corrected.json").write_text(
    json.dumps(corrected, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({k: corrected[k] for k in ("means", "skill_minus_baseline", "skill_minus_control")}, indent=2))
