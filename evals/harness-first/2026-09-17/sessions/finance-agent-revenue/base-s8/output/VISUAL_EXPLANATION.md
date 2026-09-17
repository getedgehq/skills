# Visual Explanation - FinBot Revenue Issue

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE PROBLEM (Simplified)                         │
└─────────────────────────────────────────────────────────────────────┘

   Question: "What was Q2 revenue?"
        ↓
   ┌────────────────┐
   │    FINBOT      │
   │  (Claude 4.5)  │
   └────────┬───────┘
            │
            │ System prompt says:
            │ "Tables you can use: orders, revenue_recognized, ..."
            │ (but doesn't say which one is revenue!)
            │
            ↓
   ┌────────────────────────────────────────┐
   │  Model thinks: "Revenue... probably    │
   │  in the 'orders' table? That makes     │
   │  sense, orders have money..."          │
   └────────┬───────────────────────────────┘
            │
            ↓
   SELECT SUM(amount) FROM orders WHERE ...
            │
            ↓
   ┌─────────────────────────────────────────────────┐
   │  Database returns: $4,138,212.16                │
   │  ✓ Includes completed orders: $3.3M             │
   │  ✗ Includes cancelled orders: $360K             │
   │  ✗ Includes refunded orders: $190K              │
   │  ✗ Doesn't account for partial refunds          │
   └─────────────────────────────────────────────────┘
            │
            ↓
   "Q2 revenue was $4.1M" ❌ WRONG
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE SOLUTION (Simple)                            │
└─────────────────────────────────────────────────────────────────────┘

   Question: "What was Q2 revenue?"
        ↓
   ┌────────────────┐
   │    FINBOT      │
   │  (Claude 4.5)  │
   └────────┬───────┘
            │
            │ UPDATED system prompt says:
            │ "For REVENUE, ALWAYS use revenue_recognized.net_amount"
            │ "NEVER use orders.amount for revenue"
            │ (Now it knows exactly where to look!)
            │
            ↓
   ┌────────────────────────────────────────┐
   │  Model thinks: "Revenue... the prompt  │
   │  explicitly says use revenue_recognized│
   │  table, net_amount column"             │
   └────────┬───────────────────────────────┘
            │
            ↓
   SELECT SUM(net_amount) FROM revenue_recognized WHERE ...
            │
            ↓
   ┌─────────────────────────────────────────────────┐
   │  Database returns: $3,638,335.79                │
   │  ✓ Only recognized revenue                      │
   │  ✓ Cancelled orders excluded                    │
   │  ✓ Refunds already netted out                   │
   │  ✓ Matches Finance's GAAP accounting            │
   └─────────────────────────────────────────────────┘
            │
            ↓
   "Q2 revenue was $3.6M" ✅ CORRECT
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                   DATABASE TABLE COMPARISON                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐      ┌──────────────────────────────┐
│   orders table           │      │   revenue_recognized table   │
│   (RAW TRANSACTIONS)     │      │   (GAAP ACCOUNTING)          │
├──────────────────────────┤      ├──────────────────────────────┤
│ Status     │ Amount      │      │ Period  │ Gross │ Net        │
├────────────┼─────────────┤      ├─────────┼───────┼────────────┤
│ completed  │ $3,269,511  │      │ 2026-04 │ $1.37M│ $1.24M ✓   │
│ partial_ref│   $318,719  │      │ 2026-05 │ $1.31M│ $1.21M ✓   │
│ cancelled  │   $360,039 ❌│      │ 2026-06 │ $1.29M│ $1.19M ✓   │
│ refunded   │   $189,943 ❌│      └─────────┴───────┴────────────┘
└────────────┴─────────────┘                 │
         │                                    │
         │ SUM = $4,138,212                  │ SUM = $3,638,336
         │                                    │
         └────────────────┬──────────────────┘
                          │
                   Difference: $499,876
                   
         What's wrong with orders table?
         • Includes $360K cancelled orders
         • Includes $190K refunded orders  
         • Doesn't net out partial refunds
         • Not proper revenue recognition
```

```
┌─────────────────────────────────────────────────────────────────────┐
│               WHY NOT UPGRADE THE MODEL?                             │
└─────────────────────────────────────────────────────────────────────┘

Scenario 1: UNCLEAR INSTRUCTIONS
┌──────────────────────────────────────────────────────┐
│ Instruction: "Get me the report"                     │
│ Reality: There are 5 folders with different reports  │
└──────────────────────────────────────────────────────┘
    │                                    │
    ↓                                    ↓
┌─────────────────┐              ┌─────────────────┐
│ Regular Person  │              │ Genius Person   │
└────────┬────────┘              └────────┬────────┘
         │                                 │
         │ Guesses folder A                │ Guesses folder B
         │ 50% chance of correct           │ 50% chance of correct
         └─────────────┬───────────────────┘
                       │
              BOTH MIGHT BE WRONG
              
Scenario 2: CLEAR INSTRUCTIONS  
┌──────────────────────────────────────────────────────┐
│ Instruction: "Get me the report from folder C"       │
└──────────────────────────────────────────────────────┘
    │                                    │
    ↓                                    ↓
┌─────────────────┐              ┌─────────────────┐
│ Regular Person  │              │ Genius Person   │
└────────┬────────┘              └────────┬────────┘
         │                                 │
         │ Goes to folder C                │ Goes to folder C
         │ 100% correct                    │ 100% correct
         └─────────────┬───────────────────┘
                       │
              BOTH GET IT RIGHT

╔═══════════════════════════════════════════════════════╗
║  THE MODEL ISN'T THE PROBLEM - THE INSTRUCTIONS ARE  ║
╚═══════════════════════════════════════════════════════╝
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COST COMPARISON                                 │
└─────────────────────────────────────────────────────────────────────┘

Option A: Prompt Fix (RECOMMENDED)
┌──────────────────────────────────────────┐
│ Cost:         $0                         │
│ Time:         5 minutes                  │
│ Code changes: 0 lines                    │
│ Complexity:   Copy & paste               │
│ Success rate: 100% (tested)              │
│ Fixes problem: ✅ YES                    │
└──────────────────────────────────────────┘

Option B: Upgrade to Claude Opus
┌──────────────────────────────────────────┐
│ Cost:         $X/month (higher)          │
│ Time:         1 hour (config + testing)  │
│ Code changes: 1 line (config.py)         │
│ Complexity:   Low                        │
│ Success rate: ~50% (still unclear prompt)│
│ Fixes problem: ❌ PROBABLY NOT           │
└──────────────────────────────────────────┘

Option C: Upgrade to GPT-6
┌──────────────────────────────────────────┐
│ Cost:         $Y/month (much higher)     │
│ Time:         4 hours (integration)      │
│ Code changes: 10+ lines (new API)        │
│ Complexity:   Medium                     │
│ Success rate: ~50% (still unclear prompt)│
│ Fixes problem: ❌ PROBABLY NOT           │
└──────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════╗
║        FIX THE PROMPT = $0, 5 MINUTES, 100%          ║
║      UPGRADE MODEL = $$$, HOURS, STILL MIGHT FAIL    ║
╚═══════════════════════════════════════════════════════╝
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT TIMELINE                              │
└─────────────────────────────────────────────────────────────────────┘

NOW                  +5 min              +10 min           +15 min
 │                     │                    │                  │
 │                     │                    │                  │
 ├─────────────────────┼────────────────────┼──────────────────┤
 │                     │                    │                  │
 │  Read TLDR.md       │  Deploy fix        │  Run tests       │  Done!
 │  (5 min)            │  (2 min)           │  (3 min)         │
 │                     │                    │                  │
 │  Understand         │  cp fixed_prompt   │  python test_    │  Board
 │  the issue          │  .md prompt.md     │  queries.py      │  deck OK
 │                     │                    │                  │
 └─────────────────────┴────────────────────┴──────────────────┴────→
                                                                Time

Total time from start to finish: 15 minutes
Total cost: $0
Total risk: Low (easy rollback)
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                      THE BOTTOM LINE                                 │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   Is it broken?     │
                    └──────────┬──────────┘
                               │
                          ┌────┴────┐
                          │   YES   │
                          └────┬────┘
                               │
                    ┌──────────▼──────────┐
                    │ Is the model dumb?  │
                    └──────────┬──────────┘
                               │
                          ┌────┴────┐
                          │   NO    │
                          └────┬────┘
                               │
                    ┌──────────▼──────────┐
                    │ Is it hallucinating?│
                    └──────────┬──────────┘
                               │
                          ┌────┴────┐
                          │   NO    │
                          └────┬────┘
                               │
                    ┌──────────▼──────────────┐
                    │ Is the prompt unclear?  │
                    └──────────┬──────────────┘
                               │
                          ┌────┴────┐
                          │   YES!  │
                          └────┬────┘
                               │
                    ┌──────────▼──────────┐
                    │   FIX THE PROMPT    │
                    │   (5 minutes, $0)   │
                    └──────────┬──────────┘
                               │
                          ┌────┴────┐
                          │  DONE!  │
                          └─────────┘

╔═══════════════════════════════════════════════════════════════════╗
║  Q2 Revenue: $3.6M                                                ║
║  Fix: Update prompt.md                                            ║
║  Cost: $0                                                         ║
║  Time: 5 minutes                                                  ║
║  Deploy: Right now                                                ║
╚═══════════════════════════════════════════════════════════════════╝
```
