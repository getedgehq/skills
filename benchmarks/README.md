# Edge benchmarks

Edge finds and loads specialist expertise for agents. This evidence hub measures skill content, delivery, routing and task outcomes, with protocols, task identifiers, reanalysis scripts and credited external research in one place.

Browse the [study register](STUDIES.md), [interactive benchmark pages](https://getedge.cc/benchmarks/) and [third-party sources](third-party/SOURCES.md).

## Published evidence

| Study | Without guidance | With guidance | Evidence |
| --- | --- | --- | --- |
| Sonnet 5.5, 32-task SkillsBench sample, three planned attempts per arm | 29/95 fully correct (30.5%) | 51/94 fully correct (54.3%) | [Report and per-task outcomes](studies/skillsbench-sample-sonnet55/REPORT.md): nudged benchmark-curated skills; task-paired lift +24.0 percentage points |
| Sonnet 5.5, 12 personal workflow tasks, two attempts per arm | 4/24 fully correct (16.7%) | 14/24 fully correct (58.3%) | [Exploratory pilot](studies/personal-skills/REPORT.md): mounted personal skills; task-paired lift +42.0 percentage points |

Wilson intervals, task-bootstrap intervals, exposure, exclusions, per-task outcomes and failure counts are retained in the reports and [analysis JSON](data/benchmarks.json). The completed samples measure supplied skill guidance. Production Edge retrieval outcomes remain pending. The historical Sonnet sample has 69 infrastructure exclusions, three missing scored cells and 83% observed skill reads; it does not meet the current 90% exposure gate. The personal-workflow pilot is exploratory and contains private-fixture rerun limits.

## What each claim requires

- **With benchmark-curated skills:** compare A with C on the named sample and model-agent stack. Historical C includes a skill-use nudge and differs from the published SkillsBench self-generated C arm.
- **When instructed to use Edge:** compare A with EX under the [Edge value protocol](studies/edge-value/PROTOCOL.md).
- **With Edge installed:** compare A with EI under that same protocol, preserving the baseline task instruction.

EX/EI confirmatory results are pending. Their amended protocol precedes those arms, while historical A/C outcomes were already known. The frozen retrieval study uses the free no-key ranking path; its [catalog hashes](studies/edge-value/FROZEN-SEARCH-VERIFICATION.json), [source exclusions](studies/edge-value/EXCLUSION-MANIFEST.json) and [leakage-screen coverage](studies/edge-value/leakage-publication.json) make that boundary inspectable. Cross-model claims require independently reported results for every named stack. Different samples, interventions and metrics cannot be pooled as a global ranking.

## Reanalyse the completed exports

From this folder, using Python 3 and its standard library:

```sh
python3 scripts/verify_studies.py
python3 scripts/sync_studies.py
```

These commands reconcile reviewed trial counts and regenerate the register and analysis JSON. They launch no agents and require no API keys. Trial downloads contain allowlisted measurements and identifiers; raw requests, production queries, user data, transcripts, private task fixtures and subject execution adapters are withheld. Upstream task links and hashes are in each study's task manifest. Synthetic personal-workflow identifiers have no public upstream corpus.

`PUBLIC-MANIFEST.json` pins every exported file. Pending studies retain null outcomes. The publication snapshot is dated 2026-10-02; “prepared” and “running” describe recorded study work rather than current process activity. External numerical facts retain publisher attribution, method labels and direct links in [SOURCES.md](third-party/SOURCES.md); external figures and article bodies are not copied. Study provenance does not transfer third-party dataset rights.
