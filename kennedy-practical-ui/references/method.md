# Method

Based on Erik Kennedy's public method. Not affiliated with or endorsed by Erik Kennedy.

## Scope and evidence

Kennedy's approach makes visual design tractable through observable relationships: what attracts attention, what aligns, what a control changes, and how neighboring shapes and colors work together. Prefer concrete comparisons over explanations based only on taste or a named design system. His introductory guidance addresses developers and UX designers making clean, simple interfaces; it is not a universal style prescription. [S1][S10]

This document distinguishes source principles from package practice. Citations support the attributed principles. Deliverable structure, review statuses, responsive stress cases, and preservation of existing implementation constraints are operational conventions added by this package. They are not claims about Kennedy's complete curriculum or current accessibility standards.

Start with the actual task, copy, content, and platform. Identify whether the request is design, implementation, critique, or practice. A critique may produce a prioritized set of annotated findings without a redesign. A practice exercise can reproduce a reference closely without becoming a production design. Retain established tokens where they support the task; source criticism of rigid systems does not require deleting a working system.

Record the available evidence: screenshot, rendered page, design file, code, or written description. State what can be inspected. If there is no rendered artifact, propose visual checks and mark them pending. A description cannot establish that a squint test or responsive crop passed.

## Attention and teaching

### Find the attention order

Rank the task's essential content and actions before styling. Kennedy suggests estimating how often an action occurs per page view as a first approximation of importance. A repeatedly used answer button deserves stronger emphasis than a rarely used settings action. This is a starting heuristic, not proof that low-frequency information has low importance. [S5]

Package application: adjust the ranking when occasional information is essential to informed action, such as a booking price or an irreversible action's consequence. Do not hide useful information merely to simplify a screenshot.

Squint or blur the screen until wording becomes difficult to read. Compare the visible shapes, contrast, and scale against the intended task order. If a help button, decorative header, or navigation block dominates the core action, change the emphasis. Repeat after styling because color can overturn a previously sound hierarchy. The test diagnoses visual weight; it does not prove comprehension. [S5][S10]

### Teach unfamiliar concepts concretely

When copy explains a new feature without showing what it does, supply an example of use or output. Kennedy's public examples include sample projects on first load, inline instructional content, product demonstrations, and galleries of user creations. A concrete outcome can make an abstract description understandable. [S5]

Package application: label illustrative sample data and provide a clear path to the user's own work. Choose the smallest example that communicates the capability. Do not expand a screen request into an unrelated onboarding project.

## Learning through controlled practice

When a specific skill is missing, study a reference that demonstrates that skill well. Identify its relevant relationships, such as spacing, text hierarchy, or surface contrast. Kennedy advocates active study and reproduction rather than merely accumulating inspirational images. [S2][S6]

For copywork, choose a design beyond current ability and recreate it closely. Compare concrete discrepancies: padding, type weight, line breaks, hue, decorative detail, and alignment. Explain what each discrepancy changes. The fetched copywork page is a public excerpt; this package uses its stated premise and does not imply access to its linked continuation. [S6]

A simpler practice route is to work on one small component. Kennedy explores a button to uncover typography, color, shadows, borders, and icon relationships. Fewer variables make the consequences of a change easier to see. Then transfer the principles to larger compositions. [S7]

Do not transplant a famous product's interaction solely because it looks authoritative. A floating add button may affect the wrong conceptual object in a different screen. Visual references and interaction precedents require separate evaluation. [S5][S8]

## Layout, spacing, and alignment

### Grayscale before color

For a clean application, use black, white, and gray to establish spacing, sizes, and hierarchy. Introduce color afterward for a reason, such as directing attention or distinguishing a state. One theme hue with useful variations can support a coherent interface. [S1]

Exception: a vivid, sporty, flashy, or cartoon-like identity depends substantially on color. Kennedy explicitly notes that grayscale-first is less useful there. Use grayscale as a structural diagnostic while evaluating the intended color identity in parallel. Do not assume the grayscale version settles the entire design. [S1]

### Give space a job

Kennedy urges substantially more breathing room than unstyled HTML provides. Examine three layers: line spacing, separation between elements, and separation between groups. Compare a noticeably roomier draft instead of adjusting every gap by a barely perceptible amount. [S1]

Package application: treat the whitespace advice as a corrective, not an arithmetic mandate. In a dense operational table, preserve task-relevant information and compare row readability, grouping, and scanning before increasing every dimension. Within-group spacing should support association; between-group spacing should reveal structure.

### Align content rather than obeying an arbitrary grid

Kennedy criticizes grids that force content into predetermined widths across variable screens. Preserve their useful outcome, aligned content, without forcing an image, label, or control to stretch just because the viewport grows. Simple mobile layouts can begin with left, center, and right guides. Add structure when the content demands it. [S10]

Package application: an existing responsive grid may remain useful. Judge it by text fit, meaningful alignment, and behavior at different widths. Inspect long labels and real content. The article's sample margins and image sizes illustrate its reasoning; they are not mandatory package tokens.

## Locality and reachability

Kennedy describes three related placement rules. [S4]

1. Put a control near the object it changes. Thread actions belong on a thread; folder actions belong near a folder. A conceptual object, such as an account, can anchor settings and sign-out controls even without a literal on-screen record. [S4]
2. Put controls affecting a whole region above that region. Apply this recursively: page filtering belongs above the page's list, while application search belongs at a broader level. Kennedy allows higher-level exceptions and suggests separating different scopes horizontally when necessary. [S4]
3. Increase visibility when a control must move away from its consequence. Reachability and long lists can justify displacement, but the moved action needs stronger visual presence. [S4]

For an add action, first ask where the new object appears. An inline action can communicate this well when the list is short. A long list may bury it, so compare an anchored action or a clearly associated control above the list. Kennedy discusses both approaches. [S5]

Explicit warning: spare space is not a sufficient placement rationale. A plus over the main panel may appear to add a main-panel item even if it actually creates an object in the sidebar. A label and placement must make the affected object understandable. [S5][S8]

Package application: inspect the long-list state, mobile reach, and selected-item state. If controls appear on hover, provide an appropriate visible or focus-accessible route on platforms without hover. This is a delivery safeguard, not a fourth attributed locality law.

## Control selection

Kennedy warns that dropdowns hide choices and add interactions, especially on mobile. Consider alternatives before accepting one. His warning is explicitly qualified: few options, rarely changed defaults, and desktop usage can make dropdowns reasonable. [S5]

| Choice structure | Candidate control | Decision detail |
| --- | --- | --- |
| Two peer alternatives without a natural off state | Segmented control | Show both choices and allow direct selection. [S5] |
| Binary setting committed with a form | Checkbox | Communicate an off/on value that applies on submission. [S5] |
| Binary setting applied immediately | Switch | Use when the change actually takes effect immediately. [S5] |
| A few mutually exclusive options | Radios or segmented control | Keep options visible; vertical layouts accommodate longer labels. [S5] |
| A few options requiring explanation | Selectable cards | Show the relevant descriptions or visual differences. [S5] |
| Many searchable options | Typeahead | Reduce scrolling when users can identify or search the desired value. [S5] |
| Appointment or similar near-future date | Calendar | Make the likely time window easy to select. [S5] |
| Birth date or date across many years | Direct date entry | Avoid navigating many calendar pages for an arbitrary date. [S5] |
| Small count concentrated near low values | Stepper | Support quick changes around likely counts. [S5] |
| Few options with a rarely changed default | Dropdown | Keep when its tradeoff fits the actual usage context. [S5] |

Package application: verify keyboard use, labels, bounds, and error behavior for whichever control is implemented. Date entry needs an unambiguous format and validation. A stepper suited to one to four seats may be inefficient for hundreds of units. Those constraints qualify the choice rather than invalidate the source heuristic.

## Typography and states

Begin with readable body text. Make subtitles distinguishable during scanning, and make titles distinct without producing excessive mobile wrapping. Reuse sizes for the same role across screens. Kennedy rejects relying on a mathematical type ratio to fix a poor design, while still insisting on distinguishable, consistent hierarchy. [S10]

For a clean professional interface, choose a proven neutral font that suits the brand. Kennedy's public article names several examples, but the operative principle is appropriate letterforms and readability, not a compulsory font list. He cautions beginners about difficult-to-use very light weights. [S2]

Balance attention-increasing and attention-reducing properties. A large statistic can use lighter weight; a small uppercase label can use quieter color. Kennedy reserves all-out emphasis for page titles and recommends mixed emphasis elsewhere. Supporting information should become visible when sought without overwhelming the main task. [S2][S10]

Kennedy recommends additional tracking for uppercase words in fonts designed for sentence case, while noting an uppercase-only font may already include that spacing. Inspect the actual font rather than adding tracking twice. [S7]

For interactive text, avoid size, case, or weight changes that alter the text footprint and cause unstable hover behavior. Color, background, underlining, or shadow can convey state without reflow. Kennedy also warns against using underline as arbitrary decoration because people associate it with links. [S2]

Package application: cover focus, selected, disabled, loading, and error states when applicable. Preserve readable supporting text while reducing its relative emphasis. Quiet styling is not permission to make essential text illegible.

## Color variations

Think in hue, saturation, and brightness to adjust a base color rather than collecting unrelated palette swatches. Kennedy's central pattern is darker variations through lower brightness and higher saturation, and lighter variations through higher brightness and lower saturation. Use these as coupled directional adjustments, not a fixed numeric formula. [S3]

Assign variations to actual roles: accent, action background, hover background, subtle surface, border, and supporting text. A role may need a different relationship from another role; not every state needs to darken. The public article itself includes implementations that only approximate its general pattern. [S3]

Explicit warning: adding translucent black lowers HSB brightness without adding saturation, so it cannot reproduce every desirable dark variant. This does not prohibit black overlays for image text or contextual shadows, which Kennedy discusses elsewhere. [S1][S2][S3][S7]

Hue is secondary when producing ordinary lighter and darker variants. Kennedy describes optional shifts toward local low or high points of perceived lightness. Treat this as an optional refinement and verify the result visually. Equal HSB brightness can produce very different perceived lightness across hues. [S3]

Measure rendered text/background contrast. Kennedy's button exercise shows that a pleasing aqua can fail text contrast and can be adjusted into a more readable teal. His discussion supports checking rather than trusting a hue name or brightness number. It is not a substitute for the accessibility requirements applicable to the user's project. [S7]

Package application: record the actual foreground and background, measured ratio, target requirement, and result. Do not infer compliance from grayscale appearance. Preserve semantic colors where required; a single-hue strategy is a coherence technique, not a rule against error, success, or categorical colors.

## Component coherence and light

Choose a small representative component and describe its intended personality with concrete qualities. Kennedy compares rounded, friendly letterforms with squared, engineered ones, then adjusts corners and color connotations accordingly. These are relationships to inspect rather than immutable equations linking every font to one radius. [S7]

For an inline icon, match the neighboring type's apparent stroke weight and corner character. Inspect it at actual size; tiny internal details can disappear and make an icon unsuitable. The comparison is especially useful for icons directly adjoining a label, not a demand that every illustration resemble a glyph. [S7]

If adding depth, use consistent overhead illumination. Raised controls can be lighter above and cast shadow below; inset surfaces receive different edge treatment. Kennedy advocates subtle dimensional signals in otherwise clean interfaces rather than requiring elaborate skeuomorphism. [S1]

Tune borders and shadows against their actual surface. The same translucent black border can be obvious on teal and barely visible on darker blue. A very strong shadow suitable for one dark component may overwhelm a lighter one. A black component cannot gain a darker black bottom edge. [S7]

Package application: compare states side by side and on their intended page backgrounds. Adopt successful relationships into reusable tokens, without transferring the demonstration's measurements blindly.

## Imagery and motifs

Kennedy offers several image text treatments: darken the whole image, place text on a backing, blur an area while preserving tonal separation, darken toward the text area, or use a local soft darkening treatment. Choose the simplest reliable treatment for the content and crop. [S2]

Explicit warning: direct text on an untreated image is fragile. It depends on the image's darkness, edge activity, text position, and viewport. Blurring texture alone does not guarantee tonal contrast. Repeat checks when the image, text, or crop changes. [S2]

A motif is a recurring visual idea expressed in different forms. Kennedy demonstrates shape relationships across logos, letterforms, dividers, decoration, and special text. He also presents recurring gradients as a color motif. The relationship among applications creates identity; unrelated ornaments do not. [S9]

Explicit warning: motifs improve an already sound design and cannot rescue weak fundamentals. Add them after spacing, hierarchy, readability, and interaction are working. A brand motif is also different from chasing a personal signature before mastering craft, which Kennedy discourages. [S9][S10]

Package application: a motif is optional. Preserve an established brand and avoid modifying a logo merely to force repetition. Keep decorative forms from looking like clickable controls or taking attention from the task.

## Reframing

When every small tweak disappoints, identify the constants in the attempted solutions. A button may not need to remain a rounded box in the same position. A collection of related statistics may communicate better as a visual comparison than as isolated labels and numbers. Change one sensible assumption and compare the result against the goal. [S8]

Kennedy explicitly checks ambiguity introduced by a promising alternative: an unlabeled plus can appear to expand a list rather than create an object, and a clickable area can resemble a selected navigation item. A prettier alternative still needs to communicate the intended behavior. [S8]

Package application: record the failed assumption, candidate reframe, improvement, and remaining question. For a chart, retain precise values where users need them. For an action, make the affected object and resulting state explicit. Stop when the requested outcome is supported by evidence, rather than searching indefinitely for a theoretical best solution.
