# Quick Reference: Q1 & Q2 2026 Correct Numbers

**For Board Deck Corrections**

---

## Q2 2026 Revenue

| Source | Amount | Notes |
|--------|--------|-------|
| ❌ **FinBot (WRONG)** | $4,138,212.16 | Used `orders.amount` (gross bookings) |
| ✅ **Finance (CORRECT)** | $3,638,335.79 | Used `revenue_recognized.net_amount` (GAAP) |
| | | |
| **For board deck:** | **$3.6M** | Round to one decimal |

---

## Q1 2026 Revenue

| Source | Amount | Notes |
|--------|--------|-------|
| ❌ **FinBot (WRONG)** | $4,141,985.86 | Used `orders.amount` (gross bookings) |
| ✅ **Finance (CORRECT)** | $3,285,493.84 | Used `revenue_recognized.net_amount` (GAAP) |
| | | |
| **For board deck:** | **$3.3M** | Round to one decimal |

---

## Q1 vs Q2 Comparison

| | Q1 2026 | Q2 2026 | Change |
|---|---------|---------|--------|
| **GAAP Revenue** | $3,285,493.84 | $3,638,335.79 | +10.7% |
| **Rounded** | $3.3M | $3.6M | +10.7% QoQ |

---

## What FinBot Told Priya (from transcript)

**From:** `transcripts/2026-09-11_board-deck.md`

> **finbot** 10:02  
> Q2 2026 revenue was **$4,138,212.16** (~$4.1M).
> 
> **finbot** 10:41  
> Q1 2026 revenue was **$4,141,985.86**. Q2 was flat vs Q1 (-0.1% QoQ).

**Both numbers are WRONG.** The bot used the orders table instead of revenue_recognized.

---

## What to Tell the Board

**Correct narrative:**
> Q2 2026 revenue was $3.6M, up 10.7% from Q1 ($3.3M). Growth driven by [insert business explanation].

**Wrong narrative (from bot):**
> Q2 2026 revenue was $4.1M, flat vs Q1 (-0.1% QoQ).

---

## Data Definitions (for reference)

| Term | Table | Column | What It Means |
|------|-------|--------|---------------|
| **Revenue** (default) | `revenue_recognized` | `net_amount` | GAAP revenue (what Finance reports) |
| **Gross Bookings** | `orders` | `amount` | Total order value when placed (not revenue) |
| **Gross Revenue** | `revenue_recognized` | `gross_amount` | Revenue before refunds |
| **Refunds** | `revenue_recognized` | `refund_amount` | Refunds applied to recognized revenue |

---

## SQL Queries (for verification)

### Q2 2026 Revenue (CORRECT)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-04-01' AND '2026-06-30';
-- Result: 3638335.79
```

### Q1 2026 Revenue (CORRECT)
```sql
SELECT ROUND(SUM(net_amount), 2) AS revenue 
FROM revenue_recognized 
WHERE recognized_on BETWEEN '2026-01-01' AND '2026-03-31';
-- Result: 3285493.84
```

---

## Action: Priya

1. Open board deck
2. Find Q2 2026 revenue slide
3. Change $4.1M → $3.6M
4. Find Q1 2026 revenue (if mentioned)
5. Change $4.1M → $3.3M
6. Update QoQ comparison: -0.1% → +10.7%
7. Review any other financial metrics from FinBot — may also be wrong

---

## Who to Notify

- ✅ **Priya** — fix board deck
- ✅ **Marta** — confirm Q1/Q2 numbers match Finance close
- ✅ **Daniel** — aware of incident and fix
- ❓ **Anyone else who got revenue numbers from FinBot** — see audit task in ACTION_ITEMS.md
