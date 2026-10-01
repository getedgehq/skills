---
name: clone-yourself
description: >-
  Build a private local "<your-name>-clone" skill that makes your AI work like you: your writing voice
  plus how you decide, judge work and report, learned from your own notes, agent memory and sent
  writing. Use when someone wants to clone themselves, make their AI think like them, or turn their
  working style into a reusable skill.
---

# Clone Yourself

Turn the user's own working style into a reusable local `<first-name>-clone` skill. A clone has two layers: **voice** (how they write) and **judgment** (how they decide, review and report). Keep everything on the user's machine. Do not upload samples, memory files or the generated profile to Edge, a repository or any other service.

## 1. Voice layer

Run the `clone-my-voice` workflow first, with its local-only rules, to produce or reuse the user's `my-voice` skill. The clone references it instead of duplicating it.

## 2. Judgment layer

Collect only sources the user owns and points to, in this order of strength:

1. Explicit rules the user wrote for their agents: `CLAUDE.md`, `AGENTS.md`, Cursor rules, saved agent memory or feedback files.
2. Corrections the user gave an agent ("no, do X instead"), when they choose to point at session logs.
3. Their own docs: decision logs, launch checklists, review notes.

Read them locally. If the agent uses a hosted model, ask the user before reading raw files into the conversation, and offer a written summary instead. Extract **rules, not facts**:

- how they decide (default to action or ask first, one recommendation or options, who gets a second opinion)
- how they judge work (evidence bar, what counts as boring or sloppy, what they always cut)
- how they report (length, outcome first, what they never want to hear)
- hard bans (words, formats, behaviours they corrected more than once)

Drop names, clients, money, credentials, health, locations and anything about third parties. A rule that only makes sense with a private fact attached gets cut.

## 3. Confirm, then write

Show a short proposed profile: about 10 rules grouped as decide / judge / report / bans, each tagged with where it came from (file name only, no quotes). Ask the user to confirm or edit. Then create `<first-name>-clone/SKILL.md` in the agent's local skills folder (`~/.claude/skills/`, `~/.codex/skills/`, or the configured Cursor location; ask if unclear). Use this description shape:

`Work like <first name> on <their real task types>: decide, review and write the way they do. Use when the user asks for <first name>'s take, a second opinion in their style, or says "be <first name>".`

The body holds: a one-line identity, "also follow `my-voice` for writing", the confirmed rules, and one short synthetic example that shows a decision in their style.

## 4. Verify

Check the file exists, the frontmatter parses, and the body contains no names, numbers or quotes from the sources. Then test it with three prompts the user picks, and show the answers side by side with a no-skill answer so the user can see the difference.

Finish with:

`✓ <first-name>-clone created locally. Your AI can now work like you. Turn on Edge local ranking (EDGE_LOCAL_SKILLS=1) and Edge offers it whenever a task needs your judgment.`
