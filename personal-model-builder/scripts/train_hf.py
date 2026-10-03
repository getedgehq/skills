#!/usr/bin/env python3
"""LoRA fine-tune with Hugging Face PEFT (NVIDIA GPU or CPU). The Mac path uses mlx-lm instead (see references/paths.md).

  python train_hf.py --model Qwen/Qwen2.5-0.5B-Instruct --revision <sha> --data work/data --out runs/v1 [--device cpu] [--max-steps 5]

Recipe (fixed, see SKILL.md): LoRA r16/alpha32/dropout .05 on attention+MLP projections, batch 4, 3 epochs,
lr 2e-4 linear decay with 10% warm-up, seed 42, loss on the assistant answer only. Saves an adapter about every
third of training, then scores every saved adapter on validation NLL and copies the lowest to OUT/adapter.
Never prints example text.
"""
import argparse
import json
import math
import os
import random
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import encode, load_hf, nll, read_jsonl  # noqa: E402


def rows_of(path):
    out = []
    for r in read_jsonl(path):
        m = r["messages"]
        sys_ = m[0]["content"] if m[0]["role"] == "system" else ""
        out.append({"system": sys_, "prompt": m[-2]["content"], "answer": m[-1]["content"], "messages": m})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--revision")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda" if __import__("torch").cuda.is_available() else "cpu")
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--max-steps", type=int, help="override (smoke test)")
    ap.add_argument("--saves", type=int, default=3)
    ap.add_argument("--threads", type=int)
    ap.add_argument("--resume", help="a saved checkpoint-N folder of this run: continue from it to the planned step count")
    a = ap.parse_args()

    import torch
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(42)
    random.seed(42)
    if a.threads:
        torch.set_num_threads(a.threads)

    train = rows_of(os.path.join(a.data, "train.jsonl"))
    valid = rows_of(os.path.join(a.data, "valid.jsonl"))
    model, tok = load_hf(a.model, revision=a.revision, device=a.device)
    enc = [encode(tok, r["messages"]) for r in train]   # asserts the exact assistant-only mask
    for ids, lab in enc:
        assert any(x != -100 for x in lab), "empty loss mask"
    steps = a.max_steps or math.ceil(a.epochs * len(enc) / a.batch_size)
    save_at = sorted({max(1, round(steps * (i + 1) / a.saves)) for i in range(a.saves)})

    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    start = 0
    if a.resume:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.resume, is_trainable=True)
        start = int(a.resume.rstrip("/").rsplit("-", 1)[1])
        save_at = [s for s in save_at if s > start] + [start]
    else:
        model = get_peft_model(model, cfg)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.0)
    warm = max(1, steps // 10)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, max(0.0, (steps - s) / max(1, steps - warm))))
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    os.makedirs(a.out, exist_ok=True)
    log = open(os.path.join(a.out, "train_log.jsonl"), "a" if a.resume else "w")
    order, pos, t0 = [], 0, time.time()
    model.train()
    for step in range(start + 1, steps + 1):
        batch = []
        while len(batch) < a.batch_size:
            if pos >= len(order):
                order, pos = random.sample(range(len(enc)), len(enc)), 0
            batch.append(enc[order[pos]])
            pos += 1
        n = max(len(x) for x, _ in batch)
        ids = torch.tensor([x + [pad] * (n - len(x)) for x, _ in batch], device=a.device)
        lab = torch.tensor([y + [-100] * (n - len(y)) for _, y in batch], device=a.device)
        att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x, _ in batch], device=a.device)
        loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step(); opt.zero_grad()
        rec = {"step": step, "steps": steps, "loss": round(loss.item(), 4), "elapsed_s": round(time.time() - t0, 1)}
        log.write(json.dumps(rec) + "\n"); log.flush()
        if step == 1 or step % 10 == 0 or step == steps:
            print(json.dumps(rec), flush=True)
        if step in save_at and step > start:
            model.save_pretrained(os.path.join(a.out, f"checkpoint-{step}"))

    # score the saved files, keep the lowest validation NLL
    model.eval()
    scores = {}
    for step in sorted(set(save_at)):
        path = os.path.join(a.out, f"checkpoint-{step}")
        model.load_adapter(path, adapter_name=f"s{step}")
        model.set_adapter(f"s{step}")
        tot, cnt = nll(model, tok, valid)
        scores[step] = tot / cnt
        print(json.dumps({"checkpoint": step, "valid_nll_per_token": round(scores[step], 4)}), flush=True)
    best = min(scores, key=scores.get)
    dst = os.path.join(a.out, "adapter")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(a.out, f"checkpoint-{best}"), dst)
    meta = {"model": a.model, "revision": a.revision, "device": a.device, "steps": steps, "train_examples": len(enc),
            "valid_nll_per_token": {str(k): v for k, v in scores.items()}, "chosen_checkpoint": best,
            "seconds": round(time.time() - t0, 1), "recipe": {"r": 16, "alpha": 32, "dropout": 0.05,
            "batch": a.batch_size, "epochs": a.epochs, "lr": a.lr, "seed": 42}}
    json.dump(meta, open(os.path.join(a.out, "train_meta.json"), "w"), indent=1)
    print(json.dumps({"chosen_checkpoint": best, "adapter": dst}))


if __name__ == "__main__":
    main()
