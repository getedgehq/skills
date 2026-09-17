#!/usr/bin/env bash
# run_eval.sh <brief.json> <arm: with|without> <skill-dir-or-empty>
# Generalised from getedge-skill-evals-3/harness/run-arm.sh.
# One arm of a skill-forge eval: isolated dir, headless claude, stream-json capture.
# Harness metadata lives in <run>.meta so the agent under test cannot see it.
set -euo pipefail
ROOT="${FORGE_ROOT:-$HOME/skill-forge}"
BRIEF="$1"; ARM="$2"; SKILL_DIR="${3:-}"
ID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$BRIEF")
DIR="$ROOT/runs/$ID/$ARM"
META="$ROOT/runs/$ID/$ARM.meta"
[[ -e "$DIR" ]] && { echo "refusing: $DIR exists" >&2; exit 1; }
mkdir -p "$DIR" "$META"

PROMPT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prompt'])" "$BRIEF")
SETUP=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('setup',''))" "$BRIEF")
printf '%s' "$PROMPT" > "$META/prompt.txt"
cp "$BRIEF" "$META/brief.json"

if [[ "$ARM" == "with" ]]; then
  [[ -d "$SKILL_DIR" ]] || { echo "with-arm needs a skill dir" >&2; exit 1; }
  mkdir -p "$DIR/.claude/skills"
  # -L: many production skills are symlinks (deployment pattern); copy the target
  # content or the arm runs with a dangling link and silently has no skill.
  cp -rL "$SKILL_DIR" "$DIR/.claude/skills/"
fi

cd "$DIR"
if [[ -n "$SETUP" ]]; then
  bash -c "$SETUP" > "$META/setup.log" 2>&1 || { echo "setup failed"; exit 1; }
fi

MODEL="${FORGE_MODEL:-claude-sonnet-4-5}"
TIMEOUT="${FORGE_TIMEOUT:-1200}"
start=$(date +%s)
set +e
timeout "$TIMEOUT" nice -n 10 claude -p "$PROMPT" --model "$MODEL" \
  --setting-sources project,local --strict-mcp-config \
  --permission-mode acceptEdits --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Skill" \
  --output-format stream-json --verbose < /dev/null > "$META/transcript.jsonl" 2> "$META/stderr.log"
code=$?
set -e
echo "{\"id\":\"$ID\",\"arm\":\"$ARM\",\"model\":\"$MODEL\",\"exit\":$code,\"seconds\":$(( $(date +%s) - start ))}" > "$META/run.json"
cat "$META/run.json"
