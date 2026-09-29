---
name: clone-my-voice
description: Create a private local writing skill from a user's own representative writing samples. Use when the user asks an agent to learn or clone their voice for future DMs, posts, emails, or other writing.
---

# Clone My Voice

Turn the user's own writing into a reusable local `my-voice` skill. Keep samples and the generated profile on the user's machine by default. Do not upload samples to Edge, a model API, a repository, or another service. Use only samples the user supplies or explicitly points to. If none are available, ask for 5 to 10 representative pieces across the formats they care about.

If this agent uses a hosted model, reading raw samples into its tool output or conversation would upload them to that provider. Do not do that. Run `python3 scripts/analyze_samples.py <sample paths>` locally and reason from its aggregate output, which contains no sample text, names, paths, or excerpts. Put multilingual samples in separate language folders such as `en/dm/` and `de/dm/`, or analyze each language in a separate run with `--language en` or `--language de`. Do not combine unlabelled languages into one profile. Ask the user to name phrases they dislike; absence from samples does not establish a ban. A fully on-device agent may inspect raw samples directly. If no safe local processing path is available, explain the limit and ask for a user-written style summary instead of reading the files.

1. Analyze the user's sent writing, not incoming messages. Group it by format and language. Favor recent examples and explicit corrections. Use local aggregates or an on-device model to assess casing, sentence length, rhythm, hooks, vocabulary, punctuation, formatting, phrases the user rejects, and differences between DMs, posts, email, and other formats. Separate style from claims, private details, and one-off topics. Do not infer exact personal vocabulary or a banned phrase from aggregate counts alone; ask when needed.
2. Show a brief proposed profile with the strongest rules, per-format differences, and uncertainty. Ask the user to confirm or correct it before writing the skill. Do not retain raw messages or third-party details in the profile. Write 3 to 5 short, synthetic examples that illustrate the style without copying the samples.
3. Detect the active agent's local skills folder. Typical global folders are `~/.claude/skills/` for Claude Code and `~/.codex/skills/` for Codex; Cursor installations vary, so inspect its configured skill locations. Ask which folder to use if multiple agents or locations are plausible. Create `my-voice/SKILL.md` there with valid YAML frontmatter (`name: my-voice`, a discriminating `description`) and the confirmed profile, drafting rules, prohibited patterns, format rules, and examples. Keep the file private and local. If `my-voice` already exists, inspect it and ask before replacing the user's rules.
4. Verify the file exists, parse its frontmatter, and read it back for a content and privacy check. A validator, if available, can supplement this check. Confirm the target agent can discover the file using that agent's documented local-skill mechanism.

Finish with `✓ my-voice created locally` only after the file passes verification. Say `✓ Edge can now pick it for writing tasks` only if the installed Edge version actually discovers and ranks that local folder, demonstrated by a local synthetic test of `edge.find_skill`. Otherwise say that the host agent can use the local skill and explain the precise Edge integration still needed. Do not imply Edge saw or ranked the profile merely because the file exists.

## Synthetic before and after

Sample style rule: short lowercase messages, one idea per line, no greeting.

Before: “Hello! I hope you are doing well. I would be delighted to discuss this opportunity further.”

After: “sounds interesting\nwant to talk tomorrow?”

Both lines are invented for illustration. The generated `my-voice` should reflect the user's confirmed rules, not this example.
