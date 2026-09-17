#!/bin/bash
# Quick Start - Stop the Bleeding
# Run this to see the analysis and apply fixes

set -e

echo "════════════════════════════════════════════════════════════"
echo "OUTREACH AGENT COST FIX - QUICK START"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "This script will:"
echo "  1. Show you the cost breakdown"
echo "  2. Verify the fixes are ready"
echo "  3. Help you test before deploying"
echo ""
read -p "Press ENTER to continue..."
echo ""

# Show cost breakdown
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Cost Breakdown"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 output/cost_comparison.py
echo ""
read -p "Press ENTER to continue..."
echo ""

# Verify fixes
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Verify Fixes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 output/run_eval.py
echo ""
read -p "Press ENTER to continue..."
echo ""

# Instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Apply Fixes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Run these commands:"
echo ""
echo "  # Backup current code"
echo "  cp agent/loop.py agent/loop.py.backup"
echo "  cp agent/prompts.py agent/prompts.py.backup"
echo "  cp agent/tools.py agent/tools.py.backup"
echo ""
echo "  # Apply fixes"
echo "  cp output/fixed_agent_code/*.py agent/"
echo ""
echo "  # Test with draft mode (doesn't send real emails)"
echo "  export EMAIL_DRAFT_MODE=true"
echo "  python -c \"from agent.loop import run_conversation; print(run_conversation('L-4440'))\""
echo ""
echo "  # Check logs - should see 3-4 turns, cost < \$0.30"
echo ""
echo "  # If all good, deploy to production"
echo ""
echo "Expected savings: \$37/month immediately (70% reduction)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. This week: Build golden set (see output/CHECKLIST.md)"
echo "2. Week of Sept 23: Switch to Haiku (see output/README.md)"
echo "3. Total savings: \$577/year"
echo ""
echo "Read output/EXECUTIVE_SUMMARY.md for full analysis"
echo ""
echo "════════════════════════════════════════════════════════════"
