# Tallow CRM Renewal: Renew at 40 seats

**Recommendation:** Renew at 40 seats. We use 38, pay for 60, and are locked into list-price increases we cannot see until after the notice deadline expires. Cutting to 40 saves ~€16k against current spend and gives headroom without paying for 22 unused licences.

---

**AT A GLANCE**

| Contract status | Notice deadline | Current cost | Est. 40-seat cost |
|---|---|---|---|
| Auto-renews 1 Nov 2026 unless we act | 1 October 2026 (30 days) | €48,000/year (60 seats @ €800) | ~€32,000/year (40 @ €800 baseline) |

| In scope | Not in scope | Data source | Timeline pressure |
|---|---|---|---|
| Do we renew, and at what seat count | Switching to another platform mid-term | Contract, August usage export, vendor emails | 14 days to notice deadline; pricing unknown until "early October" |

---

## 01. We are paying for 60 seats and using 38

August 2026 actuals from Tallow's own usage export:
- 60 seats assigned (what we pay for)
- 38 users active in the last 30 days (what we use)
- 22 unused seats = 37% waste

By team:
| Team | Assigned | Actually used |
|---|---|---|
| Housing Services | 22 | 17 |
| Tenant Repairs | 18 | 15 |
| Finance | 8 | 3 |
| Fundraising | 7 | 2 |
| Leadership | 5 | 1 |

**The waste is concentrated:** Finance, Fundraising and Leadership account for 20 assigned seats and 6 active users. Housing Services and Tenant Repairs are the load-bearing teams (32 active users) and they fit comfortably in 40 seats.

---

## 02. The pricing mechanism works against us

The contract auto-renews at "Vendor's then-current list price" unless we give 30 days' notice (clause 9.2). The notice deadline is **1 October 2026**. Tallow's account manager will not share the new list price until "early October" when packaging is published.

**We are deciding blind.** If we do nothing, we lock in at whatever Tallow publishes after the window closes. If we give notice now, we exit entirely. The only move we control is the seat count, and we can only change it at renewal.

Finance budgeted €52,800 for FY27 assuming a 10% increase (last year's pattern). If list price goes to €900/seat and we stay at 60, the actual cost is €54,000. If it goes to €850, it is €51,000. The uncertainty is small in absolute terms but the mechanism is adversarial.

---

## 03. Cutting to 40 seats saves ~€16,000 and still covers the teams that use it

Scenario at €800/seat (current baseline):
- **60 seats:** €48,000/year
- **40 seats:** €32,000/year
- **Savings:** €16,000 (33%)

If list price increases 10% to €880:
- **60 seats:** €52,800/year
- **40 seats:** €35,200/year  
- **Savings:** €17,600 (33%)

40 seats covers 38 active users plus 2-seat buffer. The at-risk teams (Housing Services, Tenant Repairs) have 32 active users between them and would retain all their access. The cut comes from Finance, Fundraising and Leadership where 14 assigned seats are barely touched.

**The operational objection is weak.** Aisha flagged that "the tenant repairs team live in the case module" and switching mid-winter would hurt. True—but we are not proposing to switch platforms, only to remove dormant licences from teams that are not using them.

---

## 04. If we do not cut now, we wait another 12 months

Clause 3.3: seat count can only be reduced "with effect from the start of a Renewal Term". If we renew at 60 on 1 November 2026, we are locked at 60 until 1 November 2027. The €16k is gone.

The contract does allow mid-term seat **increases** (clause 3.4, pro-rated), so we have an escape if we cut too deep. We do not have an escape if we cut too shallow.

---

## 05. The alternative is to exit entirely, which Housing Services will not accept

The contract requires 30 days' notice to prevent renewal (clause 9.2). That notice deadline is 1 October. If we miss it and decide in November we want out, we are locked in for another year and still owe the full year's fee even if we stop using it (clause 9.5).

**Exit is not credible.** Aisha's note that "switching mid-winter would hurt them badly" applies even more strongly to switching platforms entirely. The Repairs module is load-bearing and the export bug that was breaking their workflows only just got fixed in release 9.4. 

We looked at Cobbleworth two years ago (quoted ~€31k, per the ops channel) but nobody used the trial licence when Dev set it up, and it lapsed. There is no shovel-ready alternative.

---

## 06. Recommendation: Give notice to reduce to 40 seats by 1 October

**Action required:**
1. Email contracts@tallow.example and Lukas Brenner by **1 October 2026** stating we are renewing at 40 seats effective 1 November 2026.
2. Update FY27 budget line to €32,000 baseline (or €35,200 if assuming 10% list increase).
3. Confirm with Dev and Aisha which 20 seats to unassign (suggest: all Fundraising, most of Finance and Leadership, keep Housing Services and Repairs whole).

**Risk:** We cut too deep and need to add seats mid-term. Mitigation: 40 covers 38 active users, and mid-term additions are allowed under clause 3.4. We pay pro-rata for the add, not a 12-month penalty.

**If we do nothing:** We auto-renew at 60 seats and lock in another €48k–€54k (depending on list price movement) for 22 licences no one is using.

---

## Exclusions and assumptions

**Pricing assumption:** Tallow's new list price is not yet published. This analysis uses €800/seat (current rate) as baseline and €880 (10% increase) as the stress case. If the actual increase is larger, the case for cutting seats is stronger.

**No platform switching considered:** Aisha's team depends on the Repairs module and there is no transition plan in flight. This is a seat-count decision, not a vendor decision.

**Notice mechanics confirmed:** Clause 9.2 requires written notice to contracts@tallow.example at least 30 days before term end. Lukas (account manager) is out until 28 September, but the contract clause governs, not his availability.

**Seat reassignment:** The contract allows seat reassignment between individuals (clause 2.1). We are not removing access from active users, only unassigning licences that are dormant.

---

*Prepared for Priya Sundberg, 17 September 2026. Contract reference TSW-BHT-2025-114. Source materials: contract excerpt, Tallow email thread, ops channel 2–14 Sep, August 2026 seat usage export.*
