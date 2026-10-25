#!/usr/bin/env bash
# finish.sh BUNDLE_DIR [--speed X] [--headfreeze S] : the post-render chain, in order.
#   1. voiceclean.py  raw voice + gentle EQ + loudnorm (no isolation)
#   2. pcut.py        VAD jump cuts (silences to ~0.1 s, lead-in < 0.15 s), small speed-up if slow
#   3. vadgaps.py     pace gate: no pause > 0.35 s, dead air <= 8%
#   4. facecheck.py   first 0.5 s and last 2 s: eyes open, sharp, whole face
# Output: $REEL_WORK/renders/reel_<name>.mp4 (+ _face.jpg strip). Stops on the first failed gate.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
B="$(cd "$1" && pwd)"; N="$(basename "$B")"; shift
WORK=$(python3 -c "import sys; sys.path.insert(0,'$HERE'); import rmconf; print(rmconf.work())")
R="$WORK/renders"; mkdir -p "$R"; T="$B/out/finish"; mkdir -p "$T"
SRC="$B/out/reel_$N.mp4"; [ -f "$SRC" ] || SRC="$R/reel_$N.mp4"
[ -f "$SRC" ] || { echo "no render for $N: run job.sh or remote_render.sh first"; exit 1; }
python3 "$HERE/voiceclean.py" "$SRC" "$T/v.mp4"
python3 "$HERE/pcut.py" "$T/v.mp4" "$T/cut.mp4" --caps "$B/caps.json" "$@"
python3 "$HERE/vadgaps.py" "$T/cut.mp4"
python3 "$HERE/facecheck.py" "$T/cut.mp4" --strip "$R/reel_${N}_face.jpg"
cp "$T/cut.mp4" "$R/reel_$N.mp4" && rm -rf "$T"
echo "finished: $R/reel_$N.mp4 (look at $R/reel_${N}_face.jpg)"
