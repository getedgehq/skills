# job-board-scout

A deduplicated, ranked review queue of new job postings from public job feeds and
public Ashby, Greenhouse and Lever boards, filtered by rules you write down.

```
npx skills add getedgehq/skills --skill job-board-scout
```

## Prerequisites

- Python 3.9 or later. Standard library only; nothing to install.
- Outbound HTTPS to the endpoints listed in your config.
- **No credential of any kind.** No API key, no account, no OAuth, no secret.
  Every endpoint it reads is public by design.
- A config file you write. There is no default search: `filters.title_terms` is
  required, and the script exits 2 without it rather than guessing.
- `pytest` only if you want to run the bundled tests.

## What it does not do

It cannot apply to a job, message anyone, log into a board, or write to any
service. It issues public HTTPS GET requests and writes two local files.

## Quick start

```
cp examples/recruiting.json myconfig.json     # then edit every list in it
python scripts/job_board_scout.py --config myconfig.json --out out --dry-run
```

`--dry-run` records nothing as seen, so you can tune the filters against real data
and still get the same roles on the first real run. Drop the flag when the filter
counts look right, then put it on a cron.

## Output

- `out/queue.md` — the new roles, plus per-source status, per-reason filter counts,
  funnel telemetry and coverage warnings.
- `out/state.json` — a copy of the deduplication state, which also lives at
  `--state` between runs. It holds SHA-256 fingerprints of queued roles and no
  posting content.

## Honest limits

- Deduplication is company + title + location. An employer who reposts the same
  role with a changed title will be queued again.
- The geography filter reads the location restriction the posting states. It is a
  filter over posting text, not a claim about anyone's right to work anywhere, and
  a posting that states nothing is dropped unless you set
  `geography.allow_unstated`.
- The score is a review order, not a judgement of a role. Every point is printed
  with the rule that produced it.
- Board names go stale when an employer changes ATS. Watch the **Source status**
  section; a source that has failed for a week is a dead board name, not a quiet
  market.

## Tests

```
python -m pytest tests -q
```

No network: every test supplies its own fetcher.

Apache-2.0. See `LICENSE` and `DERIVATION.json`.
