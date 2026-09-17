#!/usr/bin/env bash
# deploy.sh [--to ssh-host] [skill ...]
#
# Copy the loop's own skills from this checkout to an install root, then verify
# every file matches. The loop forges skills for other tasks and had no way to
# ship itself: the Mac was running a mine.py three days older than the one the
# recheck called, which is how "unrecognized arguments: --sources" turned up
# only when a timer fired.
#
# Local install root:  $INSTALL_ROOT (default ~/.agents/skills)
# Remote:              --to ax41 copies to that host's $REMOTE_ROOT (default /root/.agents/skills)
#
# Nothing outside the named skill directories is touched, and a tree whose digest
# does not match after copying makes the whole run exit non-zero.
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PKG=$(cd "$HERE/../.." && pwd)
DEFAULT_SKILLS="skill-miner skill-eval-loop agent-infra-fixer skill-cockpit"
HOST=""
while [ $# -gt 0 ]; do
  case "$1" in
    --to) HOST=$2; shift 2;;
    *) break;;
  esac
done
SKILLS=${*:-$DEFAULT_SKILLS}
ROOT=${INSTALL_ROOT:-$HOME/.agents/skills}
RROOT=${REMOTE_ROOT:-/root/.agents/skills}

# One digest over (relative path, bytes) for every file in a tree, skipping
# bytecode. Same code both sides, so a mac-vs-linux checksum tool never differs.
read -r -d '' DIGEST <<'PY'
import hashlib, os, sys
h = hashlib.sha256()
root = sys.argv[1]
for dirpath, dirnames, names in os.walk(root):
    dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
    for n in sorted(names):
        p = os.path.join(dirpath, n)
        h.update(os.path.relpath(p, root).encode() + b"\0")
        h.update(open(p, "rb").read())
print(h.hexdigest()[:16])
PY

fail=0
for s in $SKILLS; do
  src="$PKG/$s"
  [ -d "$src" ] || { echo "no such skill in the checkout: $s"; fail=1; continue; }
  want=$(python3 -c "$DIGEST" "$src")
  if [ -n "$HOST" ]; then
    ssh "$HOST" "mkdir -p '$RROOT/$s'" || { fail=1; continue; }
    scp -q -r "$src/." "$HOST:$RROOT/$s/" || { fail=1; continue; }
    ssh "$HOST" "find '$RROOT/$s' -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null; true"
    got=$(ssh "$HOST" "python3 - '$RROOT/$s'" <<PY
$DIGEST
PY
)
    where="$HOST:$RROOT/$s"
  else
    mkdir -p "$ROOT/$s"
    (cd "$src" && find . -name '__pycache__' -prune -o -type f -print | while read -r f; do
        mkdir -p "$ROOT/$s/$(dirname "$f")"; cp -p "$f" "$ROOT/$s/$f"; done)
    find "$ROOT/$s" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
    got=$(python3 -c "$DIGEST" "$ROOT/$s")
    where="$ROOT/$s"
  fi
  if [ "$want" = "$got" ]; then
    echo "ok   $s -> $where  ($want)"
  else
    echo "DIFF $s -> $where: checkout $want vs installed $got"
    fail=1
  fi
done
exit $fail
