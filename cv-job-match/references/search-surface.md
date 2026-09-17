# The public Rocketlist surface

Verified against the live site on 2026-09-15. Everything here is reachable without an
account. Nothing here needs a credential.

## There is no public JSON API

`https://rocketlist.ai/robots.txt` disallows `/api/` for every user agent, including
GPTBot, ClaudeBot, PerplexityBot and CCBot. The search page calls internal `/api/`
routes from the browser; do not call them directly. This skill works over the public
pages that robots.txt allows.

## Search page

```
https://rocketlist.ai/jobs?q=<terms>
```

Confirmed as the canonical search URL by the site's own schema.org `SearchAction`:
`urlTemplate: https://rocketlist.ai/jobs?q={search_term_string}`.

**This page renders results client side.** A plain HTTP GET returns HTML whose embedded
state is `"initialBrowseJobs":[]` and `"initialBrowseTotalCount":0` whenever `q` or any
filter is set. Fetch it with something that executes JavaScript and waits for the result
list. A plain GET of `/jobs` with no parameters does server render the first page, which
is useful only for smoke testing the parse.

A rendered result page reads like this, and this is the text to parse:

```
Jobs
41 results of 98,856 total jobs
Staff Enterprise Developer Advocate
LaunchDarkly - United States - $145,500 - $235,400
Build and lead an education-first technical session program for enterprise clients.
Python JavaScript TypeScript
```

`Match score locked. Sign in to view.` appears on every card. There is no match score for
a signed-out visitor, so never report one.

### Query parameters that work

Each was set and read back out of the page's own filter state.

| Parameter | Multi-value | Notes |
| --- | --- | --- |
| `q` | no | Free text. Matches titles and description text, not just the title. |
| `city` | comma separated | `city=Berlin,London`. Repeating the key keeps only the first value. |
| `seniority` | comma separated | `Intern, Junior, Mid, Senior, Lead, Manager, Director, Staff` |
| `category` | comma separated | Fixed taxonomy, see below |
| `industry` | comma separated | Fixed taxonomy, see below |
| `stage` | comma separated | `Seed, Pre-Seed, Pre-Series A, Series A` through `Series H`, `Growth`, `Public`, `Acquired`, `Bootstrapped`, `Early Stage`, `Private`, `Seed VC`, `Unfunded` |
| `founded` | comma separated | `2020-2026, 2015-2019, 2010-2014, Before 2010` |
| `funding` | comma separated | `< $1M, $1M-$10M, $10M-$50M, $50M-$100M, > $100M` |
| `investor` | comma separated | Exact fund name, see below |
| `sort` | no | `date` is the default. `salary` is accepted. `relevance` is silently ignored and falls back to `date`. |
| `page` | no | 1 based |

Values are passed through without validation, so a value outside the taxonomy is accepted
and quietly matches nothing. Spell values exactly as listed, including capitalisation.

Remote status is **not** addressable from the URL. It lives in a separate `toggles` field
that URL parameters do not reach. Filter remote roles by reading the location line on each
card, which is one of `Remote`, `Hybrid`, `On-site` or a city, or by putting `remote` in `q`.

### Taxonomies

`category`: Data & AI, Design, Finance, Leadership & General Management, Legal &
Compliance, Marketing, Operations & Strategy, Other Engineering, People / HR /
Recruitment, Product, Sales & Account Management, Software Engineering, No Match.

`industry` includes: AdTech, Aerospace, AgriTech, AI & ML, Automotive, BioTech,
Blockchain, CleanTech, Consumer Electronics, Cybersecurity, Data & Analytics, DeepTech,
Developer Tools, E-Commerce, EdTech, Energy, Enterprise Software, Entertainment,
Financial Services, FinTech, FoodTech, Gaming, GreenTech and more. Read the live list
rather than assuming, see "Reading the taxonomies live" below.

`investor` is a fixed list of 60 funds. It includes `Y Combinator`, `Sequoia Capital`,
`Andreessen Horowitz`, `Accel`, `Benchmark`, `Founders Fund`, `Greylock`,
`Kleiner Perkins`, `Index Ventures`, `Khosla Ventures`, `General Catalyst`,
`Union Square Ventures`, `Techstars`, `Atomico`, `Balderton Capital`, `Creandum`,
`Speedinvest`, `Cherry Ventures`, `EQT Ventures`, `500 Global` and `SoftBank Vision Fund 2`.
Only these 60 are filterable. A company's full investor list, which is longer, is on the
job detail record.

### Reading the taxonomies live

The unfiltered `/jobs` page server renders every filter option list, so one plain GET
gives you the current vocabulary:

```
curl -s https://rocketlist.ai/jobs | grep -o 'seniorityOptions.\{0,400\}'
```

The same blob carries `cityOptions`, `categoryOptions`, `industryOptions`, `stageOptions`,
`foundedYearOptions`, `fundingOptions` and `investorOptions`.

## Job detail page

```
https://rocketlist.ai/jobs/<slug>
https://rocketlist.ai/jobs/<uuid>
```

Both forms resolve. This page **is** server rendered, so a plain GET is enough. Drop any
`?next=` suffix; robots.txt disallows it and it is the same document.

It carries two things worth parsing.

1. A `<script type="application/ld+json">` block of type `JobPosting` with `title` and the
   full HTML `description`.
2. A flat record embedded in the page state with these fields:

```
job_title_original      the title as the employer wrote it
company                 display name
company_vertical_primary
company_stage           Series A, Seed, ...
company_founded_year
company_total_raised_usd
job_city_primary
job_country_primary
job_location_type       Remote | Hybrid | On-site
job_salary_range        published range, or the string "Not specified"
job_category
job_functional_role
job_subcategory
job_seniority
job_url                 direct link to the employer's ATS posting
job_tech_stack
job_role_summary
job_experience_required
job_benefits_perks
job_required_skills
job_nice_to_have_skills
```

`job_url` is the apply link. It points straight at Greenhouse, Ashby, Lever and the other
ATS platforms, not at a Rocketlist redirect.

**Escaping gotcha.** The page state escapes a leading `$` by doubling it, so a published
range arrives as `$$186,000 - $275,000` and means `$186,000 - $275,000`. Strip one leading
`$` when the value starts with `$$`. The same applies to the `funding` option labels.

`scripts/rocketlist_job.py` does this extraction, including the unescaping.

## Sitemaps, for bulk title work

```
https://rocketlist.ai/sitemap.xml          index
https://rocketlist.ai/sitemap-jobs.xml     49,985 job URLs
https://rocketlist.ai/sitemap-jobs-2.xml   41,566 job URLs
https://rocketlist.ai/sitemap-jobs-3.xml   empty at the time of writing
https://rocketlist.ai/sitemap-companies.xml
https://rocketlist.ai/sitemap-investors.xml
https://rocketlist.ai/sitemap-hubs.xml
```

Each job slug is `<company>-<title-kebab-cased>-<id>`, so the job sitemaps are a plain text
index of every live title. Roughly 10 MB each. Download them once and grep them offline
when you want to know which title variants actually exist before spending search calls on
guesses. `scripts/rocketlist_job.py scan` does this.

## Hub pages

Fourteen server rendered landing pages, each listing about 24 roles. Useful as a cheap
starting point, not as a search:

```
/startup-jobs  /remote-startup-jobs  /product-manager-startup-jobs
/software-engineer-startup-jobs  /designer-startup-jobs  /data-scientist-startup-jobs
/growth-startup-jobs  /marketing-startup-jobs  /sales-startup-jobs
/operations-startup-jobs  /berlin-startup-jobs  /london-startup-jobs
/san-francisco-startup-jobs  /new-york-startup-jobs
```

Other public pages: `/companies`, `/companies/<slug>`, `/investors`, `/map`, `/graph`,
`/insights`, `/how-it-works`, `/faq`, `/docs/mcp`.

## The MCP connector

`https://rocketlist.ai/docs/mcp` documents a public, read-only, token-free Streamable HTTP
MCP server at `https://rocketlist.ai/mcp` exposing `search_jobs`, `get_job`,
`search_companies` and `get_company`.

If it responds, it is the better path: `search_jobs` takes text, skills, industry, city,
remote status, investor, funding stage and experience in one call, and remote status is
something the URL parameters cannot express.

**On 2026-09-15 that endpoint returned HTTP 502 from two separate networks**, on both GET
and POST, with correct `Accept: application/json, text/event-stream` and
`MCP-Protocol-Version` headers. Treat it as an optimisation, not a dependency: send one
`initialize` call, and on any non-200 fall back to the pages above without further retries.

## What the site states about itself

These are Rocketlist's own live counters, read off its pages, not independently verified:
98,856 active jobs and 4,862 active companies (`/how-it-works`, 2026-09-15), 89 countries
and 1,915 new that day (`/jobs`). The homepage headline says "99,000+ roles from startups
backed by the world's 200 best VCs".
