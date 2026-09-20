#!/usr/bin/env bash
# Run valid Harbor A/B pairs with bounded concurrency.
set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
  echo "usage: $0 <forge-root> <brief.json> <skill-dir> <first-sample> [last-sample]" >&2
  exit 2
fi

FORGE_ROOT=$1
BRIEF=$2
SKILL_DIR=$3
FIRST=$4
LAST=${5:-$FIRST}
REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
RUNNER="$REPO_ROOT/skill-eval-loop/scripts/run_eval_harbor.sh"
mkdir -p "$FORGE_ROOT/logs"

for sample in $(seq "$FIRST" "$LAST"); do
  echo "sample $sample"
  FORGE_ROOT="$FORGE_ROOT" FORGE_SAMPLE="$sample" \
    FORGE_AGENT=codex FORGE_MODEL=openai/gpt-5.6-sol FORGE_HARBOR_SUDO=1 \
    bash "$RUNNER" "$BRIEF" without "" >"$FORGE_ROOT/logs/s${sample}-without.log" 2>&1 &
  baseline_pid=$!
  FORGE_ROOT="$FORGE_ROOT" FORGE_SAMPLE="$sample" \
    FORGE_AGENT=codex FORGE_MODEL=openai/gpt-5.6-sol FORGE_HARBOR_SUDO=1 \
    bash "$RUNNER" "$BRIEF" with "$SKILL_DIR" >"$FORGE_ROOT/logs/s${sample}-with.log" 2>&1 &
  treatment_pid=$!

  baseline_status=0
  treatment_status=0
  wait "$baseline_pid" || baseline_status=$?
  wait "$treatment_pid" || treatment_status=$?
  if [[ $baseline_status -ne 0 || $treatment_status -ne 0 ]]; then
    echo "sample $sample failed: baseline=$baseline_status treatment=$treatment_status" >&2
    exit 1
  fi
done
