#!/usr/bin/env bash
# forge.sh - the full loop: mine -> brief -> match -> eval(with/without) -> judge -> gate
# Usage: forge.sh [--sessions N] [--cluster-index I] [--skill-dir PATH] [--dry-run]
# --dry-run stops after match (no eval spend). Without --skill-dir, the top matched
# LOCAL candidate is used; registry candidates need manual install first.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# mining/scoring/drafting live in the sibling skill-miner skill
MINER="${MINER_SCRIPTS:-$(cd "$HERE/../../skill-miner/scripts" 2>/dev/null && pwd || echo "$HERE")}"
export FORGE_ROOT="${FORGE_ROOT:-$HOME/skill-forge}"
PROJECTS="${FORGE_PROJECTS:-$HOME/.claude/projects}"
mkdir -p "$FORGE_ROOT"/{mined,briefs,runs}

SESSIONS=40; IDX=0; SKILL_DIR=""; DRY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sessions) SESSIONS="$2"; shift 2;;
    --cluster-index) IDX="$2"; shift 2;;
    --skill-dir) SKILL_DIR="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    *) echo "unknown arg $1" >&2; exit 1;;
  esac
done

FAIL="$FORGE_ROOT/mined/failures.json"
python3 "$MINER/mine.py" --sessions "$SESSIONS" --projects "$PROJECTS" --out "$FAIL"

BRIEF_OUT=$(python3 "$HERE/brief.py" "$FAIL" --index "$IDX" --out "$FORGE_ROOT/briefs" | head -1)
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

bash "$HERE/run_eval.sh" "$BRIEF" without ""
bash "$HERE/run_eval.sh" "$BRIEF" with "$SKILL_DIR"
python3 "$HERE/judge.py" "$BRIEF"
python3 "$HERE/gate.py" "$BRIEF" "$SKILL_DIR"
