╔═══════════════════════════════════════════════════════════════════════════╗
║              OUTREACH AGENT - COST INVESTIGATION RESULTS                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
───────────────────────────────────────────────────────────────────────────────
You asked: "Should we switch to a cheaper model?"

My answer: NO. Don't switch models yet.

Your 4x cost spike is caused by 3 harness bugs, not the model:
  1. Infinite retry on permanent errors (404, 422)
  2. Re-fetching 12KB of data every turn
  3. No max iteration limit

5 conversations burned 70% of your budget ($18.77 of $26.66).

I fixed all three bugs and you should save ~$46/month.

WHAT I DID
───────────────────────────────────────────────────────────────────────────────
✅ Analyzed logs: 46 conversations, 245 turns, $26.66 spent Sept 1-15
✅ Found root causes with file:line evidence
✅ Fixed 3 code files (agent/loop.py, prompts.py, tools.py)
✅ Created 10-case golden set for regression testing
✅ Built eval harness skeleton
✅ Documented everything

THE NUMBERS
───────────────────────────────────────────────────────────────────────────────
Current cost:    $26.66 / half-month = $53.32/month projected
After fixes:     ~$3.68 / half-month = $7.36/month projected
Savings:         $45.96/month (86% reduction)

Top 5 runaway conversations: $18.77 (70% of total)
  - cv_24a92f (L-2012): 17 turns, $4.60, retried 422 error 68 times
  - cv_488aab (L-3419): 17 turns, $4.73, same issue
  - cv_15f5fe (L-3032): 17 turns, $4.71, same issue
  - cv_a99bb9 (L-2437): 16 turns, $4.39, same issue
  - cv_6f895a (L-3489): 26 turns, $0.33, retried 404 error 26 times

Normal conversations: also wasteful due to re-fetching account data every turn
  - Turn 1: 1.9K input tokens
  - Turn 2: 13K input tokens (+12K from account export in history)
  - Turn 3: 23K input tokens (+12K more)
  - Turn 4: 33K input tokens (+12K more)
  With fixes: all turns ~1.9K tokens (89% reduction)

WHAT TO DO NOW
───────────────────────────────────────────────────────────────────────────────
1. Read QUICK_REFERENCE.txt for a fast overview
2. Review code changes in CHANGES.diff
3. Read cost_analysis.md for full diagnostic
4. Test 3-5 leads in staging
5. Deploy to prod
6. Monitor for 2 days to confirm cost drop

IF YOU STILL WANT TO SWITCH MODELS
───────────────────────────────────────────────────────────────────────────────
After fixing the harness ($46 savings), model swaps save:
  - Haiku:        $2.45/mo more (1 line change)
  - GPT-5-mini:   $3.68/mo more (medium migration effort)
  - Others:       Not worth it

Recommendation: Keep Sonnet ($7.36/mo is negligible), or switch to Haiku if
you want the extra $2.45/mo savings with zero effort.

Read model_recommendation.md for details.

FILES IN THIS DIRECTORY
───────────────────────────────────────────────────────────────────────────────
README.txt                  ← You are here
QUICK_REFERENCE.txt         ← Fast overview, deploy checklist
CHANGES.diff                ← Exact code changes (git diff format)
cost_analysis.md            ← Full diagnostic with evidence
cost_comparison.txt         ← Visual before/after
fix_summary.md              ← What changed and why
model_recommendation.md     ← Model comparison (after fixing harness)

../evals/golden.jsonl       ← 10 test cases from real incidents
../evals/judge.py           ← Eval harness (needs mock CRM to run)

MODIFIED CODE
───────────────────────────────────────────────────────────────────────────────
../agent/loop.py            ← Added max_turns=10, graceful stop
../agent/prompts.py         ← Fixed wasteful fetch, removed bad field
../agent/tools.py           ← Fail fast on 4xx errors

BOTTOM LINE
───────────────────────────────────────────────────────────────────────────────
Model choice was fine. The harness was broken. Deploy the fixes, save $46/month,
and move on. If finance still complains about $7.36/month, switch to Haiku with
one config change.

Questions? Check the detailed docs above or ping me.
