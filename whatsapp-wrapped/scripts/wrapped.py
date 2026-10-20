#!/usr/bin/env python3
"""WhatsApp Wrapped: a recap of a WhatsApp "Export chat" file, made fully on this device.

Usage:
  python3 wrapped.py <export.txt|export.zip> [--out DIR] [--no-png] [--no-words]
                     [--date-order dmy|mdy|ymd] [--title "Name"] [--json] [--share-safe]
  python3 wrapped.py --personal <ChatStorage.sqlite | folder of exports> [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                     [--me "Your Name"] [--owner "Fede"] [--tz auto|Europe/Berlin] [--out DIR] [--share-safe] [--json]

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
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from parse import parse_file  # noqa: E402
import render  # noqa: E402
from render import build_cards, build_page, card_document  # noqa: E402
from stats import compute, share_safe_words  # noqa: E402
from personal import NO_MAC_DB, compute_personal, load_desktop_db, load_exports, localize, mac_desktop_db  # noqa: E402
from render_personal import build_personal_cards, build_personal_page, share_safe_chat  # noqa: E402

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
    ap.add_argument("export", nargs="?", help="WhatsApp export: the .txt or the .zip from 'Export chat'")
    ap.add_argument("--personal", metavar="SOURCE", help="personal edition across all your chats: 'mac' (finds the "
                    "WhatsApp Desktop database on this Mac and reads a temporary copy), a ChatStorage.sqlite file, or a "
                    "folder of exports")
    ap.add_argument("--since", type=date.fromisoformat, help="personal: first day to include (default: January 1 of "
                    "the latest year in the data, so you get this year so far)")
    ap.add_argument("--all-time", action="store_true", help="personal: include everything in the source")
    ap.add_argument("--until", type=date.fromisoformat, help="personal: last day to include")
    ap.add_argument("--me", help="personal, folder of exports: your name as it appears in the exports")
    ap.add_argument("--owner", default="", help="personal: your first name for the cards (default: 'My')")
    ap.add_argument("--tz", default="auto", help="personal, database: time zone for hours and days, or 'auto' "
                    "to estimate it week by week from your quiet hours (default)")
    ap.add_argument("--theme", choices=sorted(render.THEMES), default="green",
                    help="card colours: green (default, Edge meadow greens) or edge (Edge blue)")
    ap.add_argument("--share-cards", action="store_true", help="write ONLY share-safe PNG cards into --out: initials "
                    "instead of names, no page, no stats file, no word chips unless --words")
    ap.add_argument("--words", action="store_true", help="with --share-cards: include word chips, minus anything that "
                    "looks like a name, place, number or email")
    ap.add_argument("--open", action="store_true", help="open the finished page in the default browser")
    ap.add_argument("--share-safe", action="store_true", help="replace everyone's name with 'Person #n' and initials")
    ap.add_argument("--out", default=None, help="output folder (default: ./whatsapp-wrapped-<chat>)")
    ap.add_argument("--no-png", action="store_true", help="skip PNG cards, write only the HTML page")
    ap.add_argument("--no-words", action="store_true", help="leave top words off the cards (more private to share)")
    ap.add_argument("--date-order", choices=["dmy", "mdy", "ymd"], help="override day/month order detection")
    ap.add_argument("--title", help="chat name to show (default: from the file name)")
    ap.add_argument("--json", action="store_true", help="also write stats.json")
    a = ap.parse_args(argv)
    render.set_theme(a.theme)
    if a.share_cards:
        a.share_safe, a.json, a.no_png = True, False, False
    if a.personal:
        return run_personal(a)
    if not a.export:
        ap.error("pass an export file, or --personal SOURCE")

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

    if a.share_safe:
        s = share_safe_chat(s)
    if a.share_cards:
        s["top_words"] = share_safe_words(s["top_words"], s.get("proper_words", [])) if a.words else []
        return write_share_cards(build_cards(s, show_words=a.words), Path(a.out or "whatsapp-wrapped-share-cards"))
    cards = build_cards(s, show_words=not a.no_words)
    png_names = [f"{i:02d}-{key}.png" for i, (key, _) in enumerate(cards, 1)]
    engine = ""
    if not a.no_png:
        engine = render_pngs([(n, card_document(h)) for n, (_, h) in zip(png_names, cards)], out / "cards")
    page = build_page(s, cards, png_names if engine else None)
    (out / "wrapped.html").write_text(page, encoding="utf-8")
    open_page(a, out)
    if a.json:
        (out / "stats.json").write_text(json.dumps(s, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"chat: {s['title']} ({chat.platform}, dates read as {chat.date_order}), {s['total_messages']:,} messages, "
          f"{s['people_count']} people, {s['span_days']} days")
    print(f"page: {out / 'wrapped.html'}")
    if engine:
        print(f"cards ({engine}): " + ", ".join(str(out / 'cards' / n) for n in png_names))
        print(f"share: post {out / 'cards' / png_names[-1]} (the summary) or any card. "
              + ("Names are hidden on these cards." if a.share_safe else
                 "Everyone in the chat appears by name; add --share-safe for Person #1 and initials instead."))
    return 0


def write_share_cards(cards, out: Path) -> int:
    """Only PNGs, names replaced, nothing else on disk."""
    out.mkdir(parents=True, exist_ok=True)
    names = [f"{i:02d}-{key}.png" for i, (key, _) in enumerate(cards, 1)]
    engine = render_pngs([(n, card_document(h)) for n, (_, h) in zip(names, cards)], out)
    if not engine:
        print("error: share cards need a headless browser: pip install playwright && playwright install chromium", file=sys.stderr)
        return 3
    print(f"share cards ({engine}): {len(names)} PNGs in {out}. Names are initials; no message text.")
    print(f"share: post {out / names[-1]} (the summary) or any card.")
    return 0


def open_page(a, out: Path) -> None:
    if getattr(a, "open", False):
        import webbrowser
        webbrowser.open((out / "wrapped.html").resolve().as_uri())


def run_personal(a) -> int:
    src = mac_desktop_db() if a.personal.lower() in ("mac", "desktop") else Path(a.personal)
    try:
        if a.personal.lower() in ("mac", "desktop") and not src.exists():
            print(NO_MAC_DB, file=sys.stderr)
            return 2
        if src.is_dir():
            recs, info = load_exports(src, me=a.me, date_order=a.date_order)
        elif src.is_file():
            recs, info = load_desktop_db(src)
        else:
            recs = None
    except (PermissionError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if recs is None:
        print(f"error: {src} is neither a ChatStorage.sqlite file nor a folder of exports", file=sys.stderr)
        return 2
    if not recs:
        print("error: no messages found in that source", file=sys.stderr)
        return 2
    zones = localize(recs, a.tz)
    if a.all_time:
        a.since = None
    elif a.since is None:
        a.since = date(max(r.ts for r in recs).year, 1, 1)
    try:
        s = compute_personal(recs, since=a.since, until=a.until, name_tokens=info.get("name_tokens"), owner=a.owner)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    out = Path(a.out or ("whatsapp-wrapped-personal" + ("-share-cards" if a.share_cards else "-share-safe" if a.share_safe else "")))
    if not a.share_cards:
        (out / "cards").mkdir(parents=True, exist_ok=True)
    if a.share_cards:
        s["top_words"] = share_safe_words(s["top_words"], s.get("proper_words", [])) if a.words else []
        return write_share_cards(build_personal_cards(s, owner=a.owner, safe=True), out)
    cards = build_personal_cards(s, owner=a.owner, safe=a.share_safe)
    png_names = [f"{i:02d}-{key}.png" for i, (key, _) in enumerate(cards, 1)]
    engine = "" if a.no_png else render_pngs([(n, card_document(h)) for n, (_, h) in zip(png_names, cards)], out / "cards")
    notes = ("Hours and days use local time estimated week by week from your quiet hours." if zones and a.tz == "auto"
             else f"Hours and days use {a.tz} time." if zones else "Hours and days are as written in the exports.")
    page = build_personal_page(s, cards, png_names if engine else None, owner=a.owner, safe=a.share_safe, notes=notes)
    (out / "wrapped.html").write_text(page, encoding="utf-8")
    open_page(a, out)
    if a.json:
        info_out = {k: v for k, v in info.items() if k != "name_tokens"}
        (out / "stats.json").write_text(json.dumps({"source": info_out, "time_zones_weeks": zones, **s}, indent=2,
                                                   ensure_ascii=False, default=str), encoding="utf-8")
    print(f"personal ({info['source']}): history from {s['history_start']}, this edition {s['first']} to {s['last']}")
    print(f"messages: {s['total']:,} ({s['sent']:,} sent, {s['received']:,} received) in {s['chats']:,} chats "
          f"({s['people_chats']:,} one-to-one, {s['group_chats']:,} groups); left out: {s['excluded_groups']:,} groups you "
          f"barely write in ({s['excluded_group_messages']:,} messages), {info.get('skipped_chats') or 'nothing else'}")
    if zones:
        print("time zones (weeks): " + ", ".join(f"{z} {n}" for z, n in sorted(zones.items(), key=lambda kv: -kv[1])))
    print(f"page: {out / 'wrapped.html'}")
    if engine:
        print(f"cards ({engine}): {len(png_names)} in {out / 'cards'}")
        print(f"share: post {out / 'cards' / png_names[-1]} (the summary) or any card. "
              + ("Names are hidden on these cards." if a.share_safe else
                 "These cards show friends' names; add --share-safe for a version with Person #1 and initials."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
