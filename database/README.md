# Edge public database

`edge-database.json` is the machine-readable public index behind GetEdge's skill directory and Arena.

It contains:

- one normalized record for every skill currently shown in Explore;
- the tested tasks and configurations currently shown in Arena;
- model, judge, cost, sample, score, and provenance fields when they were published;
- the authenticity audit and its limitations.

The database deliberately does not flatten unlike evaluations into one universal quality score. A missing cost is missing, not zero. A skill with no indexed task is unevaluated, not failed. Each score retains the task, configuration, model, metric, and sample scope stored beside it.

## Use

```python
import json

db = json.load(open("database/edge-database.json"))
tested = [skill for skill in db["skills"] if skill["task_ids"]]
```

Validate the committed snapshot with `python3 database/validate.py`.

Skill package files retain the licence inside each package. The normalized database metadata is released under CC0-1.0; see `DATA_LICENSE`.
