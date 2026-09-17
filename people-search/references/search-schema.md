# Canonical search schema

```yaml
objective: recruiting | partnership | sales | research
must_have:
  locations: []
  current_titles: []
  current_companies: []
  industries: []
  languages: []
  keywords: []
preferences:
  functions: []
  seniorities: []
  years_experience: null
  company_headcount: null
  recent_job_change: null
  posted_recently: null
exclusions:
  companies: []
  titles: []
  keywords: []
  profile_urls: []
  people: []
limits:
  requested_results: 20
  max_cost_usd: null
inputs:
  profile_urls: []
  sales_nav_url: null
  csv_path: null
```

Omit unknown fields; do not invent them. Explain which criteria are hard filters and which affect ranking. A Sales Navigator URL is an input artifact, not proof the agent can read LinkedIn.

`scripts/people_search.py` compiles a subset of this schema: `must_have.locations|current_titles|current_companies|industries|keywords`, `preferences.keywords`, and `exclusions.companies|titles|keywords|profile_urls`. Criteria outside that subset stay in the written plan and are not silently treated as executed filters.
