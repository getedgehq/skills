#!/usr/bin/env bash
# fetch_clips.sh UUID [UUID ...] : download iCloud Photos originals into $REEL_WORK/clips, one at a time.
# Uses the icloud-photos-bridge skill (install it and run its setup.sh first). Find UUIDs with
#   $PY $B/catalog.py --out catalog.jsonl --since <date> --kind video
# With REEL_REMOTE set, each clip is copied to the render machine and the local copy is removed
# (handy when the Mac is short on disk). Retries because iCloud downloads can stall.
set -uo pipefail
PY=$(cat ~/.config/icloud-photos/python 2>/dev/null); B=$(cat ~/.config/icloud-photos/bridge_dir 2>/dev/null)
[ -x "$PY" ] && [ -d "$B" ] || { echo "icloud-photos-bridge is not set up: run its scripts/setup.sh first"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK=$(python3 -c "import sys; sys.path.insert(0,'$HERE'); import rmconf; print(rmconf.work())")
REMOTE=$(python3 -c "import sys; sys.path.insert(0,'$HERE'); import rmconf; print(rmconf.get('REEL_REMOTE'))")
REMOTE_DIR="${REEL_REMOTE_DIR:-reel-machine/clips}"
D="$WORK/clips"; mkdir -p "$D"
for u in "$@"; do
  for t in 1 2 3 4 5 6; do ls "$D/$u".* >/dev/null 2>&1 && break; MIN_FREE_GB=4 "$PY" "$B/fetch.py" "$D" "$u" 2>&1 | tail -1; sleep 5; done
  ls "$D/$u".* >/dev/null 2>&1 || { echo "$u: not downloaded"; continue; }
  if [ -n "$REMOTE" ]; then
    for f in "$D/$u".*; do
      for r in 1 2 3; do ssh "$REMOTE" "mkdir -p $REMOTE_DIR" && rsync -q "$f" "$REMOTE:$REMOTE_DIR/" && rm -f "$f" && echo "$u copied to $REMOTE" && break; sleep 10; done
    done
  else
    echo "$u -> $D"
  fi
done
