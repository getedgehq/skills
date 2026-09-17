#!/usr/bin/env python3
"""Mine correction episodes: the moments the user told the agent it got something wrong.

Usage: corrections.py [--sources claude,opencode,codex] [--sessions 400]
                      [--memory DIR] [--out corrections.json] [--no-llm]

Tool errors show where an agent stumbles; corrections show where it produced output
the USER rejected. Those are the failures a skill can actually fix, because the fix
is knowledge the model cannot have: this user's formats, voice, thresholds and rules.
Generic failures (forgot to read a file, bad quoting) tie in evals - frontier models
already avoid them when fresh. Knowledge-gap themes win.

Each episode = (the agent message the user reacted to, the user's correction).
An LLM groups episodes into themes and marks which are knowledge gaps. With --memory,
it also maps each theme to the user's saved rule files, which draft.py and brief.py
use as enriched context.

Output clusters use the failures.json shape, so brief.py / match.py / draft.py work
on them unchanged: {kind, class, signature, count, session_count, evidence, ...}.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402

# Correction cues, English + German (the languages the loop has been dogfooded in).
# Deliberately broad: the LLM pass filters out false positives.
CUE = re.compile(
    r"\b(never|don'?t|dont|stop|wrong|i told you|again|why did you|not what i|should have|"
    r"you forgot|instead of|too long|too much|way more|concise|tldr|slop|bs|wtf|invent\w*|"
    r"not my (style|voice|tone)|hallucinat\w*|"
    r"nein|nicht|falsch|schon wieder|zu viel|zu wenig|zu lang|tonalit\w*|kein\w*)\b",
    re.I)
SYSTEMISH = re.compile(
    r"(session is being continued|<system-reminder|base directory for this skill|<command-|"
    r"<local-command|Caveat:|\[Request interrupted|<task-notification)", re.I)

THEME_PROMPT = """Below are correction episodes mined from one user's AI agent sessions. Each has an id,
what the agent wrote just before, and the user's reply.

{episodes}

{memory}

Group the GENUINE corrections (the user rejects or fixes the agent's output or behavior) into
recurring themes. Ignore episodes that are just instructions, questions, or task changes.

For each theme with at least 2 episodes return:
- "signature": one line naming what the agent keeps getting wrong, in plain words
- "knowledge_gap": true when fixing it needs THIS user's specific rules, voice, formats,
  preferences or facts that a capable model could not know; false for generic mistakes
  any careful model avoids (forgot to read a file, broke quoting, skipped a test)
- "episode_ids": ids of the episodes in this theme
- "user_rules": the user's own words that state the rule, verbatim quotes, max 6
- "memory_files": file names from the memory index that carry rules for this theme (may be empty)

Return STRICT JSON only: {{"themes": [ ... ]}}"""


def episodes_from(sessions, max_corr=400, max_asst=300):
    """Returns (episodes, turns_by_session).

    The turn count is the number of user messages the human actually typed, after the
    harness-injected ones are dropped - the same messages the episode rule below reads.
    recheck.py needs it for its denominator: an episode requires a previous user message
    and a previous assistant message, so a session with fewer than two of these turns
    cannot produce one, and counting it dilutes a rate rather than measuring it.
    """
    out, turns = [], {}
    for s in sessions:
        prev_user, prev_asst = None, ""
        typed = 0
        for e in sources.iter_events(s):
            t = e.get("type")
            if t == "assistant_text":
                prev_asst = e["text"]
            elif t == "user_text":
                text = e["text"]
                if not text or SYSTEMISH.search(text) or sources.is_injected(text):
                    continue
                typed += 1
                if 15 < len(text) < max_corr and prev_user and prev_asst and CUE.search(text):
                    out.append({"id": f"E{len(out)}", "session": s.id, "kind": s.kind,
                                "ts": s.mtime,  # recheck.py splits episodes before/after an adoption
                                "asst": " ".join(prev_asst.split())[-max_asst:],
                                "corr": " ".join(text.split())})
                prev_user = text
        turns[s.id] = typed
    return out, turns


def spread(eps, limit, per_session):
    """Round-robin across sessions (newest first) so one marathon session can't fill the budget."""
    by_sess = {}
    for e in eps:
        by_sess.setdefault(e["session"], []).append(e)
    queues = [q[:per_session] for q in by_sess.values()]
    out = []
    while queues and len(out) < limit:
        for q in queues:
            if q and len(out) < limit:
                out.append(q.pop(0))
        queues = [q for q in queues if q]
    for i, e in enumerate(out):
        e["id"] = f"E{i}"
    return out


def memory_index(mem_dir):
    rows = []
    for f in sorted(glob.glob(os.path.join(mem_dir, "*.md"))):
        if os.path.basename(f) == "MEMORY.md":
            continue
        head = open(f, errors="replace").read(800)
        m = re.search(r"description:\s*(.+)", head)
        rows.append((os.path.basename(f), m.group(1).strip() if m else ""))
    return rows


def cluster_llm(eps, mem_rows, model):
    from forge_llm import call_model
    ep_txt = "\n".join(f'{e["id"]}: agent: "{e["asst"][-200:]}" -> user: "{e["corr"][:300]}"' for e in eps)
    mem_txt = ("MEMORY INDEX (the user's saved rules, file: description):\n" +
               "\n".join(f"- {n}: {d}" for n, d in mem_rows)) if mem_rows else "(no memory index)"
    text, engine = call_model(THEME_PROMPT.format(episodes=ep_txt, memory=mem_txt), model, timeout=900)
    print(f"  (themes by {engine})", file=sys.stderr)
    start, end = text.find("{"), text.rfind("}")
    if start == -1:
        sys.exit(f"no JSON in theme output: {text[:300]}")
    return json.loads(text[start:end + 1]).get("themes", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default=None, help="comma list; default all available")
    ap.add_argument("--sessions", type=int, default=400)
    ap.add_argument("--projects", default=None,
                    help="Claude projects dir to scan instead of ~/.claude/projects "
                         "(recheck.py runs where the user actually types)")
    ap.add_argument("--memory", default=None, help="dir of the user's saved rule/memory .md files")
    ap.add_argument("--max-episodes", type=int, default=250)
    ap.add_argument("--per-session", type=int, default=6)
    ap.add_argument("--out", default="corrections.json")
    ap.add_argument("--no-llm", action="store_true", help="only extract episodes")
    ap.add_argument("--episodes", default=None, help="reuse episodes from an earlier --no-llm output")
    ap.add_argument("--model", default=os.environ.get("FORGE_BRIEF_MODEL", "claude-opus-5"))
    args = ap.parse_args()

    session_index = []
    if args.episodes:
        prev = json.load(open(args.episodes))
        eps, src_counts = prev["episodes"], prev.get("sources", {})
        session_index = prev.get("session_index", [])
    else:
        kinds = args.sources.split(",") if args.sources else sources.available_kinds()
        sess = sources.list_sessions(kinds, args.sessions,
                                     {"claude": args.projects} if args.projects else None)
        found, turns = episodes_from(sess)
        eps = spread(found, args.max_episodes, args.per_session)
        src_counts = {k: sum(1 for s in sess if s.kind == k) for k in kinds}
        # every scanned session, not just the ones with episodes: recheck.py needs the
        # denominator on both sides of an adoption date, including quiet sessions - and
        # the turn count, so it can drop the ones that could not have carried an episode
        session_index = [{"id": s.id, "kind": s.kind, "ts": s.mtime,
                          "turns": turns.get(s.id, 0)} for s in sess]
    print(f"sessions {src_counts}, {len(eps)} candidate correction episodes", file=sys.stderr)

    report = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "sources": src_counts,
              "episode_count": len(eps), "episodes": eps,
              "session_index": session_index, "clusters": []}
    if not args.no_llm and eps:
        mem_rows = memory_index(args.memory) if args.memory else []
        mem_names = {n for n, _ in mem_rows}
        by_id = {e["id"]: e for e in eps}
        clusters = []
        for th in cluster_llm(eps, mem_rows, args.model):
            members = [by_id[i] for i in th.get("episode_ids", []) if i in by_id]
            if len(members) < 2:
                continue
            clusters.append({
                "kind": "correction",
                "class": "task",
                "signature": th.get("signature", "")[:200],
                "knowledge_gap": bool(th.get("knowledge_gap")),
                "count": len(members),
                "session_count": len({m["session"] for m in members}),
                "evidence": [f'agent wrote: "{m["asst"][-260:]}" -> user corrected: "{m["corr"][:300]}"'
                             for m in members[:12]],
                "user_rules": th.get("user_rules", [])[:6],
                "context_files": [os.path.join(os.path.abspath(args.memory), n)
                                  for n in th.get("memory_files", []) if n in mem_names],
            })
        # knowledge gaps first: those are the themes a skill can win on
        clusters.sort(key=lambda c: (not c["knowledge_gap"], -c["session_count"], -c["count"]))
        report["clusters"] = clusters
        report["cluster_count"] = len(clusters)
    json.dump(report, open(args.out, "w"), indent=1, ensure_ascii=False)
    print(args.out)
    for c in report["clusters"][:10]:
        tag = "gap" if c["knowledge_gap"] else "generic"
        print(f"  [{tag}] x{c['count']} in {c['session_count']} sessions: {c['signature'][:90]}")


if __name__ == "__main__":
    main()
