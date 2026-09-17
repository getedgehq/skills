# Unmapped Account Codes in Current Data

When processing `data/current.csv`, the system reports 2 unmapped account codes:

## Code 6300
- **Transaction**: T-1005
- **Amount**: EUR 76.20
- **Description**: team lunch
- **Date**: 2026-08-05

## Code 7100
- **Transaction**: T-1008
- **Amount**: EUR 44.00
- **Description**: bank charges
- **Date**: 2026-08-21

## Action Required
Fin needs to either:
1. Add these codes to `ledgerctl/accounts.py` MAP dictionary, OR
2. Confirm these should remain unmapped

## Current Behavior
✅ Both transactions are **preserved** in the output (no data loss)
✅ The codes appear as-is: "6300" and "7100" 
✅ A warning is printed to stderr when processing

This is the safe behavior that prevents the August data loss incident.
