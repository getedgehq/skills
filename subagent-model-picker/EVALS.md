# Does picking subagent models save money without losing quality?

One Claude Code lead (`claude-opus-5-5`) gets a small Python repo with four independent tasks and must hand each task to its own subagent. Two arms, same repo, same prompt apart from one sentence, same hidden grader:

- **All Opus:** "run every subagent on model opus".
- **Skill picks:** "Use the subagent-model-picker skill to choose each subagent's model", with this Skill in `.claude/skills/`.

**15 runs per arm, interleaved A, B, A, B. All 30 runs passed all 35 hidden checks. The Skill arm cost $0.725 per run on average against $1.011 for all Opus: 28.3% less (bootstrap 95% interval 25.0% to 31.4%). The ranges do not overlap: the most expensive Skill run ($0.852) cost less than the cheapest all-Opus run ($0.898).**

Run date: 2026-10-14, Claude Code 2.1.280, on one Linux host, one run at a time.

## The tasks

`TASKS.md` in the generated repo (`make_template.py`):

1. **Inventory:** list every public function without a docstring. Exact expected list, 1 check.
2. **Date bug:** fix `parse_date` so a failing test passes and the docstring's short-year rule holds. 9 hidden cases.
3. **Allocation:** implement largest-remainder money allocation from a docstring contract, no tests given. 13 hidden cases.
4. **Config:** convert an INI file to typed JSON. 12 checks.

The grader (`grade.py`) never runs inside the agent's sandbox and the agent never sees its cases. It also confirms the visible test suite is green.

## The numbers

| | All Opus | Skill picks |
| --- | --- | --- |
| Runs | 15 | 15 |
| Runs passing all 35 checks | 15 | 15 |
| Mean cost per run | $1.011 | $0.725 |
| Standard deviation | $0.065 | $0.048 |
| Cheapest / most expensive run | $0.898 / $1.122 | $0.669 / $0.852 |
| Median | $0.995 | $0.716 |

Every Skill run made the same picks: inventory on Haiku, date bug on Sonnet, allocation on Opus, config on Haiku. No escalations. Fable was available (`claude-fable-5-1`) and never picked, which is what the Skill says for tasks with a checkable result.

Mean spend per model in the Skill arm: Opus (lead plus the allocation subagent) $0.550, Sonnet $0.092, Haiku $0.083.

## Models actually used

Aliases were pinned with `ANTHROPIC_DEFAULT_{HAIKU,SONNET,OPUS,FABLE}_MODEL`, and every run's `modelUsage` and subagent transcripts confirm the IDs: `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-4-5-20251001`. An earlier three-run pilot without pinning ran `sonnet` as `claude-sonnet-5`; that pilot is superseded by this run.

## How cost was measured

Cost is recomputed from every assistant message in the lead and subagent transcripts at Anthropic API list prices (input, output, 5-minute and 1-hour cache writes, cache reads), per model, in `cost.py`. Claude Code's own `total_cost_usd` matches this exactly for the all-Opus arm. For the Skill arm it reads higher (mean $0.797), because Claude Code 2.1.280 does not know `claude-sonnet-5-5` (`costBasis: "unknown"`) and prices it at Opus rates. Per-run figures, both ways, are in `results.json`.

## The limits

- **One task set.** Four short tasks, all solvable by the cheaper models. The result says the Skill routes these well and saves about 28%; it does not show where the cheap tiers would start failing.
- **Easy ceiling.** Both arms score 35/35 every time, so this run cannot show a quality difference in either direction.
- **The baseline is all Opus,** the case where every subagent inherits an Opus lead. It is not a comparison against a human picking models.
- **Plan lines were skipped.** Step 3 asks the lead to print one plan line per task before spawning. In 15 of 15 runs the lead went straight to the Agent calls with the right `model` values and named the models only in its final report.
- **One run stalled.** In all-Opus run A-15 the lead never wrote its final report after all four subagents finished, and Claude Code exited with no result JSON after seven minutes. Its work was graded (35/35) and its cost taken from the transcripts ($0.898), which leaves out the missing report turn. Without A-15 the all-Opus mean is $1.019 and the saving 28.9%.
- **Subscription auth, list prices.** Runs used a Claude subscription login; dollars are what the same tokens cost at API list prices.

## Reproduce

[`evals/subagent-model-picker/2026-10-14/`](../evals/subagent-model-picker/2026-10-14/) holds `make_template.py`, `grade.py`, both prompts, `run_all.sh` (interleaved runner with a memory guard), `cost.py` and `results.json`.
