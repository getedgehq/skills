"""Lane-side blind pairwise judge (stand-in for the person's own pick, which a book author cannot give).
Each pair is judged in both orders; if the two orders disagree it is a tie. Claude Sonnet via `claude -p`.
Usage: judge.py RUN_DIR [WORK_DIR]  (reads out-{mine,card,base}.jsonl, writes judge.jsonl + judge_summary.json)"""
import json, os, random, re, subprocess, sys
run = sys.argv[1]
W = sys.argv[2] if len(sys.argv) > 2 else "run/work"   # work dir with data/train.jsonl
out = {a: {r["id"]: r for r in map(json.loads, open(f"{run}/out-{a}.jsonl"))} for a in ("mine", "card", "base")}
train = [json.loads(l)["messages"][-1]["content"] for l in open(f"{W}/data/train.jsonl")]
refs = random.Random(3).sample(train, 3)
RUBRIC = ("You compare two replies by how much they read like the REFERENCE author: diction and favourite words, "
          "sentence rhythm and length, formality, characteristic moves (firm rules, contrasts, mild irony, addressing the reader). "
          "Ignore which is more helpful, correct or modern. Judge style only.")
items = []
for i, r in out["mine"].items():
    if r["kind"] not in ("fresh", "heldout"):
        continue
    for other in ("card", "base"):
        for order in ("mine_first", "other_first"):
            a, b = (r, out[other][i]) if order == "mine_first" else (out[other][i], r)
            items.append({"key": f"{i}|{other}|{order}", "prompt": r["prompt"], "A": a["reply"], "B": b["reply"]})
random.Random(5).shuffle(items)
done = {}
path = f"{run}/judge.jsonl"
if os.path.exists(path):
    for l in open(path):
        d = json.loads(l); done[d["key"]] = d["verdict"]
todo = [x for x in items if x["key"] not in done]
ref_txt = "\n\n".join(f"REFERENCE {k+1}:\n{t}" for k, t in enumerate(refs))
for s in range(0, len(todo), 8):
    batch = todo[s:s + 8]
    body = (RUBRIC + "\n\n" + ref_txt + "\n\nFor each item below answer which reply (A or B) reads more like the reference author, or TIE if truly equal. "
            "Items are independent. Return ONLY a JSON object mapping item number to \"A\", \"B\" or \"TIE\".\n\n" +
            "\n\n".join(f"ITEM {n+1}\nQuestion: {x['prompt']}\n--- Reply A ---\n{x['A']}\n--- Reply B ---\n{x['B']}" for n, x in enumerate(batch)))
    r = subprocess.run(["claude", "-p", "--model", "sonnet"], input=body, capture_output=True, text=True, timeout=900)
    m = re.search(r"\{.*\}", r.stdout, re.S)
    try:
        v = json.loads(m.group(0))
    except Exception:
        print("parse fail", s, r.stdout[:200]); continue
    with open(path, "a") as f:
        for n, x in enumerate(batch):
            verdict = str(v.get(str(n + 1), "")).upper()
            if verdict in ("A", "B", "TIE"):
                f.write(json.dumps({"key": x["key"], "verdict": verdict}) + "\n"); done[x["key"]] = verdict
    print("judged", min(s + 8, len(todo)), "of", len(todo), flush=True)

# combine orders: mine wins only if it wins in both orders
res = {}
for x in items:
    i, other, order = x["key"].split("|")
    v = done.get(x["key"])
    if v is None: continue
    mine_won = (v == "A") if order == "mine_first" else (v == "B")
    other_won = (v == "B") if order == "mine_first" else (v == "A")
    res.setdefault((i, other), []).append("mine" if mine_won else "other" if other_won else "tie")
summary = {}
kind = {i: r["kind"] for i, r in out["mine"].items()}
for other in ("card", "base"):
    for k in ("fresh", "heldout", "all"):
        sc = []
        for (i, o), vs in res.items():
            if o != other or len(vs) < 2 or (k != "all" and kind[i] != k): continue
            sc.append(1.0 if vs == ["mine", "mine"] else 0.0 if vs == ["other", "other"] else 0.5)
        if not sc: continue
        boots = []
        rng = random.Random(11)
        for _ in range(5000):
            smp = [rng.choice(sc) for _ in sc]; boots.append(sum(smp) / len(smp))
        boots.sort()
        summary[f"mine_vs_{other}_{k}"] = {"n": len(sc), "win_rate": round(sum(sc) / len(sc), 3),
            "ci95": [round(boots[124], 3), round(boots[4874], 3)],
            "wins": sc.count(1.0), "ties_or_split": sc.count(0.5), "losses": sc.count(0.0)}
json.dump(summary, open(f"{run}/judge_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
