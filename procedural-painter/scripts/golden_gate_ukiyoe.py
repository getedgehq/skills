"""Golden Gate at blue hour as a ukiyo-e woodblock print.

No brush strokes: flat colour blocks, bokashi gradients, sumi key-block outlines
from region borders, kasumi mist bands, patterned waves, baren mottling and paper fibre.
"""
import sys
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pp.core import *
from pp.bridge import Bridge, render_bridge

SEED = 1857
W, H = 2400, 1800
rng = np.random.default_rng(SEED)

cam = Camera((-420, 30, 2000), 170, 3.5, 2300, W, H)
br = Bridge((0, 0, 0), 0)
hy = cam.horizon_y()
yy, xx = np.mgrid[0:H, 0:W].astype(float)
xs = np.arange(W)
labels = np.zeros((H, W), int)
INK = hexc('1d1b22')

# ---------- sky: Prussian-blue bokashi at the top, fading to paper, pink band at the horizon ----------
t = np.clip(yy / hy, 0, 1)
img = ramp(t, [(0, hexc('1b2f5c')), (0.22, hexc('2c4f86')), (0.45, hexc('9fb3c2')), (0.62, hexc('eadcc0')), (0.85, hexc('f0cfae')), (1, hexc('e79a7a'))])

# moon
MX, MY, MR = W * 0.50, H * 0.15, 95
moon = np.clip(MR - np.hypot(xx - MX, yy - MY), 0, 1)
img = composite(img, hexc('f4ecc8'), moon)
labels[moon > 0.5] = 9

# ---------- mountains: Mt Tamalpais + Marin headlands (flat, darker bokashi at the ridge) ----------
def ridge(base, amp, cells, peak_x=None, peak_h=0, peak_w=1):
    r = base - amp * fbm1d(W, cells, rng, 4, 0.45)
    if peak_x is not None:
        r = r - peak_h * np.clip(1 - np.abs(xs - peak_x) / peak_w, 0, 1) ** 1.6
    return r

tam = ridge(hy - 90, 40, 2, W * 0.42, 330, 900)
m1 = below_curve(H, W, tam) * (yy < hy)
d1 = np.clip((yy - tam[None, :]) / 140, 0, 1)
img = composite(img, ramp(d1, [(0, hexc('2f4a6e')), (1, hexc('7d98a8'))]), m1)
labels[m1 > 0.5] = 1
head = ridge(hy - 40, 110, 3)
m2 = below_curve(H, W, head) * (yy < hy)
d2 = np.clip((yy - head[None, :]) / 90, 0, 1)
img = composite(img, ramp(d2, [(0, hexc('2e5a4a')), (1, hexc('6f937a'))]), m2)
labels[m2 > 0.5] = 2

# ---------- water: indigo bokashi ----------
tw = np.clip((yy - hy) / (H - hy), 0, 1)
water = ramp(tw, [(0, hexc('a9bcc4')), (0.12, hexc('4f76a0')), (0.5, hexc('27477c')), (1, hexc('172c55'))])
wm = yy >= hy
img = np.where(wm[..., None], water, img)
labels[wm] = 3

# ---------- bridge: two flat tones of vermilion ----------
brgb, ba, info = render_bridge(cam, br, W, H,
                               {'tower': hexc('d0452c'), 'pier': hexc('8a8f96'), 'deck': hexc('b83a28'), 'cable': hexc('c8412b')},
                               (0.9, 0.3, 0.2), ss=3)
L = lum(brgb)
tone = np.where(L > np.percentile(L[ba > 0.5], 45), 1.0, 0.0)
flat = np.where(tone[..., None] > 0.5, hexc('d24a2e'), hexc('9b3122'))
pier = (brgb[..., 2] > brgb[..., 0] * 0.8) & (ba > 0.5)
flat[pier] = hexc('7f8790')
img = composite(img, flat, ba)
labels[(ba > 0.5)] = 4
labels[pier] = 5

# ---------- kasumi: horizontal mist bands with rounded ends ----------
r = Raster(W, H, 2)
bands = []
for (x0, x1, y, h) in [(W * 0.22, W * 0.62, H * 0.27, 56), (W * 0.30, W + 100, hy + 26, 40)]:
    bands.append((x0, x1, y, h))
def kasumi(d, s):
    for x0, x1, y, h in bands:
        d.rounded_rectangle((x0 * s, (y - h / 2) * s, x1 * s, (y + h / 2) * s), radius=h / 2 * s, fill=255)
km = r.mask(kasumi)
img = composite(img, hexc('f1e2cc'), km * 0.92)
labels[km > 0.5] = 6

# ---------- patterned waves: scalloped crest lines, smaller toward the horizon ----------
wave = Image.new('L', (W * 2, H * 2), 0)
dw = ImageDraw.Draw(wave)
y = hy + 30
while y < H + 40:
    k = (y - hy) / (H - hy)
    step = 12 + 110 * k ** 1.3
    amp = 3 + 22 * k ** 1.2
    lw = max(2, int(2 + 6 * k))
    off = rng.uniform(0, step)
    for x0 in np.arange(-step + off, W + step, step):
        if rng.random() < 0.25 + 0.3 * (1 - k):
            continue
        box = (x0 * 2, (y - amp) * 2, (x0 + step) * 2, (y + amp) * 2)
        dw.arc(box, 190, 350, fill=255, width=lw * 2)
    y += 10 + 70 * k ** 1.2
wm2 = np.asarray(wave.resize((W, H), Image.LANCZOS), float) / 255 * (labels == 3)
img = composite(img, hexc('dfe6e3'), wm2 * 0.85)

# lamps along the deck: tiny flat yellow dots
lxy, lz = info['lamps']
dots = Raster(W, H, 2).mask(lambda d, s: [d.ellipse(((x - 4) * s, (y - 4) * s, (x + 4) * s, (y + 4) * s), fill=255)
                                           for (x, y), z in zip(lxy, lz) if z > 0 and 0 <= x < W and 0 <= y < H])
img = composite(img, hexc('f6d36b'), dots)

# ---------- foreground: gnarled pine on a rock, lower left ----------
rk = ridge(H * 0.90, 70, 3) + np.clip((W * 0.70 - xs) / (W * 0.12), 0, 1) ** 1.5 * 400 + 30 * np.clip((xs - W * 0.85) / (W * 0.15), 0, 1)
rm = below_curve(H, W, rk)
img = composite(img, ramp(np.clip((yy - rk[None, :]) / 160, 0, 1), [(0, hexc('5a5040')), (1, hexc('2d2822'))]), rm)
labels[rm > 0.5] = 7

def pine(d, s):
    trunk = [(W * 0.13, H * 0.95), (W * 0.15, H * 0.80), (W * 0.11, H * 0.62), (W * 0.17, H * 0.47), (W * 0.26, H * 0.36), (W * 0.30, H * 0.30)]
    from scipy.interpolate import CubicSpline
    tk = np.array(trunk); u = np.linspace(0, 1, len(tk)); uu = np.linspace(0, 1, 160)
    cx_s, cy_s = CubicSpline(u, tk[:, 0])(uu), CubicSpline(u, tk[:, 1])(uu)
    for i in range(159):
        wdt = 52 - 34 * uu[i]
        d.line([((W - cx_s[i]) * s, cy_s[i] * s), ((W - cx_s[i + 1]) * s, cy_s[i + 1] * s)], fill=255, width=int(wdt * s))
        d.ellipse(((W - cx_s[i]) * s - wdt * s / 2, cy_s[i] * s - wdt * s / 2, (W - cx_s[i]) * s + wdt * s / 2, cy_s[i] * s + wdt * s / 2), fill=255)
    d.line([(W * 0.85 * s, H * 0.66 * s), (W * 0.94 * s, H * 0.55 * s), (W * 0.99 * s, H * 0.56 * s)], fill=255, width=int(18 * s), joint='curve')
    d.line([(W * 0.80 * s, H * 0.42 * s), (W * 0.84 * s, H * 0.27 * s)], fill=255, width=int(14 * s))
trm = r.mask(pine)
img = composite(img, hexc('4a3a2e'), trm)
labels[trm > 0.5] = 8
# foliage clumps: flat dark-green cloud shapes with a lighter top bokashi
clumps = [(W * 0.70, H * 0.27, 190, 60), (W * 0.81, H * 0.24, 150, 52), (W * 0.60, H * 0.31, 130, 44),
          (W * 0.95, H * 0.52, 120, 42), (W * 0.85, H * 0.41, 110, 38), (W * 0.76, H * 0.335, 100, 34), (W * 0.86, H * 0.645, 95, 34)]
def fol(d, s):
    for cx_, cy_, rw, rh in clumps:
        for j in range(7):
            ox = rng.uniform(-rw * 0.8, rw * 0.8); oy = rng.uniform(-rh * 0.3, rh * 0.4)
            a, b = rw * rng.uniform(0.35, 0.6), rh * rng.uniform(0.6, 0.9)
            d.ellipse(((cx_ + ox - a) * s, (cy_ + oy - b) * s, (cx_ + ox + a) * s, (cy_ + oy + b) * s), fill=255)
fm = r.mask(fol)
ftop = np.zeros_like(fm)
img = composite(img, hexc('1f3b2c'), fm)
labels[fm > 0.5] = 10
# needle strokes inside foliage
nd = Image.new('L', (W, H), 0); dn = ImageDraw.Draw(nd)
fy_, fx_ = np.nonzero(fm[::6, ::6] > 0.6)
for py, px in zip(fy_ * 6, fx_ * 6):
    a = rng.uniform(-0.6, 0.6) - np.pi / 2
    ln = rng.uniform(8, 16)
    dn.line((px, py, px + np.cos(a) * ln, py + np.sin(a) * ln), fill=255, width=2)
img = composite(img, hexc('4d7a52'), np.asarray(nd, float) / 255 * fm * 0.6)

# ---------- key block: sumi outlines from region borders ----------
lab = labels.copy()
edge = np.zeros((H, W), bool)
for dy_, dx_ in ((0, 1), (1, 0)):
    a = lab[:H - dy_, :W - dx_]; b = lab[dy_:, dx_:]
    e = a != b
    edge[:H - dy_, :W - dx_] |= e
# no ink between sky and water/mist (printed without key lines)
soft = np.isin(labels, [0, 3, 6])
edge &= ~ndi.binary_erosion(soft, iterations=2)
# thin bridge parts (cables, suspenders) print from the colour block only, no key line
bm = labels == 4
thick = ndi.binary_opening(bm, structure=np.ones((7, 7)))
edge &= ~ndi.binary_dilation(bm & ~thick, iterations=2)
ink = ndi.binary_dilation(edge, iterations=1).astype(float)
ink = ndi.gaussian_filter(ink, 0.6)
# thinner ink on the bridge suspenders: the bridge gets only its own silhouette
img = composite(img, INK, np.clip(ink * 1.3, 0, 1) * 0.9)

# ---------- paper, baren mottling, misregistration ----------
img = np.roll(img, (2, -1), (0, 1)) * 0.25 + img * 0.75
mott = fbm(H, W, 40, rng, 3)
img = img * (0.94 + 0.1 * mott[..., None])
fib = np.zeros((H, W))
for _ in range(2500):
    x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
    a = rng.uniform(0, np.pi); ln = rng.uniform(10, 40)
    n = int(ln)
    px = (x0 + np.cos(a) * np.arange(n)).astype(int) % W
    py = (y0 + np.sin(a) * np.arange(n)).astype(int) % H
    fib[py, px] = 1
fib = ndi.gaussian_filter(fib, 0.7)
img = img * (1 - 0.18 * fib[..., None]) + 0.05 * fib[..., None]
grain = ndi.gaussian_filter(rng.random((H, W)), 0.8)
img = img * (0.96 + 0.08 * grain[..., None])

# ---------- margin: paper border, keyline, red seal ----------
M = 70
paper = hexc('efe4cc') * (0.95 + 0.08 * mott[..., None])
frame = np.zeros((H, W), bool)
frame[:M] = frame[-M:] = True; frame[:, :M] = frame[:, -M:] = True
img = np.where(frame[..., None], paper, img)
kl = np.zeros((H, W), bool)
kl[M - 5:M, M - 5:W - M + 5] = kl[H - M:H - M + 5, M - 5:W - M + 5] = True
kl[M - 5:H - M + 5, M - 5:M] = kl[M - 5:H - M + 5, W - M:W - M + 5] = True
img = composite(img, INK, kl.astype(float))
sx0, sy0, sz = M + 60, H - M - 170, 90
seal = np.zeros((H, W)); seal[sy0:sy0 + sz, sx0:sx0 + sz] = 1
inner = np.zeros((H, W)); inner[sy0 + 12:sy0 + sz - 12, sx0 + 12:sx0 + sz - 12] = 1
core = np.zeros((H, W)); core[sy0 + 20:sy0 + sz - 20, sx0 + 20:sx0 + sz - 20] = 1
img = composite(img, hexc('b8322a'), np.clip(seal - inner + core, 0, 1) * (0.85 + 0.15 * mott))

save(np.clip(img, 0, 1), 'out/p3_ukiyoe.png')
print('seed', SEED)
