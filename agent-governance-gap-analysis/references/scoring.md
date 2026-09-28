# Scoring and tiers

Every check resolves to one of **three** states. Record all three during the walkthrough; they are not interchangeable.

| State | Meaning | Counts toward |
|---|---|---|
| **Met** | The control exists and covers every agent, system and user in scope. | The score. |
| **Partial** | The control exists and operates, but does not cover everything in scope. | The partial count only. Never the score. |
| **Not met** | No control, or the answer is "no". | Nothing. |
| **Unknown** | The user cannot answer. | The unknown count. Never the score. |

**The headline score is met-only, out of 25.** That number is the credibility of this assessment; nothing else moves it. Partial and unknown are reported beside it:

> **7 / 25 met** · 6 partial · 2 unknown

## What counts as partial

The rule: **the control exists and operates, but not across every agent, system or user in scope.**

Partial usually takes one of four shapes:

1. **Subset of agents** — covers the sanctioned agents, not the ones people brought themselves.
2. **Subset of systems** — the production database is governed, the CRM and the wiki are not.
3. **Subset of people** — engineering is covered, the rest of the company is not.
4. **Manual where it should be automatic** — the control works, but only because a person remembers to run it.

What is **never** partial:

- Planned, budgeted, scoped, piloted, or on the roadmap. Intent is not a control. This is the single most common attempt to claim partial, and it must be refused every time.
- A control that exists on paper but has never been tested or enforced.
- A neighbouring control that happens to reduce the same risk. SSO is not credential mediation, however much it helps.

If the user argues for partial and it does not fit one of the four shapes, say plainly which shape it would need to fit and let them answer. Partial is the state that will erode first if it is allowed to become a negotiation.

## Unknown is a finding, not an absence

"I don't know" is evidence about the **Agent Discovery** dimension — somebody should be able to answer, and nobody can. Note which checks came back unknown and who would have to be asked. On the remediation plan, unknowns get an owner and a date to find out, not a fix.

Never let a user settle on unknown to avoid an uncomfortable "no". Ask once whether they genuinely don't know, or suspect the answer is no. Suspected-no is **not met**.

## Tiers

Computed from the **met** score alone.

| Score | Tier | Verdict to use in chat and on the scorecard |
|---|---|---|
| 0–6 | **Ungoverned** | Agents are operating without meaningful controls. You cannot currently answer what your agents can reach, who is responsible for their actions, or what they did. Start with discovery — everything else depends on it. |
| 7–13 | **Exposed** | Some controls exist, but the gaps are load-bearing. Most likely credentials sit inside agent runtimes and nothing evaluates an action before it executes, so a single compromised session reaches further than anyone intends. |
| 14–21 | **Partial Coverage** | The structure is there and the remaining gaps are specific rather than systemic. These are the checks that surface during an audit or an incident — worth closing deliberately rather than opportunistically. |
| 22–25 | **Governed** | Agent access is governed the way human access is: identity-bound, policy-enforced, revocable, logged. Keep the remaining gaps on the roadmap and re-test the controls, especially offboarding, on a schedule. |

A high partial count against a low met score is worth naming out loud: it means the work has started and stalled before reaching full coverage, which is a different conversation from having done nothing. Say which of the four shapes the partials cluster into — "you've covered the sanctioned agents but not what people brought themselves" is a more useful sentence than any number.

## Re-tests

On a re-run, compare all three counts against the previous assessment, per dimension rather than only in total. The expected path of progress is **unknown → not met → partial → met**, and each of those transitions is real movement worth crediting:

- unknown → not met means they found out. That is discovery working.
- not met → partial means a control now exists.
- partial → met means it reached full coverage.

A re-test where the headline score has not moved but six checks went partial is progress, and saying so is the difference between a team continuing and a team concluding the exercise was pointless. It is also why the partial count exists — do not let it inflate the headline in exchange.

## Per-dimension weighting

Dimensions are not equal in practice, even though the score treats each check as one point. When choosing what to tell the user to fix first, use this order of leverage:

1. **Agent Discovery** — you cannot govern what you cannot enumerate. Every other dimension silently applies only to the agents you know about.
2. **Credential Mediation** — the highest-severity failure mode. An agent holding a long-lived token processes untrusted input in the same process as the credential.
3. **Policy Engine** — the control point everything else hangs off. Without it, HITL and least privilege have nowhere to live.
4. **Identity Lifecycle** — the gap that produces incidents months later, via leavers and movers.
5. **Least Privilege** and **Human-in-the-Loop** — these reduce blast radius; they need 3 in place first.
6. **Audit Trail** — essential for audits and incident scoping, but it records governance rather than creating it.

Say the leverage argument in one or two sentences. Do not lecture.

A partial in a high-leverage dimension is worth more attention than a met in a low one. Finishing a started control is nearly always cheaper than starting a new one, so partials in dimensions 1–3 are the first thing to look at when choosing what goes in the 30-day column.

## Dimension max scores

For the per-dimension bars on the scorecard:

| Dimension | Max |
|---|---|
| 01 Agent Discovery | 4 |
| 02 Credential Mediation | 4 |
| 03 Policy Engine | 4 |
| 04 Human-in-the-Loop | 3 |
| 05 Privilege Scope | 3 |
| 06 Identity Lifecycle | 3 |
| 07 Audit Trail | 4 |
