#!/usr/bin/env bash
# SFTP Upload Script for September Payroll
# 
# BLOCKED: Credentials not available
# This script will upload the bank file to finance SFTP once credentials are provided.
#
# Required:
# - SFTP host (from ops vault)
# - SSH private key path (from ops vault)
#
# Usage once credentials are available:
#   python3 -m paystream \
#     --input data/september_timesheets.csv \
#     --out bank_sep.csv \
#     --run-id SEP2026 \
#     --sftp-host FINANCE_SFTP_HOST \
#     --sftp-key /path/to/private/key
#
# Note: Requires paramiko library (pip install paramiko)

echo "SFTP upload script"
echo "Credentials needed from ops vault:"
echo "  - SFTP host"
echo "  - SSH private key"
echo ""
echo "Once you have them, run:"
echo "  python3 -m paystream --input data/september_timesheets.csv --out bank_sep.csv --run-id SEP2026 --sftp-host HOST --sftp-key /path/to/key"
