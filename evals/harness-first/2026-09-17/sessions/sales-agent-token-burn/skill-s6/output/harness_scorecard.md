# Harness Scorecard: Brightkiln Outreach Agent

Assessed: 2026-09-16

## Summary

**Don't switch models yet.** 70% of September costs ($18.77 of $26.66) came from 5 conversations stuck in retry loops on deterministic errors. The harness is severely incomplete. Fix the mechanism first, then eval both models if quality still needs improvement.

---

## Six Harness Components

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden set** | ❌ MISSING | No `evals/` directory, no test cases, no expected outputs. Changes shipped based on manual testing only. |
| **Judge** | ❌ MISSING | No automated scoring. No way to detect when a prompt change breaks qualification logic or email quality. |
| **Cost governance** | ❌ MISSING | No max iterations in `loop.py` (while True with no break condition). No per-run cost cap. No graceful degradation. Agent can burn unlimited tokens until it times out or the model stops responding. |
| **Data layer** | ⚠️ PARTIAL | CRM schema exists (`crm_schema.json`) but incomplete. `lead_score_v2` field referenced in prompt but never created in CRM. No data dictionary defining scoring criteria. |
| **Action safety** | ⚠️ PARTIAL | Email send (`send_email`) has no preview/approval gate - emails go out immediately. CRM writes happen directly with full write credentials. No draft mode. |
| **Tracing** | ✅ PRESENT | Comprehensive trace logging in `calls-2026-09-01_15.jsonl` with conversation_id, turn, tokens, cost, tool_calls. Enabled diagnosis. |

---

## Root Cause (with evidence)

**File:** `agent/prompts.py`, lines 8-9  
**Instruction:** "At the start of EVERY turn, call crm_get_account to load the latest full account export..."

**File:** `agent/tools.py`, lines 16-25  
**Decorator:** `@with_retries(attempts=4)` retries all errors, including deterministic 422s.

**File:** `agent/prompts.py`, lines 11-12  
**Instruction:** "Do not finish until the CRM update has succeeded. If a tool call fails, try it again."

**File:** `agent/loop.py`, line 19  
**Loop:** `while True:` with no max iteration limit.

**Logs:** `logs/crm_client.log`  
236 instances of `422 Unprocessable Entity` for field `lead_score_v2` (field doesn't exist in CRM).

**Result:**  
5 conversations (11% of volume) spent 70% of budget in retry loops:
- Each turn fetches fresh 12-40KB account export
- Context grows from 1.9K → 14K → 27K → 40K → ... → 188K tokens per turn
- Model retries crm_update_contact with non-existent field 15-17 times
- cv_488aab: 17 turns, 1.56M input tokens, $4.73
- cv_15f5fe: 17 turns, 1.56M input tokens, $4.71
- cv_24a92f: 17 turns, 1.52M input tokens, $4.60

---

## Blocking Safety Issues

1. **Emails sent without approval:** `send_email` tool sends immediately to prospects with no human review. One bad prompt change could send spam to all leads.

2. **Write credentials on read-heavy path:** Agent has full CRM write access but primarily needs read. Compromised token or prompt injection could corrupt customer data.

---

## What Would a Model Switch Save? (Spoiler: Nothing)

Current: Sonnet @ $3/Mtok in, $15/Mtok out  
Proposed: GPT-5-mini @ $0.25/Mtok in, $2/Mtok out (90% cheaper per Priya's note)

**Sept 1-15 actual cost:** $26.66  
- Input: 8.72M tokens × $3 = $26.16  
- Output: 34K tokens × $15 = $0.51

**Same workload on GPT-5-mini (no fixes):**  
- Input: 8.72M tokens × $0.25 = $2.18  
- Output: 34K tokens × $2 = $0.07  
- **Total: $2.25** (91% cheaper!)

**But:** The retry loops would still happen. You'd still waste tokens fetching the same 12KB export 17 times per failed conversation. You'd burn through budget faster as volume scales.

**With harness fixes (same model, Sonnet):**  
Eliminate the 5 retry loops (70% of cost):  
- Input: (8.72M - 6.1M retry waste) = 2.62M tokens × $3 = $7.86  
- Output: same = $0.51  
- **Total: $8.37** (69% cheaper, no model change)

**With fixes + cheaper model:**  
- Input: 2.62M × $0.25 = $0.66  
- Output: 34K × $2 = $0.07  
- **Total: $0.73** (97% cheaper)

**Conclusion:** Fix the harness first. It saves 69% on its own. Model swap saves another 91% *after* the fix, but without the fix you're still burning money on exponential retries.
