import json
import sys

# Load the trace log
with open('/home/user/work/logs/calls-2026-09-01_15.jsonl') as f:
    calls = [json.loads(line) for line in f]

# Current model pricing (Sonnet)
SONNET_IN = 3.00
SONNET_OUT = 15.00

# Alternative model pricing from the price sheet
HAIKU_IN = 1.00
HAIKU_OUT = 5.00

GPT5_MINI_IN = 0.25
GPT5_MINI_OUT = 2.00

GEMINI_FLASH_IN = 0.30
GEMINI_FLASH_OUT = 2.50

DEEPSEEK_IN = 0.28
DEEPSEEK_OUT = 0.42

# Calculate current costs
total_cost_sonnet = 0
total_input_tokens = 0
total_output_tokens = 0
total_calls = 0
conversations = set()
leads = set()
errors = 0

for call in calls:
    if call['cost_usd'] is not None:
        total_cost_sonnet += call['cost_usd']
        total_input_tokens += call['input_tokens']
        total_output_tokens += call['output_tokens']
        total_calls += 1
        conversations.add(call['conversation_id'])
        leads.add(call['lead_id'])
    else:
        errors += 1

# Calculate costs for other models
cost_haiku = (total_input_tokens / 1e6 * HAIKU_IN) + (total_output_tokens / 1e6 * HAIKU_OUT)
cost_gpt5_mini = (total_input_tokens / 1e6 * GPT5_MINI_IN) + (total_output_tokens / 1e6 * GPT5_MINI_OUT)
cost_gemini = (total_input_tokens / 1e6 * GEMINI_FLASH_IN) + (total_output_tokens / 1e6 * GEMINI_FLASH_OUT)
cost_deepseek = (total_input_tokens / 1e6 * DEEPSEEK_IN) + (total_output_tokens / 1e6 * DEEPSEEK_OUT)

print("=" * 70)
print("ANTHROPIC COST ANALYSIS - OUTREACH AGENT")
print("Period: Sept 1-15, 2026 (first half of month)")
print("=" * 70)
print()
print(f"Usage Summary:")
print(f"  Total API calls:         {total_calls:,}")
print(f"  Unique conversations:    {len(conversations)}")
print(f"  Unique leads processed:  {len(leads)}")
print(f"  API errors (token limit):{errors}")
print()
print(f"Token Usage:")
print(f"  Input tokens:            {total_input_tokens:,}")
print(f"  Output tokens:           {total_output_tokens:,}")
print(f"  Total tokens:            {total_input_tokens + total_output_tokens:,}")
print()
print("=" * 70)
print("CURRENT COSTS (Claude Sonnet 4.5)")
print("=" * 70)
print(f"  Input:  ${total_input_tokens / 1e6 * SONNET_IN:,.2f}  ({total_input_tokens/1e6:.2f}M tokens @ ${SONNET_IN}/M)")
print(f"  Output: ${total_output_tokens / 1e6 * SONNET_OUT:,.2f}  ({total_output_tokens/1e6:.2f}M tokens @ ${SONNET_OUT}/M)")
print(f"  TOTAL:  ${total_cost_sonnet:,.2f}")
print()
print("=" * 70)
print("ALTERNATIVE MODEL COSTS & SAVINGS")
print("=" * 70)
print()
print(f"1. Claude Haiku 4.5 (drop-in replacement, same API)")
print(f"   Cost:    ${cost_haiku:,.2f}")
print(f"   Savings: ${total_cost_sonnet - cost_haiku:,.2f}  ({(1 - cost_haiku/total_cost_sonnet)*100:.1f}% cheaper)")
print()
print(f"2. GPT-5 Mini (requires OpenAI SDK)")
print(f"   Cost:    ${cost_gpt5_mini:,.2f}")
print(f"   Savings: ${total_cost_sonnet - cost_gpt5_mini:,.2f}  ({(1 - cost_gpt5_mini/total_cost_sonnet)*100:.1f}% cheaper)")
print()
print(f"3. Gemini 2.5 Flash (requires Google SDK)")
print(f"   Cost:    ${cost_gemini:,.2f}")
print(f"   Savings: ${total_cost_sonnet - cost_gemini:,.2f}  ({(1 - cost_gemini/total_cost_sonnet)*100:.1f}% cheaper)")
print()
print(f"4. DeepSeek v3.2 (cheapest, hosted in China)")
print(f"   Cost:    ${cost_deepseek:,.2f}")
print(f"   Savings: ${total_cost_sonnet - cost_deepseek:,.2f}  ({(1 - cost_deepseek/total_cost_sonnet)*100:.1f}% cheaper)")
print()
print("=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print()
print("**Switch to Claude Haiku 4.5**")
print()
print("Reasoning:")
print("  ✓ Drop-in replacement - no code changes needed")
print("  ✓ Same API, same Anthropic SDK")
print(f"  ✓ {(1 - cost_haiku/total_cost_sonnet)*100:.1f}% cost reduction")
print(f"  ✓ Projected Sept 1-30 cost: ~${cost_haiku * 2:,.2f} (vs ~${total_cost_sonnet * 2:,.2f} w/ Sonnet)")
print(f"  ✓ Monthly savings: ~${(total_cost_sonnet - cost_haiku) * 2:,.2f}")
print("  ✓ Still excellent for cold email writing")
print()
print("Alternative if you want maximum savings:")
print(f"  GPT-5 Mini would save ${(total_cost_sonnet - cost_gpt5_mini) * 2:,.2f}/month")
print("  But requires switching to OpenAI SDK (more code changes)")
print()
print("=" * 70)
print()
print(f"Note: Detected {errors} API errors due to context length issues.")
print("These are expensive failed requests that still cost money.")
print("Haiku will help with costs but won't fix the context issue.")
print("=" * 70)

