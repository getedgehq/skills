# Sources

Two kinds, both public and both keyless.

## Feed adapters

An entry in `feeds` needs a `name` (free text, used in the report), an `adapter`
and a `url`. The adapter decides how the response is unpacked; the URL is yours,
so you can change the query string without touching code.

| adapter | endpoint shape | records at | notes |
| --- | --- | --- | --- |
| `arbeitnow` | `https://www.arbeitnow.com/api/job-board-api` | `data[]` | `remote` boolean is trustworthy |
| `himalayas` | `https://himalayas.app/jobs/api?limit=100` | `jobs[]` | remote-only board; `locationRestrictions` is the geography field |
| `jobicy` | `https://jobicy.com/api/v2/remote-jobs?count=50` | `jobs[]` | remote-only board; `jobGeo` is the geography field |
| `remotive` | `https://remotive.com/api/remote-jobs?search=<term>` | `jobs[]` | remote-only; the `search` parameter narrows server-side |

A remote-only board sets `remote_hint` true for every record. The remote filter
still runs, because a board's idea of remote and yours are not the same thing.

## Public ATS boards

An entry in `ats_watchlist` needs a `provider` and a `board`, and optionally a
`company` used only when the board omits the employer name.

| provider | URL built | board name is |
| --- | --- | --- |
| `ashby` | `https://api.ashbyhq.com/posting-api/job-board/{board}` | the slug in `jobs.ashbyhq.com/<slug>` |
| `greenhouse` | `https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | the token in `boards.greenhouse.io/<token>` |
| `lever` | `https://api.lever.co/v0/postings/{board}?mode=json` | the slug in `jobs.lever.co/<slug>` |

### Confirm a board before you add it

```
curl -s -o /dev/null -w '%{http_code}\n' \
  https://boards-api.greenhouse.io/v1/boards/<board>/jobs
```

200 means the board is public and the name is right. 404 means the name is wrong
or the employer moved ATS, and adding it gives you a source that reports
`failed (HTTPError)` forever while you assume the market is quiet. Employers
change ATS often enough that a watchlist needs re-checking, which is what the
**Source status** section of the queue is for.

Keep the watchlist short and specific. It is a list of employers you would
genuinely read a posting from, not a database. Broad discovery is what the feeds
are for.

## Adapter fields

Every adapter maps onto the same record: `source`, `source_id`, `title`,
`company`, `url`, `location`, `employment_type`, `published_at`, `description`,
`tags`, `remote_hint`, and on Ashby `is_listed`. A field the source does not
provide stays empty. Nothing is inferred to fill a gap, because an inferred
location silently defeats the geography filter.

Greenhouse `metadata` is a free-form list an employer can put anything in, so
only entries whose label is a known employment-type label are kept, and only if
the value is under 120 characters. Without that, one employer's long free-text
field ends up in the queue as an employment type.
