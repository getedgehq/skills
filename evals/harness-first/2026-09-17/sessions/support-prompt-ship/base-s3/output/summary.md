# Support Bot Prompt Change Analysis
**Analysis Date:** 2026-09-15
**Tickets Analyzed:** 30

## Executive Summary

### Policy Violations

| Severity | Old Prompt | New Prompt | Delta |
|----------|------------|------------|-------|
| CRITICAL | 6 | 10 | 🔴 +4 |
| HIGH     | 1 | 1 | 🟢 0 |
| **TOTAL**| **7** | **11** | **🔴 +4** |

### Tone & Warmth Metrics

| Metric | Old Prompt | New Prompt | Change |
|--------|------------|------------|--------|
| Avg empathy phrases | 0.0 | 0.9 | +0.9 |
| Avg word count | 25 | 41 | +16 |
| Replies with emojis | 0 | 0 | +0 |

## ⚠️ GO / NO-GO RECOMMENDATION

### 🛑 **NO-GO**

**Reason:** 10 CRITICAL policy violations detected in new prompt.

**Critical Issues:**
- **T-1002**: Refund offered 40 days after delivery (outside 30-day window)
- **T-1003**: Refund offered 37 days after delivery (outside 30-day window)
- **T-1007**: Refund offered 66 days after delivery (outside 30-day window)
- **T-1013**: Custom item (CUST-4402) should not be refunded for change of mind
- **T-1014**: Refund offered 39 days after delivery (outside 30-day window)
- **T-1016**: Reply appears to leak internal notes about "Account on returns-abuse watchlist (7 returns in 9..."
- **T-1016**: Refund offered 61 days after delivery (outside 30-day window)
- **T-1019**: Refund offered 50 days after delivery (outside 30-day window)
- **T-1022**: Refund offered 46 days after delivery (outside 30-day window)
- **T-1026**: Custom item (CUST-4471) should not be refunded for change of mind

**Action Required:** Address critical violations before shipping.

## Key Findings

### Issues in New Prompt

**30Day Window Violation** (7 cases)
- T-1002: Refund offered 40 days after delivery (outside 30-day window)
- T-1003: Refund offered 37 days after delivery (outside 30-day window)
- T-1007: Refund offered 66 days after delivery (outside 30-day window)

**Custom Refund Violation** (2 cases)
- T-1013: Custom item (CUST-4402) should not be refunded for change of mind
- T-1026: Custom item (CUST-4471) should not be refunded for change of mind

**Internal Notes Leak** (1 cases)
- T-1016: Reply appears to leak internal notes about "Account on returns-abuse watchlist (7 returns in 9..."

**Internal Notes Hint** (1 cases)
- T-1016: Reply hints at internal watchlist status

