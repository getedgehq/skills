"""Find whose face is whose. Lists the biggest face clusters with a sample thumbnail page, and saves the owner.
Usage: python owner.py list [--top 12] [--html people.html]   -> pick the cluster that is the library owner
       python owner.py set <person-uuid>                       -> saved to ~/.config/icloud-photos/owner.json
       python owner.py get"""
import sys, os, json, html, osxphotos
CFG = os.path.expanduser("~/.config/icloud-photos/owner.json")
cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
if cmd == "set":
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    json.dump({"owner": sys.argv[2]}, open(CFG, "w")); print("owner saved", sys.argv[2]); sys.exit()
if cmd == "get":
    print(json.load(open(CFG))["owner"] if os.path.exists(CFG) else "NOT SET"); sys.exit()
top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 12
out = sys.argv[sys.argv.index("--html") + 1] if "--html" in sys.argv else "people.html"
db = osxphotos.PhotosDB()
nm = lambda p: None if (p.name or '').startswith('_UNK') else p.name
people = sorted([p for p in db.person_info if p.facecount], key=lambda p: -p.facecount)[:top]
rows = []
for p in people:
    kp = p.keyphoto
    thumb = (kp.path_derivatives or [None])[0] if kp else None
    print(f"{p.uuid}  faces={p.facecount:5d}  name={nm(p) or '-'}")
    img = f'<img src="file://{html.escape(thumb)}">' if thumb else "(no thumbnail)"
    rows.append(f"<div class=c>{img}<p><b>{html.escape(nm(p) or 'unnamed')}</b> {p.facecount} faces<br><code>{p.uuid}</code></p></div>")
open(out, "w").write("<style>body{font:14px system-ui;display:flex;flex-wrap:wrap;gap:12px}.c{width:220px}img{width:220px;height:220px;object-fit:cover;border-radius:8px}</style>" + "".join(rows))
print(f"open {out} and pick the owner; the largest unnamed cluster is usually the owner")
