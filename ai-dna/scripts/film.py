#!/usr/bin/env python3
"""Local 4:5 AI DNA splat renderer. Use scripts/make.py as the public entry point."""
import json, math, os, sys, argparse
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.environ.get('DNA_FILE', os.path.join(HERE, 'dna.json'))))
R = D['rungs']; N = len(R); HT = max(1, R[-1]['y'])
COLORS = {'ChatGPT': (0x74, 0xaa, 0x9c), 'Claude Code': (0xe0, 0x82, 0x5e), 'Codex': (0xa8, 0x8c, 0xff), 'Claude': (0xe0, 0x82, 0x5e)}
PROV = D['providers']
SPAN, RADIUS, PITCH = 1700.0, 300.0, 600.0
DFULL = 3450.0
FOV = math.radians(34)
BW, BH = 1080, 1350
FPS = 30
INTRO_DIR = os.environ.get('INTRO_DIR', os.path.join(HERE, 'intro'))

# ---------------- geometry (world) ----------------
ry = np.array([-SPAN / 2 + r['y'] / HT * SPAN for r in R])
rang = ry / PITCH * 2 * math.pi
rcol = np.array([COLORS[PROV[r['p']]] for r in R], float) / 255.0
rmc = np.array([r['mc'] for r in R])
t_arr = np.array([r['t'] for r in R], float); rec = (t_arr - t_arr[0]) / max(1, t_arr[-1] - t_arr[0])

rng = np.random.default_rng(7)
# message particles: one per message, spread along its conversation's rung, thicker for bigger conversations
m_r = np.repeat(np.arange(N), rmc)                      # rung index per message
M = len(m_r)
m_u = rng.uniform(0.06, 0.94, M)
sig = 1.2 + 1.1 * np.log1p(rmc[m_r])
m_j = rng.normal(0, 1, (M, 3)) * sig[:, None] * np.array([0.35, 1.0, 1.0])  # jitter; less along the rung


def rung_ends(ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.stack([-c * RADIUS, np.zeros_like(c), -s * RADIUS], 1), np.stack([c * RADIUS, np.zeros_like(c), s * RADIUS], 1)


def message_world(spin):
    a = rang[m_r] + spin
    L, Rr = rung_ends(a)
    P = L + (Rr - L) * m_u[:, None] + m_j
    P[:, 1] += ry[m_r]
    return P


# structure: faint line per rung (so 1-message conversations still read as a rung), backbones, beads
LS = 10
l_r = np.repeat(np.arange(N), LS); l_u = np.tile(np.linspace(0.04, 0.96, LS), N)
BB = 7  # backbone samples between consecutive rungs


def structure_world(spin):
    a = rang + spin
    L, Rr = rung_ends(a[l_r])
    Lp = L + (Rr - L) * l_u[:, None]; Lp[:, 1] += ry[l_r]
    # backbone: dense samples of the two helices along y
    yy = np.linspace(ry[0] - 20, ry[-1] + 20, 5200)
    aa = yy / PITCH * 2 * math.pi + spin
    bL = np.stack([-np.cos(aa) * RADIUS, yy, -np.sin(aa) * RADIUS], 1)
    bR = np.stack([np.cos(aa) * RADIUS, yy, np.sin(aa) * RADIUS], 1)
    E1, E2 = rung_ends(a); E1[:, 1] = ry; E2[:, 1] = ry
    return Lp, np.concatenate([bL, bR]), np.concatenate([E1, E2])


# ---------------- camera ----------------
def basis(yaw, pitch, dist, ty):
    ty = ty + 110 * min(1, dist / DFULL) ** 4
    cp, sp = math.cos(pitch), math.sin(pitch)
    pos = np.array([dist * cp * math.sin(yaw), ty + dist * sp, dist * cp * math.cos(yaw)])
    f = np.array([0, ty, 0]) - pos; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return pos, r, u, f


def project(P, cam, W, H, roll=0.0):
    pos, r, u, f = basis(*cam)
    d = P - pos
    cx, cy, cz = d @ r, d @ u, d @ f
    fl = (H / 2) / math.tan(FOV / 2)
    cz = np.maximum(cz, 1e-3)
    x, y = cx * fl / cz, -cy * fl / cz
    if roll:
        c, s = math.cos(roll), math.sin(roll); x, y = x * c - y * s, x * s + y * c
    return W / 2 + x, H / 2 + y, cz, fl / cz


# ---------------- splatting ----------------
def splat(buf, x, y, col, w):
    H, W, _ = buf.shape
    ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (w > 1e-5)
    x, y, col, w = x[ok], y[ok], col[ok], w[ok]
    ix, iy = x.astype(np.int64), y.astype(np.int64); fx, fy = x - ix, y - iy
    flat = buf.reshape(-1, 3)
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        idx = (iy + dy) * W + ix + dx; k = ww * w
        for ch in range(3):
            flat[:, ch] += np.bincount(idx, weights=k * col[:, ch], minlength=W * H)


def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def smoother(x):
    x = np.clip(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10)


# ---------------- timeline ----------------
# (real conversation title prefix, on-screen hot take)
if os.environ.get('STOPS_FILE'):
    STOPS_SPEC = json.load(open(os.environ['STOPS_FILE']))
    STOP_IDX = [next(i for i, r in enumerate(R) if r['title'].startswith(item['title'])) for item in STOPS_SPEC[:3]]
    STOP_LABEL = {i: item.get('label') or R[i]['title'] for i, item in zip(STOP_IDX, STOPS_SPEC)}
else:
    STOP_IDX = sorted(range(N), key=lambda i: R[i]['mc'], reverse=True)[:3]
    STOP_LABEL = {i: R[i]['title'] or f'Conversation {i+1}' for i in STOP_IDX}
CAM_IDX = (STOP_IDX + [STOP_IDX[-1]] * 3)[:3]
F = STOP_IDX[0]; FY = ry[F]
era = [dict(e, ym=-SPAN / 2 + (e['y0'] + e['y1']) / 2 / HT * SPAN) for e in D['eras']]
lastEra = era[-1]['ym']


def _near(v, ref):
    return v + 2 * math.pi * round((ref - v) / (2 * math.pi))


YF = _near(-rang[F] + 0.3, 2.7); YFP = _near(-rang[F] + 0.3, 2.0)
_ys = []; _ref = 3.3
for _i in CAM_IDX:
    _y = _near(-rang[_i] + 0.3, _ref + 0.7); _ys.append(_y); _ref = _y
Y1, Y2, Y3 = _ys; y1, y2, y3 = (ry[i] for i in CAM_IDX)
# (a, b, c, d): fade in a->b, fade out c->d; overlapping windows cross-fade between conversations
STOPS_INTRO = [(8.7, 9.3, 10.3, 10.9), (10.3, 10.9, 12.2, 12.8), (12.2, 12.8, 14.2, 14.9)]


def keys_for(mode):
    # t, yaw, pitch, dist, ty
    if mode == 'intro':
        return [(0, 0.0, 0.02, DFULL, 0), (5.2, 1.3, 0.03, DFULL, 0), (6.5, 2.0, -0.40, DFULL * 0.92, 0),
                (7.7, 2.7, 0.38, DFULL * 0.92, 0), (8.9, Y1 - 0.25, 0.12, 1650, y1 + 40), (9.4, Y1 - 0.12, 0.09, 1480, y1),
                (10.4, Y1 + 0.02, 0.05, 1380, y1), (11.1, Y2 + 0.55, -0.34, 1250, y2), (12.2, Y2 + 0.68, -0.28, 1150, y2),
                (13.0, Y3 - 0.55, 0.44, 1300, y3), (14.2, Y3 - 0.42, 0.38, 1200, y3),
                (16.0, Y3 + 0.9, -0.12, DFULL, 0), (18.0, Y3 + 1.35, 0.03, DFULL, 0)]
    return [(0, 0.0, 0.03, DFULL, 0), (2.2, 1.6, -0.13, DFULL * 0.86, 0),
            (3.0, Y1 - 0.25, 0.08, 1500, y1), (4.1, Y1 + 0.02, 0.05, 1350, y1),
            (5.0, Y2 - 0.25, -0.18, 1450, y2), (6.1, Y2 + 0.02, -0.12, 1300, y2),
            (7.0, Y3 - 0.25, 0.20, 1450, y3), (8.2, Y3 + 0.02, 0.12, 1300, y3),
            (10.4, Y3 + 0.9, 0.03, DFULL, 0), (12.0, Y3 + 1.2, 0.03, DFULL, 0)]


def cam_at(mode, t):
    K = keys_for(mode)
    k = 0
    while k < len(K) - 2 and t >= K[k + 1][0]: k += 1
    a, c = K[k], K[k + 1]
    u = smoother((t - a[0]) / (c[0] - a[0]))
    from scipy.interpolate import PchipInterpolator
    yaw = float(PchipInterpolator([q[0] for q in K], [q[1] for q in K])(min(max(t, 0), K[-1][0])))  # smooth, never stops
    m = [a[i] + (c[i] - a[i]) * u for i in range(5)]
    return (yaw, m[2], m[3], m[4])


def focus_level(mode, t):
    if mode == 'intro': a, b, c, d = 9.6, 10.9, 12.6, 13.5
    else: a, b, c, d = 5.6, 6.9, 8.7, 9.6
    return smooth((t - a) / (b - a)) * (1 - smooth((t - c) / (d - c)))


def stops_at(mode, t):
    if mode == 'intro':
        return [(i, smooth((t - a) / (b - a)) * (1 - smooth((t - c) / (d - c)))) for i, (a, b, c, d) in zip(STOP_IDX, STOPS_INTRO)]
    times = [(2.9, 3.4, 4.0, 4.5), (4.9, 5.4, 6.0, 6.5), (6.9, 7.4, 8.1, 8.7)]
    return [(i, smooth((t-a)/(b-a))*(1-smooth((t-c)/(d-c)))) for i,(a,b,c,d) in zip(STOP_IDX,times)]


def dimw(r, stops, boost, base, k, amp):
    out = np.ones(len(r))
    for i, lv in stops:
        if lv <= 0: continue
        w = np.where(r == i, boost, np.clip(base + amp * np.exp(-np.abs(r - i) / k), 0, 1))
        out -= lv * (1 - w)
    return out


def labels_level(mode, t):
    if mode == 'intro': return smooth((t - 5.6) / 0.8) * (1 - smooth((t - 8.2) / 0.5)) + smooth((t - 16.0) / 0.6)
    return smooth((t - 0.2) / 0.8) * (1 - smooth((t - 4.8) / 0.6)) + smooth((t - 10.2) / 0.6)


# ---------------- intro: video + portrait ----------------
T_VID, T_BG0, T_BG1, T_DOT0, T_DOT1, T_FLY0 = 1.5, 1.35, 2.25, 1.95, 2.75, 2.85
ZC = np.array([540.0, 610.0])  # push-in centre (face), base coords


def zoom_at(t): return 1.0 + 0.16 * smoother(t / 2.85)


_intro = {}


def load_intro():
    if _intro: return _intro
    raw = np.fromfile(os.path.join(INTRO_DIR, 'frames.raw'), np.uint8)
    frames = raw.reshape(-1, BH, BW, 3)
    mask = np.asarray(Image.open(os.path.join(INTRO_DIR, 'mask_crop.png')).convert('L'), float) / 255.0
    freeze = frames[-1].astype(float) / 255.0
    lum = freeze @ np.array([0.299, 0.587, 0.114])
    imp = mask ** 2 * (0.05 + lum ** 1.7)
    imp[:, :] = gaussian_filter(imp, 0.6)
    p = imp.ravel() / imp.sum()
    r2 = np.random.default_rng(11)
    idx = r2.choice(p.size, size=M, p=p)
    fy, fx = np.divmod(idx, BW)
    fx = fx + r2.uniform(0, 1, M); fy = fy + r2.uniform(0, 1, M)
    fcol = freeze[fy.astype(int), fx.astype(int)]
    fcol = np.clip(fcol * 1.15 + 0.04, 0, 1)
    # assignment: oldest messages -> bottom of the portrait, newest -> top of the head; local x order kept
    order_face = np.argsort(-fy, kind='stable')
    tx, ty_, _, _ = project(message_world(0.0), cam_at('intro', T_FLY0 + 1.6), BW, BH)
    order_msg = np.lexsort((m_u, m_r))  # by time
    CH = 600
    face_of = np.empty(M, np.int64)
    for s in range(0, M, CH):
        fo = order_face[s:s + CH]; mo = order_msg[s:s + CH]
        fo = fo[np.argsort(fx[fo])]; mo = mo[np.argsort(tx[mo])]
        face_of[mo] = fo
    _intro.update(frames=frames, mask=mask, fx=fx[face_of], fy=fy[face_of], fcol=fcol[face_of],
                  delay=0.95 * (1 - fy[face_of] / BH) + r2.uniform(0, 0.3, M),
                  swirl=r2.normal(0, 1, M))
    return _intro


def zoom_img(img, z, S):
    """scale an HxWx3 float image about ZC by z, output at scale S"""
    W, H = int(BW * S), int(BH * S)
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    cx, cy = ZC
    box = (cx - cx / z, cy - cy / z, cx + (BW - cx) / z, cy + (BH - cy) / z)
    return np.asarray(pil.resize((W, H), Image.LANCZOS, box=box), float) / 255.0


# ---------------- text ----------------
FONT_DIR = '/usr/local/share/fonts/extras/ttf'


def font(w, px):
    size = max(8, int(px))
    candidates = (f'{FONT_DIR}/Inter-{w}.ttf', '/usr/local/share/fonts/Inter.ttc',
                  '/System/Library/Fonts/Supplemental/Arial.ttf',
                  'C:/Windows/Fonts/arial.ttf', 'DejaVuSans.ttf')
    for cand in candidates:
        try: return ImageFont.truetype(cand, size)
        except OSError: pass
    return ImageFont.load_default()


def text_spaced(dr, xy, s, f, fill, sp=0.0, anchor='l'):
    x, y = xy
    if anchor != 'l':
        w = sum(dr.textlength(ch, font=f) + sp for ch in s) - sp
        x = x - (w if anchor == 'r' else w / 2)
    for ch in s:
        dr.text((x, y), ch, font=f, fill=fill); x += dr.textlength(ch, font=f) + sp


def fmt_date(ts):
    import datetime
    d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc); return f'{d.day} {d.strftime("%b %Y")}'


def mon(ts):
    import datetime
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime('%b %Y').upper()


# ---------------- frame ----------------
def render(mode, t, S=1, hero=False):
    W, H = int(BW * S), int(BH * S)
    intro = mode == 'intro'
    cam = cam_at(mode, t)
    spin = 0.0
    acc = np.zeros((H, W, 3)); acc_soft = np.zeros((H, W, 3)); acc_far = np.zeros((H, W, 3))
    stops = stops_at(mode, t)
    fl_level = min(1.0, sum(lv for _, lv in stops))

    Pm = message_world(spin)
    x, y, z, s = project(Pm, cam, W, H)
    zc = cam[2]
    fog = np.clip(1.25 - (z - zc + 200) / 1300, 0.3, 1.0)
    # focus: fade everything but the focus neighbourhood
    fw = dimw(m_r, stops, 9.0, 0.10, 30, 0.35)
    bright = (0.75 + 0.25 * rec[m_r])
    base_w = 0.30 * fog * fw * bright * np.minimum(1, 60 / rmc[m_r]) ** 0.3 * np.clip(s * 3.0, 0.8, 3.0)
    col = rcol[m_r]
    alpha_helix = 1.0
    photo = None; pa = 0.0
    if intro and t < T_FLY0 + 2.6:
        I = load_intro()
        z_now = zoom_at(min(t, T_FLY0))
        sx = (ZC[0] + (I['fx'] - ZC[0]) * z_now) * S; sy = (ZC[1] + (I['fy'] - ZC[1]) * z_now) * S
        u = smoother((t - T_FLY0 - I['delay'] * 0.9) / 1.35)
        # swirl: lateral arc during flight
        arc = np.sin(np.pi * u) * I['swirl'] * 90 * S
        x = sx + (x - sx) * u + arc; y = sy + (y - sy) * u
        cmix = u[:, None]
        col = I['fcol'] * (1 - cmix) + col * cmix
        dots_in = smooth((t - T_DOT0) / (T_DOT1 - T_DOT0))
        w_face = 0.55
        base_w = (w_face * (1 - u) + base_w * u) * dots_in
        alpha_helix = smooth((t - T_FLY0 - 1.2) / 1.0)
        if t < T_DOT1:
            fi = min(len(I['frames']) - 1, int(t * 24))
            img = I['frames'][fi].astype(float) / 255.0
            bg = smooth((t - T_BG0) / (T_BG1 - T_BG0))
            m = I['mask'][..., None]
            img = img * (m + (1 - m) * (1 - bg))
            img *= 1 - 0.25 * bg
            photo = zoom_img(img, zoom_at(t), S); pa = 1 - smooth((t - T_DOT0 - 0.1) / (T_DOT1 - T_DOT0))
    # depth of field layers
    coc = np.abs(z - zc) / zc * (1.0 + 0.6 * (cam[2] < 1500))
    if intro and t < T_FLY0 + 2.6: coc = coc * alpha_helix
    for i, lv in stops: coc = np.where(m_r == i, coc * (1 - lv), coc)
    near = coc < 0.06; mid = (coc >= 0.06) & (coc < 0.14); far = coc >= 0.14
    for msk, b in ((near, acc), (mid, acc_soft), (far, acc_far)):
        splat(b, x[msk], y[msk], col[msk], base_w[msk] * S * S * (0.9 if b is acc else 1.6))

    # structure
    Lp, BBp, Ends = structure_world(spin)
    lx, ly, lz, ls = project(Lp, cam, W, H)
    lf = np.clip(1.25 - (lz - zc + 200) / 1300, 0.3, 1.0)
    lr = l_r
    lfw = dimw(lr, stops, 1.0, 0.08, 25, 0.5)
    splat(acc_soft, lx, ly, rcol[lr] * 0.8 + 0.12, 0.26 * lf * lfw * alpha_helix * S * S * np.clip(ls * 3.0, 0.8, 3.0))
    bx, by, bz, bs = project(BBp, cam, W, H)
    bf = np.clip(1.25 - (bz - zc + 200) / 1300, 0.25, 1.0)
    fade_b = (1 - 0.8 * fl_level)
    splat(acc_soft, bx, by, np.tile([0.82, 0.88, 0.92], (len(bx), 1)), 0.22 * bf * alpha_helix * fade_b * S * S * np.clip(bs * 2.2, 0.4, 2.5))
    ex, ey, ez, es = project(Ends, cam, W, H)
    ef = np.clip(1.25 - (ez - zc + 200) / 1300, 0.3, 1.0)
    er = np.concatenate([np.arange(N), np.arange(N)])
    efw = dimw(er, stops, 1.0, 0.08, 25, 0.5)
    bead = (0.35 + 0.22 * np.log1p(rmc[er])) * ef * efw * alpha_helix
    beads = np.zeros((H, W, 3))
    splat(beads, ex, ey, np.clip(rcol[er] * 1.25 + 0.08, 0, 1), bead * S * S)
    for i, lv in stops:  # the focus conversation's messages glow
        if lv <= 0.01: continue
        fm = m_r == i
        splat(beads, x[fm], y[fm], np.clip(col[fm] * 1.2 + 0.1, 0, 1), np.full(fm.sum(), 0.10 * lv * S * S))

    # compose: DOF blur + bloom
    sig = S * 1.0
    img = acc + gaussian_filter(acc_soft, (sig * 1.0, sig * 1.0, 0)) + gaussian_filter(acc_far, (sig * 2.6, sig * 2.6, 0))
    img += gaussian_filter(beads, (1.3 * S * max(1, 900 / cam[2]) ** 0.5, 1.3 * S * max(1, 900 / cam[2]) ** 0.5, 0)) * 3.0
    small = img[::4, ::4]
    bloom = gaussian_filter(small, (3 * S, 3 * S, 0)) * 0.9 + gaussian_filter(small, (14 * S, 14 * S, 0)) * 0.7
    bl = np.repeat(np.repeat(bloom, 4, 0), 4, 1)[:H, :W]
    img = img + bl * 0.55
    out = 1 - np.exp(-img * 1.35)
    # background
    yy, xx = np.mgrid[0:H, 0:W]
    rad = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.48) / H) ** 2)
    bgc = np.array([0.028, 0.036, 0.046]) + np.array([0.035, 0.05, 0.058])[None, None] * np.exp(-rad[..., None] ** 2 / 0.09)
    out = out + bgc * (1 - out)
    if photo is not None:
        out = photo * pa + out * (1 - 0.6 * pa)
    # grain
    g = np.random.default_rng(int(t * 1000) + 3).normal(0, 0.006, (H, W, 1))
    out = np.clip(out + g, 0, 1)
    im = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    overlay(im, mode, t, cam, S, stops, hero)
    return im


ICON_FILE = {'ChatGPT': 'chatgpt', 'Claude Code': 'claude', 'Codex': 'codex', 'Claude': 'claude'}
_icons = {}


def paste_icon(lay, prov, x, y, size, alpha):
    key = (prov, int(size))
    if key not in _icons:
        _icons[key] = Image.open(os.path.join(HERE, '..', 'icons', ICON_FILE[prov] + '.png')).convert('RGBA').resize((int(size), int(size)), Image.LANCZOS)
    ic = _icons[key].copy()
    ic.putalpha(ic.getchannel('A').point(lambda v: int(v * max(0, min(1, alpha)))))
    lay.alpha_composite(ic, (int(x), int(y)))


def overlay(im, mode, t, cam, S, stops, hero):
    W, H = im.size
    intro = mode == 'intro'
    ui = 1.0 if not intro else smooth((t - 4.4) / 0.8)
    if hero: ui = 1.0
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    a = lambda v: int(255 * max(0, min(1, v)))
    if ui > 0:
        text_spaced(dr, (56 * S, 54 * S), 'AI DNA', font('SemiBold', 30 * S), (245, 247, 248, a(ui)), sp=5 * S)
        dr.text((56 * S, 96 * S), f'{N:,} conversations · {M:,} messages', font=font('Regular', 21 * S), fill=(255, 255, 255, a(ui * 0.55)))
        # legend
        lx = 56 * S; ly = H - 74 * S; f = font('Medium', 21 * S)
        for p in PROV:
            c = COLORS[p]; paste_icon(lay, p, lx, ly - 1 * S, 26 * S, ui)
            dr.text((lx + 36 * S, ly + 1 * S), p, font=f, fill=c + (a(ui * 0.95),)); lx += (dr.textlength(p, font=f) + 76 * S)
        if intro and os.environ.get('END_NOTE'):
            en = smooth((t - 15.2) / 0.6)
            if en > 0:
                fe = font('Regular', 19 * S); msg = os.environ['END_NOTE']
                dr.text((W - 56 * S - dr.textlength(msg, font=fe), ly + 3 * S), msg, font=fe, fill=(255, 255, 255, a(en * 0.6)))
    lv = 1.0 if hero else labels_level(mode, t)
    if lv > 0:
        f = font('Medium', 20 * S); f2 = font('Regular', 17 * S)
        pos, r, u, fwd = basis(*cam)
        fl = (H / 2) / math.tan(FOV / 2)
        for ei, e in enumerate(era):
            P = np.array([[0, e['ym'], 0]]); x, y, z, s = project(P, cam, W, H)
            xr = x[0] + RADIUS * s[0] + 70 * S
            y0 = y[0]
            if not (60 * S < y0 < H - 110 * S) or xr + dr.textlength(e['label'], font=f) + 30 * S > W: continue
            dr.line((xr - 40 * S, y0, xr - 12 * S, y0), fill=(255, 255, 255, a(lv * 0.25)), width=max(1, S))
            text_spaced(dr, (xr, y0 - 12 * S), f'ERA {ei+1}' if os.environ.get('HIDE_TITLES') == '1' else e['label'], f, (255, 255, 255, a(lv * 0.78)), sp=1.6 * S)
            yr = f"{mon(e['t0'])} – {mon(e['t1'])}".replace(' – ', ' to ')
            dr.text((xr, y0 + 10 * S), yr, font=f2, fill=(255, 255, 255, a(lv * 0.36)))
    for Fi, lvl in stops:
        if lvl <= 0.02: continue
        c = R[Fi]
        L, Rr = rung_ends(np.array([rang[Fi]]))
        E = np.concatenate([L, Rr]); E[:, 1] = ry[Fi]
        ex, ey, ez, es = project(E, cam, W, H)
        x0, x1 = float(ex.min()), float(ex.max()); ymid = float(ey.mean())
        v = smooth((lvl - 0.55) / 0.4)
        if v > 0:
            tx = max(56 * S, min(x0 + 20 * S, W - 520 * S)); ty0 = ymid - 250 * S
            for xe, ye in ((ex[0], ey[0]), (ex[1], ey[1])):
                dr.line((xe, ye - 34 * S, xe, ye + 34 * S), fill=(255, 255, 255, a(v * 0.55)), width=max(1, int(1.5 * S)))
            BELIEF = os.environ.get('STOP_STYLE') == 'belief'
            if BELIEF: text_spaced(dr, (tx, ty0), 'WHAT I BELIEVE', font('Medium', 17 * S), (255, 255, 255, a(v * 0.45)), sp=2.4 * S)
            fl = font('SemiBold', 44 * S); words = (f'CONVERSATION {Fi+1}' if os.environ.get('HIDE_TITLES') == '1' else STOP_LABEL[Fi][:100]).split(); lines = ['']
            for w_ in words:
                cand = (lines[-1] + ' ' + w_).strip()
                if dr.textlength(cand, font=fl) > W - tx - 56 * S and lines[-1]: lines.append(w_)
                else: lines[-1] = cand
            if len(lines) == 2:  # balance the two lines so no word is left alone
                best = min(range(1, len(words)), key=lambda k: max(dr.textlength(' '.join(words[:k]), font=fl), dr.textlength(' '.join(words[k:]), font=fl)))
                lines = [' '.join(words[:best]), ' '.join(words[best:])]
            dy = (len(lines) - 1) * 54 * S
            for li, ln in enumerate(lines):
                dr.text((tx, ty0 + 30 * S + li * 54 * S), ln, font=fl, fill=(255, 255, 255, a(v)))
            if BELIEF: continue
            paste_icon(lay, PROV[c['p']], tx, ty0 + 90 * S + dy, 30 * S, v)
            dr.text((tx + 42 * S, ty0 + 92 * S + dy), f"{PROV[c['p']]} · {fmt_date(c['t'])}", font=font('Regular', 24 * S), fill=(255, 255, 255, a(v * 0.62)))

    im.paste(Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('out'); ap.add_argument('--t', type=float, default=0)
    ap.add_argument('--mode', default='intro'); ap.add_argument('--scale', type=float, default=1)
    ap.add_argument('--jobs', type=int, default=1); ap.add_argument('--times', default=''); ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    if a.cmd == 'still':
        render(a.mode, a.t, a.scale).save(a.out)
    elif a.cmd == 'sheet':
        ts = [float(v) for v in a.times.split(',')]
        ims = [render(a.mode, t, 1).resize((360, 450), Image.LANCZOS) for t in ts]
        cols = min(6, len(ims)); rows = math.ceil(len(ims) / cols)
        sh = Image.new('RGB', (360 * cols, 450 * rows))
        for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 360, (i // cols) * 450))
        sh.save(a.out)
    elif a.cmd == 'hero':
        render('pure', 0, a.scale, hero=True).save(a.out)
    else:
        mode = a.cmd; dur = 18.0 if mode == 'intro' else 12.0
        os.makedirs(a.out, exist_ok=True)
        if mode == 'intro': load_intro()
        n = int(round(dur * a.fps))
        todo = [k for k in range(n) if not os.path.exists(f'{a.out}/{k:04d}.png')]
        for k in todo:
            render(mode, k / a.fps, a.scale).save(f'{a.out}/{k:04d}.png')
            if k % a.fps == 0: print(k, flush=True)


def _run(arg):
    mode, k, out = arg
    render(mode, k / FPS).save(f'{out}/{k:04d}.png'); return k


if __name__ == '__main__':
    main()
