# outreach-agent changelog

## 2026-09-03 (prompt v7)
- Scoring v2: hot leads (>=80) now write `lead_score_v2` so RevOps can compare old vs new scoring. (Dana)
- Agent refreshes the account export every turn; reps were editing accounts mid-batch and the agent used stale notes.
- Agent must not finish until the CRM write succeeds (we had leads with emails sent but no score).

## 2026-08-19 (prompt v6)
- First-touch email capped at 120 words.
- Added `with_retries` around CRM calls, the CRM was flaking with 503s.

## 2026-08-04 (prompt v5)
- Moved from Zapier flow to this agent. Nightly batch on the worker box.
