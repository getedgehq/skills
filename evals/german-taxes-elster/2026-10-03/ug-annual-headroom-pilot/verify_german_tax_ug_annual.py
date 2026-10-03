#!/usr/bin/env python3
"""Objective gate for german-tax-ug-annual. Expected: GewSt 2,870 (no Freibetrag for a UG), KSt 3,000,
KSt Ruecktrag yes / GewSt no, no IAB, Einspruch can worsen (Verboeserung), employer could NOT apply
Fuenftel since 2025, ESt 2026 return needed, Antragsveranlagung deadline 31.12.2030."""
import json, sys
try:
    d = json.load(open("out/answers.json"))
except Exception as e:
    print("no/invalid out/answers.json", e); sys.exit(1)
want = {"verlustruecktrag_kst_possible": True, "verlustruecktrag_gewst_possible": False,
        "take_iab_7g": False, "einspruch_can_make_it_worse": True,
        "employer_applied_fuenftel_correctly": False, "file_est_2026_needed_for_fuenftel": True}
f = []
def n(k):
    try: return float(str(d.get(k)).replace(".", "").replace(",", ".")) if isinstance(d.get(k), str) else float(d.get(k))
    except Exception: return None
if n("gewst_2025_eur") is None or abs(n("gewst_2025_eur") - 2870) > 1: f.append(f"gewst={d.get('gewst_2025_eur')}")
if n("kst_2025_eur") is None or abs(n("kst_2025_eur") - 3000) > 1: f.append(f"kst={d.get('kst_2025_eur')}")
for k, v in want.items():
    if d.get(k) is not v: f.append(f"{k}={d.get(k)}")
if str(d.get("est_2026_latest_deadline", "")).strip() not in ("31.12.2030",): f.append(f"deadline={d.get('est_2026_latest_deadline')}")
if f: print("FAIL: " + "; ".join(f)); sys.exit(1)
print("PASS")
