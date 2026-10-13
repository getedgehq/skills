"""Build a local HTML contact sheet from a picks JSON (list of catalog records). Thumbnails are copied next
to the page so it opens anywhere. Usage: python sheet.py picks.json sheet_dir [--title "Selfies"]"""
import sys, os, json, shutil, html
picks, outd = json.load(open(sys.argv[1])), sys.argv[2]
title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else "Picks"
os.makedirs(f"{outd}/t", exist_ok=True)
cards = []
for i, r in enumerate(picks, 1):
    src = r.get("thumb"); name = None
    if src and os.path.exists(src):
        name = f"t/{r['uuid']}{os.path.splitext(src)[1]}"; shutil.copy(src, f"{outd}/{name}")
    meta = f"#{i} · {r['date'][:16].replace('T',' ')} · score {r.get('rank_score', 0):.2f}"
    if r.get("duration"): meta += f" · {r['duration']:.0f}s"
    if r.get("why"): meta += f"<br>{html.escape(r['why'])}"
    img = f'<img src="{name}" loading=lazy>' if name else "<div class=n>no local thumbnail</div>"
    cards.append(f'<figure>{img}<figcaption>{meta}<br><code>{r["uuid"]}</code></figcaption></figure>')
open(f"{outd}/index.html", "w").write(
    f"<title>{html.escape(title)}</title><style>body{{font:13px system-ui;margin:16px}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}}"
    f"img,.n{{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:8px;background:#eee}}figure{{margin:0}}code{{font-size:10px;color:#888}}</style>"
    f"<h1>{html.escape(title)} ({len(picks)})</h1><main>{''.join(cards)}</main>")
print(f"{outd}/index.html")
