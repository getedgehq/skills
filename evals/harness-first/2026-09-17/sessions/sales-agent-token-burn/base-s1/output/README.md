# Outreach Agent Cost Analysis - Output Files

Generated: 2026-09-15

## Quick Start

1. Read `QUICK_CARD.txt` (30 seconds)
2. Deploy `updated_config.json` (5 minutes)
3. Save $35/month

## Files

### QUICK_CARD.txt
One-page summary with action items. Start here.

### SUMMARY.txt
Executive summary with numbers and comparison table.

### cost_analysis.md
Full analysis including:
- Root cause (why costs spiked 4x)
- Model comparison (Haiku vs GPT-5-mini vs Gemini)
- Top 5 most expensive conversations
- Future optimization suggestions

### updated_config.json
Ready-to-deploy config file. Only 3 lines changed:
- model: claude-haiku-4-5
- price_per_mtok_in: 1.0
- price_per_mtok_out: 5.0

### sept_1-15_cost_breakdown.csv
Per-conversation cost breakdown for finance team.
Columns: conversation_id, lead_id, timestamp, turns, input_tokens, output_tokens, cost_usd, cost_with_haiku

### implementation_guide.md
Step-by-step deployment instructions with rollback plan.

## Key Findings

- **Current cost:** $26.66 (Sept 1-15) → $53.33 projected full month
- **Root cause:** Prompt forces agent to reload 30-40KB CRM exports on every turn
- **Token usage:** 8.7M input vs 34K output (99.6% is input tokens)
- **Worst offender:** Some conversations have 17+ turns costing $4.70 each

## Recommendation

**Switch to Claude Haiku 4.5**
- Same API (Anthropic)
- 67% cost reduction ($17.78/month)
- Zero code changes
- Deploy in 5 minutes
- Can rollback instantly

## Why Not Cheaper Models?

GPT-5-mini ($0.25/$2.00) would save 92% but requires:
- OpenAI SDK integration
- Code changes in agent/llm.py
- Testing and migration effort

Haiku is the quick win. Switch to GPT later if you want more savings.
