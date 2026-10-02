# Worked examples

Both scenarios are invented illustrations. Measurements, copy, and token values below belong to these examples; they are not Kennedy's prescribed defaults. The text specifications illustrate a deliverable without claiming that a rendered interface or user test was performed.

## Illustration 1: Mobile workshop booking

### Brief and constraints

Design a booking screen for a pottery workshop. The user needs to confirm the date, choose one to four seats, see the total, and reserve. Keep the existing teal brand and workshop photograph. The workshop has one available date and costs EUR 45 per seat. Deliver a screen specification rather than production code.

Assumed attention order: booking details and seat quantity, total and Reserve action, then Help. Seat choice and reservation are expected on most visits; assistance is occasional. Frequency supports that ranking but does not justify concealing the price. [S5]

### Weak first draft

```text
[Large bright photograph with white title directly on it]
POTTERY NIGHT

Seats: [dropdown showing 1]
Date: 18 October, 18:00
EUR 45

[Large blue HELP] [Gray Find Options]
```

The photograph dominates before the task is clear. The dropdown hides a small set of counts. The bright Help button appears more important than the gray submission control, whose label does not describe reserving. White title text depends on a favorable image crop. Tight gaps merge details and controls into one block. [S1][S2][S5]

### Applying the method

1. Draft in grayscale. Reduce the photograph to a supporting image and separate the booking details, quantity, and submission group. Compare clearly roomier spacing rather than using color to cover the cramped layout. [S1]
2. Replace the seat dropdown with a labeled stepper. Put the total immediately after quantity so the consequence of changing the count is nearby. [S4][S5]
3. Make Reserve the dominant action and Help a quieter link. Use sentence case for body content; give the workshop title stronger weight without also making every label bold and uppercase. [S2][S5]
4. Derive a dark teal button and pale teal surface rather than adding unrelated accent hues. Verify contrast on the actual colors. [S3][S7]
5. Keep the title outside the photograph. If a future variant requires image text, introduce a backing and test every crop. [S2]

### Improved result

```text
Pottery night
18 October at 18:00
[Supporting workshop photograph]

Seats
[Minus]  1  [Plus]
EUR 45 per seat

Total                              EUR 45
[             Reserve 1 seat             ]
Need help with your booking?
```

Example specification:

- Content starts on a shared left edge with 20 px outer padding. Related seat content uses 8 px gaps; the major booking groups use 24 px separation. These values are starting choices to inspect, not a formula. [S1][S10]
- Body text starts at 16 px; the title starts at 26 px with a heavier weight. Supporting price text retains readability while receiving less emphasis than the total. [S2][S10]
- Reserve uses background `#00695C` and white text. Its nominal sRGB contrast is approximately 6.6:1, calculated for this illustration. A pale teal surface can support secondary grouping; the final implementation must check every text pairing separately. [S3][S7]
- At one seat, Minus is disabled; at four seats, Plus is disabled. A change to two seats updates the total to EUR 90 and the action to Reserve 2 seats. These state requirements are package implementation guidance.
- During reservation, show progress and prevent repeated submission. On failure, preserve the count and put the error near the action. On success, show a confirmation appropriate to the actual booking flow.

### What made the difference

Task-based hierarchy reverses the Help versus Reserve emphasis. A stepper makes a small count easier to change. Local placement connects quantity and total. Group spacing establishes structure before color. Keeping text outside the photograph removes crop-dependent readability. [S1][S2][S4][S5]

Review status: specification complete; narrow and wide rendering, focus behavior, disabled styling, and image cropping remain pending. The nominal button contrast calculation does not validate all rendered states.

## Illustration 2: Desktop automation workspace

### Brief and constraints

Improve an automation dashboard with a sidebar of projects and a main list of rules. Users create projects occasionally, create rules frequently, and inspect recent run counts. The workspace has a restrained brand with a small bracket shape in its logo. Keep its component library and deliver an annotated redesign specification.

### Weak first draft

```text
[Logo]  Projects          [Global search]
Project Alpha            RUN SUMMARY
Project Beta             TOTAL 120  SUCCESS 108  FAIL 12
Project Gamma            [Rule search hidden in menu]
                         Rule A   ...
                         Rule B   ...
                                            [floating +]
```

The floating plus creates a project but sits over the rule list, implying a rule action. A long project list would hide an add link placed only at its end. The run statistics repeat numbers without making their relationship clear. Uppercase heavy summary labels compete with the rule task. A blank new project explains automation through generic copy rather than showing an example. [S2][S4][S5][S8]

### Applying the method

1. Map the two creation actions to different objects. Put New project beside the Projects heading and New rule above the rule list. Keep application search above both regions and list filtering directly above the rule list. [S4]
2. Retain the existing spacing tokens but apply them consistently to headings, rows, and regional boundaries. Judge alignment and content fit rather than imposing a new column count. [S10]
3. Reframe the statistics as a success versus failure comparison. Preserve exact counts in adjacent text so the visual summary supplements the numbers. [S8]
4. Refine the New rule button as a small component. Match the inline plus icon's stroke and corners to the label and button. Keep hover geometry stable. [S2][S7]
5. Add one labeled sample rule in a new project's empty state. Show trigger and outcome concretely. [S5]
6. Echo the existing bracket motif in a noninteractive section divider and the sample card's edge detail. Keep the dominant action stronger than the motif. [S9]

### Improved result

```text
[Logo]                      [Search workspace]

Projects [New project]      Project Alpha
Project Alpha               Rules [New rule]
Project Beta                [Filter rules]
Project Gamma               Rule A  [Run] [More]
...                         Rule B  [Run] [More]
                            Recent runs: 120 total
                            [108 successful | 12 failed]
                            108 successful, 12 failed
```

Empty-state variant:

```text
No rules yet
Example: When a CSV arrives, notify the review team.
[Sample rule preview]  [Create your first rule]
```

The project action remains visible above the scrollable sidebar. Rule actions sit on the relevant rows, and regional creation remains above the rule list. The sample preview is explicitly illustrative and does not suggest that an automation is already active. [S4][S5]

For the run comparison, use a labeled proportion bar with a 90 percent successful portion and a 10 percent failed portion. Do not rely on color alone; retain labels and counts. The chart choice illustrates Kennedy's reframe principle, while the labeling safeguard is package guidance. [S8]

### What made the difference

Locality resolves the meaning of the plus by separating project creation from rule creation. Reframing makes the relationship among three counts apparent. Stable text styling and matched icon geometry improve component coherence. The sample rule teaches the unfamiliar feature, while a restrained motif adds identity after the hierarchy works. [S2][S4][S5][S7][S8][S9]

Review status: placements and copy specified; rendered squint test, long-list scrolling, touch alternatives to hover, keyboard navigation, contrast, and narrower layouts remain pending. Test whether people distinguish New project from New rule before claiming the ambiguity is resolved in use.
