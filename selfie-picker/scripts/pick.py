"""Rank the owner's best selfies from an icloud-photos-bridge catalog. Pure local ranking, no network.
Usage: python pick.py catalog.jsonl --owner <person-uuid> [--top 60] [--out picks.json] [--include-portraits] [--allow-others 0]"""
import argparse, json, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument("catalog"); ap.add_argument("--owner", required=True)
ap.add_argument("--top", type=int, default=60); ap.add_argument("--out", default="selfie_picks.json")
ap.add_argument("--include-portraits", action="store_true", help="also photos taken by others where the owner is the main subject")
ap.add_argument("--allow-others", type=int, default=0, help="max other faces in frame")
ap.add_argument("--burst-seconds", type=int, default=600, help="keep one shot per this window (near-duplicates from the same moment)")
a = ap.parse_args()
if a.owner in ("", "NOT SET"):
    raise SystemExit("No owner saved. Run icloud-photos-bridge's owner.py list, confirm with the user, then owner.py set <person-uuid>.")

def rank(r, me):
    s = r["score"]; g = lambda k: s.get(k, 0) or 0
    v = (g("overall") + 0.6 * g("well_framed_subject") + 0.6 * g("sharply_focused_subject")
         + 0.4 * g("pleasant_lighting") + 0.3 * g("pleasant_composition") - 0.8 * g("failure") - 0.3 * g("noise"))
    v += 0.3 * (me.get("quality") or 0)            # Photos' own face quality
    v += 0.15 if me.get("smile") else 0
    v -= 0.6 if me.get("eyes") == 1 else 0         # eye_state 1 = closed (2 = open, 0 = unknown)
    v += 0.2 if r["favorite"] else 0
    return v

cands = []
for line in open(a.catalog):
    r = json.loads(line)
    if r["kind"] != "photo": continue
    me = next((f for f in r["faces"] if f["person"] == a.owner), None)
    if not me: continue
    others = [f for f in r["faces"] if f["person"] != a.owner]
    if len(others) > a.allow_others: continue
    if any((f["size"] or 0) > (me["size"] or 0) for f in others): continue   # owner must be the main face
    is_selfie = r["selfie"] or r["front_camera"]
    if not is_selfie and not a.include_portraits: continue
    if r["burst"] and not r["burst_selected"]: continue
    r["rank_score"] = rank(r, me)
    r["why"] = ("selfie" if is_selfie else "portrait") + (" · smile" if me.get("smile") else "") + (" · eyes closed?" if me.get("eyes") == 1 else "") + (" · ♥" if r["favorite"] else "")
    cands.append(r)

cands.sort(key=lambda r: -r["rank_score"])
picked, taken = [], []
for r in cands:                                    # one shot per burst window, best first
    t = dt.datetime.fromisoformat(r["date"])
    if any(abs((t - x).total_seconds()) < a.burst_seconds for x in taken): continue
    picked.append(r); taken.append(t)
    if len(picked) >= a.top: break
json.dump(picked, open(a.out, "w"), indent=1)
print(f"{len(cands)} candidates, {len(picked)} picks -> {a.out}")
