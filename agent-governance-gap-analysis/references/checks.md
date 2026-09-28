# The 25 checks

Source: the Cakewalk AI Agent Governance Gap Analysis (cakewalk.security/gap-analysis).

Each check has an `id` (used in the scorecard template), the **statement** to read to the user verbatim, **means**, **a yes requires**, **partial if**, and **if no**.

**Three states, not two.** Met means full coverage. Partial means the control exists and operates but does not reach every agent, system or user — the "partial if" line on each check says what that looks like in practice. Neither partial nor unknown adds to the headline score; see `scoring.md`. Planned, piloted and budgeted are never partial.

---

## 01 — Agent Discovery · Agent Inventory and Visibility (4 checks)

Framing question: *Can you enumerate every agent, every user and every connection in one place?*

### inv1
**Statement:** We maintain a central registry of every AI agent in use across the org (Cursor, Claude, ChatGPT, Copilot and others).

**Means:** One place a person can open today and see every agent in use. Not a wiki page someone updated in March.

**A yes requires:** a live list, org-wide, covering agents employees brought in themselves — not just the ones procurement bought.

**Partial if:** a registry exists but covers only sanctioned or centrally-bought agents, or is maintained by hand and known to be behind.

**If no:** start with discovery, because nothing downstream works without it. Pull the list from what you already have: IdP OAuth grant logs (which third-party AI apps hold tokens against your Google/Microsoft tenant), SSO app inventory, expense reports for AI tooling, and endpoint software inventory. That gets you an 80% picture in a week. Then decide who owns keeping it current.

### inv2
**Statement:** New agent adoption is detected automatically. We do not rely on employees self-reporting when creating or using an agent.

**Means:** When someone connects a new agent to a company system on a Tuesday afternoon, you find out without them telling you.

**A yes requires:** an automated signal — OAuth grant monitoring, CASB/egress detection, or a gateway every agent must pass through. A quarterly survey is not detection.

**Partial if:** detection covers one channel only — say, IdP OAuth grants but not agents running locally or in CI.

**If no:** turn on OAuth app-grant alerting in your IdP first; it is usually free and catches most of it. Self-reporting fails not because people lie but because they don't think "I connected Claude to Notion" is an event worth reporting.

### inv3
**Statement:** For every agent, we know exactly which third-party apps and services it can access.

**Means:** For each agent, the list of systems it can reach and what it can do in each.

**A yes requires:** per-agent scope detail, not "it uses Google Workspace" — read-only vs full mailbox access is the difference between a nuisance and a breach.

**Partial if:** scopes are known for the managed agents, or known at integration level ('it uses Google') but not at permission level.

**If no:** inventory the connections per agent, then read the actual granted scopes rather than the marketing description of the integration. Most agent integrations request far more than the task needs.

### inv4
**Statement:** Each agent session ties to the employee who delegated it. We can trace any action back to a named user.

**Means:** When an agent does something, you can name the human responsible.

**A yes requires:** attribution at session level, for every agent, including anything running on a service account or shared key.

**Partial if:** attribution holds for most agents, but some run on shared or service identities.

**If no:** find the shared credentials first — they are where attribution goes to die. Any agent authenticating with a team-wide token produces actions no one owns.

---

## 02 — Credential Mediation · Credential Isolation (4 checks)

Framing question: *Do your agents hold real tokens? Could an attacker extract them?*

### cred1
**Statement:** Agents never hold real credentials (OAuth tokens, API keys, PATs) directly. If an agent's session is compromised, no usable credential can be extracted.

**Means:** The agent's memory, config and logs contain nothing an attacker could replay against your systems.

**A yes requires:** a broker or proxy that holds the real credential and exchanges it — the agent gets a short-lived, scoped handle at most. If the token is in the agent's environment, the answer is no.

**Partial if:** some agents go through a broker while others still hold tokens directly — commonly the older integrations.

**If no:** this is the highest-severity common gap, because an agent is a uniquely bad place to store a secret: it reads untrusted input (web pages, tickets, emails) and it has a context window that gets logged. Prompt injection turns a credential-holding agent into an exfiltration tool. Move to a credential broker or a gateway that injects auth server-side.

### cred2
**Statement:** Credentials are managed separately from the agent runtime. The agent never handles or stores the real token.

**Means:** Rotation, revocation and storage happen somewhere the agent cannot see.

**A yes requires:** separation in practice — a vault the agent reads from at startup is still the agent handling the token.

**Partial if:** credentials are centrally stored but the agent still loads the real value at runtime.

**If no:** the test is simple: can you revoke one agent's access to one app in under a minute, without touching the agent's machine? If not, credential management and agent runtime are the same system.

### cred3
**Statement:** Every agent's access traces back to one named employee. No agent operates under a shared or anonymous identity.

**Means:** No `ai-bot@company.com` with a permanent key that six teams use.

**A yes requires:** one human owner per agent identity, enforced, not just documented.

**Partial if:** most agents map to a named person, with a few shared identities left.

**If no:** shared identities break offboarding, audit and least privilege simultaneously. Split them per delegating user, even if that means more identities to manage.

### cred4
**Statement:** Agent access expires when the task ends. No credentials or permissions persist between sessions.

**Means:** Access is granted for the job and gone afterwards.

**A yes requires:** time- or task-bound access. A 90-day PAT is not expiry, it is a delay.

**Partial if:** credentials expire but on a long fixed cycle (30/60/90 days) rather than at task end.

**If no:** long-lived tokens are the reason a compromise from March is still exploitable in September. Move to short-lived, task-scoped grants.

---

## 03 — Policy Engine · Runtime Policy Enforcement (4 checks)

Framing question: *Does every tool call evaluate against a policy before it executes?*

### pol1
**Statement:** Every agent action evaluates against a written policy before it reaches the downstream app. No action runs unchecked.

**Means:** There is a checkpoint between the agent deciding and the system doing.

**A yes requires:** enforcement in the path, so it cannot be bypassed. A prompt telling the agent to be careful is not a policy — the agent is the thing you are trying to control.

**Partial if:** policy is enforced in one path — one gateway, one agent, one environment — while others reach systems directly.

**If no:** the only durable checkpoint is outside the model. Put a proxy or gateway in the call path and write policy there.

### pol2
**Statement:** Agent access approval and disapproval are taken based on defined policies.

**Means:** Whether an agent gets access is decided by a rule, not by whoever happens to be asked.

**A yes requires:** written rules applied consistently. If two identical requests can get different answers depending on who reviewed them, the answer is no.

**Partial if:** written rules exist for some decisions, with the rest left to whoever is asked.

**If no:** write down the decisions you are already making by instinct. That list is your first policy.

### pol3
**Statement:** Policies evaluate the full context (who is asking, which app, what action type) and produce a deterministic outcome. No probability scores, no ambiguity.

**Means:** Same inputs, same answer, every time.

**A yes requires:** deterministic evaluation. An LLM judging whether an action is risky is not deterministic, however good the prompt.

**Partial if:** evaluation is deterministic for most rules but a model or a human judgement call sits somewhere in the path.

**If no:** keep model judgement for triage and ranking; keep allow/deny in deterministic rules you can test and an auditor can read.

### pol4
**Statement:** When multiple rules apply to the same action, there is a clear hierarchy. Overlapping policies do not produce unpredictable results.

**Means:** Conflicts resolve the same way every time and you know which rule wins.

**A yes requires:** documented precedence — explicit deny beats allow, specific beats general, or whatever you chose, written down.

**Partial if:** precedence is understood by the people who wrote the rules but not written down or tested.

**If no:** conflicting rules fail open more often than they fail closed. Define precedence and add a test for the overlaps you can think of.

---

## 04 — Suspend-and-Resume · Human-in-the-Loop Controls (3 checks)

Framing question: *Can a human stop a sensitive action before it executes?*

### hitl1
**Statement:** When an agent attempts a sensitive action (creating records, sending messages, deleting data), it pauses and a human reviews before execution.

**Means:** Irreversible actions wait for a person.

**A yes requires:** the pause happens before the action lands, and it cannot be skipped by the agent. Notification after the fact is not review.

**Partial if:** some sensitive actions pause; the list is incomplete, or it covers writes but not external sends.

**If no:** define your irreversible set first — anything that sends to an external party, deletes, moves money, or changes access. Gate those; let reads flow.

### hitl2
**Statement:** Approval prompts appear where the user is already working. The reviewer does not need to switch to a separate app or dashboard to approve or deny.

**Means:** Approvals arrive in Slack, Teams, or the tool in hand.

**A yes requires:** approval in the flow of work. This is a control question, not a convenience one: a queue in a separate dashboard gets rubber-stamped or ignored, which means you have the cost of review without the benefit.

**Partial if:** approvals reach the user in their tools for some workflows, and a separate dashboard for the rest.

**If no:** move approvals to where the reviewer already is, and put enough context in the prompt to decide without opening anything else.

### hitl3
**Statement:** When an action is denied, it is fully blocked. The downstream app never receives the request.

**Means:** Deny means the request never arrives, not that it arrived and was logged as denied.

**A yes requires:** enforcement upstream of the target system.

**Partial if:** denial blocks in the enforced paths, but an agent with direct credentials could still reach the system another way.

**If no:** test it — deny something and check the target system's own logs for the request. Teams are often surprised.

---

## 05 — Dynamic Agent Context · Privilege Scope and Session Management (3 checks)

Framing question: *Do you apply least privilege to your agents?*

### priv1
**Statement:** Agents start every task with zero access. They do not inherit standing permissions from a prior task or a shared service account.

**Means:** No ambient authority sitting there between tasks.

**A yes requires:** access granted per task and dropped after. A broad token the agent always holds is standing privilege even if it is rarely used.

**Partial if:** tasks start clean for newer agents while others carry standing access.

**If no:** standing access is what makes a small compromise a large one. Grant on demand for the task at hand.

### priv2
**Statement:** Agent permissions are bound to the delegating user's identity. An agent acting on behalf of a marketing manager cannot access engineering repos.

**Means:** The agent can never do more than the human who asked.

**A yes requires:** the agent's effective permissions are the intersection of its scope and that user's entitlements — enforced, not assumed.

**Partial if:** agent permissions are bound to the delegating user for some systems, with broader service access elsewhere.

**If no:** privilege escalation via agent is the easiest unintentional escalation path most orgs have: the agent has broad access, so anyone who can prompt it inherits that access.

### priv3
**Statement:** Low-risk actions (reading data, searching) flow with minimal friction. High-risk actions (writing, deleting, sending externally) require additional approval or are blocked by default.

**Means:** Friction is proportional to risk.

**A yes requires:** a real distinction between read and write/send/delete in how the control behaves.

**Partial if:** read and write are distinguished for the main systems but not consistently across all of them.

**If no:** uniform friction is why controls get switched off. Classify actions by reversibility and blast radius, then spend your review budget on the ones that matter.

---

## 06 — HRIS/IdP Sync · Identity Lifecycle and Offboarding (3 checks)

Framing question: *When an employee leaves, do you revoke access automatically?*

### life1
**Statement:** Our HRIS or IdP is the source of truth for user records. Agent access inherits from it, not from a separate admin spreadsheet.

**Means:** One authoritative record of who works here, and agent access follows it.

**A yes requires:** agent access derived from that system, not maintained in parallel.

**Partial if:** the IdP is authoritative for humans, while agent access is still tracked separately in places.

**If no:** parallel lists drift within weeks. Pick the system that is already correct — payroll usually is, because people notice when it is wrong — and make agent access read from it.

### life2
**Statement:** When an employee is offboarded, their agent connections are revoked automatically on the next sync cycle. No manual cleanup required.

**Means:** Termination removes their agents' access without anyone remembering to.

**A yes requires:** automatic revocation of agent connections, not just the human's SSO session. Disabling the account does not touch a token the agent already holds.

**Partial if:** offboarding revokes agent access automatically for the managed agents, with manual cleanup needed for the rest.

**If no:** this is the gap that shows up in incident reports. Test it on your next leaver: 24 hours after offboarding, can their agent still reach anything?

### life3
**Statement:** When an employee changes role or department, their agent policies update to reflect the new attributes automatically.

**Means:** Movers, not just leavers.

**A yes requires:** attribute changes propagating to agent policy without a ticket.

**Partial if:** role changes trigger a review, but the policy update itself is manual.

**If no:** movers accumulate access; after a few internal moves an employee's agents can reach most of the company. Treat a department change as a re-evaluation, not an addition.

---

## 07 — Audit Log · Audit Trail and Compliance Readiness (4 checks)

Framing question: *Can you show an auditor exactly what every agent did, which policy fired and who approved?*

### aud1
**Statement:** Every agent action produces an immutable log entry recording what happened, who was behind it, which app was involved, which rule applied and what the outcome was.

**Means:** A tamper-evident record with all five facts, per action.

**A yes requires:** all five. Most logs have "what happened" and stop there — and the missing pieces are exactly the ones an auditor asks for.

**Partial if:** logs capture what happened but miss one or more of: who was behind it, which rule applied, what the outcome was.

**If no:** log at the enforcement point rather than in the agent, so the record does not depend on the component you are auditing.

### aud2
**Statement:** Audit events include request and response records so an auditor can reconstruct exactly what data the agent read or wrote.

**Means:** You can say which records were touched, not just that a call was made.

**A yes requires:** request/response capture, with the sensitive-field redaction that implies.

**Partial if:** request/response detail is captured for some systems, or captured without the redaction needed to keep it.

**If no:** without payload-level records you cannot scope an incident — you know an agent read from the CRM, not which customers' data left. Capture at the gateway, redact on write.

### aud3
**Statement:** Our audit trail maps every agent action to the human who delegated it, creating an unbroken chain from employee to agent to app.

**Means:** Employee → agent → app, unbroken, for every action.

**A yes requires:** no gaps where the chain lands on a service account.

**Partial if:** the chain holds except where it lands on a shared identity.

**If no:** every shared identity is a break in the chain. Fix attribution (see cred3) and this follows.

### aud4
**Statement:** We can filter audit events by user, agent, app, action type and outcome, then export for SIEM ingestion or compliance reporting.

**Means:** The logs are queryable and they leave the tool.

**A yes requires:** filtering on all five, plus export. Logs you can only read in a vendor UI do not survive an audit or an incident.

**Partial if:** events are filterable in the tool but not exported, or exported without the full set of filters.

**If no:** structured events and a SIEM pipe. If it is not in the SIEM, your detection team cannot see agent activity at all.
