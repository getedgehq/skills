#!/bin/bash
# Block CPU-heavy commands locally - they belong on a build server ($DEV_SERVER).
# Only EXECUTED heavy tools count: text inside ssh <server> payloads, pgrep/pkill/du/rsync
# arguments, grep patterns and code strings are not local work. A single-frame ffmpeg grab
# (-frames:v 1 / -vframes 1) is cheap and allowed. v1 substring matching made 24 false blocks.

INPUT=$(cat)
printf '%s' "$INPUT" | python3 -c '
import json, os, re, shlex, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "") or ""
except ValueError:
    sys.exit(0)

HEAVY = {
    "ffmpeg": "ffmpeg transcode/filter",
    "remotion": "remotion render",
    "puppeteer": "puppeteer",
    "chrome-headless-shell": "chrome-headless-shell",
    "playwright": "playwright browser run",
}

def words(segment):
    try:
        return shlex.split(segment, comments=True)
    except ValueError:
        return segment.split()

# drop heredoc bodies (python/code text, not commands)
lines, skip = [], None
for line in cmd.splitlines():
    if skip:
        if line.strip() == skip:
            skip = None
        continue
    m = re.search(r"<<-?\s*[\x27\"]?(\w+)[\x27\"]?", line)
    if m:
        skip = m.group(1)
    lines.append(line)
text = "\n".join(lines)
# quoted strings are data or remote payloads (ssh host "..."), never a local program name
text = re.sub(r"\x27[^\x27]*\x27|\"(?:\\.|[^\"\\])*\"", " Q ", text)

hit = None
for seg in re.split(r"\n|;|&&|\|\||\||\$\(|`", text):
    w = words(seg)
    while w and (re.fullmatch(r"\w+=\S*", w[0]) or w[0] in ("sudo", "-n", "nice", "time", "exec", "env", "nohup", "(", "{", "then", "do", "else")):
        w = w[1:]
    if not w:
        continue
    prog = w[0].rsplit("/", 1)[-1]
    if prog in ("ssh", "scp", "rsync", "mosh"):
        continue  # remote work or a copy: the right pattern
    if prog == "ffmpeg":
        if any(a in ("-frames:v", "-vframes") for a in w) and not any(a in ("-t", "-to") for a in w):
            continue
        if any(a in ("-vf", "-filter_complex", "-c:v", "-vcodec") or "scale=" in a for a in w):
            hit = HEAVY["ffmpeg"]
    elif prog in ("npx", "pnpm", "bunx", "yarn") and len(w) > 2 and w[1] == "remotion" and w[2] in ("render", "lambda", "still"):
        hit = HEAVY["remotion"]
    elif prog == "remotion" and len(w) > 1 and w[1] in ("render", "lambda"):
        hit = HEAVY["remotion"]
    elif prog in ("chrome-headless-shell", "puppeteer"):
        hit = HEAVY[prog]
    elif prog in ("npx", "node") and len(w) > 1 and re.search(r"playwright|puppeteer", w[1]) and "install" not in w:
        hit = HEAVY["playwright"]
    if hit:
        break

if hit:
    server = os.environ.get("DEV_SERVER", "your build server")
    print(f"BLOCKED: CPU-heavy task detected ({hit}). Run it on {server} instead:", file=sys.stderr)
    print(f"  ssh {server} \"cd <project> && <command>\"", file=sys.stderr)
    sys.exit(2)
'
