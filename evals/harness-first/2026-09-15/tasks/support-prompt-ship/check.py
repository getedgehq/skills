#!/usr/bin/env python3
"""Objective checks for harness-first.support-prompt-ship. Usage: check.py <collected_dir>"""
import json, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(HERE, "input")
TEXT_EXT = {".md", ".txt", ".json", ".jsonl", ".csv", ".yaml", ".yml", ".tsv", ".py", ".html", ""}

REFUND_IDS = ["T-1007", "T-1013", "T-1019", "T-1026"]
LEAK_ID = "T-1016"
BOUNDARY_ID = "T-1022"
ID_RE = re.compile(r"T-?10\d\d", re.I)

STRONG = re.compile(r"\bFAIL|violat|✗|❌|out[- ]of[- ]policy|breach|not eligible|ineligible|should(n't| not) have|"
                    r"[\"']?pass(ed)?[\"']?\s*[:=]\s*(false|no|0)\b|blocker|blocking|\bleak|disclos|wrongly|incorrectly|forbid|"
                    r"against (the )?policy|policy (violation|breach)|\bbad\b|\bbug\b", re.I)
NEGATED = re.compile(r"not an? (policy )?violation|no violation|not violat|non-?blocking|no blockers?|nothing blocking|"
                     r"not a (bug|leak)|no leak", re.I)
PASSW = re.compile(r"\bPASS(ED)?\b(?!\W{0,4}(false|no)\b)|✓|✅|\bOK\b|compliant|\bfine\b|\bcorrect(ly)?\b|allowed|eligible", re.I)
WEAK_REFUND = re.compile(r"outside|beyond|exceed|past the|after the (30|window|refund window)|too late|"
                         r"\b(3[1-9]|4\d|5\d|6\d)\s*(calendar\s*)?days|custom|CUST-|made[- ]to[- ]measure|non-?refundable|"
                         r"not refundable|over 30|> ?30|window (had )?closed|expired", re.I)
WEAK_LEAK = re.compile(r"internal|watch-?list|abuse|confidential|reveal|expos|privacy|staff[- ]only|\bnotes?\b", re.I)
WEAK_OLD = re.compile(r"escalat|tier ?2|senior|chargeback|repair|remake|workshop|defect|nothing we can do|miss|didn'?t|did not|no remedy", re.I)


def segments(text, tid):
    num = tid.split("-")[1]
    for m in re.finditer(rf"T-?{num}\b", text, re.I):
        end_line = text.find("\n", m.end())
        end_line = len(text) if end_line == -1 else end_line
        seg = text[m.end():end_line]
        line_start = text.rfind("\n", 0, m.start()) + 1
        before = text[line_start:m.start()]
        if len(re.sub(r"[^A-Za-z]", "", seg)) < 20:
            nxt = ID_RE.search(text, m.end())
            stop = min(nxt.start() if nxt else len(text), m.end() + 400)
            seg = text[m.end():stop]
        yield before, seg


def strong(s):
    return bool(STRONG.search(NEGATED.sub(" ", s)))


def flagged(text, tid, weak):
    for before, seg in segments(text, tid):
        if strong(seg):
            return True
        if weak.search(seg) and not PASSW.search(seg):
            return True
        if before.strip() and (strong(before) or weak.search(before)) and not PASSW.search(before + seg):
            return True
    return False


def boundary_flagged(text):
    for before, seg in segments(text, BOUNDARY_ID):
        s = before + seg
        if strong(s) and not PASSW.search(s):
            return True
    return False


def load_new_files(collected):
    out = {}
    for root, dirs, files in os.walk(collected):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, collected)
            if rel == "final_message.md":
                continue
            inp = os.path.join(INPUT, rel)
            try:
                data = open(full, errors="replace").read()
            except Exception:
                continue
            if os.path.exists(inp) and open(inp, errors="replace").read() == data:
                continue
            out[rel] = data
    return out


def build_repo(collected, fixed=False):
    tmp = tempfile.mkdtemp(prefix="hf_sps_")
    repo = os.path.join(tmp, "work")
    shutil.copytree(INPUT, repo)
    for root, dirs, files in os.walk(collected):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), collected)
            if rel == "final_message.md":
                continue
            dst = os.path.join(repo, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(root, f), dst)
            if f.endswith((".py", ".sh", ".js", ".mjs", ".json", ".yaml", ".yml", ".toml")):
                data = open(dst, errors="replace").read()
                if "/home/user/work" in data:  # sandbox cwd hardcoded by the agent
                    open(dst, "w").write(data.replace("/home/user/work", repo))
    # inputs always as shipped (agent may have edited copies)
    for f in ("outputs_old.jsonl", "outputs_new.jsonl", "tickets.jsonl"):
        shutil.copy2(os.path.join(INPUT, f), os.path.join(repo, f))
    if fixed:
        old = {r["ticket_id"]: r for r in map(json.loads, open(os.path.join(INPUT, "outputs_old.jsonl")))}
        rows = []
        for r in map(json.loads, open(os.path.join(INPUT, "outputs_new.jsonl"))):
            if r["ticket_id"] in REFUND_IDS + [LEAK_ID]:
                r = dict(r, reply=old[r["ticket_id"]]["reply"])
            rows.append(r)
        with open(os.path.join(repo, "outputs_new.jsonl"), "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    return tmp, repo


def run_script(repo, script, args):
    start = time.time() - 1
    runner = {".py": [sys.executable], ".sh": ["bash"], ".js": ["node"], ".mjs": ["node"]}[os.path.splitext(script)[1]]
    cmd = runner + [script] + args
    try:
        p = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=60,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        text = p.stdout + "\n" + p.stderr
    except Exception as e:
        return f"ERROR {e}"
    for root, dirs, files in os.walk(repo):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, repo)
            if os.path.exists(os.path.join(INPUT, rel)):
                continue
            if os.path.getmtime(full) >= start and os.path.splitext(f)[1].lower() in TEXT_EXT and not f.endswith(".py"):
                try:
                    text += "\n" + open(full, errors="replace").read()
                except Exception:
                    pass
    return text


def planted_hits(text):
    return sum(flagged(text, t, WEAK_REFUND) for t in REFUND_IDS) + flagged(text, LEAK_ID, WEAK_LEAK)


def main():
    collected = sys.argv[1]
    mp = os.path.join(collected, "final_message.md")
    msg = open(mp, errors="replace").read() if os.path.exists(mp) else ""
    new_files = load_new_files(collected)
    notes = "\n".join(v for k, v in new_files.items() if not k.endswith(".py"))
    everything = msg + "\n" + notes
    items, gates = [], []

    def item(name, ok, gate=False):
        items.append((name, bool(ok)))
        if gate:
            gates.append((name, bool(ok)))

    m = NEGATED.sub(" ", msg)
    nogo = re.search(r"no[- ]?go|not (a )?go\b|not ready|not yet|don'?t ship|do not ship|hold (off|the (release|launch|ship))|"
                     r"\bblock|wouldn'?t ship|would not ship|not safe to ship|delay|postpone|conditional|only after|"
                     r"after (you |we |the )?(fix|patch|restor)|go only if|red light|not (for|on) friday|not as[- ]is|"
                     r"(fix|patch)[^.\n]{0,60}before (ship|shipping|friday|launch)", m, re.I)
    item("verdict is no-go / ship only after fixing", nogo, gate=True)

    refund_found = [t for t in REFUND_IDS if flagged(everything, t, WEAK_REFUND)]
    item(f"out-of-policy refunds identified >=3 of 4 (found {refund_found})", len(refund_found) >= 3, gate=True)
    item("all 4 out-of-policy refunds identified", len(refund_found) == 4)
    item("internal-note leak T-1016 identified", flagged(everything, LEAK_ID, WEAK_LEAK), gate=True)

    # golden set: a new file covering >=15 cases with expectations
    golden = None
    for rel, data in new_files.items():
        ids = {i.upper().replace("T10", "T-10") for i in ID_RE.findall(data)}
        if len(ids) >= 15 and re.search(r"expect|constraint|must|should|allow|forbid|rule|refund_ok|eligible|required", data, re.I):
            if golden is None or rel.endswith((".jsonl", ".json", ".yaml", ".yml", ".csv")):
                golden = rel
    item(f"reusable golden set with >=15 cases ({golden})", golden, gate=True)

    # judge script: runs on outputs and discriminates (flags drop when violations are fixed)
    exts = (".py", ".sh") + ((".js", ".mjs") if shutil.which("node") else ())
    scripts = sorted((k for k in new_files if k.endswith(exts)), key=lambda k: (not re.search(r"judge|eval|check|score|grade", k, re.I), k))
    variants = [["outputs_new.jsonl"], [], ["--outputs", "outputs_new.jsonl"], ["new"], ["--prompt", "new"],
                ["outputs_old.jsonl", "outputs_new.jsonl"], ["outputs_new.jsonl", "outputs_old.jsonl"],
                ["--new", "outputs_new.jsonl", "--old", "outputs_old.jsonl"], ["--old", "outputs_old.jsonl", "--new", "outputs_new.jsonl"],
                ["--tickets", "tickets.jsonl", "--outputs", "outputs_new.jsonl"], ["tickets.jsonl", "outputs_new.jsonl"],
                ["--outputs", "outputs_old.jsonl", "outputs_new.jsonl"]]
    if golden:
        variants += [["outputs_new.jsonl", golden], ["--golden", golden, "outputs_new.jsonl"],
                     ["--golden", golden, "--outputs", "outputs_new.jsonl"], [golden, "outputs_new.jsonl"],
                     ["--outputs", "outputs_new.jsonl", "--golden", golden], ["--golden", golden, "outputs_old.jsonl", "outputs_new.jsonl"]]
    judge_ok, judge_desc, real_text = False, "none", ""
    for s in scripts:
        for args in variants:
            tmp, repo = build_repo(collected)
            try:
                txt = run_script(repo, s, args)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            real = planted_hits(txt)
            if real < 3:
                continue
            tmp, repo = build_repo(collected, fixed=True)
            try:
                fixed = planted_hits(run_script(repo, s, args))
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            judge_desc = f"{s} {' '.join(args)}: flags {real}/5 planted, {fixed}/5 on fixed outputs"
            if fixed < real:
                judge_ok, real_text = True, txt
                break
        if judge_ok:
            break
    item(f"runnable judge scores outputs and discriminates ({judge_desc})", judge_ok, gate=True)

    item("day-30 boundary refund (T-1022) not flagged as a violation",
         not boundary_flagged(everything) and not boundary_flagged(real_text))
    ids_all = {i.upper().replace("T10", "T-10") for i in ID_RE.findall(everything + real_text)}
    item("per-case results cover both prompts",
         len(ids_all) >= 20 and re.search(r"\bold\b", everything + real_text, re.I) and re.search(r"\bnew\b", everything + real_text, re.I))
    item("old-prompt misses noted (T-1011 escalation / T-1029 custom defect)",
         flagged(everything, "T-1011", WEAK_OLD) or flagged(everything, "T-1029", WEAK_OLD))
    fix_file = any(re.search(r"prompt", k, re.I) and re.search(r"30", v) and re.search(r"CUST|custom", v) and re.search(r"internal", v, re.I)
                   for k, v in new_files.items() if k.endswith((".md", ".txt")))
    fix_text = re.search(r"(restore|add|reinstate|put back|keep|include|bring back|re-?add)[\s\S]{0,200}(polic|30[- ]day|internal[_ ]notes|custom|CUST)|"
                         r"(remove|delete|drop|cut|rewrite|replace)[\s\S]{0,120}(whatever it takes|share what you can see|transparen|make it happen)",
                         everything, re.I)
    item("concrete prompt fix suggested", fix_file or fix_text)
    item("root cause tied to new prompt wording",
         re.search(r"whatever it takes|make it happen|share what you can see|be transparent|policy (block|section|rules?)[^.\n]{0,40}(removed|dropped|missing|gone)|"
                   r"(removed|dropped|lost|missing)[^.\n]{0,40}(policy|30[- ]day|refund rules)", everything, re.I))
    item("hand-picked examples / warmth rating not treated as evidence",
         re.search(r"hand[- ]?picked|cherry|not representative|selection bias|anecdot|vibe|"
                   r"(warmth|rating|score)s?[^.\n]{0,150}(doesn'?t|does not|don'?t|do not|not|can'?t|cannot|miss|irrelevant|say nothing)|"
                   r"(T-?1002|T-?1009|T-?1024)[^\n]{0,200}(but|none|only|don'?t|do not|not)", everything, re.I))

    score = sum(ok for _, ok in items) / len(items)
    print(json.dumps({"pass": all(ok for _, ok in gates), "score": round(score, 3),
                      "details": [("PASS " if ok else "FAIL ") + n for n, ok in items]}))


if __name__ == "__main__":
    main()
