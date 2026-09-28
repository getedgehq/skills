# What happens to the data this skill reads

Answer this accurately whenever a user asks, and volunteer it before scanning anyone who looks like a security buyer. Overclaiming here destroys the credibility of everything else in the assessment.

## The honest version

**"Nothing leaves your machine" is not true, and must never be said.**

This skill runs inside an AI assistant. Anything the assistant reads becomes part of the conversation, and conversations are processed by the AI provider's servers. A file opened during the scan is transmitted for inference exactly like text pasted into the chat. Local file access does not mean local processing.

What is accurate:

| Claim | True? |
|---|---|
| Nothing is sent to Cakewalk | **Yes.** The skill makes no network calls. It is instructions and templates, nothing else. |
| No third-party service receives the findings | **Yes.** No API calls, no telemetry, no uploads. |
| Nothing is modified, deleted or revoked | **Yes.** Read-only throughout. |
| File contents stay on the machine | **No.** What the assistant reads is processed by the AI provider, under whatever terms and retention policy governs the user's account. |
| Credential values never reach the model | **No — but exposure is minimised.** See below. |
| Credential values never appear in outputs | **Yes.** No secret value goes into the transcript, the scorecard, or the plan. |

## Minimising what gets ingested

`scripts/scan.py` exists for this reason. It reads config files inside its own process and emits only findings — key name, credential kind, file, line number, value length. **No credential value is placed in its output at all**, so no secret value enters the conversation, the model's context, or anything the provider processes. Secrets found inside URLs are replaced with `<redacted>` before the URL is printed.

That is a control, not a promise. It holds because the value is never written to the result structure, not because the assistant chose well. Specifically: a credential's name is read only from the text *preceding* the located secret, so it cannot return the secret itself; and URLs are rebuilt from their parsed parts with every query value and password dropped, rather than pattern-matched against a list of known vendors — so an unfamiliar vendor's key is dropped too.

`python3 scripts/scan.py --selftest` demonstrates this on planted fake credentials: it asserts that no secret, and no 8-character fragment of one, reaches either output mode. Offer to run it for anyone who wants the guarantee shown rather than stated.

So: **run the script.** Reading config files directly defeats the whole mechanism — the file contents, secrets included, land in context exactly as if pasted. Hand-reading is the fallback for when Python is unavailable, and it should be named as a downgrade when it happens.

What still enters the conversation when the script runs: file paths, agent and connection names, environment-variable key names, permission rule counts, and the findings above. Enough to identify the user's tooling, not enough to authenticate as them.

If asked whether this is airtight: no. The script reduces exposure sharply and removes the credential values specifically, but paths and tool names still describe their setup. Say that rather than overselling it.

## If the user is not comfortable with that

Reasonable position, especially for a regulated org or a security team assessing a vendor. Offer alternatives without arguing:

1. **Questionnaire only.** All 25 checks answered as questions. No files opened. Works everywhere, loses the evidence, keeps the assessment.
2. **User-run.** They run the checks themselves — the pattern list in `detection.md` is not secret — and tell you the results. They see the output before anything reaches the conversation.
3. **A scratch account or non-production machine**, if they want to see how the scan behaves before pointing it at anything real.

Never pressure someone into the scan. A user who declines and completes the questionnaire is a good outcome; a user who feels a security tool was evasive about its own data handling is a lost one.

## Where outputs go

- **Scorecard and plan** are files written where the user chooses. They contain scores, check outcomes, gap descriptions and fixes — no file contents, no credential values, no usernames or hostnames.
- **Publishing the scorecard as a shareable link uploads it.** That is a deliberate egress to a hosted page. Ask before publishing, every time, and make sure the user understands the page is reachable by anyone holding the link once shared. If the assessment surfaced anything sensitive, offer the local file instead and let them decide.
