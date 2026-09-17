#!/usr/bin/env bash
# run_eval_harbor.sh <brief.json> <arm: with|without> <skill-dir-or-empty>
#
# The same contract as run_eval.sh - same arguments, same output layout, so
# judge.py, aggregate.py and gate.py read a Harbor arm and a local arm the same
# way - but the agent runs in a container Harbor builds, not in a directory on
# this host.
#
# Why bother: run_eval.sh installs the skill by hand and has to know where each
# CLI looks for one. It got that wrong (.claude only), which put the skill's path
# in the judge's prompt on any other runner. Harbor injects the skill through the
# agent class that owns that knowledge, and in the without arm never creates the
# directory at all. The blind stops depending on us remembering a path.
#
# FORGE_AGENT        claude (default) | codex | opencode
# FORGE_MODEL        model id passed to Harbor
# FORGE_SAMPLE       sample number; runs land in runs/<id>/s<N>/<arm>
# FORGE_HARBOR       harbor binary (default: harbor)
# FORGE_HARBOR_SUDO  set to 1 where the docker socket needs root (AX41)
# FORGE_TASK_DIR     reuse an already-rendered task dir instead of rendering one
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${FORGE_ROOT:-$HOME/skill-forge}"
BRIEF="$1"; ARM="$2"; SKILL_DIR="${3:-}"
AGENT="${FORGE_AGENT:-claude}"
HARBOR="${FORGE_HARBOR:-harbor}"

ID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$BRIEF")
BASE="$ROOT/runs/$ID"
[[ -n "${FORGE_SAMPLE:-}" ]] && BASE="$BASE/s$FORGE_SAMPLE"
DIR="$BASE/$ARM"
META="$BASE/$ARM.meta"
[[ -e "$DIR" ]] && { echo "refusing: $DIR exists" >&2; exit 1; }
mkdir -p "$DIR" "$META"

python3 -c "import json,sys;sys.stdout.write(json.load(open(sys.argv[1]))['prompt'])" \
  "$BRIEF" > "$META/prompt.txt"
cp "$BRIEF" "$META/brief.json"

# Harbor's own names for the agents our FORGE_AGENT values refer to.
case "$AGENT" in
  claude)   HAGENT="claude-code"; MODEL="${FORGE_MODEL:-anthropic/claude-sonnet-5}";;
  codex)    HAGENT="codex";       MODEL="${FORGE_MODEL:-openai/gpt-5.4}";;
  opencode) HAGENT="opencode";    MODEL="${FORGE_MODEL:-}";;
  *) echo "unknown FORGE_AGENT $AGENT" >&2; exit 1;;
esac

TASK="${FORGE_TASK_DIR:-}"
if [[ -z "$TASK" ]]; then
  TASK="$BASE/task"
  # Rendered once per sample and reused by both arms: one instruction file and
  # one image, so the arms cannot differ anywhere but the --skill flag.
  [[ -d "$TASK" ]] || python3 "$HERE/harbor_task.py" "$BRIEF" "$TASK" >/dev/null
fi

ARGS=(run -p "$TASK" -a "$HAGENT" --n-concurrent 1 -o "$META/jobs")
[[ -n "$MODEL" ]] && ARGS+=(-m "$MODEL")
if [[ "$ARM" == "with" ]]; then
  [[ -d "$SKILL_DIR" ]] || { echo "with-arm needs a skill dir" >&2; exit 1; }
  # -L first: production skills are deployed as symlinks, and Harbor uploads the
  # directory as it finds it, so a link would arrive dangling and the with arm
  # would silently be a second without arm.
  RESOLVED="$META/skill/$(basename "$SKILL_DIR")"
  mkdir -p "$(dirname "$RESOLVED")"
  cp -rL "$SKILL_DIR" "$RESOLVED"
  ARGS+=(--skill "$RESOLVED")
fi

# Subscription auth. The token is read into this process and exported; it is
# never an argument, never echoed, and never written to the run record. Harbor
# drops ANTHROPIC_API_KEY when CLAUDE_FORCE_OAUTH is truthy, so the arm bills the
# Max subscription instead of an API key we do not have.
if [[ "$AGENT" == "claude" && -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
  if command -v agentwallet >/dev/null; then
    CLAUDE_CODE_OAUTH_TOKEN="$(agentwallet get anthropic/oauth-token/claude-code 2>/dev/null || true)"
    export CLAUDE_CODE_OAUTH_TOKEN
  fi
fi
[[ "$AGENT" == "claude" ]] && export CLAUDE_FORCE_OAUTH="${CLAUDE_FORCE_OAUTH:-1}"
if [[ "$AGENT" == "claude" && -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
  echo "no CLAUDE_CODE_OAUTH_TOKEN: run 'claude setup-token' and store it as" >&2
  echo "anthropic/oauth-token/claude-code in AgentWallet" >&2
  exit 1
fi

RUN=("$HARBOR")
if [[ "${FORGE_HARBOR_SUDO:-}" == "1" ]]; then
  # Pass the auth through sudo explicitly rather than with -E: -E would carry
  # this shell's whole environment into a root process, and the point of naming
  # the variables is that only these cross the boundary.
  RUN=(sudo -n env "PATH=$PATH" "HOME=$HOME"
       "CLAUDE_FORCE_OAUTH=${CLAUDE_FORCE_OAUTH:-}"
       "CLAUDE_CODE_OAUTH_TOKEN=${CLAUDE_CODE_OAUTH_TOKEN:-}"
       "CODEX_FORCE_AUTH_JSON=${CODEX_FORCE_AUTH_JSON:-}"
       "$HARBOR")
fi

start=$(date +%s)
set +e
"${RUN[@]}" "${ARGS[@]}" > "$META/harbor.log" 2> "$META/stderr.log"
code=$?
set -e

# Harbor writes one trial per job here. Pull the agent's workdir into $DIR and
# its native session log into the transcript file judge.py already parses.
python3 - "$META" "$DIR" "$ID" "$ARM" "$AGENT" "$MODEL" "${FORGE_SAMPLE:-}" \
         "$code" "$(( $(date +%s) - start ))" <<'PYEOF'
import glob, json, os, shutil, sys
meta, workdir, rid, arm, agent, model, sample, code, secs = sys.argv[1:]
row = {"id": rid, "arm": arm, "agent": agent, "model": model, "sample": sample,
       "exit": int(code), "seconds": int(secs), "runner": "harbor"}

trials = sorted(glob.glob(os.path.join(meta, "jobs", "*", "*", "result.json")))
trial = os.path.dirname(trials[-1]) if trials else None

if trial:
    # /app as the agent left it becomes the arm's workdir, so the file manifest
    # the judge sees is the agent's output and nothing else: the skill lives in
    # the agent's own config dir inside the container and never reaches /app.
    app = os.path.join(trial, "artifacts", "app")
    if os.path.isdir(app):
        for name in os.listdir(app):
            dst = os.path.join(workdir, name)
            src = os.path.join(app, name)
            (shutil.copytree if os.path.isdir(src) else shutil.copy2)(src, dst)
    sessions = sorted(glob.glob(os.path.join(trial, "agent", "**", "*.jsonl"),
                                recursive=True), key=os.path.getmtime)
    if sessions:
        shutil.copy2(sessions[-1], os.path.join(meta, "transcript.jsonl"))
    res = json.load(open(os.path.join(trial, "result.json")))
    row["harbor_trial"] = os.path.basename(trial)
    # Harbor's own exception, when it had one, is the failure reason worth
    # keeping: a non-zero exit with no message reads as a mystery in the record.
    exc = res.get("exception_info") or {}
    if exc.get("exception_message"):
        row["error"] = str(exc["exception_message"])[:300]

if row["exit"] != 0 and "error" not in row:
    tail = [l for l in open(os.path.join(meta, "stderr.log"),
                            errors="replace").read().splitlines() if l.strip()]
    row["error"] = tail[-1][:300] if tail else ""
if not os.path.exists(os.path.join(meta, "transcript.jsonl")):
    open(os.path.join(meta, "transcript.jsonl"), "w").close()

json.dump(row, open(os.path.join(meta, "run.json"), "w"))
PYEOF
cat "$META/run.json"
