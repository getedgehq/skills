# Evaluation status

**This result did not clear the repository bar** (a 95% confidence interval on the judge point delta that excludes zero, fixed in advance). It is a directional check on one synthetic task, not a measured effect. Do not read it as a guarantee.

What was run: one held-out synthetic task, billing reconciliation (contract schedule vs invoice export, with credit notes, merged and parent/child accounts, FX). Agent: Claude Sonnet (Claude Code), 8 attempts per arm, fully correct output required. The task data was generated for this check and is not published, and the Skill was written from general domain knowledge before the failures were reviewed.

| | fully correct runs |
| --- | --- |
| Without the Skill | 1 of 8 |
| With the Skill mounted, instruction unchanged | 7 of 8 |
| Difference | +75 points |

Limits: n=8 per arm on a single task; the without-Skill runs came from an earlier batch, not run at the same time; the with-Skill arm was not repeated; one of the eight with-skill runs ended in an agent timeout and counts as a failure. Session logs and grader verdicts for this check are not in this repository.
