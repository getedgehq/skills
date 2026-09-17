# Quick Implementation Guide

## To deploy Haiku 4.5 before month end:

### Option 1: Update in place (recommended)
```bash
cd /path/to/agent/repo
cp output/updated_config.json config.json
# restart your agent service
systemctl restart brightkiln-outreach  # or however you run it
```

### Option 2: Test first
```bash
# backup current config
cp config.json config.json.sonnet-backup

# deploy new config
cp output/updated_config.json config.json

# run a test batch on a small lead set
python agent/run_batch.py --limit 5 --dry-run

# if looks good, restart for real
systemctl restart brightkiln-outreach
```

### Verification
Check the logs to confirm the model switched:
```bash
tail -f logs/calls-*.jsonl | grep -o '"model":"[^"]*"' | head -5
# should see: "model":"claude-haiku-4-5"
```

### Rollback if needed
```bash
cp config.json.sonnet-backup config.json
systemctl restart brightkiln-outreach
```

## What changed?
Only 3 lines in config.json:
- `"model": "claude-haiku-4-5"` (was claude-sonnet-4-5)
- `"price_per_mtok_in": 1.0` (was 3.0)
- `"price_per_mtok_out": 5.0` (was 15.0)

Zero code changes. Same API. Same everything.

## Monitoring
- Check cost_usd in the trace logs drops to ~⅓ previous
- Monitor email quality for first few days
- Expected: zero quality change (it's just cold emails)
- If quality drops: rollback, let me know

## Expected savings timeline
- Remaining Sept 16-30: save ~$17.78
- October onwards: save ~$35/month
- Annual: ~$425 savings
