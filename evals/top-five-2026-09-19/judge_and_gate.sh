#!/usr/bin/env bash
# Judge valid pairs, aggregate them, and apply the predefined adoption gate.
set -euo pipefail

if [[ $# -ne 5 ]]; then
  echo "usage: $0 <forge-root> <brief.json> <skill-dir> <first-sample> <last-sample>" >&2
  exit 2
fi

FORGE_ROOT=$1
BRIEF=$2
SKILL_DIR=$3
FIRST=$4
LAST=$5
REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
export FORGE_ROOT FORGE_AGENT=codex FORGE_MODEL=openai/gpt-5.6-sol

for sample in $(seq "$FIRST" "$LAST"); do
  python3 "$REPO_ROOT/skill-eval-loop/scripts/judge.py" "$BRIEF" --sample "$sample"
done
python3 "$REPO_ROOT/skill-eval-loop/scripts/aggregate.py" "$BRIEF"
python3 "$REPO_ROOT/skill-eval-loop/scripts/gate.py" "$BRIEF" "$SKILL_DIR" \
  --adopt-dir "$FORGE_ROOT/adopted"
