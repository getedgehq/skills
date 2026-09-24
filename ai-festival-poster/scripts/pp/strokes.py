"""Stroke-based painting (after Hertzmann 1998, "Painterly Rendering with Curved Brush
Strokes of Multiple Sizes") driven by a procedural underpainting instead of a photo,
plus an impasto pass: per-stroke height + bristle texture via line-integral convolution.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from .core import rgb2hsv, hsv2rgb, lum, fbm


def lic(noise, vx, vy, steps=10, h=1.0):
    """Line-integral convolution of `noise` along (vx, vy)."""
    H, W = noise.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    acc = noise.astype(np.float32).copy()
    n = 1
    for sgn in (1, -1):
        px, py = xx.copy(), yy.copy()
        for _ in range(steps):
            ix = np.clip(px, 0, W - 1).astype(int)
            iy = np.clip(py, 0, H - 1).astype(int)
            px += sgn * vx[iy, ix] * h
            py += sgn * vy[iy, ix] * h
            acc += ndi.map_coordinates(noise, [py, px], order=1, mode='reflect')
            n += 1
    return acc / n


class Painter:
    def __init__(self, ref, labels, field, rng, ground=(0.45, 0.35, 0.25)):
        """
        ref: (H,W,3) underpainting in [0,1]
        labels: (H,W) int region map (strokes never cross region borders)
        field: (vx, vy) unit style flow field
        """
        self.ref = ref
        self.H, self.W = ref.shape[:2]
        self.labels = labels
        self.fx, self.fy = field
        self.rng = rng
        self.canvas = Image.new('RGB', (self.W, self.H), tuple(int(c * 255) for c in ground))
        self.height = Image.new('F', (self.W, self.H), 0.0)
        self.dc = ImageDraw.Draw(self.canvas)
        self.dh = ImageDraw.Draw(self.height)
        self.n_strokes = 0

    def arr(self):
        return np.asarray(self.canvas, np.float32) / 255.0

    def layer(self, R, *, thresh=0.06, blur_k=0.5, grid_k=1.0, minlen=2, maxlen=10, step_k=0.9,
              edge_w=6.0, jitter=(0.02, 0.10, 0.08), sat=1.0, max_r=None, first=False,
              curv=0.6, mask=None, min_r=None, color_fn=None, height_amp=1.0, stroke_filter=None):
        """Paint one brush size. jitter = (hue, sat, val) per-stroke random offsets."""
        rng = self.rng
        H, W = self.H, self.W
        blur = ndi.gaussian_filter(self.ref, (blur_k * R, blur_k * R, 0)) if blur_k > 0 else self.ref
        L = lum(blur)
        gy = ndi.sobel(L, 0)
        gx = ndi.sobel(L, 1)
        gm = np.hypot(gx, gy) + 1e-9
        # edge-following direction (perpendicular to gradient), blended with style field by edge strength
        ex, ey = -gy / gm, gx / gm
        wgt = np.clip(gm * edge_w, 0, 1)
        # orient edge vectors to agree with style field
        sgn = np.sign(ex * self.fx + ey * self.fy + 1e-6)
        ex, ey = ex * sgn, ey * sgn
        vx = self.fx * (1 - wgt) + ex * wgt
        vy = self.fy * (1 - wgt) + ey * wgt
        vn = np.hypot(vx, vy) + 1e-9
        vx, vy = vx / vn, vy / vn

        cur = self.arr()
        diff = np.linalg.norm(cur - blur, axis=-1)
        g = max(1, int(round(R * grid_k)))
        ny, nx = H // g, W // g
        d = diff[:ny * g, :nx * g].reshape(ny, g, nx, g).transpose(0, 2, 1, 3).reshape(ny, nx, g * g)
        err = d.mean(-1)
        am = d.argmax(-1)
        cy = np.arange(ny)[:, None] * g + am // g
        cx = np.arange(nx)[None, :] * g + am % g
        sel = np.ones_like(err, bool) if first else err > thresh
        # random subpixel jitter of start points
        sx = (cx[sel] + rng.uniform(-0.5, 0.5, sel.sum()) * (g if first else 1)).clip(0, W - 1)
        sy = (cy[sel] + rng.uniform(-0.5, 0.5, sel.sum()) * (g if first else 1)).clip(0, H - 1)
        ix, iy = sx.astype(int), sy.astype(int)
        keep = np.ones(len(sx), bool)
        if max_r is not None:
            keep &= R <= max_r[self.labels[iy, ix]]
        if min_r is not None:
            keep &= R >= min_r[self.labels[iy, ix]]
        if mask is not None:
            keep &= mask[iy, ix] > 0.5
        sx, sy = sx[keep], sy[keep]
        N = len(sx)
        if N == 0:
            return 0
        order = rng.permutation(N)
        sx, sy = sx[order], sy[order]
        ix, iy = sx.astype(int), sy.astype(int)
        lab0 = self.labels[iy, ix]
        col = blur[iy, ix].copy()
        # per-stroke colour jitter in HSV
        hsv = rgb2hsv(col)
        hsv[:, 0] += rng.normal(0, jitter[0], N)
        hsv[:, 1] = hsv[:, 1] * sat * (1 + rng.normal(0, jitter[1], N))
        hsv[:, 2] = hsv[:, 2] * (1 + rng.normal(0, jitter[2], N))
        col = np.clip(hsv2rgb(hsv), 0, 1)
        if color_fn is not None:
            col = color_fn(col, sx, sy, lab0, rng)

        # trace all strokes in parallel
        pts = np.zeros((maxlen + 1, N, 2), np.float32)
        pts[0, :, 0], pts[0, :, 1] = sx, sy
        alive = np.ones(N, bool)
        length = np.ones(N, int)
        px, py = sx.copy(), sy.copy()
        dx = vx[iy, ix]; dy = vy[iy, ix]
        # random initial orientation sign so strokes grow both ways on average
        flip = rng.random(N) < 0.5
        dx[flip] *= -1; dy[flip] *= -1
        for k in range(1, maxlen + 1):
            jx, jy = np.clip(px, 0, W - 1).astype(int), np.clip(py, 0, H - 1).astype(int)
            nxd, nyd = vx[jy, jx], vy[jy, jx]
            s = np.sign(nxd * dx + nyd * dy + 1e-6)
            nxd, nyd = nxd * s, nyd * s
            # limit curvature
            dx = dx * (1 - curv) + nxd * curv
            dy = dy * (1 - curv) + nyd * curv
            nn = np.hypot(dx, dy) + 1e-9
            dx, dy = dx / nn, dy / nn
            qx, qy = px + dx * R * step_k, py + dy * R * step_k
            inb = (qx >= 0) & (qx < W) & (qy >= 0) & (qy < H)
            qix, qiy = np.clip(qx, 0, W - 1).astype(int), np.clip(qy, 0, H - 1).astype(int)
            same = self.labels[qiy, qix] == lab0
            if k > minlen:
                rc = blur[qiy, qix]
                good = np.linalg.norm(rc - col, axis=-1) <= np.linalg.norm(rc - cur[qiy, qix], axis=-1) + 0.02
            else:
                good = np.ones(N, bool)
            ok = alive & inb & same & good
            px = np.where(ok, qx, px); py = np.where(ok, qy, py)
            pts[k, :, 0], pts[k, :, 1] = px, py
            length += ok
            alive = ok

        width = max(1, int(round(2 * R)))
        hval = rng.uniform(0.55, 1.0, N) * height_amp
        c8 = (col * 255 + 0.5).astype(int)
        for i in range(N):
            n = length[i]
            if stroke_filter is not None and not stroke_filter(i):
                continue
            p = [(float(pts[j, i, 0]), float(pts[j, i, 1])) for j in range(n)]
            c = (int(c8[i, 0]), int(c8[i, 1]), int(c8[i, 2]))
            if n >= 2:
                self.dc.line(p, fill=c, width=width, joint='curve')
                self.dh.line(p, fill=float(hval[i]), width=width, joint='curve')
            r = R * 0.98
            for (x, y) in (p[0], p[-1]):
                self.dc.ellipse((x - r, y - r, x + r, y + r), fill=c)
                self.dh.ellipse((x - r, y - r, x + r, y + r), fill=float(hval[i]))
        self.n_strokes += N
        return N

    def finish(self, impasto=0.35, bristle=0.5, light=(-0.6, -0.8), rng=None, lic_steps=8,
               bristle_scale=0.8, flow=None):
        """Apply impasto relief lighting. Returns float RGB."""
        rng = rng or self.rng
        img = self.arr().astype(np.float64)
        h = np.asarray(self.height, np.float32)
        if bristle > 0:
            noise = ndi.gaussian_filter(rng.random((self.H, self.W)).astype(np.float32), bristle_scale)
            noise = (noise - noise.mean()) / (noise.std() + 1e-9)
            fx, fy = flow if flow is not None else (self.fx, self.fy)
            streak = lic(noise, fx.astype(np.float32), fy.astype(np.float32), steps=lic_steps)
            streak = streak / (streak.std() + 1e-9)
            h = h + bristle * 0.12 * streak
        h = ndi.gaussian_filter(h, 0.8)
        gy, gx = np.gradient(h)
        lx, ly = light
        shade = -(gx * lx + gy * ly) * 6.0
        shade = np.clip(shade, -1.5, 1.5)
        img = img * (1 + impasto * shade[..., None])
        return np.clip(img, 0, 1)

    def dab(self, x, y, r, col, hval=1.0):
        c = tuple(int(np.clip(v, 0, 1) * 255) for v in col)
        self.dc.ellipse((x - r, y - r, x + r, y + r), fill=c)
        self.dh.ellipse((x - r, y - r, x + r, y + r), fill=float(hval))

    def line(self, pts, w, col, hval=1.0):
        c = tuple(int(np.clip(v, 0, 1) * 255) for v in col)
        p = [(float(x), float(y)) for x, y in pts]
        self.dc.line(p, fill=c, width=max(1, int(round(w))), joint='curve')
        self.dh.line(p, fill=float(hval), width=max(1, int(round(w))), joint='curve')
