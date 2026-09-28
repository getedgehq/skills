#!/usr/bin/env python3
"""Normalize ChatGPT exports and local Claude Code/Codex session logs to JSONL.
The AI DNA entry point is make.py; this module holds its local parsers.
"""
import argparse, glob, hashlib, json, os, re, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone

MAX_MSG_CHARS = 4000        # per stored user message
MAX_EMBED_CHARS = 6000      # textForEmbedding cap

NOISE_PREFIX = re.compile(r"^\s*(<command-|<local-command|<task-notification|<system-reminder|<bash-|<user-prompt-submit-hook|Caveat: The messages below|\[Request interrupted|<environment_context|<user_instructions|# AGENTS\.md|<turn_aborted|<subagent_notification)", re.I)
AUTOMATED_CWD = re.compile(r"skill-forge-runs|getedgeeval|harbor-|/evals?/|eval-run|/tmp/claude-\d", re.I)


def iso(ts):
    if ts is None or ts == "":
        return None
    if isinstance(ts, (int, float)):
        if ts > 1e12:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def finish(conv, stats):
    msgs = [m for m in conv["messages"] if m["text"].strip()]
    conv["messages"] = msgs
    user = [m["text"] for m in msgs if m["role"] == "user"]
    if not user:
        stats["skipped_no_user_text"][conv["provider"]] += 1
        return None
    title = (conv.get("title") or "").strip()
    emb = (title + "\n" + "\n".join(u[:1500] for u in user))[:MAX_EMBED_CHARS]
    conv["textForEmbedding"] = emb
    conv["messageCount"] = conv.get("messageCount") or len(msgs)
    conv["charCount"] = conv.get("charCount") or sum(len(m["text"]) for m in msgs)
    if not conv.get("createdAt"):
        ts = [m.get("createdAt") for m in msgs if m.get("createdAt")]
        conv["createdAt"] = min(ts) if ts else None
    if not conv["createdAt"]:
        stats["skipped_no_date"][conv["provider"]] += 1
        return None
    return conv


# ---------- ChatGPT ----------
def chatgpt_text(content):
    ct = content.get("content_type")
    if ct in ("text", "multimodal_text"):
        return "\n".join(p if isinstance(p, str) else (p.get("text", "") if isinstance(p, dict) and p.get("content_type") == "audio_transcription" else "") for p in content.get("parts") or []).strip()
    if ct in ("user_editable_context", "model_editable_context", "thoughts", "reasoning_recap"):
        return ""
    return (content.get("text") or "").strip() if isinstance(content.get("text"), str) else ""


def parse_chatgpt(arr, account, stats):
    out = []
    for c in arr:
        mapping = c.get("mapping") or {}
        chain, nid = [], c.get("current_node")
        while nid and nid in mapping:
            chain.append(mapping[nid]); nid = mapping[nid].get("parent")
        chain.reverse()
        msgs, model = [], ""
        for n in chain:
            m = n.get("message")
            if not m or not m.get("content"):
                continue
            role = (m.get("author") or {}).get("role", "assistant")
            md = m.get("metadata") or {}
            if md.get("model_slug"):
                model = md["model_slug"]
            if role == "system" or md.get("is_visually_hidden_from_conversation"):
                continue
            t = chatgpt_text(m["content"])
            if not t:
                continue
            role = role if role in ("user", "assistant", "tool") else "assistant"
            msgs.append({"role": role, "text": t[:MAX_MSG_CHARS] if role == "user" else t[:800], "createdAt": iso(m.get("create_time")), "_len": len(t)})
        conv = {
            "id": "chatgpt:" + str(c.get("conversation_id") or c.get("id")),
            "provider": "ChatGPT", "account": account, "model": model,
            "title": c.get("title") or "", "createdAt": iso(c.get("create_time")), "updatedAt": iso(c.get("update_time")),
            "messages": msgs,
        }
        conv["charCount"] = sum(m.pop("_len") for m in msgs)
        conv = finish(conv, stats)
        if conv:
            out.append(conv)
    return out


def parse_claude_ai(arr, stats):
    out = []
    for c in arr:
        msgs = []
        for m in c.get("chat_messages") or []:
            t = m.get("text") or "\n".join(p.get("text", "") for p in m.get("content") or [] if isinstance(p, dict) and p.get("type") == "text")
            role = "user" if m.get("sender") == "human" else "assistant"
            msgs.append({"role": role, "text": t[:MAX_MSG_CHARS] if role == "user" else t[:800], "createdAt": iso(m.get("created_at")), "_len": len(t)})
        conv = {"id": "claude:" + str(c.get("uuid")), "provider": "Claude", "model": c.get("model") or "",
                "title": c.get("name") or "", "createdAt": iso(c.get("created_at")), "updatedAt": iso(c.get("updated_at")), "messages": msgs}
        conv["charCount"] = sum(m.pop("_len") for m in msgs)
        conv = finish(conv, stats)
        if conv:
            out.append(conv)
    return out


def load_zip(path, stats, account):
    out = []
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if re.search(r"(^|/)conversations(-\d+)?\.json$", n)]
        for n in names:
            arr = json.loads(z.read(n))
            if arr and isinstance(arr, list) and "mapping" in arr[0]:
                out += parse_chatgpt(arr, account, stats)
            elif arr and isinstance(arr, list) and "chat_messages" in arr[0]:
                out += parse_claude_ai(arr, stats)
    return out


# ---------- Claude Code ----------
def human_text(r):
    if r.get("type") != "user" or r.get("isSidechain") or r.get("isMeta") or r.get("isCompactSummary") or r.get("toolUseResult") is not None:
        return None
    if r.get("promptSource") in ("system", "sdk"):
        return None
    o = r.get("origin")
    if isinstance(o, dict) and o.get("kind") not in (None, "human"):
        return None
    c = (r.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(p, dict) and p.get("type") == "tool_result" for p in c):
            return None
        c = "\n".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
    if not isinstance(c, str) or not c.strip() or NOISE_PREFIX.match(c):
        return None
    return c.strip()


def parse_claude_code(path, host, stats):
    msgs, title, sid, cwd, entry, first_ts, last_ts, n_asst, chars = [], "", None, None, None, None, None, 0, 0
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return None
    with fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            t = r.get("type")
            if t == "ai-title" or t == "summary":
                title = r.get("aiTitle") or r.get("title") or r.get("summary") or title
                continue
            if t == "custom-title":
                title = r.get("customTitle") or title
                continue
            if t not in ("user", "assistant") or r.get("isSidechain"):
                continue
            sid = sid or r.get("sessionId"); cwd = cwd or r.get("cwd"); entry = entry or r.get("entrypoint")
            ts = r.get("timestamp")
            if ts:
                first_ts = first_ts or ts; last_ts = ts
            if t == "assistant":
                c = (r.get("message") or {}).get("content")
                if isinstance(c, list) and any(isinstance(p, dict) and p.get("type") == "text" and p.get("text", "").strip() for p in c):
                    n_asst += 1
                    chars += sum(len(p.get("text", "")) for p in c if isinstance(p, dict) and p.get("type") == "text")
                continue
            h = human_text(r)
            if h:
                chars += len(h)
                msgs.append({"role": "user", "text": h[:MAX_MSG_CHARS], "createdAt": iso(ts)})
    if not sid:
        return None
    if entry and entry != "cli":
        stats["skipped_non_interactive"]["Claude Code"] += 1
        return None
    if cwd and AUTOMATED_CWD.search(cwd):
        stats["skipped_automated_cwd"]["Claude Code"] += 1
        return None
    if not title and msgs:
        title = re.sub(r"\s+", " ", msgs[0]["text"])[:70]
    conv = {"id": "claudecode:" + sid, "provider": "Claude Code", "host": host, "project": os.path.basename(cwd or ""),
            "title": title, "createdAt": iso(first_ts), "updatedAt": iso(last_ts), "messages": msgs,
            "messageCount": len(msgs) + n_asst, "charCount": chars}
    return finish(conv, stats)


# ---------- Codex ----------
def parse_codex(path, host, stats):
    msgs, sid, cwd, originator, source, first_ts, last_ts, n_asst, chars = [], None, None, None, None, None, None, 0, 0
    fallback = []; fallback_asst = 0
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return None
    with fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            p = r.get("payload") or {}
            ts = r.get("timestamp")
            if r.get("type") == "session_meta":
                sid = sid or p.get("id"); cwd = p.get("cwd"); originator = p.get("originator"); source = p.get("source")
                continue
            if ts:
                first_ts = first_ts or ts; last_ts = ts
            # legacy / fallback: user turns recorded only as response items
            item = p if r.get("type") == "response_item" else (r if r.get("type") == "message" else None)
            if item and item.get("type") == "message" and item.get("role") == "assistant":
                if any(isinstance(c,dict) and c.get("type") in ("output_text","text") and c.get("text","").strip() for c in item.get("content") or []): fallback_asst += 1
            if item and item.get("type") == "message" and item.get("role") == "user":
                txt = "\n".join(c.get("text", "") for c in item.get("content") or [] if isinstance(c, dict) and c.get("type") in ("input_text", "text"))
                if txt.strip() and not NOISE_PREFIX.match(txt):
                    fallback.append({"role": "user", "text": txt.strip()[:MAX_MSG_CHARS], "createdAt": iso(ts)})
            if r.get("type") == "event_msg" and p.get("type") == "user_message":
                m = (p.get("message") or "").strip()
                if m and not NOISE_PREFIX.match(m):
                    chars += len(m)
                    msgs.append({"role": "user", "text": m[:MAX_MSG_CHARS], "createdAt": iso(ts)})
            elif r.get("type") == "event_msg" and p.get("type") == "agent_message":
                n_asst += 1; chars += len(p.get("message") or "")
    if not msgs and fallback:
        msgs = fallback; chars += sum(len(m["text"]) for m in fallback); n_asst = max(n_asst, fallback_asst)
    if not sid:
        m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$", path)
        if not m:
            return None
        sid, source = m.group(1), "cli"   # pre-session_meta logs came from the interactive CLI
    interactive = isinstance(source, str) and source in ("cli", "vscode") and originator != "codex_exec"
    if not interactive:
        stats["skipped_non_interactive"]["Codex"] += 1
        return None
    if cwd and AUTOMATED_CWD.search(cwd):
        stats["skipped_automated_cwd"]["Codex"] += 1
        return None
    title = re.sub(r"\s+", " ", msgs[0]["text"])[:70] if msgs else ""
    conv = {"id": "codex:" + sid, "provider": "Codex", "host": host, "project": os.path.basename(cwd or ""),
            "title": title, "createdAt": iso(first_ts), "updatedAt": iso(last_ts), "messages": msgs,
            "messageCount": len(msgs) + n_asst, "charCount": chars}
    return finish(conv, stats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chatgpt", nargs="*", default=[], help="account=path.zip")
    ap.add_argument("--claude-export", nargs="*", default=[])
    ap.add_argument("--claude-code", nargs="*", default=[], help="host=dir")
    ap.add_argument("--codex", nargs="*", default=[], help="host=dir")
    ap.add_argument("--merge", nargs="*", default=[], help="previously extracted jsonl parts (e.g. restored archives)")
    ap.add_argument("--out", default="data/conversations.jsonl")
    a = ap.parse_args()
    stats = defaultdict(Counter)
    convs = {}

    def add(c, src):
        if not c:
            return
        prev = convs.get(c["id"])
        if prev is None or len(c["messages"]) > len(prev["messages"]):
            if prev:
                stats["deduped"][c["provider"]] += 1
            convs[c["id"]] = c
            stats["files"][src] += 1
        else:
            stats["deduped"][c["provider"]] += 1

    for path in a.merge:
        for line in open(path):
            c = json.loads(line)
            add(c, "part:" + os.path.basename(path))
    for spec in a.chatgpt:
        acct, path = spec.split("=", 1)
        for c in load_zip(path, stats, acct):
            add(c, "chatgpt:" + acct)
    for path in a.claude_export:
        for c in load_zip(path, stats, "claude.ai"):
            add(c, "claude.ai")
    for spec in a.claude_code:
        host, d = spec.split("=", 1)
        for f in glob.glob(os.path.join(d, "*", "*.jsonl")):  # top-level sessions only; subagents/ sidechains excluded
            add(parse_claude_code(f, host, stats), "claudecode:" + host)
    for spec in a.codex:
        host, d = spec.split("=", 1)
        for f in glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True):
            add(parse_codex(f, host, stats), "codex:" + host)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        for c in sorted(convs.values(), key=lambda c: c["createdAt"]):
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    per = Counter(c["provider"] for c in convs.values())
    summary = {"total": len(convs), "per_provider": per, **{k: dict(v) for k, v in stats.items()}}
    json.dump(summary, open(a.out + ".stats.json", "w"), indent=1, default=dict)
    print(json.dumps(summary, indent=1, default=dict))


if __name__ == "__main__":
    main()
