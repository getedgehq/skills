#!/usr/bin/env bash
# Encode a video for scroll scrubbing: dense keyframes, no audio, faststart,
# desktop and mobile variants plus poster images. Re-checks both outputs.
#
# Usage:
#   encode-scrub.sh <input-video> <outdir> [--fps 24] [--crf 28] [--desktop-width 1920] [--mobile-width 960]

set -euo pipefail

IN=""; OUT=""; FPS=24; CRF=28; DW=1920; MW=960
while [[ $# -gt 0 ]]; do
  case "$1" in
    --fps) FPS="$2"; shift 2 ;;
    --crf) CRF="$2"; shift 2 ;;
    --desktop-width) DW="$2"; shift 2 ;;
    --mobile-width) MW="$2"; shift 2 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) if [[ -z "$IN" ]]; then IN="$1"; elif [[ -z "$OUT" ]]; then OUT="$1"; else echo "error: unexpected argument: $1" >&2; exit 1; fi; shift ;;
  esac
done
[[ -z "$IN" || -z "$OUT" ]] && { echo "usage: encode-scrub.sh <input-video> <outdir>" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "error: ffmpeg not found" >&2; exit 1; }
[[ -f "$IN" ]] || { echo "error: no such file: $IN" >&2; exit 1; }
mkdir -p "$OUT"
HERE="$(cd "$(dirname "$0")" && pwd)"

encode() { # width gop crf outfile
  ffmpeg -v error -y -i "$IN" -an \
    -vf "fps=${FPS},scale=$1:-2:flags=lanczos,format=yuv420p" \
    -c:v libx264 -preset slow -crf "$3" -g "$2" -keyint_min "$2" -sc_threshold 0 -bf 0 \
    -profile:v high -movflags +faststart "$4"
}

echo "desktop: ${DW}px, keyframe every 2 frames, crf ${CRF}"
encode "$DW" 2 "$CRF" "$OUT/hero-desktop.mp4"
echo "mobile: ${MW}px, keyframe every frame, crf $((CRF + 2))"
encode "$MW" 1 "$((CRF + 2))" "$OUT/hero-mobile.mp4"

ffmpeg -v error -y -i "$OUT/hero-desktop.mp4" -frames:v 1 -q:v 3 "$OUT/poster.jpg"
ffmpeg -v error -y -i "$OUT/hero-mobile.mp4" -frames:v 1 -q:v 4 "$OUT/poster-mobile.jpg"

python3 "$HERE/check-scrub.py" "$OUT/hero-desktop.mp4" --budget-mb 12
python3 "$HERE/check-scrub.py" "$OUT/hero-mobile.mp4" --budget-mb 5
