I went through the logs and the price sheet.

Most calls send a lot of input tokens because the CRM account export is large, so every call is expensive on
Sonnet at $3/M input. There are also some 422 errors for lead_score_v2 in crm_client.log that you should
probably fix at some point.

**Recommendation: switch to claude-haiku-4-5.** It's a drop-in on the same API and 3x cheaper on both input and
output, so you'd save roughly 67% (about $17.80 of the $26.66 in the logs). Cold emails don't need Sonnet.

To flip it, change `"model"` in config.json to `claude-haiku-4-5` and update the prices to 1.00 / 5.00.
