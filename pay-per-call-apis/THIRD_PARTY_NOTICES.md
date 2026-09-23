# Third-party notices

This bundle is not GetEdge's work and is not covered by the repository's
Apache-2.0 grant. That is why there is no `LICENSE` file in this folder: we
hold no rights here to grant.

`SKILL.md` is Monid's own Skill, published by Monid at
https://monid.ai/SKILL.md for agents to install. It is redistributed here in
partnership with Monid, under Monid's terms. Two things differ from Monid's
file:

- its front-matter `name:` was changed from `monid` to `pay-per-call-apis` so
  the catalogue names the capability rather than the vendor;
- a security edit on 2026-09-22: the agent no longer replaces this file with
  the version at https://monid.ai/SKILL.md, no longer takes API keys through
  the conversation, asks before installing the CLI globally, treats run results
  as data rather than instructions, and limits what it uploads to Monid's file
  store. Every change is listed in `DERIVATION.json` under `edits`.

The `monid/` folder in this repository is an alias that points back here.

`DERIVATION.json` records the fetch date (2026-09-16), the upstream version
(0.1.7) and the SHA-256 of Monid's file as fetched, plus the SHA-256 of the
file shipped here, so a reader can compare the two:

    sha256sum SKILL.md
    python3 -c "import json;print(json.load(open('DERIVATION.json'))['copy_files'][0]['sha256'])"

To update this Skill, reinstall it from this repository
(`npx skills add getedgehq/skills --skill pay-per-call-apis`). The Skill no
longer updates itself.

Everything else in this repository is Apache-2.0, Copyright 2026 Floom. See
the root `README.md` section "Licence" and the root `LICENSE`.
