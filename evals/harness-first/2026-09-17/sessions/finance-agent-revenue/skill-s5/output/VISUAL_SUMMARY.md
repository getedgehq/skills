# FinBot Q2 Revenue - Visual Summary

## The Problem

```
┌─────────────────────────────────────────────────────────────┐
│  Priya: "What was Q2 2026 revenue?"                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  FinBot's Reasoning:                                         │
│  "Revenue... probably the orders table's amount column"      │
│                                                              │
│  Query: SELECT SUM(amount) FROM orders WHERE Q2              │
│  Result: $4,138,212                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Board Pre-Read: "Q2 revenue: $4.1M"  ✓ (sent)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Marta (Finance): "Our close is $3.6M!"  ❌ (500K off)       │
└─────────────────────────────────────────────────────────────┘
```

---

## The Root Cause

```
Warehouse has TWO "revenue" sources:

┌─────────────────────────┐         ┌─────────────────────────┐
│   orders table          │         │ revenue_recognized      │
│                         │         │                         │
│  • All order amounts    │         │  • GAAP net revenue     │
│  • Includes cancelled   │         │  • Gross minus refunds  │
│  • Before refunds       │         │  • Official number      │
│                         │         │                         │
│  Q2 = $4,138,212        │         │  Q2 = $3,638,336        │
└─────────────────────────┘         └─────────────────────────┘
         ▲                                    ▲
         │                                    │
         │ FinBot chose this                  │ Finance uses this
         │ (reasonable guess)                 │ (source of truth)
         │                                    │
    Difference: $499,876 (12% error)
```

**Why the difference:**
- Cancelled orders: +$360,039
- Refund adjustments: +$139,837
- **Total difference: $499,876**

---

## The Data Flow

```
orders table breakdown (Q2 2026):
┌─────────────────────────────────────┐
│  Completed:         $3,269,511      │
│  Partially refunded:  $318,719      │
│  Refunded:            $189,943      │
│  Cancelled:           $360,039  ⚠️  │ ← FinBot counted this
│  ─────────────────────────────────  │
│  TOTAL:            $4,138,212       │
└─────────────────────────────────────┘
                │
                │ Finance's process:
                │ - Remove cancelled
                │ - Net out refunds
                │ - Apply GAAP recognition rules
                ▼
┌─────────────────────────────────────┐
│  revenue_recognized (Q2 2026):      │
│                                     │
│  Gross amount:      $3,970,863      │
│  Refund amount:      -$332,527      │
│  ─────────────────────────────────  │
│  NET REVENUE:      $3,638,336       │ ← Finance's close
└─────────────────────────────────────┘
```

---

## The Missing Harness

```
What FinBot had:                What FinBot needed:
┌─────────────────────┐         ┌─────────────────────┐
│  ❌ No golden set    │         │  ✓ 6 test cases     │
│  ❌ No judge         │         │  ✓ Eval script      │
│  ⚠️ Partial cost cap │         │  ✓ Max iterations   │
│  ❌ No data dict     │         │  ✓ Metric defs      │
│  ⚠️ Write access     │         │  ✓ Read-only DB     │
│  ❌ No tracing       │         │  ✓ Structured logs  │
└─────────────────────┘         └─────────────────────┘
   Harness Score: 6/60              Target: 50+/60
```

---

## The Fix

### Before (ambiguous prompt):
```
Tables you can use:
- orders
- revenue_recognized
- daily_kpis
```
➜ Model guesses which table to use ❌

### After (clear data dictionary):
```
Revenue:
- Definition: GAAP net revenue (gross minus refunds)
- Source: revenue_recognized.net_amount
- Do NOT use: orders.amount (includes cancelled, no refunds)

Tables:
- revenue_recognized: official revenue (use for reporting)
  - net_amount: gross minus refunds
  - recognized_on: recognition date
  
- orders: raw transactions (use for order counts, status)
  - amount: order value (before refunds)
  - status: completed | cancelled | refunded
```
➜ Model has clear guidance ✓

---

## Impact Timeline

```
March 2026         Sep 11            Sep 14           Sep 16
    │                │                 │                │
    ▼                ▼                 ▼                ▼
┌────────┐      ┌─────────┐      ┌─────────┐     ┌──────────┐
│ FinBot │      │ Board   │      │ Finance │     │ Fix      │
│ goes   │ ---> │ deck    │ ---> │ flags   │ --> │ deployed │
│ live   │      │ wrong # │      │ error   │     │          │
└────────┘      └─────────┘      └─────────┘     └──────────┘
  (no tests)    ($4.1M sent)     ($3.6M actual)  (+ harness)
```

**Months in prod without test coverage:** 6 months  
**Questions answered:** ~hundreds (estimated)  
**Other errors:** Unknown (need to audit Slack history)

---

## Model Upgrade Decision Tree

```
                Should we upgrade the model?
                          │
                          ▼
            Does the golden set show quality issues?
                    ╱           ╲
                  ╱               ╲
               NO                  YES
              ╱                       ╲
             ▼                         ▼
    Don't upgrade yet         Benchmark models
    (current model is         (run golden set on
     working correctly)        both, compare scores)
             │                         │
             │                         ▼
             │                Cost vs. quality
             │                tradeoff analysis
             │                         │
             ▼                         ▼
    Keep current model        Decide with evidence
    + harness fixes           (not vibes)
```

**Current situation:** NO quality issues detected (model executed correctly)  
**Recommendation:** Don't upgrade yet

---

## Cost Impact

```
Option A: Upgrade Model (e.g., Sonnet → Opus)
┌───────────────────────────────────────┐
│  Cost: ~2-3x per query                │
│  Time: 1 day to test + deploy         │
│  Fixes this bug: NO ❌                 │
│  Monthly cost increase: $X,XXX        │
└───────────────────────────────────────┘

Option B: Fix Harness
┌───────────────────────────────────────┐
│  Cost: $0                             │
│  Time: 3 hours eng work               │
│  Fixes this bug: YES ✓                │
│  Prevents similar bugs: YES ✓         │
│  Monthly cost increase: $0            │
└───────────────────────────────────────┘

Recommendation: Option B
```

---

## Deployment Checklist

```
Priority 1: Safety (15 min)
  [ ] Deploy agent.py (read-only DB, max iterations)
  
Priority 2: Fix Bug (30 min)
  [ ] Deploy prompt.md (data dictionary)
  [ ] Copy evals/ directory
  
Priority 3: Validation (15 min)
  [ ] Run eval script: python evals/run_evals.py
  [ ] Verify Q2 revenue test passes (expect $3.6M)
  
Priority 4: Monitoring (ongoing)
  [ ] Audit Slack history since March
  [ ] Add structured logging
  [ ] Set up cost/error dashboards
```

---

## Success Metrics

**Before fix:**
- Golden set: 0 test cases
- Test coverage: 0%
- Harness score: 6/60 (10%)
- Known wrong answers: 1+ (this incident)

**After fix:**
- Golden set: 6 test cases → expand to 20+
- Test coverage: Key metrics covered
- Harness score: 40+/60 (67%+)
- Regression prevention: ✓ (tests will catch)

**Long-term target:**
- 50+ test cases
- 90%+ test pass rate
- <1% error rate in production
- Full observability (logs, dashboards)
