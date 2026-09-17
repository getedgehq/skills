#!/usr/bin/env python3
"""skill-cockpit: a local browser cockpit for the self-improvement loop.

Usage: cockpit.py [--port 7788] [--forge-root ~/skill-forge] [--skills-dir DIR ...]

Serves one page on 127.0.0.1 showing:
  - the installed skill fleet (with each skill's forge status from the ledger)
  - candidates: drafted skills + scored registry/local matches
  - every eval: blind verdict, verify exits, tool errors, gate decision
  - mined failures (task vs infra) and the jobs this cockpit started
and lets the user start loop stages (mine, dry run, full loop, eval, recheck).

Stdlib only. Nothing leaves the machine; evals run with the user's own agent CLI.
Actions require a per-process token embedded in the page, so other sites in the
browser cannot trigger evals (no CSRF against localhost).
"""
import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = secrets.token_urlsafe(24)
JOBS = {}
JOBS_LOCK = threading.Lock()


def sibling(skill, env):
    """Scripts of a sibling skill (skill-miner / skill-eval-loop)."""
    if os.environ.get(env):
        return os.environ[env]
    for base in (os.path.join(HERE, "..", ".."), os.path.expanduser("~/.agents/skills"),
                 os.path.expanduser("~/.claude/skills")):
        p = os.path.realpath(os.path.join(base, skill, "scripts"))
        if os.path.isdir(p):
            return p
    return ""


def read_json(path, default=None):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def frontmatter(skill_md):
    try:
        text = open(skill_md, errors="replace").read(6000)
    except OSError:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    desc = re.search(r"^description:\s*(.+?)(?=^\w[\w-]*:|\Z)", fm, re.MULTILINE | re.DOTALL)
    d = " ".join(desc.group(1).split()) if desc else ""
    return {"name": (name.group(1).strip().strip("\"'") if name else ""),
            "description": d.strip("\"'")}


def list_skills(root):
    out = []
    if not os.path.isdir(root):
        return out
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        md = os.path.join(path, "SKILL.md")
        if not os.path.isfile(md):
            continue
        fm = frontmatter(md) or {"name": entry, "description": ""}
        out.append({
            "dir": entry,
            "name": fm["name"] or entry,
            "description": fm["description"],
            "path": path,
            "link": os.path.realpath(path) if os.path.islink(path) else None,
            "mtime": int(os.path.getmtime(md)),
        })
    return out


def ledger_rows(root):
    rows = []
    try:
        with open(os.path.join(root, "ledger.jsonl")) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return rows


def skill_status(rows):
    """Latest forge decision per skill name. recheck verdicts supersede probation."""
    status = {}
    for r in rows:
        if r.get("skill"):
            status[r["skill"]] = r.get("decision")
    return status


def running_eval(brief_id):
    with JOBS_LOCK:
        return any(j["status"] == "running" and j["label"].endswith(" on " + brief_id)
                   for j in JOBS.values())


def state(cfg):
    root = cfg.forge_root
    rows = ledger_rows(root)
    status = skill_status(rows)

    fleet, seen = [], set()
    for d in cfg.skills_dirs:
        for s in list_skills(d):
            # same skill symlinked or copied into several pools counts once
            key = s["dir"]
            if key in seen:
                continue
            seen.add(key)
            s["pool"] = d
            s["forge"] = status.get(s["dir"]) or status.get(s["name"])
            fleet.append(s)

    drafts = []
    for s in list_skills(os.path.join(root, "drafts")):
        s["forge"] = status.get(s["dir"]) or status.get(s["name"])
        s["installed"] = any(f["dir"] == s["dir"] for f in fleet)
        drafts.append(s)

    scored = read_json(os.path.join(root, "mined", "scored.json"), {}) or {}
    candidates = scored.get("scored", [])
    for c in candidates:
        c["forge"] = status.get(c.get("name"))

    evals = []
    runs_dir = os.path.join(root, "runs")
    ledger_by_brief = {}
    for r in rows:
        if r.get("brief"):
            ledger_by_brief[r["brief"]] = r
    if os.path.isdir(runs_dir):
        for rid in os.listdir(runs_dir):
            v = read_json(os.path.join(runs_dir, rid, "verdict.json"))
            runs = {a: read_json(os.path.join(runs_dir, rid, a + ".meta", "run.json"))
                    for a in ("without", "with")}
            brief = read_json(os.path.join(root, "briefs", rid + ".json"), {}) or {}
            led = ledger_by_brief.get(rid)
            evals.append({
                "id": rid,
                "prompt": brief.get("prompt", ""),
                "rubric": brief.get("rubric"),
                "verdict": v,
                "runs": runs,
                "ledger": led,
                "stage": ("gated" if led else "judged" if v else
                          "running" if running_eval(rid) else
                          "incomplete" if os.path.isdir(os.path.join(runs_dir, rid, "without")) else "empty"),
                "mtime": int(os.path.getmtime(os.path.join(runs_dir, rid))),
            })
    evals.sort(key=lambda e: -e["mtime"])

    briefs = sorted(f[:-5] for f in os.listdir(os.path.join(root, "briefs"))
                    if f.endswith(".json")) if os.path.isdir(os.path.join(root, "briefs")) else []

    failures = read_json(os.path.join(root, "mined", "failures.json"), {}) or {}
    with JOBS_LOCK:
        jobs = [{k: v for k, v in j.items() if k != "proc"} for j in JOBS.values()]
    for j in jobs:
        j["tail"] = tail(j["log"], 60)

    return {
        "forge_root": root,
        "skills_dirs": cfg.skills_dirs,
        "scripts": {"miner": sibling("skill-miner", "MINER_SCRIPTS"),
                    "eval": sibling("skill-eval-loop", "EVAL_SCRIPTS")},
        "fleet": fleet,
        "drafts": drafts,
        "candidates": candidates,
        "candidate_failure": scored.get("failure"),
        "evals": evals,
        "briefs": briefs,
        "ledger": rows,
        "failures": {
            "generated": failures.get("generated"),
            "sessions_scanned": failures.get("sessions_scanned"),
            "clusters": failures.get("clusters", []),
            "anger": failures.get("anger", [])[:40],
            "anger_count": len(failures.get("anger", [])),
            "top_spend_sessions": failures.get("top_spend_sessions", [])[:10],
        },
        "jobs": sorted(jobs, key=lambda j: -j["started"]),
    }


def tail(path, n):
    try:
        with open(path, errors="replace") as fh:
            return "".join(fh.readlines()[-n:])
    except OSError:
        return ""


# ---- actions -------------------------------------------------------------

def build_command(cfg, body):
    """Whitelisted loop stages only. Returns (label, argv) or raises ValueError."""
    action = body.get("action")
    miner = sibling("skill-miner", "MINER_SCRIPTS")
    ev = sibling("skill-eval-loop", "EVAL_SCRIPTS")
    sessions = str(int(body.get("sessions") or 40))
    projects = cfg.projects

    if action == "mine":
        return "mine sessions", [sys.executable, os.path.join(miner, "mine.py"), "--sessions", sessions,
                                 "--projects", projects, "--out",
                                 os.path.join(cfg.forge_root, "mined", "failures.json")]
    if action in ("dry-run", "loop"):
        argv = ["bash", os.path.join(ev, "forge.sh"), "--sessions", sessions]
        if body.get("cluster_index") not in (None, ""):
            argv += ["--cluster-index", str(int(body["cluster_index"]))]
        if action == "dry-run":
            argv.append("--dry-run")
        return ("dry run (no eval spend)" if action == "dry-run" else "full loop"), argv
    if action == "recheck":
        return "probation recheck", [sys.executable, os.path.join(ev, "recheck.py"),
                                     "--projects", projects, "--sessions", sessions]
    if action == "eval":
        brief_id = body.get("brief", "")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", brief_id):
            raise ValueError("bad brief id")
        brief = os.path.join(cfg.forge_root, "briefs", brief_id + ".json")
        if not os.path.isfile(brief):
            raise ValueError("brief not found")
        skill = os.path.realpath(body.get("skill_path", ""))
        allowed = [os.path.realpath(os.path.join(cfg.forge_root, "drafts"))] + \
                  [os.path.realpath(d) for d in cfg.skills_dirs]
        if not (os.path.isfile(os.path.join(skill, "SKILL.md")) and
                any(skill.startswith(a + os.sep) for a in allowed)):
            raise ValueError("skill must be a draft or an installed skill")
        if os.path.exists(os.path.join(cfg.forge_root, "runs", brief_id)):
            raise ValueError("this brief already has a run - evals are never overwritten; "
                             "re-brief under a new id")
        script = " && ".join([
            'bash "$EV/run_eval.sh" "$BRIEF" without ""',
            'bash "$EV/run_eval.sh" "$BRIEF" with "$SKILL"',
            'python3 "$EV/judge.py" "$BRIEF"',
            'python3 "$EV/gate.py" "$BRIEF" "$SKILL"' + (" --probation" if body.get("probation") else ""),
        ])
        return (f"eval {os.path.basename(skill)} on {brief_id}",
                ["bash", "-c", script],
                {"EV": ev, "BRIEF": brief, "SKILL": skill})
    raise ValueError("unknown action")


def start_job(cfg, body):
    spec = build_command(cfg, body)
    label, argv = spec[0], spec[1]
    extra_env = spec[2] if len(spec) > 2 else {}
    with JOBS_LOCK:
        if any(j["status"] == "running" for j in JOBS.values()):
            raise ValueError("a job is already running - one at a time keeps eval spend visible")
    jid = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)
    jobs_dir = os.path.join(cfg.forge_root, "cockpit", "jobs")
    os.makedirs(jobs_dir, exist_ok=True)
    log = os.path.join(jobs_dir, jid + ".log")
    env = dict(os.environ, FORGE_ROOT=cfg.forge_root, FORGE_PROJECTS=cfg.projects, **extra_env)
    if sibling("skill-miner", "MINER_SCRIPTS"):
        env.setdefault("MINER_SCRIPTS", sibling("skill-miner", "MINER_SCRIPTS"))
    fh = open(log, "w")
    fh.write("$ " + " ".join(argv) + "\n")
    fh.flush()
    proc = subprocess.Popen(argv, stdout=fh, stderr=subprocess.STDOUT, env=env,
                            cwd=cfg.forge_root, start_new_session=True)
    job = {"id": jid, "label": label, "status": "running", "started": int(time.time()),
           "ended": None, "exit": None, "log": log, "proc": proc}
    with JOBS_LOCK:
        JOBS[jid] = job

    def wait():
        code = proc.wait()
        fh.close()
        with JOBS_LOCK:
            job.update(status="done" if code == 0 else "failed", exit=code, ended=int(time.time()))
    threading.Thread(target=wait, daemon=True).start()
    return jid


# ---- http ----------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    cfg = None

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self.host_ok():
            return self.send(403, {"error": "host not allowed"})
        if self.path in ("/", "/index.html"):
            html = open(os.path.join(HERE, "cockpit.html"), encoding="utf-8").read()
            return self.send(200, html.replace("__COCKPIT_TOKEN__", TOKEN).encode(),
                             "text/html; charset=utf-8")
        if self.path == "/api/state":
            return self.send(200, state(self.cfg))
        return self.send(404, {"error": "not found"})

    def do_POST(self):
        if not self.host_ok() or self.headers.get("X-Cockpit-Token") != TOKEN:
            return self.send(403, {"error": "forbidden"})
        if self.path != "/api/jobs":
            return self.send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
            jid = start_job(self.cfg, body)
        except (ValueError, TypeError) as e:
            return self.send(400, {"error": str(e)})
        return self.send(200, {"job": jid})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("COCKPIT_PORT", 7788)))
    ap.add_argument("--forge-root", default=os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge")))
    ap.add_argument("--projects", default=os.environ.get("FORGE_PROJECTS", os.path.expanduser("~/.claude/projects")))
    ap.add_argument("--skills-dir", action="append", dest="skills_dirs")
    ap.add_argument("--dump", action="store_true", help="print state JSON and exit")
    cfg = ap.parse_args()
    cfg.forge_root = os.path.abspath(os.path.expanduser(cfg.forge_root))
    cfg.skills_dirs = [os.path.expanduser(d) for d in (cfg.skills_dirs or
                       ["~/.claude/skills", "~/.agents/skills"])]
    os.makedirs(cfg.forge_root, exist_ok=True)
    if cfg.dump:
        print(json.dumps(state(cfg), indent=1))
        return
    Handler.cfg = cfg
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", cfg.port), Handler)
    except OSError as e:
        sys.exit(f"port {cfg.port} unavailable ({e}) - pass --port")
    print(f"skill-cockpit: http://127.0.0.1:{cfg.port}/  (forge root {cfg.forge_root})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
