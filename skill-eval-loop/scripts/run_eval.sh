#!/usr/bin/env bash
# run_eval.sh <brief.json> <arm: with|without> <skill-dir-or-empty>
# Generalised from the GetEdge skill-eval harness (run one arm of an A/B).
# One arm of a skill-forge eval: isolated dir, headless agent, transcript capture.
# Harness metadata lives in <run>.meta so the agent under test cannot see it.
#
# Each arm installs the skill directory it is handed, and the without-arm is
# normally handed none. Handing it one makes the baseline the skill already
# installed for this trigger rather than an empty machine, which is the
# comparison an adoption into a populated fleet actually rests on. Only the
# with-arm requires a skill; everything downstream reads the arms by what they
# were given, not by their names.
#
# FORGE_AGENT   claude (default) | codex | opencode - the agent CLI under test
# FORGE_MODEL   model id for that CLI
# FORGE_SAMPLE  sample number; runs land in runs/<id>/s<N>/<arm> (repeat samples
#               make a verdict about the skill, not about one lucky run)
set -euo pipefail
ROOT="${FORGE_ROOT:-$HOME/skill-forge}"
BRIEF="$1"; ARM="$2"; SKILL_DIR="${3:-}"
AGENT="${FORGE_AGENT:-claude}"
ID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$BRIEF")
BASE="$ROOT/runs/$ID"
[[ -n "${FORGE_SAMPLE:-}" ]] && BASE="$BASE/s$FORGE_SAMPLE"
DIR="$BASE/$ARM"
META="$BASE/$ARM.meta"
# Guard the directory the judge reads from, not only the one the agent writes in.
# The agent's workdir is $DIR and the harness metadata is $META, and the verdict is
# built entirely out of $META: final.txt, transcript.jsonl, run.json. Everything in
# there is truncated by the run itself except final.txt, which only the codex arm
# writes, so a $META left behind by an earlier pass hands the judge a previous run's
# answer as this run's. That is the failure of #43 with the evidence pointing the
# other way: there the dead arm answered with the runner's error and was catchable,
# here it answers with a real reply somebody's agent really wrote, and nothing
# downstream can tell. Refuse both.
for d in "$DIR" "$META"; do
  [[ -e "$d" ]] && { echo "refusing: $d exists - delete the sample dir to rerun" >&2; exit 1; }
done
mkdir -p "$DIR" "$META"

PROMPT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prompt'])" "$BRIEF")
SETUP=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('setup',''))" "$BRIEF")
printf '%s' "$PROMPT" > "$META/prompt.txt"
cp "$BRIEF" "$META/brief.json"

if [[ "$ARM" == "with" && ! -d "$SKILL_DIR" ]]; then
  echo "with-arm needs a skill dir" >&2; exit 1
fi
if [[ -n "$SKILL_DIR" ]]; then
  [[ -d "$SKILL_DIR" ]] || { echo "no such skill dir: $SKILL_DIR" >&2; exit 1; }
  # -L: many production skills are symlinks (deployment pattern); copy the target
  # content or the arm runs with a dangling link and silently has no skill.
  # Each CLI discovers project skills in its own folder.
  case "$AGENT" in
    claude)   SK="$DIR/.claude/skills";;
    codex)    SK="$DIR/.agents/skills";;
    opencode) SK="$DIR/.opencode/skill";;
    *) echo "unknown FORGE_AGENT $AGENT" >&2; exit 1;;
  esac
  mkdir -p "$SK"
  cp -rL "$SKILL_DIR" "$SK/"
fi

cd "$DIR"
# setup may copy shared fixtures from $FORGE_ROOT/fixtures
export FORGE_ROOT="$ROOT"
if [[ -n "$SETUP" ]]; then
  bash -c "$SETUP" > "$META/setup.log" 2>&1 || { echo "setup failed"; exit 1; }
fi

TIMEOUT="${FORGE_TIMEOUT:-1200}"
start=$(date +%s)
set +e
# macOS ships no `timeout`; fall back to gtimeout (coreutils) or a perl alarm.
if command -v timeout >/dev/null; then TO=(timeout "$TIMEOUT")
elif command -v gtimeout >/dev/null; then TO=(gtimeout "$TIMEOUT")
else TO=(perl -e 'alarm shift; exec @ARGV' "$TIMEOUT"); fi
case "$AGENT" in
  claude)
    MODEL="${FORGE_MODEL:-claude-sonnet-5}"
    "${TO[@]}" nice -n 10 claude -p "$PROMPT" --model "$MODEL" \
      --setting-sources project,local --strict-mcp-config \
      --permission-mode acceptEdits --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Skill" \
      --output-format stream-json --verbose < /dev/null > "$META/transcript.jsonl" 2> "$META/stderr.log"
    code=$?;;
  codex)
    MODEL="${FORGE_MODEL:-}"
    M=(); [[ -n "$MODEL" ]] && M=(-m "$MODEL")
    "${TO[@]}" nice -n 10 codex exec --skip-git-repo-check --sandbox workspace-write "${M[@]}" \
      --json -o "$META/final.txt" "$PROMPT" < /dev/null > "$META/transcript.jsonl" 2> "$META/stderr.log"
    code=$?;;
  opencode)
    MODEL="${FORGE_MODEL:-}"
    M=(); [[ -n "$MODEL" ]] && M=(-m "$MODEL")
    "${TO[@]}" nice -n 10 opencode run --pure --auto "${M[@]}" --format json "$PROMPT" \
      < /dev/null > "$META/transcript.jsonl" 2> "$META/stderr.log"
    code=$?;;
esac
set -e
python3 - "$META" "$ID" "$ARM" "$AGENT" "$MODEL" "${FORGE_SAMPLE:-}" "$code" "$(( $(date +%s) - start ))" <<'PYEOF'
import json, os, re, sys
meta, rid, arm, agent, model, sample, code, secs = sys.argv[1:]
row = {"id": rid, "arm": arm, "agent": agent, "model": model, "sample": sample,
       "exit": int(code), "seconds": int(secs)}
if row["exit"] != 0:
    # keep the agent's own failure reason (quota, auth, timeout) next to the exit code
    err = ""
    for line in open(os.path.join(meta, "transcript.jsonl"), errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        msg = d.get("message") if d.get("type") == "error" else (d.get("result") if d.get("is_error") else None)
        if isinstance(msg, str):
            err = msg
    if not err:
        tail = [l for l in open(os.path.join(meta, "stderr.log"), errors="replace").read().splitlines() if l.strip()]
        err = tail[-1] if tail else ("timeout" if row["exit"] == 124 else "")
    row["error"] = err[:300]
json.dump(row, open(os.path.join(meta, "run.json"), "w"))
PYEOF
cat "$META/run.json"
