# Second brain

Shared by every role on the team. Private repo. Pull before work, commit and push after writing.

| Path | What goes there | Who writes |
| --- | --- | --- |
| `MEMORY.md` | One line per memory, newest first, linking to `memory/`. Keep it under 150 lines. | Any role |
| `memory/` | One file per durable fact: `feedback_*` (corrections from the human), `project_*`, `person_*`, `decision_*` | Any role |
| `notes/` | Research, meeting notes, longer drafts worth keeping | Any role |
| `projects/<name>/` | `BRIEF.md`, `DECISIONS.md` and what the team produces for that project | Owner of the project card |
| `board/BOARD.md` | The board | Chief of Staff moves cards; owners add notes |
| `team/` | One prompt per role, plus `REVIEW.md` | The human, or the Chief of Staff with the human's OK |
| `skills/` | The team's own skills, one folder each with a SKILL.md | Any role, reviewed like any other output |

A memory file:

```markdown
---
name: <short title>
type: feedback | project | person | decision
date: <YYYY-MM-DD>
---
<The fact in one or two sentences. Why it matters. Where it came from.>
```

Never store keys, tokens or passwords here.
