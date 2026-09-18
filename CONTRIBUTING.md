# Contributing

GetEdge Skills welcomes community contributions. This guide describes how this repository manages issues and PRs, and how to contribute a Skill in a way that is likely to be accepted.

# Golden Rule

A Skill is instructions an agent will follow on somebody else's machine, so **you must understand what you contribute**. Use coding agents liberally, but you are in charge of demonstrating that understanding.

How to demonstrate it:

- Write your own PR description.
- Say what the Skill is for, and what an agent does badly without it.
- Document your design process, including the approaches you tried and the tradeoffs.
- Disclose which agents you used and to what extent.

# Communication

Code and Skill scripts can be written by agents. Docs, PR descriptions, issues and comments should be written by a human with AI assistance.

A general guideline for written communication: **you are in charge of the *first* draft and the *last* draft but can use agents in between**.

# Issues

The issues section is to report bugs in a Skill and to request new ones.

Please write the first and last draft of your issue description yourself, and feel free to use agents in between. You must understand the *problem* but do not need to propose a solution. Because implementation is easier than ever, an issue is often better than a PR.

# Contributing a Skill

A Skill is a folder at the repository root with a `SKILL.md` at its root: front matter naming the Skill and saying when to invoke it, then the instructions themselves, plus any scripts those instructions call.

Every new Skill ships with:

- `SKILL.md`, with front matter that passes `.github/scripts/frontmatter_gate.py`.
- `DERIVATION.json`, recording where the Skill came from, every file it ships and the SHA-256 of each. `.github/scripts/derivation_gate.py` fails the PR if a record drifts.
- A licence file, Apache-2.0 unless the Skill is a third party's own work published here unchanged.

## Measure it before you claim it

The distinctive thing about this repository is that a Skill is expected to be **measured** before it is adopted, not argued for. Where a Skill's benefit can be compared against the same agent without it, ship an `EVALS.md` alongside `SKILL.md` and put the session logs, grader verdicts and task definitions under [`evals/`](evals/).

Our bar is a 95% confidence interval on the judge point delta that excludes zero, fixed before the numbers are read. An `EVALS.md` says in its opening paragraph whether the result cleared the bar. A page that reports a result that did not clear it is welcome and will be merged. A Skill claiming a benefit with no page behind it will not.

[`skill-eval-loop`](skill-eval-loop) runs this comparison for you. Generic advice a capable agent already follows tends to tie with the baseline, so measure early.

# Interfaces and repository-wide changes

We are unlikely to change the repository layout, the gates or the derivation format without first discussing a design.

To open a design discussion, create a PR with an RFC. The RFC should be **concise** and written by a human with AI assistance. If an RFC is slop, we will close it. RFCs go in the `rfcs/` directory and follow the existing naming convention.

Integrations with a third party's tool or API are accepted when at least one *user* has asked for the integration, so please provide evidence of that, for example by having them leave a comment.
