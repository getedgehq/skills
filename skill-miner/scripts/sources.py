"""Session-log sources for skill-miner: Claude Code, opencode, Codex CLI.

Stdlib only. Every source is read-only; opencode's sqlite is opened with
`mode=ro` via URI.

    list_sessions(kinds, n, roots=None) -> list[Session]
    iter_events(session) -> iterator of event dicts:
        {"type": "user_text", "text": str}
        {"type": "assistant_text", "text": str}
        {"type": "tool_call", "name": str, "input": str}   # input truncated to 2000
        {"type": "tool_error", "text": str}
        {"type": "usage", "output_tokens": int}

Scope parity with the original Claude-only miner: only top-level sessions are
listed. Claude subagent transcripts live in `<session>/subagents/` and were
never globbed; the equivalents are opencode child sessions (`parent_id`) and
Codex subagent threads (`thread_source == "subagent"`), which are skipped too.

opencode storage: `opencode.db` (sqlite: session / message / part tables) is
authoritative. The legacy `storage/{session,message,part}` JSON tree was
migrated into the db (`storage/migration` marker) and is no longer written.
"""
import glob
import json
import os
import re
import sqlite3
from dataclasses import dataclass, field

KINDS = ("claude", "opencode", "codex")
DEFAULT_ROOTS = {
    "claude": "~/.claude/projects",
    "opencode": "~/.local/share/opencode",
    "codex": "~/.codex/sessions",
}
MAX_INPUT = 2000

# Eval-arm working dirs produce machine sessions, not real user work.
HARNESS_RE = re.compile(r"(skill-evals.*runs|skill-forge.runs)|-(with|without)$")
# Harness filter for full cwd paths (opencode / codex): same pattern, applied
# to the whole path and to its basename.
def _is_harness_cwd(cwd):
    cwd = (cwd or "").rstrip("/")
    return bool(HARNESS_RE.search(cwd) or HARNESS_RE.search(os.path.basename(cwd)))


# User-role text that the harness injects rather than the human typing it.
INJECTED_RE = re.compile(
    r"^\s*(# AGENTS\.md instructions|<environment_context>|<user_instructions>"
    r"|<codex_internal_context|<turn_aborted>|<subagent_notification>|<user_shell_command>"
    r"|<skill>|<system-reminder|<permissions instructions>|<collaboration_mode>)",
    re.IGNORECASE,
)
IMAGE_TAG_RE = re.compile(r"<image\b[^>]*>|</image>", re.IGNORECASE)
# A whole message that is one harness-style wrapped block, e.g.
# <recommended_plugins>...</recommended_plugins>, <in-app-browser-context ...>...</...>
WRAPPED_BLOCK_RE = re.compile(r"^\s*<([a-z]+[_-][\w-]*)\b[^>]*>.*</\1>\s*$", re.DOTALL | re.IGNORECASE)


def is_injected(text):
    return bool(INJECTED_RE.search(text) or WRAPPED_BLOCK_RE.match(text))


@dataclass
class Session:
    id: str
    kind: str
    cwd: str
    mtime: float
    ref: object = field(default=None, repr=False)  # path or db locator


def _roots(roots):
    out = {k: os.path.expanduser(v) for k, v in DEFAULT_ROOTS.items()}
    for k, v in (roots or {}).items():
        if v:
            out[k] = os.path.expanduser(v)
    return out


def available_kinds(roots=None):
    r = _roots(roots)
    ok = []
    for k in KINDS:
        if k == "opencode":
            if os.path.exists(os.path.join(r[k], "opencode.db")):
                ok.append(k)
        elif os.path.isdir(r[k]):
            ok.append(k)
    return ok


# ---------------------------------------------------------------- claude

def _claude_sessions(root):
    files = glob.glob(os.path.join(root, "*", "*.jsonl"))
    files = [f for f in files if os.path.getsize(f) > 2000
             and not HARNESS_RE.search(os.path.basename(os.path.dirname(f)))]
    files.sort(key=os.path.getmtime, reverse=True)
    return [Session(id=os.path.basename(f), kind="claude",
                    cwd=os.path.basename(os.path.dirname(f)),
                    mtime=os.path.getmtime(f), ref=f) for f in files]


def _claude_events(path):
    try:
        fh = open(path, errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            msg = entry.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage") or {}
            if isinstance(usage, dict) and usage.get("output_tokens"):
                yield {"type": "usage", "output_tokens": usage.get("output_tokens") or 0}
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                text = None
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = [c.get("text", "") for c in content
                             if isinstance(c, dict) and c.get("type") == "text"]
                    text = "\n".join(p for p in parts if p)
                if text:
                    yield {"type": "user_text", "text": text}
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                t = c.get("type")
                if role == "assistant" and t == "text" and c.get("text"):
                    yield {"type": "assistant_text", "text": c["text"]}
                elif t == "tool_use":
                    yield {"type": "tool_call", "name": str(c.get("name", "")),
                           "input": json.dumps(c.get("input"), ensure_ascii=False)[:MAX_INPUT]}
                elif t == "tool_result" and c.get("is_error"):
                    text = c.get("content")
                    if isinstance(text, list):
                        text = " ".join(x.get("text", "") for x in text if isinstance(x, dict))
                    yield {"type": "tool_error", "text": str(text or "")}


# ---------------------------------------------------------------- opencode

def _oc_connect(root):
    db = os.path.join(root, "opencode.db")
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)


def _opencode_sessions(root):
    if not os.path.exists(os.path.join(root, "opencode.db")):
        return []
    con = _oc_connect(root)
    try:
        rows = con.execute(
            "SELECT s.id, s.directory, s.time_updated FROM session s "
            "WHERE s.parent_id IS NULL "
            "AND (SELECT count(*) FROM message m WHERE m.session_id = s.id) >= 2 "
            "ORDER BY s.time_updated DESC").fetchall()
    finally:
        con.close()
    return [Session(id=sid, kind="opencode", cwd=d or "", mtime=(t or 0) / 1000.0,
                    ref=(root, sid))
            for sid, d, t in rows if not _is_harness_cwd(d)]


def _opencode_events(ref):
    root, sid = ref
    con = _oc_connect(root)
    try:
        msgs = con.execute(
            "SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created, id",
            (sid,)).fetchall()
        parts = {}
        for mid, data in con.execute(
                "SELECT message_id, data FROM part WHERE session_id = ? ORDER BY time_created, id",
                (sid,)):
            parts.setdefault(mid, []).append(data)
    finally:
        con.close()
    for mid, mdata in msgs:
        try:
            m = json.loads(mdata)
        except ValueError:
            continue
        role = m.get("role")
        user_texts = []
        for pdata in parts.get(mid, []):
            try:
                p = json.loads(pdata)
            except ValueError:
                continue
            pt = p.get("type")
            if pt == "text":
                if p.get("synthetic") or p.get("ignored"):
                    continue
                text = p.get("text") or ""
                if role == "user":
                    if text.strip() and not is_injected(text):
                        user_texts.append(text)
                elif role == "assistant" and text:
                    yield {"type": "assistant_text", "text": text}
            elif pt == "tool":
                state = p.get("state") or {}
                inp = state.get("input")
                yield {"type": "tool_call", "name": str(p.get("tool", "")),
                       "input": (inp if isinstance(inp, str)
                                 else json.dumps(inp, ensure_ascii=False))[:MAX_INPUT]}
                if state.get("status") == "error":
                    yield {"type": "tool_error", "text": str(state.get("error") or "")}
        if role == "user":
            text = "\n".join(t for t in user_texts if t)
            if text:
                yield {"type": "user_text", "text": text}
        elif role == "assistant":
            out = ((m.get("tokens") or {}).get("output")) or 0
            if out:
                yield {"type": "usage", "output_tokens": int(out)}


# ---------------------------------------------------------------- codex

def _codex_meta(path):
    try:
        with open(path, errors="replace") as fh:
            first = json.loads(fh.readline())
    except (OSError, ValueError):
        return None
    if not isinstance(first, dict) or first.get("type") != "session_meta":
        return None
    return first.get("payload") or {}


def _codex_sessions(root):
    out = []
    for f in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        try:
            if os.path.getsize(f) <= 2000:
                continue
            mtime = os.path.getmtime(f)
        except OSError:
            continue
        meta = _codex_meta(f)
        if meta is None:
            continue
        src = meta.get("source")
        if meta.get("thread_source") == "subagent" or (isinstance(src, dict) and "subagent" in src):
            continue
        cwd = meta.get("cwd") or ""
        if _is_harness_cwd(cwd):
            continue
        out.append(Session(id=meta.get("id") or os.path.basename(f), kind="codex",
                           cwd=cwd, mtime=mtime, ref=f))
    out.sort(key=lambda s: s.mtime, reverse=True)
    return out


def _texts(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content
                         if isinstance(c, dict) and isinstance(c.get("text"), str))
    return ""


_CODEX_KEEP = ('"response_item"', '"item_completed"', '"token_usage_record"', '"token_count"')
_CODEX_SKIP_ITEMS = ('"type":"reasoning"', '"item":{"type":"AgentMessage"', '"item":{"type":"Reasoning"',
                     '"item":{"type":"UserMessage"', '"item":{"type":"SubAgentActivity"')


def _codex_events(path):
    records = 0
    fallback_tokens = 0
    try:
        fh = open(path, errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            head = line[:300]
            if not any(k in head for k in _CODEX_KEEP) or any(k in head for k in _CODEX_SKIP_ITEMS):
                continue
            if '"token_count"' in head and records:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            et = e.get("type")
            p = e.get("payload") or {}
            if not isinstance(p, dict):
                continue
            pt = p.get("type")
            if et == "token_usage_record":
                records += 1
                out = (p.get("usage") or {}).get("output_tokens") or 0
                if out:
                    yield {"type": "usage", "output_tokens": int(out)}
            elif et == "event_msg" and pt == "token_count":
                info = p.get("info") or {}
                fallback_tokens += ((info.get("last_token_usage") or {}).get("output_tokens") or 0)
            elif et == "response_item":
                if pt == "message":
                    role = p.get("role")
                    if role == "user":
                        # Filter per content part: harness blocks can share a
                        # message with the human's text.
                        content = p.get("content")
                        chunks = content if isinstance(content, list) else [{"text": content}]
                        kept = []
                        for c in chunks:
                            t = c.get("text") if isinstance(c, dict) else None
                            if not isinstance(t, str):
                                continue
                            t = IMAGE_TAG_RE.sub("", t).strip()
                            if t and not is_injected(t):
                                kept.append(t)
                        text = "\n".join(kept)
                        if text:
                            yield {"type": "user_text", "text": text}
                    elif role == "assistant":
                        text = _texts(p.get("content"))
                        if text:
                            yield {"type": "assistant_text", "text": text}
                elif pt in ("function_call", "custom_tool_call", "local_shell_call"):
                    inp = p.get("arguments") if pt == "function_call" else p.get("input", p.get("action"))
                    yield {"type": "tool_call", "name": str(p.get("name") or pt),
                           "input": (inp if isinstance(inp, str)
                                     else json.dumps(inp, ensure_ascii=False))[:MAX_INPUT]}
                elif pt in ("function_call_output", "custom_tool_call_output"):
                    err = _codex_output_error(p.get("output"))
                    if err is not None:
                        yield {"type": "tool_error", "text": err}
            elif et == "event_msg" and pt == "item_completed":
                err = _codex_item_error(p.get("item") or {})
                if err is not None:
                    yield {"type": "tool_error", "text": err}
    if not records and fallback_tokens:
        yield {"type": "usage", "output_tokens": int(fallback_tokens)}


_SCRIPT_HEAD_RE = re.compile(r"^(Script failed|Wall time [\d.]+ \w+|Output:|Script error:)\s*$")


def _codex_output_error(output):
    """Tool-call outputs that are failures in themselves (not command exits,
    which arrive as CommandExecution items)."""
    text = _texts(output) if not isinstance(output, dict) else json.dumps(output)
    if not text:
        return None
    s = text.lstrip()
    if s.startswith("Script failed"):
        lines = [l for l in s.splitlines() if l.strip() and not _SCRIPT_HEAD_RE.match(l.strip())]
        return "\n".join(lines) or "Script failed"
    if s.startswith("aborted by user"):
        return s
    # Older exec formats: JSON with metadata.exit_code, or a "Process exited" line.
    if s.startswith("{"):
        try:
            d = json.loads(s)
        except ValueError:
            d = None
        if isinstance(d, dict) and isinstance(d.get("metadata"), dict):
            code = d["metadata"].get("exit_code")
            if code not in (None, 0, "0"):
                return f"Exit code {code}\n{d.get('output', '')}"
    m = re.search(r"Process exited with code (-?\d+)", s[:2000])
    if m and m.group(1) != "0":
        body = s.split("Output:", 1)[1] if "Output:" in s else ""
        return f"Exit code {m.group(1)}\n{body.strip()}"
    return None


def _codex_item_error(item):
    t = item.get("type")
    status = item.get("status")
    if t == "CommandExecution":
        code = item.get("exit_code")
        if code in (None, 0, "0") and status not in ("failed", "declined"):
            return None
        body = (item.get("stderr") or item.get("aggregated_output")
                or item.get("formatted_output") or "").strip()
        if not body:
            cmd = item.get("command")
            if isinstance(cmd, list) and cmd:
                cmd = cmd[-1]
            body = f"$ {cmd}"
        head = f"Exit code {code}" if code not in (None, 0, "0") else f"Command {status}"
        return f"{head}\n{body}"
    if t in ("McpToolCall", "FileChange", "CollabAgentToolCall") and status in ("failed", "declined"):
        res = item.get("error") or item.get("result") or item.get("stderr") or ""
        if isinstance(res, dict):
            res = _texts(res.get("content")) or res.get("message") or json.dumps(res)
        name = item.get("tool") or t
        return str(res).strip() or f"{name} {status}"
    return None


# ---------------------------------------------------------------- public API

_LISTERS = {"claude": _claude_sessions, "opencode": _opencode_sessions, "codex": _codex_sessions}


def list_sessions(kinds, n, roots=None):
    """Most recent n sessions across `kinds`, newest first."""
    r = _roots(roots)
    allsess = []
    for k in KINDS:
        if k in kinds:
            allsess.extend(_LISTERS[k](r[k]))
    allsess.sort(key=lambda s: s.mtime, reverse=True)
    return allsess[:n]


def iter_events(session):
    if session.kind == "claude":
        return _claude_events(session.ref)
    if session.kind == "opencode":
        return _opencode_events(session.ref)
    if session.kind == "codex":
        return _codex_events(session.ref)
    raise ValueError(f"unknown session kind: {session.kind}")
