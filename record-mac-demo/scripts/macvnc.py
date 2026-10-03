#!/usr/bin/env python3
"""Drive a second Mac over VNC without a Screen Sharing window, and log every action for captions.

The connection itself matters as much as the control: a headless Mac (no monitor, no dummy
plug) has no framebuffer, so screenshots and screen recordings fail until a VNC client is
attached. This process is that client. Nothing appears on your own screen.

Config (environment only; the password never goes on a command line):
  MACVNC_HOST      host or host::port of the target Mac            (required)
  MACVNC_USER      macOS account to log in as                     (required for macOS auth)
  MACVNC_PASSWORD  the password, if you inject it into the environment yourself
                   otherwise it is read once from your macOS login keychain, where
                   Screen Sharing saves it after one manual connection
  MACVNC_PORT      local control port, default 8765 (bound to 127.0.0.1 only)

Control API, all GET, coordinates in the target's framebuffer pixels:
  /shot?out=PATH            save a PNG of the target screen
  /click?x=&y=  /dbl?x=&y=  /move?x=&y=  /drag?x1=&y1=&x2=&y2=
  /type?t=TEXT              URL-encode TEXT (%20 for spaces) or nothing arrives
  /key?k=NAME               enter, esc, pgdn, home, tab, or combos like super-shift-5
  /log?path=FILE            start an action log (TSV: seconds since start, label)
  /act?label=TEXT           append one line to that log, timed from /log
  /grab_start?dir=&fps=     fallback recorder: JPEG frames over VNC (slow, ~1-4 fps)
  /grab_stop

    python3 scripts/macvnc.py &
    curl -s 'http://127.0.0.1:8765/shot?out=/tmp/now.png'
"""
import os
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def keychain_password(host, user):
    server = host.split("::")[0].split(":")[0]
    r = subprocess.run(["security", "find-internet-password", "-s", server, "-a", user, "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip()


class Controller:
    """Wraps a vncdotool-style client. Tests pass a fake client with the same methods."""

    def __init__(self, client):
        self.client = client
        self.lock = threading.Lock()
        self.grab = {"on": False}
        self.log_path, self.t0 = None, None

    def act(self, label):
        if not self.log_path:
            raise ValueError("call /log?path= first")
        with open(self.log_path, "a") as f:
            f.write(f"{time.time() - self.t0:7.1f}\t{label}\n")

    def _grabber(self, d, fps):
        os.makedirs(d, exist_ok=True)
        i = 0
        while self.grab["on"]:
            t = time.time()
            with self.lock:
                self.client.refreshScreen()
                img = self.client.screen.copy() if self.client.screen else None
            if img is not None:
                img.convert("RGB").save(f"{d}/f{i:06d}.jpg", quality=88)
                with open(f"{d}/times.txt", "a") as f:
                    f.write(f"{i} {t:.3f}\n")
                i += 1
            time.sleep(max(0, 1 / fps - (time.time() - t)))

    def handle(self, path, q):
        c = self.client
        if path == "/log":
            self.log_path, self.t0 = q["path"], time.time()
            open(self.log_path, "w").close()
            return
        if path == "/act":
            return self.act(q["label"])
        if path == "/grab_stop":
            self.grab["on"] = False
            return
        if path == "/grab_start":
            self.grab["on"] = True
            threading.Thread(target=self._grabber, args=(q["dir"], float(q.get("fps", 2))),
                             daemon=True).start()
            return
        with self.lock:
            if path == "/shot":
                c.refreshScreen()
                c.captureScreen(q["out"])
            elif path == "/move":
                c.mouseMove(int(q["x"]), int(q["y"]))
            elif path in ("/click", "/dbl"):
                c.mouseMove(int(q["x"]), int(q["y"]))
                time.sleep(0.1)
                c.mousePress(1)
                if path == "/dbl":
                    time.sleep(0.08)
                    c.mousePress(1)
            elif path == "/drag":
                c.mouseMove(int(q["x1"]), int(q["y1"])); time.sleep(0.1)
                c.mouseDown(1); time.sleep(0.1)
                c.mouseDrag(int(q["x2"]), int(q["y2"]), step=20); time.sleep(0.1)
                c.mouseUp(1)
            elif path == "/type":
                for ch in q["t"]:
                    c.keyPress("space" if ch == " " else ch)
                    time.sleep(0.02)
            elif path == "/key":
                c.keyPress(q["k"])
            else:
                raise KeyError(path)


def serve(ctl, port):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
            try:
                ctl.handle(u.path, q)
                self.send_response(200); self.end_headers(); self.wfile.write(b"ok\n")
            except Exception as e:  # report to the caller, keep serving
                self.send_response(500); self.end_headers(); self.wfile.write(repr(e).encode())

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    return srv


def main():
    from vncdotool import api
    host, user = os.environ.get("MACVNC_HOST"), os.environ.get("MACVNC_USER")
    if not host:
        sys.exit("set MACVNC_HOST")
    pw = os.environ.pop("MACVNC_PASSWORD", "") or (keychain_password(host, user) if user else "")
    if not pw:
        sys.exit("no password: connect once with Screen Sharing and save it, or set MACVNC_PASSWORD")
    if "::" not in host:
        host += "::5900"
    client = api.connect(host, password=pw, username=user, timeout=30)
    del pw
    port = int(os.environ.get("MACVNC_PORT", "8765"))
    print(f"connected; control on http://127.0.0.1:{port}", flush=True)
    serve(Controller(client), port).serve_forever()


if __name__ == "__main__":
    main()
