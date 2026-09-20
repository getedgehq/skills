import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
try:
    rows = json.loads(path.read_text())
except Exception as exc:
    print(f"invalid JSON: {exc}")
    raise SystemExit(1)

expected = {
    "api-403": ("recommend", "http-error-triage"),
    "uptime-covered": ("covered", None),
    "translate-basic": ("unnecessary", None),
    "private-mail": ("no_match", None),
    "agent-quality": ("recommend", "agent-evals"),
    "logo-keyword-trap": ("no_match", None),
}
catalog = {p.name for p in pathlib.Path("catalog").iterdir() if p.is_dir()}
bad = []
if not isinstance(rows, list):
    bad.append("top level must be a list")
    rows = []
by_id = {r.get("id"): r for r in rows if isinstance(r, dict)}
if len(rows) != len(by_id):
    bad.append("duplicate or malformed rows")
if set(by_id) != set(expected):
    bad.append(f"IDs differ: {sorted(by_id)}")
for rid, want in expected.items():
    row = by_id.get(rid, {})
    got = (row.get("decision"), row.get("skill_id"))
    if got != want:
        bad.append(f"{rid}: expected {want}, got {got}")
    if set(row) != {"id", "decision", "skill_id", "reason"}:
        bad.append(f"{rid}: wrong fields")
    if not isinstance(row.get("reason"), str) or not 0 < len(row.get("reason", "")) <= 180:
        bad.append(f"{rid}: invalid reason")
    if row.get("decision") == "recommend" and row.get("skill_id") not in catalog:
        bad.append(f"{rid}: invented skill ID")
print(bad)
raise SystemExit(1 if bad else 0)
