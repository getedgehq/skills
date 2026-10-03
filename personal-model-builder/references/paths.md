# Paths: exact commands per machine

All commands run with the private cache:

```bash
export HF_HOME=~/my-model/cache/hf UV_CACHE_DIR=~/my-model/cache/uv HF_HUB_DISABLE_TELEMETRY=1
```

## Pinned models (checked on Hugging Face 2026-10-03)

| Use | Model | Revision | Licence |
|---|---|---|---|
| CPU | `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` | Apache-2.0 |
| NVIDIA GPU | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | Apache-2.0 |
| Mac 16 GB+ | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` | `8b403126fc14f14cfc99bb4cfa72ecbc129ea677` | Apache-2.0 |
| Mac 24 GB+ | `mlx-community/Qwen3-4B-Instruct-2507-4bit` | `50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b` | Apache-2.0 |
| Mac small/CPU smoke | `mlx-community/Qwen2.5-0.5B-Instruct-4bit` | `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3` | Apache-2.0 |

Not allowed: `Qwen2.5-3B-Instruct` (Qwen Research License, non-commercial research/evaluation only).

Download once into the private cache and use the **local snapshot path** as `--model` everywhere (pins the revision and works offline):

```bash
python3 -c "from huggingface_hub import snapshot_download as d; print(d('<model>', revision='<revision>'))"
```

## Mac (Apple Silicon), MLX — documented, not yet run on a Mac by the authors

Needs: macOS on M1 or newer, 16 GB+ memory, 10 GB+ free disk. mlx-lm 0.32.0 needs Python 3.11+, which macOS does not ship; `uv` provides it without touching the system:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # once; installs uv for this user
MLX='uvx --python 3.12 --from mlx-lm[train]==0.32.0'
```

Data: `build_dataset.py` writes `train.jsonl`, `valid.jsonl`, `test.jsonl` in the `{"messages": [...]}` chat format mlx-lm reads. Run it with the tokenizer of the same model (`--tokenizer <snapshot path>`; needs `transformers`: `uv run --with transformers python3 scripts/build_dataset.py ...`).

`~/my-model/work/lora.yaml` (fill N = number of lines in train.jsonl):

```yaml
model: <snapshot path>
train: true
data: /Users/<you>/my-model/work/data
fine_tune_type: lora
mask_prompt: true          # prompt excluded from the loss (see limitation below)
batch_size: 1
grad_accumulation_steps: 4
iters: <4 * ceil(3 * N / 4)>   # ~three epochs, one example per batch, multiple of 4
num_layers: 16
learning_rate: 1e-4
max_seq_length: 1024       # build_dataset.py already made every example fit
steps_per_eval: 100000     # validation is done on the saved files afterwards
save_every: <N>            # one save per epoch
adapter_path: /Users/<you>/my-model/runs/v1/adapters
seed: 42
grad_checkpoint: true
lora_parameters:
  rank: 16
  scale: 2.0               # = alpha 32 / rank 16
  dropout: 0.05
```

```bash
$MLX mlx_lm.lora -c ~/my-model/work/lora.yaml
```

Known limitation of pinned mlx-lm 0.32.0: its batcher pads every sequence (even at batch 1) and the loss mask uses `steps <= length`, so each example shorter than `max_seq_length` adds one extra target, the padding token after the conversation ends. All answer tokens are trained and the prompt is excluded, but the loss is not exactly answer-only. Generation stops at the end-of-turn token, so this should rarely show; do not describe the MLX loss as exact. MLX NLL numbers include the same extra token for every arm (comparable across arms, not with the PC numbers).

Smoke first: same file with `iters: 5`, `adapter_path: .../runs/smoke`; time it and multiply.

Choose the checkpoint: for each saved `NNNNNNN_adapters.safetensors`, copy it as `adapters.safetensors` next to a copy of `adapter_config.json` in its own folder, then score on validation (mlx-lm `--test` reads `test.jsonl`, so point it at a folder whose `test.jsonl` is a copy of `valid.jsonl`):

```bash
$MLX mlx_lm.lora --model <snapshot> --adapter-path <ckpt folder> --data <folder with valid as test.jsonl> --test --mask-prompt --batch-size 1
```

Keep the lowest "Test loss" as `runs/v1/adapter`. The same command with the real test split gives the NLL rows for the check (`mine`: with `--adapter-path`; `base` and `card`: without, on a copy of `test.jsonl` whose system message is the neutral prompt or `system.md`). For these NLL rows add `--max-seq-length 2048`: every fitted example is at most 1024 tokens, so each example in every arm carries exactly one padding target and nothing is truncated. MLX NLL is therefore "answer tokens + one padding token per example": comparable across the three arms, not with PC numbers.

Generate (for `evaluate.py generate --backend mlx`): `uv run --python 3.12 --with mlx-lm==0.32.0 --with transformers python3 scripts/evaluate.py generate --backend mlx ...`.

Resume after a stop: `--resume-adapter-file <last checkpoint>` with `iters` = remaining batches and a new `adapter_path` (keeps earlier checkpoints). Optimizer state restarts.

Out of memory: close other apps; use the 0.5B model; lower `num_layers` to 8.

## Windows / Linux with NVIDIA GPU — script shared with CPU; GPU branch not yet run

```bash
python3 -m venv ~/my-model/venv && ~/my-model/venv/bin/pip install torch==2.14.1 transformers==5.18.0 peft==0.21.2 accelerate safetensors
~/my-model/venv/bin/python scripts/train_hf.py --model <snapshot> --data ~/my-model/work/data --out ~/my-model/runs/v1 --device cuda
```

(Windows: `~\my-model\venv\Scripts\python.exe`; the CUDA build of torch comes from https://pytorch.org/get-started/locally/.) bf16 is used when the GPU supports it, else fp32.

## No GPU, 16 GB+ free RAM — tested end to end

```bash
python3 -m venv ~/my-model/venv
~/my-model/venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.1
~/my-model/venv/bin/pip install transformers==5.18.0 peft==0.21.2 accelerate safetensors
~/my-model/venv/bin/python scripts/train_hf.py --model <0.5B snapshot> --data ~/my-model/work/data --out ~/my-model/runs/smoke --device cpu --max-steps 5 --saves 1   # smoke
~/my-model/venv/bin/python scripts/train_hf.py --model <0.5B snapshot> --data ~/my-model/work/data --out ~/my-model/runs/v1 --device cpu
```

Measured on a shared 12-core Linux server under heavy load (see VALIDATION.md): 0.5B, 200 examples, 150 steps. On a quiet modern laptop expect it to be faster, but always time the smoke run and estimate from it.

On a busy machine pass `--threads 2` to `evaluate.py generate` (fewer threads were ~3x faster under contention).

Resume after a stop: `--resume <runs/v1/checkpoint-N>` continues from that saved adapter to the planned step count (optimizer restarts).

## Hosted fine-tuning

Out of scope for v1: untested, costs money, uploads the person's writing, and the result must still run locally. If asked: "Services like that exist; this skill does not guide them yet. Your Layer A helper already works."
