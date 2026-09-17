#!/bin/bash
# Quick script to review the NEXT prompt change
# Usage: ./output/run_next_review.sh new_outputs.jsonl

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <new_outputs_file.jsonl>"
    echo "Example: $0 outputs_v5.jsonl"
    exit 1
fi

NEW_OUTPUTS="$1"

if [ ! -f "$NEW_OUTPUTS" ]; then
    echo "Error: File $NEW_OUTPUTS not found"
    exit 1
fi

echo "========================================="
echo "Running prompt compliance review"
echo "New outputs: $NEW_OUTPUTS"
echo "========================================="
echo

# Backup current judge.py
cp output/judge.py output/judge.py.bak

# Update judge.py to use new outputs file
sed "s|outputs_new.jsonl|$NEW_OUTPUTS|g" output/judge.py > output/judge_temp.py
mv output/judge_temp.py output/judge.py

# Run judge
echo "Running automated policy checks..."
python3 output/judge.py

RESULT=$?

# Restore original judge.py
mv output/judge.py.bak output/judge.py

echo
echo "========================================="
if [ $RESULT -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    echo "Next steps:"
    echo "1. Manual review 10 random tickets for tone"
    echo "2. Get Legal/Finance sign-off if policies changed"
    echo "3. Ship with monitoring"
else
    echo "❌ VIOLATIONS FOUND - DO NOT SHIP"
    echo "Next steps:"
    echo "1. Review judge_results_new.json for details"
    echo "2. Fix prompt"
    echo "3. Re-run this script"
fi
echo "========================================="

exit $RESULT
