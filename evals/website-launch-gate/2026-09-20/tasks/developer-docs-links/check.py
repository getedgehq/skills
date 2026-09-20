#!/usr/bin/env python3
import json, pathlib, re, sys

ROOT = pathlib.Path(sys.argv[1])
CHECKS = [['no insecure asset', 'not', '*', '(?:src|href)=[\'\\"]http://'], ['meaningful alt', 'must', 'index.html', '<img[^>]+alt=[\'\\"][^\'\\"]{12,}'], ['guide target', 'exists', 'guide.html', ''], ['api target', 'exists', 'api.html', ''], ['CTA target', 'exists', 'quickstart.html', ''], ['clear CTA', 'must', 'index.html', 'class=[\'\\"]cta[\'\\"][^>]*href=[\'\\"]quickstart\\.html[\'\\"][^>]*>\\s*(?:Start|Install|Quickstart)'], ['description', 'must', 'index.html', 'name=[\'\\"]description[\'\\"]']]

def read(rel):
    p = ROOT / rel
    return p.read_text(errors="ignore") if p.exists() and p.is_file() else ""

all_text = "\n".join(p.read_text(errors="ignore") for p in ROOT.rglob("*") if p.is_file() and p.stat().st_size < 2_000_000)
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
