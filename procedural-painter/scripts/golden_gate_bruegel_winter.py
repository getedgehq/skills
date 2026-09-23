"""Golden Gate at blue hour in winter, Northern Renaissance detail (Bruegel-like).

Elevated viewpoint over a snowy Marin hillside: bare trees, hunters, a frozen pond with
skaters, a hamlet with lit windows; the bridge in the middle distance. Fine strokes,
then a rigger pass for the small narrative marks, varnish and craquelure.
"""
import sys, time
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pp.core import *
from pp.bridge import Bridge, render_bridge
from pp.strokes import Painter

SEED = 1565
W, H = 2400, 1800
rng = np.random.default_rng(SEED)
PREVIEW = '--under' in sys.argv

cam = Camera((-520, 210, -1050), 22, -5.0, 2800, W, H)
br = Bridge((0, 0, 0), 0)
hy = cam.horizon_y()
yy, xx = np.mgrid[0:H, 0:W].astype(float)
xs = np.arange(W)
labels = np.zeros((H, W), int)
SNOW, SNOW_SH = hexc('e4e6df'), hexc('a9b6b8')

# ---------- sky: Bruegel's cold green-grey, darkening upward at blue hour ----------
t = np.clip(yy / hy, 0, 1)
img = ramp(t, [(0, hexc('2f4648')), (0.5, hexc('58706c')), (0.85, hexc('93a49a')), (1, hexc('c9c3a8'))])
img = img * (0.96 + 0.08 * fbm(H, W, 3, rng, 4)[..., None])

# ---------- far snowy hills (city side) ----------
far = hy + 20 - 150 * fbm1d(W, 2, rng) - 60 * np.exp(-((xs - W * 0.75) / 400) ** 2)
fm = below_curve(H, W, far)
fsn = ramp(np.clip((yy - far[None, :]) / 120, 0, 1), [(0, hexc('c8d0cb')), (1, hexc('9aa8a6'))])
img = composite(img, fsn, fm)
labels[fm > 0.5] = 1
far_bot = np.maximum(far + 40, hy + 45 + 25 * fbm1d(W, 5, rng))      # shoreline

# ---------- bay: dark green water, lighter ice along the shore ----------
wm = below_curve(H, W, far_bot)
tw = np.clip((yy - far_bot[None, :]) / 700, 0, 1)
water = ramp(tw, [(0, hexc('6f8580')), (0.2, hexc('3d5652')), (1, hexc('2c403e'))])
img = composite(img, water, wm)
labels[wm > 0.5] = 2

# ---------- bridge ----------
brgb, ba, info = render_bridge(cam, br, W, H,
                               {'tower': hexc('9a4030'), 'pier': hexc('8e8f86'), 'deck': hexc('7a3528'), 'cable': hexc('8a3a2c')},
                               (0.6, 0.6, -0.4), flood=0.3, flood_col=hexc('e8a060'), sky_amb=hexc('607a74'))
img = composite(img, brgb, ba)
labels[ba > 0.5] = 3

# ---------- near shore lowland (hamlet + frozen pond), lower right ----------
low = H * 0.70 - 40 * fbm1d(W, 4, rng) + np.clip((W * 0.45 - xs) / (W * 0.45), 0, 1) * 200 - np.clip((xs - W * 0.78) / (W * 0.22), 0, 1) ** 0.8 * 190
lm = below_curve(H, W, low)
img = composite(img, ramp(np.clip((yy - low[None, :]) / 400, 0, 1), [(0, SNOW), (1, hexc('c9d0cb'))]), lm)
labels[lm > 0.5] = 4
r = Raster(W, H, 2)
pond = r.mask(lambda d, s: d.ellipse((W * 0.54 * s, H * 0.815 * s, W * 0.84 * s, H * 0.905 * s), fill=255))
img = composite(img, hexc('8ea09a'), pond)
labels[pond > 0.5] = 5

# ---------- foreground hill: snow slope descending from the left ----------
hill = H * 0.47 + (xs / W) * H * 0.44 + 30 * fbm1d(W, 6, rng)
hill = hill + np.clip((xs - W * 0.42) / (W * 0.14), 0, 1) ** 2 * 700
hm = below_curve(H, W, hill)
shade = np.clip((yy - hill[None, :]) / 500, 0, 1)
hc = ramp(shade + (fbm(H, W, 8, rng, 4)[...] - 0.5) * 0.3, [(0, SNOW), (0.6, hexc('d2d6cf')), (1, SNOW_SH)])
img = composite(img, hc, hm)
labels[hm > 0.5] = 6

lxy, lz = info['lamps']
vis = [(x, y) for (x, y), z in zip(lxy, lz) if z > 0 and 0 <= x < W and 0 <= y < H and labels[int(y), int(x)] in (0, 1, 2, 3)]
lights = np.clip(glow(H, W, [(x, y, 0.7) for x, y in vis], 2.5), 0, 1)
img = img + lights[..., None] * (hexc('ffd08a') - img)
img = np.clip(img, 0, 1)

if PREVIEW:
    save(img, 'out/p4_under.png'); sys.exit()

# ---------- paint: fine, restrained strokes ----------
ang = (fbm(H, W, 3, rng, 3) - 0.5) * 0.8
vx, vy = np.cos(ang), np.sin(ang) * 0.4
slope = np.arctan2(H * 0.44, W)
m6 = labels == 6
vx[m6], vy[m6] = np.cos(slope), np.sin(slope)
nn = np.hypot(vx, vy); vx, vy = vx / nn, vy / nn
t0 = time.time()
P = Painter(img, labels, (vx, vy), rng, ground=hexc('8a7a5a'))
c = dict(sat=1.0, jitter=(0.008, 0.06, 0.035), curv=0.35, edge_w=4.0, max_r=np.array([14, 8, 12, 2.5, 10, 8, 14]))
P.layer(12, first=True, maxlen=6, minlen=2, thresh=0, **c)
P.layer(7, maxlen=6, minlen=2, thresh=0.025, **c)
P.layer(4, maxlen=5, minlen=2, thresh=0.03, **c)
P.layer(2.2, maxlen=4, minlen=1, thresh=0.04, **c)

# ---------- rigger pass: the narrative detail ----------
DARK, BARK = hexc('2a2622'), hexc('3b3128')

def tree(x, y, hgt, ang=-np.pi / 2, depth=0, w=None):
    """recursive bare tree, drawn with the thin brush."""
    w = w or max(1.5, hgt * 0.07)
    x2, y2 = x + np.cos(ang) * hgt, y + np.sin(ang) * hgt
    P.line([(x, y), ((x + x2) / 2 + rng.normal(0, hgt * 0.05), (y + y2) / 2), (x2, y2)], w, BARK, 0.9)
    if depth < 6 and hgt > 5:
        for da in (rng.uniform(-0.7, -0.25), rng.uniform(0.25, 0.7), rng.uniform(-0.15, 0.15)):
            if rng.random() < 0.85:
                tree(x2, y2, hgt * rng.uniform(0.6, 0.75), ang + da, depth + 1, w * 0.65)

COATS = [hexc('2a2622'), hexc('4a3526'), hexc('5b2a22'), hexc('2f3a3a')]
def person(x, y, s, col=None, spear=False, skate=False, bend=0.0):
    col = col if col is not None else COATS[rng.integers(0, len(COATS))]
    hx = x + s * bend                                                          # hunched forward
    for k in range(6):                                                         # coat: widening downward
        f = k / 5
        P.line([(x + (hx - x) * (1 - f) - s * (0.10 + 0.12 * f), y - s * (0.62 - 0.44 * f)),
                (x + (hx - x) * (1 - f) + s * (0.10 + 0.12 * f), y - s * (0.62 - 0.44 * f))], s * 0.11, col, 1)
    P.dab(hx, y - s * 0.72, s * 0.09, hexc('b58a6a'), 1)                        # face
    P.line([(hx - s * 0.1, y - s * 0.8), (hx + s * 0.1, y - s * 0.8)], s * 0.08, DARK, 1)   # cap
    lean = 0.3 if skate else 0.1
    P.line([(x - s * 0.06, y - s * 0.18), (x - s * lean, y)], s * 0.07, DARK, 1)
    P.line([(x + s * 0.06, y - s * 0.18), (x + s * lean, y)], s * 0.07, DARK, 1)
    if spear:
        P.line([(hx - s * 0.1, y - s * 0.15), (hx + s * 0.35, y - s * 1.25)], 2, BARK, 1)
        P.line([(hx + s * 0.1, y - s * 0.6), (hx + s * 0.28, y - s * 0.35)], s * 0.12, hexc('6a5a44'), 1)  # game bag

def dog(x, y, s):
    P.line([(x, y - s * 0.42), (x + s * 0.35, y - s * 0.38), (x + s * 0.7, y - s * 0.44)], s * 0.2, DARK, 1)   # arched body
    P.line([(x + s * 0.7, y - s * 0.44), (x + s * 0.88, y - s * 0.62)], s * 0.12, DARK, 1)                    # neck/head down-sloped
    P.line([(x - s * 0.02, y - s * 0.45), (x - s * 0.2, y - s * 0.62)], 1.5, DARK, 1)                         # tail
    for lx, d in ((0.05, -0.08), (0.15, 0.06), (0.6, -0.05), (0.68, 0.08)):
        P.line([(x + s * lx, y - s * 0.36), (x + s * (lx + d), y)], 1.8, DARK, 1)

def house(x, y, w_, h_):
    P.line([(x, y - h_ / 2), (x + w_, y - h_ / 2)], h_, hexc('6e5a45'), 0.9)
    roof = [(x - 4, y - h_), (x + w_ / 2, y - h_ - w_ * 0.45), (x + w_ + 4, y - h_)]
    for k in range(int(w_ * 0.45)):
        f = k / (w_ * 0.45)
        P.line([(roof[0][0] + (roof[1][0] - roof[0][0]) * f, roof[0][1] + (roof[1][1] - roof[0][1]) * f),
                (roof[2][0] + (roof[1][0] - roof[2][0]) * f, roof[2][1] + (roof[1][1] - roof[2][1]) * f)], 2, hexc('f2f2ec'), 1)
    P.line([roof[0], roof[1], roof[2]], 2, hexc('4a3a2c'), 1)
    P.line([(x - 4, y - h_ + 2), (x + w_ + 4, y - h_ + 2)], 3, hexc('3a2e24'), 1)
    for k in range(rng.integers(1, 3)):
        wx = x + w_ * rng.uniform(0.2, 0.8)
        P.dab(wx, y - h_ * 0.5, max(2, h_ * 0.12), hexc('ffc86a'), 1)
    sx0 = x + w_ * 0.75                                                    # chimney smoke
    pts = [(sx0 + np.sin(k * 0.5) * 4 + k * 1.5, y - h_ - w_ * 0.3 - k * 6) for k in range(10)]
    P.line(pts, 3, hexc('b8bcb4'), 0.5)

# trees along the ridge of the hill
for k in range(9):
    x = W * (0.03 + 0.055 * k) + rng.normal(0, 15)
    y = float(hill[int(np.clip(x, 0, W - 1))]) + 20 + rng.uniform(0, 60)
    tree(x, y, rng.uniform(110, 190) * (1.1 - k * 0.04))
# long blue tree shadows and footprint tracks on the snow
for k in range(9):
    x = W * (0.03 + 0.055 * k)
    y = float(hill[int(np.clip(x, 0, W - 1))]) + 40
    pts = [(x + 200 * f, y + 115 * f) for f in np.linspace(0, 1, 8)]
    pts = [(px, py) for px, py in pts if py > hill[int(min(px, W - 1))] + 12]
    if len(pts) > 1:
        P.line(pts, 6, hexc('c4cccb'), 0.55)
for j in range(70):
    f = j / 70
    x = W * (0.10 + 0.25 * f) + rng.normal(0, 3); y = float(hill[int(x)]) + 150 + 60 * f + rng.normal(0, 3)
    P.dab(x, y, 2.4, hexc('9aa6a6'), 0.5)
# a wattle fence running down the slope
fx0 = W * 0.02
for j in range(26):
    x = fx0 + j * 34; y = float(hill[int(x)]) + 300 + j * 8
    P.line([(x, y), (x, y - 38)], 4, BARK, 1)
    if j:
        P.line([(x - 34, y - 8 - 22), (x, y - 22)], 3, hexc('5a4838'), 1)
# dry tufts poking through snow
for j in range(160):
    x = W * rng.uniform(0.0, 0.5); y0 = float(hill[int(x)])
    y = y0 + rng.uniform(30, H - y0)
    if y < H - 5:
        for q in range(3):
            P.line([(x, y), (x + rng.normal(0, 4), y - rng.uniform(6, 14))], 1.4, hexc('6a5a44'), 0.6)
# hunters and dogs trudging down the slope
for k, fx in enumerate((0.16, 0.2, 0.245)):
    x = W * fx; y = float(hill[int(x)]) + 120
    person(x, y, 95, spear=True, bend=0.12)
for fx in (0.13, 0.18, 0.225, 0.27, 0.3):
    x = W * fx; y = float(hill[int(x)]) + 150 + rng.uniform(-10, 10)
    dog(x, y, 44)
# hamlet on the lowland
for k in range(14):
    x = W * rng.uniform(0.50, 0.97); y = float(low[int(x)]) + rng.uniform(40, 150)
    if pond[int(min(y, H - 1)), int(x)] > 0.3:
        continue
    house(x, y, rng.uniform(45, 80), rng.uniform(26, 40))
for k in range(6):
    x = W * rng.uniform(0.5, 0.97); y = float(low[int(x)]) + rng.uniform(10, 60)
    tree(x, y, rng.uniform(40, 70))
# skaters on the pond
for k in range(40):
    x = W * rng.uniform(0.58, 0.9); y = H * rng.uniform(0.815, 0.9)
    if pond[int(y), int(x)] > 0.7:
        person(x, y, rng.uniform(18, 26), skate=rng.random() < 0.6)
# lamps and beacons
for x, y in vis:
    P.dab(x, y, 2.2, hexc('ffe0a0'), 1)
for (x, y) in info['beacons'][0]:
    P.dab(x, y, 3, hexc('ff4030'), 1)
# a few crows
for k in range(6):
    x, y = W * rng.uniform(0.3, 0.7), H * rng.uniform(0.08, 0.25)
    P.line([(x - 9, y - 3), (x, y), (x + 9, y - 4)], 2.2, DARK, 1)

out = P.finish(impasto=0.18, bristle=0.35, light=(-0.6, -0.8), lic_steps=4)

# ---------- varnish + craquelure ----------
out = out * np.array([1.02, 0.99, 0.9])[None, None] + 0.015
seeds = np.ones((H // 2, W // 2), bool)
for _ in range(2600):
    seeds[rng.integers(0, H // 2), rng.integers(0, W // 2)] = False
_, idx = ndi.distance_transform_edt(seeds, return_indices=True)
lab = idx[0] * W + idx[1]
crack = (np.diff(lab, axis=0, prepend=lab[:1]) != 0) | (np.diff(lab, axis=1, prepend=lab[:, :1]) != 0)
crack = ndi.zoom(crack.astype(float), 2, order=1)[:H, :W]
crack *= fbm(H, W, 6, rng, 3) > 0.5
out = out * (1 - 0.06 * crack[..., None])
out = out * (0.93 + 0.07 * (1 - ((xx / W - 0.5) ** 2 + (yy / H - 0.5) ** 2) * 1.6))[..., None]
save(np.clip(out, 0, 1), 'out/p4_bruegel_winter.png')
print('strokes', P.n_strokes, 'secs', round(time.time() - t0, 1), 'seed', SEED)
