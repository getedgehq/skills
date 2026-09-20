#!/bin/bash
# The objective gate is the brief's verify, run on the host by
# judge.py. Reward 0 here means 'not scored', not 'failed'.
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
