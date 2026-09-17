#!/bin/bash
# Quick verification that the model switch is complete

echo "=== Model Switch Verification ==="
echo ""
echo "Current config.json:"
cat /home/user/work/config.json | grep -E "(model|price_per_mtok)"
echo ""
echo "✅ Model switched to: $(cat /home/user/work/config.json | grep '"model"' | cut -d'"' -f4)"
echo ""
echo "Backup available at: config.json.backup"
echo ""
echo "To rollback if needed:"
echo "  cp config.json.backup config.json"
