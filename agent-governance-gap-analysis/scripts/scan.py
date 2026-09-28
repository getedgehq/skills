#!/usr/bin/env python3
# Copyright 2026 Cakewalk Technology GmbH
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Read-only inspection for the AI Agent Governance Gap Analysis.

Finds AI agent configurations, the systems they can reach, credentials sitting in
plain text, and whether any permission check stands between an agent and a tool call.

SAFETY PROPERTIES — these are enforced here, not left to judgement:
  * Read-only. Opens files. Never writes, moves or deletes anything.
  * No network. Imports no networking library and makes no request.
  * Secret values never leave this process. A match is reported as key name,
    pattern label, file, line number and value length — never the value, never a
    prefix, never a fragment. Values are not stored in the result structure at all.
  * Only known agent-config locations are examined. No general sweep of the home
    folder, no documents, no mail, no browser data.
  * Shell history is skipped unless --include-history is passed explicitly.

Usage:
    python3 scan.py                  # human-readable summary (default)
    python3 scan.py --json           # machine-readable, same content
    python3 scan.py --root ~/work    # also sweep project configs under this folder
    python3 scan.py --include-history
    python3 scan.py --paths          # list every location that would be examined

Stdlib only. Python 3.8+.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

HOME = Path.home()
MAX_FILE_BYTES = 2_000_000
MAX_PROJECT_DEPTH = 4
SKIP_DIRS = {
    "node_modules", ".git", "venv", ".venv", "dist", "build", "__pycache__",
    "Library", ".Trash", ".cache", "site-packages", ".next", "target",
}

# ---------------------------------------------------------------- secrets

SECRET_PATTERNS = [
    ("Anthropic API key",   re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI API key",      re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("GitHub PAT",          re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained", re.compile(r"\bgithub_" r"pat_[A-Za-z0-9_]{20,}")),
    ("GitLab PAT",          re.compile(r"\bglpat-[A-Za-z0-9_\-]{15,}")),
    ("Slack token",         re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("AWS access key id",   re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key",      re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("JWT",                 re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.")),
    ("Bearer token",        re.compile(r"Bearer\s+[A-Za-z0-9_\-.=]{20,}")),
    ("Private key block",   re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY")),
    ("Stripe live key",     re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{10,}")),
]

# Credential embedded in a connection string: scheme://user:secret@host
# Matches postgres, mysql, mongodb, redis, amqp, http(s) and anything else
# using URI userinfo. The password is located, never captured for output.
URI_USERINFO = re.compile(
    r"\b(?P<scheme>[a-z][a-z0-9+.\-]{1,20})://(?P<user>[^\s:/@\"']{1,64}):(?P<pw>[^\s@/\"']{1,256})@(?P<host>[^\s/\"'?]{1,255})",
    re.I)

# Credential passed as a URL query parameter: ?api_key=…  ?access_token=…
# The parameter NAME is captured for reporting; the value only for its length.
URL_QUERY_CRED = re.compile(
    r"[?&](?P<param>[A-Za-z0-9_\-]*(?:api[_\-]?key|access[_\-]?token|auth[_\-]?token|"
    r"token|secret|password|passwd|signature|sig|key)[A-Za-z0-9_\-]*)=(?P<val>[^&\s\"'#]{8,})",
    re.I)

# A key name is only ever read from the KEY side of a pair. It is never
# derived from the value, because a value containing the word "secret" would
# otherwise be printed as its own name. See safe_key_name().
SECRET_KEY_NAME = re.compile(
    r"^[\s\"'\[{,]*([A-Za-z0-9_.\-]{1,64})[\"']*\s*$")
CREDENTIAL_WORD = re.compile(
    r"(TOKEN|SECRET|PASSWORD|PASSWD|APIKEY|API_KEY|ACCESS_KEY|PRIVATE_KEY|"
    r"CREDENTIAL|CLIENT_SECRET|AUTH|BEARER|PASSPHRASE)", re.I)

# Settings whose value NAMES A COMMAND that fetches a credential. This is the
# better practice, not a finding — the secret is not in the file.
CREDENTIAL_HELPERS = {
    "apikeyhelper", "credentialhelper", "credential.helper", "tokenhelper",
    "authhelper", "awsauthrefresh", "credentialprocess", "credential_process",
}

# Placeholder vocabulary. Deliberately broad: a suppressed real secret still
# shows up as its file being flagged, whereas a wall of fake ones means the
# real findings never get read.
PLACEHOLDER_WORD = re.compile(
    r"(?i)(your[-_ ]?|my[-_ ]?|replace|changeme|change[-_]me|placeholder|example|"
    r"sample|dummy|fake|insert|here|todo|tbd|redacted|xxx+|\.\.\.|\*{3,}|"
    r"^test$|_test_|^sk_test|^pk_test|^none$|^null$|^string$|^value$|^abc123)")
PLACEHOLDER_EXACT = re.compile(
    r"^\s*(|<[^>]*>|\$\{[^}]*\}|\$[A-Z_][A-Z0-9_]*|x{3,}|\*{3,}|\.{3,})\s*$", re.I)

# Values that live in an OS keychain or are injected at runtime are a better
# posture than a literal, and are counted separately rather than as a finding.
INDIRECTION = re.compile(
    r"\$\{[^}]+\}|\$[A-Z_][A-Z0-9_]*|op://|keychain|vault:|aws-vault|1password|"
    r"secretRef|pass:|gopass|\bkeyring\b", re.I)

# Generic high-entropy token, used only by the redactor as a safety net for
# strings that must be displayed (commands, non-URL targets).
GENERIC_TOKEN = re.compile(r"\b(?=[A-Za-z0-9_\-]{20,})(?=[^\s]*\d)(?=[^\s]*[A-Za-z])[A-Za-z0-9_\-]{20,}\b")

BYPASS_FLAGS = [
    "--dangerously-skip-permissions", "bypassPermissions", "--yolo",
    "--auto-approve", "--autoapprove", "--no-confirm", "--force-approve",
    "acceptEdits", "--allow-all-tools",
]

# Example/template files exist to hold fake values. Never scanned.
EXAMPLE_FILE = re.compile(
    r"\.(example|sample|template|dist|defaults?)$|"
    r"^\.env\.(example|sample|template|dist|defaults?|test|ci)$|"
    r"(example|sample|template)\.(json|ya?ml|env)$", re.I)


def looks_placeholder(value):
    """True if this value is obviously not a live credential."""
    v = (value or "").strip().strip('",\'')
    if not v or PLACEHOLDER_EXACT.match(v):
        return True
    if PLACEHOLDER_WORD.search(v):
        return True
    if len(v) < 8:
        return True
    if len(set(v)) <= 4:                     # "aaaaaaaaaaaa", "123123123123"
        return True
    return False


def split_kv(line):
    """Split a config line into (key_side, value_side) on the FIRST separator.

    Everything downstream reads the key from the left and the secret from the
    right, and only the left is ever emitted.
    """
    for sep in (":", "="):
        i = line.find(sep)
        if i > -1:
            return line[:i], line[i + 1:]
    return "", line


def key_before(line, pos):
    """Name of the key immediately preceding position `pos`.

    Reads ONLY the text to the left of the located secret, so it is structurally
    incapable of returning the secret itself — the bug this replaced.
    """
    left = line[:pos]
    names = re.findall(r"([A-Za-z0-9_.\-]{1,64})[\"']?\s*[:=]", left)
    if not names:
        return None
    name = names[-1]
    return name if CREDENTIAL_WORD.search(name) else None


def safe_key_name(key_side):
    """Emit a key name only if it really is a short identifier from the key side."""
    m = SECRET_KEY_NAME.match(key_side.strip().split(",")[-1])
    if not m:
        return None
    name = m.group(1)
    if len(name) > 64 or not CREDENTIAL_WORD.search(name):
        return None
    return name


# --------------------------------------------------------------- locations

def global_config_paths():
    """Known global agent-config locations. Absolute, non-recursive."""
    p = [
        HOME / ".claude.json",
        HOME / ".claude" / "settings.json",
        HOME / ".claude" / "settings.local.json",
        HOME / ".cursor" / "mcp.json",
        HOME / ".codeium" / "windsurf" / "mcp_config.json",
        HOME / ".continue" / "config.json",
        HOME / ".aider.conf.yml",
        HOME / ".config" / "github-copilot" / "mcp.json",
        HOME / ".gemini" / "settings.json",
        HOME / ".config" / "zed" / "settings.json",
    ]
    if sys.platform == "darwin":
        appsup = HOME / "Library" / "Application Support"
        p += [
            appsup / "Claude" / "claude_desktop_config.json",
            appsup / "Code" / "User" / "settings.json",
            appsup / "Code" / "User" / "mcp.json",
            appsup / "Cursor" / "User" / "settings.json",
        ]
    elif sys.platform.startswith("win"):
        appdata = Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming"))
        p += [
            appdata / "Claude" / "claude_desktop_config.json",
            appdata / "Code" / "User" / "settings.json",
            appdata / "Code" / "User" / "mcp.json",
        ]
    else:
        cfg = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config"))
        p += [
            cfg / "Claude" / "claude_desktop_config.json",
            cfg / "Code" / "User" / "settings.json",
            cfg / "Code" / "User" / "mcp.json",
        ]
    return p


PROJECT_FILENAMES = {
    ".mcp.json", "mcp.json", ".env", ".env.local", ".env.development",
    "claude_desktop_config.json", "settings.json", "settings.local.json",
}
PROJECT_PARENTS = {".claude", ".cursor", ".vscode", ".continue", ".gemini"}


def project_config_paths(root, max_depth=MAX_PROJECT_DEPTH):
    """Project-level agent config beneath root. Bounded depth, skips heavy dirs."""
    out, root = [], Path(root).expanduser()
    if not root.is_dir():
        return out
    base_depth = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        d = Path(dirpath)
        if len(d.parts) - base_depth >= max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS and
                       (not x.startswith(".") or x in PROJECT_PARENTS)]
        for f in filenames:
            if EXAMPLE_FILE.search(f):          # .env.example, config.sample, …
                continue
            if f in PROJECT_FILENAMES or f.startswith(".env."):
                if f in {"settings.json", "settings.local.json", "mcp.json"} and d.name not in PROJECT_PARENTS:
                    continue
                out.append(d / f)
    return out


def history_paths():
    return [HOME / ".zsh_history", HOME / ".bash_history", HOME / ".zshrc",
            HOME / ".bashrc", HOME / ".profile", HOME / ".zprofile"]


# ------------------------------------------------------------------ io

def read_lines(path):
    """Return (lines, status). Never raises. Content stays local to the caller."""
    try:
        if not path.is_file():
            return None, "absent"
        if path.stat().st_size > MAX_FILE_BYTES:
            return None, "too_large"
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines(), "read"
    except PermissionError:
        return None, "no_permission"
    except OSError:
        return None, "unreadable"


def parse_jsonish(lines):
    """Best-effort parse of JSON that may carry // comments or trailing commas."""
    if lines is None:
        return None
    text = "\n".join(lines)
    for attempt in (text,
                    re.sub(r"^\s*//.*$", "", text, flags=re.M),
                    re.sub(r",(\s*[}\]])", r"\1",
                           re.sub(r"^\s*//.*$", "", text, flags=re.M))):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


# --------------------------------------------------------------- analysis

def sanitize_url(u):
    """Rebuild a URL from its parsed parts, dropping every value that could be
    a credential. Structural, so an unknown vendor's key is dropped too."""
    try:
        p = urlsplit(u)
    except Exception:
        return "<unparseable url>"
    if not p.scheme or not p.netloc:
        return redact_text(u)
    host = p.hostname or ""
    if p.port:
        host = f"{host}:{p.port}"
    if p.username:
        host = f"{p.username}:<redacted>@{host}" if p.password else f"{p.username}@{host}"
    out = f"{p.scheme}://{host}{p.path}"
    if p.query:
        keys = []
        for part in p.query.split("&"):
            k = part.split("=", 1)[0]
            if k:
                keys.append(f"{k}=<redacted>")
        if keys:
            out += "?" + "&".join(keys)
    return out[:200]


def redact_text(value):
    """Safety net for strings that are not URLs: known patterns, then any
    generic high-entropy token."""
    if not isinstance(value, str):
        return value
    out = value
    for _, pat in SECRET_PATTERNS:
        out = pat.sub("<redacted>", out)
    out = URI_USERINFO.sub(lambda m: f"{m.group('scheme')}://{m.group('user')}:<redacted>@{m.group('host')}", out)
    out = GENERIC_TOKEN.sub("<redacted>", out)
    return (out[:120] + "\u2026") if len(out) > 120 else out


def safe(value):
    """The single exit point for any string that leaves this process."""
    if not isinstance(value, str):
        return value
    return sanitize_url(value) if "://" in value else redact_text(value)


def find_secrets(path, lines):
    """Locate credentials without ever retaining or emitting their value.

    Returns (findings, suppressed, indirect). A finding carries the key name
    read from the key side of the pair, the kind, file, line and length —
    the value itself is never written into the structure.
    """
    findings, suppressed, indirect = [], [], 0
    if lines is None:
        return findings, suppressed, indirect

    for n, line in enumerate(lines, 1):
        if len(line) > 4000:
            line = line[:4000]
        key_side, value_side = split_kv(line)
        key = safe_key_name(key_side)
        value = value_side.strip().strip('",\'')

        # Credential helper: the value names a command, the secret is elsewhere.
        bare_key = key_side.strip().strip('"\' \t{[,:').lower()
        if bare_key in CREDENTIAL_HELPERS:
            indirect += 1
            continue

        # 1. Connection-string password (scheme://user:pw@host)
        m = URI_USERINFO.search(line)
        if m and not looks_placeholder(m.group("pw")):
            findings.append({
                "file": str(path), "line": n,
                "kind": f"{m.group('scheme').lower()} connection-string password",
                "key_name": key or key_before(line, m.start()), "value_length": len(m.group("pw")),
                "context": safe(f"{m.group('scheme')}://{m.group('user')}:x@{m.group('host')}"),
            })
            continue

        # 2. Credential in a URL query string
        q = URL_QUERY_CRED.search(line)
        if q and not looks_placeholder(q.group("val")):
            host = ""
            um = re.search(r"(?P<scheme>https?)://(?P<host>[^/\s\"']+)", line, re.I)
            if um:
                host = f"{um.group('scheme')}://{um.group('host')}"
            findings.append({
                "file": str(path), "line": n,
                "kind": "credential in URL query string",
                "key_name": q.group("param"), "value_length": len(q.group("val")),
                "context": safe(host) or None,
            })
            continue

        # 3. Known vendor credential format
        hit = None
        for label, pat in SECRET_PATTERNS:
            mm = pat.search(line)
            if mm:
                hit = (label, mm.group(0))
                break
        if hit:
            label, matched = hit
            if looks_placeholder(matched):
                suppressed.append({"file": str(path), "line": n, "why": "placeholder value"})
            else:
                findings.append({"file": str(path), "line": n, "kind": label,
                                 "key_name": key or key_before(line, mm.start()),
                                 "value_length": len(matched), "context": None})
            continue

        # 4. Credential-named key holding something literal
        if key:
            if INDIRECTION.search(value):
                indirect += 1
            elif looks_placeholder(value):
                suppressed.append({"file": str(path), "line": n, "why": "placeholder value"})
            else:
                findings.append({"file": str(path), "line": n, "kind": "credential-named value",
                                 "key_name": key, "value_length": len(value), "context": None})

    return findings, suppressed, indirect


REACHES = [
    ("GitHub", r"github"), ("GitLab", r"gitlab"), ("Slack", r"slack"),
    ("Notion", r"notion"), ("Google Workspace", r"google|gmail|gdrive|gcal"),
    ("Jira/Atlassian", r"jira|atlassian|confluence"), ("Linear", r"linear"),
    ("Database", r"postgres|mysql|sqlite|mongo|snowflake|bigquery|database"),
    ("Filesystem", r"filesystem|^fs$|file-system"), ("Shell/exec", r"shell|bash|exec|terminal|command"),
    ("Browser", r"browser|puppeteer|playwright|chrome"), ("Cloud", r"\baws\b|azure|gcp|kubernetes|k8s"),
    ("Email", r"email|smtp|imap|outlook"), ("CRM", r"hubspot|salesforce|pipedrive"),
    ("Payments", r"stripe|paypal|billing"),
]
HIGH_BLAST = {"Filesystem", "Shell/exec", "Browser", "Cloud", "Database", "Payments", "Email"}


def classify_reach(name, command_blob):
    hay = f"{name} {command_blob}".lower()
    return sorted({label for label, pat in REACHES if re.search(pat, hay)})


def extract_servers(path, data):
    """Pull MCP server definitions out of a parsed config, whatever its shape."""
    servers = []
    if not isinstance(data, dict):
        return servers

    def walk(obj, depth=0):
        if depth > 4 or not isinstance(obj, dict):
            return
        for key in ("mcpServers", "mcp_servers", "servers", "context_servers"):
            block = obj.get(key)
            if isinstance(block, dict):
                for name, cfg in block.items():
                    if not isinstance(cfg, dict):
                        continue
                    blob = " ".join(str(cfg.get(k, "")) for k in
                                    ("command", "url", "type", "transport")) + " " + \
                           " ".join(str(a) for a in cfg.get("args", []) if isinstance(a, (str, int)))
                    env_keys = sorted(cfg.get("env", {}).keys()) if isinstance(cfg.get("env"), dict) else []
                    servers.append({
                        "name": name,
                        "file": str(path),
                        "transport": cfg.get("type") or cfg.get("transport") or
                                     ("http" if cfg.get("url") else "stdio"),
                        "target": safe(str(cfg.get("url") or cfg.get("command") or "")),
                        "env_keys": env_keys,          # names only, never values
                        "reaches": classify_reach(name, blob),
                    })
        for v in obj.values():
            if isinstance(v, dict):
                walk(v, depth + 1)

    walk(data)
    return servers


def extract_controls(path, data, lines):
    """Permission rules, hooks, and anything that switches review off."""
    c = {"allow": 0, "deny": 0, "ask": 0, "default_mode": None,
         "hooks": [], "bypass": [], "auto_approve_servers": None}
    if isinstance(data, dict):
        def walk(obj, depth=0):
            if depth > 5 or not isinstance(obj, dict):
                return
            perms = obj.get("permissions")
            if isinstance(perms, dict):
                for k in ("allow", "deny", "ask"):
                    v = perms.get(k)
                    if isinstance(v, list):
                        c[k] += len(v)
                if perms.get("defaultMode"):
                    c["default_mode"] = perms["defaultMode"]
            hooks = obj.get("hooks")
            if isinstance(hooks, dict):
                c["hooks"] += [k for k in hooks.keys() if k not in c["hooks"]]
            if obj.get("enableAllProjectMcpServers") is True:
                c["auto_approve_servers"] = True
            for v in obj.values():
                if isinstance(v, dict):
                    walk(v, depth + 1)
        walk(data)
    if lines:
        blob = "\n".join(lines)
        c["bypass"] = sorted({f for f in BYPASS_FLAGS if f in blob})
    return c


SANDBOX_HINTS = [
    ("/.dockerenv", lambda: Path("/.dockerenv").exists()),
    ("/run/.containerenv", lambda: Path("/run/.containerenv").exists()),
    ("container cgroup", lambda: _cgroup_hit()),
    ("no home config at all", lambda: not any(p.exists() for p in global_config_paths())),
]


def _cgroup_hit():
    try:
        with open("/proc/1/cgroup", "r", errors="replace") as fh:
            return bool(re.search(r"docker|kubepods|containerd|lxc", fh.read()))
    except Exception:
        return False


def sandbox_signals():
    hits = []
    for label, fn in SANDBOX_HINTS:
        try:
            if fn():
                hits.append(label)
        except Exception:
            pass
    return hits


# ------------------------------------------------------------------ run

def scan(root=None, include_history=False):
    result = {
        "sandbox_signals": sandbox_signals(),
        "examined": [], "not_read": [], "servers": [], "secrets": [], "suppressed": [],
        "controls": {"allow": 0, "deny": 0, "ask": 0, "default_mode": None,
                     "hooks": [], "bypass": [], "auto_approve_servers": None},
        "indirection_count": 0,
    }
    targets = list(global_config_paths())
    if root:
        targets += project_config_paths(root)
    if include_history:
        targets += history_paths()

    seen = set()
    for path in targets:
        if path in seen:
            continue
        seen.add(path)
        lines, status = read_lines(path)
        if status != "read":
            if status != "absent":
                result["not_read"].append({"file": str(path), "reason": status})
            continue
        result["examined"].append(str(path))

        data = parse_jsonish(lines) if path.suffix in {".json", ""} or path.name.endswith(".json") else None
        result["servers"] += extract_servers(path, data)

        found, suppressed, indirect = find_secrets(path, lines)
        result["secrets"] += found
        result["suppressed"] += suppressed
        result["indirection_count"] += indirect

        ctl = extract_controls(path, data, lines)
        for k in ("allow", "deny", "ask"):
            result["controls"][k] += ctl[k]
        result["controls"]["default_mode"] = result["controls"]["default_mode"] or ctl["default_mode"]
        result["controls"]["hooks"] = sorted(set(result["controls"]["hooks"]) | set(ctl["hooks"]))
        result["controls"]["bypass"] = sorted(set(result["controls"]["bypass"]) | set(ctl["bypass"]))
        result["controls"]["auto_approve_servers"] = (result["controls"]["auto_approve_servers"]
                                                      or ctl["auto_approve_servers"])
    result["evidence"] = map_to_checks(result)
    return result


def map_to_checks(r):
    """Translate findings into per-check proposals. Never decides — proposes."""
    ev, ctl = {}, r["controls"]
    n_servers, n_secrets = len(r["servers"]), len(r["secrets"])
    high = sorted({x for s in r["servers"] for x in s["reaches"] if x in HIGH_BLAST})

    ev["inv1"] = ("gap", f"{n_servers} agent connections found by scanning. A scan is not a registry — "
                         "ask whether a central one exists.") if n_servers else \
                 ("ask", "No agent connections found here; cannot speak to an org registry.")
    ev["inv3"] = ("gap", f"Connections reach: {', '.join(sorted({x for s in r['servers'] for x in s['reaches']})) or 'unclassified'}. "
                         f"{'High blast radius: ' + ', '.join(high) + '. ' if high else ''}"
                         "Confirm the user knew all of these.") if n_servers else ("ask", "Nothing found to compare.")
    ev["inv4"] = ("ask", "Attribution cannot be read from config. Ask whether each agent ties to a named person.")

    if n_secrets:
        ev["cred1"] = ("fail", f"{n_secrets} credential(s) in plain text in agent config. A compromised session "
                               "yields replayable credentials.")
        ev["cred2"] = ("fail", "Credentials sit in the agent runtime's own config, not managed separately.")
        ev["cred4"] = ("ask", "Static keys in config are long-lived by construction — confirm actual expiry.")
    else:
        ev["cred1"] = ("pass?", f"No plaintext credentials in the files read"
                                f"{' (' + str(r['indirection_count']) + ' via env/keychain indirection)' if r['indirection_count'] else ''}. "
                                "Only proves these files.")
        ev["cred2"] = ("ask", "No literal credentials here. Ask where they are actually held and rotated.")

    if ctl["bypass"]:
        ev["hitl1"] = ("fail", f"Permission bypass in use: {', '.join(ctl['bypass'])}. Nothing pauses for review.")
        ev["hitl3"] = ("fail", "With bypass enabled, denial cannot block anything.")
        ev["pol1"] = ("fail", "Bypass flags defeat any in-path policy check.")
        ev["priv1"] = ("fail", "Bypass grants standing, unreviewed privilege.")
    else:
        has_rules = bool(ctl["deny"] or ctl["ask"] or ctl["hooks"])
        ev["pol1"] = ("partial" if has_rules else "gap",
                      f"{ctl['deny']} deny, {ctl['ask']} ask, {ctl['allow']} allow rules; "
                      f"hooks: {', '.join(ctl['hooks']) or 'none'}. Local to this machine only."
                      if has_rules else "No in-path permission rules or hooks found.")
        ev["hitl1"] = ("partial" if (ctl["ask"] or "PreToolUse" in ctl["hooks"]) else "gap",
                       "Review prompts exist on this machine." if (ctl["ask"] or "PreToolUse" in ctl["hooks"])
                       else "Nothing found that pauses a sensitive action.")
        ev["priv1"] = ("gap", f"{ctl['allow']} standing allow rules"
                              + (f"; defaultMode={ctl['default_mode']}" if ctl["default_mode"] else "")) \
                      if ctl["allow"] or ctl["default_mode"] else ("ask", "No standing-permission signal found.")

    ev["pol3"] = ("ask", "Whether evaluation is deterministic cannot be read from config.")
    ev["priv3"] = ("partial" if ctl["deny"] and ctl["allow"] else "ask",
                   "Rules distinguish some actions — check whether the split is read vs write/send/delete.")
    ev["aud1"] = ("ask", "No durable audit sink found locally. Local transcripts are not an audit trail.")
    return ev


# ------------------------------------------------------------- rendering

PER_FILE_CAP = 5


def render(r, show_all=False):
    L = []
    if r["sandbox_signals"]:
        L += ["!! SANDBOX SIGNALS: " + ", ".join(r["sandbox_signals"]),
              "!! These files may belong to a container, NOT the user's computer.",
              "!! Confirm with the user before reporting any of this as their setup.", ""]
    L.append(f"Examined {len(r['examined'])} file(s); {len(r['not_read'])} unreadable.")
    for x in r["not_read"]:
        L.append(f"  NOT CHECKED  {x['file']}  ({x['reason']})")

    L.append("")
    L.append(f"AGENT CONNECTIONS: {len(r['servers'])}")
    for s in r["servers"]:
        reach = ", ".join(s["reaches"]) or "unclassified"
        envs = f"  env: {', '.join(s['env_keys'])}" if s["env_keys"] else ""
        L.append(f"  - {s['name']}  [{s['transport']}]  reaches: {reach}{envs}")
        L.append(f"      from {s['file']}")
    high = sorted({x for s in r["servers"] for x in s["reaches"] if x in HIGH_BLAST})
    if high:
        L.append(f"  Highest blast radius: {', '.join(high)}")

    L.append("")
    n = len(r["secrets"])
    L.append(f"CREDENTIALS IN PLAIN TEXT: {n}   (values are never read out)")
    by_file = {}
    for s in r["secrets"]:
        by_file.setdefault(s["file"], []).append(s)
    for fpath, items in by_file.items():
        L.append(f"  {fpath}")
        shown = items if show_all else items[:PER_FILE_CAP]
        for s in shown:
            key = s["key_name"] or "unnamed"
            ln = f", {s['value_length']} chars" if s["value_length"] else ""
            ctx = f"  [{s['context']}]" if s.get("context") else ""
            L.append(f"    line {s['line']:<5} {s['kind']}: {key}{ln}{ctx}")
        if len(items) > len(shown):
            L.append(f"    … {len(items) - len(shown)} more in this file (--all to list)")
    if r["suppressed"]:
        L.append(f"  {len(r['suppressed'])} placeholder/example value(s) ignored"
                 + (" (--all to list)" if not show_all else ":"))
        if show_all:
            for s in r["suppressed"]:
                L.append(f"    {s['file']}:{s['line']}  {s['why']}")
    if r["indirection_count"]:
        L.append(f"  {r['indirection_count']} value(s) held indirectly "
                 "(env var, keychain, credential helper) — better posture, not a finding.")

    c = r["controls"]
    L += ["", "CONTROLS",
          f"  permission rules: {c['allow']} allow / {c['deny']} deny / {c['ask']} ask",
          f"  defaultMode: {c['default_mode'] or 'unset'}",
          f"  hooks: {', '.join(c['hooks']) or 'none'}",
          f"  auto-approve MCP servers: {c['auto_approve_servers'] or False}",
          f"  BYPASS FLAGS: {', '.join(c['bypass']) if c['bypass'] else 'none found'}"]

    L += ["", "PROPOSED CHECK EVIDENCE  (proposals for the user to confirm, not verdicts)"]
    for cid, (verdict, why) in r["evidence"].items():
        L.append(f"  {cid:<6} {verdict:<8} {why}")

    L += ["", "Scope: these files on this computer only. Says nothing about colleagues'",
          "machines, CI, servers, or browser-based agents. Never present as org-wide."]
    return "\n".join(L)



# ------------------------------------------------------------- self-test

# Fake tokens, split so secret scanners do not flag the fixture; the runtime strings are unchanged.
SELFTEST_SECRETS = [
    "gh" "p_" "Aa1Bb2Cc3Dd4Ee5Ff6Gg7Hh8Ii9Jj0Kk1Ll2",
    "xo" "xb-" "3310069898-4455667788-QwErTyUiOpAsDfGh",
    "sk-" "ant-" "api03-Zz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2Rr1Qq0",
    "a7f3e91c4b8d2056e1f9c3a7b5d8e204",
    "Sup3rSecretPw",
    "x7gT2qLm9Wz",
]

SELFTEST_FIXTURE = {
    ".mcp.json": """{"mcpServers":{
 "api":{"type":"http","url":"https://mcp.vendor.io/v1?api_key=%s"},
 "pg":{"command":"npx","args":["server-postgres","postgresql://admin:%s@prod-db.internal:5432/customers"]},
 "mongo":{"type":"http","url":"mongodb+srv://svc:%s@cluster0.mongodb.net"},
 "gh":{"command":"npx","env":{"GITHUB_TOKEN":"%s"}},
 "slack":{"command":"npx","env":{"SLACK_BOT_TOKEN":"%s"}},
 "ant":{"command":"npx","env":{"ANTHROPIC_API_KEY":"%s"}}
}}""",
    ".env.example": 'GITHUB_TOKEN=gh' 'p_REPLACE_ME_WITH_YOUR_TOKEN\nDB_PASSWORD=your-password-here\n',
    ".claude/settings.json": '{"apiKeyHelper":"/opt/company/bin/get-creds.sh","permissions":{"deny":["Bash(rm:*)"]}}',
}


def selftest():
    """Scan a fixture of known fake secrets, then assert that not one of them —
    nor any 8-character fragment — appears in the text or JSON output."""
    import tempfile
    s = SELFTEST_SECRETS
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".claude").mkdir()
        (root / ".mcp.json").write_text(
            SELFTEST_FIXTURE[".mcp.json"] % (s[3], s[4], s[4], s[0], s[1], s[2]), encoding="utf-8")
        (root / ".env.example").write_text(SELFTEST_FIXTURE[".env.example"], encoding="utf-8")
        (root / ".claude" / "settings.json").write_text(
            SELFTEST_FIXTURE[".claude/settings.json"], encoding="utf-8")

        r = scan(root=str(root))
        outputs = {"text": render(r, show_all=True), "json": json.dumps(r, indent=2)}

        leaks = []
        for mode, text in outputs.items():
            for secret in s:
                for i in range(max(1, len(secret) - 7)):
                    frag = secret[i:i + 8]
                    if frag in text:
                        leaks.append(f"{mode}: fragment {frag!r} of a fixture secret")
                        break

        detected = {f["kind"] for f in r["secrets"]}
        expected = ["connection-string password", "GitHub PAT", "Slack token",
                    "Anthropic API key", "URL query string"]
        missed = [e for e in expected if not any(e in d for d in detected)]
        from_example = [f for f in r["secrets"] if ".env.example" in f["file"]]

        print("SELF-TEST")
        print(f"  fixture secrets planted : {len(s)}")
        print(f"  findings reported       : {len(r['secrets'])}")
        print(f"  detected kinds          : {', '.join(sorted(detected)) or 'none'}")
        print()
        ok = True
        for label, bad, detail in [
            ("no secret material in output", leaks, leaks),
            ("expected credentials detected", missed, [f"missed: {m}" for m in missed]),
            ("example files not scanned", from_example, [f"scanned {f['file']}" for f in from_example]),
        ]:
            print(f"  {'PASS' if not bad else 'FAIL'}  {label}")
            for d in detail:
                print(f"          {d}")
            ok = ok and not bad
        print()
        print("  RESULT:", "PASS" if ok else "FAIL")
        return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Read-only AI agent governance inspection.")
    ap.add_argument("--root", help="also sweep project configs beneath this folder")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--include-history", action="store_true",
                    help="also check shell rc/history for permission-bypass flags (off by default)")
    ap.add_argument("--paths", action="store_true", help="list locations that would be examined, then exit")
    ap.add_argument("--all", action="store_true", help="show every finding, including suppressed placeholders")
    ap.add_argument("--selftest", action="store_true",
                    help="run the built-in leak test: scan a fixture of known fake secrets "
                         "and assert none of them appear in either output mode")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())

    if a.paths:
        for p in global_config_paths():
            print(("exists  " if p.exists() else "absent  ") + str(p))
        if a.root:
            for p in project_config_paths(a.root):
                print("project " + str(p))
        return

    r = scan(root=a.root, include_history=a.include_history)
    print(json.dumps(r, indent=2) if a.json else render(r, show_all=a.all))


if __name__ == "__main__":
    main()
