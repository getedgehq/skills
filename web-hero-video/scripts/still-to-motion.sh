#!/usr/bin/env bash
# Turn a single hero still into a slow camera move (push-in or pan) for a
# scroll-scrubbed background, when no video model is available.
#
# Usage:
#   still-to-motion.sh <image> <out.mp4> [--seconds 8] [--fps 24] [--move push|pan-left|pan-right|rise] [--amount 0.12]
#
# The image is upscaled 4x before zoompan. zoompan rounds its crop to whole
# pixels, so on a 1920 frame the move steps visibly; at 4x the rounding error
# is a quarter pixel and the move reads as continuous.
set -euo pipefail

IN=""; OUT=""; SECS=8; FPS=24; MOVE=push; AMT=0.12
while [[ $# -gt 0 ]]; do
  case "$1" in
    --seconds) SECS="$2"; shift 2 ;;
    --fps) FPS="$2"; shift 2 ;;
    --move) MOVE="$2"; shift 2 ;;
    --amount) AMT="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) if [[ -z "$IN" ]]; then IN="$1"; elif [[ -z "$OUT" ]]; then OUT="$1"; else echo "error: unexpected argument: $1" >&2; exit 1; fi; shift ;;
  esac
done
[[ -z "$IN" || -z "$OUT" ]] && { echo "usage: still-to-motion.sh <image> <out.mp4>" >&2; exit 1; }
[[ -f "$IN" ]] || { echo "error: no such file: $IN" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "error: ffmpeg not found" >&2; exit 1; }

N=$(( SECS * FPS ))
# p runs 0..1 across the clip with ease-in-out, so the move starts and ends softly.
P="(0.5-0.5*cos(PI*on/${N}))"
case "$MOVE" in
  push)      Z="1+${AMT}*${P}"; X="iw/2-(iw/zoom/2)"; Y="ih/2-(ih/zoom/2)" ;;
  pan-left)  Z="1+${AMT}"; X="(iw-iw/zoom)*(1-${P})"; Y="ih/2-(ih/zoom/2)" ;;
  pan-right) Z="1+${AMT}"; X="(iw-iw/zoom)*${P}"; Y="ih/2-(ih/zoom/2)" ;;
  rise)      Z="1+${AMT}"; X="iw/2-(iw/zoom/2)"; Y="(ih-ih/zoom)*(1-${P})" ;;
  *) echo "error: --move must be push, pan-left, pan-right or rise" >&2; exit 1 ;;
esac

ffmpeg -v error -y -loop 1 -i "$IN" \
  -vf "scale=7680:4320:force_original_aspect_ratio=increase:flags=lanczos,crop=7680:4320,zoompan=z='${Z}':x='${X}':y='${Y}':d=${N}:s=1920x1080:fps=${FPS},format=yuv420p" \
  -frames:v "$N" -an -c:v libx264 -preset slow -crf 18 -movflags +faststart "$OUT"
echo "wrote $OUT (${SECS}s, ${FPS} fps, move ${MOVE}). Next: encode-scrub.sh from the scroll-video-site Skill."
