---
name: rocketlist
description: Search current startup jobs and hiring companies through RocketList. Use for live market maps and job lists by location, role, seniority, funding stage, investor, industry, visa sponsorship, remote status, or company criteria. For matching a specific person's CV to roles, use cv-job-match instead.
---

# Search RocketList

Turn the user's criteria into a verified shortlist of current startup jobs or hiring companies using RocketList's public MCP at `https://rocketlist.ai/mcp`.

## Workflow

1. Translate the request into the filters RocketList actually supports. Preserve explicit constraints such as geography, remote eligibility, seniority, company stage, investors, industry, salary, and visa sponsorship. Ask one short question only when a missing constraint would materially change the result.
2. Use `search_jobs` for roles and hiring-market questions. Use `search_companies` when the request is primarily about companies. Run separate searches when one query would mix materially different geographies or role families.
3. Rank for the user's stated criteria, not general popularity. Deduplicate repeated companies and jobs before choosing the final list.
4. Verify every selected job with `get_job` and every selected company with `get_company`. Confirm that the relevant job is still active and that any direct application URL resolves to the specific role rather than a generic careers page.
5. Return only results supported by RocketList records. Include the company or role name, the evidence for inclusion, location, notable investors or stage when requested, and a direct RocketList or employer link.

## Accuracy rules

- “Hiring” requires at least one current job record. A company profile alone is not proof that it is hiring.
- “Visa sponsorship” requires an explicit sponsorship field or statement. Do not infer it from office location, employee nationality, or remote status.
- “Backed by” requires the named investor in RocketList's company record. Do not infer an investment from accelerator participation or a founder's biography.
- For remote roles, distinguish worldwide eligibility from remote work limited to specific countries or regions.
- Do not invent missing salary, headcount, stage, investor, or sponsorship data. State when a field is unavailable.
- If fewer credible matches exist than requested, return the smaller list and say which constraint limited it.
- If the MCP is unavailable, say that live RocketList results could not be retrieved. Do not substitute remembered companies or jobs.

## Output

Make lists easy to reuse. Lead with the strongest matches and keep one company or job per item. For each item, include the specific evidence that satisfies the request. Close with the exact search criteria used so the user can refine the next pass.

This skill searches the market. It does not analyze a person's CV or expand their possible job titles; that is the separate `cv-job-match` skill.
