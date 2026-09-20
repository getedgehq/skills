#!/usr/bin/env python3
"""Build compact Edge result pages from a publication manifest."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def page(item: dict[str, object]) -> str:
    slug = esc(item["slug"])
    title = esc(item["title"])
    description = esc(item["description"])
    status = esc(item["status"])
    status_label = esc(item["status_label"])
    package_hash = esc(item["package_hash"])
    model = esc(item.get("model", "Not applicable"))
    method = esc(item["method"])
    stats = "".join(
        f'<div class="stat"><strong>{esc(row["value"])}</strong><span>{esc(row["label"])}</span></div>'
        for row in item["stats"]
    )
    limits = "".join(f"<li>{esc(limit)}</li>" for limit in item["limitations"])
    repo = f"https://github.com/getedgehq/skills/tree/main/{slug}"
    canonical = f"https://getedge.cc/evaluation/{slug}/"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="description" content="{description}">
<meta property="og:title" content="{title} evaluation | Edge"><meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}">
<title>{title} evaluation | Edge</title><style>
@font-face{{font-family:Inter;font-style:normal;font-weight:100 900;font-display:swap;src:url('/assets/edge-inter.woff2') format('woff2')}}
:root{{color-scheme:light;--bg:#fff;--surface:#f7f7f7;--ink:#050505;--muted:#6f6f6f;--line:#e5e5e5;--accent:#154cff;--font:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif}}
@media(prefers-color-scheme:dark){{:root{{color-scheme:dark;--bg:#1b1a17;--surface:#25241f;--ink:#f2f0eb;--muted:#b0ada5;--line:#3a3831;--accent:#a5b6ff}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 var(--font);-webkit-font-smoothing:antialiased}}a{{color:inherit;text-decoration:none}}.wrap{{width:min(1120px,calc(100% - 48px));margin:auto}}nav{{height:92px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}}.brand{{font-size:18px;font-weight:650}}.brand small{{margin-left:12px;padding-left:12px;border-left:1px solid var(--line);color:var(--muted);font-size:11px;font-weight:500}}.links{{display:flex;gap:24px;color:var(--muted);font-size:12px}}main{{padding:78px 0 100px}}.eyebrow{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:650}}h1{{max-width:900px;margin:16px 0 20px;font-size:clamp(48px,7vw,82px);line-height:1.02;letter-spacing:-.055em;font-weight:500}}.lead{{max-width:680px;font-size:18px;color:var(--muted)}}.status{{display:inline-flex;margin-top:28px;padding:8px 12px;border:1px solid var(--line);border-radius:999px;font-size:12px;color:var(--accent)}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);margin-top:70px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}.stat{{padding:28px 22px 30px;border-right:1px solid var(--line)}}.stat:last-child{{border-right:0}}.stat strong{{display:block;font-size:32px;line-height:1.15;font-weight:560;font-variant-numeric:tabular-nums}}.stat span{{display:block;margin-top:7px;font-size:11px;color:var(--muted)}}.grid{{display:grid;grid-template-columns:.8fr 1.2fr;gap:72px;margin-top:72px}}h2{{margin:0;font-size:28px;line-height:1.15;letter-spacing:-.035em;font-weight:540}}.copy{{border-top:1px solid var(--line)}}.row{{padding:23px 0;border-bottom:1px solid var(--line)}}.row span{{display:block;margin-bottom:6px;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}.row p,.row ul{{margin:0;color:var(--muted)}}ul{{padding-left:18px}}code{{font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;overflow-wrap:anywhere}}.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:30px}}.btn{{display:inline-flex;min-height:44px;align-items:center;padding:0 17px;border:1px solid var(--line);border-radius:9px;font-size:12px}}.btn.primary{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}footer{{padding:32px 0 48px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}}
@media(max-width:760px){{.wrap{{width:min(100% - 30px,1120px)}}nav{{height:76px}}.links a:not(:last-child){{display:none}}main{{padding-top:52px}}h1{{font-size:46px}}.stats{{grid-template-columns:repeat(2,1fr)}}.stat:nth-child(2){{border-right:0}}.stat:nth-child(-n+2){{border-bottom:1px solid var(--line)}}.grid{{grid-template-columns:1fr;gap:30px;margin-top:52px}}}}
</style></head><body><div class="wrap"><nav><a class="brand" href="/">Edge <small>skills that prove their work</small></a><div class="links"><a href="/explore/">Explore</a><a href="/standards/">Standards</a><a href="{repo}">GitHub</a></div></nav>
<main><p class="eyebrow">Evaluation receipt / {slug}</p><h1>{title}</h1><p class="lead">{description}</p><span class="status">{status_label}</span>
<section class="stats">{stats}</section>
<section class="grid"><div><p class="eyebrow">What this proves</p><h2>{esc(item["claim"])}</h2><div class="actions"><a class="btn primary" href="{repo}">Inspect package</a><a class="btn" href="/eval-data/{slug}/index.json">Machine record</a></div></div>
<div class="copy"><div class="row"><span>Status</span><p>{status}. {esc(item["status_explanation"])}</p></div><div class="row"><span>Method</span><p>{method}</p></div><div class="row"><span>Model</span><p>{model}</p></div><div class="row"><span>Limitations</span><ul>{limits}</ul></div><div class="row"><span>Exact package</span><code>sha256:{package_hash}</code></div></div></section></main></div>
<footer><div class="wrap">Evidence is published with its limits. A package page, a controlled result, and a universal claim are different things.</div></footer></body></html>'''


def build(manifest: Path, output: Path) -> None:
    records = json.loads(manifest.read_text(encoding="utf-8"))
    routes: list[str] = []
    for item in records:
        slug = str(item["slug"])
        evaluation = output / "evaluation" / slug / "index.html"
        skill = output / "skills" / slug / "index.html"
        data = output / "eval-data" / slug / "index.json"
        for target in (evaluation, skill, data):
            target.parent.mkdir(parents=True, exist_ok=True)
        rendered = page(item)
        evaluation.write_text(rendered, encoding="utf-8")
        skill.write_text(rendered.replace(f"/evaluation/{slug}/", f"/skills/{slug}/"), encoding="utf-8")
        data.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
        routes.extend((f"/evaluation/{slug}/", f"/skills/{slug}/", f"/eval-data/{slug}/index.json"))
    (output / "result-routes.txt").write_text("\n".join(routes) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.manifest.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
