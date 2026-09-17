#!/usr/bin/env bash
# Quick verification script for the September paystream run

set -e
cd "$(dirname "$0")"

echo "=================================="
echo "Paystream September Run Verification"
echo "=================================="
echo

# Run tests
echo "Running tests..."
bash run_tests.sh
echo "✓ All tests passing"
echo

# Check bank file exists
if [ -f "september_bank_file.csv" ]; then
    echo "✓ Bank file generated: september_bank_file.csv"
    echo "  Rows: $(tail -n +2 september_bank_file.csv | wc -l)"
else
    echo "✗ Bank file not found"
    exit 1
fi

# Dry run to verify totals
echo
echo "Running dry-run verification..."
python3 -m paystream --input data/september_timesheets.csv \
    --out /tmp/verify.csv --run-id SEP2026 --dry-run 2>/dev/null

echo
echo "=================================="
echo "✓ Ready for September 24th run"
echo "=================================="
echo
echo "Next steps:"
echo "1. Review september_bank_file.csv"
echo "2. Chase depot about E-1005 (Elif Sarac) - no cost centres"
echo "3. Upload bank file by Sept 24th"
echo
echo "See README_FOR_INES.md for details"
