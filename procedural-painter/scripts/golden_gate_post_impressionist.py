"""Golden Gate at blue hour, post-impressionist swirling brushwork.

Every pixel is computed here: a 3D bridge model + procedural landscape form the
underpainting, then curved brush strokes follow a vortex flow field.
"""
import sys, time
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pp.core import *
from pp.bridge import Bridge, render_bridge, DECK_Y
from pp.strokes import Painter

SEED = 1889
W, H = 2400, 1800
rng = np.random.default_rng(SEED)
PREVIEW = '--under' in sys.argv

cam = Camera((-330, 55, -760), 17, 5.6, 3200, W, H)
br = Bridge((0, 0, 0), 0)
hy = cam.horizon_y()
yy, xx = np.mgrid[0:H, 0:W].astype(float)

# ---------------- sky ----------------
t = np.clip(yy / hy, 0, 1)
sky = ramp(t, [(0, hexc('0a1640')), (0.35, hexc('17307a')), (0.7, hexc('2d5fa8')), (0.9, hexc('4f8fc0')), (1.0, hexc('9cc6c9'))])
# afterglow low on the right (west)
glow_w = np.exp(-((xx - W * 0.92) / (W * 0.35)) ** 2) * np.exp(-((hy - yy) / (H * 0.12)).clip(0) ** 1.2)
sky = sky + glow_w[..., None] * (hexc('f2a65a') - sky) * 0.85
# swirling cloud ribbons: noise banded along the vortex field later; here luminous streaks
n = fbm(H, W, 3, rng, 5)
band = np.sin((yy / H * 5 + n * 2.2) * np.pi) * 0.5 + 0.5
sky = sky + (ndi.gaussian_filter(band ** 3, 25) * np.clip((hy - 80 - yy) / 200, 0, 1))[..., None] * (hexc('5d92cc') - sky) * 0.45

# moon (crescent with halo) + stars
MX, MY, MR = W * 0.17, H * 0.16, 62
d = np.hypot(xx - MX, yy - MY)
halo = np.exp(-((d - MR) / 120).clip(0) ** 2) * (d > MR)
ring = np.exp(-((d - MR * 2.2) / 26) ** 2) * 0.45
sky = sky + (halo * 0.55 + ring)[..., None] * (hexc('e8d86a') - sky)
moon = np.clip(MR - d + 0.5, 0, 1) * np.clip(np.hypot(xx - MX + 30, yy - MY + 18) - MR * 0.95, 0, 1)
stars = []
for _ in range(9):
    sx_, sy_ = rng.uniform(0.30, 0.97) * W, rng.uniform(0.05, 0.50) * H
    if np.hypot(sx_ - MX, sy_ - MY) < 300:
        continue
    stars.append((sx_, sy_, rng.uniform(14, 30)))
star_core = np.zeros((H, W)); star_halo = np.zeros((H, W))
for sx_, sy_, r in stars:
    dd = np.hypot(xx - sx_, yy - sy_)
    star_core = np.maximum(star_core, np.clip(r * 0.45 - dd, 0, 1))
    star_halo = np.maximum(star_halo, np.exp(-(dd / (r * 2.6)) ** 2) * 0.8 + np.exp(-((dd - r * 1.9) / 7) ** 2) * 0.35)
sky = sky + star_halo[..., None] * (hexc('dfe8a8') - sky)
# swirl bands: LIC of coarse noise along the vortex field -> light/dark ribbons that the strokes pick up
from pp.strokes import lic
def vortex_field():
    ang = (fbm(H, W, 2.5, np.random.default_rng(SEED + 1), 3) - 0.5) * 1.6
    fx, fy = np.cos(ang), np.sin(ang) * 0.6
    for (cx_, cy_, rad, st) in VORT:
        dx_, dy_ = xx - cx_, yy - cy_
        dd = np.hypot(dx_, dy_) + 1e-6
        fall = np.exp(-(dd / rad) ** 2) * st
        fx = fx - dy_ / dd * fall; fy = fy + dx_ / dd * fall
    nn = np.hypot(fx, fy) + 1e-9
    return fx / nn, fy / nn
VORT = [(W * 0.47, H * 0.24, 330, 2.6), (W * 0.74, H * 0.14, 230, -2.0), (W * 0.30, H * 0.38, 190, 1.6), (MX, MY, 260, 1.8)]
svx, svy = vortex_field()
cn = ndi.zoom(rng.random((H // 24 + 2, W // 24 + 2)), 24, order=1)[:H, :W].astype(np.float32)
bands = lic(cn, svx.astype(np.float32), svy.astype(np.float32), steps=40, h=4.0)
bands = (bands - bands.mean()) / (bands.std() + 1e-9)
skyw = np.clip((hy - 40 - yy) / 150, 0, 1)[..., None]
sky = sky + skyw * np.clip(bands, 0, 3)[..., None] * 0.22 * (hexc('8fc0e8') - sky) + skyw * np.clip(-bands, 0, 3)[..., None] * 0.18 * (hexc('0a1440') - sky)
sky = np.clip(sky, 0, 1)
img = sky.copy()
labels = np.zeros((H, W), int)                        # 0 sky

# ---------------- far shore (city side) ----------------
xs = np.arange(W)
far = hy - 30 - 70 * fbm1d(W, 3, rng) - 60 * np.exp(-((xs - W * 0.12) / (W * 0.15)) ** 2)
far = np.where(xs > W * 0.6, hy - (hy - far) * np.clip(1 - (xs - W * 0.6) / (W * 0.25), 0, 1), far)
fm = below_curve(H, W, far) * (yy < hy + 6)
far_col = ramp(np.clip((yy - far[None, :]) / 90, 0, 1), [(0, hexc('34426e')), (1, hexc('1c2447'))])
img = img * (1 - fm[..., None]) + far_col * fm[..., None]
labels[fm > 0.5] = 1
# city lights on the far shore
city = []
for _ in range(900):
    x = rng.uniform(0, W * 0.62)
    top = far[int(x)]
    if top > hy - 4:
        continue
    y = rng.uniform(top + 8, hy - 2)
    city.append((x, y, rng.uniform(0.4, 1.0)))

# ---------------- water ----------------
wm = (yy >= hy).astype(float)
tw = np.clip((yy - hy) / (H - hy), 0, 1)
water = ramp(tw, [(0, hexc('4a79a8')), (0.15, hexc('20407c')), (1, hexc('0b173f'))])
wn = fbm(H, W, 4, rng, 4)
ripple = np.sin(yy * 0.35 + wn * 18) * 0.5 + 0.5
water = water * (0.85 + 0.3 * ripple[..., None])
water = water + (glow_w * 0.8)[..., None] * (hexc('d88a55') - water) * (yy > hy)[..., None] * np.exp(-(yy - hy) / 160)[..., None]
img = img * (1 - wm[..., None] * (labels == 0)[..., None]) + water * (wm * (labels == 0))[..., None]
labels[(wm > 0.5) & (labels == 0)] = 2

# ---------------- bridge ----------------
brgb, ba, info = render_bridge(cam, br, W, H,
                               {'tower': hexc('c2452c'), 'pier': hexc('5a6275'), 'deck': hexc('9a3524'), 'cable': hexc('d0553a')},
                               (0.5, 0.7, -0.5), flood=0.55, flood_col=hexc('ffb060'), sky_amb=hexc('2a4a90'))
img = composite(img, brgb, ba)
labels[ba > 0.5] = 3

# ---------------- near hills + cypress ----------------
hl = H * 0.93 - 60 * fbm1d(W, 3, rng)
hl = hl + np.clip((W * 0.34 - xs) / (W * 0.34), 0, 1) ** 1.6 * -330      # headland rising to the left
hr = H * 0.97 - np.clip((xs - W * 0.74) / (W * 0.26), 0, 1) ** 0.8 * 560 - 25 * fbm1d(W, 6, rng)
near = np.minimum(hl, hr)
nm = below_curve(H, W, near)
hn = fbm(H, W, 6, rng, 5)
near_col = ramp(np.clip((yy - near[None, :]) / 380 + (hn - 0.5) * 0.5, 0, 1),
                [(0, hexc('3f6a5a')), (0.35, hexc('27493f')), (1, hexc('142a2a'))])
# warm path of light across the grass
near_col = near_col + (np.exp(-((xx - W * 0.2) / 260) ** 2) * 0.25)[..., None] * (hexc('b99a4a') - near_col)
img = composite(img, near_col, nm)
labels[nm > 0.5] = 4

# cypress: flame-shaped silhouette rising from the left hill
cx0, cyb, ch = W * 0.11, H + 10, H * 1.0
cy = np.linspace(0, 1, 400)
lobes = 0.75 + 0.35 * np.abs(np.sin(cy * np.pi * 6.5 + 0.7)) + 0.15 * (fbm1d(400, 8, rng) - 0.5)
half = 165 * (1 - cy) ** 0.75 * lobes + 5
wob = 40 * np.sin(cy * 5 + 0.4) * cy + 60 * cy ** 2
left = [(cx0 - half[i] + wob[i] - 25 * cy[i], cyb - cy[i] * ch) for i in range(400)]
right = [(cx0 + half[i] * 0.9 + wob[i] - 25 * cy[i], cyb - cy[i] * ch) for i in range(399, -1, -1)]
r = Raster(W, H, 2)
cm = r.poly(left + right)
cyp_col = ramp(np.clip(fbm(H, W, 10, rng, 4) * 1.3 - 0.15, 0, 1), [(0, hexc('0e1e1e')), (0.6, hexc('1f3b30')), (1, hexc('3e5a38'))])
img = composite(img, cyp_col, cm)
labels[cm > 0.5] = 5

# ---------------- lights ----------------
lxy, lz = info['lamps']
vis = [(x, y, 1.0) for (x, y), z in zip(lxy, lz) if z > 0 and 0 <= x < W and 0 <= y < H and labels[int(y), int(x)] in (0, 2, 3)]
bxy, _ = info['beacons']
lights = np.clip(glow(H, W, vis, 3.5) * 0.9 + glow(H, W, city, 2.2) * 0.7, 0, 1.5)
img = img + lights[..., None] * (hexc('ffd27a') - img) * np.clip(lights, 0, 1)[..., None]
# reflections: vertical streaks in the water under lamps and city
refl_pts = []
for x, y, a in vis + city:
    ry = hy + (hy - y) * 0.9 if y < hy else y
    if hy < ry < H:
        refl_pts.append((x, ry + (ry - hy) * 0.2, a))
f = np.zeros((H, W))
for x, y, a in refl_pts:
    xi, yi = int(x), int(min(y, H - 1))
    f[yi, xi] += a
refl = ndi.gaussian_filter(f, (38, 2.0)) * 60
refl *= (labels == 2)
img = img + np.clip(refl, 0, 1)[..., None] * (hexc('f0b24f') - img) * 0.9
img = np.clip(img, 0, 1)

# moon + star cores on top (labels 6)
img = composite(img, hexc('f6eb8c'), moon)
img = composite(img, hexc('fbf6c8'), star_core)
labels[(moon > 0.5) | (star_core > 0.5)] = 6

if PREVIEW:
    save(img, 'out/p1_under.png')
    sys.exit()

# ---------------- flow field ----------------
vx = np.ones((H, W)); vy = np.zeros((H, W))
ang = (fbm(H, W, 2.5, rng, 3) - 0.5) * 1.6
vx, vy = np.cos(ang), np.sin(ang) * 0.6
# vortices in the sky
for (cx_, cy_, rad, s) in VORT:
    dx_, dy_ = xx - cx_, yy - cy_
    dd = np.hypot(dx_, dy_) + 1e-6
    fall = np.exp(-(dd / rad) ** 2) * s
    vx += -dy_ / dd * fall
    vy += dx_ / dd * fall
# around stars: tight circles
for sx_, sy_, rr in stars:
    dx_, dy_ = xx - sx_, yy - sy_
    dd = np.hypot(dx_, dy_) + 1e-6
    fall = np.exp(-(dd / (rr * 3.5)) ** 2) * 4
    vx += -dy_ / dd * fall; vy += dx_ / dd * fall
# water: horizontal; hills: follow slope; cypress: vertical flames
water_m = labels == 2
vx[water_m], vy[water_m] = 1.0, 0.08 * np.sin(xx[water_m] * 0.01)
hill_m = labels == 4
a2 = np.arctan2(np.gradient(near)[None, :].repeat(H, 0), 1)[hill_m] + (hn[hill_m] - 0.5) * 1.8
vx[hill_m], vy[hill_m] = np.cos(a2), np.sin(a2)
cyp_m = labels == 5
a3 = -np.pi / 2 + 0.55 * np.sin(yy[cyp_m] * 0.02 + xx[cyp_m] * 0.01)
vx[cyp_m], vy[cyp_m] = np.cos(a3), np.sin(a3)
nn = np.hypot(vx, vy) + 1e-9
vx, vy = ndi.gaussian_filter(vx / nn, 6), ndi.gaussian_filter(vy / nn, 6)
nn = np.hypot(vx, vy) + 1e-9
vx, vy = vx / nn, vy / nn

# ---------------- paint ----------------
t0 = time.time()
P = Painter(img, labels, (vx, vy), rng, ground=hexc('3a3a5a'))
min_r = np.array([9, 0, 5, 0, 9, 5, 0])
max_r = np.array([30, 16, 30, 3.5, 30, 14, 3])
common = dict(sat=1.3, jitter=(0.025, 0.15, 0.16), max_r=max_r, min_r=min_r, curv=0.45, edge_w=5.0)
P.layer(26, first=True, maxlen=9, minlen=4, thresh=0.0, **common)
P.layer(15, maxlen=10, minlen=4, thresh=0.04, **common)
P.layer(9, maxlen=10, minlen=4, thresh=0.04, **common)
P.layer(5.5, maxlen=7, minlen=2, thresh=0.06, **common)
P.layer(3.2, maxlen=6, minlen=1, thresh=0.07, **{**common, 'jitter': (0.01, 0.08, 0.06)})
P.layer(2.0, maxlen=5, minlen=1, thresh=0.09, **{**common, 'jitter': (0.01, 0.05, 0.05)})

# rigger pass: cables and lamps re-stated with a thin brush
for xy, wd in info['cables']:
    seg = [(x + rng.normal(0, 0.4), y + rng.normal(0, 0.4)) for x, y in xy[::2] if 0 <= x < W and 0 <= y < H]
    if len(seg) > 1:
        P.line(seg, max(2, float(np.median(wd)) * 1.1), hexc('e0663f'), 0.9)
for x, y, a in vis:
    P.dab(x, y, rng.uniform(2.5, 4.2), hexc('ffe39a'), 1.0)
for (x, y) in bxy:
    P.dab(x, y, 4, hexc('ff4a3a'), 1.0)

out = P.finish(impasto=0.55, bristle=0.9, light=(-0.55, -0.85), lic_steps=7)
# final palette pass: slight contrast + warm/cool split
L0 = lum(out)[..., None]
out = np.clip((out - 0.5) * 1.06 + 0.5, 0, 1)
save(out, 'out/p1_post_impressionist.png')
print('strokes', P.n_strokes, 'secs', round(time.time() - t0, 1), 'seed', SEED)
