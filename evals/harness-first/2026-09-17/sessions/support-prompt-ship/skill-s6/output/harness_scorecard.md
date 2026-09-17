# HARNESS SCORECARD: Support Bot v4

## Six Critical Harness Components

| Component | Status | Evidence |
|-----------|--------|----------|
| **Golden Set** | 🟡 PARTIAL | 30 real August tickets replayed through both prompts. Good start, but needs expected answers/constraints defined per case, not just eyeball comparison. Should include explicit pass/fail criteria. |
| **Judge** | 🔴 MISSING | No automated checking. PM did manual review + 5-person warmth survey. **CRITICAL**: No automated policy checks for custom items, 30-day window, internal notes leaks. These violations were not caught before this audit. |
| **Cost Governance** | 🔴 UNKNOWN | No evidence of token caps, max iterations, or cost limits. Can't assess if new longer/warmer replies increase cost per ticket. |
| **Data Layer** | 🟡 PARTIAL | tickets.jsonl structure exists with order data, internal notes field. No data dictionary defining business rules (e.g., "refund window = delivered_on + 30 days"). Policies mentioned but not linked/provided. |
| **Action Safety** | 🔴 MISSING | Bot appears to state refund decisions ("I've arranged a full refund") but no evidence of approval workflow, draft mode, or human-in-loop for refunds. **CRITICAL** for custom items. |
| **Tracing** | 🟡 PARTIAL | outputs_{old,new}.jsonl show replies per ticket. Missing: model config (temp, model name), token counts, timestamp, whether bot can actually execute refunds or just drafts replies. |

## Overall Harness Maturity: 🔴 **INSUFFICIENT FOR PRODUCTION**

**Blockers identified:**
1. No automated policy violation detection
2. No approval workflow for financial decisions (refunds)
3. No cost/safety guardrails in prompt evaluation process

