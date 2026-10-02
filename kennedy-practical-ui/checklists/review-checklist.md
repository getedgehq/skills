# Review checklist

For each applicable row, record **Pass** or **Fail** plus evidence. Use **Pending** when the needed artifact or observation is unavailable, and **N/A** with a reason for an irrelevant check. Pending is not a pass. Fix failed items within the requested scope before delivery, or clearly disclose the unresolved limitation.

This review combines source heuristics with package delivery safeguards. It evaluates observable design decisions and does not claim to replace user testing or the project's accessibility requirements.

## Pass/fail gates

| Gate | Pass condition | Fail condition |
| --- | --- | --- |
| Task fit | The requested screen, critique, or practice output is delivered using actual task content. | A theory essay or unrelated redesign substitutes for the request. |
| Attention order | The rendered squint or blur result matches the declared task priorities. [S5] | Help, navigation, or decoration wins over the essential action. |
| Supporting information | Useful secondary text is findable and readable. [S2][S10] | Deemphasis hides information needed to act. |
| Layout | Meaningful edges align, content fits, and spacing distinguishes related items from separate groups. [S1][S10] | Crowding, arbitrary stretched widths, or excessive spacing obscures relationships. |
| Grayscale diagnostic | For a clean interface, structure works without color; colorful exceptions are explained. [S1] | Color masks unresolved layout or grayscale is treated as a universal style requirement. |
| Object locality | Each control clearly associates with the object it changes. [S4] | A floating or distant control appears to change a different object. |
| Regional locality | Regional controls sit above their scope or have a justified, intelligible exception. [S4] | Global, page, and item actions are mixed without clear scope. |
| Long-list reach | Creation and frequent actions remain reachable when the list grows; displaced controls remain visible. [S4][S5] | A required action disappears at the end of a long list. |
| Choice semantics | Controls match exclusivity, option count, likely values, and when changes apply. [S5] | Checkboxes imply multiple selection for a single choice, or a switch falsely implies immediate effect. |
| Dropdown rationale | A retained dropdown has an appropriate default, option count, and context. [S5] | A dropdown is the unexamined default for every choice. |
| Text roles | Body is readable, roles are distinct and reused, and emphasis is balanced. [S2][S10] | Every heading shouts or a mathematical scale causes unsuitable wrapping. |
| Interactive geometry | Hover or selection styling does not cause disruptive reflow. [S2] | Weight, size, or case changes make controls jump. |
| Color roles | Variations serve actual roles and are judged visually; contrast is measured on actual pairs. [S3][S7] | Palette names or HSB brightness numbers are treated as proof of readability. |
| Coherence | Representative components share deliberate corner, type, icon, border, and shadow relationships. [S1][S7] | Inline icons clash with text or depth cues contradict each other. |
| Image text | Text remains legible in every inspected crop and viewport with its chosen treatment. [S2] | Readability depends on a lucky image region or blur alone. |
| Motif, if present | A recurring brand idea supports a sound hierarchy across suitable elements. [S9] | Unrelated ornaments compete with the task or mask weak fundamentals. |
| Reframe, if used | The alternative improves communication while preserving meaning. [S8] | A newly styled action resembles selection, expansion, or another unintended behavior. |
| Teaching, if needed | A concrete example reveals what the unfamiliar capability does. [S5] | Abstract copy leaves the outcome unclear. |
| Delivery evidence | Relevant states and widths are inspected, contrast results are recorded, and pending checks are disclosed. | The report asserts checks that were never performed. |

The task-fit and delivery-evidence gates are package conventions. State, focus, touch, and responsive checks should follow the actual platform and requested scope.

## Common failure modes and fixes

| Failure mode | Fix |
| --- | --- |
| Polish before hierarchy | Return to the declared task order, compare a grayscale layout, then reintroduce color with a role. [S1][S5] |
| Mechanical whitespace doubling | Compare grouping, density, and usable content at actual size; choose gaps that clarify relationships. [S1] |
| Familiar pattern copied into the wrong context | Identify what the control changes, move it near that object, and label it if meaning remains ambiguous. [S4][S5][S8] |
| Every control made equally prominent | Reserve strongest emphasis for the core task and make secondary actions discoverable without competing. [S2][S5] |
| Dropdown ban applied indiscriminately | Reconsider defaults, option count, platform, and direct alternatives; keep the dropdown when it fits. [S5] |
| Dark variants made only with black overlays | Try lower brightness plus higher saturation, then inspect the actual role and contrast. [S3] |
| Rigid grid or scale used as justification | Explain alignment, content fit, and attention; adjust values while preserving useful consistency. [S10] |
| One shadow or border opacity copied everywhere | Retune against each surface's perceived lightness and inspect at actual size. [S7] |
| More decoration added to a weak design | Fix readability, spacing, hierarchy, and locality first; introduce a restrained recurring motif afterward. [S9] |
| Endless tweaks to the same unsatisfactory form | List fixed assumptions and compare a different position, form, or representation. [S8] |
| Specification mistaken for validation | Mark rendering and interaction checks pending and identify the concrete evidence needed. |
