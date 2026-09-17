#!/usr/bin/env python3
"""Fix Claude Code PreToolUse hooks that print block reasons to stdout instead
of stderr (and one that exits 1 instead of 2). Exit-2 blocks read the reason
from stderr; stdout-only blocks surface as 'hook error: No stderr output' and
the agent never learns why it was blocked.

Run: sudo python3 fix-hooks.py [--apply]
Default is dry-run. Creates .bak-stdrefix backups before writing.
"""
import os
import shutil
import sys

H = "/root/.claude/hooks"
FIXES = {
    "block-destructive.sh": [
        ('echo "BLOCKED: Destructive command detected: $pattern"',
         'echo "BLOCKED: Destructive command detected: $pattern" >&2'),
    ],
    "enforce-hetzner-heavy-tasks.sh": [
        ('''        echo "BLOCKED: CPU-heavy task detected. Run on AX41/Hetzner instead:"
        echo ""
        echo "  Wrap with: ssh ax41 \\"$pattern ...\\""
        echo "  For Remotion: ~/linkedin-posts/render-on-hetzner.sh <project-dir> <composition> <output.mp4>"
        echo "  For browser automation: use MCP authenticated-browser (already on AX41)"
        echo ""
        echo "Pattern matched: $pattern"''',
         '''        echo "BLOCKED: CPU-heavy task detected. Run on AX41/Hetzner instead:" >&2
        echo "" >&2
        echo "  Wrap with: ssh ax41 \\"$pattern ...\\"" >&2
        echo "  For Remotion: ~/linkedin-posts/render-on-hetzner.sh <project-dir> <composition> <output.mp4>" >&2
        echo "  For browser automation: use MCP authenticated-browser (already on AX41)" >&2
        echo "" >&2
        echo "Pattern matched: $pattern" >&2'''),
    ],
    "enforce-server-routing.sh": [
        ('''        echo "BLOCKED: CPU-heavy task detected. Run on $DEV_SERVER instead:"
        echo ""
        echo "  ssh $DEV_SERVER \\"$pattern ...\\""
        echo ""
        echo "Pattern matched: $pattern"''',
         '''        echo "BLOCKED: CPU-heavy task detected. Run on $DEV_SERVER instead:" >&2
        echo "" >&2
        echo "  ssh $DEV_SERVER \\"$pattern ...\\"" >&2
        echo "" >&2
        echo "Pattern matched: $pattern" >&2'''),
    ],
    "protect-sensitive-files.sh": [
        ('echo "BLOCKED: Cannot modify sensitive file matching: $pattern"',
         'echo "BLOCKED: Cannot modify sensitive file matching: $pattern" >&2'),
        ('echo "File: $FILE"',
         'echo "File: $FILE" >&2'),
    ],
    "sandbox-heavy-tasks.sh": [
        ("cat <<EOF\nBLOCKED: Heavy task detected.",
         "cat >&2 <<EOF\nBLOCKED: Heavy task detected."),
    ],
    "block-terminal-minimize.sh": [
        ('echo "BLOCKED: This command would minimize/hide terminal windows, which is not allowed."',
         'echo "BLOCKED: This command would minimize/hide terminal windows, which is not allowed." >&2'),
        ('echo "Pattern matched: $pattern"\n        exit 1',
         'echo "Pattern matched: $pattern" >&2\n        exit 2'),
    ],
}


def main():
    apply = "--apply" in sys.argv
    for name, subs in FIXES.items():
        path = os.path.join(H, name)
        if not os.path.exists(path):
            print(f"SKIP {name}: missing")
            continue
        text = open(path).read()
        new = text
        for old, repl in subs:
            if old not in new:
                print(f"WARN {name}: pattern not found: {old[:60]!r}")
                continue
            new = new.replace(old, repl, 1)
        if new == text:
            print(f"OK   {name}: nothing to change")
            continue
        if apply:
            shutil.copyfile(path, path + ".bak-stdrefix")
            open(path, "w").write(new)
            print(f"FIXED {name} (backup: {name}.bak-stdrefix)")
        else:
            print(f"WOULD FIX {name}")


if __name__ == "__main__":
    main()
