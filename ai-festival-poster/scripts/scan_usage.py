#!/usr/bin/env python3
"""Count real AI usage from local agent logs and write usage.json for render_poster.py.

Signal per act = number of sessions in which it was actually used:
  - Claude Code / Codex: number of session logs on this machine
  - tools: sessions whose tool calls (commands, API calls, paths) invoked the tool, not chat mentions
  - models: sessions that ran on that model
  - MCP servers: sessions that called that server
  - ChatGPT (optional): conversations in a ChatGPT export (--chatgpt-export conversations.json or export .zip)
Everything stays on this machine; nothing is uploaded.

Usage: python3 scan_usage.py [--chatgpt-export PATH] [--out usage.json] [--min 3]
"""
import argparse, collections, glob, json, os, re, zipfile

TOOLS = {  # name: (day, regex over tool-call text)
    "GitHub": ("BUILD", r"\bgh (pr|repo|api|issue|run|release|workflow)\b|github\.com/"),
    "Docker": ("BUILD", r"\bdocker (run|build|compose|ps|exec|images)\b"),
    "Vercel": ("BUILD", r"\bvercel\b"),
    "Supabase": ("BUILD", r"supabase"),
    "Cloudflare": ("BUILD", r"cloudflare|wrangler"),
    "Hetzner": ("BUILD", r"hetzner"),
    "AWS": ("BUILD", r"\baws (s3|lambda|bedrock|sts|ec2|iam|logs)\b|bedrock"),
    "Playwright": ("BUILD", r"playwright"),
    "Cursor": ("BUILD", r"\bcursor-agent\b|\.cursor/"),
    "Gemini": ("THINK", r"gemini"),
    "OpenAI API": ("THINK", r"api\.openai\.com|from openai import"),
    "Kimi": ("THINK", r"\bkimi\b|moonshot"),
    "OpenRouter": ("THINK", r"openrouter"),
    "Perplexity": ("THINK", r"perplexity"),
    "Remotion": ("CREATE", r"remotion"),
    "HyperFrames": ("CREATE", r"hyperframes"),
    "FFmpeg": ("CREATE", r"\bffmpeg\b|\bffprobe\b"),
    "ElevenLabs": ("CREATE", r"elevenlabs"),
    "Figma": ("CREATE", r"figma"),
    "Lovable": ("CREATE", r"lovable"),
    "Resend": ("CREATE", r"\bresend\b"),
    "PostHog": ("CREATE", r"posthog"),
    "Midjourney": ("CREATE", r"midjourney"),
}
MODEL_NAMES = [  # (regex on the model id, display name, day)
    (r"^claude-opus-5-5", "Opus 5.5", "THINK"), (r"^claude-opus-5$", "Opus 5", "THINK"),
    (r"^claude-fable", "Fable", "THINK"), (r"^claude-sonnet-5", "Sonnet 5", "THINK"),
    (r"^claude-haiku-4-5", "Haiku 4.5", "THINK"), (r"^claude-opus-4", "Opus 4", "THINK"),
    (r"^claude-sonnet-4", "Sonnet 4", "THINK"), (r"^gpt-6", "GPT-6", "THINK"),
    (r"^gpt-5\.6", "GPT-5.6", "THINK"), (r"^gpt-5", "GPT-5", "THINK"), (r"^o[34]", "o-series", "THINK"),
]
RX = {k: re.compile(v[1], re.I) for k, v in TOOLS.items()}
MCP_DAY = {"github": "BUILD", "chrome-devtools": "BUILD", "claude-in-chrome": "BUILD", "playwright": "BUILD"}


def tool_text(line):
    try:
        o = json.loads(line)
    except Exception:
        return ""
    out = []
    m = o.get("message") or {}
    if isinstance(m.get("content"), list):
        for c in m["content"]:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                out.append(json.dumps(c.get("input", ""))[:20000])
    p = o.get("payload") or {}
    if isinstance(p, dict) and p.get("type") in ("function_call", "local_shell_call", "custom_tool_call"):
        out.append(json.dumps(p.get("arguments") or p.get("action") or p.get("input") or "")[:20000])
    return "\n".join(out)


def model_name(mid):
    mid = re.sub(r"-\d{8}$", "", mid.lower()).replace("[1m]", "")
    for rx, name, day in MODEL_NAMES:
        if re.search(rx, mid):
            return name, day
    return None


def chatgpt_count(path):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.endswith("conversations.json"))
            return len(json.loads(z.read(name)))
    return len(json.load(open(path)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chatgpt-export")
    ap.add_argument("--out", default="usage.json")
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    tools, models, mcp = collections.Counter(), collections.Counter(), collections.Counter()
    model_day, sessions = {}, {"Claude Code": 0, "Codex": 0}
    for src, pat in (("Claude Code", "~/.claude/projects/**/*.jsonl"), ("Codex", "~/.codex/sessions/**/*.jsonl")):
        for f in glob.glob(os.path.expanduser(pat), recursive=True):
            if "/subagents/" in f:
                continue
            sessions[src] += 1
            hit, mhit, shit = set(), set(), set()
            with open(f, errors="ignore") as fh:
                for line in fh:
                    if '"model"' in line:
                        for mid in re.findall(r'"model"\s*:\s*"([A-Za-z0-9.\-_\[\]/]+)"', line):
                            mn = model_name(mid)
                            if mn:
                                mhit.add(mn[0]); model_day[mn[0]] = mn[1]
                    if '"tool_use"' in line:
                        shit.update(re.findall(r'"name"\s*:\s*"mcp__([A-Za-z0-9_\-]+?)__', line))
                    if '"tool_use"' in line or "function_call" in line or "shell_call" in line or "custom_tool_call" in line:
                        t = tool_text(line)
                        for k, rx in RX.items():
                            if k not in hit and t and rx.search(t):
                                hit.add(k)
            tools.update(hit); models.update(mhit); mcp.update(shit)
    rows = [{"name": k, "day": TOOLS[k][0], "sessions": n, "signal": "sessions whose tool calls invoked it"} for k, n in tools.items()]
    rows += [{"name": k, "day": model_day[k], "sessions": n, "signal": "sessions that ran on this model"} for k, n in models.items()]
    for k, n in mcp.items():
        name = k.replace("claude_ai_", "").replace("_", " ").replace("-", " ").title()
        if name.lower() in {r["name"].lower() for r in rows}:
            continue
        rows.append({"name": name, "day": MCP_DAY.get(k, "THINK"), "sessions": n, "signal": "sessions that called this MCP server"})
    for k, n in sessions.items():
        if n:
            rows.append({"name": k, "day": "BUILD", "sessions": n, "signal": f"{k} session logs on this machine"})
    if a.chatgpt_export:
        rows.append({"name": "ChatGPT", "day": "THINK", "sessions": chatgpt_count(a.chatgpt_export), "signal": "conversations in the ChatGPT export"})
    rows = [dict(r, verified=r["sessions"] >= a.min) for r in rows]
    json.dump(sorted(rows, key=lambda r: -r["sessions"]), open(a.out, "w"), indent=1)
    for r in sorted(rows, key=lambda r: (r["day"], -r["sessions"])):
        if r["verified"]:
            print(f'{r["day"]:6} {r["sessions"]:5}  {r["name"]}')
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
