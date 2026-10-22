#!/usr/bin/env bash
# remote_render.sh BUNDLE_DIR [HOST] : optional. Render a bundle on another machine with ffmpeg + python3 + Pillow
# (a bigger box, a throwaway cloud VM, a home server). Ships the bundle over ssh, runs job.sh there,
# pulls back out/reel_<name>.mp4 into $REEL_WORK/renders/, deletes the remote copy.
# HOST defaults to REEL_REMOTE from config. Rendering locally works too: bash BUNDLE_DIR/job.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
B="$(cd "$1" && pwd)"; N="$(basename "$B")"
H="${2:-$(python3 -c "import sys; sys.path.insert(0,'$HERE'); import rmconf; print(rmconf.get('REEL_REMOTE'))")}"
[ -n "$H" ] || { echo "no host: pass one or set REEL_REMOTE"; exit 1; }
WORK=$(python3 -c "import sys; sys.path.insert(0,'$HERE'); import rmconf; print(rmconf.work())")
RD=$(ssh "$H" 'mktemp -d')
tar czhf - -C "$B" . | ssh "$H" "tar xzf - -C $RD"
ssh "$H" "bash $RD/job.sh"
mkdir -p "$WORK/renders"
scp -q "$H:$RD/out/reel_$N.mp4" "$WORK/renders/"
ssh "$H" "rm -rf $RD"
echo "render: $WORK/renders/reel_$N.mp4"
