"""RELEASE GATE: capture ALL network traffic of the share flow and assert no fake name, phone number or secret leaves.

The test runs inside a fresh network namespace where loopback is the only interface, so nothing can reach the
internet and every packet the flow sends is on the capture. It:
  1. writes a SYNTHETIC group chat seeded with canaries (fake names, a phone-number sender, passwords, keys, IBAN,
     email, address, the chat title), see canary.py;
  2. starts the real share server on loopback and tcpdump on every interface;
  3. runs the real uploader CLI under a pseudo-terminal, typing the two approvals, with strace logging every
     connect/sendto/sendmsg syscall of the process tree;
  4. opens the printed link in headless Chromium (recipient side), logging every request;
  5. asserts: no canary in either capture (raw, lower case, URL-encoded), the key never on the wire, the uploader
     connected only to the share server, every browser request went to the share server without the key or a
     Referer, the terminal output has no canary, and the stored ciphertext decrypts to a valid payload without one.

Run on Linux with sudo: python3 tests/test_share_egress.py  (it re-runs itself as root in `unshare -n`).
"""
from __future__ import annotations

import json
import os
import pty
import re
import select
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))

PORT = 18871
BASE = "/w-preview"
ORIGIN = f"http://127.0.0.1:{PORT}"


def run_pty(argv: list, env: dict, answers: dict, timeout: float = 180) -> tuple[int, bytes]:
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe(argv[0], argv, env)
    out, sent, end = b"", set(), time.time() + timeout
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
            for prompt, answer in answers.items():
                if prompt in out and prompt not in sent:
                    os.write(fd, answer)
                    sent.add(prompt)
        else:
            done, status = os.waitpid(pid, os.WNOHANG)
            if done:
                return os.waitstatus_to_exitcode(status), out
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status), out


class Capture:
    """tcpdump on every interface of the namespace. Immediate mode and a large buffer, and the gate fails if the
    kernel dropped a single packet, so 'nothing leaked' cannot come from an incomplete capture."""

    def __init__(self, path: Path):
        self.path, self.err = path, path.with_suffix(".err")
        self.p = subprocess.Popen(["tcpdump", "-Z", "root", "--immediate-mode", "-B", "65536", "-i", "any", "-U",
                                   "-s", "0", "-n", "-w", str(path)], stderr=open(self.err, "w"))
        for _ in range(100):
            if "listening" in self.err.read_text():
                break
            time.sleep(0.05)
        else:
            raise RuntimeError("tcpdump did not start")
        time.sleep(0.5)

    def stop(self) -> bytes:
        time.sleep(0.5)
        self.p.terminate()
        self.p.wait(timeout=10)
        stats = self.err.read_text()
        m = re.search(r"(\d+) packets dropped by kernel", stats)
        assert m and m.group(1) == "0", f"capture incomplete: {stats!r}"
        return self.path.read_bytes()

    def flows(self) -> list[str]:
        r = subprocess.run(["tcpdump", "-nn", "-r", str(self.path)], capture_output=True, text=True)
        return [ln for ln in r.stdout.splitlines() if ln.strip()]


def gate() -> dict:
    import canary
    from share_schema import validate
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    assert os.geteuid() == 0, "run as root inside unshare -n"
    if os.environ.get("SUDO_USER") and "PLAYWRIGHT_BROWSERS_PATH" not in os.environ:
        cache = Path(os.path.expanduser("~" + os.environ["SUDO_USER"])) / ".cache" / "ms-playwright"
        if cache.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(cache)
    subprocess.run(["ip", "link", "set", "lo", "up"], check=True)
    links = subprocess.run(["ip", "-o", "link"], capture_output=True, text=True).stdout.splitlines()
    assert len(links) == 1 and ": lo:" in links[0], f"not an isolated namespace: {links}"

    tmp = Path(tempfile.mkdtemp(prefix="egress-"))
    os.chmod(tmp, 0o755)
    chat = canary.write_group(tmp / "WhatsApp Chat with Quixtarr Secret Society.txt")
    env = {**os.environ, "CR_PORT": str(PORT), "CR_BASE": BASE, "CR_ORIGIN": ORIGIN, "CR_DB": str(tmp / "db.sqlite3"),
           "CHAT_REPLAY_HOME": str(tmp / "home"), "PYTHONDONTWRITEBYTECODE": "1", "HOME": str(tmp)}
    srv = subprocess.Popen([sys.executable, str(SKILL / "share" / "server.py")], env=env, stderr=subprocess.DEVNULL)
    report = {}
    try:
        for _ in range(50):
            try:
                import urllib.request
                urllib.request.build_opener(urllib.request.ProxyHandler({})).open(ORIGIN + BASE + "/", timeout=1)
                break
            except Exception:
                time.sleep(0.1)

        # ---------------- phase A: the uploader
        cap = Capture(tmp / "uploader.pcap")
        strace_log = tmp / "strace.log"
        code, term = run_pty(
            ["strace", "-f", "-qq", "-e", "trace=connect,sendto,sendmsg", "-o", str(strace_log), sys.executable,
             str(SKILL / "scripts" / "share.py"), str(chat), "--server", ORIGIN + BASE, "--out", str(tmp / "local"),
             "--cover", "messages", "--expires", "24h"],
            env, {b"Approval 1 of 2": b"COVER\n", b"Approval 2 of 2": b"PUBLISH\n"})
        pcap_a = cap.stop()
        flows_a = cap.flows()
        assert code == 0, term.decode(errors="replace")[-2000:]
        m = re.search(rb"link: (\S+)", term)
        assert m, "no link printed"
        link = m.group(1).decode()
        key = link.split("#k=")[1]
        sid = link.split("/s/")[1].split("#")[0]

        assert b"POST /w-preview/api/shares" in pcap_a, f"capture is empty ({len(pcap_a)} bytes, {len(flows_a)} packets): the gate would prove nothing"
        assert canary.leaks(pcap_a) == [], f"canary on the wire (uploader): {canary.leaks(pcap_a)}"
        assert key.encode() not in pcap_a, "key on the wire"
        assert canary.leaks(term) == [], f"canary in terminal output: {canary.leaks(term)}"
        stray = [f for f in flows_a if f".{PORT}" not in f]
        assert not stray, f"uploader traffic to something other than the share server: {stray[:5]}"
        connects = [ln for ln in strace_log.read_text().splitlines() if "connect(" in ln]
        inet = [ln for ln in connects if "AF_INET" in ln]
        bad = [ln for ln in inet if f"sin_port=htons({PORT})" not in ln or '"127.0.0.1"' not in ln]
        assert inet and not bad, f"uploader connected elsewhere: {bad[:5]}"
        sends = [ln for ln in strace_log.read_text().splitlines() if re.search(r"\bsend(to|msg)\(", ln)]

        # stored data: ciphertext only, decrypts to a valid payload with no canary
        db = sqlite3.connect(tmp / "db.sqlite3")
        ct, iv, teaser = db.execute("SELECT ct, iv, teaser FROM shares WHERE id = ?", (sid,)).fetchone()
        assert canary.leaks(ct) == [] and canary.leaks(teaser.encode()) == []
        import share
        plain = AESGCM(share.b64u_dec(key)).decrypt(iv, ct, b"chat-replay/v1")
        validate(json.loads(plain))
        assert canary.leaks(plain) == [], "canary inside the encrypted payload"

        # ---------------- phase B: a recipient opens the link
        cap_b = Capture(tmp / "viewer.pcap")
        requests, frames_seen = [], 0
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 390, "height": 844})
            page.on("request", lambda r: requests.append({"url": r.url, "headers": r.headers}))
            page.goto(link)
            page.wait_for_selector(".frame.on.frame-cover", timeout=15000)
            for _ in range(20):
                frames_seen += 1
                if page.locator(".frame.on.frame-final").count():
                    break
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(150)
            assert page.locator(".frame.on.frame-final").count(), "story did not reach the final frame"
            assert "Can your group beat this?" in page.inner_text(".frame.on")
            b.close()
        pcap_b = cap_b.stop()
        assert canary.leaks(pcap_b) == [], f"canary on the wire (viewer): {canary.leaks(pcap_b)}"
        assert key.encode() not in pcap_b, "key on the wire (viewer)"
        off = [r["url"] for r in requests if not r["url"].startswith(ORIGIN + BASE + "/")]
        assert not off, f"viewer requested other origins: {off}"
        assert not [r for r in requests if key in r["url"] or key in json.dumps(r["headers"])], "key in a request"
        with_ref = [r["url"] for r in requests if any(k.lower() == "referer" and v for k, v in r["headers"].items())]
        assert not with_ref and b"\r\nreferer:" not in pcap_b.lower(), f"a request sent a Referer: {with_ref}"

        report = {"result": "PASS", "canaries": len(canary.CANARIES), "uploader_packets": len(flows_a),
                  "uploader_bytes_captured": len(pcap_a), "uploader_inet_connects": len(inet),
                  "uploader_send_syscalls": len(sends), "viewer_requests": len(requests),
                  "viewer_bytes_captured": len(pcap_b), "frames_seen": frames_seen,
                  "viewer_request_paths": sorted({r["url"].split("#")[0].replace(ORIGIN, "").split("?")[0]
                                                  .replace(sid, "<id>") for r in requests})}
        return report
    finally:
        srv.terminate()
        shutil.rmtree(tmp, ignore_errors=True)


class EgressGate(unittest.TestCase):
    def test_no_canary_leaves_the_device(self):
        if sys.platform != "linux" or not shutil.which("tcpdump") or not shutil.which("strace"):
            self.skipTest("needs Linux with tcpdump and strace")
        cmd = ["sudo", "-n", "unshare", "-n", sys.executable, str(Path(__file__).resolve()), "--inside"]
        if os.geteuid() == 0:
            cmd = cmd[2:]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode == 2 and "sudo" in r.stderr:
            self.skipTest("needs passwordless sudo for a network namespace")
        print(r.stdout.strip())
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-3000:])


if __name__ == "__main__":
    if "--inside" in sys.argv:
        try:
            print(json.dumps(gate(), indent=1))
        except AssertionError as exc:
            print(f"FAIL: {exc}")
            raise SystemExit(1)
        raise SystemExit(0)
    unittest.main()
