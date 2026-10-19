#!/usr/bin/env python3
"""WhatsApp Wrapped: a recap of a WhatsApp "Export chat" file, made fully on this device.

Usage:
  python3 wrapped.py <export.txt|export.zip> [--out DIR] [--no-png] [--no-words]
                     [--date-order dmy|mdy|ymd] [--title "Name"] [--json]

Writes:
  DIR/wrapped.html        self-contained page (all cards + table), no network requests
  DIR/cards/NN-*.png      1080x1920 story cards (needs Playwright or a local Chrome/Chromium)
  DIR/stats.json          only with --json (contains names and top words)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from parse import parse_file  # noqa: E402
from render import build_cards, build_page, card_document  # noqa: E402
from stats import compute  # noqa: E402

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser",
]
OFFLINE_ARGS = ["--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost", "--disable-background-networking",
                "--disable-component-update", "--disable-sync", "--no-first-run", "--disable-default-apps"]


def render_pngs(docs: list[tuple[str, str]], out_dir: Path) -> str:
    """Render each (filename, html) to PNG. Returns the engine used, or '' if none was available."""
    tmp = Path(tempfile.mkdtemp(prefix="wa-wrapped-"))
    try:
        files = []
        for name, doc in docs:
            f = tmp / (Path(name).stem + ".html")
            f.write_text(doc, encoding="utf-8")
            files.append((f, out_dir / name))
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
            with sync_playwright() as p:
                browser = p.chromium.launch(args=OFFLINE_ARGS)
                page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
                # Belt and braces: refuse every request that is not the local file or inline data.
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(("file:", "data:")) else route.abort())
                for src, dst in files:
                    page.goto(src.as_uri())
                    page.evaluate("document.fonts.ready")
                    page.wait_for_timeout(150)
                    for attempt in range(3):  # headless screenshots can fail transiently under load
                        try:
                            page.screenshot(path=str(dst), clip={"x": 0, "y": 0, "width": 1080, "height": 1920})
                            break
                        except Exception:
                            if attempt == 2:
                                raise
                            page.wait_for_timeout(500)
                browser.close()
            return "playwright"
        except Exception as exc:  # fall back to a local browser binary
            pw_error = exc
            if os.environ.get("WRAPPED_DEBUG"):
                print(f"playwright: {exc!r}", file=sys.stderr)
        for cand in CHROME_CANDIDATES:
            exe = cand if os.path.isabs(cand) and os.path.exists(cand) else shutil.which(cand)
            if not exe:
                continue
            for src, dst in files:
                subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                                "--window-size=1080,1920", "--virtual-time-budget=1500", f"--screenshot={dst}", *OFFLINE_ARGS,
                                f"--user-data-dir={tmp / 'profile'}", src.as_uri()],
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            if all(dst.exists() for _, dst in files):
                return Path(exe).name
        print(f"note: no headless browser found for PNG cards ({pw_error.__class__.__name__}). "
              "The HTML page still has every card. Install one with: pip install playwright && playwright install chromium",
              file=sys.stderr)
        return ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", help="WhatsApp export: the .txt or the .zip from 'Export chat'")
    ap.add_argument("--out", default=None, help="output folder (default: ./whatsapp-wrapped-<chat>)")
    ap.add_argument("--no-png", action="store_true", help="skip PNG cards, write only the HTML page")
    ap.add_argument("--no-words", action="store_true", help="leave top words off the cards (more private to share)")
    ap.add_argument("--date-order", choices=["dmy", "mdy", "ymd"], help="override day/month order detection")
    ap.add_argument("--title", help="chat name to show (default: from the file name)")
    ap.add_argument("--json", action="store_true", help="also write stats.json")
    a = ap.parse_args(argv)

    chat = parse_file(a.export, date_order=a.date_order)
    if a.title:
        chat.title = a.title
    if not chat.messages:
        print("error: no messages found. Use WhatsApp > chat > More > Export chat, then pass the .txt or .zip.", file=sys.stderr)
        return 2
    if len(chat.messages) < 100:
        print(f"note: only {len(chat.messages)} messages. The recap works, but it gets fun from a few hundred up.", file=sys.stderr)
    s = compute(chat)
    slug = "".join(c if c.isalnum() else "-" for c in chat.title.lower()).strip("-")[:40] or "chat"
    out = Path(a.out or f"whatsapp-wrapped-{slug}")
    (out / "cards").mkdir(parents=True, exist_ok=True)

    cards = build_cards(s, show_words=not a.no_words)
    png_names = [f"{i:02d}-{key}.png" for i, (key, _) in enumerate(cards, 1)]
    engine = ""
    if not a.no_png:
        engine = render_pngs([(n, card_document(h)) for n, (_, h) in zip(png_names, cards)], out / "cards")
    page = build_page(s, cards, png_names if engine else None)
    (out / "wrapped.html").write_text(page, encoding="utf-8")
    if a.json:
        (out / "stats.json").write_text(json.dumps(s, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"chat: {s['title']} ({chat.platform}, dates read as {chat.date_order}), {s['total_messages']:,} messages, "
          f"{s['people_count']} people, {s['span_days']} days")
    print(f"page: {out / 'wrapped.html'}")
    if engine:
        print(f"cards ({engine}): " + ", ".join(str(out / 'cards' / n) for n in png_names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
