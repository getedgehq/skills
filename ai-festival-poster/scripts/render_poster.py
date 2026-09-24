#!/usr/bin/env python3
"""Paint a desert-at-dusk festival lineup poster from usage.json (scan_usage.py) with brush strokes.
Every act and its billing comes from real counts. No image model, no reference images.

Usage: python3 render_poster.py --usage usage.json --presenter "ADA LOVELACE" [--dates "JAN 2025 TO SEP 2026"]
       [--title "AI FEST"] [--out out/] [--under]   (fonts: run get_fonts.py once)"""
import argparse, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pp.core import fbm, fbm1d, hexc as hx, ramp, Raster, composite, below_curve, glow
from pp.strokes import Painter

S = 2
W, H = 1080 * S, 1350 * S
rng = np.random.default_rng(2026)
yy, xx = np.mgrid[0:H, 0:W].astype(float)
xs = np.arange(W)
ap = argparse.ArgumentParser()
ap.add_argument("--usage", default="usage.json"); ap.add_argument("--presenter", default="")
ap.add_argument("--title", default="AI FEST"); ap.add_argument("--dates", default="")
ap.add_argument("--out", default="out"); ap.add_argument("--under", action="store_true"); ap.add_argument("--fonts", default=os.path.join(HERE, "fonts"))
A = ap.parse_args()
PREVIEW = A.under
os.makedirs(A.out, exist_ok=True)

# ---------------- underpainting ----------------
HOR = 1125 * S
t = np.clip(yy / HOR, 0, 1)
img = ramp(t, [(0, hx("1A0F33")), (0.35, hx("2E1850")), (0.58, hx("5A2561")), (0.74, hx("A43C58")), (0.86, hx("E0663F")), (0.95, hx("F59A4A")), (1, hx("FBC46A"))])
# big low sun, half behind the mountains
SX, SY, SR = W * 0.34, HOR - 20 * S, 150 * S
dsun = np.hypot(xx - SX, yy - SY)
img = img + (np.exp(-((dsun - SR) / (220 * S)).clip(0) ** 2) * 0.30)[..., None] * (hx("FFB860") - img)
img = composite(img, ramp(np.clip((yy - (SY - SR)) / (2 * SR), 0, 1), [(0, hx("FFE3A0")), (1, hx("FF9A4A"))]), np.clip(SR - dsun + 1, 0, 1))
# thin horizontal cloud streaks lit from below
cl = fbm(H, W, 3, rng, 5)
streak = np.clip((np.sin(yy / (18 * S) + cl * 6) - 0.7) * 3, 0, 1) * np.clip((yy - 520 * S) / (300 * S), 0, 1) * np.clip((HOR - 60 * S - yy) / (200 * S), 0, 1)
img = img + streak[..., None] * (hx("FF9E7A") - img) * 0.35
labels = np.zeros((H, W), int)

def ridge(base, amp, cells, seed):
    r = np.random.default_rng(seed)
    return base - amp * fbm1d(W, cells, r, 5, 0.5)

for base, amp, cells, col, lab, seed in [(HOR + 15 * S, 170 * S, 2, "5B2A4E", 1, 11), (HOR + 55 * S, 110 * S, 3, "3A1B3A", 2, 12)]:
    r = ridge(base, amp, cells, seed)
    m = below_curve(H, W, r)
    shade = np.clip((yy - r[None, :]) / (160 * S), 0, 1)
    img = composite(img, ramp(shade, [(0, hx(col)), (1, hx("1F0F22"))]), m)
    labels[m > 0.5] = lab

# ground / festival field
gnd = HOR + 95 * S
gm = (yy > gnd).astype(float)
img = composite(img, ramp(np.clip((yy - gnd) / (250 * S), 0, 1), [(0, hx("2A1426")), (1, hx("140A14"))]), gm)
labels[gm > 0.5] = 3

r = Raster(W, H, 2)
# Ferris wheel on the right, with a warm glow ring
FX, FY, FR = W * 0.78, gnd - 140 * S, 118 * S
def wheel(dr, s):
    dr.ellipse(((FX - FR) * s, (FY - FR) * s, (FX + FR) * s, (FY + FR) * s), outline=255, width=int(7 * S * s))
    dr.ellipse(((FX - FR * .82) * s, (FY - FR * .82) * s, (FX + FR * .82) * s, (FY + FR * .82) * s), outline=255, width=int(3 * S * s))
    for k in range(16):
        a = k * math.pi / 8
        dr.line((FX * s, FY * s, (FX + math.cos(a) * FR) * s, (FY + math.sin(a) * FR) * s), fill=255, width=int(2.5 * S * s))
    for k in range(16):
        a = k * math.pi / 8 + 0.2
        gx, gy = FX + math.cos(a) * FR, FY + math.sin(a) * FR
        dr.rounded_rectangle(((gx - 9 * S) * s, (gy - 4 * S) * s, (gx + 9 * S) * s, (gy + 16 * S) * s), radius=4 * S * s, fill=255)
    dr.polygon([((FX - 12 * S) * s, FY * s), ((FX + 12 * S) * s, FY * s), ((FX + 95 * S) * s, gnd * s), ((FX - 95 * S) * s, gnd * s)], outline=255, width=int(6 * S * s))
    dr.line(((FX - 95 * S) * s, gnd * s, FX * s, FY * s), fill=255, width=int(6 * S * s))
    dr.line(((FX + 95 * S) * s, gnd * s, FX * s, FY * s), fill=255, width=int(6 * S * s))
wm = r.mask(wheel)
img = composite(img, hx("1B0E1E"), wm)
labels[wm > 0.5] = 4
# glowing gondola lights around the rim
lights = []
for k in range(48):
    a = k * math.pi / 24
    lights.append((FX + math.cos(a) * FR, FY + math.sin(a) * FR, 1.0))
# festival tents (big-top shapes) along the field, and a stage
def tents(dr, s):
    for cx, w_, h_ in [(W * 0.12, 150, 95), (W * 0.30, 110, 70), (W * 0.52, 190, 120), (W * 0.93, 120, 80)]:
        w_, h_ = w_ * S, h_ * S
        base = gnd + 6 * S
        dr.polygon([((cx - w_) * s, base * s), ((cx - w_ * .15) * s, (base - h_) * s), (cx * s, (base - h_ - 22 * S) * s), ((cx + w_ * .15) * s, (base - h_) * s), ((cx + w_) * s, base * s)], fill=255)
tm = r.mask(tents)
img = composite(img, hx("241021"), tm)
labels[tm > 0.5] = 5
# palm rows: many small palms on the horizon + two big ones framing
def palms(dr, s, specs):
    for x0, y0, h_, lean in specs:
        pts = [(x0 + lean * (i / 20) ** 1.7 * h_ * .15, y0 - h_ * i / 20) for i in range(21)]
        for i in range(20):
            dr.line([(pts[i][0] * s, pts[i][1] * s), (pts[i + 1][0] * s, pts[i + 1][1] * s)], fill=255, width=max(1, int(h_ / 45 * (1 - .4 * i / 20) * s)))
        tx, ty = pts[-1]
        for a in np.linspace(-3.0, -0.14, 10):
            L = h_ * .36; poly_u, poly_l = [], []
            for u in np.linspace(0, 1, 14):
                cx_ = tx + math.cos(a) * L * u; cy_ = ty + math.sin(a) * L * u * (1 - .3 * u) + L * .7 * u ** 2.1
                wd = (1 - u) * h_ / 34 * math.sin(math.pi * min(1, u * 1.5 + .12))
                nx, ny = -math.sin(a), math.cos(a)
                poly_u.append(((cx_ + nx * wd) * s, (cy_ + ny * wd) * s)); poly_l.append(((cx_ - nx * wd * .4) * s, (cy_ - ny * wd * .4) * s))
            dr.polygon(poly_u + poly_l[::-1], fill=255)
row = [(x, gnd + rng.uniform(-4, 6) * S, rng.uniform(70, 120) * S, rng.choice([-1, 1])) for x in np.linspace(W * 0.02, W * 0.98, 16) if abs(x - FX) > FR * 0.9]
pm = r.mask(lambda dr, s: palms(dr, s, row))
img = composite(img, hx("150A16"), pm)
labels[pm > 0.5] = 6
big = r.mask(lambda dr, s: palms(dr, s, [(W * 0.05, H + 20 * S, 380 * S, 1), (W * 0.97, H + 20 * S, 330 * S, -1)]))
img = composite(img, hx("0E070F"), big)
labels[big > 0.5] = 7
# field lights (crowd + stages), warm and violet
for _ in range(420):
    x, y = rng.uniform(0, W), gnd + abs(rng.normal(0, 60)) * S + 8 * S
    if y < H: lights.append((x, y, rng.uniform(0.15, 0.6)))
L = np.clip(glow(H, W, lights, 3.0 * S) * 1.4, 0, 1)
img = img + L[..., None] * (hx("FFD38A") - img)
stars = [(rng.uniform(0, W), rng.uniform(0, H * 0.4), rng.uniform(0.2, 0.7)) for _ in range(160)]
img = img + np.clip(glow(H, W, stars, 1.2 * S), 0, 1)[..., None] * (hx("FFF4E0") - img)
img = np.clip(img, 0, 1)
labels[(yy < HOR) & (labels == 0)] = 0

if PREVIEW:
    Image.fromarray((img * 255).astype(np.uint8)).resize((540, 675)).save(os.path.join(A.out, "underpainting.png")); sys.exit()

# ---------------- paint: gouache-like strokes (horizontal in sky, contour on land) ----------------
ang = (fbm(H, W, 2.5, rng, 3) - 0.5) * 0.5
vx, vy = np.cos(ang), np.sin(ang) * 0.3
nn = np.hypot(vx, vy); vx, vy = vx / nn, vy / nn
P = Painter(img, labels, (vx, vy), rng, ground=hx("2A1A3A"))
max_r = np.array([22, 16, 16, 12, 3, 5, 3, 6])
c = dict(sat=1.12, jitter=(0.012, 0.07, 0.05), max_r=max_r, curv=0.35, edge_w=3.0)
P.layer(20 * S / 2, first=True, maxlen=6, minlen=2, thresh=0, **c)
P.layer(11 * S / 2, maxlen=6, minlen=2, thresh=0.03, **c)
P.layer(6 * S / 2, maxlen=5, minlen=2, thresh=0.035, **c)
P.layer(3 * S / 2, maxlen=4, minlen=1, thresh=0.05, **c)
for x, y, a in lights[:48]:
    P.dab(x, y, 3.5 * S, hx("FFE7A8"), 1.0)
bg = P.finish(impasto=0.28, bristle=0.4, light=(-0.5, -0.85), lic_steps=5)

# darken the upper two thirds a touch so the bill reads
dk = np.clip(1 - (yy - 0) / (1080 * S), 0, 1) ** 0.9 * 0.30
bg = bg * (1 - dk[..., None])
poster = Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8))
d = ImageDraw.Draw(poster)

# ---------------- billing ----------------
FONT = lambda n: os.path.join(A.fonts, n)
def anton(sz): return ImageFont.truetype(FONT("Anton-Regular.ttf"), int(sz * S))
def archivo(sz, w="Bold"):
    f = ImageFont.truetype(FONT("ArchivoNarrow[wght].ttf"), int(sz * S)); f.set_variation_by_name(w); return f
def inter(sz, w="SemiBold"):
    f = ImageFont.truetype(FONT("Inter[opsz,wght].ttf"), int(sz * S))
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
CREAM, ACC = hx("F7F2E9"), hx("FFB35C")
C8 = lambda c: tuple(int(v * 255) for v in c)
M = 64 * S; MAXW = W - 2 * M

def tracked(y, text, font, fill, tr):
    ws = [d.textlength(ch, font=font) for ch in text]; tot = sum(ws) + tr * S * (len(text) - 1); x = (W - tot) / 2
    for ch, w in zip(text, ws): d.text((x, y), ch, font=font, fill=fill); x += w + tr * S
    return tot

def fill_line(y, text, maker, max_sz, fill):
    sz = max_sz
    while d.textlength(text, font=maker(sz)) > MAXW and sz > 8: sz -= 0.5
    f = maker(sz); w = d.textlength(text, font=f)
    top = d.textbbox((0, 0), text, font=f)[1]
    d.text(((W - w) / 2, y - top), text, font=f, fill=fill)
    bb = d.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]

rows = [r for r in json.load(open(A.usage)) if r.get("verified")]
DAYS = [("FRIDAY", "BUILD"), ("SATURDAY", "THINK"), ("SUNDAY", "CREATE")]

if A.presenter: tracked(40 * S, f"{A.presenter.upper()} PRESENTS", inter(13), C8(CREAM), 6)
fill_line(64 * S, A.title.upper(), lambda s: anton(s), 150, C8(CREAM))
tracked(218 * S, (A.dates.upper() + "  ·  " if A.dates else "") + "EVERY ACT BOOKED BY REAL USAGE", inter(11.5), C8(ACC), 4)

y = 256 * S
for day, cat in DAYS:
    acts = [a["name"].upper() for a in sorted([r for r in rows if r["day"] == cat], key=lambda r: -r["sessions"])]
    if not acts:
        continue
    lab = f"{day}  ·  {cat}"
    f = archivo(17, "Bold"); w = d.textlength(lab, font=f) + 8 * S * len(lab) * 0.3
    tw = tracked(y + 5 * S, lab, f, C8(ACC), 5)
    d.rectangle(((W - tw) / 2 - 14 * S, y, (W + tw) / 2 + 14 * S, y + 30 * S), outline=C8(ACC), width=int(1.5 * S))
    y += 42 * S
    y += fill_line(y, acts[0], anton, 80, C8(CREAM)) + 10 * S
    rest = acts[1:]
    tiers = [(rest[:3], 40, "Bold"), (rest[3:7], 28, "Bold"), (rest[7:13], 21, "SemiBold"), (rest[13:], 17, "SemiBold")]
    for names, mx, wt in tiers:
        if not names: continue
        y += fill_line(y, "  ·  ".join(names), lambda s, wt=wt: archivo(s, wt), mx, C8(CREAM)) + 8 * S
    y += 16 * S
tracked(H - 40 * S, "2026  ·  PAINTED IN PYTHON  ·  NO IMAGE MODEL", inter(11), C8(CREAM), 4)

arr = np.asarray(poster).astype(np.float32) + rng.normal(0, 4.0, (H, W, 1)).astype(np.float32)
poster = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
poster.save(os.path.join(A.out, "poster-2160x2700.png"))
poster.resize((1080, 1350), Image.LANCZOS).save(os.path.join(A.out, "poster-1080x1350.png"))
print("lineup bottom", y / S)
