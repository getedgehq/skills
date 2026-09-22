# Seed-stage engineering and open source go-to-market

Source: 1984 Ventures Founders Handbook, chapters "Engineering Best Practices at Seed
Stage" and "The Open Source Content Marketing Playbook: Lessons from Posthog", both by
Mark Percival (https://1984.vc/docs/founders-handbook/eng/best-practices-seed and
https://1984.vc/docs/founders-handbook/eng/open-source-playbook-posthog). This file is a
derived work; credit 1984 Ventures and the author, and do not present it as original.

## Engineering best practices at seed stage

The premise: the technical debt accumulated in the first 18 months determines whether
the company scales or spends its post-Series-A rewriting everything. Five practice
areas.

### 1. Testing is a competitive advantage

Testing lets you move faster, not slower. The right time to implement testing is at 2
engineers, not 20, because retrofitting tests onto an untested codebase is like adding a
foundation to a house that is already built.

You do not need 100% coverage on day one. Cover the code that would take the company
down if it broke:

- Payment processing flows
- User authentication and authorization
- Core business logic that drives revenue
- Data integrity checks (very hard to fix data later)

If you are backfilling tests, junior engineers should not write them; you or your most
senior engineers should. Practical rule: every new feature ships with tests, no
exceptions, and existing code gets tests when you touch it. You do not need over 90%
today, but you need forward progress each week.

### 2. Code reviews scale engineering knowledge

Do not make the CTO or lead engineer the bottleneck for every review; that stops scaling
past 3 engineers. Implement peer review from day one. Juniors will miss things, and they
will learn faster reviewing code than from any mentorship program.

The review process that works:

- Every PR reviewed within 4 hours during business hours.
- Reviews focus on business logic, not formatting (you should already be linting).
- Junior engineers review senior code too.
- Comments can ask questions or share learnings, e.g. "The API team is also using this
  endpoint"; they do not have to be critiques.
- PRs are not formally reviewed until ready to merge. Asking for feedback earlier is
  fine.

LGTM and a thumbs-up are not reviews. Find something to add to the conversation.

### 3. Engineering discipline that compounds

- Semantic commits: git history should tell a story. "fix bug" is not a commit message;
  "Fix: Payment webhook retry logic for failed Stripe events" is.
- Concise PRs with a single focus. Quick fixes bundled with feature work introduce bugs
  because reviewers cannot evaluate 1,500 lines of mixed changes.
- Automated checks: CI runs linting, type checking (if applicable), and tests. If any
  check fails, the PR does not merge. No exceptions, not even for the CEO.
- Changelog: automate most of it with semantic commits. Everyone in the company, not
  just engineers, should be able to review progress.

Setting the standard: engineers perform at the level you expect. Have your strongest
engineer model the practices religiously for the first 3 months. If nobody can set the
standard, your first hire should be someone who can. After 3 months, anyone who cannot
meet the standards should be let go.

### 4. AI is your force multiplier

Every engineer should have:

- An AI coding assistant (Cline, Cursor or Claude) with project-specific rules.
- A rules file updated weekly with architecture decisions, coding patterns, and company
  conventions.
- Documentation generation for all public APIs and complex functions.
- Test generation for routine cases; AI is great at edge cases, and AI-generated code
  tends to be verbose, which is perfect for tests.

AI does not replace engineers, it replaces engineering tedium. Engineers should solve
business problems, not write boilerplate.

### 5. Technical leaders, not managers

If the current team cannot implement these practices, you need different people; the
alternative is burning 18 months and $2M on a product that needs a ground-up rewrite.
The right person is a true believer in engineering best practices who can teach and
mentor, not just code. Avoid anyone who only wants heads-down tasks or complex
architecture problems; communication is critical. It does not need to be a CTO: a strong
senior engineer or engineering manager can reset the culture, but someone must own the
transformation.

### Common objections, and why they are wrong

- "We don't have time for this." You do not have time not to. Every month of delay makes
  the fix many times harder.
- "Customers don't care about our engineering practices." They care about bugs,
  downtime, and feature velocity, and practices drive all three.
- "We'll fix it after product-market fit." Companies that find PMF with bad engineering
  often cannot scale fast enough to capitalize on it.

### The other direction: process theater

The opposite trap, common in leaders from larger organizations: rigid metrics and
mandatory tooling instead of culture. Tests written to hit arbitrary coverage targets
build a culture of compliance, not excellence; the team stops asking "how do we build
the best product?" and starts asking "how do I get this pipeline to pass?". At seed
stage, every process should make engineers more effective, not more compliant. If you
are managing metrics instead of mentoring engineers, you are building the wrong culture.

### The 30-day implementation plan

For companies that reach Series A with few tests, a brittle codebase, and a burnt-out
team:

- Week 1: set up basic CI/CD with linting and type checking; implement PR review
  requirements; write tests for the most critical flow.
- Week 2: add semantic commit enforcement; set up AI coding assistants for all
  engineers; all new code comes with tests.
- Week 3: achieve 50% test coverage on critical paths; establish code review SLAs;
  create the first CHANGELOG (automated).
- Week 4: add AI code reviews to CI/CD to supplement human ones; run a retrospective on
  the new processes; adjust based on team feedback.

## Open source go-to-market: the PostHog content playbook

Discovery is the primary challenge for early to mid-stage open source startups. "If you
build it, they will come" does not work; even exceptional open source software needs
marketing. These lessons come from PostHog, one of 1984's best-performing open source
portfolio companies, via their head of content Andy Vandervell.

### Start with the "alternatives to X" list

The first piece of content should be "The X best open source [your product space]
tools". PostHog's most successful post ever is "The 12 best open source analytics
tools". It works because people actively search for alternatives, it positions you in
the market, it ranks well in search, and it is what developers actually read. List the
main players, be honest about strengths and weaknesses, and explain where your tool
fits. Examples: "The 12 best open source analytics tools", "The 9 best open source
feature flag tools", "PostHog alternatives".

### The conversion article: "Setup for X"

Forget long tutorials. Write short, targeted pieces showing how to set up your tool with
one specific technology:

1. Pick one technology (React, Nuxt, whatever).
2. Show the exact integration steps.
3. Keep it under 1,000 words.
4. Include the actual code.
5. Link to related setups at the bottom.

Structure: title "Using [Your Tool] with React", then prerequisites, installation with
code, basic setup with code, a quick test that shows it works, and links to related
setups.

The common pitfall is writing for an experienced developer who already understands your
product and stack. Many real users are just getting started with the framework, may be
juniors or stack-switchers, have limited domain understanding, and want quick solutions.
Meet developers where they are. Examples: "How to set up analytics in Nuxt", "How to set
up analytics in React Native".

### Comparison content: tables are king

People skim the article and zero in on the table. Embrace it. Make tables honest about
pros and cons, clear about pricing, specific about features, and easy to scan. Do not
try to win every comparison; acknowledge where competitors have an edge. Developers
detect marketing spin and FUD, and a balanced comparison converts better than a
promotional one. Examples: "PostHog vs Hotjar", "PostHog vs Amplitude", "PostHog vs
Matomo".

### What else works

- Write about problems you solve even when the search audience is small. A high-intent
  reader beats high traffic.
- Be authentic and transparent; PostHog includes a changelog at the top of comparison
  articles.
- Track what matters: where readers go next, whether they hit the docs, whether they
  sign up.
- Do not worry about posting cadence. Good content beats regular content.
- For social sharing: use personal accounts, not company ones; LinkedIn works better
  than Twitter; newsletter promotion often beats social.

### The reality check

SEO takes time; do not expect immediate payback. Early on, focus on sharing what you
learn and solving specific problems. The occasional Hacker News thought piece helps
hiring and investor relations, but your end user is not on Hacker News all day. They are
trying to solve a problem, so get your solution in front of them.
