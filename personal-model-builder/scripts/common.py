"""Shared helpers: chat encoding with an exact assistant-only loss mask, and NLL scoring.

Used by build_dataset.py (token fitting), train_hf.py and evaluate.py so that training,
fitting and scoring all see the same tokens.
"""
import json
import os
import re

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

MAX_TOKENS = 1024


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def messages(system, prompt, answer=None):
    m = [{"role": "system", "content": system}] if system else []
    m.append({"role": "user", "content": prompt})
    if answer is not None:
        m.append({"role": "assistant", "content": answer})
    return m


def _ids(x):
    # transformers may return a list, a tensor, or a BatchEncoding depending on version
    if hasattr(x, "input_ids"):
        x = x["input_ids"]
    if hasattr(x, "tolist"):
        x = x.tolist()
    return list(x)


def encode(tok, msgs):
    """Return (input_ids, labels). Labels are -100 everywhere except the final assistant turn.

    The prompt part is the same text the model sees at inference (add_generation_prompt=True),
    which is also how mlx-lm's --mask-prompt computes its offset.
    """
    prompt_ids = _ids(tok.apply_chat_template(msgs[:-1], add_generation_prompt=True, tokenize=True))
    full_ids = _ids(tok.apply_chat_template(msgs, tokenize=True))
    if full_ids[: len(prompt_ids)] != prompt_ids:
        raise AssertionError("chat template: prompt is not a prefix of the full conversation")
    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    span = tok.decode(full_ids[len(prompt_ids):])
    if msgs[-1]["content"].strip() not in span or len(full_ids) == len(prompt_ids):
        raise AssertionError("assistant span does not contain the full answer")
    return full_ids, labels


def fit(tok, system, prompt, answer, max_tokens=MAX_TOKENS):
    """Cut the prompt from the left (whole words) until the example fits. None if the answer alone does not fit."""
    if len(encode(tok, messages(system, "", answer))[0]) > max_tokens:
        return None
    words = prompt.split()
    lo = 0
    while True:
        p = ("... " if lo else "") + " ".join(words[lo:])
        if len(encode(tok, messages(system, p, answer))[0]) <= max_tokens:
            return p
        lo += max(1, (len(words) - lo) // 8)
        if lo >= len(words):
            return None


def nll(model, tok, rows, system=None, batch_size=4):
    """Token-weighted negative log-likelihood over assistant tokens only. Returns (total_nll, n_tokens).

    rows: dicts with prompt/answer (+ optional system). `system` overrides every row's system prompt.
    """
    import torch
    total, count = 0.0, 0
    model.eval()
    enc = [encode(tok, messages(system if system is not None else r.get("system", ""), r["prompt"], r["answer"])) for r in rows]
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    with torch.no_grad():
        for i in range(0, len(enc), batch_size):
            chunk = enc[i:i + batch_size]
            n = max(len(x) for x, _ in chunk)
            ids = torch.tensor([x + [pad] * (n - len(x)) for x, _ in chunk])
            lab = torch.tensor([y + [-100] * (n - len(y)) for _, y in chunk])
            att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x, _ in chunk])
            logits = model(input_ids=ids, attention_mask=att).logits[:, :-1].float()
            tgt = lab[:, 1:]
            lp = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1),
                                                   ignore_index=-100, reduction="sum")
            total += lp.item()
            count += int((tgt != -100).sum())
    return total, count


def load_hf(model_name, adapter=None, revision=None, device="cpu"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name, revision=revision)
    dtype = torch.bfloat16 if device == "cuda" and torch.cuda.is_bf16_supported() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision, dtype=dtype).to(device)
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter).to(device)
    return model, tok


def banned_phrases(card):
    """Literal hard rules from a style card: lines like  Never write: "XOXO", "Best regards"."""
    out = []
    for line in card.splitlines():
        if re.match(r"\s*[-*]?\s*never (write|say|use)\b", line, re.I):
            out += re.findall(r"[\"“']([^\"”']{2,60})[\"”']", line)
    return out
