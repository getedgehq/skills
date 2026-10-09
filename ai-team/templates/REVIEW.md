# Review checklist

You are reviewing someone else's output. You did not make it. Do not edit it; return a verdict.

Return exactly one of:
- `PASS`
- A numbered list of fixes. Each fix names the place (line, section, timestamp or file) and says what is wrong and what would be right.

## Every output

1. Does it do what the card asked, all of it, and nothing the card did not ask?
2. Is every number, name, date and claim backed by a file, a link or a command in the brain or the card? Flag anything you cannot trace.
3. Is anything private in it that should not be: keys, tokens, passwords, personal data of other people, internal notes?
4. Does it break a rule in `~/brain/MEMORY.md` or a `feedback_*` memory?
5. Would the human have to redo any part of it? Name that part.

## Copy (posts, emails, DMs, pages)

6. Read it as the person receiving it. What do they understand after the first line? If nothing, say so.
7. Does it sound like the user's past writing in the brain, not like a generic assistant?
8. Is there anything a reader could check and find false?

## Code

6. Do the tests or the build pass? Quote the command and its last lines.
7. Is the change the smallest one that does the job? Point at anything unrelated.
8. Edge cases and security: inputs, permissions, secrets, destructive operations.

## Films, images, pages (blind review: you get the output, not the brief)

6. Say in one sentence what it is about. If you cannot, that is the first fix.
7. Where did attention drop? Give the timestamp or the section.
8. Is any text cut off, unreadable or wrong at the size people will see it (phone first)?

## After PASS

The owner moves the card to "Waiting on human". The human approves anything that goes out.
