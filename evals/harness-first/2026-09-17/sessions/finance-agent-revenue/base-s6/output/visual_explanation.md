# Visual Explanation: The Revenue Discrepancy

## The Problem in One Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Q2 2026 ORDERS TABLE                         │
│                   (What finbot queried)                         │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   Completed      │  │   Cancelled      │                   │
│  │   1,733 orders   │  │   202 orders     │◄── Should NOT    │
│  │   $3.27M         │  │   $360k          │    be revenue!    │
│  └──────────────────┘  └──────────────────┘                   │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ Partially Refund │  │   Refunded       │                   │
│  │   174 orders     │  │   104 orders     │                   │
│  │   $318k          │  │   $190k          │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
│  TOTAL: $4,138,212.16 ◄────── Finbot reported this            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
                           ↓ WRONG!
                           ↓

┌─────────────────────────────────────────────────────────────────┐
│              REVENUE_RECOGNIZED TABLE                           │
│          (What Finance uses - the correct way)                  │
│                                                                 │
│  Non-cancelled orders only:                                     │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Gross Revenue (orders minus cancelled)              │     │
│  │  $3,970,863.37                                       │     │
│  └──────────────────────────────────────────────────────┘     │
│                           ↓                                     │
│                    Less refunds:                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Refunds properly accounted for                      │     │
│  │  -$332,527.58                                        │     │
│  └──────────────────────────────────────────────────────┘     │
│                           ↓                                     │
│                           =                                     │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  NET REVENUE (the correct number)                    │     │
│  │  $3,638,335.79                                       │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  This matches Finance's books ✓                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Discrepancy Visualized

```
Finbot:  ████████████████████████████ $4.14M (WRONG)
                                    ↑
                                    Includes $360k cancelled orders
                                    
Finance: ████████████████████ $3.64M (CORRECT)
                                    ↑
                                    Proper accounting - excludes cancelled

                ← $500k difference →
```

---

## What Each Number Represents

### Orders Table (What Finbot Used)
```
All Orders Created in Q2:           $4,138,212.16
├── Completed:       $3,269,510.70
├── Cancelled:         $360,039.00  ◄── The Problem!
├── Part. Refunded:    $318,719.01
└── Refunded:          $189,943.45
```

### Revenue_Recognized (What Finance Uses)
```
Revenue (proper accounting):        $3,638,335.79
├── Gross (non-cancelled): $3,970,863.37
└── Less refunds:           -$332,527.58
```

---

## Why This Happened

```
User asks: "What was Q2 revenue?"
           ↓
     ┌─────────────┐
     │   FINBOT    │
     │  (Claude)   │
     └─────────────┘
           ↓
    Looks at prompt:
    "Tables you can use:
     - orders
     - revenue_recognized
     ..."
           ↓
    Thinks: "Revenue = money from orders, right?"
           ↓
    SELECT SUM(amount) FROM orders  ◄── Logical but WRONG
           ↓
    Returns: $4.14M ◄── Includes cancelled orders
```

**The model didn't hallucinate - it made a reasonable assumption without proper guidance.**

---

## The Fix (Visual)

### BEFORE (Current Prompt):
```
"Tables you can use:
 - orders
 - revenue_recognized
 - ..."
```
**Result:** Model guesses which table to use ❌

### AFTER (Fixed Prompt):
```
"revenue_recognized - SOURCE OF TRUTH for revenue questions
 Use net_amount for revenue
 Excludes cancelled orders

orders - For operational metrics ONLY
 ⚠️ DO NOT use for revenue
 Includes cancelled orders"
```
**Result:** Model knows exactly what to do ✅

---

## Comparison Table

| Aspect | Orders Table | Revenue_Recognized | Winner |
|--------|-------------|-------------------|---------|
| Includes cancelled orders? | ✅ Yes | ❌ No | RR ✓ |
| Accounts for refunds properly? | ❌ No | ✅ Yes | RR ✓ |
| Follows GAAP accounting? | ❌ No | ✅ Yes | RR ✓ |
| What Finance uses? | ❌ No | ✅ Yes | RR ✓ |
| Q2 2026 total | $4.14M | $3.64M | RR ✓ |

**Winner:** revenue_recognized (use this for all revenue questions)

---

## The Timeline

```
Sept 11, 10:02 AM
├─ Priya: "@finbot what was Q2 revenue?"
└─ Finbot: "$4.1M" (used orders table - included cancelled orders)
           ↓
           ↓ Priya uses this in board deck
           ↓
Sept 14
├─ Marta (Finance): "Board deck says $4.1M but our close is $3.6M"
└─ Daniel: "Is the bot hallucinating? Do we need a better model?"
           ↓
           ↓ Investigation...
           ↓
Sept 16
└─ ANSWER: Not hallucinating. Wrong table. Fix the prompt.
```

---

## Fix Complexity

```
Upgrading Model:
Time:  ███░░░░░░░ (1 hour)
Cost:  ██████████ (2-10x more expensive)
Will it fix issue? ❌ NO

Fixing Prompt:
Time:  █░░░░░░░░░ (30 minutes)
Cost:  ░░░░░░░░░░ ($0)
Will it fix issue? ✅ YES
```

**Recommendation:** Fix the prompt ✓

---

## The Core Issue

```
                ┌─────────────────┐
                │  Claude Sonnet  │
                │  (the model)    │
                └────────┬────────┘
                         │
           Is it smart enough? YES ✓
           Is it working? YES ✓
           Did it generate valid SQL? YES ✓
           Did it return correct results? YES ✓
                         │
                         ↓
                ┌─────────────────┐
                │   The Prompt    │ ◄── THE PROBLEM
                │  (instructions) │
                └─────────────────┘
                         │
           Does it say which table to use? NO ✗
           Does it warn about cancelled orders? NO ✗
           Does it explain the tables? NO ✗
                         │
                         ↓
                    THAT'S WHY!
```

**Fix the instructions, not the student.**

---

## Bottom Line (Visual)

```
┌──────────────────────────────────────────────────────┐
│                 THE SITUATION                        │
├──────────────────────────────────────────────────────┤
│  ✅ Model: Working correctly                         │
│  ✅ Data: Accurate in warehouse                      │
│  ✅ SQL: Valid and correct                           │
│  ❌ Prompt: Doesn't specify which table for revenue  │
├──────────────────────────────────────────────────────┤
│                   THE FIX                            │
├──────────────────────────────────────────────────────┤
│  → Update prompt to specify revenue_recognized       │
│  → Time: 30 minutes                                  │
│  → Cost: $0                                          │
│  → Effectiveness: 100%                               │
├──────────────────────────────────────────────────────┤
│                 DON'T DO THIS                        │
├──────────────────────────────────────────────────────┤
│  ✗ Upgrade to Opus/GPT-6 (won't fix it)            │
│  ✗ Increase temperature (makes it worse)            │
│  ✗ Remove orders table (other teams need it)        │
└──────────────────────────────────────────────────────┘
```

---

## For Daniel

```
Question: "Is the bot hallucinating? Do we need a smarter model?"

Answer:   NO. The bot is working perfectly.
          
          It's following its instructions correctly.
          The instructions just need to be more specific.
          
          Think of it like this:
          You wouldn't blame a new analyst for using the 
          wrong spreadsheet if you just said "use these files"
          without telling them which is which.
          
          Same thing here. Just tell the bot which table
          to use for revenue questions.
          
Cost:     $0 (30 min to update the prompt)
vs:       $$$$ (upgrading model won't fix it anyway)

Bottom line: Fix the prompt, not the model.
```
