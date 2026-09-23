"""Golden Gate at blue hour, impressionist broken colour: the bridge dissolving in fog.

Underpainting: 3D bridge + atmospheric fog + mirrored water. Paint: short dabs,
per-stroke hue scatter and complementary flecks (optical mixing, no blending).
"""
import sys, time
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pp.core import *
from pp.bridge import Bridge, render_bridge
from pp.strokes import Painter

SEED = 1903
W, H = 2400, 1800
rng = np.random.default_rng(SEED)
PREVIEW = '--under' in sys.argv

cam = Camera((380, 22, 2150), 196, 5.5, 2500, W, H)
br = Bridge((0, 0, 0), 0)
hy = cam.horizon_y()
yy, xx = np.mgrid[0:H, 0:W].astype(float)
SUNX = W * 0.3

# ---------------- sky: violet above, rose, then an orange afterglow behind the far tower ----------------
t = np.clip(yy / hy, 0, 1)
sky = ramp(t, [(0, hexc('34386e')), (0.4, hexc('5f5a92')), (0.7, hexc('a57fa6')), (0.88, hexc('e0a092')), (1, hexc('f3c58e'))])
sun = np.exp(-(((xx - SUNX) / 520) ** 2 + ((yy - hy + 40) / 220) ** 2))
sky = sky + sun[..., None] * (hexc('ffc27a') - sky) * 0.8
cl = fbm(H, W, 3, rng, 5)
clouds = np.clip((cl - 0.45) * 3, 0, 1) * np.clip(1 - yy / (hy * 0.8), 0, 1)
sky = sky + clouds[..., None] * (hexc('c49aae') - sky) * 0.45
img = sky.copy()
labels = np.zeros((H, W), int)

# far hills (Marin), lost in haze
xs = np.arange(W)
hill = hy - 40 - 150 * fbm1d(W, 2, rng) * np.clip((xs - W * 0.35) / (W * 0.4), 0, 1)
hm = below_curve(H, W, hill) * (yy < hy)
img = composite(img, hexc('8c7aa0'), hm * 0.75)
labels[hm > 0.5] = 1

# ---------------- bridge with depth haze ----------------
brgb, ba, info = render_bridge(cam, br, W, H,
                               {'tower': hexc('a9452f'), 'pier': hexc('6b5d78'), 'deck': hexc('7e3a33'), 'cable': hexc('9c4a3a')},
                               (0.8, 0.4, 0.3), flood=0.25, flood_col=hexc('ffb070'), sky_amb=hexc('504880'))
# haze by screen position: stronger to the right (towards far tower and the glow)
fogc = hexc('c7a2ac')
dep = ndi.grey_dilation(info['depth'], size=5)
haze = np.clip(1 - np.exp(-(dep - 700).clip(0) / 900), 0, 0.82)
brgb = brgb * (1 - haze[..., None]) + fogc * haze[..., None]
img = composite(img, brgb, ba * (yy < hy + 2))
labels[(ba > 0.5) & (yy < hy + 2)] = 3

# south headland (Fort Point side) swallowing the deck on the right
sh = hy - np.clip((xs - W * 0.70) / (W * 0.30), 0, 1) ** 0.7 * 330 - 40 * fbm1d(W, 5, rng) * (xs > W * 0.7)
shm = below_curve(H, W, sh) * (yy < hy + 4)
shc = ramp(np.clip((yy - sh[None, :]) / 300, 0, 1), [(0, hexc('6a5578')), (1, hexc('3c3354'))])
img = composite(img, shc, shm)
labels[shm > 0.5] = 1

# fog bank rolling through the span, low over the water
fn = fbm(H, W, 4, rng, 5)
fog = np.clip(1 - np.abs(yy - (hy - 55 - 60 * fn)) / (110 + 90 * fn), 0, 1) ** 1.3
fog *= (0.5 + 0.5 * fn)
img = img + fog[..., None] * (hexc('e3c1bf') - img) * 0.95

# ---------------- water: mirrored scene broken into horizontal ripples ----------------
wm = yy >= hy
ry = np.clip(2 * hy - yy, 0, H - 1)
def hstreaks(ry_, rx_):
    z = rng.random((H // ry_ + 2, W // rx_ + 2))
    return ndi.zoom(z, (ry_, rx_), order=1)[:H, :W] - 0.5
wob = hstreaks(5, 60) * 30 * np.clip((yy - hy) / 300, 0.2, 1.5)
rx = np.clip(xx + wob, 0, W - 1)
mir = np.stack([ndi.map_coordinates(img[..., k], [ry, rx], order=1) for k in range(3)], -1)
mir = ndi.gaussian_filter(mir, (6, 1.5, 0))
tw = np.clip((yy - hy) / (H - hy), 0, 1)
wcol = ramp(tw, [(0, hexc('9f86a8')), (0.5, hexc('4d4f86')), (1, hexc('2b2f5f'))])
water = mir * 0.62 + wcol * 0.38
streak = hstreaks(4, 90) * 2
water = water * (1 + 0.12 * streak[..., None])
img = np.where(wm[..., None], water, img)
labels[wm & (labels == 0)] = 2
labels[wm & (labels == 3)] = 2

# lamps, beacons, and a small boat
lxy, lz = info['lamps']
vis = [(x, y, 0.8) for (x, y), z in zip(lxy, lz) if z > 0 and 0 <= x < W and 0 <= y < hy]
lights = np.clip(glow(H, W, vis, 4) * 0.8, 0, 1)
img = img + lights[..., None] * (hexc('ffd890') - img)
bx, by = W * 0.14, hy + 330
r = Raster(W, H, 2)
boat = r.poly([(bx - 90, by), (bx + 110, by), (bx + 80, by + 22), (bx - 70, by + 22)])
sail = r.poly([(bx - 5, by - 5), (bx + 3, by - 170), (bx + 70, by - 8)])
img = composite(img, hexc('3a2f52'), boat)
img = composite(img, hexc('d9b3a6'), sail)
labels[(boat + sail) > 0.5] = 4
img = np.clip(img, 0, 1)

if PREVIEW:
    save(img, 'out/p2_under.png'); sys.exit()

# ---------------- flow: hatching diagonals in air, horizontals on water ----------------
ang = np.radians(-28) + (fbm(H, W, 3, rng, 3) - 0.5) * 1.2
vx, vy = np.cos(ang), np.sin(ang)
vx[labels == 2], vy[labels == 2] = 1.0, 0.0
vx[labels == 3], vy[labels == 3] = 0.0, 1.0

def broken(col, sx, sy, lab, rng):
    """complementary flecks: some strokes warm/cool shifted, lifting the value."""
    hsv = rgb2hsv(col)
    k = rng.random(len(col))
    hsv[k < 0.07, 0] += 0.06
    hsv[(k >= 0.07) & (k < 0.14), 0] -= 0.06
    hsv[k < 0.14, 2] *= 1.05
    return np.clip(hsv2rgb(hsv), 0, 1)

t0 = time.time()
P = Painter(img, labels, (vx, vy), rng, ground=hexc('b9a08a'))
max_r = np.array([30, 30, 30, 6, 6])
min_r = np.array([8, 8, 8, 0, 0])
c = dict(sat=1.12, jitter=(0.014, 0.07, 0.05), grid_k=0.75, max_r=max_r, min_r=min_r, curv=0.3, edge_w=2.0, color_fn=broken)
P.layer(22, first=True, maxlen=4, minlen=2, thresh=0, **c)
P.layer(14, maxlen=4, minlen=2, thresh=0.03, **c)
P.layer(9, maxlen=4, minlen=2, thresh=0.035, **c)
P.layer(5, maxlen=2, minlen=1, thresh=0.045, **c)
P.layer(3, maxlen=2, minlen=1, thresh=0.06, **{**c, 'jitter': (0.02, 0.1, 0.06)})
for x, y, a in vis:
    P.dab(x, y, rng.uniform(2.5, 4), hexc('ffe2a0'))
out = P.finish(impasto=0.4, bristle=0.35, light=(-0.5, -0.85), lic_steps=5)
save(out, 'out/p2_impressionist.png')
print('strokes', P.n_strokes, 'secs', round(time.time() - t0, 1), 'seed', SEED)
