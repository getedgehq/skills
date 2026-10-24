"""Share server: expiry, delete, report, caps, throttles and headers. Runs the real server on a loopback port."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE.parent / "share"))

os.environ.setdefault("CR_BASE", "/w-test")
os.environ["CR_TRUST_PROXY"] = "1"
import server  # noqa: E402
import share  # noqa: E402
from test_share_schema import good  # noqa: E402

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class Clock:
    t = 1_800_000_000.0


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        server.now = lambda: Clock.t
        cls.srv = server.make_server("127.0.0.1", 0, str(cls.tmp / "db.sqlite3"))
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}{server.BASE}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        server.THROTTLE.hits.clear()
        os.environ["CHAT_REPLAY_HOME"] = str(self.tmp / "home")
        share.LINKS_FILE = self.tmp / "home" / "links.json"
        self.ip = f"10.0.0.{id(self) % 250}"

    def req(self, method, path, body=None, headers=None, ip=None, raw=None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        r = urllib.request.Request(self.base + path, data=data, method=method,
                                   headers={"Content-Type": "application/json", "X-Real-IP": ip or self.ip, **(headers or {})})
        try:
            with OPENER.open(r, timeout=10) as res:
                return res.status, dict(res.headers), res.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def publish(self, ttl="30d", teaser=None):
        return share.publish(good(), teaser or {"tpl": "messages", "n": 5849}, self.base, ttl)

    # -------------------------------------------------------------- round trip
    def test_round_trip_and_server_cannot_read(self):
        res = self.publish()
        sid, key = res["id"], res["link"].split("#k=")[1]
        self.assertEqual(len(sid), 22)
        st, h, body = self.req("GET", f"/s/{sid}")
        self.assertEqual(st, 200)
        self.assertIn(b'property="og:image"', body)
        self.assertIn(f"/og/{sid}.jpg".encode(), body)
        self.assertIn(b"5,849 messages. Can your group beat this?", body)
        self.assertNotIn(key.encode(), body)
        st, _, blob = self.req("GET", f"/api/shares/{sid}")
        data = json.loads(blob)
        self.assertEqual(set(data), {"v", "ct", "iv", "expires"})
        rows = server.STORE.q("SELECT ct, teaser, del_hash FROM shares WHERE id = ?", (sid,))
        self.assertNotIn(b"messages", rows[0][0])  # stored bytes are ciphertext, not the JSON
        self.assertEqual(rows[0][2], hashlib.sha256(res["delete_secret"].encode()).hexdigest())
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        plain = AESGCM(share.b64u_dec(key)).decrypt(share.b64u_dec(data["iv"]), share.b64u_dec(data["ct"]),
                                                   b"chat-replay/v1")
        self.assertEqual(json.loads(plain), good())
        self.assertEqual(server.STORE.q("SELECT views FROM shares WHERE id = ?", (sid,))[0][0], 1)
        st, h, jpg = self.req("GET", f"/og/{sid}.jpg")
        self.assertEqual((st, h["Content-Type"], jpg[:3]), (200, "image/jpeg", b"\xff\xd8\xff"))
        self.assertLess(len(jpg), 300_000)  # WhatsApp skips preview images much larger than this

    def test_headers_everywhere(self):
        sid = self.publish()["id"]
        for path in ("/", f"/s/{sid}", f"/api/shares/{sid}", f"/og/{sid}.jpg", "/static/viewer.js", "/s/AAAAAAAAAAAAAAAAAAAAAA"):
            with self.subTest(path):
                _, h, _ = self.req("GET", path)
                self.assertEqual(h["X-Robots-Tag"], "noindex, nofollow, noarchive, nosnippet")
                self.assertEqual(h["Referrer-Policy"], "no-referrer")
                self.assertIn("default-src 'none'", h["Content-Security-Policy"])
                self.assertIn("script-src 'self'", h["Content-Security-Policy"])
                self.assertNotIn("unsafe-inline", h["Content-Security-Policy"])
                self.assertEqual(h["X-Content-Type-Options"], "nosniff")

    # -------------------------------------------------------------- expiry
    def test_expiry_24h(self):
        sid = self.publish(ttl="24h")["id"]
        self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 200)
        Clock.t += 86400 + 1
        try:
            st, _, body = self.req("GET", f"/s/{sid}")
            self.assertEqual(st, 410)
            self.assertNotIn(b"og:image", body)  # expired page carries no preview
            self.assertNotIn(b"og:title", body)
            self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 410)
            self.assertEqual(self.req("GET", f"/og/{sid}.jpg")[0], 404)
            server.STORE.purge()
            self.assertEqual(server.STORE.q("SELECT COUNT(*) FROM shares WHERE id = ?", (sid,))[0][0], 0)
        finally:
            Clock.t -= 86400 + 1

    def test_expiry_options(self):
        for ttl, secs in (("7d", 7 * 86400), ("30d", 30 * 86400)):
            sid = self.publish(ttl=ttl)["id"]
            Clock.t += secs - 5
            self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 200, ttl)
            Clock.t += 10
            self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 410, ttl)
            Clock.t -= secs + 5
        st, _, body = self.req("POST", "/api/shares", self.body(ttl="365d"))
        self.assertEqual(st, 400)

    # -------------------------------------------------------------- delete
    def test_delete(self):
        res = self.publish()
        sid = res["id"]
        st, _, _ = self.req("DELETE", f"/api/shares/{sid}", headers={"X-Delete-Secret": "wrong"})
        self.assertEqual(st, 403)
        st, _, _ = self.req("DELETE", f"/api/shares/{sid}")
        self.assertEqual(st, 403)
        self.assertEqual(share.delete(sid, None), 0)  # the CLI path, secret read from the local file
        self.assertEqual(self.req("GET", f"/s/{sid}")[0], 410)
        self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 410)
        self.assertEqual(self.req("GET", f"/og/{sid}.jpg")[0], 404)
        self.assertEqual(server.STORE.q("SELECT COUNT(*) FROM shares WHERE id = ?", (sid,))[0][0], 0)
        self.assertNotIn(sid, json.loads(share.LINKS_FILE.read_text()))

    # -------------------------------------------------------------- report abuse
    def test_report_hides_after_three_people(self):
        sid = self.publish()["id"]
        self.assertEqual(self.req("POST", f"/api/report/{sid}", {"reason": "free text"})[0], 400)
        self.assertEqual(self.req("POST", f"/api/report/{sid}", {"reason": "spam", "note": "x"})[0], 400)
        for i in range(3):
            self.assertEqual(self.req("POST", f"/api/report/{sid}", {"reason": "spam"}, ip="10.9.9.1")[0], 202)
        self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 200, "one person reporting three times is not three")
        self.req("POST", f"/api/report/{sid}", {"reason": "harmful"}, ip="10.9.9.2")
        self.req("POST", f"/api/report/{sid}", {"reason": "personal_info"}, ip="10.9.9.3")
        self.assertEqual(self.req("GET", f"/api/shares/{sid}")[0], 410)
        self.assertEqual(self.req("GET", f"/og/{sid}.jpg")[0], 404)
        ip_hashes = [r[0] for r in server.STORE.q("SELECT ip_hash FROM reports WHERE id = ?", (sid,))]
        self.assertTrue(all("10.9.9" not in h for h in ip_hashes))

    # -------------------------------------------------------------- caps and validation
    def body(self, **over):
        b = {"v": 1, "ct": share.b64u(os.urandom(200)), "iv": share.b64u(os.urandom(12)), "ttl": "30d",
             "teaser": {"tpl": "generic"}, "del": "a" * 64}
        b.update(over)
        return b

    def test_create_validation_and_caps(self):
        cases = {
            "ciphertext too big": self.body(ct=share.b64u(os.urandom(server.MAX_CT + 1))),
            "iv wrong size": self.body(iv=share.b64u(os.urandom(16))),
            "extra field": self.body(title="Sunday League"),
            "free-text teaser": self.body(teaser={"tpl": "custom", "text": "hello"}),
            "teaser with a name": self.body(teaser={"tpl": "messages", "n": 3, "name": "Maya"}),
            "bad delete hash": self.body(**{"del": "not-a-hash"}),
            "ct not base64url": self.body(ct="<script>"),
            "wrong version": self.body(v=2),
        }
        for name, b in cases.items():
            with self.subTest(name):
                self.assertEqual(self.req("POST", "/api/shares", b)[0], 400)
        st, _, _ = self.req("POST", "/api/shares", raw=b"x" * (server.MAX_BODY + 1))
        self.assertEqual(st, 413)
        self.assertEqual(self.req("POST", "/api/shares", raw=b"{not json")[0], 400)

    def test_create_throttle(self):
        limit = server.LIMITS["create"][0]
        codes = [self.req("POST", "/api/shares", self.body(), ip="10.7.7.7")[0] for _ in range(limit + 1)]
        self.assertEqual(codes[:limit], [201] * limit)
        self.assertEqual(codes[-1], 429)
        self.assertEqual(self.req("POST", "/api/shares", self.body(), ip="10.7.7.8")[0], 201)

    def test_max_active_cap(self):
        old = server.MAX_ACTIVE
        server.MAX_ACTIVE = server.STORE.q("SELECT COUNT(*) FROM shares")[0][0]
        try:
            self.assertEqual(self.req("POST", "/api/shares", self.body())[0], 503)
        finally:
            server.MAX_ACTIVE = old

    def test_no_arbitrary_files_or_methods(self):
        for path in ("/static/../server.py", "/static/shares.sqlite3", "/static/config.json", "/og/../../etc.jpg"):
            with self.subTest(path):
                self.assertEqual(self.req("GET", path)[0], 404)
        self.assertEqual(self.req("PUT", "/api/shares")[0], 501)


if __name__ == "__main__":
    unittest.main()
