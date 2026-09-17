#!/usr/bin/env bash
# SFTP Push Setup - Complete once credentials are available
#
# This script shows how to configure and test SFTP push.
# DO NOT RUN until you have the credentials from ops vault.

set -e

echo "=== Paystream SFTP Push Configuration ==="
echo ""
echo "Step 1: Install paramiko"
echo "  pip install paramiko"
echo ""

echo "Step 2: Set environment variables (get values from ops vault)"
echo "  export PAYSTREAM_SFTP_HOST='finance.example.com'"
echo "  export PAYSTREAM_SFTP_USER='paystream_user'"
echo "  export PAYSTREAM_SFTP_KEY='/path/to/private/key'"
echo "  export PAYSTREAM_SFTP_PORT='22'  # optional, defaults to 22"
echo "  export PAYSTREAM_SFTP_DIR='/incoming'  # optional, defaults to /incoming"
echo ""

echo "Step 3: Test with dry run (validates config without uploading)"
echo "  python3 << 'EOF'"
echo "from paystream import sftp_push"
echo "try:"
echo "    # This will fail if credentials not set, which is expected"
echo "    sftp_push.SFTP_CONFIG"
echo "    print('SFTP config loaded:', sftp_push.SFTP_CONFIG)"
echo "except Exception as e:"
echo "    print('Error:', e)"
echo "EOF"
echo ""

echo "Step 4: Run paystream with SFTP push"
echo "  python3 -m paystream \\"
echo "    --input data/september_timesheets.csv \\"
echo "    --out bank_september_2026.csv \\"
echo "    --run-id SEP2026 \\"
echo "    --sftp-push"
echo ""

echo "=== Troubleshooting ==="
echo ""
echo "If you get 'paramiko not installed':"
echo "  pip install paramiko"
echo ""
echo "If you get 'SFTP host not configured':"
echo "  Make sure PAYSTREAM_SFTP_HOST is exported in your shell"
echo ""
echo "If you get 'Authentication failed':"
echo "  Verify the SSH key path and permissions (should be 600)"
echo "  Test key manually: ssh -i /path/to/key user@host"
echo ""
echo "If you get 'Connection refused':"
echo "  Check host and port are correct"
echo "  Verify firewall allows outbound SSH/SFTP"
echo ""
