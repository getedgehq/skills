"""Write a contact sheet of picks as ONE self-contained .html file (thumbnails embedded), opens in any browser.
Each photo shows its number, filename, date and caption (`caption`, else `why`, else place and labels).
Usage: python sheet.py picks.json out.html [--title "Selfies"]   (a folder instead of out.html writes folder/index.html)
montage.py calls write() too, so every montage JPG gets this HTML next to it."""
import base64, html, io, json, os, sys

CSS = """:root{--ground:#f5f3eb;--ink:#16251e;--muted:#59685f;--surface:#fff;--blue:#154cff;--soft:#e9efff;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--ground:#121a16;--ink:#eef2ec;--muted:#a3b0a8;--surface:#1c2621;--soft:#1f2a4d;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.5 "Inter Display",Inter,system-ui,-apple-system,sans-serif}
main{max-width:1280px;margin:0 auto;padding:48px 20px 64px}
h1{font-weight:500;letter-spacing:-.035em;line-height:1;font-size:clamp(30px,4vw,48px);margin:0 0 12px}
.lede{color:var(--muted);font-size:17px;letter-spacing:-.01em;margin:0 0 32px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}
figure{margin:0;background:var(--surface);border-radius:18px;overflow:hidden;box-shadow:0 1px 2px rgba(22,37,30,.06),0 8px 24px rgba(22,37,30,.06)}
.ph{position:relative;aspect-ratio:4/5;background:var(--soft)}.ph img{width:100%;height:100%;object-fit:cover;display:block}
.ph .none{position:absolute;inset:0;display:grid;place-items:center;color:var(--muted);font-size:13px}
.tag{position:absolute;top:10px;left:10px;background:rgba(22,37,30,.72);color:#fff;font-size:12px;font-weight:500;padding:3px 9px;border-radius:999px}
.tag.r{left:auto;right:10px}
figcaption{padding:12px 14px 14px}.fn{font-weight:500;font-size:14px;overflow-wrap:anywhere}
.d{color:var(--muted);font-size:13px}.c{color:var(--muted);font-size:13px;margin-top:4px}"""


def thumb_uri(path, size=640):
    if not path or not os.path.exists(path):
        return None
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB"); im.thumbnail((size, size))
        b = io.BytesIO(); im.save(b, "JPEG", quality=78)
        return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    except Exception:
        return None


def caption(r):
    if r.get("caption") or r.get("why"):
        return r.get("caption") or r["why"]
    return " · ".join(x for x in [r.get("place")] + list(r.get("labels") or [])[:3] if x)


def write(picks, out, title="Picks"):
    e = lambda s: html.escape(str(s))
    cards = []
    for i, r in enumerate(picks, 1):
        uri = thumb_uri(r.get("thumb"))
        img = f'<img src="{uri}" alt="">' if uri else '<div class="none">no local preview</div>'
        dur = f'<span class="tag r">{r["duration"]:.0f}s</span>' if r.get("duration") else ""
        cap = caption(r)
        cards.append(f'<figure><div class="ph">{img}<span class="tag">{i}</span>{dur}</div><figcaption>'
                     f'<div class="fn">{e(r.get("filename") or r["uuid"])}</div>'
                     f'<div class="d">{e((r.get("date") or "")[:16].replace("T", " "))}</div>'
                     + (f'<div class="c">{e(cap)}</div>' if cap else "") + "</figcaption></figure>")
    dates = sorted(r["date"][:10] for r in picks if r.get("date"))
    span = f" · {dates[0]} to {dates[-1]}" if dates and dates[0] != dates[-1] else (f" · {dates[0]}" if dates else "")
    page = (f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)}</title><style>{CSS}</style><main><h1>{e(title)}</h1>'
            f'<p class="lede">{len(picks)} {"item" if len(picks) == 1 else "items"}{span}</p>'
            f'<div class="grid">{"".join(cards)}</div></main>')
    if not out.endswith(".html"):
        os.makedirs(out, exist_ok=True); out = os.path.join(out, "index.html")
    open(out, "w").write(page)
    return out


if __name__ == "__main__":
    title = sys.argv[sys.argv.index("--title") + 1] if "--title" in sys.argv else "Picks"
    print(write(json.load(open(sys.argv[1])), sys.argv[2], title))
