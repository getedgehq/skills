#!/usr/bin/env bash
# Reuse GetEdge's skill-eval-loop with a two-arm explicit-load treatment.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVAL="$ROOT/vendor/skill-eval-loop/scripts"
BRIEF="${1:?usage: run_explicit_eval.sh BRIEF SKILL_DIR [SAMPLES]}"
SKILL_DIR="${2:?usage: run_explicit_eval.sh BRIEF SKILL_DIR [SAMPLES]}"
SAMPLES="${3:-3}"

[[ -f "$BRIEF" ]] || { echo "brief not found: $BRIEF" >&2; exit 2; }
[[ -f "$SKILL_DIR/SKILL.md" ]] || { echo "candidate has no SKILL.md: $SKILL_DIR" >&2; exit 2; }
[[ "$SAMPLES" =~ ^[1-9][0-9]*$ ]] || { echo "samples must be a positive integer" >&2; exit 2; }
(( SAMPLES <= 6 )) || { echo "refusing more than 6 samples" >&2; exit 2; }

STATE="${FORGE_ROOT:-$HOME/skill-forge}"
mkdir -p "$STATE/brain-scan"
BASE_BRIEF="$STATE/brain-scan/base-brief.json"
EXPLICIT="$STATE/brain-scan/explicit-brief.json"
DELIVERY="$STATE/brain-scan/explicit-delivery"
for generated in "$BASE_BRIEF" "$EXPLICIT"; do
  [[ ! -e "$generated" ]] || { echo "refusing to overwrite $generated" >&2; exit 2; }
done
[[ ! -e "$DELIVERY" ]] || { echo "refusing to overwrite $DELIVERY" >&2; exit 2; }
mkdir "$DELIVERY"

python3 - "$BRIEF" "$SKILL_DIR/SKILL.md" "$BASE_BRIEF" "$EXPLICIT" <<'PY'
import hashlib, json, pathlib, sys
brief_path, skill_path, base_path, out_path = map(pathlib.Path, sys.argv[1:])
brief = json.loads(brief_path.read_text())
# Older Harbor briefs unpacked into /app because that was their container workdir.
# The local runner already starts inside a fresh arm, so normalize only this exact
# setup destination; all other setup bytes remain frozen.
brief["setup"] = brief.get("setup", "").replace("tar -xz -C /app", "tar -xz -C .")
base_path.write_text(json.dumps(brief, indent=2) + "\n")
skill = skill_path.read_text()
brief["prompt"] = (
    "The following Skill is loaded for this task. Apply it where relevant.\n\n"
    "<loaded_skill>\n" + skill + "\n</loaded_skill>\n\n"
    "<task>\n" + brief["prompt"] + "\n</task>"
)
brief["brain_scan_treatment"] = {
    "mode": "explicit_load",
    "skill_sha256": hashlib.sha256(skill.encode()).hexdigest(),
}
out_path.write_text(json.dumps(brief, indent=2) + "\n")
PY

cleanup() { rm -f "$BASE_BRIEF" "$EXPLICIT"; rmdir "$DELIVERY"; }
trap cleanup EXIT

run_isolated() {
  local brief="$1" arm="$2" skill_dir="$3" sample="$4" isolated_home
  isolated_home=$(mktemp -d "${TMPDIR:-/tmp}/brain-scan-home.XXXXXX")
  # The evaluation subject must not see user-level Skills, instructions, or
  # state. OpenCode's --pure mode disables plugins but still retains $HOME;
  # replacing HOME and the XDG roots gives both arms the same empty surface.
  (
    trap 'rm -rf -- "$isolated_home"' EXIT
    HOME="$isolated_home" \
      XDG_CONFIG_HOME="$isolated_home/.config" \
      XDG_DATA_HOME="$isolated_home/.local/share" \
      XDG_CACHE_HOME="$isolated_home/.cache" \
      FORGE_SAMPLE="$sample" \
      bash "$EVAL/run_eval.sh" "$brief" "$arm" "$skill_dir"
  )
}

for sample in $(seq 1 "$SAMPLES"); do
  run_isolated "$BASE_BRIEF" without "" "$sample"
  # The treatment is already loaded in the prompt. Hand the runner an empty
  # delivery directory so it creates the arm without also advertising a
  # discoverable Skill; otherwise this would mix explicit load and discovery.
  run_isolated "$EXPLICIT" with "$DELIVERY" "$sample"
  python3 "$EVAL/judge.py" "$BRIEF" --sample "$sample"
done
python3 "$EVAL/aggregate.py" "$BRIEF"
