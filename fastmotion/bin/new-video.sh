#!/bin/bash
# Scaffold a new fastmotion video project.
#   bin/new-video.sh <target-dir> [--no-install]
# Copies the engine + the Demo video (a minimal starting point).
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:?usage: new-video.sh <target-dir> [--no-install]}"
shift
INSTALL=1
for a in "$@"; do
  case "$a" in
    --no-install) INSTALL=0 ;;
    *) echo "unknown flag: $a" >&2; exit 1 ;;
  esac
done
if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "refusing: $TARGET exists and is not empty" >&2; exit 1
fi
mkdir -p "$TARGET"
(cd "$SKILL/template" && tar --exclude=node_modules --exclude=out -cf - .) | (cd "$TARGET" && tar -xf -)
if [ "$INSTALL" = 1 ]; then (cd "$TARGET" && npm install --no-audit --no-fund); fi
echo "Scaffolded $TARGET  (npm run dev to open the studio)"
