#!/usr/bin/env python3
"""hook_png.py OUT HOOK SIZE [--after WORD=IMG ...] [--strip IMG]

1080x1920 transparent hook layer for frame 0: soft dark top scrim, white bold centered
lines starting at y=285, an inline icon right after any WORD (a logo or a flag, the
"signal"), and an optional logo strip under the last line. SIZE is a ceiling: the text
shrinks until the widest line, icons included, fits the frame.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

W, H = 1080, 1920
out, hook, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
after, strip = {}, None
a = sys.argv[4:]
while a:
    k = a.pop(0)
    if k == "--after":
        w, p = a.pop(0).split("=", 1); after[w] = p
    elif k == "--strip":
        strip = a.pop(0)
MAXW = W - 174
lines = [l.strip() for l in hook.split("\n") if l.strip()]
d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))


def line_w(ln, f, sz):
    """text width plus inline icons, so a line with a logo still fits the frame"""
    sp_ = d.textlength(" ", font=f); w = d.textlength(ln, font=f)
    for wd in ln.split(" "):
        if wd in after:
            im = Image.open(after[wd]); w += sp_ * 0.8 + im.width * int(sz * 0.95) / im.height
    return w


while True:  # SIZE is the ceiling; shrink until the widest line fits
    hf = rmconf.bold(ImageFont.truetype(rmconf.hook_font(), size))
    if size <= 40 or max(line_w(l, hf, size) for l in lines) <= MAXW:
        break
    size -= 1
img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); px = img.load()
bott = int(H * 0.50)
for yy in range(bott):
    al = int(200 * ((bott - yy) / bott) ** 1.3)
    for xx in range(W):
        px[xx, yy] = (6, 6, 6, al)
asc = hf.getmetrics()[0]; sp = d.textlength(" ", font=hf)
icon_h = int(size * 0.95)


def icon(p):
    im = Image.open(p).convert("RGBA")
    return im.resize((int(im.width * icon_h / im.height), icon_h), Image.LANCZOS)


y = 285
for ln in lines:
    parts = []  # (kind, value, width)
    for i, wd in enumerate(ln.split(" ")):
        if i:
            parts.append(("s", None, sp))
        parts.append(("t", wd, d.textlength(wd, font=hf)))
        if wd in after:
            ic = icon(after[wd]); parts += [("s", None, sp * 0.8), ("i", ic, ic.width)]
    x = (W - sum(p[2] for p in parts)) / 2
    for k, v, wdt in parts:
        if k == "t":
            d.text((x, y), v, font=hf, fill=(255, 255, 255, 255))
        elif k == "i":
            img.alpha_composite(v, (int(x), int(y + asc * 0.55 - v.height / 2)))
        x += wdt
    y += size
if strip:
    s = Image.open(strip).convert("RGBA")
    img.alpha_composite(s, ((W - s.width) // 2, y + int(size * 0.45)))
img.save(out); print(out, "size", size, "bottom", y)
