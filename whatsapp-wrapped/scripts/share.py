#!/usr/bin/env python3
"""Hosted share link: the ONLY file in this skill that sends anything over a network.

It turns the local stats into the restricted share schema (numbers, enums, allowlisted emojis, month dates, no
participant identifiers), encrypts that with AES-GCM-256 on this device, and uploads only the ciphertext plus a
creator-approved public cover. The key goes in the link's #fragment, which browsers never send to the server.
Publishing needs two approvals typed by a person at this terminal; an agent cannot approve for them.

Usage:
  python3 share.py <export.txt|export.zip> [--me "Your Name"] [--cover messages|streak|generic] [--expires 24h|7d|30d]
  python3 share.py --personal <mac | ChatStorage.sqlite | folder> [--since YYYY-MM-DD] [--all-time] [--me NAME] ...
  python3 share.py ... --dry-run          write the payload and covers locally, no prompts, no upload
  python3 share.py --delete <link or id>  delete a link you made (the delete secret is kept on this device)

Needs: `pip install cryptography pillow` (encryption, and the cover image you approve).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from share_schema import CONFIG, PRODUCT_NAME, SCHEMA, describe, teaser_lines, validate, validate_teaser  # noqa: E402

LINKS_FILE = Path(os.environ.get("CHAT_REPLAY_HOME", Path.home() / ".chat-replay")) / "links.json"
ID_RE = re.compile(r"^[A-Za-z0-9_-]{22}$")


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


# ---------------------------------------------------------------- local stats -> share payload

def build_payload(a) -> dict:
    """Parse and compute locally, then keep only what the share schema allows. Never prints chat content."""
    from parse import parse_file
    from stats import compute
    from share_schema import from_chat_stats, from_personal_stats
    if a.personal:
        from personal import compute_personal, load_desktop_db, load_exports, localize, mac_desktop_db
        src = mac_desktop_db() if a.personal.lower() in ("mac", "desktop") else Path(a.personal)
        recs, info = load_exports(src, me=a.me, date_order=a.date_order) if src.is_dir() else load_desktop_db(src)
        if not recs:
            raise SystemExit("error: no messages found in that source")
        localize(recs, a.tz)
        since = None if a.all_time else (a.since or date(max(r.ts for r in recs).year, 1, 1))
        s = compute_personal(recs, since=since, until=a.until, name_tokens=info.get("name_tokens"))
        return from_personal_stats(s)
    chat = parse_file(a.export, date_order=a.date_order)
    senders = {m.sender for m in chat.messages if m.kind != "call"}
    if not senders:
        raise SystemExit("error: no messages found. Use WhatsApp > chat > Export chat, then pass the .txt or .zip.")
    if len(senders) > 2:
        return from_chat_stats(compute(chat), "group")
    # Two-person chat: the link may only show the creator's own stats.
    if not a.me or a.me not in senders:
        raise SystemExit('error: this is a two-person chat. Pass --me "<your name as it appears in the export>"; '
                         "the link then shows only your own stats.")
    chat.messages = [m for m in chat.messages if m.sender == a.me]
    return from_chat_stats(compute(chat), "duo")


def make_teaser(payload: dict, cover: str) -> dict:
    if cover == "messages":
        return validate_teaser({"tpl": "messages", "n": payload["cards"][0]["n"]})
    if cover == "streak":
        st = next((c for c in payload["cards"] if c["t"] == "streak"), None)
        if st:
            return validate_teaser({"tpl": "streak", "days": st["days"]})
    return validate_teaser({"tpl": "generic"})


# ---------------------------------------------------------------- approvals (a person at a terminal)

def tty_ask(prompt: str) -> str:
    """Read an answer from the controlling terminal, never from stdin, so a piped 'yes' cannot approve."""
    try:
        fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
    except OSError:
        raise SystemExit("error: publishing needs two approvals typed by a person at a terminal, and there is no "
                         "terminal here. Run this command yourself in a terminal (in Claude Code: prefix it with !).")
    try:
        os.write(fd, prompt.encode())
        buf = b""
        while not buf.endswith((b"\n", b"\r")):
            chunk = os.read(fd, 256)
            if not chunk:
                break
            buf += chunk
        return buf.decode(errors="replace").strip()
    finally:
        os.close(fd)


# ---------------------------------------------------------------- network (the only egress)

def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))  # direct connection, no env proxies


def check_server(server: str) -> str:
    u = urllib.parse.urlparse(server)
    local = u.hostname in ("127.0.0.1", "localhost", "::1")
    if u.scheme != "https" and not (local and u.scheme == "http"):
        raise SystemExit("error: the server must use https")
    return server.rstrip("/")


def http(method: str, url: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json", "User-Agent": "chat-replay-share/1", **(headers or {})})
    try:
        with _opener().open(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def encrypt(payload: dict) -> tuple[bytes, bytes, bytes]:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise SystemExit("error: encryption needs the cryptography package: pip install cryptography")
    plain = json.dumps(validate(payload), ensure_ascii=False, separators=(",", ":")).encode()
    key, iv = AESGCM.generate_key(bit_length=256), secrets.token_bytes(12)
    return key, iv, AESGCM(key).encrypt(iv, plain, SCHEMA["aad"].encode())


def publish(payload: dict, teaser: dict, server: str, ttl: str) -> dict:
    """Encrypt and upload. Returns {link, id, expires, delete_secret}. Callers must have the two approvals first."""
    key, iv, ct = encrypt(payload)
    delete_secret = secrets.token_urlsafe(32)
    status, res = http("POST", f"{server}/api/shares", {
        "v": SCHEMA["version"], "ct": b64u(ct), "iv": b64u(iv), "ttl": ttl, "teaser": teaser,
        "del": hashlib.sha256(delete_secret.encode()).hexdigest()})
    if status != 201 or not ID_RE.match(str(res.get("id", ""))):
        raise SystemExit(f"error: upload failed ({status}): {res.get('error', 'no details')}")
    save_link(res["id"], server, delete_secret, res.get("expires"))
    return {"id": res["id"], "expires": res.get("expires"), "delete_secret": delete_secret,
            "link": f"{server}/s/{res['id']}#k={b64u(key)}"}


def save_link(share_id: str, server: str, delete_secret: str, expires) -> None:
    LINKS_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    links = json.loads(LINKS_FILE.read_text()) if LINKS_FILE.exists() else {}
    links[share_id] = {"server": server, "delete_secret": delete_secret, "expires": expires,
                       "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    fd = os.open(LINKS_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(links, f, indent=1)


def delete(ref: str, server: str | None) -> int:
    share_id = ref.split("#")[0].rstrip("/").split("/")[-1]
    if not ID_RE.match(share_id):
        raise SystemExit("error: that is not a share link or id")
    links = json.loads(LINKS_FILE.read_text()) if LINKS_FILE.exists() else {}
    rec = links.get(share_id)
    if not rec:
        raise SystemExit(f"error: no delete secret for {share_id} in {LINKS_FILE}. Only the device that made the "
                         "link can delete it; anyone can report it from the page.")
    server = check_server(server or rec["server"])
    status, res = http("DELETE", f"{server}/api/shares/{share_id}", headers={"X-Delete-Secret": rec["delete_secret"]})
    if status in (200, 404, 410):
        links.pop(share_id, None)
        LINKS_FILE.write_text(json.dumps(links, indent=1))
        print(f"deleted: {share_id} (the encrypted stats and the public cover are gone from the server)")
        print("note: apps that already showed the preview may keep their cached copy of the cover for a while.")
        return 0
    print(f"error: delete failed ({status}): {res.get('error', 'no details')}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------- CLI

def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", nargs="?", help="WhatsApp export (.txt or .zip) for the chat edition")
    ap.add_argument("--personal", metavar="SOURCE", help="personal edition: mac, a ChatStorage.sqlite, or a folder")
    ap.add_argument("--me", help="your name as it appears in the export (needed for two-person chats)")
    ap.add_argument("--since", type=date.fromisoformat)
    ap.add_argument("--until", type=date.fromisoformat)
    ap.add_argument("--all-time", action="store_true")
    ap.add_argument("--tz", default="auto")
    ap.add_argument("--date-order", choices=["dmy", "mdy", "ymd"])
    ap.add_argument("--cover", choices=sorted(SCHEMA["teaser_templates"]), default="messages",
                    help="public link-preview cover: one number (messages or streak) or generic (no stats)")
    ap.add_argument("--expires", choices=sorted(CONFIG["expiry_options"]), default=CONFIG["default_expiry"])
    ap.add_argument("--server", default=os.environ.get("CHAT_REPLAY_SERVER", CONFIG["default_server"]))
    ap.add_argument("--out", default="chat-replay-share", help="local folder for the payload and cover images")
    ap.add_argument("--dry-run", action="store_true", help="write the payload and covers locally; do not upload")
    ap.add_argument("--delete", metavar="LINK_OR_ID", help="delete a link this device made")
    return ap


def main(argv=None) -> int:
    ap = parser()
    a = ap.parse_args(argv)
    if a.delete:
        return delete(a.delete, a.server if "--server" in (argv or sys.argv) else None)
    if not a.export and not a.personal:
        ap.error("pass an export file, or --personal SOURCE")
    server = check_server(a.server)

    payload = build_payload(a)
    teaser = make_teaser(payload, a.cover)
    generic = validate_teaser({"tpl": "generic"})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "share-payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    covers = {}
    try:
        from share_og import write_cover
        covers = {"cover": write_cover(teaser, out / "cover.jpg"),
                  "generic": write_cover(generic, out / "cover-generic.jpg")}
    except ImportError:
        print("note: pip install pillow to see the cover image itself; its exact text is below.")

    print(f"\n{PRODUCT_NAME}: share link preview. Your chat stays on this device.")
    print("Only these statistics are encrypted on this device and uploaded. The server cannot read them;")
    print("anyone with the full link can. No names, no messages, no exact dates.\n")
    print("  WHAT LINK RECIPIENTS WILL SEE (decrypted):")
    for line in describe(payload):
        print(f"    {line}")
    print(f"\n  PUBLIC COVER (shown in link previews; anyone who sees the link can see this, even without the key):")
    print("    " + " / ".join((PRODUCT_NAME, *teaser_lines(teaser))))
    if covers:
        print(f"    image: {covers['cover']}")
    print("    generic alternative: " + " / ".join((PRODUCT_NAME, *teaser_lines(generic)))
          + (f"  ({covers['generic']})" if covers else ""))
    print(f"\n  Saved locally first: {out / 'share-payload.json'}" + (f", {out / 'cover.jpg'}" if covers else ""))
    print(f"  Server: {server}. Expires after {a.expires}; you can delete it sooner.")
    print("  Recipients can forward the link. Apps such as WhatsApp, X and iMessage cache link previews,")
    print("  so the cover may stay visible in old chats after the link expires or is deleted.\n")
    if a.dry_run:
        print("dry run: nothing uploaded.")
        return 0

    ans = tty_ask("Approval 1 of 2. Type COVER to approve the public cover above, GENERIC to use the generic cover "
                  "instead. Anything else cancels: ")
    if ans == "GENERIC":
        teaser = generic
    elif ans != "COVER":
        print("cancelled: nothing uploaded.")
        return 1
    ans = tty_ask(f"Approval 2 of 2. Type PUBLISH to encrypt the statistics above and upload them to {server} "
                  f"(expires after {a.expires}). Anything else cancels: ")
    if ans != "PUBLISH":
        print("cancelled: nothing uploaded.")
        return 1
    res = publish(payload, teaser, server, a.expires)
    me = Path(__file__).resolve()
    print(f"\nlink: {res['link']}")
    print(f"expires: {res['expires']}")
    print(f"delete: python3 {me} --delete {res['id']}")
    print(f"(the delete secret is saved only on this device, in {LINKS_FILE})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
