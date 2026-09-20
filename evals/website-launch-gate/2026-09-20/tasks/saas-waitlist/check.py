#!/usr/bin/env python3
import json, pathlib, re, sys

ROOT = pathlib.Path(sys.argv[1])
CHECKS = [['specific title', 'must', 'index.html', '<title>[^<]*(AcmeFlow)[^<]+</title>'], ['meta description', 'must', 'index.html', 'name=[\'\\"]description[\'\\"]'], ['privacy link', 'must', 'index.html', 'href=[\'\\"]privacy\\.html[\'\\"]'], ['privacy page', 'exists', 'privacy.html', ''], ['email validation', 'must', 'index.html', 'type=[\'\\"]email[\'\\"][^>]*required|required[^>]*type=[\'\\"]email[\'\\"]'], ['accessible status', 'must', 'index.html', 'aria-live='], ['no exposed secret', 'not', '*', 'sk_live_|TEST_ONLY_SHOULD_NOT_SHIP'], ['error state', 'must', 'app.js', 'catch\\s*\\(|!r\\.ok|!.*\\.ok']]

def read(rel):
    p = ROOT / rel
    return p.read_text(errors="ignore") if p.exists() and p.is_file() else ""

all_text = "\n".join(
    p.read_text(errors="ignore")
    for p in ROOT.rglob("*")
    if p.is_file()
    and p.stat().st_size < 2_000_000
    and "output" not in p.relative_to(ROOT).parts
)
details = []
passed = 0
for name, kind, rel, arg in CHECKS:
    text = all_text if rel == "*" else read(rel)
    if kind == "must": ok = bool(re.search(arg, text, re.I | re.S))
    elif kind == "not": ok = not bool(re.search(arg, text, re.I | re.S))
    elif kind == "exists": ok = (ROOT / rel).is_file() and (ROOT / rel).stat().st_size > 0
    elif kind == "maxsize": ok = (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= int(arg)
    else: ok = False
    passed += int(ok)
    details.append(f"{'PASS' if ok else 'FAIL'}: {name}")
report = ROOT / "output" / "launch-report.md"
report_ok = report.is_file() and report.stat().st_size >= 80
details.append(f"{'PASS' if report_ok else 'FAIL'}: launch report")
passed += int(report_ok)
total = len(CHECKS) + 1
print(json.dumps({"pass": passed == total, "score": round(passed / total, 4), "details": details}))
