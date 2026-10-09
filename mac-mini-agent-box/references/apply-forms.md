# Fill and submit web forms through the real Chrome

What we run: applications (programs, grants, credits, jobs) and other web forms filled through a
logged-in Chrome profile on the box (`browser-cdp.md`), from a home connection. Cloud servers and
automation-launched browsers get blocked by Cloudflare and reCAPTCHA spam checks; a real Chrome on a
home IP usually passes.

Prerequisite: the profile's Chrome is up. Check: `curl -s http://127.0.0.1:<port>/json/version`.

## Driver

`scripts/cdp_tab.py` provides `CdpTab()`: an isolated new tab on the running Chrome (never touches the
account's own tabs). Methods: `navigate(url)`, `fields()` (JSON of inputs, textareas and selects with
label, type and required flag), `set_value(css, value)`, `click(css)`, `upload(css, path_on_mac)`,
`screenshot(local_png)`, `ev(js)`, `close()`. **Always `close()` in a `finally` block.**

```python
import sys; sys.path.insert(0, "scripts")
from cdp_tab import CdpTab
t = CdpTab()
try:
    t.navigate("https://example.com/apply")
    print(t.fields())
    t.screenshot("/tmp/before.png")
finally:
    t.close()
```

Files to upload must already be on the box: keep them in one folder, for example
`/Users/owner/apply-assets/` (copy new ones with `scp file owner@agent-box:apply-assets/`).

## Per form

1. `navigate(url)`, then `fields()` to map the form, then `screenshot()` and **look at it**. Never fill
   blind.
2. Fill from the owner's approved answers (a document the owner wrote and keeps up to date). Never
   invent facts, numbers or claims.
3. `upload()` files where required.
4. `screenshot()` before submitting and check every field character by character, especially name,
   email and links.
5. Submit only when everything is correct. Low-stakes forms the owner has approved in general: submit.
   High-stakes ones (equity programs, anything that burns a one-time slot, anything legal or paid):
   stop with the screenshot and ask the owner.
6. A visible CAPTCHA: stop and report `CAPTCHA_WALL`. Do not solve it and do not use a solving
   service.
7. A login is missing: stop and report `NEEDS_LOGIN`. Never type credentials.
8. Log what you did (form, date, result, screenshot path) where the owner tracks it, then `close()`.

## Parallel workers

One Chrome handles many isolated tabs at once: one worker per form, each with its own `CdpTab()`, each
closing its tab when done. Cap at about six at once. Open tabs pile up and slow the box.

## Hard rules

- Never fabricate data. Never submit a high-stakes form without the owner seeing the screenshot.
- Always `close()` your tab. Never quit Chrome, and never touch another account's tab or login.
