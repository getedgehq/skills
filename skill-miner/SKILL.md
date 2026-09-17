---
name: skill-miner
description: Mine Claude session logs for recurring failures, user frustration, token-heavy sessions, and repeated manual workflows, then find and score skills that could fix them. Use when asked "what skills am I missing", "mine my session logs", "where do my agents keep failing", "find a skill for X", "which sessions burned the most tokens", or to discover existing skills from skills.sh / Floom / local pools before writing anything new. Pairs with skill-eval-loop, which proves candidates before adoption.
---

# skill-miner

Two jobs: (1) find where the agent actually suffers in real session logs,
(2) find the best existing or drafted skill for each pain point. Never adopt
anything here - that is skill-eval-loop's job, with proof.

## Mine

```bash
python3 scripts/mine.py --sessions 100 --out failures.json
# root's history on a server: sudo python3 scripts/mine.py --projects /root/.claude/projects ...
```

Output `failures.json`:
- **clusters** - recurring tool errors and user corrections, classified
  `infra` (broken environment: hooks, permissions, rate limits) vs `task`
  (agent behavior a skill could change). Only patterns seen in >=2 sessions.
- **anger** - user messages with frustration markers (wtf, "why is", "!!!",
  German equivalents). Highest-signal source of workflow skills.
- **top_spend_sessions** - sessions ranked by output tokens + error counts.
- **repeated_workflow** clusters - near-identical opening prompts across
  sessions. A workflow done by hand N times is a skill waiting to be written.

Eval-harness sessions and system banners are filtered out automatically.

## Find + score candidates

```bash
python3 scripts/match.py failures.json --index 0 --out candidates.json
python3 scripts/score.py candidates.json failures.json --index 0
```

- `match.py` searches local installs, the getedgehq skills repo, the Floom
  registry, and skills.sh (`npx skills find`, install counts included).
- `score.py` enriches each candidate with its actual SKILL.md (fetched for
  registry hits), the failure evidence, and ledger history, then LLM-scores
  P(measurable improvement) 0-1. Only candidates >=0.5 deserve eval spend.
- Nothing matches? `draft.py failures.json --index 0` drafts a minimal
  candidate skill from the failure evidence into `$FORGE_ROOT/drafts/`.

## Rules

- Infra-class clusters go to **agent-infra-fixer** (fix the hook/permission/wrapper,
  verify, record in ledger). No skill fixes a broken environment.
- Drafted skills must name task-context triggers in their description -
  "prevents X error" never gets loaded, the agent can't know it will err.
- A candidate is a hypothesis, not an adoption. Hand off to skill-eval-loop.

State lives in `$FORGE_ROOT` (default `~/skill-forge`): mined/, drafts/, ledger.jsonl.
