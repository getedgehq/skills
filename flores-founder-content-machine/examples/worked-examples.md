# Worked examples

All companies, people, situations, interview answers, and outcomes below are invented illustrations. They are not Jay Flores clients, quotes, or case studies. Source keys map to [sources.md](../references/sources.md). Phase labels and editorial tools come from this package.

## Illustration 1: A pre-launch infrastructure founder

### Assignment and raw material

Mira leads fictional routing software company RelayNest. She wants a LinkedIn post for engineering leaders deciding whether to add an abstraction layer. Marketing proposes taking the whole content program internal because a writer has joined.

Illustrative interview notes:

- Initial belief: hiding all routing choices would make adoption easier.
- Episode: a design partner could not diagnose why a request selected a particular destination.
- Alternatives: add more automated routing, or expose an explanation of the routing choice.
- Decision: make the explanation visible before expanding automation.
- Cost: postpone a planned routing feature.
- Limit: routine traffic can still benefit from silent automation.
- Evidence available: design-partner feedback and a demo walkthrough; no measured incident reduction.

### Weak first draft

> At RelayNest, we believe innovation starts with customer feedback. Our team is committed to building transparent, scalable infrastructure that empowers engineering leaders. Listening to users helps us deliver better experiences as we prepare for launch.

This version reports agreeable values while omitting the actual choice and its cost.

### Outside challenge

The interviewer asks: What did transparency change? What did you stop building? Would you expose every routing detail? What evidence do you have for the result?

The founder confirms the notes above and declines to claim a quantified reliability improvement.

### Improved result

> We postponed a routing feature to explain the routing choices we already made.
>
> In a design-partner walkthrough, an engineer could see where a request went but could not work out why it went there. We had treated that hidden decision as a simpler experience. For someone diagnosing an incident, it was missing context.
>
> We chose to show the reason for a routing choice before adding more automation. That cost us a feature slot, but it gave the partner something concrete to inspect and question.
>
> I still want routine routing to be automatic. My boundary is the diagnostic path: if our software makes a consequential choice, the person responsible for investigating it should be able to see the reason.
>
> When you evaluate an infrastructure abstraction, test the failure investigation as well as the successful request.

### Which rules made the difference

- S2's judgment principle restores the postponed feature and diagnostic boundary.
- S1's outside perspective challenges the team's assumption that hidden decisions mean simplicity.
- S3's technical nuance connects the design choice to the engineering reader's actual task.
- The package evidence rule prevents a fabricated reliability metric.

### Ownership recommendation

Use Phase B for editing and coordination, while keeping outside extraction in Phase A for unsettled product positions. The new writer can own production without inheriting the entire articulation problem. Gate the next transfer on whether internal drafts preserve the decision and its limits without repeated founder rescue.

## Illustration 2: A growing company with two co-founders

### Assignment and raw material

Fictional audit workflow company ClearLedger has a CEO, Omar, and CTO, Lena. Their internal team can ship content consistently. They want to internalize interviews too.

Illustrative notes, confirmed separately by the two founders:

- Product premise: help reviewers inspect evidence and take responsibility for approval.
- Omar's experience: a buyer wanted an automated approval promise; he declined because nobody had agreed who would own an incorrect approval.
- Lena's experience: a prototype's decision trace was difficult to inspect; the team prioritized trace access before adding more decision automation.
- Boundary: automate evidence collection where appropriate, but preserve the reviewer's ability to inspect and contest a consequential decision.
- Evidence: internal decision records, with no public customer name or financial result authorized.

### Weak first draft

> We are proud to help finance teams embrace the future of intelligent automation. Our innovative technology delivers efficiency and trust. As co-founders, we share a passion for empowering our customers to work smarter.

The draft could belong to either founder and replaces a responsibility question with a broad promise.

### Outside challenge

The interviewer asks Omar which promise he refused and why, then asks Lena which technical choice made the shared premise real. Both identify the same boundary from different responsibilities.

### Improved result: CEO version

> I declined to promise automatic audit approval when we could not answer who would own a wrong decision.
>
> The buyer wanted less manual work. So did we. But faster approval and clearer responsibility are different requirements. We could explain how our system gathered evidence; we could not justify removing the person who needed to stand behind the final approval.
>
> We kept evidence collection in scope and left approval with the reviewer. That made the offer narrower. It also made the responsibility explicit.
>
> My test for an automation promise is now simple: before removing a human decision, agree who can inspect it, contest it, and own the consequences.

### Improved result: CTO companion

> Our prototype could produce a decision before it could explain that decision well enough for a reviewer to inspect it.
>
> We prioritized access to the decision trace before adding more decision automation. A correct-looking answer was insufficient if the person responsible for approval could not examine the evidence behind it.
>
> For evidence collection, automation can save work. For approval, inspectability is part of the requirement. I would test that distinction before expanding an automated review system.

### Which rules made the difference

- S4's shared product strategy and separate expertise lanes create coherent, distinct posts.
- S2's judgment rule retains the refused promise and the narrower offer.
- S1's reader-clarity rule exposes a responsibility assumption hidden in the original draft.
- The package evidence rule avoids inventing customer endorsement or savings.

### Ownership recommendation and improved plan

Weak plan: hire a content manager and end outside support next month.

Improved plan: let the internal owner lead the next agreed interview cycle with an outside reviewer observing. Give the owner the decision records, example idea cards, question sequence, and review checklist. Advance from Phase C to Phase D when both founders' positions survive internal drafting, an unfamiliar reader can distinguish them, and the owner can challenge unsupported promises. Retain a scoped outside review for new automation claims while that gate remains unmet. Documentation draws on S5; the gates are package adaptations.
