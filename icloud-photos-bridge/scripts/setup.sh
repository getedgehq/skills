#!/bin/bash
# One-time setup on the Mac that owns the iCloud Photos library. Safe to re-run.
set -euo pipefail
if ! command -v osxphotos >/dev/null; then
  if command -v pipx >/dev/null; then pipx install osxphotos
  elif command -v uv >/dev/null; then uv tool install osxphotos
  else echo "Install pipx first: brew install pipx && pipx ensurepath"; exit 1; fi
fi
# Pillow for montages (pipx/uv venvs don't ship it)
pipx inject osxphotos pillow >/dev/null 2>&1 || uv tool install --force osxphotos --with pillow >/dev/null 2>&1 || true
PY="$(dirname "$(readlink -f "$(command -v osxphotos)")")/python"
[ -x "$PY" ] || PY="$HOME/.local/pipx/venvs/osxphotos/bin/python"
mkdir -p "$HOME/.config/icloud-photos"
echo "$PY" > "$HOME/.config/icloud-photos/python"
# Where these scripts live, so selfie-picker and broll-picker find them wherever the skill was installed.
(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) > "$HOME/.config/icloud-photos/bridge_dir"
echo "osxphotos: $(osxphotos --version | head -1)"
echo "python:    $PY"
echo "scripts:   $(cat "$HOME/.config/icloud-photos/bridge_dir")"
# Reading the library needs Full Disk Access for the terminal app running the agent.
if "$PY" -c "import osxphotos; db=osxphotos.PhotosDB(); print('library ok:', len(db.photos()), 'items')" 2>/dev/null; then
  echo "READY"
else
  echo "BLOCKED: give your terminal Full Disk Access (System Settings > Privacy & Security > Full Disk Access), restart it, re-run."
  exit 2
fi
