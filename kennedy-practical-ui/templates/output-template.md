# UI design deliverable template

Use this template for a screen design, implementation handoff, or critique. Fill fields with observed facts or explicitly labeled assumptions. Remove inapplicable optional sections. For a small task, keep each field to one or two sentences. Deliver the requested artifact alongside this record, rather than substituting the template for the work.

## Task and artifact

- **Request:** [Design, implement, critique, or practice; name the actual screen.]
- **User goal:** [Describe the outcome the user seeks on this screen.]
- **Delivered artifact:** [Link to implementation, design file, annotated image, or specification. For critique, link to findings tied to elements.]
- **Scope and constraints:** [Platform, content, brand, component library, and boundaries of the requested change.]
- **Evidence available:** [Rendered interface, screenshot, code, or description; identify what cannot yet be observed.]

Guidance: distinguish an inspected implementation from a proposed design. Reference study can inform the artifact but should not replace the user's actual content. [S1][S6]

## Intended attention order

1. [First content or action; explain why it deserves attention.]
2. [Second content or action; explain its task relationship.]
3. [Supporting or occasional action; explain how it stays findable.]

- **Frequency assumption or evidence:** [Estimate usage if useful; label estimates.]
- **Observed squint result:** [What dominates in the rendered artifact, or Pending.]

Guidance: frequency is an initial proxy. Explain essential exceptions instead of equating all rare information with dispensable information. The squint result records visible weight, not user comprehension. [S5]

## Control and consequence map

| Control | Affected object or region | Placement | Choice rationale | Reachability or ambiguity |
| --- | --- | --- | --- | --- |
| [Label] | [What changes] | [Where it lives] | [Why this control fits the options] | [Long-list or mobile consideration] |

Guidance: map scope before placing controls. Note immediate versus submitted changes, likely date ranges, or count bounds when relevant. If retaining a dropdown, explain why it is appropriate. [S4][S5]

## Reusable visual decisions

| Area | Decision | Reason and reuse boundary |
| --- | --- | --- |
| Alignment and spacing | [Edges, padding, internal gaps, group gaps] | [How content fits and groups remain distinct] |
| Typography | [Body, supporting text, heading, title roles] | [Readable, distinguishable, consistent roles] |
| Color | [Base hue and functional variations] | [Role of each variation and contrast evidence] |
| Component coherence | [Corners, icon stroke, border, shadow] | [Shared shapes and intended personality] |
| Imagery or motif, if used | [Backing, crop, recurring idea] | [Reliability and contribution to identity] |

Guidance: explain relationships and actual values rather than invoking a grid, type scale, or palette name as proof. Mark sample tokens provisional until inspected in context. [S1][S2][S3][S7][S9][S10]

## States and viewport evidence

| Case | Expected behavior | Evidence | Status |
| --- | --- | --- | --- |
| [Default, focused, selected, disabled, loading, error, or empty] | [Task-specific result] | [Screenshot, measurement, or observation] | [Pass, Fail, Pending, or N/A with reason] |
| [Narrow or wide viewport; long content or long list] | [Readable and reachable arrangement] | [Inspected artifact] | [Status] |

- **Contrast record:** [Foreground/background pair, measured ratio, applicable target, and result.]
- **Image text record:** [Treatment and inspected crops, or N/A.]

Guidance: numeric HSB brightness does not establish readability. Changing image content or text requires renewed checks. State coverage and status recording are package conventions. [S2][S3][S7]

## Optional reframe or practice record

- **Original assumption:** [What remained constant in failed iterations.]
- **Alternative:** [Change to form, placement, or representation.]
- **Result:** [Observable improvement and any new ambiguity.]
- **Practice comparison:** [Reference and the specific discrepancy learned from, if this is a practice request.]

Guidance: a reframe must preserve the intended meaning; a practice copy should reveal transferable principles. [S6][S8]

## Review and remaining questions

- **Review result:** [Link to completed checklist and summarize failures.]
- **Unverified checks:** [Pending render, contrast, responsive, or interaction checks.]
- **Open question:** [Specific user interpretation or missing requirement to investigate.]
- **Next correction:** [Concrete action addressing a failed or pending item, if needed.]

Guidance: report limits honestly. Never mark the design fully reviewed when applicable checks remain unobserved.
