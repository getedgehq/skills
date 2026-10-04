# Third-party notices

This bundle is not GetEdge's work and is not covered by the repository's
Apache-2.0 grant. That is why there is no `LICENSE` file in this folder: we
hold no rights here to grant.

`SKILL.md` is RadarKit's own Skill (https://radarkit.ai), written by RadarKit
and provided by RadarKit for Edge on 2026-10-02. No licence was stated with
it, so it is published here as provided by RadarKit for Edge, in partnership
with RadarKit, under RadarKit's terms. RadarKit remains its author and
copyright holder.

It is unmodified apart from its front-matter `name:`, which was changed from
`ai-prompt-discovery` to `geo-domination` (published as GEO Domination, by
RadarKit; it was first listed as `radarkit-prompt-discovery`, which stays as an
install alias). `DERIVATION.json` records the SHA-256 of the
file as received and of the renamed copy, so a reader can verify that nothing
else was changed:

    sha256sum SKILL.md
    python3 -c "import json;print(json.load(open('DERIVATION.json'))['copy_files'][0]['sha256'])"

Everything else in this repository is Apache-2.0, Copyright 2026 Floom. See
the root `README.md` section "License and attribution" and the root `LICENSE`.
