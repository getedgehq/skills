#!/bin/bash
cd "$(dirname "$0")/../../../.."   # adjust: folder holding run/ and venv/
export HF_HOME=$PWD/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
M=$PWD/hf/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775
E="venv/bin/python skills/personal-model-builder/scripts/evaluate.py"
R=run/runs/v1
for arm in mine card base; do
  $E generate --arm $arm --threads 2 --model $M --adapter $R/adapter --system-file run/work/style-card.md --prompts run/work/prompts.jsonl --out $R/out-$arm.jsonl > run/gen-$arm.log 2>&1 &
done
wait
echo GEN_DONE
