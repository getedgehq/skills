#!/usr/bin/env python3
import json, pathlib, re, sys

ROOT = pathlib.Path(sys.argv[1])
CHECKS = [['indexable', 'not', 'index.html', 'noindex|nofollow'], ['description', 'must', 'index.html', 'name=[\'\\"]description[\'\\"]'], ['social image', 'must', 'index.html', 'property=[\'\\"]og:image[\'\\"]'], ['twitter card', 'must', 'index.html', 'twitter:card'], ['favicon', 'exists', 'favicon.svg', ''], ['robots', 'must', 'robots.txt', 'Sitemap:\\s*https?://'], ['sitemap', 'must', 'sitemap.xml', '<urlset'], ['custom 404 recovery', 'must', '404.html', 'href=[\'\\"]/[\'\\"]']]

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
