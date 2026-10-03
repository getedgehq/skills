#!/usr/bin/env python3
"""Objective gate for the german-tax-ustva-q3 brief. Runs in the arm's workdir.
Expected (Ist, Regelbesteuerung, no USt-IdNr, company card except one private domain invoice):
  Kz81 500 | Kz46 100 / Kz47 19.00 (Anthropic Ireland, EU reverse charge on the net)
  Kz84 63 (Cursor 40 + Supabase USD 25 at BMF rate 1.0870 = 23.00; 62 accepted for bank rate)
  Kz67 = Kz47 + Kz85 (~30.97) | Kz66 5.70 (Hetzner only: no DE000000000 VAT, no private invoice)
  Einspruch deadline against the 29.09.2026 Bescheid: 4-day Bekanntgabe -> Sat 03.10 (holiday)
  -> Mon 05.10.2026 -> deadline Thu 05.11.2026.
"""
import json, os, re, sys

fails = []
def num(d, k):
    for key in (k, k.upper(), k.replace("kz", "Kz"), k.replace("kz", "Kz ")):
        if key in d:
            v = d[key]
            if isinstance(v, str):
                v = v.replace(".", "").replace(",", ".") if "," in v else v
            try:
                return float(v)
            except Exception:
                return None
    return 0.0

try:
    d = json.load(open("out/ustva.json"))
    if isinstance(d, dict) and "kz" in d and isinstance(d["kz"], dict):
        d = d["kz"]
except Exception as e:
    print("no/invalid out/ustva.json:", e); sys.exit(1)

def near(k, want, tol):
    v = num(d, k)
    if v is None or abs(v - want) > tol:
        fails.append(f"{k}={v} want {want}")

near("kz81", 500, 0.5)
near("kz66", 5.70, 0.02)
near("kz46", 100, 0.5)
near("kz47", 19.00, 0.05)
v84 = num(d, "kz84")
if v84 is None or not (62 - 0.01 <= v84 <= 63.01):
    fails.append(f"kz84={v84} want 63 (62 tolerated)")
v67, v47, v85 = num(d, "kz67"), num(d, "kz47"), num(d, "kz85")
if None in (v67, v47, v85) or abs(v67 - (v47 + v85)) > 0.05 or not (30.7 <= v67 <= 31.05):
    fails.append(f"kz67={v67} want ~30.97 = kz47+kz85")

text = ""
for p in ("out/notes.md",):
    if os.path.exists(p):
        text += open(p, errors="replace").read()
fp = os.environ.get("FORGE_FINAL")
if fp and os.path.exists(fp):
    text += open(fp, errors="replace").read()
if not re.search(r"\b0?5\.\s?11\.\s?(20)?26\b|2026-11-05|\b0?5\.?\s+Nov(ember)?\.?\s+2026|Nov(ember)?\.?\s+0?5,?\s+2026", text, re.I):
    fails.append("Einspruch deadline 05.11.2026 not stated")

if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS"); sys.exit(0)
