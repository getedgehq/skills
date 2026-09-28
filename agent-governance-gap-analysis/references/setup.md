# Setup: installing, read scope, and scoping the run

Where the skill is **installed** decides whether it loads. What the session can **read** decides how much can be evidenced — and that is set by the host and its working folder, not by where the skill sits. A globally installed skill in a session that sees one folder still sees one folder.

## Installing

The skill is a folder — `SKILL.md`, `references/`, `assets/` — that must stay intact. The `.skill` file is that folder zipped.

| Host | How | Scan possible? |
|---|---|---|
| **Claude Code** | Unzip into `~/.claude/skills/` → `~/.claude/skills/agent-governance-gap-analysis/SKILL.md`. A project's `.claude/skills/` scopes it to that project. | Yes — full |
| **Cowork** | Open the `.skill` file → *Save skill*. | Yes — connected folders only |
| **claude.ai** | Upload the `.zip` in Settings → Features. Needs Pro/Max/Team/Enterprise with code execution. Per-user; each colleague uploads their own copy. | **No** |
| **Claude API** | Upload via the Skills API (`/v1/skills`), used with the code execution tool. Workspace-wide. | **No** |
| **Team-wide** | Wrap in a plugin, serve from a marketplace. | Depends on host |

Skills do **not** sync across surfaces — a copy uploaded to claude.ai is not available in Claude Code or the API, and vice versa.

**Never install by pasting SKILL.md into a save-skill tool that takes only content** — that drops `references/` and `assets/`, leaving a skill pointing at documents that do not exist. It fails mid-assessment, confusingly. Install from the zip.

## Critical: are you looking at the user's own computer?

On claude.ai and the API, the skill runs in a **sandboxed container**, not on the user's computer. That container has a filesystem, and it may well contain agent settings files — belonging to the sandbox, not to the user.

**Scanning it and reporting the results would be worse than useless: it would be fabricated evidence about a machine that is not theirs.**

Before any scan, confirm you are on the user's own computer. If the session is a hosted container with no access to their real files, say so and run questionnaire mode:

> I'm running in a sandbox here rather than on your own computer, so there's nothing of yours for me to look at. We'll do this as questions — you'll still get the full score and plan.

If you cannot tell which you are in, ask. Never guess, and never report findings from a filesystem you cannot confirm belongs to the user.

## Licence

Apache-2.0. `LICENSE` and `NOTICE` ship in the bundle and must travel with any copy or fork — that is the one condition. If a user asks whether they may adapt it, put it in their own internal tooling, or hand it to a client: yes, including commercially, provided the licence and attribution notices stay with it.

## What each host can read

**Claude Code** — full filesystem, subject to permission prompts, following the launch directory.

- *Widest view: launch from the home directory* (`cd ~ && claude`). Everything lives under `~`: `~/.claude.json`, `~/.claude/settings.json`, `~/.cursor/mcp.json`, `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), VS Code user settings, plus every project's `.mcp.json` and `.claude/settings.json` beneath it.
- *Launched from a project* — that project plus global settings. Sibling projects are invisible and their agents go uncounted. Note it on the scorecard.

**Cowork** — sandboxed to connected folders plus outputs. **Cannot see `~/.claude.json` or any global agent settings unless the home folder has been connected.** If it is unreachable, say so and offer the choice: connect the home folder, or skip the scan and answer by hand.

**claude.ai, the API, Claude desktop/mobile** — no access to the user's own files. Questionnaire only; be explicit that nothing was verified. See the sandbox warning above.

## Scoping the run

Establish three things before scanning, and record them on the scorecard:

1. **Read scope** — what can actually be opened, confirmed rather than assumed.
2. **Scan root** — home folder, or a named project folder. Get the path; never assume the session's current folder is the one they mean.
3. **Assessment scope** — whole organisation, or their own setup. Governs the process checks no scan can answer: `inv2`, `pol2`, `pol4`, `hitl2`, `priv2`, `life1–3`, `aud3`.

Scan root and assessment scope are independent. Scanning one laptop while answering process checks for the org is a normal run — just label it: *"Global agent settings on one workstation; organisational controls self-reported."*

## Script: offering the scan

Reword naturally; do not paste.

> I can also look at your own setup and answer some checks with evidence instead of a guess: which AI tools and connections are configured, what they can reach, whether any keys are sitting in plain text, whether anything checks an action before it runs. Read-only — I change nothing — and no key value ever appears in the results.
>
> Straight about one thing, since this is a security assessment: what I read becomes part of our conversation, so it's processed by the AI provider like anything you'd type here. Nothing goes to Cakewalk or any other service. If you'd rather I open nothing, we can do this entirely as questions.

## Script: whole-organisation mode

> Worth setting expectations: I can't technically verify an organisation from here. A scan reads this computer only — not colleagues' laptops, not agents running in CI or on servers, not browser-based agents holding access with nothing stored locally. So all 25 checks get answered as questions about the organisation, and the score reflects what you tell me.
>
> I can still scan this machine alongside. It can't confirm anything org-wide — but it can contradict something. If you tell me no agent holds a raw key and I find one in your own settings, that's worth knowing before an auditor finds it.

Then hold to it: in org mode a scan **falsifies only**. A clean local result lifts no check. A contradiction gets named once — the statement, the finding, the file — and the answer stays the user's. Their laptop may genuinely be the exception; the point is they know first.

## The honest ceiling

Even a perfect home-folder scan covers **one machine, one user**. It cannot see colleagues' laptops, agents in CI or on servers, browser-based agents holding OAuth grants with nothing stored locally, or anything connected from a personal device.

So a scan can never positively evidence `inv1` (org-wide registry). It can only show that agents exist which the org never recorded — which is itself the finding.

Org-wide inventory comes from the IdP: OAuth app-grant logs showing which third-party AI applications hold live tokens against the tenant. Point users there when they ask for the real number. It is usually larger than they expect, and it makes the discovery dimension concrete faster than anything else.
