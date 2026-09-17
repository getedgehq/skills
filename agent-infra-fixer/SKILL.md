---
name: agent-infra-fixer
description: Fix the agent's own environment when skill-miner surfaces infra-class failures - broken hooks, permission-mode denials, wrappers, sandboxing. Use when session mining shows hook errors ("No stderr output"), denied permissions, or environment breakage that no skill could fix. The rule: infra failures get fixed in the environment, never worked around with skills.
---

# agent-infra-fixer

skill-miner classifies clusters as `infra` or `task`. Infra clusters come here.
No eval, no skill draft - reproduce, fix, verify, record.

## Process

1. **Reproduce.** Re-run the failing component on a triggering input. For hooks:
   pipe a realistic tool-input JSON into the hook script and check exit code AND
   which stream the message lands on.
2. **Fix the environment** (hook, wrapper, permission config), minimal diff.
3. **Verify with a trigger/benign pair**: the fix must fire on the bad input and
   stay silent on good input.
4. **Record** in `$FORGE_ROOT/ledger.jsonl` as `decision: "infra-fix"` so the next
   mining run can confirm the cluster count dropped.

## Known failure class: stdout-block hooks

PreToolUse hooks that print block reasons to **stdout** instead of **stderr**
surface to the agent as `hook error: No stderr output` - the block works but the
agent never sees WHY, retries, and the error count explodes. Exit code must be 2
with the reason on stderr.

Detector/fixer (dry-run by default, `--apply` patches with `.bak-stdrefix` backups):

```bash
python3 scripts/fix-hooks.py           # scan + report
sudo python3 scripts/fix-hooks.py --apply
```

Adapt the FIXES table for the machine's hook set. 2026-09-16: this class was the
#1 cluster on both of Federico's machines (117 errors in 40% of Mac sessions,
180 in 22 AX41 sessions) - ten hooks fixed, verified with test pairs.
