#!/usr/bin/env python3
"""Evaluate base vs base+style card vs personal model. Subcommands:

  nll       token-weighted NLL on held-out answers (assistant tokens only)      -> appends to --results
  generate  replies for one arm on a prompt file ({"id","prompt","kind"} lines) -> outputs jsonl
  sheet     blind A/B page for the person (compare.html) + answer key
  score     tally the person's picks (picks.json saved from the page)
  regurg    flag outputs that copy 50+ characters of a training answer

Arms: base = base model + NEUTRAL system prompt; card = base model + style card/memory;
mine = adapter + the same style card/memory (exactly what the launcher runs).
Prints numbers only; texts stay in files.
"""
import argparse
import html
import json
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_hf, nll, read_jsonl, write_jsonl  # noqa: E402

NEUTRAL = "You write replies and texts for the user."
GREETINGS = re.compile(r"^(hi|hello|dear|thanks|thank you|love|best|cheers|regards)\b", re.I)


def system_for(arm, system_file):
    if arm == "base":
        return NEUTRAL
    return open(system_file, encoding="utf-8").read().strip()


def cmd_nll(a):
    rows = []
    for r in read_jsonl(a.data):
        m = r["messages"]
        rows.append({"prompt": m[-2]["content"], "answer": m[-1]["content"]})
    model, tok = load_hf(a.model, adapter=a.adapter if a.arm == "mine" else None, revision=a.revision, device=a.device)
    tot, cnt = nll(model, tok, rows, system=system_for(a.arm, a.system_file))
    res = {"metric": "nll", "arm": a.arm, "split": os.path.basename(a.data), "examples": len(rows), "tokens": cnt,
           "nll_per_token": round(tot / cnt, 4), "perplexity": round(math.exp(tot / cnt), 3)}
    with open(a.results, "a") as f:
        f.write(json.dumps(res) + "\n")
    print(json.dumps(res))


def cmd_generate(a):
    from generate import DECODING, Generator
    if a.threads:
        import torch
        torch.set_num_threads(a.threads)
    g = Generator(a.model, adapter=a.adapter if a.arm == "mine" else None, revision=a.revision,
                  backend=a.backend, device=a.device)
    system = system_for(a.arm, a.system_file)
    out = []
    for i, p in enumerate(read_jsonl(a.prompts)):
        out.append({"id": p["id"], "kind": p.get("kind", "fresh"), "arm": a.arm, "prompt": p["prompt"],
                    "reply": g.reply(system, p["prompt"], seed=42 + i), "decoding": DECODING})
        print(json.dumps({"arm": a.arm, "done": i + 1}), flush=True)
    write_jsonl(a.out, out)


def cmd_sheet(a):
    A = {r["id"]: r for r in read_jsonl(a.first)}
    B = {r["id"]: r for r in read_jsonl(a.second)}
    rng = random.Random(a.seed)
    ids = [i for i in A if i in B and A[i]["kind"] in a.kinds.split(",")]
    key, cards = {}, []
    for n, i in enumerate(ids, 1):
        left, right = (A[i], B[i]) if rng.random() < 0.5 else (B[i], A[i])
        key[i] = {"A": left["arm"], "B": right["arm"]}
        cards.append(f"""<section><h2>{n}. {html.escape(A[i]['prompt'])}</h2>
<div class=pair><div><h3>A</h3><p>{html.escape(left['reply']).replace(chr(10), '<br>')}</p></div>
<div><h3>B</h3><p>{html.escape(right['reply']).replace(chr(10), '<br>')}</p></div></div>
<p class=q>Which sounds more like you?
{''.join(f'<label><input type=radio name="{html.escape(i)}" value="{v}"> {t}</label>' for v, t in [('A','A'),('B','B'),('both','Both equally'),('neither','Neither')])}</p></section>""")
    page = f"""<!doctype html><meta charset=utf-8><title>Which sounds like you?</title>
<style>body{{font:17px/1.5 system-ui;max-width:900px;margin:2em auto;padding:0 1em}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:1em}}
.pair div{{border:1px solid #ccc;border-radius:8px;padding:0 1em}}label{{margin-right:1.2em}}button{{font-size:18px;padding:.5em 1.2em}}</style>
<h1>Which one sounds more like you?</h1><p>Read each pair and pick the one that sounds more like something you would write.
There is no right answer. When you are done, press the button at the bottom; it saves a small file called <b>picks.json</b>.</p>
{''.join(cards)}
<button onclick="const p={{}};document.querySelectorAll('input:checked').forEach(e=>p[e.name]=e.value);
const b=new Blob([JSON.stringify(p,null,1)],{{type:'application/json'}});const l=document.createElement('a');
l.href=URL.createObjectURL(b);l.download='picks.json';l.click()">I'm done: save my picks</button>"""
    open(a.out, "w", encoding="utf-8").write(page)
    json.dump(key, open(a.key, "w"), indent=1)
    print(json.dumps({"pairs": len(ids), "sheet": a.out}))


def cmd_score(a):
    picks, key = json.load(open(a.picks)), json.load(open(a.key))
    t = {"mine": 0, "other": 0, "both": 0, "neither": 0, "unanswered": 0}
    for i, k in key.items():
        p = picks.get(i)
        if p in ("A", "B"):
            t["mine" if k[p] == "mine" else "other"] += 1
        elif p in ("both", "neither"):
            t[p] += 1
        else:
            t["unanswered"] += 1
    n = len(key)
    t["pairs"] = n
    t["accepted"] = t["mine"] >= math.ceil(0.6 * n) and t["neither"] < max(t["mine"], t["other"], t["both"])
    t["note"] = "personal preference on these prompts; tentative, not scientific evidence"
    print(json.dumps(t, indent=1))


def cmd_regurg(a, span=50):
    # any shared span of `span`+ characters = a shared window of exactly `span` characters
    train = [r["messages"][-1]["content"] for r in read_jsonl(a.train)]
    windows = {}
    for k, t in enumerate(train):
        for i in range(len(t) - span + 1):
            windows.setdefault(t[i:i + span], k)
    outs = read_jsonl(a.outputs)
    hits = []
    for r in outs:
        reply = r["reply"]
        for i in range(len(reply) - span + 1):
            w = reply[i:i + span]
            if w in windows and w not in r["prompt"] and not GREETINGS.match(w.strip()):
                t, j = train[windows[w]], train[windows[w]].index(w)
                n = span
                while i + n < len(reply) and j + n < len(t) and reply[i + n] == t[j + n]:
                    n += 1
                hits.append({"id": r["id"], "arm": r["arm"], "chars": n})
                break
    print(json.dumps({"outputs": len(outs), "flagged": len(hits), "hits": hits}))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("nll", "generate"):
        p = sp.add_parser(name)
        p.add_argument("--model", required=True)
        p.add_argument("--revision")
        p.add_argument("--adapter")
        p.add_argument("--arm", choices=["base", "card", "mine"], required=True)
        p.add_argument("--system-file")
        p.add_argument("--device", default="cpu")
    sp.choices["nll"].add_argument("--data", required=True)
    sp.choices["nll"].add_argument("--results", required=True)
    sp.choices["generate"].add_argument("--prompts", required=True)
    sp.choices["generate"].add_argument("--out", required=True)
    sp.choices["generate"].add_argument("--backend", default="hf", choices=["hf", "mlx"])
    sp.choices["generate"].add_argument("--threads", type=int, help="CPU threads; fewer is faster on a busy machine")
    p = sp.add_parser("sheet")
    p.add_argument("--first", required=True); p.add_argument("--second", required=True)
    p.add_argument("--out", required=True); p.add_argument("--key", required=True)
    p.add_argument("--kinds", default="fresh"); p.add_argument("--seed", type=int, default=7)
    p = sp.add_parser("score")
    p.add_argument("--picks", required=True); p.add_argument("--key", required=True)
    p = sp.add_parser("regurg")
    p.add_argument("--outputs", required=True); p.add_argument("--train", required=True)
    a = ap.parse_args()
    {"nll": cmd_nll, "generate": cmd_generate, "sheet": cmd_sheet, "score": cmd_score, "regurg": cmd_regurg}[a.cmd](a)


if __name__ == "__main__":
    main()
