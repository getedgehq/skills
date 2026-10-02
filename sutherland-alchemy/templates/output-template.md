# Decision brief template

Use this template for a concise recommendation and first-test plan. Adapt the length to the assignment; a small task can use one sentence per field. Replace every bracketed instruction with evidence, a proposal, or an explicit unknown. Do not fabricate a baseline, result, cost, or causal explanation.

The fields and testing conventions are package design. Source citations support the relevant reasoning principles, not a claim that Sutherland prescribed this exact format.

## Decision and status

**Working title:** [Name the customer problem, not just the proposed solution.]

**Recommendation:** [State one first action, its intended benefit, and the evidence needed before committing further.]

**Status:** [Proposal, prototype, test plan, or completed test. State whether any real implementation has occurred.]

## Brief and experiential reframing

**User's request:** [Preserve the requested deliverable and constraints.]

**Original proposed improvement:** [Record the organization's current means, such as a discount or shorter wait.]

**Customer outcome:** [Describe the experience or behavior sought in a specific occasion. Avoid simply renaming the original metric. Reframing principle: [S5].]

**Essential requirements:** [Identify requirements already working, failures that must be repaired, and claims that operations cannot currently support. Attribute distinction: [S3].]

**Journey and neglected moment:** [Map the relevant stages briefly. Name the worst moment and the evidence supporting that diagnosis.]

## Evidence and competing explanations

**Known facts:** [List supplied observations and their source or date. Separate observations from interpretations.]

**Unknowns:** [Identify missing facts that could change the recommendation and the least costly way to learn them.]

| Explanation | Evidence for or against | Distinguishing observation |
| --- | --- | --- |
| [Conventional economic explanation] | [Actual evidence or unknown] | [What would differ if true?] |
| [Psychological or coordination explanation] | [Actual evidence or unknown] | [What would distinguish it?] |
| [Another plausible explanation] | [Actual evidence or unknown] | [What would weaken it?] |

Treat reported motivations as clues and coherent explanations as hypotheses. [S2] [S6]

## Decision context

**Audience and occasion:** [Who is deciding, when, and for what purpose?]

**Alternatives and comparison:** [Include doing nothing, familiar alternatives, and the customer's likely reference point. [S3]]

**Downside and optionality:** [What can go wrong? How costly is it? Can the customer change course? [S7]]

**Contextual reversal:** [Who might prefer the opposite treatment, and why? [S7]]

## Candidate portfolio

Include a conventional improvement, a psychological alternative, and a contextual opposite when relevant. Explain any omission.

| Candidate | Exact intervention or prototype | Inference and expected behavior | Credibility and feasibility | Cost | Reversal or downside |
| --- | --- | --- | --- | --- | --- |
| [Conventional] | [What changes?] | [Mechanism] | [Operational support] | [Known estimate or unknown] | [Where it fails] |
| [Psychological] | [What changes?] | [Mechanism] | [Why the cue is credible] | [Known estimate or unknown] | [Where it fails] |
| [Contextual opposite] | [What changes?] | [Mechanism] | [Who it serves] | [Known estimate or unknown] | [Where it fails] |

**Selected candidate:** [Explain why this is the most useful first test, considering information gained, cost, delivery, and downside. Novelty alone is insufficient. [S3] [S6]]

## First-test plan

- **Hypothesis:** [Changed stimulus leads to a proposed inference and observable behavior.]
- **Comparison:** [Treatment versus comparator; identify assignment method and material confounds.]
- **Held constant:** [Price, capability, or other variables needed to preserve the question.]
- **Primary outcome:** [Define the useful customer or business outcome and denominator.]
- **Diagnostic and downside measures:** [Include completion, failures, complaints, or costs as appropriate.]
- **Exposure and stopping conditions:** [State bounded scope, duration or sample cap, and unacceptable downside.]
- **Decision criterion:** [Set a worthwhile threshold from economics before results. State the analysis approach and limitations.]
- **Disconfirming observation:** [Name a result that would weaken the hypothesis.]
- **Low-evidence fallback:** [Describe what discovery can establish if a causal comparison is infeasible.]

Behavioral knowledge makes an idea worth testing; it does not guarantee success. [S3]

## Decision after evidence

**Choose:** [What result justifies continuing?]

**Revise:** [What result requires changing the treatment or diagnosing implementation?]

**Abandon:** [What result makes another explanation or option preferable?]

**Residual uncertainty:** [Distinguish observed effects from unproven mechanism and untested contexts.]

**Review:** [Record failed checklist items and repairs using ../checklists/review-checklist.md.]
