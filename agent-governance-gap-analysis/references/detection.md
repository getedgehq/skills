# Read-only inspection playbook

Purpose: replace guesses with evidence on the checks that a machine can actually speak to. Roughly 8–12 of the 25.

## Run the script — do not hand-roll the scan

```
python3 scripts/scan.py                 # global agent settings
python3 scripts/scan.py --root <folder> # plus project configs beneath that folder
python3 scripts/scan.py --paths         # show what it would look at, first
python3 scripts/scan.py --all           # include suppressed placeholder values
python3 scripts/scan.py --selftest      # prove the redaction works, on fake secrets
```

`--selftest` plants known fake credentials, scans them, and asserts that not one — nor any 8-character fragment — reaches either output mode. Run it if a user asks how they can trust the scan, or before shipping any change to the script.

Use the script by default. It enforces the safety rules below in code rather than by intention — credential values are never placed in its output at all, only key name, kind, file, line and length — and its findings are the only thing that enters the conversation, instead of whole config files. It ends with per-check proposals for you to put to the user.

Reading config files by hand pulls their full contents, secrets included, into the conversation. Only do it if Python is unavailable or the script errors, and say so when you do.

Add `--include-history` only if the user agrees: it checks shell rc and history files for permission-bypass flags, which is useful evidence but a more personal file to open.

Interpreting the output:

- `!! SANDBOX SIGNALS` — stop. Confirm with the user whether this is really their computer before reporting anything (see `references/setup.md`).
- `NOT CHECKED` lines — say these out loud. An unreadable file is not a clean file.
- `pass?` on cred1 — means "nothing found in the files that were read", never "no credentials exist".
- **Suppressed placeholders** — the script ignores `.env.example`-style files and obvious dummy values, and reports how many it ignored. That count is not a finding; if a user asks what was skipped, `--all` lists it.
- **Held indirectly** — env-var references, keychain lookups and credential-helper settings such as `apiKeyHelper`. These are the *better* posture. Credit them; never report them as exposed credentials.
- **Connection-string and URL findings** name the scheme, host and parameter, never the credential — `postgresql://admin:<redacted>@prod-db.internal`. The host is the useful part: it tells the user which system an agent can reach.
- Everything under PROPOSED CHECK EVIDENCE is a proposal. The user confirms or corrects it; you do not score from it directly.

The rest of this file is the manual fallback, and the reasoning behind what the script looks for — read it when interpreting findings or when the script cannot run.

**Set the scan root before you start** — see `references/setup.md`. "The project" below means the project root the user named, not whatever directory the session happens to be in. If the root is the home directory, sweep the project-level files across the projects beneath it. If a global config path is unreachable, record it as **not checked** and say so in the findings; never let an unreadable file pass as a clean one.

## Safety rules — absolute

0. **Confirm this is the user's own computer, not a hosted sandbox.** On claude.ai and the API the skill runs in a container whose files belong to the sandbox, not the user. Reporting findings from it would be fabricated evidence. See `references/setup.md`; if unsure, ask, and fall back to questionnaire mode.
1. **Read-only.** No writes, no edits, no config changes, no revocations, no "let me just fix that for you". Report; the user acts.
2. **Never print a credential value.** Not partially, not the first four characters, not "for confirmation". Report shape and location only: `GITHUB_PAT (ghp_… , 40 chars) in ~/.cursor/mcp.json line 14`. If a secret value appears in a file you read, do not echo it in the conversation, the scorecard, or the plan.
3. **No third party receives anything.** No uploading config files, no sending findings to an API, no pasting contents into a web tool, nothing to Cakewalk. But do **not** claim "nothing leaves the machine" — what you read enters the conversation and is processed by the AI provider. See `references/data-handling.md` and be accurate about it. If the scorecard is published as a shareable page, it carries counts and check outcomes only — never file contents, hostnames, usernames, or redacted-but-identifiable secrets.
4. **Minimise what you ingest.** Confirm a secret exists without pulling its value into the conversation: match on key names and patterns, return paths, line numbers and counts rather than matched lines, and never dump a whole file you have already flagged as holding a credential.
5. **Only paths the user has granted.** Do not go hunting through the home directory beyond the specific config locations below. If a location is not accessible, record it as "not checked" and move on.
6. **Say what you did.** List the paths you looked at, before or after. No silent scanning.
7. **This is the user's own machine.** Never run this against someone else's files, a shared server, or a colleague's laptop.

## What to look for

### Agent and connection inventory → inv1, inv3, inv4

Enumerate configured agents and MCP servers/connectors from the locations that exist:

- Claude Code: `~/.claude.json`, `~/.claude/settings.json`, project `.mcp.json`, project `.claude/settings.json`
- Claude desktop app: `claude_desktop_config.json` in the app support directory
- Cursor: `~/.cursor/mcp.json`, project `.cursor/mcp.json`
- VS Code / Copilot: MCP entries in user and workspace settings JSON
- Other agent runtimes present: `.continue/`, `~/.codeium/`, `~/.aider*`, any `*mcp*.json` in the project

For each server found, record: name, transport (stdio / http / sse), the tools or scopes it exposes if declared, and the target system it reaches (GitHub, Slack, Notion, database, filesystem, browser).

Map to checks:

- **inv1** — met only if the user can point to an org-wide registry. A local list you built by scanning is evidence that no registry exists, not a substitute for one. Say this explicitly.
- **inv3** — compare the connections you found against what the user believed was connected. A mismatch is the finding.
- **inv4** — look for servers authenticating with a static token shared across a team (see below) versus per-user OAuth.

Also worth surfacing: filesystem servers with a broad root, shell/exec-capable servers, and browser-control servers. These have the widest blast radius and users routinely forget they are enabled.

### Credentials in agent reach → cred1, cred2, cred3, cred4

Search agent config files and any `.env` the project uses for credentials in four shapes — the script covers all four:

1. **Vendor formats:** `sk-`, `sk-ant-`, `ghp_`, `github_pat` + `_`, `gho_`, `xoxb-`, `xoxp-`, `AKIA`, `AIza`, `glpat-`, `sk_live_`, `Bearer `, `eyJ` (JWT), private-key blocks.
2. **Connection strings:** `scheme://user:password@host` — postgres, mysql, mongodb, redis, amqp, http(s). Easy to miss by eye and often the highest-value finding in the file, because it is usually a production database.
3. **URL query strings:** `?api_key=`, `?access_token=`, `?token=`, `?signature=`.
4. **Credential-named keys** holding a literal value: `*_TOKEN`, `*_KEY`, `*_SECRET`, `PASSWORD`, `CREDENTIAL`.

Skip example and template files (`.env.example`, `.env.sample`, `config.template.json`) — they exist to hold fake values, and reporting them buries the real findings.

Report count, key name, file, and line. **Never the value.**

Map to checks:

- **cred1 / cred2** — any raw long-lived credential sitting in an agent's env or config is a direct fail. This is the single most common finding and the one worth spending a minute on: explain that the agent reads untrusted content (web pages, tickets, issue text) into the same process that holds this token.
- **cred3** — a token whose name or scope implies a shared bot identity (`SLACK_BOT_TOKEN` used by the whole team, a service-account key) argues fail.
- **cred4** — PATs and static API keys are long-lived by construction. OAuth with refresh is better but still not task-bound. Ask what the actual expiry is; do not assume.

Note when a value is absent because the server uses a keychain or OS credential store — that is a meaningfully better posture, and worth crediting in the narrative even if the check still fails.

### Policy enforcement and approvals → pol1, pol3, hitl1, hitl3, priv1, priv3

Inspect permission and hook configuration:

- `permissions` blocks in `~/.claude/settings.json` and project `.claude/settings.json` — `allow`, `deny`, `ask` lists, and `defaultMode`
- `hooks` configuration, particularly `PreToolUse` hooks, and what they actually do
- `enableAllProjectMcpServers`, auto-approve or always-allow settings in any agent config
- Any use of permission-bypass flags in shell history, aliases, scripts, CI config, or launch wrappers — e.g. `--dangerously-skip-permissions`, `--yolo`, `bypassPermissions`, `--auto-approve`, `--no-confirm`
- Whether agent traffic goes through a gateway or proxy (a base-URL override pointing at an internal host is a good sign — ask about it)

Map to checks:

- **pol1** — a deny list plus a PreToolUse hook that can block is a partial in-path control; note that it governs this machine, not the org. Nothing in the path at all is a clear fail.
- **pol3** — deterministic rules present? A hook that asks a model whether to allow is not deterministic.
- **hitl1 / hitl3** — a permission prompt that blocks before execution is real human-in-the-loop. A bypass flag anywhere in regular use fails both, regardless of what the settings file says.
- **priv1 / priv3** — a broad `allow` list, or `defaultMode` set to accept everything, is standing privilege. Rules that distinguish reads from writes/sends/deletes argue toward priv3.

An important nuance to state out loud: local settings are per-machine and per-user. They are evidence of what one person's agent does, not of an org-wide control, unless the user confirms the settings are distributed and non-overridable.

### Logging and audit → aud1, aud2, aud4

Look for whether agent activity is captured anywhere durable: gateway or proxy configuration, OTel/logging exporters in agent config, a log directory the agent writes to, a SIEM forwarder on the machine. Local session transcripts on disk are not an audit trail — they are user-deletable, unstructured, and hold no policy decision. Say so.

Nothing on the machine can evidence aud3 or the HRIS/IdP dimension. Mark those "must ask".

## Cannot be detected — always ask

`inv2`, `pol2`, `pol4`, `hitl2`, `priv2`, `life1`, `life2`, `life3`, `aud3`, and any check where the finding was only about this one machine. Organisational process leaves no trace in a config file.

## Presenting findings

One table: **Finding · Evidence (path, no values) · Check · Argues for / against**. Then a one-paragraph summary of the top two risks. Then hand control back:

> These are proposals. Correct anything I got wrong before I score it — I can only see this machine.
