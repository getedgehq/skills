"""Shared primitives: noise, color, camera, rasterising. Nothing here loads an image."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi


# ---------- noise ----------

def value_noise(h, w, cells, rng):
    """Smooth value noise: random grid of `cells` rows, cubic-upsampled to h x w."""
    ch = max(2, int(cells))
    cw = max(2, int(round(cells * w / h)))
    g = rng.random((ch + 3, cw + 3))
    z = ndi.zoom(g, ((h + 3 * h / ch) / (ch + 3), (w + 3 * w / cw) / (cw + 3)), order=3)
    return z[:h, :w]


def fbm(h, w, cells, rng, octaves=5, gain=0.5, lac=2.0):
    out = np.zeros((h, w))
    amp, tot, c = 1.0, 0.0, cells
    for _ in range(octaves):
        out += amp * value_noise(h, w, c, rng)
        tot += amp
        amp *= gain
        c *= lac
    out /= tot
    out -= out.min()
    return out / max(out.max(), 1e-9)


def fbm1d(n, cells, rng, octaves=5, gain=0.5):
    out = np.zeros(n)
    amp, tot, c = 1.0, 0.0, cells
    x = np.linspace(0, 1, n)
    for _ in range(octaves):
        k = int(c) + 4
        pts = rng.random(k)
        xs = np.linspace(0, 1, k)
        from scipy.interpolate import CubicSpline
        out += amp * CubicSpline(xs, pts)(x)
        tot += amp
        amp *= gain
        c *= 2
    return out / tot


# ---------- color ----------

def hexc(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def lerp(a, b, t):
    t = np.asarray(t, float)
    return a + (b - a) * t[..., None] if t.ndim else a + (b - a) * t


def ramp(t, stops):
    """stops: list of (pos, rgb). t: array. Returns t.shape + (3,)."""
    t = np.clip(np.asarray(t, float), 0, 1)
    ps = np.array([p for p, _ in stops])
    cs = np.array([c for _, c in stops])
    out = np.empty(t.shape + (3,))
    for k in range(3):
        out[..., k] = np.interp(t, ps, cs[:, k])
    return out


def rgb2hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx = np.max(c, -1); mn = np.min(c, -1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-9
    rm = m & (mx == r); gm = m & (mx == g) & ~rm; bm = m & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    h /= 6
    s = np.where(mx > 1e-9, d / np.maximum(mx, 1e-9), 0)
    return np.stack([h, s, mx], -1)


def hsv2rgb(c):
    h, s, v = c[..., 0] % 1.0, np.clip(c[..., 1], 0, 1), np.clip(c[..., 2], 0, 1)
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    sel = [np.stack(x, -1) for x in ((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))]
    out = np.zeros(h.shape + (3,))
    for k in range(6):
        out[i == k] = sel[k][i == k]
    return out


def lum(img):
    return img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def save(img, path):
    import os
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    Image.fromarray(to_u8(img)).save(path)


# ---------- raster helpers ----------

class Raster:
    """Supersampled mask drawing via PIL; returns float masks in [0,1] at base size."""

    def __init__(self, w, h, ss=2):
        self.w, self.h, self.ss = w, h, ss

    def mask(self, fn):
        im = Image.new('L', (self.w * self.ss, self.h * self.ss), 0)
        d = ImageDraw.Draw(im)
        fn(d, self.ss)
        im = im.resize((self.w, self.h), Image.LANCZOS)
        return np.asarray(im, float) / 255.0

    def poly(self, pts):
        s = self.ss
        return self.mask(lambda d, _: d.polygon([(x * s, y * s) for x, y in pts], fill=255))

    def polys(self, list_of_pts):
        s = self.ss
        def f(d, _):
            for pts in list_of_pts:
                if len(pts) >= 3:
                    d.polygon([(x * s, y * s) for x, y in pts], fill=255)
        return self.mask(f)

    def lines(self, segs):
        """segs: list of (pts, width)."""
        s = self.ss
        def f(d, _):
            for pts, wd in segs:
                if len(pts) >= 2:
                    d.line([(x * s, y * s) for x, y in pts], fill=255, width=max(1, int(round(wd * s))), joint='curve')
        return self.mask(f)


def composite(base, color, mask):
    """base (h,w,3), color (3,) or (h,w,3), mask (h,w)."""
    m = mask[..., None]
    return base * (1 - m) + np.asarray(color) * m


def below_curve(h, w, ys):
    """Mask of pixels below curve ys (len w) with 1px AA."""
    yy = np.arange(h)[:, None]
    return np.clip(yy - ys[None, :] + 0.5, 0, 1)


def glow(h, w, pts, radius, rng=None):
    """pts: list of (x,y,intensity). Returns additive glow field."""
    f = np.zeros((h, w))
    for x, y, a in pts:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < w and 0 <= yi < h:
            f[yi, xi] += a
    return ndi.gaussian_filter(f, radius) * (2 * np.pi * radius * radius)


# ---------- camera ----------

class Camera:
    def __init__(self, pos, yaw_deg, pitch_deg, focal, w, h, cx=None, cy=None):
        self.p = np.array(pos, float)
        self.w, self.h = w, h
        self.f = focal
        self.cx = w / 2 if cx is None else cx
        self.cy = h / 2 if cy is None else cy
        y, p = np.radians(yaw_deg), np.radians(pitch_deg)
        fwd = np.array([np.sin(y) * np.cos(p), np.sin(p), np.cos(y) * np.cos(p)])
        right = np.array([np.cos(y), 0, -np.sin(y)])
        up = np.cross(fwd, right)
        self.R = np.stack([right, up, fwd])

    def cam(self, P):
        return (np.asarray(P, float) - self.p) @ self.R.T

    def proj(self, P):
        c = self.cam(P)
        z = np.maximum(c[..., 2], 1e-3)
        x = self.cx + self.f * c[..., 0] / z
        y = self.cy - self.f * c[..., 1] / z
        return np.stack([x, y], -1), c[..., 2]

    def horizon_y(self):
        # a point far away at camera height
        fwd = self.R[2].copy(); fwd[1] = 0; fwd /= np.linalg.norm(fwd)
        (xy, _) = self.proj(self.p * np.array([1, 0, 1]) + fwd * 1e7)
        return xy[1]
