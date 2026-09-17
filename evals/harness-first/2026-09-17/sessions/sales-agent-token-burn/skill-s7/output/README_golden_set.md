# Golden Set Starter Kit

## Purpose
Before switching models or changing prompts, you need a way to verify the agent still works correctly.

## What's Here

### golden_set_starter.jsonl
- 4 example evaluation cases drawn from actual Sept 1-15 logs
- Includes both normal cases and the problematic retry-loop cases
- Format: one JSON object per line with expected outcomes

### How to Expand This

Add 16-26 more cases covering:

1. **Edge cases from logs:**
   - Different studio sizes (hobbyist, mid-size, industrial)
   - Various activity levels (inactive, recent, very active)
   - Different kiln counts (0, 1, 3, 8+)
   
2. **Policy requirements:**
   - What score threshold really matters for follow-up?
   - Are there industries/regions to exclude?
   - Any content guidelines for emails?

3. **Known incidents:**
   - The merged account case (L-3489)
   - The lead_score_v2 validation failures
   - Any leads where reps complained about the email

### Next Steps

1. **Collect real examples:** Export 20-30 leads from CRM with diversity in:
   - Studio size, kiln count, activity, geography
   - Mix of converted/not converted leads (if known)

2. **Define expected outcomes:** For each:
   - Expected score range (not exact - models vary)
   - Should email be sent? (yes/no)
   - Any specific content requirements for email?
   
3. **Get human labels:** Have your SDR team or subject matter expert:
   - Score 5-10 leads manually to calibrate expectations
   - Review agent-generated emails for tone/quality issues

4. **Build the judge script:** See judge_template.py for starter code
   - Check score in expected range
   - Check email sent/not sent correctly
   - Check email quality (length, tone, formatting)
   - Optionally: LLM-as-judge for email quality

5. **Baseline current model:** Run golden set on Sonnet, record results

6. **Then test changes:** Any prompt/model/tool change should be run against golden set first
