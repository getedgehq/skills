# Filling the output templates

Both templates in `assets/` are placeholder files. Copy each one, replace every `{{PLACEHOLDER}}`, save the result to a new path. Never edit the templates in place, and never leave a `{{...}}` unreplaced — grep the finished file for `{{` before presenting it.

Do not rewrite the scorecard CSS. Design consistency is the point of shipping a template.

---

## Scorecard — `assets/scorecard-template.html`

| Placeholder | Value |
|---|---|
| `{{SCORE}}` | checks **met**, e.g. `7`. Met only — never add partial to this. |
| `{{PARTIAL}}` | checks partial |
| `{{NOT_MET}}` | checks not met |
| `{{UNKNOWN}}` | checks the user could not answer |
| `{{PARTIAL_PCT}}` | `round(PARTIAL / 25 * 100)` — the second bar segment, drawn after the met segment |
| `{{SINCE_LAST}}` | on a re-test, one `<p class="since">` comparing all three counts to the previous run; **delete the placeholder entirely on a first assessment** |
| `{{TIER}}` | `Ungoverned` / `Exposed` / `Partial Coverage` / `Governed` |
| `{{TIER_CLASS}}` | `t-ungoverned` / `t-exposed` / `t-partial` / `t-governed` |
| `{{TIER_VERDICT}}` | the tier verdict sentence from `scoring.md`, verbatim |
| `{{SCOPE}}` | `Whole organisation` or `One user's setup`, plus a clause if it was mixed. In whole-organisation mode write `Whole organisation — self-reported`, and add `; one workstation spot-checked` if a scan ran alongside. Never let an org-scope scorecard imply anything was technically verified org-wide. |
| `{{DATE}}` | assessment date, e.g. `31 August 2026` |
| `{{METHOD}}` | what was actually done, including the scan root — e.g. `Interactive walkthrough`, or `Read-only scan of global agent config on one workstation + interactive walkthrough`, or `Read-only scan of one project folder (global config not reachable) + interactive walkthrough`. Never write "scan" without saying what it covered. |
| `{{PROGRESS_PCT}}` | `round(SCORE / 25 * 100)` |
| `{{HEADLINE}}` | one sentence, specific to this result — what you would say to their CISO |
| `{{DIMENSION_ROWS}}` | seven dimension blocks, see below |
| `{{GAP_ROWS}}` | one gap block per unmet check, weakest dimension first |
| `{{UNVERIFIED}}` | one `<li>` per unknown check and per check the scan could not reach — say what to find out and who would know. Delete the whole `<section id="unverified">` if there are none. |
| `{{FIRST_MOVE}}` | the single highest-leverage gap to close first, and why |

### Dimension block

One per dimension, all seven, in order, concatenated into `{{DIMENSION_ROWS}}`:

```html
<div class="dim">
  <div class="dim-head">
    <span class="dim-name">01 — Agent Discovery</span>
    <span class="dim-num">1/4 met · 2 partial</span>
  </div>
  <div class="bar">
    <i class="bar-fill mid" style="width:25%"></i><i class="bar-part" style="width:50%"></i>
  </div>
  <p class="dim-note">Registry covers sanctioned agents only; no automated detection of new adoption.</p>
</div>
```

- First segment width is `met / max * 100`; second segment is `partial / max * 100`. Omit the second `<i>` when there are no partials.
- Bar class on the first segment: `good` when all checks are met, `bad` when none are met and none are partial, `mid` otherwise.
- `dim-num` reads `{met}/{max} met`, plus ` · {n} partial` and ` · {n} unknown` only when those are non-zero. Do not print zeros.
- Drop the `<p class="dim-note">` entirely when the dimension is complete. Do not write "nothing missing".
- Max per dimension is in `scoring.md`.

### Gap block

One per unmet check, ordered by the leverage list in `scoring.md`, concatenated into `{{GAP_ROWS}}`:

```html
<li class="gap">
  <div class="gap-dim">02 — Credential Mediation</div>
  <p class="gap-stmt">Agents never hold real credentials directly.</p>
  <p class="gap-fix"><b>Close it:</b> Move the GitHub PAT out of your MCP config and behind a broker, so a compromised session yields nothing replayable.</p>
</li>
```

The fix must be specific to what this user told you or what you found — the generic version from `checks.md` is a starting point, not the output. Reference their actual tools by name where you know them.

**Order:** partials in high-leverage dimensions first, then not-met in high-leverage dimensions, then the rest. Finishing a started control is nearly always cheaper than starting a new one, and leading with it makes the list feel closable rather than damning.

**Mark the state.** A partial gap carries `<span class="chip">Partially in place</span>` after the statement, and its "Close it" line says what is missing rather than restating the whole control — "extend it to the agents people set up themselves", not "build a registry". Getting this wrong is the fastest way to lose a reader who has already done the work.

**Unknowns are not gaps.** They go in the `{{UNVERIFIED}}` section, phrased as what to go and find out and who would know — never as a failure.

---

## Remediation plan — `assets/remediation-plan-template.md`

Every gap on the scorecard appears exactly once, in one of the three horizons.

**Placement:** 30 days = high severity or low effort. 60 days = needs a tool or a process change. 90 days = needs a platform decision, a budget, or another team's roadmap.

**Table columns:** owner is a role, not a guessed name, unless the user named someone. Effort in hours / days / weeks, honestly — a plan nobody believes does not get done. "Done when" must be a condition someone can test, not "implemented".

**Two sections come before the horizons:**

- **Finish what's already started** — one row per *partial* check. `{{WHAT_IS_MISSING}}` names only the uncovered part ("the agents staff set up themselves", "everything outside engineering"), never the whole control. These are the cheapest wins and the reason the next assessment moves, so they lead.
- **Find out** — one row per *unknown* check. `{{UNKNOWN_CHECK}}` is phrased as a question, `{{WHO}}` is the role who would know, `{{DATE_BY}}` is when they will have asked. Unknowns get an answer, not a fix; do not invent remediation for something nobody could confirm.

Partial checks appear in these sections and **not** again in the 30/60/90 tables. Every other gap appears exactly once across the three horizons.

Delete a horizon that ends up empty rather than padding it — same for the two sections above, `{{ACCEPTED_RISKS}}`, and the whole table if there were no partials or no unknowns.

Row placeholders (`{{CHECK}}`, `{{ACTION}}`, `{{ROLE}}`, `{{EFFORT}}`, `{{DONE_WHEN}}`) repeat per row; the table rules above apply to all of them.

The prose placeholders — `{{WHY_THIS_MATTERS_NOW}}`, `{{OPEN_DECISIONS}}`, `{{ACCEPTED_RISKS}}` and the dependency note — carry the plan. Write them in plain language with no vendor framing: this org's actual exposure, via which gap, and what it would cost to find out the hard way.


## Re-tests

On a re-run, fill `{{SINCE_LAST}}` with a single line comparing all three counts:

```html
<p class="since">Since the last assessment on 14 June: <b>+3 met</b>, +2 partial, 4 fewer unknown.</p>
```

Credit every transition, not only the ones that moved the headline — unknown → not met means they found out, and not met → partial means a control now exists. A re-test where the score held but six checks went partial is progress, and saying so plainly is what makes a team run it a third time.

Never restate the previous score as if it were today's, and never reorder the dimensions between runs — the scorecard is compared side by side with its predecessor.
