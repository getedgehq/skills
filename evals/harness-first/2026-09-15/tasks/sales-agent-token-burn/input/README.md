# outreach-agent

Nightly SDR agent for Brightkiln. For every new inbound lead it loads the CRM account, scores the lead,
writes the score back, and sends a first-touch email from the rep's mailbox.

```
python -m agent.run_batch --queue inbound --leads-file leads.json
```

- `agent/loop.py` main loop
- `agent/tools.py` CRM + email tools
- `agent/prompts.py` system prompt
- `config.json` model + prices
- `logs/` trace export (one line per model call) and the CRM client error log
- `docs/model_pricing.md` price sheet Priya put together

No tests yet (TODO).
