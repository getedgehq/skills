FINBOT REVENUE DISCREPANCY - INVESTIGATION RESULTS
===================================================

Prepared for: Daniel Kurz (CEO)
Date: September 16, 2026
Issue: FinBot reported Q2 revenue as $4.1M, Finance says $3.6M

SUMMARY
-------
✅ The model is NOT hallucinating
✅ The model is NOT broken  
✅ You do NOT need a more expensive model

The bot queried the WRONG TABLE in the database. Simple prompt fix.

THE NUMBERS
-----------
FinBot said:    $4,138,212 (from 'orders' table - includes cancelled/refunded)
Finance says:   $3,638,336 (from 'revenue_recognized' table - correct GAAP revenue)
Difference:     $499,876 (refunded + cancelled orders)

THE FIX
-------
Update prompt.md to tell the bot which table to use for revenue questions.
See: prompt_UPDATED.md (ready to deploy)

FILES IN THIS FOLDER
--------------------
1. executive_summary.md
   → One-page summary for Daniel (start here)

2. root_cause_analysis.md
   → Complete explanation with all context and recommendations

3. technical_analysis.md
   → Database queries, data validation, detailed technical breakdown

4. prompt_UPDATED.md
   → Fixed system prompt (ready to deploy)
   → Jonas can replace the current prompt.md with this

5. validation_tests.py
   → Python script to test that finbot gives correct answers
   → Run from parent directory: python3 output/validation_tests.py
   → Use this after deploying the prompt update

NEXT STEPS
----------
1. Read executive_summary.md
2. Review prompt_UPDATED.md
3. Have Jonas deploy the updated prompt
4. Run validation_tests.py to verify the fix
5. Add process: "Check with Finance before putting finbot numbers in board decks"

QUESTIONS?
----------
All analysis based on:
- warehouse.db (2,213 orders in Q2 2026)
- Slack transcript from Sept 11 (Priya asking finbot)
- Exec thread from Sept 14 (Marta catching the error)
- Agent code and system prompt

The root cause is clear and the fix is simple.
