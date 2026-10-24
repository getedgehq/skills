"""Public link-preview cover (1200x630 JPEG, under 100 KB so WhatsApp shows it) from a fixed template. Needs Pillow.

The same function runs on the creator's device (to show the exact cover before approval) and on the server (to
serve og:image). Input is only a validated teaser: a template name and at most one number.
"""
from __future__ import annotations

import io
from pathlib import Path

from share_schema import PRODUCT_NAME, SHARE_DIR, teaser_lines, validate_teaser

W, H = 1200, 630
PAPER, INK, MUTED, GREEN = (245, 243, 235), (22, 37, 30), (89, 104, 95), (49, 95, 67)
FONT = SHARE_DIR.parent / "assets" / "InterVariable-subset.woff2"
MEADOW = SHARE_DIR / "static" / "meadow.webp"


def _font(size: int, weight: int):
    from PIL import ImageFont
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([32 if size >= 40 else 14, weight])
    except Exception:
        pass
    return f


def _fit(draw, text: str, max_w: int, size: int, weight: int):
    while size > 24:
        f = _font(size, weight)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return _font(size, weight)


def render_cover(teaser: dict) -> bytes:
    from PIL import Image, ImageDraw
    validate_teaser(teaser)
    line1, line2 = teaser_lines(teaser)
    im = Image.new("RGB", (W, H), PAPER)
    meadow = Image.open(MEADOW).convert("RGBA")
    meadow = meadow.resize((W, round(meadow.height * W / meadow.width)))
    im.paste(meadow, (0, H - 250), meadow)
    d = ImageDraw.Draw(im)
    x = 72
    d.text((x, 64), PRODUCT_NAME, font=_font(34, 500), fill=MUTED)
    big = _fit(d, line1, W - 2 * x, 112, 450)
    d.text((x, 118), line1, font=big, fill=INK)
    d.text((x, 262), line2, font=_fit(d, line2, W - 2 * x, 50, 450), fill=GREEN)
    # Footer: the Edge arch and "made with Edge", on the cream above the hills.
    fy = 352
    d.pieslice((x, fy, x + 34, fy + 34), 180, 360, fill=INK)
    d.rectangle((x, fy + 17, x + 34, fy + 22), fill=INK)
    d.text((x + 46, fy - 4), "made with Edge · getedge.cc", font=_font(26, 450), fill=MUTED)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    return buf.getvalue()


def write_cover(teaser: dict, path: Path) -> Path:
    path.write_bytes(render_cover(teaser))
    return path
