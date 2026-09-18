# domain-uptime-monitor

A daily HTTPS probe with a real content check per domain, so a suspended
deployment or a broken build that still returns 200 is caught. Alerts fire on
state change only.

```
npx skills add getedgehq/skills --skill domain-uptime-monitor
```

## Prerequisites

- Python 3.9 or later. Standard library only; nothing to install.
- Outbound HTTPS to the domains you list.
- **Detection needs no credential.** Email alerting is optional: a
  [Resend](https://resend.com) API key in the `RESEND_API_KEY` environment
  variable, and a sender domain verified on that account. Without the key the
  probe still runs, the report is still written and the exit code is still
  correct — only the send is skipped. `--no-email` turns sending off explicitly.
- A config file you write. `notify_email` has no default and will not get one.
- `pytest` only if you want to run the bundled tests.

## Why not just check for HTTP 200

Because these all return 200:

- a suspended or payment-disabled hosting deployment serving a billing page
- a broken build serving an empty shell
- a partial deploy serving the old page over a missing API
- a misconfigured origin where the marketing page is fine and every signed-in
  action fails

Each domain declares what a working response actually contains: a content marker,
a JSON health field, an allowed status set, and optionally an authenticated
write-path probe with the signature of a break you have actually seen.

## Quick start

```
cp examples/domains.example.json domains.json     # then replace every host
python scripts/uptime_probe.py --config domains.json --no-email
```

Then add alerting:

```
export RESEND_API_KEY=...        # never put this in the config file
python scripts/uptime_probe.py --config domains.json \
    --state .uptime/state.json --report out/report.md \
    --notify-email ops@yourdomain --email-from "Uptime <uptime@yourdomain>"
```

Exit codes: `0` all critical domains up, `1` a critical domain is down, `2` bad
config, `3` the probe could not run.

## Honest limits

- It probes from wherever you run it. One machine's view of the internet is not
  the internet's view of your site, and a regional outage can look like a total
  one or like nothing at all.
- A marker check is only as good as the marker. A build hash will false-alarm on
  every deploy; a string a hosting error page also contains will never alarm.
- `post_check` sends a real request to your own endpoint on every run. Only
  configure one where you know what the broken response looks like.
- There is no retry and no flap damping. One transient failure on a critical
  domain sends one email. Run it on a schedule you are happy to be paged by.
- Email goes through Resend and nothing else. If you want PagerDuty or Slack,
  read the exit code from your scheduler.
- `gzip` and `deflate` responses are decoded before the marker check. `br` is not
  decodable with the standard library, so a Brotli-only origin needs a `status` or
  `json` check rather than a `marker` one.

## Tests

```
python -m pytest tests -q
```

No network: every test supplies its own HTTP callable.

Apache-2.0. See `LICENSE` and `DERIVATION.json`.
