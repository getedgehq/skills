"""A procedural 3D Golden Gate Bridge: towers, portals, deck, cables, suspenders, lamps.

Dimensions follow the real bridge (metres): main span 1280, side spans 343,
towers 227 above water, deck at ~67, cable planes ~27 apart.
"""
import numpy as np
from PIL import Image, ImageDraw

MAIN = 1280.0
SIDE = 343.0
TOWER_H = 227.0
DECK_Y = 67.0
HALF = 14.5          # half distance between cable planes / leg centres
CABLE_LOW = 71.0     # lowest point of main cable at midspan


class Bridge:
    def __init__(self, origin, angle_deg):
        """origin: world position of north tower base (x, 0, z); angle: axis heading in xz (0 => +z)."""
        a = np.radians(angle_deg)
        self.o = np.array(origin, float)
        self.d = np.array([np.sin(a), 0, np.cos(a)])        # along the bridge
        self.n = np.array([np.cos(a), 0, -np.sin(a)])       # across the bridge
        self.up = np.array([0, 1.0, 0])

    def P(self, s, y, lat):
        return self.o + self.d * s + self.up * y + self.n * lat

    # ----- geometry -----
    def boxes(self):
        """Return list of (8 corners, kind, meta)."""
        out = []
        # towers
        levels = [0, 20, DECK_Y, 104, 144, 184, TOWER_H]
        lw = [13, 12, 11, 10, 9, 8]
        ld = [22, 18, 16, 14, 12, 10.5]
        for ts in (0.0, MAIN):
            for side in (-1, 1):
                for k in range(len(levels) - 1):
                    y0, y1 = levels[k], levels[k + 1]
                    w, dd = lw[k], ld[k]
                    kind = 'pier' if k == 0 else 'tower'
                    if k == 0:
                        w, dd = 16, 30
                    out.append((self._box(ts, y0, y1, side * HALF, w, dd), kind, {'ts': ts, 'y0': y0, 'y1': y1}))
            # pier block between legs
            out.append((self._box_span(ts, 0, 20, -HALF, HALF, 30), 'pier', {'ts': ts}))
            # portal struts (between the legs, above the deck)
            for (y0, y1, dd) in [(96, 104, 9), (136, 144, 8), (176, 184, 7), (212, 227, 9)]:
                k = np.searchsorted(levels, y0) - 1
                w = lw[min(k, len(lw) - 1)]
                out.append((self._box_span(ts, y0, y1, -HALF + w / 2, HALF - w / 2, dd), 'tower', {'ts': ts, 'y0': y0, 'y1': y1}))
            # strut under the deck
            out.append((self._box_span(ts, 50, DECK_Y - 8, -HALF, HALF, 10), 'tower', {'ts': ts}))
        # deck (segmented for depth sort)
        segs = np.arange(-SIDE - 120, MAIN + SIDE + 121, 10.0)
        for s0, s1 in zip(segs[:-1], segs[1:]):
            out.append((self._box_s(s0, s1, DECK_Y - 8, DECK_Y, -HALF - 1.5, HALF + 1.5), 'deck', {}))
        return out

    def _box(self, s, y0, y1, lat, w, dd):
        return self._box_s(s - dd / 2, s + dd / 2, y0, y1, lat - w / 2, lat + w / 2)

    def _box_span(self, s, y0, y1, l0, l1, dd):
        return self._box_s(s - dd / 2, s + dd / 2, y0, y1, l0, l1)

    def _box_s(self, s0, s1, y0, y1, l0, l1):
        c = []
        for s in (s0, s1):
            for y in (y0, y1):
                for l in (l0, l1):
                    c.append(self.P(s, y, l))
        return np.array(c)

    def cable_y(self, s):
        s = np.asarray(s, float)
        y = np.empty_like(s)
        m = (s >= 0) & (s <= MAIN)
        t = s[m] / MAIN
        y[m] = TOWER_H - 4 * (TOWER_H - CABLE_LOW) * t * (1 - t)
        for lo, hi, sign in ((-SIDE, 0, -1), (MAIN, MAIN + SIDE, 1)):
            mm = (s >= lo) & (s <= hi)
            u = (s[mm] - lo) / SIDE           # 0..1 across side span
            if sign < 0:
                lin = DECK_Y - 4 + (TOWER_H - DECK_Y + 4) * u
            else:
                lin = TOWER_H - (TOWER_H - DECK_Y + 4) * u
            y[mm] = lin - 22 * 4 * u * (1 - u)
        return y

    def cables(self, n=400):
        s = np.linspace(-SIDE, MAIN + SIDE, n)
        y = self.cable_y(s)
        return [np.array([self.P(si, yi, side * HALF) for si, yi in zip(s, y)]) for side in (-1, 1)]

    def suspenders(self, spacing=15.24):
        out = []
        for side in (-1, 1):
            for s in np.arange(-SIDE + spacing, MAIN + SIDE, spacing):
                if abs(s) < 8 or abs(s - MAIN) < 8:
                    continue
                cy = float(self.cable_y(np.array([s]))[0])
                if cy - DECK_Y < 2:
                    continue
                out.append(np.array([self.P(s, cy, side * HALF), self.P(s, DECK_Y, side * HALF)]))
        return out

    def lamps(self, spacing=50.0):
        pts = []
        for side in (-1, 1):
            for s in np.arange(-SIDE - 100, MAIN + SIDE + 100, spacing):
                pts.append(self.P(s, DECK_Y + 9, side * (HALF + 1)))
        return np.array(pts)

    def beacons(self):
        return np.array([self.P(ts, TOWER_H + 3, side * HALF) for ts in (0, MAIN) for side in (-1, 1)])


FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def render_bridge(cam, br, w, h, colors, light, ss=3, flood=0.0, flood_col=None, sky_amb=None):
    """Rasterise the bridge. Returns (rgb float, alpha float, info dict)."""
    W, H = w * ss, h * ss
    rgb = Image.new('RGB', (W, H), (0, 0, 0))
    al = Image.new('L', (W, H), 0)
    dep = Image.new('F', (W, H), 0.0)
    dr, da, dd = ImageDraw.Draw(rgb), ImageDraw.Draw(al), ImageDraw.Draw(dep)
    L = np.array(light, float); L /= np.linalg.norm(L)
    polys = []
    for corners, kind, meta in br.boxes():
        cc = cam.cam(corners)
        if (cc[:, 2] < 1).any():
            continue
        xy, z = cam.proj(corners)
        ctr = corners.mean(0)
        for f in FACES:
            p = corners[list(f)]
            nrm = p.mean(0) - ctr
            nrm /= np.linalg.norm(nrm) + 1e-9
            if nrm @ (cam.p - p.mean(0)) <= 0:
                continue
            base = np.array(colors[kind], float)
            sh = 0.35 + 0.65 * max(0.0, nrm @ L)
            col = base * sh
            if sky_amb is not None:
                col = col + np.array(sky_amb) * max(0.0, nrm[1]) * 0.5
            if flood and kind == 'tower':
                y = p[:, 1].mean()
                face_cam = max(0.0, nrm @ ((cam.p - p.mean(0)) / np.linalg.norm(cam.p - p.mean(0))))
                col = col + np.array(flood_col) * flood * face_cam * np.exp(-(y - DECK_Y) / 110.0)
            polys.append((float(np.linalg.norm(p.mean(0) - cam.p)), xy[list(f)], col))
    polys.sort(key=lambda t: -t[0])
    for dist, pts, col in polys:
        q = [(float(x * ss), float(y * ss)) for x, y in pts]
        c = tuple(int(np.clip(v, 0, 1) * 255) for v in col)
        dd.polygon(q, fill=dist)
        dr.polygon(q, fill=c)
        da.polygon(q, fill=255)
    # cables + suspenders
    cabs = []
    for cab in br.cables():
        xy, z = cam.proj(cab)
        wd = np.clip(cam.f * 0.95 / z, 0.9, 12)
        cabs.append((xy, wd))
        for i in range(len(xy) - 1):
            seg = [(xy[i, 0] * ss, xy[i, 1] * ss), (xy[i + 1, 0] * ss, xy[i + 1, 1] * ss)]
            c = tuple(int(v * 255) for v in np.clip(colors['cable'], 0, 1))
            dr.line(seg, fill=c, width=max(1, int(round(wd[i] * ss))))
            da.line(seg, fill=255, width=max(1, int(round(wd[i] * ss))))
    sus = []
    for sp in br.suspenders():
        xy, z = cam.proj(sp)
        wd = float(np.clip(cam.f * 0.25 / z.mean(), 0.35, 3))
        sus.append((xy, wd))
        seg = [(xy[0, 0] * ss, xy[0, 1] * ss), (xy[1, 0] * ss, xy[1, 1] * ss)]
        a = int(255 * min(1.0, wd / 1.0))
        dr.line(seg, fill=tuple(int(v * 255) for v in np.clip(colors['cable'], 0, 1)), width=max(1, int(round(wd * ss))))
        da.line(seg, fill=a, width=max(1, int(round(wd * ss))))
    rgb = rgb.resize((w, h), Image.LANCZOS)
    al = al.resize((w, h), Image.LANCZOS)
    lamps_xy, lz = cam.proj(br.lamps())
    bea_xy, bz = cam.proj(br.beacons())
    info = {'depth': np.asarray(dep.resize((w, h), Image.NEAREST), float), 'cables': cabs, 'suspenders': sus, 'lamps': (lamps_xy, lz), 'beacons': (bea_xy, bz),
            'towers': [cam.proj(br.P(ts, y, 0))[0] for ts in (0, MAIN) for y in (0, TOWER_H)]}
    return np.asarray(rgb, float) / 255, np.asarray(al, float) / 255, info
