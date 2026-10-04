#!/usr/bin/env python3
"""Turn a person's own writing into a clean, split, chat-format training set.

Input, either:
  --input examples.jsonl   one example per line: {"answer": "...", "prompt": "...", "group": "...", "synthetic": true}
                           (prompt optional; group = thread / conversation / document)
  --input folder/          every .txt/.md file is one example; group = its subfolder (or file name)
Steps: sanitize -> drop empty/short -> dedupe (exact + near) -> reject prompts that leak their answer
-> fit to the token limit (needs --tokenizer) -> split by whole groups -> write
  OUT/train.jsonl valid.jsonl test.jsonl   ({"messages": [...]}, the format mlx-lm and train_hf.py read)
  OUT/split.json                           group -> split, frozen after the first build
  OUT/preview.md                           5 sanitized pairs for the person to check
  OUT/summary.json                         counts only, safe to show the agent in local-only mode
Prints the summary only, never sample text.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MAX_TOKENS, fit, messages, read_jsonl, write_jsonl  # noqa: E402

QUOTE_HEADER = re.compile(r"^\s*(On .{3,200} wrote:|Am .{3,200} schrieb .*:|-----\s*Original Message\s*-----|---------- Forwarded message ---------|Begin forwarded message:)\s*$", re.I | re.M)
PATTERNS = [
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    (re.compile(r"https?://\S+|www\.\S+"), "[LINK]"),
    (re.compile(r"\b(?:sk|pk|rk|ghp|gho|xox[abp]|AKIA)[-_A-Za-z0-9]{12,}\b"), "[SECRET]"),
    (re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}\b"), "[IBAN]"),
    (re.compile(r"(?<!\w)\+?\d[\d ()./-]{7,}\d\b"), "[NUMBER]"),
    (re.compile(r"\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Blvd)\b\.?"), "[ADDRESS]"),
    (re.compile(r"\b[A-Z][a-zäöüß]+(?:straße|strasse|weg|gasse|platz|allee)\s+\d+\w?\b"), "[ADDRESS]"),
]


def sanitize(text, names):
    m = QUOTE_HEADER.search(text)
    if m:
        text = text[: m.start()]
    lines = [l for l in text.splitlines() if not l.lstrip().startswith(">")]
    # signature block after the standard "-- " delimiter
    if "-- " in lines:
        lines = lines[: lines.index("-- ")]
    text = "\n".join(lines).strip()
    for rx, rep in PATTERNS:
        text = rx.sub(rep, text)
    for n in names:
        text = re.sub(r"\b" + re.escape(n) + r"\b", "[NAME]", text, flags=re.I)
    return text


def words(t):
    return re.findall(r"[a-z0-9']+", t.lower())


def ngrams(ws, n):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def load(path):
    if os.path.isdir(path):
        rows = []
        for root, _, files in os.walk(path):
            for f in sorted(files):
                if f.endswith((".txt", ".md")):
                    p = os.path.join(root, f)
                    rel = os.path.relpath(root, path)
                    rows.append({"answer": open(p, encoding="utf-8", errors="replace").read(),
                                 "group": rel if rel != "." else f})
        return rows
    return read_jsonl(path)


def split_groups(rows, seed, frozen):
    groups = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    if frozen:
        assign = dict(frozen)
        for g in groups:
            assign.setdefault(g, "train")   # new groups (feedback) only ever go to train
        return assign
    order = sorted(groups, key=lambda g: hashlib.sha256(f"{seed}:{g}".encode()).hexdigest())
    n = len(rows)
    need = {"test": max(12, math.ceil(0.1 * n)), "valid": max(8, math.ceil(0.1 * n))}
    assign, i = {}, 0
    for split in ("test", "valid"):
        have = 0
        while have < need[split] and i < len(order):
            assign[order[i]] = split
            have += len(groups[order[i]])
            i += 1
    for g in order[i:]:
        assign[g] = "train"
    return assign


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--system-file", help="style card + memory used as the system prompt (same text the launcher uses)")
    ap.add_argument("--names", default="", help="comma-separated names to replace with [NAME]")
    ap.add_argument("--tokenizer", help="HF model id or path; enables token fitting and mask checks")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--min-words", type=int, default=5)
    ap.add_argument("--seed", default="42")
    ap.add_argument("--default-prompt", default="Write this in my usual way.",
                    help="used when an example has no prompt and none was written (local-only mode)")
    ap.add_argument("--block-size", type=int, default=10, help="messages per group when there are fewer than 3 groups")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    system = open(a.system_file, encoding="utf-8").read().strip() if a.system_file else ""
    names = [n.strip() for n in a.names.split(",") if n.strip()]
    s = {"input_examples": 0, "dropped_short": 0, "dropped_duplicate": 0, "dropped_prompt_leak": 0,
         "dropped_too_long": 0, "prompts_cut_to_fit": 0, "synthetic_prompts": 0, "default_prompts": 0}

    rows = load(a.input)
    s["input_examples"] = len(rows)
    clean = []
    for i, r in enumerate(rows):
        ans = sanitize(r["answer"], names)
        if len(words(ans)) < a.min_words:
            s["dropped_short"] += 1
            continue
        prompt = sanitize(r.get("prompt") or "", names)
        synthetic = bool(r.get("synthetic"))
        if not prompt:
            prompt, synthetic = a.default_prompt, True
            s["default_prompts"] += 1
        clean.append({"id": r.get("id", f"ex{i}"), "group": str(r.get("group") or f"ex{i}"),
                      "prompt": prompt, "answer": ans, "synthetic": synthetic})

    # exact + near duplicates on the answer
    kept, seen = [], []
    for r in clean:
        g = ngrams(words(r["answer"]), 5) or {tuple(words(r["answer"]))}
        if any(len(g & h) / max(1, len(g | h)) >= 0.6 for h in seen):
            s["dropped_duplicate"] += 1
            continue
        seen.append(g)
        kept.append(r)

    # prompt must not give away its answer
    out = []
    for r in kept:
        if r["prompt"] != a.default_prompt and ngrams(words(r["prompt"]), 6) & ngrams(words(r["answer"]), 6):
            s["dropped_prompt_leak"] += 1
            continue
        out.append(r)

    if a.tokenizer:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
        fitted = []
        for r in out:
            p = fit(tok, system, r["prompt"], r["answer"], a.max_tokens)
            if p is None:
                s["dropped_too_long"] += 1
                continue
            if p != r["prompt"]:
                s["prompts_cut_to_fit"] += 1
                r["prompt"] = p
            fitted.append(r)
        out = fitted

    # fewer than 3 groups: contiguous blocks become groups (neighbouring blocks may share context)
    s["blocked_groups"] = False
    if len({r["group"] for r in out}) < 3:
        for i, r in enumerate(out):
            r["group"] = f"{r['group']}#block{i // a.block_size}"
        s["blocked_groups"] = True

    split_path = os.path.join(a.out, "split.json")
    frozen = json.load(open(split_path)) if os.path.exists(split_path) else None
    assign = split_groups(out, a.seed, frozen)
    parts = {"train": [], "valid": [], "test": []}
    for r in out:
        parts[assign[r["group"]]].append(r)
    s.update({f"{k}_examples": len(v) for k, v in parts.items()})
    s.update({f"{k}_groups": len({r['group'] for r in v}) for k, v in parts.items()})
    s["synthetic_prompts"] = sum(r["synthetic"] for r in out)
    ok = s["train_examples"] >= 30 and s["valid_examples"] > 0 and s["test_examples"] > 0
    s["trainable"] = ok
    if not ok:
        s["reason"] = "need >= 30 training examples and at least one group each for valid and test after filtering"

    if not frozen:
        json.dump(assign, open(split_path, "w"), indent=1)
    for k, v in parts.items():
        write_jsonl(os.path.join(a.out, f"{k}.jsonl"),
                    [{"messages": messages(system, r["prompt"], r["answer"]), "id": r["id"], "group": r["group"],
                      "synthetic": r["synthetic"]} for r in v])
    with open(os.path.join(a.out, "preview.md"), "w", encoding="utf-8") as f:
        f.write("# Check these before training\n\nThis is what the training will see after cleaning. "
                "If you spot a name, address or anything private, tell Claude (or add it to --names) and rebuild.\n\n")
        for r in parts["train"][:5]:
            f.write(f"**Message:** {r['prompt']}\n\n**Your answer:** {r['answer']}\n\n---\n\n")
    json.dump(s, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
    print(json.dumps(s, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
