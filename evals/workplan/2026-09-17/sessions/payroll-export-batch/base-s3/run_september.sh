#!/usr/bin/env bash
# September 2026 Payroll Run - Quick Start
# Run date: September 24th

set -e

echo "================================"
echo "Paystream September 2026 Run"
echo "================================"
echo ""

# Run tests first
echo "1. Running tests..."
./run_tests.sh
echo "✓ Tests passed"
echo ""

# Dry run to preview
echo "2. Dry run (preview)..."
python3 -m paystream \
  --input data/september_timesheets.csv \
  --out bank_sep.csv \
  --run-id SEP2026 \
  --dry-run
echo ""

read -p "Continue with actual run? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Actual run
echo "3. Generating bank file..."
python3 -m paystream \
  --input data/september_timesheets.csv \
  --out bank_sep.csv \
  --run-id SEP2026

echo ""
echo "✓ Bank file generated: bank_sep.csv"
echo ""

# Check if SFTP credentials are available
if [ -f ".sftp_config" ]; then
    source .sftp_config
    if [ -n "$SFTP_HOST" ] && [ -n "$SFTP_KEY" ]; then
        echo "4. Uploading to finance SFTP..."
        python3 -m paystream \
          --input data/september_timesheets.csv \
          --out bank_sep.csv \
          --run-id SEP2026 \
          --sftp-host "$SFTP_HOST" \
          --sftp-key "$SFTP_KEY"
        echo "✓ Uploaded to finance"
    else
        echo "⚠ SFTP credentials incomplete in .sftp_config"
        echo "Upload bank_sep.csv manually"
    fi
else
    echo "⚠ No .sftp_config found"
    echo "Upload bank_sep.csv manually to finance SFTP"
fi

echo ""
echo "================================"
echo "Done! Next steps:"
echo "- Review bank_sep.csv"
echo "- Chase E-1005 (Elif Sarac) for missing cost_centre"
echo "- Upload to finance if not done automatically"
echo "================================"
