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
# Both dirs, for the reason spelled out in run_eval.sh: the verdict is built out of
# $META, and a $META left behind by an earlier pass hands the judge that pass's answer.
for d in "$DIR" "$META"; do
  [[ -e "$d" ]] && { echo "refusing: $d exists - delete the sample dir to rerun" >&2; exit 1; }
done
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
  # one image, so the arms cannot differ anywhere but the --skill flag. Both
  # arms can start together, so serialize the check and render. A directory
  # existence check alone races while fixture trees are being copied.
  mkdir -p "$BASE"
  python3 - "$BASE/task-render.lock" "$HERE/harbor_task.py" "$BRIEF" "$TASK" <<'PY'
import fcntl, os, shutil, subprocess, sys
lock_path, renderer, brief, task = sys.argv[1:]
with open(lock_path, "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    marker = os.path.join(task, ".render-complete")
    if not os.path.isfile(marker):
        if os.path.exists(task):
            shutil.rmtree(task)
        subprocess.check_call([sys.executable, renderer, brief, task], stdout=subprocess.DEVNULL)
        with open(marker, "w") as completed:
            completed.write("ok\n")
PY
fi

ARGS=(run -p "$TASK" -a "$HAGENT" --n-concurrent 1 -o "$META/jobs"
      --agent-setup-timeout-multiplier "${FORGE_HARBOR_SETUP_MULTIPLIER:-3}")
[[ -n "$MODEL" ]] && ARGS+=(-m "$MODEL")
if [[ "$ARM" == "with" && ! -d "$SKILL_DIR" ]]; then
  echo "with-arm needs a skill dir" >&2; exit 1
fi
# Whatever the arm was handed, same as the local runner: a baseline given the skill
# already installed for this trigger is the comparison an adoption rests on, and the
# arm names decide nothing. The without arm handed nothing still receives no --skill
# and no skills directory, which is what keeps the blind.
if [[ -n "$SKILL_DIR" ]]; then
  [[ -d "$SKILL_DIR" ]] || { echo "no such skill dir: $SKILL_DIR" >&2; exit 1; }
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
# Fall back to the CLI's own credential file. `claude setup-token` mints a
# long-lived token and is the right thing to store in AgentWallet, but it needs a
# browser, so on a host where nobody can complete that flow this reads the access
# token Claude Code already keeps here and refreshes on its own. It is read, never
# written: nothing in this script touches the login state, because a run that
# logged the host out would cost far more than the eval it was trying to save.
CLAUDE_CREDS="${CLAUDE_CREDS:-$HOME/.claude/.credentials.json}"
if [[ "$AGENT" == "claude" && -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" && -r "$CLAUDE_CREDS" ]]; then
  CLAUDE_CODE_OAUTH_TOKEN="$(python3 - "$CLAUDE_CREDS" <<'PY' || true
import json, sys, time
try:
    d = json.load(open(sys.argv[1]))["claudeAiOauth"]
except Exception:
    sys.exit(0)
# expiresAt is milliseconds. An expired token fails deep inside the container with
# an opaque error, so treat it as absent here and let the check below say so.
if d.get("expiresAt", 0) / 1000 <= time.time():
    sys.exit(0)
sys.stdout.write(d.get("accessToken", ""))
PY
)"
  export CLAUDE_CODE_OAUTH_TOKEN
fi
[[ "$AGENT" == "claude" ]] && export CLAUDE_FORCE_OAUTH="${CLAUDE_FORCE_OAUTH:-1}"
if [[ "$AGENT" == "claude" && -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
  echo "no usable CLAUDE_CODE_OAUTH_TOKEN. Either run 'claude setup-token' and store" >&2
  echo "it as anthropic/oauth-token/claude-code in AgentWallet, or log the CLI in on" >&2
  echo "this host so $CLAUDE_CREDS holds an unexpired token." >&2
  exit 1
fi

# Codex authenticates by file, not by token: CODEX_FORCE_AUTH_JSON makes Harbor
# upload auth.json into the container. Default it on for the same reason
# CLAUDE_FORCE_OAUTH defaults on, and fail here if the file is missing rather
# than let Harbor fall back to an OPENAI_API_KEY we do not have. That fallback
# is the dangerous one: it would not error, it would bill an API key or run
# unauthenticated deep inside a container and surface as a task failure that
# looks like the skill's fault.
CODEX_AUTH="${CODEX_AUTH:-$HOME/.codex/auth.json}"
if [[ "$AGENT" == "codex" ]]; then
  export CODEX_FORCE_AUTH_JSON="${CODEX_FORCE_AUTH_JSON:-1}"
  if [[ "$CODEX_FORCE_AUTH_JSON" == "1" && ! -r "$CODEX_AUTH" ]]; then
    echo "no readable $CODEX_AUTH. Log the Codex CLI in on this host, or set" >&2
    echo "CODEX_FORCE_AUTH_JSON=0 to use an API key instead." >&2
    exit 1
  fi
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

# Under sudo, Harbor writes the whole job tree as root, and the step below runs as
# the invoking user: the first real container pair died on PermissionError reading
# the agent's own session log, after the run had already been paid for. Hand the
# tree back before anything tries to read it. Failures here are not fatal on their
# own - the read below will say what it could not open - but a silent chown that
# did nothing would turn this into the same error one line later.
if [[ "${FORGE_HARBOR_SUDO:-}" == "1" && -d "$META/jobs" ]]; then
  sudo -n chown -R "$(id -u):$(id -g)" "$META/jobs" \
    || echo "could not take ownership of $META/jobs back from root" >&2
fi

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
