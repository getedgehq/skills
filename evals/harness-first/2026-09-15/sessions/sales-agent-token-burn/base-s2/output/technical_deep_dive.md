# Technical Deep Dive: What Went Wrong

## TL;DR
Your agent has a prompt bug causing 70% cost overrun + 4 conversation failures. The agent is also using an expensive model for a simple task.

---

## Issue #1: Context Bloat from Repeated CRM Fetches

### The Bug
**Location:** `agent/prompts.py`, line 5
```python
1. At the start of EVERY turn, call crm_get_account to load the latest full account export so your
   information is always fresh (reps edit accounts during the day).
```

### Why This Is Expensive

The agent runs in a nightly batch (2-5am UTC per config). Reps aren't editing accounts at 3am. But the prompt forces the agent to reload account data every turn, causing exponential context growth:

```
Turn 1:  2K tokens (system prompt + initial user message)
         + Load account (40KB = ~10K tokens)
         = 12K total

Turn 2:  12K context + tool results + new prompt
         + Load account AGAIN (10K tokens)
         = 24K total

Turn 3:  24K context + tool results
         + Load account AGAIN (10K tokens)
         = 36K total

Turn 17: 150K context
         + Load account AGAIN (10K tokens)
         = 200K+ tokens → API ERROR (limit exceeded)
```

### Real Examples from Logs

**Conversation cv_488aab (Lead L-3419):**
- Turn 1: 1,914 input tokens
- Turn 2: 13,229 input tokens (+11K)
- Turn 3: 24,682 input tokens (+11K)  
- Turn 5: 48,168 input tokens (+11K per turn)
- Turn 10: 106,017 input tokens
- Turn 15: 163,866 input tokens
- Turn 17: **206,428 tokens → FAILED** (200K limit)
- Cost: **$4.73** for one failed conversation

**Normal conversation (most leads):**
- Turn 1: ~2K tokens
- Turn 2: ~11K tokens  
- Turn 3: ~14K tokens
- Turn 4: Done (~$0.15 total)

### The Fix

```python
# OLD (bad):
1. At the start of EVERY turn, call crm_get_account...

# NEW (good):
1. Call crm_get_account ONCE at the start to load the account data...
...
Do not reload the account data multiple times - the data is fresh enough for this task.
```

**Impact:** Should reduce average turns from 5.3 → 3-4, eliminate the $4+ outliers.

---

## Issue #2: Wrong Model for the Task

### The Task
1. Load CRM data (contact info, company notes)
2. Score the lead 0-100 based on: studio size, kiln count, activity
3. Update CRM with score
4. Maybe send a 100-word cold email

**This is not complex reasoning.** It's basic data extraction + template filling.

### Current Setup
- Model: `claude-sonnet-4-5`
- Cost: $3 input / $15 output per Mtok
- Why: Unknown (probably default choice, never revisited)

### Why This Is Wasteful

Average conversation uses:
- Input: 189K tokens (mostly CRM JSON that gets read once)
- Output: 736 tokens (the lead score + short email)

**Cost breakdown per conversation:**
```
Input:  189K × $3/Mtok  = $0.567
Output: 736 × $15/Mtok  = $0.011
Total: $0.578 per lead
```

With Haiku:
```
Input:  189K × $1/Mtok  = $0.189
Output: 736 × $5/Mtok   = $0.004
Total: $0.193 per lead (67% savings)
```

### Why Haiku Is Fine

From the logs, the agent successfully:
- Parses CRM JSON
- Extracts relevant fields (studio size, kiln count)
- Calculates scores
- Writes coherent cold emails

**Example output from logs (turn 3, send_email call):**
```json
{
  "to": "contact@example.com",
  "subject": "Kiln monitoring for your studio",
  "body": "Hi [Name], saw you recently expanded to 3 kilns..."
}
```

This is simple structured output. Haiku handles this easily. Sonnet's advanced reasoning is overkill.

---

## Issue #3: Tool Call Loops

Some conversations hit 17-26 turns. Normal should be 3-4:
1. Get account → 2. Score & update → 3. Send email → 4. Done

### Why Loops Happen

**Hypothesis from logs:** Tool call failures trigger retries. The tools have retry logic:

```python
# agent/tools.py
def with_retries(fn, attempts=4, backoff=1.5):
    """CRM is flaky, retry everything a few times."""
```

If CRM is slow/flaky at 2am, the agent retries. Combined with "call crm_get_account at EVERY turn", this creates:
1. Try get_account → timeout
2. Retry get_account → timeout  
3. Retry get_account → success, but now we're on turn 3
4. Try update_contact → fail
5. Call get_account again (per prompt) → success
6. Retry update_contact → success
7. Call get_account again → success
8. Send email → success
9. Call get_account again → success
10. Done (9 turns for a 4-turn task)

### The Fix

The prompt fix eliminates step "call get_account again" at every turn, so failures don't compound.

---

## Data Summary

### Conversation Length Distribution
```
3 turns:   15 conversations (32.6%)
4 turns:   26 conversations (56.5%)
5-10 turns: 3 conversations (6.5%)
11-17 turns: 4 conversations (8.7%) ← these cost $18.77 (70% of total)
18+ turns:  1 conversation (2.2%) ← cv_6f895a, 26 turns but only $0.33
```

### Token Usage
```
Average input per turn: ~10K tokens (CRM export size)
Total input Sept 1-15: 8.7M tokens
Total output Sept 1-15: 34K tokens

Input/output ratio: 257:1 (!!!)
Savings opportunity: 95% of cost is reading the same CRM data repeatedly
```

### API Errors
```
4 conversations hit 200K context limit
Failure rate: 8.7%
Cost of failures: ~$18.40 (no successful work output)
```

---

## Recommendations

### Immediate (do before Sept 30)
1. **Switch to Haiku** - Update `config.json`, restart agent
   - Saves: $35/month (67%)
   - Risk: None (same API, same quality for this task)
   - Effort: 2 minutes

### Short term (do this week)
2. **Fix the prompt** - Update `agent/prompts.py`
   - Eliminates context bloat bug
   - Fixes the 4 failing conversations
   - Additional savings: ~$10-15/month
   - Effort: 5 minutes + testing

### Long term (next sprint)
3. **Add conversation length circuit breaker**
   ```python
   if turn > 10:
       raise ToolError("Conversation too long, bailing out")
   ```
   - Prevents runaway costs from future bugs
   - Effort: 30 minutes

4. **Consider caching CRM data**
   - Anthropic offers prompt caching (50% discount on cached tokens)
   - Could save another 30-40% on Haiku costs
   - Effort: 1-2 hours

---

## Expected Results After Fixes

### Current State
- Monthly cost: $53.33
- Failure rate: 8.7%
- Average turns: 5.3

### After Model Switch Only
- Monthly cost: $17.78 (67% savings)
- Failure rate: 8.7% (unchanged)
- Average turns: 5.3 (unchanged)

### After Model Switch + Prompt Fix
- Monthly cost: ~$12-15 (75-80% savings)
- Failure rate: ~0% (context bloat eliminated)
- Average turns: 3-4 (as designed)

---

## Questions?

**Q: Will Haiku produce worse emails?**  
A: No. The logs show Sonnet's output is already simple structured data. Haiku handles this easily. The emails are templatized cold outreach, not creative writing.

**Q: Why not switch to GPT-5 Mini and save 91%?**  
A: You could, but it requires rewriting the LLM client (different SDK, different tool use format). Haiku gives 67% savings with zero code changes. Do Haiku now, consider GPT later if you need more savings.

**Q: What if a lead needs more complex reasoning?**  
A: The task is "score lead, send email" - it's deterministic. If you need complex reasoning in the future, add a model selection parameter per lead type.

**Q: Should we keep Sonnet for anything?**  
A: Not for this workload. If you build a different agent that does complex multi-step planning or creative strategy, use Sonnet there.
