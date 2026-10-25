#!/usr/bin/env bash
# setup.sh : check tools, install Python deps, fetch the hook font (Funnel Display, SIL OFL) into $REEL_WORK/fonts.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CFG="${REEL_CONFIG:-$HOME/.config/reel-machine/config.env}"
WORK="${REEL_WORK:-}"
if [ -z "$WORK" ] && [ -f "$CFG" ]; then WORK="$(grep -E '^REEL_WORK=' "$CFG" | tail -1 | cut -d= -f2- | tr -d '"'"'")"; fi
WORK="${WORK:-$HOME/reel-machine}"; WORK="${WORK/#\~/$HOME}"
mkdir -p "$WORK"/{clips,transcripts,bundles,renders,fonts,sig}

ok=1
for t in ffmpeg ffprobe python3; do
  command -v "$t" >/dev/null || { echo "MISSING: $t"; ok=0; }
done
command -v rsvg-convert >/dev/null || echo "optional: rsvg-convert (librsvg) for logo_png.py"
python3 -m pip install -q -r "$HERE/requirements.txt" || python3 -m pip install -q --user -r "$HERE/requirements.txt" \
  || echo "pip could not install (managed Python?): use a venv, then pip install -r scripts/requirements.txt"
python3 -c "import PIL, numpy, av, faster_whisper, cv2" 2>/dev/null || { echo "MISSING Python deps (see scripts/requirements.txt)"; ok=0; }

F="$WORK/fonts/FunnelDisplay.ttf"
if [ ! -s "$F" ]; then
  curl -fsSL -o "$F" "https://github.com/google/fonts/raw/main/ofl/funneldisplay/FunnelDisplay%5Bwght%5D.ttf"
  curl -fsSL -o "$WORK/fonts/OFL.txt" "https://github.com/google/fonts/raw/main/ofl/funneldisplay/OFL.txt" || true
fi
[ -s "$F" ] && echo "hook font: $F" || { echo "could not fetch Funnel Display"; ok=0; }

if [ ! -f "$CFG" ]; then
  mkdir -p "$(dirname "$CFG")"; cp "$HERE/../config.example.env" "$CFG"
  echo "wrote $CFG from config.example.env: edit REEL_HANDLE and the Buffer channels"
fi
[ $ok = 1 ] && echo "READY (work dir $WORK)" || { echo "NOT READY"; exit 1; }
