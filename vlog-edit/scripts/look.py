"""The visual system: palette, type, and every graphic the editor draws.

Every function here returns one full 1080x1920 RGBA frame. Cards are drawn per frame because they
BUILD across their beat (title, then figure, then bar, then qualifier), and a card that stops
building halfway reads as a freeze.

Three rules drive the drawing code, and each was learned from a cut that looked broken:
  - Text reveals in place and never slides. Objects (the whole card, the map) travel.
  - Motion is sub-pixel. A composite at a whole-pixel offset quantises a slow move into runs of
    identical frames, which is a freeze. Everything that moves goes through one AFFINE resample.
  - A figure is never animated through values it does not have. A count-up scrubbed to any frame
    shows a number nobody counted, so figures fade in at their final value.
"""
import json, math, os, urllib.request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920

CACHE = os.environ.get("VLOG_EDIT_CACHE", os.path.expanduser("~/.cache/vlog-edit"))
FONT_DIR = os.path.join(CACHE, "fonts")

# Palette. One saturated colour. Everything else is navy ink on a lavender ground.
ACCENT = (0x15, 0x4C, 0xFF)
INK = (0x0B, 0x15, 0x33)
INK_MID = (0x5A, 0x6B, 0x93)
SURFACE = (0xFF, 0xFF, 0xFF)
HAIRLINE = (0xE6, 0xE9, 0xF2)
GROUND = ((0xF2, 0xF5, 0xFD), (0xE7, 0xEC, 0xFA), (0xDF, 0xE6, 0xF8))
WHITE = (255, 255, 255)

# The caption band. Every shot, face or graphic, puts the line here, so a card keeps everything
# below CAP_CLEAR empty.
CAP_Y = 1640
CAP_CLEAR = 1520
# With a translation line, the band moves up to make room for it below.
SUB_CAP_Y = 1580
SUB_Y = 1650


# --------------------------------------------------------------------------------------------
# Type
# --------------------------------------------------------------------------------------------

_FONTS = {}


def font(weight, size):
    """Inter Display at `weight`. Raises if `vlog.py setup` has not fetched it: a silent fallback
    to some system sans changes every measurement the layout makes."""
    key = (weight, size)
    if key not in _FONTS:
        p = os.path.join(FONT_DIR, f"InterDisplay-{weight}.ttf")
        if not os.path.isfile(p):
            raise SystemExit(f"vlog-edit: missing {p}. Run `python3 vlog.py setup` once.")
        _FONTS[key] = ImageFont.truetype(p, size)
    return _FONTS[key]


# --------------------------------------------------------------------------------------------
# Timing helpers. `i` is the frame, `n` the last frame index of the card.
# --------------------------------------------------------------------------------------------

def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def window(i, n, a, b):
    """0..1 progress of frame i through the [a, b] fraction of the card's life."""
    u = i / max(1, n)
    return clamp01((u - a) / max(1e-6, b - a))


def smoothstep(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def push(u, accel=0.12, decel=0.30, v0=0.35):
    """Position 0..1 on a trapezoidal velocity profile. It LEAVES already moving (at v0 of cruise),
    cruises, then decelerates to rest, so a move that starts on a cut does not dead-hold first."""
    u = clamp01(u)
    cruise = 1.0 - accel - decel
    ramp = accel * (v0 + 1.0) / 2.0
    area = ramp + cruise + decel / 2.0
    if u < accel:
        s = v0 * u + (1.0 - v0) * u * u / (2.0 * accel)
    elif u < accel + cruise:
        s = ramp + (u - accel)
    else:
        r = 1.0 - u
        s = ramp + cruise + decel / 2.0 - r * r / (2.0 * decel)
    return clamp01(s / area)


def mix(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


# --------------------------------------------------------------------------------------------
# Drawing primitives
# --------------------------------------------------------------------------------------------

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def balanced(d, text, fnt, maxw):
    """As few lines as fit, evened out, so line two is never one orphaned word."""
    words = text.split()
    if d.textlength(text, font=fnt) <= maxw or len(words) < 2:
        return [text]
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        m = max(d.textlength(a, font=fnt), d.textlength(b, font=fnt))
        if m <= maxw and (best is None or m < best[0]):
            best = (m, [a, b])
    return best[1] if best else wrap(d, text, fnt, maxw)


def centred(d, y, text, fnt, colour, a=1.0):
    if a <= 0.004:
        return
    w = d.textlength(text, font=fnt)
    d.text(((W - w) / 2, y), text, font=fnt, fill=(*colour, int(255 * clamp01(a))))


_GROUND = None


def ground():
    """The lavender ground, a near-vertical three-stop gradient, built small and scaled."""
    global _GROUND
    if _GROUND is None:
        sw, sh = 64, 256
        small = Image.new("RGB", (sw, sh))
        px = small.load()
        for y in range(sh):
            for x in range(sw):
                t = clamp01(0.94 * ((y + 0.5) / sh) + 0.06 * (1 - (x + 0.5) / sw))
                px[x, y] = (mix(GROUND[0], GROUND[1], t / 0.55) if t <= 0.55
                            else mix(GROUND[1], GROUND[2], (t - 0.55) / 0.45))
        _GROUND = small.resize((W, H), Image.BICUBIC).convert("RGBA")
    return _GROUND


_SHADOW = {}


def shadow(box, radius):
    """Soft navy drop shadow, cached by geometry: the blur costs more than the rest of a frame."""
    key = (tuple(int(v) for v in box), radius)
    if key not in _SHADOW:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x0, y0, x1, y1 = key[0]
        ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y0 + 22, x1 - 6, y1 + 22], radius,
                                             fill=(*INK, 30))
        _SHADOW[key] = sh.filter(ImageFilter.GaussianBlur(24))
    return _SHADOW[key]


def surface(img, box, radius=36, alpha=255):
    if alpha < 255:
        s = shadow(box, radius).copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha / 255)))
        img.alpha_composite(s)
    else:
        img.alpha_composite(shadow(box, radius))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius, fill=(*SURFACE, alpha), outline=(*HAIRLINE, alpha), width=2)
    return d


def settle(layer, i, n, cy, amount=0.05):
    """The whole graphic keeps pushing in to the last frame, as ONE sub-pixel affine.

    The push scales with the card's length: what the eye reads as motion is pixels per frame, so
    a four-second card needs a bigger total move than a two-second one or it creeps.
    """
    amount = max(amount, min(0.12, 0.0011 * n))
    s = 1.0 + amount * window(i, n, 0.0, 1.0)
    cx = W / 2.0
    return layer.transform((W, H), Image.AFFINE,
                           (1.0 / s, 0.0, cx - cx / s, 0.0, 1.0 / s, cy - cy / s),
                           resample=Image.BICUBIC)


def fmt(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def text_shadowed(text_layer, strength=0.55, blur=7, dy=4):
    """White type over footage needs a soft shadow, not an outline."""
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(text_layer.getchannel("A").point(lambda v: int(v * strength)))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)), (0, dy))
    out.alpha_composite(text_layer)
    return out


# --------------------------------------------------------------------------------------------
# Cards. Each takes (i, n, spec) and returns an opaque RGBA frame.
# --------------------------------------------------------------------------------------------

def card_stat(i, n, c):
    """Type on the ground: title, the figure, a bar that fills, the qualifier, the source.

    `total` and `part` make the bar a real ratio of two published figures. With part == total the
    whole bar fills in ink; with a smaller part the accent grows inside a pale full-length track.
    """
    img = ground().copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    title = c.get("title", "")
    tf = font("Medium", 60)
    for k, ln in enumerate(balanced(d, title, tf, 880)):
        centred(d, 400 + k * 74, ln, tf, INK)

    colour = ACCENT if c.get("accent") else INK
    nf = font("Bold", 290 if len(str(c["value"])) <= 6 else 220)
    centred(d, 620, str(c["value"]), nf, colour, smoothstep(window(i, n, 0.02, 0.16)))

    total, part = c.get("total"), c.get("part")
    if total:
        bx0, bx1, by, bh = 150, 930, 1030, 46
        ta = smoothstep(window(i, n, 0.10, 0.24))
        if ta > 0.004:
            d.rounded_rectangle([bx0, by, bx1, by + bh], bh // 2, fill=(*SURFACE, int(255 * ta)),
                                outline=(*HAIRLINE, int(255 * ta)), width=2)
            if part != total:
                d.rounded_rectangle([bx0, by, bx1, by + bh], bh // 2,
                                    fill=(*HAIRLINE, int(200 * ta)))
        f = (part / total) * push(window(i, n, 0.22, 0.95))
        if f > 0.002:
            d.rounded_rectangle([bx0, by, bx0 + max(bh, (bx1 - bx0) * f), by + bh], bh // 2,
                                fill=(*colour, 255))
    if c.get("unit"):
        centred(d, 1110, c["unit"], font("Medium", 50), INK_MID,
                smoothstep(window(i, n, 0.34, 0.52)))
    if c.get("source"):
        sf = font("Medium", 32)
        for k, ln in enumerate(wrap(d, c["source"], sf, 860)):
            centred(d, 1210 + k * 42, ln, sf, INK_MID, smoothstep(window(i, n, 0.50, 0.68)))
    img.alpha_composite(settle(layer, i, n, cy=860, amount=0.06))
    return img


def card_list(i, n, c):
    """A title and a column of items that arrive one by one; optionally one gets picked.

    Items are objects, so each one rises a few pixels as it arrives (sub-pixel, via the per-item
    layer). The pick lands late in the beat: the others dim and the chosen row takes an accent
    ring and, if given, a small label.
    """
    img = ground().copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    items = c["items"][:8]
    pick = c.get("pick")
    # Size the stack to the frame: big rows for a short list, and the whole block (title + rows)
    # centred between the top and the caption band, so a five-item list does not leave the bottom
    # third of the frame empty.
    rh = 150 if len(items) <= 5 else 120 if len(items) <= 6 else 104
    gap, x0, x1 = 26, 90, 990
    tf = font("SemiBold", 70)
    tlines = balanced(d, c.get("title", ""), tf, 900)
    block = len(tlines) * 84 + 70 + len(items) * (rh + gap) - gap
    ttop = max(160, (CAP_CLEAR - 40 - block) / 2 + 60)
    for k, ln in enumerate(tlines):
        centred(d, ttop + k * 84, ln, tf, INK)
    top = ttop + len(tlines) * 84 + 70
    stagger_end = 0.55 if pick is not None else 0.88
    step = (stagger_end - 0.08) / max(1, len(items))
    pa = smoothstep(window(i, n, 0.66, 0.80)) if pick is not None else 0.0
    itf = font("SemiBold", 56 if rh >= 150 else 50 if rh >= 120 else 44)
    for k, text in enumerate(items):
        a = smoothstep(window(i, n, 0.08 + k * step, 0.08 + k * step + 0.14))
        if a <= 0.004:
            continue
        dim = 1.0 - 0.55 * pa if (pick is not None and k != pick) else 1.0
        y = top + k * (rh + gap) + 18 * (1 - a)
        row = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = surface(row, [x0, y, x1, y + rh], radius=26, alpha=int(255 * a * dim))
        if pick == k and pa > 0.004:
            rd.rounded_rectangle([x0 - 3, y - 3, x1 + 3, y + rh + 3], 29,
                                 outline=(*ACCENT, int(255 * pa)), width=5)
        rd.ellipse([x0 + 34, y + rh / 2 - 15, x0 + 64, y + rh / 2 + 15],
                   fill=(*(ACCENT if pick == k and pa > 0.5 else HAIRLINE), int(255 * a * dim)))
        th = itf.getbbox("Hg")[3]
        rd.text((x0 + 92, y + (rh - th) / 2 - 4), text, font=itf, fill=(*INK, int(255 * a * dim)))
        if pick == k and c.get("pick_label") and pa > 0.004:
            lf = font("Bold", 40)
            lw = rd.textlength(c["pick_label"], font=lf)
            bx1, by0 = x1 - 24, y + rh / 2 - 34
            rd.rounded_rectangle([bx1 - lw - 44, by0, bx1, by0 + 68], 34, fill=(*ACCENT, int(255 * pa)))
            rd.text((bx1 - lw - 22, by0 + 10), c["pick_label"], font=lf, fill=(*WHITE, int(255 * pa)))
        layer.alpha_composite(row)
    img.alpha_composite(settle(layer, i, n, cy=(ttop + top + len(items) * (rh + gap)) / 2,
                               amount=0.04))
    return img


def card_prompt(i, n, c):
    """A chat composer: an app label, the prompt typing in, then the send button lighting up.

    Typing is the one place text changes while on screen, and it changes by addition only: a
    character that has appeared never moves.
    """
    img = ground().copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if c.get("title"):
        tf = font("Medium", 60)
        for k, ln in enumerate(balanced(d, c["title"], tf, 880)):
            centred(d, 420 + k * 74, ln, tf, INK)
    box = [80, 700, 1000, 1010]
    ba = 1.0
    bd = surface(layer, box, radius=34, alpha=int(255 * ba))
    lf = font("SemiBold", 32)
    bd.ellipse([box[0] + 36, box[1] + 38, box[0] + 60, box[1] + 62], fill=(*INK, int(255 * ba)))
    bd.text((box[0] + 76, box[1] + 30), c.get("app", "Assistant"), font=lf,
            fill=(*INK_MID, int(255 * ba)))
    text = c["text"]
    typed = int(round(len(text) * window(i, n, 0.12, 0.62)))
    pf = font("Medium", 48)
    lines = wrap(bd, text, pf, box[2] - box[0] - 190)
    shown, left = [], typed
    for ln in lines:
        take = ln[:max(0, left)]
        shown.append(take)
        left -= len(ln) + 1
    for k, ln in enumerate(shown):
        if ln:
            bd.text((box[0] + 40, box[1] + 104 + k * 62), ln, font=pf, fill=(*INK, int(255 * ba)))
    if 0.12 <= i / max(1, n) <= 0.66 and (i // 8) % 2 == 0:
        k = max(0, len([s for s in shown if s]) - 1)
        cx = box[0] + 40 + bd.textlength(shown[k] if shown else "", font=pf) + 4
        bd.rectangle([cx, box[1] + 110 + k * 62, cx + 4, box[1] + 160 + k * 62], fill=(*INK, 255))
    sa = smoothstep(window(i, n, 0.66, 0.74))
    cx, cy, r = box[2] - 70, box[3] - 70, 36
    bd.ellipse([cx - r, cy - r, cx + r, cy + r],
               fill=(*mix(HAIRLINE, ACCENT, sa), int(255 * ba)))
    bd.polygon([(cx, cy - 16), (cx - 13, cy + 2), (cx + 13, cy + 2)], fill=(*WHITE, int(255 * ba)))
    bd.rectangle([cx - 4, cy - 2, cx + 4, cy + 16], fill=(*WHITE, int(255 * ba)))
    img.alpha_composite(settle(layer, i, n, cy=860, amount=0.035))
    return img


# --------------------------------------------------------------------------------------------
# Map
# --------------------------------------------------------------------------------------------

TILE = 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = os.environ.get("VLOG_EDIT_UA", "vlog-edit/1.0 (+https://getedge.cc)")
MAP_BOX = (56, 360, 1024, 1480)
MAP_PAD = 24
PLATE = 1520
_PLATES = {}


def lonlat_px(lon, lat, z):
    s = TILE * 2.0 ** z
    x = (lon + 180.0) / 360.0 * s
    lr = math.radians(lat)
    y = (1.0 - math.log(math.tan(lr) + 1.0 / math.cos(lr)) / math.pi) / 2.0 * s
    return x, y


def fetch_tile(z, x, y):
    """One OSM tile, cached on disk. OpenStreetMap's tile policy asks for a real User-Agent and
    light use; a map card needs a few dozen tiles once, then everything comes from the cache."""
    x %= 2 ** z
    p = os.path.join(CACHE, "tiles", str(z), str(x), f"{y}.png")
    if os.path.isfile(p):
        return Image.open(p).convert("RGB")
    req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y), headers={"User-Agent": UA})
    body = urllib.request.urlopen(req, timeout=30).read()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(body)
    return Image.open(BytesIO(body)).convert("RGB")


def styled_plate(lat, lon, z):
    """A PLATE x PLATE raster centred on (lat, lon) at integer zoom z, restyled to a blue-grey ramp
    so the accent is the only saturated thing on the map."""
    key = (round(lat, 5), round(lon, 5), z)
    if key in _PLATES:
        return _PLATES[key]
    p = os.path.join(CACHE, "plates", f"{key[0]}_{key[1]}_z{z}_{PLATE}.png")
    if os.path.isfile(p):
        _PLATES[key] = Image.open(p).convert("RGB")
        return _PLATES[key]
    cx, cy = lonlat_px(lon, lat, z)
    x0, y0 = cx - PLATE / 2, cy - PLATE / 2
    tx0, ty0 = int(x0 // TILE), int(y0 // TILE)
    tx1, ty1 = int((x0 + PLATE) // TILE), int((y0 + PLATE) // TILE)
    canvas = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            canvas.paste(fetch_tile(z, tx, ty), ((tx - tx0) * TILE, (ty - ty0) * TILE))
    ox, oy = int(x0 - tx0 * TILE), int(y0 - ty0 * TILE)
    raw = canvas.crop((ox, oy, ox + PLATE, oy + PLATE))
    g = ImageOps.autocontrast(ImageOps.grayscale(raw), cutoff=1)
    tinted = ImageOps.colorize(g, black=(0x6E, 0x7C, 0xA0), mid=(0xC6, 0xD0, 0xE8), white=WHITE)
    plate = Image.blend(tinted, Image.new("RGB", tinted.size, WHITE), 0.18)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    plate.save(p)
    _PLATES[key] = plate
    return plate


def load_shape(c):
    """The place as [(lat, lon), ...]. A GeoJSON Polygon/MultiPolygon draws the real boundary; a
    bare lat/lon draws a pin. A neighbourhood is a shape, so prefer the city's own boundary file."""
    if c.get("geojson"):
        g = json.load(open(c["geojson"]))
        if g.get("type") == "FeatureCollection":
            g = g["features"][0]
        if g.get("type") == "Feature":
            g = g["geometry"]
        coords = g["coordinates"]
        while isinstance(coords[0][0], list):
            coords = coords[0]
        return [(float(lat), float(lon)) for lon, lat in coords]
    return [(float(c["lat"]), float(c["lon"]))]


def map_zooms(c, pts, vw, vh):
    """End zoom: the shape fills about 60% of the viewport. Start: 4.4 levels out (a city)."""
    if "zoom_end" in c:
        z1 = float(c["zoom_end"])
    elif len(pts) < 3:
        z1 = 15.5
    else:
        z1 = 18.0
        while z1 > 3:
            xs, ys = zip(*[lonlat_px(lon, lat, z1) for lat, lon in pts])
            if max(xs) - min(xs) <= 0.6 * vw and max(ys) - min(ys) <= 0.6 * vh:
                break
            z1 -= 0.1
    z0 = float(c.get("zoom_start", z1 - 4.4))
    return z0, z1


def card_map(i, n, c):
    """The map fills the frame under a title and pushes from the city down to the block grid.

    One styled plate per integer zoom, crossfaded across the half-zoom boundary, keeps every frame
    inside a 0.7x..1.5x resample. The boundary is drawn in continuous-zoom pixels so it tracks the
    push exactly instead of being resampled with the raster.
    """
    img = ground().copy()
    pts = load_shape(c)
    flat = sum(p[0] for p in pts) / len(pts)
    flon = sum(p[1] for p in pts) / len(pts)
    vx0, vy0 = MAP_BOX[0] + MAP_PAD, MAP_BOX[1] + MAP_PAD
    vw, vh = MAP_BOX[2] - MAP_BOX[0] - 2 * MAP_PAD, MAP_BOX[3] - MAP_BOX[1] - 2 * MAP_PAD
    z0, z1 = map_zooms(c, pts, vw, vh)
    z = z0 + (z1 - z0) * push(window(i, n, 0.0, 1.0))

    lo = int(math.floor(z))
    w_hi = smoothstep((z - (lo + 0.5)) / 0.30 + 0.5)
    view = None
    for zk, wt in ((lo, 1 - w_hi), (lo + 1, w_hi)):
        if wt <= 0.003:
            continue
        s = 2.0 ** (z - zk)
        bw, bh = vw / s, vh / s
        if bw > PLATE or bh > PLATE:
            continue
        cc = PLATE / 2
        fr = styled_plate(flat, flon, zk).resize((vw, vh), Image.BICUBIC,
                                                 box=(cc - bw / 2, cc - bh / 2, cc + bw / 2, cc + bh / 2))
        view = fr if view is None else Image.blend(view, fr, wt)
    view = (view or Image.new("RGB", (vw, vh), (0xEF, 0xF2, 0xFA))).convert("RGBA")

    fx, fy = lonlat_px(flon, flat, z)
    ov = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    if len(pts) >= 3:
        poly = [(vw / 2 + lonlat_px(lon, lat, z)[0] - fx, vh / 2 + lonlat_px(lon, lat, z)[1] - fy)
                for lat, lon in pts]
        od.polygon(poly, fill=(*ACCENT, 46))
        od.line(poly + [poly[0]], fill=(*ACCENT, 255), width=5, joint="curve")
        da = 1.0 - smoothstep((z - z0 - 0.9) / 1.3)
    else:
        da = 1.0
    if da > 0.01:
        r = 11
        od.ellipse([vw / 2 - r - 5, vh / 2 - r - 5, vw / 2 + r + 5, vh / 2 + r + 5],
                   fill=(255, 255, 255, int(235 * da)))
        od.ellipse([vw / 2 - r, vh / 2 - r, vw / 2 + r, vh / 2 + r], fill=(*ACCENT, int(255 * da)))
    view = Image.alpha_composite(view, ov)

    ad = ImageDraw.Draw(view)
    af = font("Medium", 24)
    att = c.get("attribution", "Map: OpenStreetMap")
    aw = ad.textlength(att, font=af)
    ad.rounded_rectangle([vw - 20 - aw - 40, vh - 76, vw - 20, vh - 20], 18,
                         fill=(*SURFACE, 236), outline=(*HAIRLINE, 236), width=2)
    ad.text((vw - 20 - aw - 20, vh - 62), att, font=af, fill=(*INK_MID, 255))

    mask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, vw - 1, vh - 1], 24, fill=255)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    surface(layer, MAP_BOX, radius=40)
    layer.paste(view.convert("RGB"), (vx0, vy0), mask)
    img.alpha_composite(layer)

    d = ImageDraw.Draw(img)
    centred(d, 150, c.get("title", ""), font("Bold", 92), INK)
    if c.get("sub"):
        centred(d, 262, c["sub"], font("Medium", 50), INK_MID, smoothstep(window(i, n, 0.05, 0.16)))
    return img


CARDS = {"stat": card_stat, "list": card_list, "prompt": card_prompt, "map": card_map}


# --------------------------------------------------------------------------------------------
# Captions, hook, outro
# --------------------------------------------------------------------------------------------

_CAP = {}


def caption(words, active, light, keys):
    """One caption line in the band: spoken words full, upcoming words dim, key words on an accent
    box once spoken. Navy ink on light shots, white with a soft shadow on footage. Box padding is
    reserved in the layout, so nothing shifts when a box arrives."""
    key = (tuple(words), active, light)
    if key in _CAP:
        return _CAP[key]
    caps = [w.upper() for w in words]
    iskey = [w.strip(".,!?;:'\"").lower() in keys for w in words]
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    size = 80
    while True:
        fnt = font("ExtraBold", size)
        sp = probe.textlength(" ", font=fnt)
        widths = [probe.textlength(w, font=fnt) for w in caps]
        total = sum(widths) + sp * (len(caps) - 1) + 36 * sum(iskey)
        if total <= W - 144 or size <= 52:
            break
        size -= 4
    asc, desc = fnt.getmetrics()
    top = CAP_Y - (asc + desc) / 2
    full = INK if light else WHITE
    dim = 0.34 if light else 0.52
    text = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    boxes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td, bd = ImageDraw.Draw(text), ImageDraw.Draw(boxes)
    x = (W - total) / 2
    for k, (w, cw) in enumerate(zip(caps, widths)):
        spoken = k <= active
        if iskey[k]:
            x += 18
        if spoken and iskey[k]:
            bd.rounded_rectangle([x - 14, top - 2, x + cw + 14, top + asc + desc + 6], 14,
                                 fill=(*ACCENT, 255))
            td.text((x, top), w, font=fnt, fill=(*WHITE, 255))
        else:
            td.text((x, top), w, font=fnt, fill=(*full, 255 if spoken else int(255 * dim)))
        x += cw + sp + (18 if iskey[k] else 0)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(boxes)
    img.alpha_composite(text if light else text_shadowed(text))
    _CAP[key] = img
    return img


_SUB = {}


def subtitle(text, light):
    """The translation line under the caption: smaller, one weight lighter, whole line at once.
    The spoken words stay the hero; this line only says what they mean."""
    key = (text, light)
    if key in _SUB:
        return _SUB[key]
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    size = 54
    while d.textlength(text, font=font("SemiBold", size)) > W - 144 and size > 36:
        size -= 2
    lines = balanced(d, text, font("SemiBold", size), W - 144)
    y = SUB_Y
    for ln in lines[:2]:
        centred(d, y, ln, font("SemiBold", size), INK_MID if light else WHITE, 1.0 if light else 0.95)
        y += size + 10
    img = t if light else text_shadowed(t, strength=0.75, blur=6, dy=3)
    _SUB[key] = img
    return img


def shade():
    """A soft dark ramp under the caption band, for footage only.

    White type with a shadow reads on a face; on bright sky or a white wall it vanishes. A ramp from
    clear to 55% black across the bottom third is what every phone app does, and it never shows on
    a card because it is only enabled outside card windows.
    """
    g = Image.new("L", (1, H), 0)
    top = CAP_CLEAR - 260
    for y in range(H):
        u = clamp01((y - top) / (H - top))
        g.putpixel((0, y), int(140 * smoothstep(u)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.putalpha(g.resize((W, H)))
    return img


def hook(text, kicker=""):
    """The opening line in the caption face, under the chin and above the caption band, no scrim.
    It is the thumbnail, so while it is up no caption runs under it."""
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    tf = font("ExtraBold", 96)
    lines = wrap(d, text.upper(), tf, W - 160)
    y = 1110 - max(0, len(lines) - 3) * 112
    if kicker:
        centred(d, y, kicker, font("SemiBold", 40), WHITE, 0.92)
        y += 70
    for ln in lines:
        centred(d, y, ln, tf, WHITE)
        y += 112
    return text_shadowed(t, strength=0.6, blur=9, dy=5)


def outro_frame(still, i, n, text):
    """The held last frame with the closing line. The still pushes in sub-pixel so it is not a
    freeze, and the line fades in once and stays."""
    s = 1.0 + 0.035 * window(i, n, 0.0, 1.0)
    cx, cy = W / 2, H * 0.45
    img = still.transform((W, H), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s),
                          resample=Image.BICUBIC).convert("RGBA")
    dark = Image.new("RGBA", (W, H), (0, 0, 0, int(90 * smoothstep(window(i, n, 0.0, 0.2)))))
    img.alpha_composite(dark)
    if text:
        t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(t)
        tf = font("ExtraBold", 84)
        lines = balanced(d, text.upper(), tf, W - 160)
        a = smoothstep(window(i, n, 0.05, 0.25))
        for k, ln in enumerate(lines):
            centred(d, 1180 + k * 100, ln, tf, WHITE, a)
        img.alpha_composite(text_shadowed(t))
    return img
