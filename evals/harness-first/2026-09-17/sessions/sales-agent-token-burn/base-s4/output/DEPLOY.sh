#!/bin/bash
# Quick deploy script for Haiku migration
# Run this to switch from Sonnet to Haiku

echo "Backing up current config..."
cp config.json config.json.backup.$(date +%Y%m%d)

echo "Deploying Haiku config..."
cp output/config.json.new config.json

echo ""
echo "✓ Done! Next batch run will use claude-haiku-4-5"
echo ""
echo "Expected savings: ~$35/month (67% reduction)"
echo ""
echo "To rollback: cp config.json.backup.* config.json"
