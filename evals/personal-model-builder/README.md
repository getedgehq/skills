# personal-model-builder: validation evidence (run mms-20261003-v1)

Write-up: [`personal-model-builder/VALIDATION.md`](../../personal-model-builder/VALIDATION.md). Everything here is public-domain text (Emily Post, *Etiquette*, 1922, Project Gutenberg #14314) or generated from it. There is no personal data.

- `fixture/examples.jsonl`: 262 passages and their synthetic reader questions (made by `tools/extract.py` and `tools/gen_prompts.py`, Claude Sonnet)
- `fixture/split.json`, `fixture/summary.json`: frozen chapter split and builder counts
- `fixture/style-card.md`: style card written from train passages only, used as the system prompt
- `fixture/prompts.jsonl`: 10 fresh prompts, 4 probes, 28 held-out prompts
- `run-v1/train_log.jsonl`, `train_meta.json`, `smoke_train_meta.json`, `adapter_config.json`: training record (the adapter weights are not committed)
- `run-v1/results.jsonl`: held-out NLL per arm
- `run-v1/out-{mine,card,base}.jsonl`: every generated reply, with its decoding settings
- `run-v1/judge.jsonl`, `judge_summary.json`: blind style judge verdicts (both orders) and win rates with bootstrap CIs (`tools/judge.py`)
- `tools/run_gen.sh`: how the three arms were generated (2 CPU threads each, in parallel)
