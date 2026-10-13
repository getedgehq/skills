"""Rank B-roll (scenes without the owner as subject) from an icloud-photos-bridge catalog. Local only.
Usage: python pick.py catalog.jsonl --owner <person-uuid> [--kind video|photo|all] [--top 60]
       [--min-sec 2 --max-sec 60] [--label city --label sunset] [--place "Lisbon"] [--out broll_picks.json]"""
import argparse, json, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument("catalog"); ap.add_argument("--owner")
ap.add_argument("--kind", default="video", choices=["video", "photo", "all"])
ap.add_argument("--top", type=int, default=60); ap.add_argument("--out", default="broll_picks.json")
ap.add_argument("--min-sec", type=float, default=2); ap.add_argument("--max-sec", type=float, default=60)
ap.add_argument("--label", action="append", default=[], help="keep items whose Photos labels contain this (case-insensitive)")
ap.add_argument("--place", help="substring of the coarse place name")
ap.add_argument("--window-min", type=int, default=10, help="at most one pick per this many minutes, for variety")
ap.add_argument("--max-face-size", type=float, default=0.12, help="with --people small: faces bigger than this (fraction of frame) are skipped")
ap.add_argument("--people", default="none", choices=["none", "small"], help="none = no faces and no people labels; small = small background people ok")
a = ap.parse_args()
PEOPLE = {"people", "clothing", "adult", "child", "baby", "selfie", "portrait", "costume"}

def rank(r):
    s = r["score"]; g = lambda k: s.get(k, 0) or 0
    return (g("overall") + 0.5 * g("immersiveness") + 0.5 * g("interesting_subject") + 0.4 * g("pleasant_composition")
            + 0.3 * g("harmonious_color") + 0.3 * g("sharply_focused_subject") - 0.8 * g("failure")
            - 0.4 * g("intrusive_object_presence") - 0.3 * g("noise") + (0.2 if r["favorite"] else 0))

cands = []
for line in open(a.catalog):
    r = json.loads(line)
    if a.kind != "all" and r["kind"] != a.kind: continue
    if r["kind"] == "video" and not (a.min_sec <= (r["duration"] or 0) <= a.max_sec): continue
    if r["selfie"] or r["front_camera"]: continue
    if a.owner and any(f["person"] == a.owner for f in r["faces"]): continue
    labels = [l.lower() for l in r["labels"]]
    if a.people == "none" and (r["faces"] or PEOPLE & set(labels)): continue
    if any((f["size"] or 0) > a.max_face_size for f in r["faces"]): continue   # identifiable people up close
    if a.label and not any(any(w.lower() in l for l in labels) for w in a.label): continue
    if a.place and a.place.lower() not in (r["place"] or "").lower(): continue
    r["rank_score"] = rank(r)
    r["why"] = ", ".join(r["labels"][:4]) + (f" · {r['place']}" if r["place"] else "")
    cands.append(r)

cands.sort(key=lambda r: -r["rank_score"])
picked, taken = [], []
for r in cands:
    t = dt.datetime.fromisoformat(r["date"])
    if any(abs((t - x).total_seconds()) < a.window_min * 60 for x in taken): continue
    picked.append(r); taken.append(t)
    if len(picked) >= a.top: break
json.dump(picked, open(a.out, "w"), indent=1)
print(f"{len(cands)} candidates, {len(picked)} picks -> {a.out}")
