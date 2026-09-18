# Third-party notices

This bundle is not GetEdge's work and is not covered by the repository's
Apache-2.0 grant. That is why there is no `LICENSE` file in this folder: we
hold no rights here to grant.

`SKILL.md` is Monid's own Skill, published by Monid at
https://monid.ai/SKILL.md for agents to install. It is redistributed here in
partnership with Monid, under Monid's terms, unmodified apart from its
front-matter `name:`, which was changed from `monid` to `pay-per-call-apis` so
the catalogue names the capability rather than the vendor. The `monid/` folder
in this repository is an alias that points back here.

`DERIVATION.json` records the fetch date (2026-09-16), the upstream version
(0.1.7) and the SHA-256 of the file as fetched, so a reader can verify that
nothing else was changed:

    sha256sum SKILL.md
    python3 -c "import json;print(json.load(open('DERIVATION.json'))['copy_files'][0]['sha256'])"

The Skill instructs your agent to replace this file with the current version
from https://monid.ai/SKILL.md whenever the installed Monid CLI and the Skill
disagree on version, so the copy here is a starting point rather than the
canonical text.

Everything else in this repository is Apache-2.0, Copyright 2026 Floom. See
the root `README.md` section "Licence" and the root `LICENSE`.
