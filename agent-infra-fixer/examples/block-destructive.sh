#!/bin/bash
# Block dangerous/destructive commands.
# Patterns are anchored to what actually destroys: a bare root/home wipe, a force push that
# can clobber others, SQL TRUNCATE/DROP, raw device writes, curl piped into a shell.
# v1 matched substrings ("rm -rf /" hit every rm of /tmp/x, "truncate" hit "truncated",
# "curl.*|.*sh" hit "| head") - 72 false blocks in 20 sessions. Replay: skill-forge hook tests.

INPUT=$(cat)
printf '%s' "$INPUT" | python3 -c '
import json, re, sys
try:
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "") or ""
except ValueError:
    sys.exit(0)

END = r"""(?=\s|$|[;&|)'"'"'"])"""
RULES = [
    ("rm -rf on / or home", r"\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+|-[a-zA-Z]*f[a-zA-Z]*\s+|--\s+)*(/|/\*|~|~/|~/\*|\$HOME|\$HOME/|\$HOME/\*|\"\$HOME\"|\*)" + END, re.I),
    ("git push --force (use --force-with-lease)", r"\bgit\b[^;&|\n]*\bpush\b[^;&|\n]*(\s--force(?!-with-lease)\b|\s-f\b|\s\+\S+:)", 0),
    ("git reset --hard origin", r"\bgit\b[^;&|\n]*\breset\s+--hard\s+origin", 0),
    ("git checkout . / restore . (discards work)", r"\bgit\b[^;&|\n]*\b(checkout|restore)\s+(--\s+)?\.(\s|$|[;&|])", 0),
    ("git clean -fd", r"\bgit\b[^;&|\n]*\bclean\s+-[a-zA-Z]*f[a-zA-Z]*d|\bgit\b[^;&|\n]*\bclean\s+-[a-zA-Z]*d[a-zA-Z]*f", 0),
    ("DROP TABLE/DATABASE", r"\bdrop\s+(table|database|schema)\b", re.I),
    ("SQL TRUNCATE", r"\btruncate\s+(table\s+)?(only\s+)?[\"\w.]+\s*(;|cascade|restart|,)|\btruncate\s+table\b", re.I),
    ("raw device write", r">\s*/dev/(sd|nvme|disk)|\bmkfs\.|\bdd\b[^;&|\n]*\bof=/dev/(sd|nvme|disk|rdisk)", 0),
    ("curl/wget piped into a shell", r"\b(curl|wget)\b[^|;&\n]*\|\s*(sudo\s+(-\S+\s+)*)?(ba|z|da)?sh\b", 0),
]
for label, pat, flags in RULES:
    if re.search(pat, cmd, flags):
        print(f"BLOCKED: Destructive command detected: {label}", file=sys.stderr)
        sys.exit(2)
'
