# Open source telemetry done right

Source: 1984 Ventures Founders Handbook, section "6. Open Source", chapter "Why Your Open
Source Project Needs Telemetry (And how to do it right)",
https://1984.vc/docs/founders-handbook/eng/open-source-telemetry. This file is a derived
summary: credit 1984 Ventures, link the chapter, and do not present it as original. The
content playbook from the same section is in [seed-engineering.md](seed-engineering.md).

## The argument

Without usage data a maintainer builds in the dark. Telemetry enables data-driven
development, issue prioritization and user-experience insight. Frame it as a value
exchange: anonymous data for a better product, stated explicitly in the docs.

## Privacy first, not eventually

- Collect coarse environment data ("linux", "node_18", a memory tier, install method),
  not exact versions or specs.
- Collect what happened, not who: feature used, a duration bucket, success, and a
  session hash that is not reused across sessions.
- Never log IP addresses, usernames, paths or filenames, user content or queries, unique
  device identifiers, or detailed system specs.

## Opt-out that is obvious

The chapter argues opt-in rates below 3% make data statistically useless, so it
recommends default-on with trivially easy opt-out:

- A first-run notice that says what is and is not collected, links the exact schema, and
  asks to continue.
- Several opt-out paths: environment variable, config file, command flag, settings UI.
- Telemetry status shown in version output, help and startup logs.

## Transparency in the architecture

- Keep the telemetry code open and in one readable location.
- Publish a data promise: minimum data, no personal information or session correlation,
  raw data deleted after 90 days with only aggregates kept, never sell individual-level
  data, opt out anytime without losing features.

## Implementation patterns

- Add statistical noise to sensitive counts (differential privacy).
- Batch and aggregate locally (a daily summary, not every click).
- Fail silently with a short timeout; telemetry must never affect the user.
- Offer a debug flag that prints every event before it is sent.

## Community and pitfalls

- Announce it with explicit collected and not-collected lists, opt-out instructions,
  and links to the source and policy; include privacy advocates in the design.
- Pitfalls: feature creep (start minimal, announce additions), third-party analytics
  that break your constraints, and "we value your privacy" marketing speak.
- Start with under 10 event types, ship the transparency features first, get community
  feedback, iterate and publish what you learn.
