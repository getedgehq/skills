---
name: cv-job-match
description: Turn a CV into a shortlist of live startup roles from Rocketlist's public job board, including adjacent job titles the person would never have searched for, each with its published salary, the evidence for the fit, and a direct apply link. Use for "find roles I would be a strong fit for", career pivots, remote or VC-backed job hunts, and salary-visible role discovery.
---

# Match Your CV to Startup Jobs

Read a CV once, work out what the person can actually do, then find the live postings that
match, including the ones filed under a title they have never typed into a search box.

## The surface you are working with

Rocketlist has no public JSON API. Its `robots.txt` disallows `/api/` for every agent, so
this skill works over the public web pages, which need no account and no credential.

- Search: `https://rocketlist.ai/jobs?q=<terms>`, plus `city`, `seniority`, `category`,
  `industry`, `stage`, `founded`, `funding`, `investor`, `sort`, `page`. **The result list
  renders in the browser**, so fetch this URL with something that executes JavaScript. A
  plain GET of a filtered search returns an empty list, not an error.
- Job detail: `https://rocketlist.ai/jobs/<slug>`. Server rendered, so a plain GET works.
  Carries the published salary, the required and nice-to-have skills, and `job_url`, the
  direct link to the employer's own ATS posting.
- Job sitemaps: about 91,000 live job URLs whose slugs contain the company and the title.
  A free offline index for testing whether a title exists before searching it.

Exact parameters, taxonomies, parsing recipes and gotchas: [references/search-surface.md](references/search-surface.md).

Rocketlist also documents a public, token-free MCP connector at `https://rocketlist.ai/mcp`
with `search_jobs`, `get_job`, `search_companies` and `get_company`. It was returning
HTTP 502 on 2026-09-15. Send one `initialize` call; if it answers, use it, because its
`search_jobs` takes remote status and skills that the URL cannot express. On any non-200,
fall back to the pages and do not retry.

## Workflow

1. **Read the CV into capabilities.** Verbs, objects, counterparties, tools, domain, scope,
   and the constraints the person stated: location, remote, seniority, salary floor,
   industries they will not go back to. Ask only for a constraint you genuinely need.

2. **Expand into fifteen to twenty-five candidate titles** along the five axes in
   [references/title-expansion.md](references/title-expansion.md). Keep both the titles the
   person would have searched and the ones they would not, tagged so you can separate them
   later. Record the CV evidence behind each one.

3. **Kill the invented titles before you spend a search on them.**

   ```
   python3 scripts/rocketlist_job.py scan --pattern "forward deployed" --pattern "deployment strategist"
   ```

   This greps the job sitemaps and prints a live posting count per title. Zero means the
   title does not exist on this board. Drop it silently.

4. **Search each surviving title separately.** One title per `q`, widest first. `q` is free
   text over the description as well as the title, so long compound queries collapse to
   nothing. Add `city`, `seniority` or `investor` only when a bare title returns too much.
   Remote status is not a URL parameter; read it off each card or put `remote` in `q`.

   Capture from each result card: title, company, location, salary range, one-line summary,
   tech stack, and the `/jobs/<id>` link. Ignore "Match score locked", there is no score for
   a signed-out visitor.

5. **Open the detail page for every role you intend to shortlist.**

   ```
   python3 scripts/rocketlist_job.py job <slug-or-url>
   ```

   This prints the structured record: `job_salary_range`, `job_required_skills`,
   `job_nice_to_have_skills`, `job_experience_required`, `job_seniority`,
   `job_location_type`, company stage, investors, and `job_url`. Check the requirements
   against the CV here. A title that sounded right and asks for eight years of a skill the
   person does not have is not a fit; cut it.

6. **Rank.** Dedupe on `job_url`, since the same role can surface under several titles.
   Then order by how much of the CV the posting's required skills are covered by, whether
   the stated experience band contains the person's, whether the location and remote status
   satisfy their constraint, and whether the salary clears their floor. Do not weight by how
   exciting the company is.

7. **Present the shortlist.** Eight to fifteen roles, in two labelled groups:

   - **Roles you would have found yourself**, the titles matching their current one.
   - **Roles you would not have searched for**, the expansion. This is the part that earns
     the skill. For each of these, name the title, and say in one sentence which part of
     their CV maps onto it.

   One row per role:

   | Field | Content |
   | --- | --- |
   | Title and company | plus company stage and lead investors when notable |
   | Location | Remote, Hybrid, On-site, or the city |
   | Salary | the published range verbatim, or "not published" |
   | Why you fit | the specific CV evidence, not adjectives |
   | Gap | the requirement they do not meet, stated plainly |
   | Apply | the `job_url` from the record, the employer's own posting |

   Close with the titles you tested that turned out to be dead ends and why, so they can
   steer the next pass.

## Boundaries

- Rocketlist aggregates public postings; it is not the employer and the listing can be
  stale. Send the person to `job_url` and tell them to confirm the details there.
- Salary is published only when the employer published it. Many records read
  "Not specified". Write "not published" and never estimate a range, infer one from a
  similar role, or present a market average as this role's salary.
- Stay on the public pages. Do not call `/api/`, do not create an account, do not sign in,
  and do not use a signed-in or admin surface even if one is available to you.
- Every role in the output must be a posting you actually retrieved. Never fill a thin
  shortlist with a plausible role, a company you assume is hiring, or a title you did not
  verify against the index.
- The site's own counters, currently about 98,800 active jobs across about 4,860 companies,
  are Rocketlist's numbers. Quote them as such or leave them out.
- A "Gap" line is not optional. A shortlist with no gaps anywhere is a shortlist that was
  not checked against the postings.
