# Outstanding Items for Fin Aregbesola

**Date:** 2026-09-16  
**Re:** ledgerctl v3 Q3 Close Preparation

Hi Fin,

The ledgerctl v3 development work is complete and ready for the Q3 close. However, there are two items that need your attention:

## 1. 🚨 URGENT: Unmapped Account Codes

The new bank export (current.csv) contains two account codes that are not in the system's MAP:

- **Code 6300** - "team lunch" transaction on 2026-08-05 for EUR 76.20
- **Code 7100** - "bank charges" transaction on 2026-08-21 for EUR 44.00

### What's happening now:
These transactions are being kept in the output (not dropped like in August), but they're appearing with their raw account codes instead of canonical names. The system prints a warning:

```
WARNING: 2 unmapped account code(s): 6300, 7100
```

### Action needed:
Please either:
1. **Add these codes to the MAP** in `ledgerctl/accounts.py` with their canonical names, OR
2. **Confirm these should stay unmapped** if they're expected to be handled differently downstream

If you want to add them, edit `ledgerctl/accounts.py` and add lines like:
```python
MAP = {
    ...
    "6300": "expenses:meals",     # or whatever the canonical name should be
    "7100": "expenses:bank_fees",  # or whatever the canonical name should be
}
```

## 2. ⏸️ 2023 Archive Reconciliation (Step 7)

This is still blocked waiting on you to send the 2023 archive CSV file. Once you send it:
- Place it in the `data/` directory
- Run: `python3 -m ledgerctl --input data/2023_archive.csv --out 2023_output.json`
- Verify the output matches your records

This isn't blocking the Q3 close, but it's on the list to complete when the file is available.

## What's Working Now

✅ New bank export format (July 2026+) processes correctly  
✅ Legacy 2024 exports still work (backward compatible)  
✅ Deduplication keeps most recently updated transactions  
✅ Negative amounts in parentheses parse correctly  
✅ Unmapped codes are kept and reported (won't lose data like August)  
✅ --since date filter available for incremental loads  
✅ All 14 tests passing  

## Testing

You can test the current export anytime:
```bash
python3 -m ledgerctl --input data/current.csv --out test_output.json
```

The output will be in `test_output.json` and you'll see any warnings about unmapped codes.

---

Let me know about the account codes when you get a chance!
