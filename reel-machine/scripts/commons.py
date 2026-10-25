#!/usr/bin/env python3
"""commons.py OUTDIR key="File:Some photo.jpg" [key2="File:..." ...]

Downloads a 1600 px version of each Wikimedia Commons file into OUTDIR/<key>.<ext> and records
its credit ("Author, Licence (Wikimedia Commons)") in OUTDIR/credits.json. Put that credit on the
cutaway in the spec ("cuts": [{"image": ..., "credit": ...}]); mkreel.py collects the credits of a
reel into credits.txt for the post caption. Use only files whose licence allows reuse (CC BY,
CC BY-SA, CC0, public domain) and keep the credit line with the post.
Wikimedia asks every API client for a User-Agent with a contact: set REEL_HTTP_CONTACT.
"""
import html, json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

if len(sys.argv) < 3:
    sys.exit(__doc__)
contact = rmconf.get("REEL_HTTP_CONTACT")
if not contact:
    sys.exit("set REEL_HTTP_CONTACT (a URL or email) in config: Wikimedia requires a contact in the User-Agent")
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
cf = out / "credits.json"
cred = json.loads(cf.read_text()) if cf.exists() else {}
UA = {"User-Agent": f"reel-machine/1.1 ({contact})"}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()


def strip(s):
    return re.sub(r"<[^>]+>", "", html.unescape(s or "")).strip()


for kv in sys.argv[2:]:
    k, t = kv.split("=", 1)
    q = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "titles": t, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1600, "format": "json"})
    page = list(json.loads(get(q))["query"]["pages"].values())[0]
    if "imageinfo" not in page:
        sys.exit(f"not found on Commons: {t}")
    ii = page["imageinfo"][0]; m = ii["extmetadata"]
    author = strip(m.get("Artist", {}).get("value", "")) or "Unknown author"
    lic = strip(m.get("LicenseShortName", {}).get("value", ""))
    url = ii.get("thumburl") or ii["url"]; ext = os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
    (out / f"{k}{ext}").write_bytes(get(url))
    cred[k] = f"{author}, {lic} (Wikimedia Commons)"
    print(k, ext, cred[k])
cf.write_text(json.dumps(cred, indent=1, ensure_ascii=False))
