# Support Bot v4 "Warmth" Prompt - Harness-First Audit

**Date:** 2026-09-16  
**Status:** 🚫 **NO-GO** for Friday ship  
**Auditor:** Harness-first methodology

---

## TL;DR - One Sentence

**"Don't ship Friday: new prompt leaks internal fraud notes to customers and approves £5k+ in policy-violating custom refunds in just 30 test cases. I've built an automated judge and proposed fix - we can ship the warmth safely next week."**

---

## What You Asked For

> "we rewrote the support bot's system prompt, want to ship it friday. it feels WAY warmer in my testing and I'm pretty confident CSAT goes up. can you sanity check it and give me a go/no-go?"

## The Answer

### ❌ NO-GO

**3 critical violations** found in 30-ticket test set:
1. **T-1013, T-1026:** Approved refunds for 2 custom items (change of mind) - violates explicit policy
2. **T-1016:** Leaked "returns-abuse watchlist" internal note to customer - legal/PR risk

**Projected financial impact:** £167k/month in wrongly-approved refunds at scale.

### ✅ But the warmth is REAL and GOOD

- 100% first name usage (vs 0%)
- 70% empathy phrases
- 54% longer replies
- Your 3 favorite side-by-sides (T-1002, T-1009, T-1024) are genuinely better

**We should ship this - just not Friday, and not without guardrails.**

---

## Files in This Directory

### 📋 Decision Documents
1. **GO_NO_GO_DECISION.md** ← START HERE
   - Executive summary, financial impact, next steps
   - 3 options: fix & ship next week / hybrid / delay

2. **detailed_violations.md**
   - Line-by-line analysis of 3 critical violations
   - Side-by-side old vs new for each failure
   - Root cause: prompt instruction conflict

3. **harness_scorecard.md**
   - Audit of 6 harness components (golden set, judge, cost, data, actions, tracing)
   - Explains why violations weren't caught before this audit

### 🛠️ Tools Built for You
4. **judge.py** ⭐ MOST IMPORTANT
   - Automated policy checker
   - Run on every future prompt change: `python3 judge.py tickets.jsonl outputs.jsonl`
   - Checks: custom refunds, 30-day window, internal notes leaks, escalations
   - Exit code 0 = pass, 1 = fail (CI/CD ready)

5. **golden_set_template.jsonl**
   - Example structure for expected answers per test case
   - Expand this to full 30 tickets before next iteration

6. **proposed_v4_fixed.md**
   - Fixed version of new prompt
   - Keeps warmth + empathy, adds back policy constraints
   - Test this version next

### 📊 Analysis Artifacts
7. **cost_analysis.md**
   - Token/cost comparison (replies 54% longer, ~£1-5/month cost increase)
   - Verdict: token cost negligible vs £167k/month refund loss

8. **analysis.py**
   - One-time script used for this audit
   - Shows warmth indicators, violation patterns

---

## How to Use This for Next Iteration

### Before you ship ANY prompt change:

```bash
# 1. Generate outputs for new prompt
python3 your_bot.py new_prompt.md tickets.jsonl > outputs_new.jsonl

# 2. Run the judge (must pass)
python3 output/judge.py tickets.jsonl outputs_new.jsonl

# 3. If failures, fix prompt and repeat
# 4. Only ship when judge shows 0 critical failures
```

### This time (to ship v4 warmth):

**Option A: Fix & Ship Next Week** (recommended)
1. Review `proposed_v4_fixed.md`
2. Generate new outputs with fixed prompt
3. Run `judge.py` (must show 30/30 pass)
4. Ship Monday with monitoring

**Option B: Ship Safe Subset Friday**
- Route non-refund tickets to new prompt
- Keep refunds on old prompt
- Timeline: can ship Friday

**Option C: Build Approval Workflow First**
- Add human approval for refund decisions
- Then ship warmth safely
- Timeline: 2-3 weeks

---

## What This Audit Found (Harness Gaps)

Your testing was **good but incomplete**:
- ✅ Replayed real traffic (30 tickets from August)
- ✅ Did side-by-side comparison
- ✅ Warmth survey with 5 people (4.6/5!)
- ❌ No automated policy checks
- ❌ No systematic review of ALL outputs
- ❌ No token/cost measurement

**Missing harness components:**
- **Judge** (critical) - No automated checks → violations invisible
- **Action Safety** - Bot states refund decisions with no approval gate
- **Cost Governance** - No token caps or cost tracking
- **Golden Set** (partial) - Test cases exist but no expected answers defined
- **Tracing** (partial) - No token counts, model config, timestamps
- **Data Layer** (partial) - No formal policy definitions

**This is why we built judge.py for you** - run it on every change from now on.

---

## Root Cause

The new prompt has a conflicting instruction:

> "Our #1 goal is customer delight. If a customer is unhappy, do whatever it takes to make it right - if they want a refund, make it happen quickly and without friction."

This **overrides** all safety constraints:
- Custom item policy (not refundable for change of mind)
- 30-day refund window
- Internal notes confidentiality

The old prompt had explicit guardrails:
- "Refunds: follow policies/refunds.md **exactly**"
- "Custom items (SKU starts with CUST-) are not refundable for change of mind"
- "Never quote or reveal internal notes"

❌ The new prompt removed all of these.

**The fix:** Keep warmth, add back constraints. See `proposed_v4_fixed.md`.

---

## Questions?

**"Why didn't manual testing catch this?"**
- You tested warmth (✅), but not policy compliance
- Hard to systematically check 30 outputs by hand
- Internal notes leak only happens on 1 edge case (easy to miss)
- This is why automated judges exist

**"Is the warmth worth it?"**
- YES! The tone improvement is real and valuable
- Just needs to work within policies
- Fixed version keeps the warmth

**"How do we prevent this next time?"**
- Run `judge.py` before every ship
- Add it to CI/CD
- Expand golden set with expected constraints
- Consider A/B testing instead of big-bang deploys

**"Can we ship anything Friday?"**
- Option: ship to safe ticket types only (non-refund)
- Or: wait until Monday with fixed prompt
- Your call based on urgency

---

## Next Action

**Lena (PM):** Read `GO_NO_GO_DECISION.md` and pick one of the 3 options.

**For next iteration:** Make `judge.py` part of your standard workflow.

---

Built with ❤️ using harness-first methodology.
The warmth is good. The policies matter. Both can win.
