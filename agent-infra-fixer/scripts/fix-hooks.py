#!/usr/bin/env python3
"""Fix Claude Code shell hooks that block with the reason on stdout instead of stderr.

Usage: fix-hooks.py [--hooks-dir ~/.claude/hooks] [--exit2] [--apply]

A PreToolUse hook blocks by exiting 2; Claude Code shows the agent the hook's STDERR.
A block message echoed to stdout surfaces as "hook error: No stderr output" and the
agent never learns why it was blocked, so it retries or invents a workaround.
A hook that exits 1 does not block at all (non-blocking error) - --exit2 rewrites
`exit 1` after a BLOCKED message to `exit 2`.

For every `exit 2` (and with --exit2 every `exit 1`) in a *.sh hook, the output lines
of the same block above it (echo / printf / cat <<EOF) get `>&2`. Default is a dry run
that prints a diff; --apply writes <hook>.bak-stderr backups first.
Verify afterwards with a must-block input: exit code 2 AND non-empty stderr.
"""
import argparse
import difflib
import glob
import os
import re
import shutil
import sys

OUT = re.compile(r"^(\s*)(echo|printf)\b")
HEREDOC = re.compile(r"^(\s*)cat\s+(<<-?\s*['\"]?\w+['\"]?)(.*)$")
BLOCK_START = re.compile(r"^\s*(if|elif|else|then|fi|do|done|case|esac|for|while|\S+\)\s*$|\w+\s*\(\)\s*\{|\}|;;)")
REDIRECTED = re.compile(r">&2|/dev/stderr|\s[12]?>>?\s*[^\s\"'>]+\s*$")  # output already sent somewhere


def fix_text(text, exit1):
    lines = text.split("\n")
    exits = [i for i, l in enumerate(lines)
             if re.match(r"^\s*exit\s+2\b", l) or (exit1 and re.match(r"^\s*exit\s+1\b", l))]
    changed = set()
    for i in exits:
        j, blocked_msg = i - 1, False
        while j >= 0:
            l = lines[j]
            if BLOCK_START.match(l) and not OUT.match(l):
                break
            m = HEREDOC.match(l)
            if m and ">&2" not in l:
                lines[j] = f"{m.group(1)}cat >&2 {m.group(2)}{m.group(3)}"
                changed.add(j)
                blocked_msg = True
            elif OUT.match(l) and not REDIRECTED.search(l.rstrip()):
                lines[j] = l.rstrip() + " >&2"
                changed.add(j)
                blocked_msg = True
            elif OUT.match(l):
                blocked_msg = True
            j -= 1
        if exit1 and blocked_msg and re.match(r"^\s*exit\s+1\b", lines[i]):
            lines[i] = re.sub(r"exit\s+1\b", "exit 2", lines[i], count=1)
            changed.add(i)
    return "\n".join(lines), len(changed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hooks-dir", default=os.path.expanduser("~/.claude/hooks"))
    ap.add_argument("--exit2", action="store_true", help="also turn `exit 1` after a message into `exit 2`")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    hooks = sorted(glob.glob(os.path.join(args.hooks_dir, "*.sh")))
    if not hooks:
        sys.exit(f"no *.sh hooks in {args.hooks_dir}")
    total = 0
    for path in hooks:
        text = open(path, errors="replace").read()
        new, n = fix_text(text, args.exit2)
        name = os.path.basename(path)
        if not n:
            print(f"OK    {name}")
            continue
        total += n
        if args.apply:
            shutil.copyfile(path, path + ".bak-stderr")
            open(path, "w").write(new)
            print(f"FIXED {name}: {n} lines (backup {name}.bak-stderr)")
        else:
            print(f"WOULD FIX {name}: {n} lines")
            sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True),
                                                       name, name + " (fixed)", n=1))
    print(f"{total} lines {'changed' if args.apply else 'to change'}")


if __name__ == "__main__":
    main()
