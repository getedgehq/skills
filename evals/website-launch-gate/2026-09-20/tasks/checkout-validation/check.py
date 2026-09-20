#!/usr/bin/env python3
import json, pathlib, re, sys

ROOT = pathlib.Path(sys.argv[1])
CHECKS = [['browser validation enabled', 'not', 'index.html', '\\bnovalidate\\b'], ['email required', 'must', 'index.html', 'type=[\'\\"]email[\'\\"][^>]*required|required[^>]*type=[\'\\"]email[\'\\"]'], ['terms required', 'must', 'index.html', 'type=[\'\\"]checkbox[\'\\"][^>]*(?:name=[\'\\"]terms[\'\\"]|required)[^>]*required|name=[\'\\"]terms[\'\\"][^>]*required'], ['honeypot', 'must', 'index.html', 'name=[\'\\"](?:website|company_url|honeypot)[\'\\"]'], ['HTTPS API', 'not', '*', 'http://api\\.workshop\\.example'], ['server validation', 'must', 'server.js', 'status\\((?:400|422)\\)'], ['rate limiting', 'must', 'server.js', 'rateLimit|rate.?limit'], ['terms page', 'exists', 'terms.html', '']]

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
