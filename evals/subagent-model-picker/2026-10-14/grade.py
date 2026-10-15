"""Hidden grader. Usage: python3 grade.py WORKDIR -> prints JSON with per-task checks."""
import json, sys, pathlib, importlib, subprocess
from datetime import date
wd = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(wd))
res = {}

# 1 inventory (exact expected list)
expected = sorted(["dates.days_between", "dates.is_weekend", "money.format_cents",
                   "money.total", "report.pad_label", "report.table"])
inv = wd / "INVENTORY.md"
got = [l.strip() for l in inv.read_text().splitlines() if l.strip()] if inv.exists() else []
res["inventory"] = {"pass": int(got == expected), "total": 1, "got": got}

# 2 dates (hidden cases)
checks = 0; ok = 0
try:
    dates = importlib.import_module("ledgerkit.dates")
    cases = [("2026-03-04", date(2026, 3, 4)), ("04/03/2026", date(2026, 3, 4)),
             (" 31/12/2025 ", date(2025, 12, 31)), ("04/03/26", date(2026, 3, 4)),
             ("01/01/69", date(2069, 1, 1)), ("01/01/70", date(1970, 1, 1)),
             ("15/08/99", date(1999, 8, 15))]
    for s, want in cases:
        checks += 1
        try: ok += int(dates.parse_date(s) == want)
        except Exception: pass
    for bad in ["2026.03.04", "hello"]:
        checks += 1
        try: dates.parse_date(bad)
        except ValueError: ok += 1
        except Exception: pass
except Exception:
    checks = 9
res["dates"] = {"pass": ok, "total": checks}

# 3 allocate (hidden cases)
def ref(total, w):
    if not w or any(x < 0 for x in w) or sum(w) == 0: raise ValueError
    from fractions import Fraction
    neg = total < 0; T = abs(total)
    F = [Fraction(x) for x in w]; S = sum(F)
    exact = [T * f / S for f in F]
    base = [int(e // 1) for e in exact]
    left = T - sum(base)
    order = sorted(range(len(w)), key=lambda i: (-(exact[i] - base[i]), i))
    for i in order[:left]: base[i] += 1
    return [-b for b in base] if neg else base
acases = [(100, [1, 1, 1]), (5, [1, 1]), (7, [2, 3, 5]), (-100, [1, 1, 1]), (1, [0, 1, 1]),
          (10, [0.25, 0.25, 0.5]), (99, [3]), (0, [1, 2]), (1000003, [33, 33, 34]),
          (17, [1, 0, 2, 0, 3])]
ok = 0; checks = 0
try:
    money = importlib.import_module("ledgerkit.money")
    for t, w in acases:
        checks += 1
        try: ok += int(money.allocate(t, w) == ref(t, w))
        except Exception: pass
    for w in ([], [0, 0], [1, -1]):
        checks += 1
        try: money.allocate(10, w)
        except ValueError: ok += 1
        except Exception: pass
except Exception:
    checks = 13
res["allocate"] = {"pass": ok, "total": checks}

# 4 config
want = {"server": {"host": "ledger.internal", "port": 8443, "debug": False, "timeout_s": 12.5},
        "export": {"formats": ["csv", "xlsx", "json"], "currency": "EUR", "round_half_even": True, "max_rows": 50000},
        "alerts": {"emails": ["ops@example.com", "finance@example.com"], "threshold": 0.75, "enabled": True}}
ok = 0; checks = 0
try: cj = json.loads((wd / "config.json").read_text())
except Exception: cj = {}
for s, kv in want.items():
    for k, v in kv.items():
        checks += 1
        g = cj.get(s, {}).get(k, None) if isinstance(cj.get(s), dict) else None
        ok += int(g == v and type(g) == type(v))
checks += 1; ok += int((wd / "config.ini").exists())
res["config"] = {"pass": ok, "total": checks}

# visible test suite still green
r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(wd / "tests")], cwd=wd, capture_output=True, text=True)
res["visible_tests_green"] = r.returncode == 0
res["score"] = sum(v["pass"] for v in res.values() if isinstance(v, dict))
res["max"] = sum(v["total"] for v in res.values() if isinstance(v, dict))
print(json.dumps(res))
