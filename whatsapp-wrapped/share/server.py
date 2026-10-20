#!/usr/bin/env python3
"""Tiny host for encrypted share links. Python standard library plus Pillow (for the cover image).

Stores per link: ciphertext, nonce, version, expiry, the approved public teaser, the SHA-256 of the delete secret,
and a view counter. It never receives the key (it lives in the URL #fragment) and cannot read the statistics.

Routes, under CR_BASE (default /w-preview):
  GET    /s/<id>            viewer page (OG tags from the teaser); 410 page without preview once expired or deleted
  GET    /api/shares/<id>   {v, ct, iv, expires}; counts a view
  POST   /api/shares        create: {v, ct, iv, ttl, teaser, del}
  DELETE /api/shares/<id>   header X-Delete-Secret
  POST   /api/report/<id>   {reason}; three reports from different people hide the link until reviewed
  GET    /og/<id>.jpg       cover rendered from a fixed template; /og/generic.jpg
  GET    /static/<file>     viewer assets (allowlist)

Environment: CR_HOST, CR_PORT, CR_BASE, CR_ORIGIN (public origin for og:image), CR_DB, CR_TRUST_PROXY=1.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import html
import json
import os
import re
import sqlite3
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

from share_schema import CONFIG, PRODUCT_NAME, SCHEMA, SchemaError, teaser_lines, validate_teaser  # noqa: E402

HOST = os.environ.get("CR_HOST", "127.0.0.1")
PORT = int(os.environ.get("CR_PORT", "8871"))
BASE = "/" + os.environ.get("CR_BASE", "/w-preview").strip("/")
ORIGIN = os.environ.get("CR_ORIGIN", f"http://{HOST}:{PORT}").rstrip("/")
DB_PATH = os.environ.get("CR_DB", str(HERE / "shares.sqlite3"))
TRUST_PROXY = os.environ.get("CR_TRUST_PROXY") == "1"

MAX_BODY = 16 * 1024
MAX_CT = SCHEMA["max_plain_bytes"] + 16          # plaintext cap plus the GCM tag
MAX_ACTIVE = int(os.environ.get("CR_MAX_ACTIVE", "5000"))
LIMITS = {"create": (20, 3600), "report": (10, 3600), "read": (240, 60), "og": (120, 60), "delete": (30, 3600)}
REPORT_HIDE_AT = 3
REPORT_RETENTION_S = 7 * 86400
REASONS = {"spam", "harmful", "personal_info", "other"}
ID_RE = re.compile(r"^[A-Za-z0-9_-]{22}$")
B64U = re.compile(r"^[A-Za-z0-9_-]+$")
STATIC = {
    "viewer.js": (HERE / "static" / "viewer.js", "text/javascript; charset=utf-8"),
    "viewer.css": (HERE / "static" / "viewer.css", "text/css; charset=utf-8"),
    "meadow.webp": (HERE / "static" / "meadow.webp", "image/webp"),
    "favicon.svg": (HERE / "static" / "favicon.svg", "image/svg+xml"),
    "schema-v1.json": (HERE / "schema-v1.json", "application/json"),
    "inter.woff2": (HERE.parent / "assets" / "InterVariable-subset.woff2", "font/woff2"),
}
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; "
       "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
SECURITY_HEADERS = {
    "X-Robots-Tag": "noindex, nofollow, noarchive, nosnippet",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": CSP,
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}
IP_SALT = os.urandom(16)  # report IP hashes cannot be linked across restarts


def now() -> float:
    return time.time()


def b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.lock = threading.Lock()
        with self.lock:
            self.db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS shares (id TEXT PRIMARY KEY, v INTEGER NOT NULL, ct BLOB NOT NULL,
                  iv BLOB NOT NULL, teaser TEXT NOT NULL, del_hash TEXT NOT NULL, created REAL NOT NULL,
                  expires REAL NOT NULL, views INTEGER NOT NULL DEFAULT 0, hidden INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS reports (id TEXT NOT NULL, reason TEXT NOT NULL, ip_hash TEXT NOT NULL,
                  at REAL NOT NULL);
            """)

    def q(self, sql: str, args=()):
        with self.lock:
            return self.db.execute(sql, args).fetchall()

    def purge(self) -> None:
        t = now()
        with self.lock:
            self.db.execute("DELETE FROM shares WHERE expires <= ?", (t,))
            self.db.execute("DELETE FROM reports WHERE at <= ?", (t - REPORT_RETENTION_S,))

    def live(self, share_id: str):
        rows = self.q("SELECT v, ct, iv, teaser, expires, hidden FROM shares WHERE id = ?", (share_id,))
        if not rows or rows[0][4] <= now() or rows[0][5]:
            return None
        return rows[0]


class Throttle:
    def __init__(self):
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, kind: str, ip: str) -> bool:
        limit, window = LIMITS[kind]
        t = now()
        with self.lock:
            dq = self.hits[(kind, ip)]
            while dq and dq[0] <= t - window:
                dq.popleft()
            if len(dq) >= limit:
                return False
            dq.append(t)
            return True


STORE: Store | None = None
THROTTLE = Throttle()
OG_CACHE: dict = {}


def page(title: str, body: str, head: str = "", body_attrs: str = "") -> bytes:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="referrer" content="no-referrer">
<meta name="theme-color" content="#f5f3eb">
<title>{html.escape(title)}</title>
<link rel="icon" href="{BASE}/static/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE}/static/viewer.css">
{head}</head>
<body {body_attrs}>{body}</body></html>""".encode()


def viewer_page(share_id: str, teaser: dict) -> bytes:
    l1, l2 = teaser_lines(teaser)
    title = f"{l1} {l2}" if teaser["tpl"] != "generic" else PRODUCT_NAME
    e = html.escape
    og = f"{ORIGIN}{BASE}/og/{share_id}.jpg"
    head = f"""<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(PRODUCT_NAME)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="A chat story made on the sender's device. Tap to watch.">
<meta property="og:url" content="{ORIGIN}{BASE}/s/{share_id}">
<meta property="og:image" content="{og}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(PRODUCT_NAME)} cover">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:image" content="{og}">
<script src="{BASE}/static/viewer.js" defer></script>
"""
    attrs = (f'data-base="{e(BASE)}" data-id="{share_id}" data-name="{e(PRODUCT_NAME)}" '
             f'data-cta="{e(CONFIG["make_yours_url"])}"')
    body = ('<main id="app" class="stage"><div class="story" aria-live="polite"><div class="frame frame-loading">'
            '<p class="kicker">Opening the story</p></div></div></main>'
            '<noscript><p class="nojs">This story decrypts in your browser and needs JavaScript.</p></noscript>')
    return page(PRODUCT_NAME, body, head, attrs)


def gone_page() -> bytes:
    cta = html.escape(CONFIG["make_yours_url"])
    body = (f'<main class="stage"><div class="story"><section class="frame frame-final frame-gone">'
            f'<p class="kicker">{html.escape(PRODUCT_NAME)}</p><h1 class="headline">This story has expired or was '
            f'deleted.</h1><p class="sub">Links last up to 30 days. Ask the sender for a new one, or make your own.</p>'
            f'<a class="cta" href="{cta}" rel="noreferrer noopener">Make yours</a>'
            f'<img class="meadow" src="{BASE}/static/meadow.webp" alt=""></section></div></main>')
    return page(PRODUCT_NAME, body)


def home_page() -> bytes:
    cta = html.escape(CONFIG["make_yours_url"])
    body = (f'<main class="stage"><div class="story"><section class="frame frame-final">'
            f'<p class="kicker">{html.escape(PRODUCT_NAME)} · preview</p><h1 class="headline">Your chat, replayed as '
            f'a story.</h1><p class="sub">Stats are made and encrypted on your device. This server only stores '
            f'ciphertext it cannot read.</p><a class="cta" href="{cta}" rel="noreferrer noopener">Make yours</a>'
            f'<img class="meadow" src="{BASE}/static/meadow.webp" alt=""></section></div></main>')
    return page(PRODUCT_NAME, body)


def og_image(key: str, teaser: dict) -> bytes:
    from share_og import render_cover
    if key not in OG_CACHE:
        if len(OG_CACHE) > 500:
            OG_CACHE.clear()
        OG_CACHE[key] = render_cover(teaser)
    return OG_CACHE[key]


class Handler(BaseHTTPRequestHandler):
    server_version = "chat-replay"
    sys_version = ""

    def log_message(self, *args):  # no access logs: nothing about viewers is kept
        pass

    def ip(self) -> str:
        if TRUST_PROXY and self.client_address[0] in ("127.0.0.1", "::1"):
            return self.headers.get("X-Real-IP", self.client_address[0])
        return self.client_address[0]

    def send(self, status: int, body: bytes = b"", ctype: str = "text/html; charset=utf-8", cache: str = "no-store",
             extra: dict | None = None):
        self.send_response(status)
        for k, v in {**SECURITY_HEADERS, "Content-Type": ctype, "Cache-Control": cache, **(extra or {})}.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def json(self, status: int, obj: dict):
        self.send(status, json.dumps(obj).encode(), "application/json")

    def route(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path == BASE:
            return None, None
        if not path.startswith(BASE + "/"):
            return "", ""
        rest = path[len(BASE):]
        return rest, rest.split("/")

    # ------------------------------------------------------------ GET / HEAD
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        rest, parts = self.route()
        if rest is None:
            return self.send(301, b"", extra={"Location": BASE + "/"})
        if rest == "/":
            return self.send(200, home_page())
        if len(parts) == 3 and parts[1] == "s":
            sid = parts[2]
            row = STORE.live(sid) if ID_RE.match(sid) else None
            if not row:
                return self.send(410, gone_page())
            return self.send(200, viewer_page(sid, json.loads(row[3])))
        if len(parts) == 4 and parts[1:3] == ["api", "shares"]:
            if not THROTTLE.allow("read", self.ip()):
                return self.json(429, {"error": "too many requests"})
            sid = parts[3]
            row = STORE.live(sid) if ID_RE.match(sid) else None
            if not row:
                return self.json(410, {"error": "expired or deleted"})
            STORE.q("UPDATE shares SET views = views + 1 WHERE id = ?", (sid,))
            return self.json(200, {"v": row[0], "ct": base64.urlsafe_b64encode(row[1]).decode().rstrip("="),
                                   "iv": base64.urlsafe_b64encode(row[2]).decode().rstrip("="),
                                   "expires": datetime.fromtimestamp(row[4], timezone.utc).isoformat(timespec="seconds")})
        if len(parts) == 3 and parts[1] == "og" and parts[2].endswith(".jpg"):
            if not THROTTLE.allow("og", self.ip()):
                return self.send(429, b"", "text/plain")
            sid = parts[2][:-4]
            if sid == "generic":
                teaser = {"tpl": "generic"}
            else:
                row = STORE.live(sid) if ID_RE.match(sid) else None
                if not row:
                    return self.send(404, b"not found", "text/plain")
                teaser = json.loads(row[3])
            key = json.dumps(teaser, sort_keys=True)
            return self.send(200, og_image(key, teaser), "image/jpeg", "public, max-age=600",
                             {"Cross-Origin-Resource-Policy": "cross-origin"})
        if len(parts) == 3 and parts[1] == "static" and parts[2] in STATIC:
            f, ctype = STATIC[parts[2]]
            return self.send(200, f.read_bytes(), ctype, "public, max-age=3600")
        return self.send(404, b"not found", "text/plain")

    # ------------------------------------------------------------ POST / DELETE
    def body_json(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            return None, "body too large"
        try:
            return json.loads(self.rfile.read(n) or b"null"), None
        except ValueError:
            return None, "invalid json"

    def do_POST(self):
        rest, parts = self.route()
        if rest == "/api/shares":
            return self.create()
        if parts and len(parts) == 4 and parts[1:3] == ["api", "report"]:
            return self.report(parts[3])
        return self.json(404, {"error": "not found"})

    def create(self):
        if not THROTTLE.allow("create", self.ip()):
            return self.json(429, {"error": "too many links from this address; try again later"})
        body, err = self.body_json()
        if err:
            return self.json(413 if "large" in err else 400, {"error": err})
        try:
            if type(body) is not dict or set(body) != {"v", "ct", "iv", "ttl", "teaser", "del"}:
                raise SchemaError("expected exactly v, ct, iv, ttl, teaser, del")
            if body["v"] != SCHEMA["version"] or type(body["v"]) is not int:
                raise SchemaError("unsupported version")
            if type(body["ttl"]) is not str or body["ttl"] not in CONFIG["expiry_options"]:
                raise SchemaError("ttl must be one of " + ", ".join(CONFIG["expiry_options"]))
            if type(body["del"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", body["del"]):
                raise SchemaError("del must be a sha256 hex digest")
            for k in ("ct", "iv"):
                if type(body[k]) is not str or not B64U.match(body[k]):
                    raise SchemaError(f"{k} must be base64url")
            ct, iv = b64u_decode(body["ct"]), b64u_decode(body["iv"])
            if len(iv) != 12:
                raise SchemaError("iv must be 12 bytes")
            if not 17 <= len(ct) <= MAX_CT:
                raise SchemaError("ciphertext size out of range")
            teaser = validate_teaser(body["teaser"])
        except (SchemaError, ValueError) as exc:
            return self.json(400, {"error": str(exc)})
        STORE.purge()
        if STORE.q("SELECT COUNT(*) FROM shares")[0][0] >= MAX_ACTIVE:
            return self.json(503, {"error": "the preview is full; try again later"})
        sid = base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip("=")
        t = now()
        exp = t + CONFIG["expiry_options"][body["ttl"]]
        STORE.q("INSERT INTO shares (id, v, ct, iv, teaser, del_hash, created, expires) VALUES (?,?,?,?,?,?,?,?)",
                (sid, body["v"], ct, iv, json.dumps(teaser, sort_keys=True), body["del"], t, exp))
        return self.json(201, {"id": sid, "expires": datetime.fromtimestamp(exp, timezone.utc).isoformat(timespec="seconds")})

    def report(self, sid: str):
        if not THROTTLE.allow("report", self.ip()):
            return self.json(429, {"error": "too many reports"})
        body, err = self.body_json()
        if err or type(body) is not dict or set(body) != {"reason"} or body["reason"] not in REASONS:
            return self.json(400, {"error": "reason must be one of " + ", ".join(sorted(REASONS))})
        if not ID_RE.match(sid) or not STORE.q("SELECT 1 FROM shares WHERE id = ?", (sid,)):
            return self.json(404, {"error": "not found"})
        ip_hash = hmac.new(IP_SALT, self.ip().encode(), hashlib.sha256).hexdigest()
        STORE.q("INSERT INTO reports (id, reason, ip_hash, at) VALUES (?,?,?,?)", (sid, body["reason"], ip_hash, now()))
        n = STORE.q("SELECT COUNT(DISTINCT ip_hash) FROM reports WHERE id = ?", (sid,))[0][0]
        if n >= REPORT_HIDE_AT:
            STORE.q("UPDATE shares SET hidden = 1 WHERE id = ?", (sid,))
        print(f"report: {sid} {body['reason']} ({n} reporter(s))", file=sys.stderr, flush=True)
        return self.json(202, {"ok": True})

    def do_DELETE(self):
        rest, parts = self.route()
        if not (parts and len(parts) == 4 and parts[1:3] == ["api", "shares"]):
            return self.json(404, {"error": "not found"})
        if not THROTTLE.allow("delete", self.ip()):
            return self.json(429, {"error": "too many requests"})
        sid, secret = parts[3], self.headers.get("X-Delete-Secret", "")
        rows = STORE.q("SELECT del_hash FROM shares WHERE id = ?", (sid,)) if ID_RE.match(sid) else []
        if not rows:
            return self.json(404, {"error": "not found"})
        if not hmac.compare_digest(rows[0][0], hashlib.sha256(secret.encode()).hexdigest()):
            return self.json(403, {"error": "wrong delete secret"})
        STORE.q("DELETE FROM shares WHERE id = ?", (sid,))
        STORE.q("DELETE FROM reports WHERE id = ?", (sid,))
        return self.json(200, {"deleted": sid})


def make_server(host: str = HOST, port: int = PORT, db_path: str = DB_PATH) -> ThreadingHTTPServer:
    global STORE
    STORE = Store(db_path)
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    return srv


def main() -> int:
    srv = make_server()
    print(f"{PRODUCT_NAME} share server on {HOST}:{PORT}{BASE} (db {DB_PATH})", file=sys.stderr, flush=True)

    def janitor():
        while True:
            time.sleep(600)
            STORE.purge()
    threading.Thread(target=janitor, daemon=True).start()
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
