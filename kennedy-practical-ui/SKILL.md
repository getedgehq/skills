---
name: kennedy-practical-ui
description: "Design or critique web and mobile interfaces using Erik Kennedy's practical approach to hierarchy, spacing, typography, color variations, local controls, and cohesive motifs. Use for concrete screen design, UI redesign, or visual design practice."
---

# Practical UI Design through Learn UI Design and Design Hacks
Based on Erik Kennedy's public method. Not affiliated with or endorsed by Erik Kennedy.

## When to use

Use this skill when designing a real interface, improving a working screen, or explaining why a UI feels awkward. It is especially useful for developers and UX designers who need actionable visual decisions rather than abstract design theory. Work on the actual screen and its content instead of substituting a lecture about aesthetics. [S1]

For a practice request, use a controlled reproduction or a minimal component exercise. For a production request, carry the discovered principles into the user's own interface. Treat the procedure below as an operational synthesis of public essays, rather than a claim to reproduce Kennedy's paid curriculum. [S6][S7]

## Operational procedure

### 1. Define the attention order before styling

List what the user most often needs to see or do on this screen, then rank supporting and occasional actions. If the brief leaves priority unclear, estimate how often each action occurs per screen visit and state the assumption. Frequency is a useful first approximation of importance, not a reason to make every available feature equally prominent. [S5]

Specify a short attention sequence, such as choosing a ticket quantity, submitting the purchase, then finding help. Squint at the current screen or inspect a blurred rendering. If help, navigation, decoration, or a secondary button wins over the essential task, record that mismatch as the first problem to fix. [S5]

### 2. Acquire a specific visual technique

When you cannot design a particular element well, find a strong reference for that element. Identify what works in its spacing, letterforms, color relationships, or treatment of information. Do not borrow an interaction merely because a famous product uses it; check whether its affected object and context match this task. [S2][S5]

For learning, choose a reference slightly beyond current ability and recreate it closely enough to discover the small decisions you would otherwise miss. Compare the result with the original and name the discrepancies. The point is to expand visual vocabulary through observation, not to passively collect inspirational screenshots. [S6]

### 3. Make the layout work in grayscale

For a clean, simple application, build the screen using black, white, and gray before introducing theme colors. Establish sizes, spacing, and hierarchy without using color to hide weak structure. If the intended identity is strongly colorful, sporty, or cartoon-like, treat grayscale as a diagnostic aid rather than assuming it can settle the entire visual direction. [S1]

Increase breathing room when the screen feels like default, tightly packed HTML. Try substantially more space within controls, between lines, and between groups, then compare the versions. Kennedy's whitespace advice is a corrective to habitual crowding, not a requirement to double every existing measurement mechanically. [S1]

Align meaningful content edges and let the content determine useful widths. On a simple mobile screen, begin with left, center, and right guides; add structure when the content needs it. Avoid forcing every element into a column scheme merely to satisfy a grid, particularly across changing viewport sizes. [S10]

### 4. Put each control near its consequence

Map every action to the thing it changes. Put item actions on or near that item, and put actions for a whole region above that region. Apply the same logic recursively: a search over the entire application belongs at a broader level than a filter over one visible list. Conceptual objects, such as an account, can also anchor related actions. [S4]

Check the layout with a long list, not just the tidy sample. An add action at the list's end can become unreachable; consider an anchored control or the nearest logical location above the list. When reachability forces a control away from its consequence, increase its visibility and preserve a clear association with what it creates or changes. [S4][S5]

Reject the common shortcut of placing an action wherever spare space exists. A floating plus near the main content can suggest adding to that content even when it actually creates a sidebar object. Resolve that ambiguity through placement or explicit labeling before polishing the button. [S5][S8]

### 5. Choose controls from the user's choice structure

Before selecting a dropdown, compare alternatives. For a few mutually exclusive options, try segmented controls or radios; use cards when choices need richer descriptions. For many searchable options, consider typeahead. A checkbox suits an off/on setting applied on submission, while a switch suits an immediate change. [S5]

Distinguish near-future dates from dates spread across many years. A calendar can make likely appointment dates easy to choose, while direct entry can suit a birth date. Use steppers for small counts. Keep a dropdown when its few options, sensible default, and usage context make its extra interaction cost acceptable. [S5]

### 6. Tune typography with competing emphasis

Start with readable body text and a proven, clean font appropriate to the intended personality. Set headings far enough apart in visual weight that scanning distinguishes their roles, then reuse those roles consistently. Do not assume a mathematical type scale will rescue a weak screen or produce sensible multiline headings on mobile. [S2][S10]

For supporting text, balance attention-increasing properties against attention-reducing ones. A large number can have lighter weight; an uppercase label can be smaller and quieter. Reserve maximal emphasis for the main title rather than making every heading large, bold, high contrast, and uppercase. Keep useful secondary information findable. [S2]

Inspect interactive states for movement. Changing text size, case, or weight on hover can alter its footprint and make the interface jump. Prefer treatments such as color, background, underline, or shadow when they communicate the state without disrupting geometry. [S2]

### 7. Develop color variations rather than a palette collection

Introduce a purposeful theme color once the grayscale hierarchy works. Use HSB to derive related surface, text, accent, and state colors. For a darker variation, lower brightness and generally increase saturation; for a lighter one, increase brightness and generally reduce saturation. Adjust by eye rather than treating this as an exact formula. [S1][S3]

Avoid assuming that transparent black over a base color creates the desired darker variation: it reduces brightness without supplying the saturation change. Treat hue adjustment as secondary. Also remember that equal HSB brightness does not mean equal perceived lightness, so compare the actual colors and measure text contrast instead of trusting the numeric brightness setting. [S3][S7]

### 8. Solve component coherence on a small playing field

If the interface has inconsistent personality, isolate one representative component, such as a button with an inline icon. Match its font shapes, corner treatment, color connotations, and icon geometry to the same descriptive qualities. A rounded, friendly letterform suggests a different treatment from a squared, engineered one. [S7]

Match an inline icon's stroke weight and corner character to its neighboring text, then inspect it at actual display size. Tiny decorative details that disappear at that size are liabilities. Transfer the successful relationships to other components instead of copying the sample's exact numbers indiscriminately. [S7]

When using dimensional cues, keep a coherent overhead-light model: raised surfaces receive light above and cast shadow below, while inset surfaces behave differently. Keep the effect subtle. Tune shadow and border strength against the actual background; a black overlay that works on a light surface may disappear on a dark one. [S1][S7]

### 9. Add imagery and identity after the structure works

When text sits over an image, select a reliable treatment such as an overall dark overlay, a text backing, blur with sufficient tonal separation, or a fade beneath the text. Direct placement is fragile. Inspect every relevant crop and viewport, and repeat the check when either image or copy changes. [S2]

For a clean design that still lacks identity, develop one recurring motif from the brand's existing visual language. Echo it through suitable typography, dividers, decorative shapes, or special text details. A motif can also be a distinctive color treatment. Repetition across different forms creates cohesion; unrelated embellishments do not. Do not expect motifs to repair poor fundamentals. [S9]

If an unfamiliar feature requires lengthy explanation, show a concrete example of its use or output. Consider sample data in the initial experience or a small showcase of achievable results. Make the concept understandable through examples before relying on abstract descriptive copy. [S5]

### 10. Reframe stalled decisions and deliver the evidence

When every small adjustment remains unsatisfactory, write down the constants shared by the attempted solutions. Challenge a sensible assumption about form, position, or representation. A troublesome button may become a labeled action beside its object; related statistics may become a visual comparison. Check that the alternative still communicates the intended action rather than settling for cosmetic improvement. [S8]

Finish with the requested screen or implementation, an annotated explanation of its attention order and control placement, and the reusable typography, spacing, color, and component decisions it establishes. Include relevant states and viewport comparisons. Explain choices through observable relationships rather than claiming that a grid, palette name, or personal style makes them correct. [S4][S7][S10]

Report what the final squint check revealed, any measured contrast issues, and unresolved interpretation questions. If no rendered artifact was available, identify those checks as pending instead of asserting success. Treat remaining ambiguity as something to investigate with people using the interface, especially when reframing changes the meaning of a control. [S5][S7][S8]

## Worked example: invented illustration

A mobile workshop booking screen has a colorful banner, a dropdown for one to four seats, and equally strong Help and Reserve buttons. The agent ranks seat selection and reservation above assistance, quiets the banner in a grayscale draft, and compares roomier group spacing. [S1][S5]

The agent replaces the seat dropdown with a stepper, puts Reserve beneath the booking controls, and makes Help a quieter link. It derives a darker teal action color and pale teal surface through HSB adjustments, then measures the button's text contrast. The numeric values are chosen for this screen, not presented as Kennedy's universal tokens. [S3][S5][S7]

The delivery includes the revised screen, narrow and wide comparisons, button states, and a brief explanation of the attention sequence. If the workshop image carries text, the agent tests its backing treatment at both crops before declaring the design ready. [S2][S5]

## Sources

[S1] 7 Rules for Creating Gorgeous UI (2024 update)
https://www.learnui.design/blog/7-rules-for-creating-gorgeous-ui-part-1.html

[S2] 7 Rules for Creating Gorgeous UI, Part 2 (2024 update)
https://www.learnui.design/blog/7-rules-for-creating-gorgeous-ui-part-2.html

[S3] Color in UI Design: A (Practical) Framework
https://www.learnui.design/blog/color-in-ui-design-a-practical-framework.html

[S4] The 3 Laws of Locality
https://www.learnui.design/blog/the-3-laws-of-locality.html

[S5] 4 Rules for Intuitive UX
https://www.learnui.design/blog/4-rules-intuitive-ux.html

[S6] Copywork: The Ultimate Way to Rapidly Improve Your Design Skills
https://www.learnui.design/blog/copywork-ultimate-way-rapidly-improve-design-skills.html

[S7] The King vs. Pawn Game of UI Design
https://www.learnui.design/blog/king-vs-pawn-game-ui-design.html

[S8] The Reframe Technique
https://www.learnui.design/blog/the-reframe-technique.html

[S9] The #1 Way to Spice Up Your Designs (And Create a More Cohesive Brand)
https://www.learnui.design/blog/spice-up-designs-create-cohesive-brand.html

[S10] Why Beginning Designers Don't Need to Learn Grids, Type Scales, or Color Theory (and other Designer Dogma)
https://www.learnui.design/blog/why-beginning-designers-dont-need-grids-type-scales-color-theory.html
