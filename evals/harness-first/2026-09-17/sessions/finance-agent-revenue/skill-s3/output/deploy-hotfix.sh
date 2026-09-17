#!/bin/bash
# Hotfix deployment script for FinBot Q2 revenue issue
# Run this to deploy the prompt fix immediately

set -e

echo "=================================================="
echo "FinBot Hotfix Deployment"
echo "Issue: Q2 revenue $4.1M → should be $3.6M"
echo "Fix: Add data dictionary to prompt"
echo "=================================================="
echo ""

# Check we're in the right directory
if [ ! -f "prompt.md" ]; then
    echo "ERROR: prompt.md not found. Run this from /home/user/work/"
    exit 1
fi

if [ ! -f "output/recommended-prompt.md" ]; then
    echo "ERROR: output/recommended-prompt.md not found"
    exit 1
fi

# Backup current prompt
echo "1. Backing up current prompt..."
cp prompt.md prompt.md.backup-$(date +%Y%m%d-%H%M%S)
echo "   ✓ Backed up to prompt.md.backup-$(date +%Y%m%d-%H%M%S)"
echo ""

# Deploy new prompt
echo "2. Deploying fixed prompt..."
cp output/recommended-prompt.md prompt.md
echo "   ✓ Deployed output/recommended-prompt.md → prompt.md"
echo ""

# Test the fix
echo "3. Testing the fix..."
echo "   Running: python agent.py 'what was our Q2 2026 revenue?'"
echo "   Expected: ~$3.6M (not $4.1M)"
echo ""

if [ -n "$FINBOT_GATEWAY_TOKEN" ]; then
    # Only test if we have credentials
    result=$(python agent.py "what was our Q2 2026 revenue?" 2>&1 || echo "ERROR")
    echo "   Result: $result"
    echo ""
    
    if echo "$result" | grep -q "3.6\|3,638"; then
        echo "   ✓ Test PASSED - bot now returns ~$3.6M"
    elif echo "$result" | grep -q "ERROR"; then
        echo "   ⚠ Test SKIPPED - check manually"
    else
        echo "   ✗ Test FAILED - result doesn't contain $3.6M"
        echo "   Manual verification recommended"
    fi
else
    echo "   ⚠ FINBOT_GATEWAY_TOKEN not set - skipping automated test"
    echo "   Please test manually: python agent.py 'what was our Q2 2026 revenue?'"
fi

echo ""
echo "=================================================="
echo "Hotfix deployed!"
echo ""
echo "Next steps:"
echo "1. Test manually if automated test was skipped"
echo "2. Update board deck with correct $3.6M"
echo "3. Post correction in #exec-staff"
echo "4. This week: deploy agent-v2.py (safety rails)"
echo ""
echo "To rollback: cp prompt.md.backup-* prompt.md"
echo "=================================================="
