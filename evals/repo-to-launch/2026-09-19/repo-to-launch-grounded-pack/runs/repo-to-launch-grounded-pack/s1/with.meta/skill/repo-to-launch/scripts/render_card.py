#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json
from pathlib import Path

W,H=1200,675

def esc(s): return html.escape(str(s))

def render_svg(data: dict) -> str:
    title=esc(data.get('title','Edge experiment'))
    eyebrow=esc(data.get('eyebrow','EDGE LAB'))
    subtitle=esc(data.get('subtitle',''))
    badge=esc(data.get('badge',''))
    footer=esc(data.get('footer',''))
    metrics=data.get('metrics',[])[:4]
    findings=data.get('findings',[])[:3]
    metric_nodes=[]
    x=72
    n=max(1,len(metrics)); boxw=(1056-(n-1)*18)/n
    for m in metrics:
        metric_nodes.append(f'''<g transform="translate({x},272)"><rect width="{boxw}" height="150" rx="24" fill="#111"/><text x="24" y="42" font-family="Inter,Arial,sans-serif" font-size="19" fill="#999">{esc(m.get('label',''))}</text><text x="24" y="102" font-family="Inter,Arial,sans-serif" font-size="48" font-weight="700" fill="white">{esc(m.get('value',''))}</text></g>''')
        x += boxw+18
    finding_nodes=[]
    y=475
    for f in findings:
        finding_nodes.append(f'''<text x="84" y="{y}" font-family="Inter,Arial,sans-serif" font-size="22" fill="#d8d8d8">• {esc(f)}</text>''')
        y+=36
    badge_node=''
    if badge:
        bw=min(360,max(110,20+len(badge)*11))
        badge_node=f'''<g transform="translate({1128-bw},64)"><rect width="{bw}" height="42" rx="21" fill="#151515" stroke="#333"/><text x="{bw/2}" y="27" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="16" font-weight="600" fill="#eee">{badge}</text></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="100%" height="100%" fill="#050505"/>
<text x="72" y="86" font-family="Inter,Arial,sans-serif" font-size="17" font-weight="700" letter-spacing="2" fill="#8e8e8e">{eyebrow}</text>
{badge_node}
<text x="72" y="170" font-family="Inter,Arial,sans-serif" font-size="56" font-weight="700" fill="white">{title}</text>
<text x="72" y="218" font-family="Inter,Arial,sans-serif" font-size="23" fill="#aaa">{subtitle}</text>
{''.join(metric_nodes)}
{''.join(finding_nodes)}
<text x="72" y="635" font-family="Inter,Arial,sans-serif" font-size="16" fill="#666">{footer}</text>
</svg>'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input', type=Path)
    ap.add_argument('--svg', type=Path, required=True)
    ap.add_argument('--png', type=Path)
    args=ap.parse_args()
    data=json.loads(args.input.read_text())
    svg=render_svg(data)
    args.svg.parent.mkdir(parents=True,exist_ok=True)
    args.svg.write_text(svg,encoding='utf-8')
    if args.png and __import__('os').environ.get('EDGE_SKIP_PNG') != '1':
        try:
            import cairosvg
            args.png.parent.mkdir(parents=True,exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(),write_to=str(args.png),output_width=1200,output_height=675)
        except Exception as e:
            raise SystemExit(f'PNG render failed: {e}')
if __name__=='__main__': main()

