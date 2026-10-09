#!/usr/bin/env python3
"""Drive an isolated tab on a logged-in Chrome over CDP, and test that its logins persist.

Same method the Edge team uses on its shared Mac mini: attach to the REAL, already logged-in Chrome
(not a Playwright-launched one), open a NEW tab through the browser-level Target API so the account's
own tabs are never touched, use Page.captureScreenshot (no webfont hang) and DOM.setFileInputFiles for
uploads (the file must already be on the Mac).

CDP endpoint: env CDP_URL, default http://127.0.0.1:9334 . Run on the Mac itself, or through an SSH
tunnel (ssh -N -L 9334:127.0.0.1:9334 helper@agent-box) and keep CDP_URL on 127.0.0.1.

Usage:
  python3 cdp_tab.py shot <url>        # open, navigate, screenshot, close the tab
  python3 cdp_tab.py inspect <url>     # same, plus a JSON list of the form fields
  python3 cdp_tab.py persist seed      # write a test cookie + localStorage on example.com
  python3 cdp_tab.py persist close     # close Chrome GRACEFULLY (KeepAlive relaunches it)
  python3 cdp_tab.py persist check     # after relaunch or reboot: SURVIVED or LOST

Needs: pip install --user websocket-client
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.request

import websocket  # websocket-client

BASE = os.environ.get("CDP_URL", "http://127.0.0.1:9334").rstrip("/")


def hostport():
    return re.search(r"://([^/]+)", BASE).group(1)


def browser_ws():
    """Browser-level websocket. Chrome reports its own host:port; rewrite it to ours so tunnels work."""
    url = re.sub(r"://[^/]+/", f"://{hostport()}/", http("/json/version")["webSocketDebuggerUrl"])
    # No Origin header: Chrome accepts non-browser clients without one, while any Origin it does not
    # recognise is rejected with 403 unless Chrome was started with --remote-allow-origins.
    return websocket.create_connection(url, timeout=25, max_size=None, suppress_origin=True)


def http(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read())


class CdpTab:
    """Isolated new tab on the running Chrome. ALWAYS call close() in a finally block."""

    def __init__(self):
        self.ws = browser_ws()
        self._id = 0
        self.tid = self._raw("Target.createTarget", {"url": "about:blank"})["targetId"]
        self.sid = self._raw("Target.attachToTarget", {"targetId": self.tid, "flatten": True})["sessionId"]
        for domain in ("Page", "Runtime", "DOM"):
            self._raw(f"{domain}.enable", sid=self.sid)

    def _raw(self, method, params=None, sid=None):
        self._id += 1
        mid = self._id
        msg = {"id": mid, "method": method, "params": params or {}}
        if sid:
            msg["sessionId"] = sid
        self.ws.send(json.dumps(msg))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mid:
                return m.get("result", {})

    def ev(self, expr):
        r = self._raw("Runtime.evaluate", {"expression": expr, "returnByValue": True}, sid=self.sid)
        return r.get("result", {}).get("value")

    def navigate(self, url, wait=8):
        self._raw("Page.navigate", {"url": url}, sid=self.sid)
        for _ in range(60):
            if self.ev("document.readyState") == "complete":
                break
            time.sleep(0.5)
        time.sleep(wait)

    def fields(self):
        return self.ev("""(()=>{const o=[];document.querySelectorAll('input,textarea,select').forEach(e=>{
          if(e.type==='hidden')return;const l=(e.labels&&e.labels[0]?e.labels[0].innerText:'')||e.getAttribute('aria-label')||e.placeholder||e.name||'';
          o.push({tag:e.tagName.toLowerCase(),type:e.type||'',name:e.name||'',id:e.id||'',label:l.trim().slice(0,60),req:e.required});});
          return JSON.stringify(o.slice(0,50));})()""")

    def set_value(self, selector, value):
        """Native value setter + input/change events, so React and similar forms see the value."""
        js = ("(()=>{const e=document.querySelector(%s);if(!e)return false;"
              "const set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value')||"
              "Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value');"
              "set.set.call(e,%s);e.dispatchEvent(new Event('input',{bubbles:true}));"
              "e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()") % (
            json.dumps(selector), json.dumps(value))
        return self.ev(js)

    def click(self, selector):
        return self.ev(f"(()=>{{const e=document.querySelector({json.dumps(selector)});"
                       f"if(!e)return false;e.click();return true;}})()")

    def upload(self, selector, path_on_mac):
        doc = self._raw("DOM.getDocument", {"depth": 0}, sid=self.sid)["root"]["nodeId"]
        node = self._raw("DOM.querySelector", {"nodeId": doc, "selector": selector}, sid=self.sid).get("nodeId")
        if not node:
            return False
        self._raw("DOM.setFileInputFiles", {"files": [path_on_mac], "nodeId": node}, sid=self.sid)
        return True

    def screenshot(self, local_path):
        r = self._raw("Page.captureScreenshot", {"format": "png"}, sid=self.sid)
        with open(local_path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
        return local_path

    def close(self):
        try:
            self._raw("Target.closeTarget", {"targetId": self.tid})
            self.ws.close()
        except Exception:
            pass


def persist(mode):
    """Never test persistence with set-cookie-then-kill: Chrome flushes cookies on a ~30 s timer or a
    graceful shutdown, so a hard kill loses them whatever the keychain state. Seed, close gracefully,
    let KeepAlive relaunch (or reboot), then check."""
    if mode == "close":
        ws = browser_ws()
        try:
            ws.send(json.dumps({"id": 1, "method": "Browser.close"}))
            ws.recv()  # wait for the reply or the connection dropping as Chrome exits
        except Exception:
            pass
        print("CLOSED")
        return
    t = CdpTab()
    try:
        t.navigate("https://example.com", wait=3)
        if mode == "seed":
            print("SEEDED:", t.ev("localStorage.setItem('agentbox','persist-v1');"
                                  "document.cookie='agentbox=persist-v1; max-age=31536000; path=/';"
                                  "[localStorage.getItem('agentbox'), document.cookie]"))
        else:
            ls, ck = t.ev("[localStorage.getItem('agentbox'), document.cookie]")
            print("localStorage:", "SURVIVED" if ls == "persist-v1" else f"LOST ({ls!r})")
            print("cookie:", "SURVIVED" if "agentbox=persist-v1" in (ck or "") else f"LOST ({ck!r})")
    finally:
        t.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    action, arg = sys.argv[1], sys.argv[2]
    if action == "persist":
        persist(arg)
        sys.exit(0)
    tab = CdpTab()
    try:
        tab.navigate(arg)
        print("TITLE:", tab.ev("document.title"), "| URL:", tab.ev("location.href"))
        shot = f"/tmp/cdp-tab-{int(time.time())}.png"
        tab.screenshot(shot)
        print("SHOT:", shot)
        if action == "inspect":
            print("FIELDS:", tab.fields())
    finally:
        tab.close()
