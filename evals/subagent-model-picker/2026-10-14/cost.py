"""Recompute cost per run from transcripts with explicit list prices. Usage: cost.py RUNSDIR"""
import json, sys, glob, os, pathlib, statistics as st
P = {  # in, out, cw5m, cw1h, cr  ($/MTok)
 "claude-opus-5-5": (4, 20, 5, 8, 0.20),
 "claude-sonnet-5-5": (2, 10, 2.5, 4, 0.20),
 "claude-sonnet-5": (2, 10, 2.5, 4, 0.20),
 "claude-haiku-4-5-20251001": (1, 5, 1.25, 2, 0.10),
 "claude-fable-5-1": (10, 50, 12.5, 20, 0.25),
}
runs = pathlib.Path(sys.argv[1]); home = os.path.expanduser("~/.claude/projects")
out = {}
for gj in sorted(runs.glob("*.grade.json")):
    rid = gj.name.split(".")[0]
    raw = (runs / f"{rid}.json").read_text(); g = json.loads(gj.read_text())
    proj = glob.glob(f"{home}/*mp-bench2-runs-{rid}")[0]
    if raw.strip():
        d = json.loads(raw)
    else:  # lead exited without a result: take the session from its transcript
        (j,) = glob.glob(f"{proj}/*.jsonl")
        d = {"session_id": os.path.basename(j)[:-6], "total_cost_usd": None, "is_error": "no_result_json"}
    sid = d["session_id"]
    files = [f"{proj}/{sid}.jsonl"] + glob.glob(f"{proj}/{sid}/subagents/*.jsonl")
    msgs = {}
    sub_models = []
    for f in files:
        first = True
        for line in open(f):
            try: e = json.loads(line)
            except Exception: continue
            m = e.get("message") or {}
            if e.get("type") == "assistant" and m.get("usage") and m.get("model"):
                msgs[(f, m.get("id"))] = (m["model"], m["usage"])
                if "subagents" in f and first: sub_models.append(m["model"]); first = False
    cost = 0.0; per = {}
    for (f, _), (model, u) in msgs.items():
        if model == "<synthetic>": continue
        pi, po, p5, p1, pr = P[model]
        cc = u.get("cache_creation") or {}
        c5 = cc.get("ephemeral_5m_input_tokens", 0); c1 = cc.get("ephemeral_1h_input_tokens", 0)
        if not cc: c5 = u.get("cache_creation_input_tokens", 0)
        c = (u.get("input_tokens", 0) * pi + u.get("output_tokens", 0) * po + c5 * p5 + c1 * p1
             + u.get("cache_read_input_tokens", 0) * pr) / 1e6
        cost += c; per[model] = per.get(model, 0) + c
    out[rid] = {"cost": cost, "cli_cost": d["total_cost_usd"], "per_model": per, "subagent_models": sorted(sub_models),
                "modelUsage_ids": sorted(d.get("modelUsage", {})), "score": g["score"], "max": g["max"],
                "tests_green": g["visible_tests_green"], "is_error": d.get("is_error"),
                "tasks": {k: f'{g[k]["pass"]}/{g[k]["total"]}' for k in ("inventory","dates","allocate","config")}}
summ = {}
for C in "AB":
    rs = [v for k, v in out.items() if k.startswith(C + "-")]
    if not rs: continue
    cs = [r["cost"] for r in rs]
    summ[C] = {"n": len(rs), "mean": st.mean(cs), "sd": st.stdev(cs) if len(cs) > 1 else 0, "min": min(cs), "max": max(cs),
               "median": st.median(cs), "full_pass": sum(r["score"] == r["max"] and r["tests_green"] for r in rs),
               "checks": f'{sum(r["score"] for r in rs)}/{sum(r["max"] for r in rs)}',
               "cli_mean": st.mean(r["cli_cost"] for r in rs if r["cli_cost"] is not None),
               "no_result_json": [k for k, v in out.items() if k.startswith(C + "-") and v["is_error"] == "no_result_json"]}
print(json.dumps({"summary": summ, "runs": out}, indent=1))
