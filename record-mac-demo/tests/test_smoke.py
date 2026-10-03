#!/usr/bin/env python3
"""Smoke test for the controller's HTTP API with a fake VNC client. No Mac, no network.

    python3 tests/test_smoke.py
"""
import os
import sys
import tempfile
import threading
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import macvnc  # noqa: E402


class FakeClient:
    screen = None

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        return lambda *a, **k: self.calls.append((name, a))


def main():
    fake = FakeClient()
    srv = macvnc.serve(macvnc.Controller(fake), 0)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    get = lambda p: urllib.request.urlopen(f"http://127.0.0.1:{port}{p}").read()

    log = os.path.join(tempfile.mkdtemp(), "actions.tsv")
    get(f"/log?path={log}")
    get("/act?label=click%3A%20Copy%20setup%20link")
    get("/click?x=10&y=20")
    get("/type?t=a%20b")
    get("/key?k=super-shift-5")
    try:
        get("/nope")
        raise AssertionError("unknown path must fail")
    except urllib.error.HTTPError as e:
        assert e.code == 500

    assert ("mouseMove", (10, 20)) in fake.calls and ("mousePress", (1,)) in fake.calls
    assert [a for n, a in fake.calls if n == "keyPress"] == [("a",), ("space",), ("b",), ("super-shift-5",)]
    rows = open(log).read().splitlines()
    assert len(rows) == 1 and rows[0].split("\t")[1] == "click: Copy setup link", rows
    assert float(rows[0].split("\t")[0]) < 5
    srv.shutdown()
    print("ok")


if __name__ == "__main__":
    main()
