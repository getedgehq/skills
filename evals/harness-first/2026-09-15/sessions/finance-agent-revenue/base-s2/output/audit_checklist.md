# FinBot Audit Checklist

**Purpose:** Identify other places where incorrect revenue numbers may have been used

**Context:** FinBot has been overstating revenue by ~14-26% since March 2026 due to including cancelled/refunded orders.

---

## Confirmed Issues

| Date | User | Query | FinBot Response | Correct Answer | Used In |
|------|------|-------|----------------|----------------|----------|
| 2026-09-11 | Priya | Q2 2026 revenue | $4.1M | $3.6M | ✅ Board deck |
| 2026-09-11 | Priya | Q1 2026 revenue | $4.1M | $3.3M | ❓ Unknown |

## Search Terms for Slack Audit

Search #ask-finance channel history for:

```
@finbot revenue
@finbot sales
@finbot Q1
@finbot Q2
@finbot Q3
@finbot quarterly
@finbot YTD
@finbot year to date
@finbot total revenue
@finbot how much
```

## Potential Artifacts to Check

### Board/Investor Materials
- [x] Q3 2026 Board Deck (contains Q2 revenue)
- [ ] Q2 2026 Board Deck (may contain Q1 revenue)
- [ ] Q1 2026 Board Deck
- [ ] Investor update emails (Q1, Q2, Q3 2026)
- [ ] Pitch decks updated since March 2026

### Internal Planning
- [ ] 2026 budget vs actuals reports
- [ ] Q2 business review slides
- [ ] Department performance reviews
- [ ] Sales team comp calculations (if based on company revenue)

### External Communications
- [ ] Press releases mentioning revenue
- [ ] Customer case studies with company stats
- [ ] Recruiting materials (company metrics)

## Reference: Correct Revenue Numbers

Use these to verify/correct any documents:

| Period | ❌ FinBot Said | ✅ Finance Actual | Difference |
|--------|--------------|------------------|------------|
| Q1 2026 | $4,141,985.86 | $3,285,493.84 | $856,492.02 (+26.1%) |
| Q2 2026 | $4,307,322.65 | $3,638,335.79 | $668,986.86 (+18.4%) |
| Q3 2026 | $2,944,799.03 | $2,681,560.47 | $263,238.56 (+9.8%) |

### Monthly Detail

| Month | Revenue |
|-------|----------|
| 2026-01 | $1,029,676.69 |
| 2026-02 | $1,007,956.74 |
| 2026-03 | $1,247,860.41 |
| 2026-04 | $1,237,516.63 |
| 2026-05 | $1,209,658.31 |
| 2026-06 | $1,191,160.85 |
| 2026-07 | $1,335,233.73 |
| 2026-08 | $1,162,073.21 |
| 2026-09 | $184,253.53 |

| **YTD 2026** | $11,524,266.03 | $9,605,390.10 | $1,918,875.93 (+20.0%) |

## Action Items

### Priority 1 (Before Board Meeting)
- [ ] Update Q3 board deck with correct Q2 revenue ($3.6M, not $4.1M)
- [ ] Check if Q1 revenue is also in deck (correct to $3.3M, not $4.1M)
- [ ] Review QoQ comparison (Q2 is -11% vs Q1, not flat)

### Priority 2 (This Week)
- [ ] Export #ask-finance Slack history since March 2026
- [ ] Search for revenue-related queries (see search terms above)
- [ ] Create spreadsheet of: date, user, query, response, used_in
- [ ] Contact users to verify where numbers were used

### Priority 3 (Next Week)
- [ ] Review all board/investor materials from Q2 and Q3 2026
- [ ] Check internal planning docs for wrong numbers
- [ ] Update any affected documents
- [ ] Consider notification if external materials affected

## Notes

- FinBot has been live since **March 2026** (6 months)
- Overstatement ranges from **14-26%** depending on quarter
- The error is **systematic** - affects all revenue queries the same way
- Order count queries are likely **correct** (those properly use orders table)
- Customer, refund, and KPI queries should also be **correct**

## Who to Involve

- **Jonas (Data):** Lead technical investigation of Slack history
- **Marta (Finance):** Validate corrected numbers
- **Priya (Strategy):** Audit board/investor materials
- **Legal/Comms:** If external disclosures affected
