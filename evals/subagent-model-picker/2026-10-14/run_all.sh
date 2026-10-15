#!/bin/bash
# Interleaved A/B runs, one at a time, memory guard >=16GB available.
set -u
N=${1:-10}
B=~/mp-bench2
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-5-5
export ANTHROPIC_DEFAULT_FABLE_MODEL=claude-fable-5-1
mkdir -p $B/runs
for i in $(seq 1 $N); do
  for C in A B; do
    [ -f $B/runs/$C-$i.grade.json ] && continue
    while :; do
      avail=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo)
      [ "$avail" -ge 16 ] && break
      echo "$(date +%T) wait mem avail=${avail}G" >> $B/runs/log.txt; sleep 60
    done
    D=$B/runs/$C-$i
    rm -rf $D; cp -r $B/template $D; rm -rf $D/.pytest_cache
    if [ "$C" = B ]; then mkdir -p $D/.claude/skills/subagent-model-picker && cp $B/SKILL.md $D/.claude/skills/subagent-model-picker/; fi
    echo "$(date +%T) start $C-$i avail=${avail}G" >> $B/runs/log.txt
    (cd $D && env -u ANTHROPIC_API_KEY timeout 1800 /usr/local/bin/claude -p "$(cat $B/PROMPT_$C.txt)" --model claude-opus-5-5 --dangerously-skip-permissions --output-format json > ../$C-$i.json 2> ../$C-$i.err)
    echo "$(date +%T) end $C-$i exit=$?" >> $B/runs/log.txt
    python3 $B/grade.py $D > $B/runs/$C-$i.grade.json 2>>$B/runs/$C-$i.err
  done
done
echo "$(date +%T) ALL DONE" >> $B/runs/log.txt
