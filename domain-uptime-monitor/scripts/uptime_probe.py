#!/usr/bin/env python3
"""Probe a list of domains you declare, with a real content check per domain.

An HTTP 200 is not proof a site is working. A suspended Vercel deployment returns
200 with a billing page. A broken build returns 200 with an empty shell. A failed
deploy leaves the previous marker in place but the API behind it gone. This script
checks what the response actually contains, per domain, in the way you say.

Alerts fire on state change only. A domain that has been down for a week sends one
email, not seven.

Usage
-----
  python scripts/uptime_probe.py --config domains.json --state .uptime/state.json \
      --report out/report.md

Exit codes: 0 all critical domains up, 1 at least one critical domain down,
2 bad config or arguments, 3 the probe itself could not run.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
import zlib
from pathlib import Path
from typing import Any, Callable

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
DEFAULT_TIMEOUT_SECONDS = 15
VALID_TIERS = ("critical", "standard")
VALID_CHECKS = ("status", "marker", "json")


class ConfigError(ValueError):
    """The config is missing something this script will not invent."""


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #
def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file is not valid JSON: {exc}") from None
    if not isinstance(config, dict):
        raise ConfigError("config file must contain a JSON object")

    domains = config.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ConfigError("'domains' must be a non-empty list")
    for entry in domains:
        if not isinstance(entry, dict) or not entry.get("host"):
            raise ConfigError("every 'domains' entry needs a 'host'")
        tier = entry.get("tier", "standard")
        if tier not in VALID_TIERS:
            raise ConfigError(f"{entry['host']}: tier must be one of {VALID_TIERS}")
        check = entry.get("check") or {"type": "status"}
        if not isinstance(check, dict):
            raise ConfigError(f"{entry['host']}: 'check' must be an object")
        if check.get("type", "status") not in VALID_CHECKS:
            raise ConfigError(f"{entry['host']}: check.type must be one of {VALID_CHECKS}")
        if check.get("type") == "marker" and not check.get("marker"):
            raise ConfigError(f"{entry['host']}: a marker check needs 'marker'")
        if check.get("type") == "json" and not check.get("field"):
            raise ConfigError(f"{entry['host']}: a json check needs 'field'")
    # Results are keyed by label, so two entries that share one would silently
    # overwrite each other and the report would be short a domain without saying so.
    labels = [label_of(entry) for entry in domains]
    duplicates = sorted({label for label in labels if labels.count(label) > 1})
    if duplicates:
        raise ConfigError(
            f"two or more domains share the label {', '.join(duplicates)}. "
            "Give each entry a distinct 'name' when you probe one host more than once")
    return config


def label_of(entry: dict[str, Any]) -> str:
    """What the report calls this entry. Defaults to the host."""
    return str(entry.get("name") or entry["host"])


def resolve_notify(config: dict[str, Any], cli_email: str | None,
                   cli_from: str | None, no_email: bool) -> tuple[str, str]:
    """Return (notify_email, email_from). Neither has a default: an alerting tool
    that ships with somebody else's address in it is a bug waiting to be shipped."""
    if no_email:
        return "", ""
    notify = (cli_email or config.get("notify_email") or "").strip()
    sender = (cli_from or config.get("email_from") or "").strip()
    if not notify:
        raise ConfigError(
            "no alert recipient: pass --notify-email, set 'notify_email' in the "
            "config, or pass --no-email to run detection only")
    if not sender:
        raise ConfigError(
            "no alert sender: pass --email-from or set 'email_from' in the config. "
            "Its domain must be verified on the Resend account behind RESEND_API_KEY")
    return notify, sender


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def decode_body(raw: bytes, headers: Any) -> bytes:
    """Undo Content-Encoding so a marker check reads text, not a compressed blob.

    This is not hypothetical tidiness. www.python.org gzips its homepage even when
    the request asks for `identity`, so without this a perfectly healthy site fails
    its own marker check and the monitor pages someone at 3am over nothing.

    An encoding the standard library cannot undo (`br`) is returned untouched: a
    check that then fails is a real miss, not a silent pass.
    """
    encoding = ""
    try:
        encoding = (headers.get("Content-Encoding") or "").strip().lower()
    except Exception:  # noqa: BLE001 - a stub http() may pass anything through
        return raw
    if not encoding or encoding == "identity":
        return raw
    try:
        if encoding == "gzip":
            return gzip.decompress(raw)
        if encoding == "deflate":
            try:
                return zlib.decompress(raw)
            except zlib.error:
                return zlib.decompress(raw, -zlib.MAX_WBITS)
    except Exception:  # noqa: BLE001 - a truncated or mislabelled body
        return raw
    return raw


def make_http(user_agent: str, timeout: int) -> Callable[..., tuple[int | None, bytes]]:
    def http(url: str, method: str = "GET", data: bytes | None = None,
             extra_headers: dict[str, str] | None = None) -> tuple[int | None, bytes]:
        headers = {"User-Agent": user_agent, "Accept-Encoding": "identity"}
        if extra_headers:
            headers.update(extra_headers)
        try:
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status, decode_body(response.read(), response.headers)
        except urllib.error.HTTPError as exc:
            # A 401/403/404 is a result, not an error: some checks expect one.
            try:
                return exc.code, decode_body(exc.read(), exc.headers)
            except Exception:
                return exc.code, b""
        except Exception as exc:  # noqa: BLE001 - DNS, TLS, timeout all land here
            return None, f"ERR:{type(exc).__name__}:{exc}"[:300].encode()
    return http


def body_text(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "ignore")
    return str(value)


def dig(payload: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(payload, dict):
            return None
        payload = payload.get(part)
    return payload


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def run_check(host: str, check: dict[str, Any], http) -> tuple[bool, str]:
    kind = check.get("type", "status")
    scheme = check.get("scheme", "https")
    url = f"{scheme}://{host}{check.get('path', '/')}"

    if kind == "status":
        allow = [int(code) for code in check.get("allow", [])] or None
        status, _ = http(url)
        if allow is not None:
            if status in allow:
                return True, f"status={status} (allowed {allow})"
            return False, f"status={status} (expected one of {allow})"
        if status is not None and 200 <= status < 400:
            return True, f"status={status}"
        return False, f"status={status}"

    if kind == "marker":
        marker = str(check["marker"])
        expect = int(check.get("expect_status", 200))
        status, body = http(url)
        if status != expect:
            return False, f"status={status} (expected {expect})"
        if marker in body_text(body):
            return True, f"status={status} marker {marker!r} present"
        # This is the failure a bare 200 check misses.
        return False, (f"status={status} but marker {marker!r} missing "
                       f"(suspended deployment, empty build, or wrong origin?)")

    if kind == "json":
        field = str(check["field"])
        expect = int(check.get("expect_status", 200))
        status, body = http(url)
        if status != expect:
            return False, f"{check.get('path', '/')} status={status} (expected {expect})"
        try:
            payload = json.loads(body_text(body))
        except json.JSONDecodeError as exc:
            return False, f"status={status} but body is not JSON: {exc}"
        actual = dig(payload, field)
        if "equals" in check:
            if actual == check["equals"]:
                return True, f"status={status} {field}={actual!r}"
            return False, f"status={status} {field}={actual!r} (expected {check['equals']!r})"
        if "contains" in check:
            if str(check["contains"]).lower() in str(actual).lower():
                return True, f"status={status} {field}={actual!r}"
            return False, (f"status={status} {field}={actual!r} "
                           f"(expected to contain {check['contains']!r})")
        if actual is not None:
            return True, f"status={status} {field}={actual!r}"
        return False, f"status={status} but {field} is absent"

    return False, f"unsupported check type {kind!r}"


def run_post_check(host: str, post_check: dict[str, Any], http) -> tuple[bool, str]:
    """An authenticated-write-path probe.

    A site whose homepage is fine can still have a broken write path: a
    misconfigured origin or CSRF setting makes every logged-in action fail while
    the marketing page serves 200. Declare the signature of that break and this
    catches it.
    """
    scheme = post_check.get("scheme", "https")
    url = f"{scheme}://{host}{post_check.get('path', '/')}"
    body = post_check.get("body")
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    headers.update(post_check.get("headers") or {})
    if post_check.get("origin"):
        headers["Origin"] = str(post_check["origin"])

    status, raw = http(url, method=post_check.get("method", "POST"),
                       data=data, extra_headers=headers)
    text = body_text(raw)

    fail_if = post_check.get("fail_if") or {}
    if fail_if:
        status_hit = "status" not in fail_if or status == int(fail_if["status"])
        body_hit = ("body_contains" not in fail_if
                    or str(fail_if["body_contains"]).lower() in text.lower())
        if status_hit and body_hit:
            return False, (f"write path status={status} matched the declared failure "
                           f"signature {json.dumps(fail_if, sort_keys=True)}")
    ok_status = [int(code) for code in post_check.get("ok_status", [200, 401, 403])]
    if status in ok_status:
        return True, "write path ok"
    return False, f"write path status={status} (expected one of {ok_status})"


# --------------------------------------------------------------------------- #
# state
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", delete=False) as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


# --------------------------------------------------------------------------- #
# email
# --------------------------------------------------------------------------- #
def send_email(subject: str, text: str, notify: str, sender: str,
               user_agent: str) -> tuple[bool, str]:
    """Send through Resend. The key is read from the environment inside this
    function and never logged, echoed or written to a file."""
    key = (os.environ.get("RESEND_API_KEY") or "").strip()
    if not key:
        return False, "RESEND_API_KEY not set; detection ran, no email sent"
    payload = json.dumps({"from": sender, "to": [notify],
                          "subject": subject, "text": text}).encode()
    try:
        req = urllib.request.Request(
            "https://api.resend.com/emails", data=payload, method="POST",
            # The User-Agent is required: api.resend.com sits behind a CDN that
            # rejects the default Python-urllib agent with a 403.
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "User-Agent": user_agent})
        with urllib.request.urlopen(req, timeout=20) as response:
            return True, f"sent ({response.status})"
    except Exception as exc:  # noqa: BLE001
        return False, f"send failed: {type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def probe(config: dict[str, Any], http) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for entry in config["domains"]:
        host = str(entry["host"])
        tier = entry.get("tier", "standard")
        up, detail = run_check(host, entry.get("check") or {"type": "status"}, http)
        if up and entry.get("post_check"):
            post_ok, post_detail = run_post_check(host, entry["post_check"], http)
            if post_ok:
                detail = f"{detail} + {post_detail}"
            else:
                up, detail = False, post_detail
        results[label_of(entry)] = {"tier": tier, "up": up, "detail": detail}
    return results


def transitions_for(results: dict[str, dict[str, Any]],
                    previous: dict[str, str]) -> tuple[list[tuple[str, str, str]], dict[str, str]]:
    changes: list[tuple[str, str, str]] = []
    current: dict[str, str] = {}
    for host, result in results.items():
        if result["tier"] != "critical":
            continue
        state = "up" if result["up"] else "down"
        current[host] = state
        was = previous.get(host)
        # A host with no previous state is new, not a transition. Adding a domain
        # must never page anyone.
        if was is not None and was != state:
            changes.append((host, "DOWN" if state == "down" else "RECOVERED",
                            result["detail"]))
    return changes, current


def render_report(results: dict[str, dict[str, Any]],
                  changes: list[tuple[str, str, str]], email_note: str) -> str:
    critical = {h: r for h, r in results.items() if r["tier"] == "critical"}
    crit_down = sorted(h for h, r in critical.items() if not r["up"])
    up_count = sum(1 for r in results.values() if r["up"])
    lines = [f"# Domain uptime — {now_iso()}", "",
             f"**{up_count}/{len(results)} up.** "
             f"Critical: {len(critical) - len(crit_down)}/{len(critical)} up."]
    if crit_down:
        lines += ["", "## Critical down", ""]
        lines += [f"- `{h}` — {results[h]['detail']}" for h in crit_down]
    if changes:
        lines += ["", "## State changes this run", ""]
        lines += [f"- {kind}: `{host}` — {detail}" for host, kind, detail in changes]
        lines += ["", f"Alert: {email_note}"]
    lines += ["", "## All domains", "", "| domain | tier | state | detail |", "|---|---|---|---|"]
    for host, result in results.items():
        lines.append(f"| {host} | {result['tier']} | {'UP' if result['up'] else 'DOWN'} "
                     f"| {result['detail']} |")
    return "\n".join(lines) + "\n"


def run(config: dict[str, Any], state_path: Path, report_path: Path,
        notify: str, sender: str, http=None, send: bool = True) -> dict[str, Any]:
    user_agent = str(config.get("user_agent") or DEFAULT_USER_AGENT)
    http = http or make_http(user_agent,
                             int(config.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS))

    results = probe(config, http)
    previous = load_state(state_path).get("status", {})
    changes, current = transitions_for(results, previous)

    email_note = "no state change, nothing sent"
    if changes:
        downs = [c for c in changes if c[1] == "DOWN"]
        ups = [c for c in changes if c[1] == "RECOVERED"]
        parts = ([f"{len(downs)} DOWN"] if downs else []) + \
                ([f"{len(ups)} recovered"] if ups else [])
        subject = ("Uptime: " + ", ".join(parts)
                   + f" ({', '.join(host for host, _, _ in changes)})")
        critical = [h for h, r in results.items() if r["tier"] == "critical"]
        crit_down = [h for h in critical if not results[h]["up"]]
        text = "\n".join(
            [f"Domain uptime state change at {now_iso()}:", ""]
            + [f"  [{kind}] {host} — {detail}" for host, kind, detail in changes]
            + ["", f"Critical set: {len(critical) - len(crit_down)}/{len(critical)} up."])
        if not send or not notify:
            email_note = "sending disabled for this run"
        else:
            ok, email_note = send_email(subject, text, notify, sender, user_agent)
            if not ok:
                # A send failure must never mask the detection result.
                print(f"[email] {email_note}", file=sys.stderr)

    save_state(state_path, {"status": current, "updated_at": now_iso()})
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(results, changes, email_note), encoding="utf-8")

    critical_down = sorted(h for h, r in results.items()
                           if r["tier"] == "critical" and not r["up"])
    return {"up": sum(1 for r in results.values() if r["up"]), "total": len(results),
            "critical_down": critical_down,
            "standard_down": sorted(h for h, r in results.items()
                                    if r["tier"] != "critical" and not r["up"]),
            "state_changes": [f"{kind}:{host}" for host, kind, _ in changes],
            "email": email_note, "report_path": str(report_path), "results": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, type=Path,
                        help="JSON config listing the domains and their checks")
    parser.add_argument("--state", type=Path, default=Path(".uptime/state.json"),
                        help="state file; alerts fire on change against this")
    parser.add_argument("--report", type=Path, default=Path("out/report.md"),
                        help="markdown status report written every run")
    parser.add_argument("--notify-email", default=None,
                        help="alert recipient; required unless --no-email")
    parser.add_argument("--email-from", default=None,
                        help="alert sender, e.g. 'Uptime <uptime@yourdomain>'")
    parser.add_argument("--no-email", action="store_true",
                        help="detect and report only, never send")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        notify, sender = resolve_notify(config, args.notify_email,
                                        args.email_from, args.no_email)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    try:
        result = run(config, args.state, args.report, notify, sender,
                     send=not args.no_email)
    except Exception as exc:  # noqa: BLE001
        print(f"uptime probe failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "results"},
                         sort_keys=True, indent=2))
    else:
        print(f"{result['up']}/{result['total']} up | "
              f"critical down: {result['critical_down'] or 'none'} | "
              f"state changes: {result['state_changes'] or 'none'} | "
              f"email: {result['email']}")
    return 1 if result["critical_down"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
