#!/usr/bin/env bash
# September 2026 Payroll Run
#
# This script runs the payroll for September 2026 and uploads to finance SFTP.
# 
# Usage:
#   ./september_run.sh <input_csv> [--dry-run]
#
# Required environment variables (unless --dry-run):
#   FINANCE_SFTP_HOST - SFTP hostname from ops vault
#   FINANCE_SFTP_KEY  - Path to SFTP private key from ops vault
#
# Example:
#   # Dry run to check totals
#   ./september_run.sh timesheet_september.csv --dry-run
#   
#   # Real run (requires ops vault credentials)
#   export FINANCE_SFTP_HOST="sftp.finance.example.com"
#   export FINANCE_SFTP_KEY="/path/to/finance_key"
#   ./september_run.sh timesheet_september.csv

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INPUT_CSV="${1:-}"
DRY_RUN="${2:-}"

if [ -z "$INPUT_CSV" ]; then
    echo "Usage: $0 <input_csv> [--dry-run]" >&2
    exit 1
fi

if [ ! -f "$INPUT_CSV" ]; then
    echo "Error: Input file not found: $INPUT_CSV" >&2
    exit 1
fi

RUN_ID="SEP2026"
OUTPUT_FILE="payroll_september_2026.csv"

# Build the command
CMD="python3 -m paystream --input \"$INPUT_CSV\" --run-id $RUN_ID"

if [ "$DRY_RUN" = "--dry-run" ]; then
    CMD="$CMD --dry-run"
    echo "=== DRY RUN MODE ===" >&2
    echo "" >&2
else
    CMD="$CMD --out \"$OUTPUT_FILE\""
    
    # Check for SFTP credentials
    if [ -n "${FINANCE_SFTP_HOST:-}" ] && [ -n "${FINANCE_SFTP_KEY:-}" ]; then
        CMD="$CMD --sftp-host \"$FINANCE_SFTP_HOST\" --sftp-key \"$FINANCE_SFTP_KEY\""
        echo "=== PRODUCTION RUN - Will upload to $FINANCE_SFTP_HOST ===" >&2
        echo "" >&2
    else
        echo "=== PRODUCTION RUN - No SFTP credentials, file will be saved locally only ===" >&2
        echo "Set FINANCE_SFTP_HOST and FINANCE_SFTP_KEY to enable automatic upload" >&2
        echo "" >&2
    fi
fi

# Run the payroll
eval "$CMD"

if [ "$DRY_RUN" != "--dry-run" ]; then
    echo "" >&2
    echo "Output written to: $OUTPUT_FILE" >&2
fi
