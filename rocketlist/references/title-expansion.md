# Expanding a CV into titles the person would not search

Keyword matching a CV returns the titles the person already types into a search box. The
value of this skill is the other set: real, live titles that describe the same work under
a name the person has never applied to. This file is the method for producing them.

## Step 1: decompose the CV into capabilities, not titles

For each of the last three or four roles, write down:

- **Verbs.** What the person actually did. "Ran a weekly forecast", "shipped a billing
  migration", "onboarded the first ten enterprise customers".
- **Objects.** What the work acted on: a data warehouse, a partner integration, a hiring
  funnel, a Kubernetes fleet.
- **Counterparties.** Who they worked with or sold to: engineers, clinicians, CFOs,
  procurement, regulators. This is the strongest single predictor of an adjacent title.
- **Tools and stack.** Named systems, in the CV's own words.
- **Domain.** The industry the work was embedded in.
- **Scope.** Individual contributor, first hire, team lead, budget owner, headcount.

Never carry a title forward at this step. A "Product Manager" who spent three years
answering integration questions for enterprise customers has a solutions engineering CV
wearing a product title.

## Step 2: generate candidate titles along five axes

1. **Same work, different function.** Engineer who spent most of their time in front of
   customers: forward deployed engineer, solutions engineer, solutions architect, sales
   engineer, implementation engineer, technical account manager, developer advocate.
   Analyst who built the models everyone else used: analytics engineer, data platform,
   revenue operations, strategic finance.
2. **Same work, different company stage.** At seed stage one title absorbs four jobs.
   "Founding" and "first" prefixes are a real and searchable family: founding engineer,
   founding account executive, founding designer, first GTM hire, chief of staff.
   A manager at a large company often maps to a lead or founding title at a small one.
3. **Same work, different industry vocabulary.** The same job is a "Customer Success
   Manager" in SaaS, a "Client Partner" in agencies, a "Deployment Strategist" in AI
   infrastructure, a "Program Manager" in health systems. Translate the verbs into the
   target industry's dialect, then search the dialect.
4. **The new-category names.** Titles that did not exist a few years ago and that nobody
   searches for by habit: AI deployment strategist, forward deployed engineer, agent
   engineer, evaluation engineer, applied AI engineer, developer experience engineer,
   platform advocate, technical curriculum lead. Check them against the live index rather
   than assuming they exist.
5. **The adjacent seniority.** Both directions. A senior IC may be a strong fit for a lead
   role at a smaller company and for a staff role at a larger one, and those two searches
   return disjoint results.

Aim for fifteen to twenty-five candidate titles. Cheap to generate, cheap to test.

## Step 3: test each title against the live index before searching it

Do not spend a rendered search call on a title that does not exist. Grep the job sitemaps
for each candidate first:

```
python3 scripts/rocketlist_job.py scan --pattern "forward deployed" --pattern "solutions architect"
```

A title with zero sitemap hits is a hallucination; drop it and say nothing about it. A
title with hits is worth a real search. Keep the hit counts: they tell you how much of the
market each title represents, which is worth reporting when a title is unexpectedly large.

## Step 4: run each surviving title, widest first

Search the surviving titles one at a time rather than as one long `q` string. `q` is free
text over the description as well as the title, so a long compound query narrows fast and
unpredictably. Add filters only after a bare title returns too much.

## Step 5: keep the reason each title was generated

Carry the axis and the CV evidence forward with each title, for example "forward deployed
engineer, axis 1, three years of on-site customer integration work at Acme". That sentence
becomes the "why this fits" line in the shortlist, and it is what makes an unfamiliar title
credible to the person reading it rather than random.

## What not to do

- Do not present a title as a fit on the strength of the title alone. Open the posting and
  check the requirements against the CV.
- Do not invent a title family to sound thorough. Every title in the output must have live
  postings behind it.
- Do not drop the person's obvious titles. The shortlist should contain both, clearly
  separated, so they can see what the expansion added.
