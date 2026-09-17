---
name: skill-cockpit
description: Open a local browser cockpit for the agent self-improvement loop - see every installed skill, the new candidate skills, and the blind eval results and adopt/probation/reject decisions for all of them, and start mining, dry runs, full loops, evals and probation rechecks from the page. Use when asked to "show my skills", "open the cockpit", "what did the loop adopt", "show eval results", "manage my skills", or to watch skill-miner / skill-eval-loop runs. Local only, stdlib Python, no cloud.
---

# skill-cockpit

The UX layer over skill-miner and skill-eval-loop. One local page, three questions:
what skills do I have, which new ones are being considered, and did they prove
themselves on my own tasks.

## Start

```bash
lsof -iTCP:7788 -sTCP:LISTEN                 # check the port first
python3 scripts/cockpit.py                    # http://127.0.0.1:7788/
python3 scripts/cockpit.py --port 7790 --forge-root ~/skill-forge \
  --projects ~/.claude/projects --skills-dir ~/.claude/skills --skills-dir ~/.agents/skills
python3 scripts/cockpit.py --dump             # state JSON, no server (for agents/tests)
```

On a remote box, tunnel it: `ssh -L 7788:127.0.0.1:7788 host`, then open locally.

## What the page shows

- **Evals** - every run in `$FORGE_ROOT/runs`: winner (skill / baseline / tie /
  invalid), verify pass/fail and tool errors per arm, gate decision. Expand for the
  exact task prompt, the blind judge's reasons, per-criterion winners, the
  production failure it targets, and the probation recheck date.
- **Candidates** - drafted skills (`drafts/`) with their forge status, and scored
  matches from local, getedge, Floom and skills.sh with P(improvement). Any draft
  can be evaluated on an unused brief from the page.
- **Fleet** - installed skills (symlinks de-duplicated) with their latest ledger
  decision, filterable.
- **Failures** - mined clusters (task vs infra), frustration quotes, and the
  heaviest sessions by output tokens. Task clusters can be looped directly.
- **Jobs** - live log tail of anything the cockpit started.

## Rules

- Binds 127.0.0.1 only, rejects foreign Host headers, and every action needs the
  per-process token embedded in the page (no CSRF against localhost).
- Actions are a fixed whitelist that call the sibling skills' scripts. One job at a
  time, so eval spend stays visible. Evals never overwrite an existing run.
- The cockpit never adopts or deletes skills by itself - `gate.py` and
  `recheck.py` own those decisions, and the ledger records them.
- Scripts are found as siblings (`../../skill-miner/scripts`), then in
  `~/.agents/skills` / `~/.claude/skills`; override with `MINER_SCRIPTS` /
  `EVAL_SCRIPTS`.
