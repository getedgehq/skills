#!/usr/bin/env bash
# forge.sh - the full loop: mine -> brief -> match -> eval(with/without) -> judge -> gate
# Usage: forge.sh [--mode errors|corrections] [--sessions N] [--cluster-index I]
#                 [--memory DIR] [--samples N] [--skill-dir PATH] [--brief FILE] [--probation] [--dry-run]
# --mode corrections (recommended) mines the moments the user corrected the agent and
#   builds knowledge-gap briefs; errors mines tool-error clusters (generic, often ties).
# --memory DIR  the user's saved rule files; mapped to themes and fed to brief + draft.
# --samples N   eval samples per arm (default 3); verdict = strict majority (aggregate.py).
# --brief FILE  skip mining/briefing and eval this brief (needs --skill-dir).
# --dry-run stops before eval spend. Without --skill-dir, the top matched LOCAL
# candidate is used, else a skill is drafted from the cluster.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# mining/scoring/drafting live in the sibling skill-miner skill
MINER="${MINER_SCRIPTS:-$(cd "$HERE/../../skill-miner/scripts" 2>/dev/null && pwd || echo "$HERE")}"
export FORGE_ROOT="${FORGE_ROOT:-$HOME/skill-forge}"
PROJECTS="${FORGE_PROJECTS:-$HOME/.claude/projects}"
mkdir -p "$FORGE_ROOT"/{mined,briefs,runs}

SESSIONS=40; IDX=0; SKILL_DIR=""; DRY=0; MODE=errors; MEMORY=""; SAMPLES=3; BRIEF=""; PROB=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2;;
    --memory) MEMORY="$2"; shift 2;;
    --samples) SAMPLES="$2"; shift 2;;
    --brief) BRIEF="$2"; shift 2;;
    --sessions) SESSIONS="$2"; shift 2;;
    --cluster-index) IDX="$2"; shift 2;;
    --skill-dir) SKILL_DIR="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    --probation) PROB=(--probation); shift;;
    *) echo "unknown arg $1" >&2; exit 1;;
  esac
done

eval_brief() {  # eval_brief <brief> <skill-dir>: N samples, blind judge each, majority, gate
  local brief="$1" skill="$2" s
  for s in $(seq 1 "$SAMPLES"); do
    FORGE_SAMPLE=$s bash "$HERE/run_eval.sh" "$brief" without ""
    FORGE_SAMPLE=$s bash "$HERE/run_eval.sh" "$brief" with "$skill"
    python3 "$HERE/judge.py" "$brief" --sample "$s"
  done
  python3 "$HERE/aggregate.py" "$brief"
  python3 "$HERE/gate.py" "$brief" "$skill" --adopt-dir "${FORGE_ADOPT_DIR:-$HOME/.agents/skills}" ${PROB[@]+"${PROB[@]}"}
}

if [[ -n "$BRIEF" ]]; then
  [[ -d "$SKILL_DIR" ]] || { echo "--brief needs --skill-dir" >&2; exit 1; }
  eval_brief "$BRIEF" "$SKILL_DIR"; exit 0
fi

FAIL="$FORGE_ROOT/mined/failures.json"
if [[ "$MODE" == corrections ]]; then
  FAIL="$FORGE_ROOT/mined/corrections.json"
  M=(); [[ -n "$MEMORY" ]] && M=(--memory "$MEMORY")
  python3 "$MINER/corrections.py" --sessions "$SESSIONS" ${M[@]+"${M[@]}"} --out "$FAIL"
else
  python3 "$MINER/mine.py" --sessions "$SESSIONS" --projects "$PROJECTS" --out "$FAIL"
fi

# Route the chosen cluster: infra-class goes to agent-infra-fixer, not the eval loop.
# If the requested index is infra, advance to the next task-class cluster.
IDX=$(python3 - <<PYEOF
import json, sys
clusters = json.load(open("$FAIL"))["clusters"]
if not clusters:
    sys.exit("no clusters mined - nothing to do")
i = $IDX
while i < len(clusters) and clusters[i].get("class") == "infra":
    print(f"cluster {i} is infra-class -> route to agent-infra-fixer: {clusters[i]['signature'][:80]}", file=sys.stderr)
    i += 1
if i >= len(clusters):
    sys.exit("all mined clusters are infra-class - nothing to eval")
print(i)
PYEOF
)

KG=(); [[ "$MODE" == corrections ]] && KG=(--knowledge-gap)
BRIEF_OUT=$(python3 "$HERE/brief.py" "$FAIL" --index "$IDX" --out "$FORGE_ROOT/briefs" ${KG[@]+"${KG[@]}"} | head -1)
BRIEF="$BRIEF_OUT"
echo "brief: $BRIEF"

CAND="$FORGE_ROOT/mined/candidates.json"
python3 "$MINER/match.py" "$FAIL" --index "$IDX" --out "$CAND"

SCORED="$FORGE_ROOT/mined/scored.json"
python3 "$MINER/score.py" "$CAND" "$FAIL" --index "$IDX" --out "$SCORED"

if [[ -z "$SKILL_DIR" ]]; then
  SKILL_DIR=$(python3 -c "
import json
scored = json.load(open('$SCORED'))['scored']
local = [c for c in scored if c.get('path') and c.get('potential', 0) >= 0.5]
print(local[0]['path'] if local else '')")
fi
if [[ -z "$SKILL_DIR" ]]; then
  echo "no candidate scored >=0.5 potential - drafting a candidate skill from the failure cluster"
  SKILL_DIR=$(python3 "$MINER/draft.py" "$FAIL" --index "$IDX")
fi
[[ -n "$SKILL_DIR" && -d "$SKILL_DIR" ]] || { echo "no candidate skill - pass --skill-dir"; exit 1; }
echo "candidate skill: $SKILL_DIR"
[[ "$DRY" == 1 ]] && { echo "dry run, stopping before eval"; exit 0; }

eval_brief "$BRIEF" "$SKILL_DIR"
