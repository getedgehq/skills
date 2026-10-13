"""Write a metadata catalog of the Photos (iCloud) library as JSONL. Reads only; never modifies Photos.
Usage: python catalog.py --out catalog.jsonl [--since 2026-08-01] [--until 2026-10-31] [--kind photo|video|all]"""
import argparse, json, datetime as dt, osxphotos

KEEP = ["overall", "curation", "failure", "sharply_focused_subject", "well_framed_subject", "pleasant_composition",
        "pleasant_lighting", "pleasant_camera_tilt", "well_timed_shot", "interesting_subject", "noise", "low_light",
        "harmonious_color", "immersiveness", "intrusive_object_presence"]

def day(s): return dt.datetime.fromisoformat(s).astimezone()

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--since"); ap.add_argument("--until")
ap.add_argument("--kind", default="all", choices=["photo", "video", "all"])
a = ap.parse_args()
db = osxphotos.PhotosDB()
kw = {}
if a.since: kw["from_date"] = day(a.since)
if a.until: kw["to_date"] = day(a.until) + dt.timedelta(days=1)
n = 0
with open(a.out, "w") as f:
    for p in db.photos(images=a.kind != "video", movies=a.kind != "photo", **kw):
        if p.hidden or p.intrash or p.screenshot: continue
        faces = []
        for fi in (p.face_info or []):
            d = fi.asdict(); pi = fi.person_info
            faces.append({"person": pi.uuid if pi else None, "name": (pi.name if pi else None) or None,
                          "size": d.get("size"), "quality": d.get("quality"), "eyes": d.get("eye_state"),
                          "smile": d.get("has_smile"), "yaw": d.get("yaw")})
        e = p.exif_info
        sc = p.score.asdict() if p.score else {}
        rec = {"uuid": p.uuid, "date": p.date.isoformat(), "kind": "video" if p.ismovie else "photo",
               "selfie": bool(p.selfie), "front_camera": "front" in ((e.lens_model or "") if e else "").lower(),
               "favorite": p.favorite, "burst": p.burst, "burst_selected": p.burst_selected, "live": p.live_photo,
               "portrait": p.portrait, "w": p.width, "h": p.height,
               "duration": (e.duration if (e and p.ismovie) else None),
               "local_original": not p.ismissing, "thumb": (p.path_derivatives or [None])[0],
               "place": (p.place.name if p.place else None), "labels": list(p.labels or [])[:12],
               "score": {k: round(sc[k], 3) for k in KEEP if sc.get(k) is not None}, "faces": faces}
        f.write(json.dumps(rec) + "\n"); n += 1
print(f"{n} items -> {a.out}")
