#!/usr/bin/env python3
"""Objective checks for harness-first.sales-agent-token-burn. Usage: check.py <collected_dir>"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "input")

LOOP_IDS = ["cv_24a92f", "cv_488aab", "cv_a99bb9", "cv_15f5fe"]
NOISY_ID = "cv_6f895a"
LOOP_SHARE = 69.8  # % of tokens; cost share is 69.2
SHARE_TOL = 6.0
LOOP_COST = 18.43  # USD of 26.66 total

REPORT_EXT = {".md", ".txt", ".rst", ""}
TEXT_EXT = REPORT_EXT | {".py", ".json", ".jsonl", ".yaml", ".yml", ".diff", ".patch", ".toml", ".cfg", ".csv", ".sh"}
MODELS = r"(haiku|gpt-?5-?mini|gpt|gemini|flash|deepseek|mini\b|cheaper model|smaller model)"

FAKE = r'''
import sys, json, importlib, time
sys.path.insert(0, ".")
time.sleep = lambda *a, **k: None
LIMIT = 300
class Sentinel(BaseException): pass
class Usage(dict):
    def __getattr__(self, k):
        try: return self[k]
        except KeyError: raise AttributeError(k)
class Call:
    def __init__(self, i):
        self.id = f"t{i}"; self.name = "crm_update_contact"; self.type = "tool_use"
        self.arguments = {"contact_id": "ct_1", "fields": {"lead_score_v2": 91}}; self.input = self.arguments
class Resp:
    def __init__(self, i):
        self.tool_calls = [Call(i)]
        self.content = [{"type": "tool_use", "id": f"t{i}", "name": "crm_update_contact", "input": self.tool_calls[0].arguments}]
        self.text = ""; self.stop_reason = "tool_use"; self.model = "fake"
        self.input_tokens = 60000; self.output_tokens = 400; self.cost_usd = 0.186
        self.usage = Usage(input_tokens=60000, output_tokens=400, cost_usd=0.186)
    def __getitem__(self, k): return getattr(self, k)
    def get(self, k, d=None): return getattr(self, k, d)
class FakeLLM:
    n = 0
    model = "fake"
    def complete(self, *a, **k):
        FakeLLM.n += 1
        if FakeLLM.n > LIMIT: raise Sentinel()
        return Resp(FakeLLM.n)
    __call__ = complete
    chat = complete
    create = complete
for modname in ("agent.tracing",):
    try:
        m = importlib.import_module(modname)
        for name in dir(m):
            if name.startswith("log") and callable(getattr(m, name)):
                setattr(m, name, lambda *a, **k: None)
    except Exception:
        pass
tools_mod = importlib.import_module("agent.tools")
ToolErr = getattr(tools_mod, "ToolError", Exception)
def mkerr():
    msg = '422 Unprocessable Entity: {"error":"validation_failed","detail":"unknown field","field":"lead_score_v2"}'
    for args in ((msg,), ):
        for kw in ({"status": 422}, {}):
            try:
                e = ToolErr(*args, **kw)
                try: e.status = 422
                except Exception: pass
                return e
            except TypeError:
                continue
    try: return ToolErr(msg, 422)
    except Exception: return Exception(msg)
class FakeTools:
    def schemas(self): return []
    def execute(self, name, arguments=None, *a, **k):
        if name == "crm_get_account": return {"account": "acc_1"}
        if name == "send_email": return {"sent": True}
        raise mkerr()
    def crm_update_contact(self, *a, **k): raise mkerr()
    def crm_get_account(self, *a, **k): return {"account": "acc_1"}
    def send_email(self, *a, **k): return {"sent": True}
loop = importlib.import_module("agent.loop")
for name in dir(loop):
    if name.startswith("log") and callable(getattr(loop, name)):
        setattr(loop, name, lambda *a, **k: None)
fn = getattr(loop, "run_conversation")
out = {"calls": 0, "terminated": False, "inconclusive": True, "exc": None}
attempts = [lambda: fn("L-1", llm=FakeLLM(), tools=FakeTools(), conversation_id="cv_test"),
            lambda: fn("L-1", llm=FakeLLM(), tools=FakeTools()),
            lambda: fn("L-1", FakeLLM(), FakeTools())]
for att in attempts:
    FakeLLM.n = 0
    try:
        att()
        out.update(calls=FakeLLM.n, terminated=True, inconclusive=FakeLLM.n == 0)
    except Sentinel:
        out.update(calls=FakeLLM.n, terminated=False, inconclusive=False)
    except TypeError as e:
        if FakeLLM.n == 0:
            out["exc"] = "TypeError: " + str(e)[:200]
            continue
        out.update(calls=FakeLLM.n, terminated=True, inconclusive=False, exc="TypeError: " + str(e)[:200])
    except BaseException as e:
        out.update(calls=FakeLLM.n, terminated=True, inconclusive=FakeLLM.n == 0, exc=type(e).__name__ + ": " + str(e)[:200])
    break
print("RESULT" + json.dumps(out))
'''


def read(p):
    try:
        return open(p, errors="replace").read()
    except OSError:
        return ""


def collect(collected):
    report, alltext, files = [], [], {}
    for root, dirs, fs in os.walk(collected):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fs:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, collected)
            ext = os.path.splitext(f)[1].lower()
            files[rel] = p
            if rel == "final_message.md":
                continue
            if ext in TEXT_EXT and os.path.getsize(p) < 2_000_000:
                txt = read(p)
                alltext.append(txt)
                if ext in REPORT_EXT:
                    report.append(txt)
    return report, alltext, files


def overlay(collected):
    tmp = tempfile.mkdtemp(prefix="hf_sales_")
    repo = os.path.join(tmp, "repo")
    shutil.copytree(INPUT, repo)
    for root, dirs, fs in os.walk(collected):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), collected)
            if rel == "final_message.md":
                continue
            dst = os.path.join(repo, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(root, f), dst)
    return tmp, repo


def behavioral_cap(collected):
    tmp, repo = overlay(collected)
    try:
        open(os.path.join(repo, "_fake_run.py"), "w").write(FAKE)
        p = subprocess.run([sys.executable, "_fake_run.py"], cwd=repo, capture_output=True, text=True, timeout=60,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "BK_TRACE_PATH": os.path.join(tmp, "t.jsonl")})
        line = [l for l in p.stdout.splitlines() if l.startswith("RESULT")]
        if not line:
            return {"inconclusive": True, "err": p.stderr[-300:]}
        return json.loads(line[-1][6:])
    except subprocess.TimeoutExpired:
        return {"inconclusive": False, "terminated": False, "calls": None, "err": "timeout"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def near(a, b, text, gap=250):
    return re.search(rf"(?:{a})[\s\S]{{0,{gap}}}(?:{b})|(?:{b})[\s\S]{{0,{gap}}}(?:{a})", text, re.I)


def main():
    collected = sys.argv[1]
    msg = read(os.path.join(collected, "final_message.md"))
    report_files, alltext_files, files = collect(collected)
    report = msg + "\n" + "\n".join(report_files)
    everything = msg + "\n" + "\n".join(alltext_files)
    items, gates = [], []

    def item(name, ok, gate=False):
        items.append((name, bool(ok)))
        if gate:
            gates.append((name, bool(ok)))

    # 1. mechanism: deterministic 422 on lead_score_v2 + retry/loop with no stop
    mech = near(r"422|lead_score_v2|unknown field|invalid field|validation", r"retr|loop|never (stops|ends|finish)|keeps? (calling|trying)|over and over|until .{0,40}(context|overflow|too long)|infinite|max(imum)?[ _-]?(iter|turn|step)", report, 300)
    item("retry-loop mechanism on the 422 / lead_score_v2 write identified", mech, gate=True)

    # 2. dominating conversations or share
    ids_named = [c for c in LOOP_IDS if c in report]
    share_ok = False
    for m in re.finditer(r"(\d{2}(?:\.\d+)?)\s?%", report):
        v = float(m.group(1))
        if abs(v - LOOP_SHARE) <= SHARE_TOL:
            ctx = report[max(0, m.start() - 300): m.end() + 300]
            if re.search(r"loop|retr|422|lead_score_v2|conversations|cv_|four|three", ctx, re.I) and not re.search(r"sav|cheaper", ctx, re.I):
                share_ok = True
                break
    cost_ok = False
    for m in re.finditer(r"\$\s?1[78](\.\d+)?|\$\s?19(\.[0-4]\d*)?\b", report):
        ctx = report[max(0, m.start() - 200): m.end() + 200]
        if re.search(r"loop|retr|422|lead_score_v2|cv_|conversations", ctx, re.I) and not re.search(r"sav", ctx, re.I):
            cost_ok = True
            break
    item("dominating conversations named (>=3 of 4 ids) or their ~70% share quantified",
         len(ids_named) >= 3 or share_ok or cost_ok, gate=True)
    item("noisy cv_6f895a not blamed as the main cost driver",
         not re.search(rf"{NOISY_ID}[^\n.]{{0,120}}(main|biggest|largest|primary|root cause|culprit|most expensive|drives?)", report, re.I))

    # 3. no unconditional model switch
    hold = (re.search(r"(don'?t|do not|wouldn'?t|would not|not|no need to|hold off|before|shouldn'?t|should not)\s+(\w+\s+){0,3}(switch|swap|chang|downgrad|mov|migrat|flip)", report, re.I)
            or re.search(r"not (really |primarily |mainly )?(a |the )?model(-| )(problem|issue|cost)", report, re.I)
            or near(r"eval|golden|benchmark|compare|a/b|side-by-side|test set", r"model|haiku|cheaper|swap|switch", report, 200) and near(r"fix|stop|cap|loop|retr", r"first|before|then", report, 200))
    uncond = []
    for s in sentences(report):
        if re.search(rf"(switch|swap|move|migrat|downgrad|go with|pick|use|recommend|flip)\w*[^.\n]{{0,60}}{MODELS}", s, re.I):
            if not re.search(r"\b(after|once|if|only|eval|golden|compar|test|benchmark|don'?t|do not|not|before|candidate|consider|later|then|could|might|may|option|instead of|rather than|until|should we|\?)", s, re.I):
                uncond.append(s.strip()[:120])
    item("does not recommend an unconditional model switch (fix/eval first)", hold and not uncond, gate=True)

    # 4. send_email approval gap
    item("flags send_email firing without approval",
         near(r"send_email|send[ -]email|sends? (real |actual |live )?e-?mails?|outbound e-?mail|mailer", r"approv|human[ -]in|human review|review step|confirm|draft|gate|sign-?off|guardrail|dry[ -]?run|unsupervised|no (check|limit|guard)", everything, 300),
         gate=True)

    # 5. cap in code (behavioral) or concrete patch
    loop_changed = any(r.replace("\\", "/").endswith("agent/loop.py") for r in files)
    beh = behavioral_cap(collected) if loop_changed else {"inconclusive": True, "skipped": True}
    cap_re = r"max[_ ]?(turns|iter\w*|steps|calls|rounds)|MAX_(TURNS|ITER\w*|STEPS|CALLS|ROUNDS)|budget|cost[_ ]?cap|token[_ ]?(cap|budget|limit)|max[_ ]?(cost|tokens_per_(run|conv\w*))"
    if not beh.get("inconclusive"):
        cap_ok = bool(beh.get("terminated")) and (beh.get("calls") or 0) <= 60
    else:
        patches = [read(p) for r, p in files.items() if os.path.splitext(r)[1].lower() in {".py", ".diff", ".patch"} or (r.endswith(".md") and "```" in read(p))]
        cap_ok = any(re.search(cap_re, t) and re.search(r"(>=|>|<=|<|range\()", t) for t in patches)
    item(f"max-iterations / cost cap enforced (behavioral={beh})", cap_ok, gate=True)

    # scored extras
    item("root field named: lead_score_v2 not in CRM schema",
         re.search(r"lead_score_v2", report) and near(r"lead_score_v2", r"schema|doesn'?t exist|does not exist|not (a )?(valid|writable|existing|defined)|unknown|invalid|custom field|admin|not in", report, 250))
    per_conv = sum(1 for c in LOOP_IDS if re.search(rf"{c}[^\n]{{0,160}}(\d[\d,.]*\s?(k|m|tokens|calls)|\$\s?\d)", report, re.I))
    item("per-conversation numbers for the loop conversations (>=3)", per_conv >= 3)
    item("full account export re-sent every turn identified",
         near(r"crm_get_account|account export|full export|export|dump", r"every turn|each turn|every (loop )?iteration|each iteration|re-?fetch|re-?load|re-?sent|resend|fetch\w* (it )?again|accumulat|grows?|piles? up", report, 200))
    code_texts = [read(p) for r, p in files.items() if r.endswith(".py")]
    nontransient = (near(r"non-?transient|4xx|client error|422|deterministic|permanent", r"retr", everything, 200)
                    and (any(re.search(r"429|>=\s*500|5\d\d|transient|RETRYABLE|retryable", t, re.I) for t in code_texts)
                         or near(r"don'?t|do not|never|stop|only", r"retr", report, 60)))
    item("stops retrying non-transient errors (retry only 429/5xx)", nontransient)

    golden = False
    for rel, p in files.items():
        if not re.search(r"golden|eval|case|regression|test", rel, re.I):
            continue
        ext = os.path.splitext(rel)[1].lower()
        t = read(p)
        n = 0
        if ext == ".jsonl":
            for l in t.splitlines():
                try:
                    json.loads(l); n += 1
                except Exception:
                    pass
        elif ext == ".json":
            try:
                d = json.loads(t)
                d = d.get("cases", d.get("examples", d)) if isinstance(d, dict) else d
                n = len(d) if isinstance(d, (list, dict)) else 0
            except Exception:
                pass
        elif ext in {".yaml", ".yml"}:
            n = len(re.findall(r"(?m)^\s*-\s+(id|name|input|lead|case)\s*:", t))
        elif ext == ".csv":
            n = max(0, len([l for l in t.splitlines() if l.strip()]) - 1)
        elif ext == ".py":
            n = len(re.findall(r"(?m)^\s*(def test_|\{\s*[\"'](id|name|input|lead)[\"']\s*:)", t))
        elif ext == ".md":
            n = len(re.findall(r"(?m)^\s*(\|\s*[A-Za-z]*-?\d+|#{2,4}\s*(case|G|GS|T)[-_ ]?\d+)", t, ))
        if n >= 10:
            golden = True
            break
    item("golden set with >=10 cases written", golden)

    score = sum(ok for _, ok in items) / len(items)
    print(json.dumps({"pass": all(ok for _, ok in gates), "score": round(score, 3),
                      "details": [("PASS " if ok else "FAIL ") + n for n, ok in items] + ([f"unconditional switch: {uncond[:2]}"] if uncond else [])}))


if __name__ == "__main__":
    main()
