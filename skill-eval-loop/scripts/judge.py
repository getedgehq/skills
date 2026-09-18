#!/usr/bin/env python3
"""Blind A/B judge for a skill-forge eval pair.

Usage: judge.py <brief.json> [--sample N] [--model M]

1. Runs the brief's verify command in each arm's workdir (objective gate).
2. Extracts each arm's final assistant message + file manifest.
3. Shuffles arms into anonymous slots (mapping kept in mapping.private.json,
   never shown to the judge) and asks a judge model for a verdict.

Verdict JSON: {"winner": "A"|"B"|"tie", "reasons": [...], "per_criterion": {...}}
The judge only ever sees slot letters - arm identity stays on disk, private.

Blindness is enforced, not assumed. The skill under test is found by its SKILL.md
inside the arm's own dot-directories and dropped from the file manifest, whichever
runner installed it; an arm that names the skill in its final message makes the pair
invalid rather than a win. And a verdict the judge did not state readably is refused
by name: recorded as a tie it would be enough to adopt a skill on probation.

The arm is also checked for having used the skill at all. Installing it does not load
it - the model still has to choose it from its description, exactly as in production -
and when it does not, the two arms are one run twice and whatever the judge preferred
it was not the skill.
"""
import argparse
import json
import os
import re
import secrets
import subprocess
import sys

JUDGE_PROMPT = """You are a blind judge comparing two AI agent runs on the same task.

TASK GIVEN TO BOTH AGENTS:
{prompt}

JUDGING CRITERIA:
{rubric}

VERIFY COMMAND RESULTS (exit 0 = task objectively completed):
- Run A: verify exit {va}, tool errors during run: {ea}
- Run B: verify exit {vb}, tool errors during run: {eb}

RUN A - final message and produced files:
{fa}

RUN B - final message and produced files:
{fb}

Judge ONLY what you can see above. If verify failed for a run, weight that heavily.
Return STRICT JSON, no fences:
{{"winner": "A"|"B"|"tie", "per_criterion": {{"<criterion>": "A"|"B"|"tie"}}, "reasons": ["<short reason>"]}}"""


def run_verify(brief, workdir, final_path):
    # Verify may check the agent's reply itself, not only files: $FORGE_FINAL
    # points at the final message (kept outside the workdir the agent saw).
    env = dict(os.environ, FORGE_FINAL=final_path)
    try:
        out = subprocess.run(["bash", "-c", brief["verify"]], cwd=workdir, env=env,
                             capture_output=True, text=True, timeout=120)
        return out.returncode, (out.stdout + out.stderr)[:500]
    except subprocess.TimeoutExpired:
        return 124, "verify timed out"


def final_message(meta):
    # codex writes the last message itself (-o final.txt)
    fp = os.path.join(meta, "final.txt")
    if os.path.exists(fp) and os.path.getsize(fp):
        return open(fp, errors="replace").read()
    last = "(no final message)"
    try:
        for line in open(os.path.join(meta, "transcript.jsonl"), errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            part = d.get("part") if isinstance(d, dict) else None
            if isinstance(part, dict) and part.get("type") == "text" and part.get("text"):
                last = part["text"]  # opencode --format json
                continue
            msg = d.get("message")
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content")
                if isinstance(content, list):
                    texts = [c.get("text", "") for c in content
                             if isinstance(c, dict) and c.get("type") == "text"]
                    if any(texts):
                        last = "\n".join(t for t in texts if t)
    except OSError:
        pass
    return last


def transcript_bytes(meta):
    try:
        return os.path.getsize(os.path.join(meta, "transcript.jsonl"))
    except OSError:
        return 0


def never_ran(arm):
    """True when the runner never got an agent started in this arm.

    Not the same failure as a bad brief, and the loop kept calling it one. A Harbor
    arm whose binary was not on the sudo PATH exited 127 in two seconds with an empty
    transcript; both arms did; and the judge, reading two empty workdirs, recorded
    "both arms failed verify - fix the brief, not the loop" and spent a model call
    saying it. The brief was fine. Twice in a row the record blamed the one thing that
    was not broken, which is worse than a missing verdict: the next person reruns a
    brief that never needed a rewrite and the infrastructure fault leaves no trace.

    All three of these have to hold, because each alone has an innocent reading: a
    non-zero exit can be a timeout after real work, an empty transcript can be a
    runner that writes none, and a missing final message can be an agent that only
    edited files. Together they mean nothing ran.

    That shape was read off a Harbor arm, and it missed the next one. When the CLI
    itself fails, it still writes its init line to the transcript and still writes a
    final message - the failure text. Both arms of the first rival pair came back
    exit 1, 145 bytes of transcript header and the final message "Failed to
    authenticate: OAuth session expired and could not be refreshed", which is not an
    empty arm by any of the three tests above. That pair survived only because the
    judge's own model call was failing on the same credential; with a working judge
    it would have been scored as two agents answering the brief with the same
    sentence, and the loop would have blamed the brief a third time.

    So the second reading: run_eval.sh copies the CLI's error result into run.json,
    and -o writes that same result to final.txt, so a final message that is the
    runner's recorded error is the runner talking, not the agent. Truncation is why
    this compares by prefix - run.json keeps 300 characters. A timeout after real
    work still reads as a real arm: its error comes from stderr, and no agent answer
    opens with it.
    """
    if arm["run"].get("exit", 0) == 0:
        return False
    final = arm["final"].strip()
    if not arm["transcript_bytes"] and final in ("", "(no final message)"):
        return True
    err = (arm["run"].get("error") or "").strip()
    return bool(err) and final.startswith(err)


def dead_reason(name, arm):
    """Why this arm counts as never started, in the words of what was actually seen.

    The two shapes leave different evidence and the record has to say which one it
    read. A line saying "produced no transcript" over an arm that produced a
    transcript header and an authentication error sends the next reader looking for
    a missing file instead of at an expired credential.
    """
    err = (arm["run"].get("error") or "").strip()
    seen = ("its final message is the runner's own error" if err and
            arm["final"].strip().startswith(err) else "it produced no transcript")
    return (f"the {name}-arm exited {arm['run'].get('exit')} and {seen}"
            + (f" ({err})" if err else "")
            + ", so the agent never started and this sample measures the runner, "
              "not the skill")


def tool_error_count(meta):
    n = 0
    try:
        for line in open(os.path.join(meta, "transcript.jsonl"), errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            part = d.get("part") if isinstance(d, dict) else None
            if isinstance(part, dict) and (part.get("state") or {}).get("status") == "error":
                n += 1  # opencode tool part
                continue
            msg = d.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), list):
                n += sum(1 for c in msg["content"]
                         if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"))
    except OSError:
        pass
    return n


def skills_loaded(meta, agent="claude"):
    """(skills this arm loaded, whether its runner records skill calls at all).

    A with-arm that never loaded the skill is not a with-arm. Both arms then ran the
    same task with the same tools and the same model, and whichever the judge preferred
    it was preferring one run over another, not a skill over its absence. Recorded as a
    win it is worse than no verdict: it credits a skill that never executed, which is
    the same defect the production recheck fixed on its own side, still live here. It
    has already happened three times in 39 real arms, in both briefs whose skill was
    adopted, and in one of them it left a 2-1 adoption resting on a single valid sample.

    Read per runner, off real transcripts, because each spells the call its own way and
    guessing has now produced the same bug three times: Claude Code emits a tool_use
    named `Skill` with the name in `skill`, OpenCode a part with tool `skill` and the
    name in `state.input.name`, and Codex records no skill call whatever. So a Codex
    zero is not evidence and the caller is told as much by the second return value -
    withholding that distinction would invalidate every Codex sample the loop ever runs.
    """
    if agent == "codex":
        return set(), False
    got = set()
    try:
        fh = open(os.path.join(meta, "transcript.jsonl"), errors="replace")
    except OSError:
        return got, True
    for line in fh:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        part = d.get("part") if isinstance(d, dict) else None
        if isinstance(part, dict) and part.get("tool") == "skill":
            name = ((part.get("state") or {}).get("input") or {}).get("name")
            if name:
                got.add(name.split(":")[-1])  # a plugin skill is invoked as plugin:skill
            continue
        msg = d.get("message")
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_use" \
                        and (b.get("name") or "").lower() == "skill":
                    name = (b.get("input") or {}).get("skill") or (b.get("input") or {}).get("name")
                    if name:
                        got.add(name.split(":")[-1])
    return got, True


def never_used_its_skill(arm):
    """True when this arm had a skill, its runner would have said so, and it did not.

    All three conditions matter and each has a way of being wrong on its own: an arm
    with no skill installed is an empty baseline and is supposed to load nothing, and an
    arm whose runner records no skill call has an unknowable zero rather than an empty
    one. Written against the arm rather than against the with-arm by name, because a
    baseline given a rival skill has to clear the same bar to be a baseline.
    """
    return bool(arm["skills"]) and arm["loads_knowable"] and not arm["loaded"]


def advertised_skills(meta):
    """Skill names this arm's agent was offered, or None when the runner never says.

    skill_trees answers what we installed. This answers what the agent could actually
    reach, and the two come apart in the direction that matters: a skill already on the
    host, or baked into the container image, is offered to both arms and installed by
    neither. The without-arm is then not a baseline, it is a second with-arm, and every
    check in this file goes on agreeing with itself because all of them read what we
    put there.

    Nothing has caught fire yet, and the measurement is what says so rather than a
    guess: across all 53 without-arms on AX41 whose runner writes an inventory, not one
    advertised the skill its pair was testing. But adoption ends in deployment - the loop's own four skills are
    installed exactly this way - so the day a re-check runs over an adopted skill its
    baseline sees it, and the recheck reads as a skill that stopped working. The
    inventory is read here, before that is anybody's outage.

    Two shapes because two Claude Code versions write it differently, and both are in
    the runs directory today: the host CLI puts a `skills` list on the system/init
    line, the SDK CLI inside Harbor's image emits a `skill_listing` attachment with
    `names`. A runner that writes neither returns None, which is not an empty
    inventory: Codex records no listing at all, and reading its silence as "offered
    nothing" would clear every Codex baseline without checking one.
    """
    found = None
    try:
        fh = open(os.path.join(meta, "transcript.jsonl"), errors="replace")
    except OSError:
        return None
    for line in fh:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        names = None
        if d.get("type") == "system" and d.get("subtype") == "init":
            names = d.get("skills")
        att = d.get("attachment")
        if isinstance(att, dict) and att.get("type") == "skill_listing":
            names = att.get("names")
        if isinstance(names, list):
            found = (found or set()) | {str(n).split(":")[-1] for n in names}
    return found


def advertised_record(arms):
    """What each arm was offered, for the verdict record. None stays None: an arm whose
    runner writes no listing has an unknown inventory, and writing [] would file that
    as a checked-and-empty one."""
    return {a: (None if arms[a]["advertised"] is None else sorted(arms[a]["advertised"]))
            for a in arms}


def blind_broken(arms):
    """Skills the baseline could reach that only the candidate was handed.

    Subtracting the without-arm's own installs first is what keeps --rival legal: a
    baseline deliberately given the incumbent is supposed to reach it, and that pair is
    the head-to-head the ledger wants. What is not legal is a name the with-arm alone
    was handed turning up in the baseline's inventory anyway, because the only way it
    got there is a copy neither arm installed.
    """
    candidate = set(arms["with"]["skills"]) - set(arms["without"]["skills"])
    offered = arms["without"]["advertised"]
    if offered is None or not candidate:
        return []
    return sorted(candidate & offered)


def skill_trees(workdir, meta=None):
    """Where the skill under test was installed in this arm, and what it is called.

    run_eval.sh drops it in a different place per runner: .claude/skills for Claude
    Code, .agents/skills for Codex, .opencode/skill for OpenCode. manifest() used to
    skip the Claude path by name, so a Codex or OpenCode arm handed the judge
    ".agents/skills/li-post-fede/SKILL.md (2114b)" in its file list and the blind
    named the arm. Skipping the three paths by name would leak again the day a fourth
    runner is added, so the skill is found by its SKILL.md instead, and only inside a
    dot-directory: an agent asked to WRITE a SKILL.md puts it in the work it produced,
    which is the deliverable and stays in the manifest.

    And the fourth runner arrived, exactly as predicted, except that it broke the
    other end: run_eval_harbor.sh never puts the skill in the workdir at all. It
    resolves it into <arm>.meta/skill/<name> and hands that to Harbor, which mounts it
    inside the container, so the host workdir the scan above walks is empty of skills
    whatever the arm was given. Every Harbor with-arm therefore read as an arm with no
    skill installed, and two of the three integrity checks went quiet on it: with no
    installed name, never_used_its_skill cannot fire, and named_skills has nothing to
    match, so neither the never-loaded check nor the blindness check could ever refuse
    a Harbor pair. The first one to run proved it. The judge recorded
    skills_installed {"with": []} for an arm the container's own skill listing shows it
    advertised, and the pair was filed against the brief instead.
    """
    out = {}
    for entry in sorted(os.listdir(workdir)) if os.path.isdir(workdir) else []:
        if not entry.startswith("."):
            continue
        for root, dirs, names in os.walk(os.path.join(workdir, entry)):
            if "SKILL.md" in names:
                out[os.path.basename(root)] = root
                dirs[:] = []
    handed = os.path.join(meta or "", "skill")
    for entry in sorted(os.listdir(handed)) if meta and os.path.isdir(handed) else []:
        if os.path.exists(os.path.join(handed, entry, "SKILL.md")):
            out.setdefault(entry, os.path.join(handed, entry))
    return out


def manifest(workdir, hide=()):
    files = []
    for root, dirs, names in os.walk(workdir):
        if any(root == h or root.startswith(h + os.sep) for h in hide):
            dirs[:] = []
            continue
        for n in names:
            p = os.path.relpath(os.path.join(root, n), workdir)
            files.append(f"{p} ({os.path.getsize(os.path.join(root, n))}b)")
    return "\n".join(sorted(files)[:80]) or "(no files)"


def named_skills(text, names):
    """Skill names an arm said out loud in its final message.

    Hiding the files is only half of it: an agent that writes "following the
    li-post-fede skill" has told the judge which arm it is reading. That verdict is
    not a blind one and is worth less than no verdict, so it is marked invalid rather
    than recorded as a win. Checked against all 45 real sample verdicts on AX41: not
    one arm ever named a skill, so this refuses nothing that has already happened.
    """
    return sorted(n for n in names
                  if re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", text, re.I))


def first_object(text):
    """The first complete JSON object in a model reply, or None.

    One implementation, in forge_llm, because there were two: this one and score.py's,
    written from the same lesson and already drifted apart. score.py's had learned to
    read a reply with a missing comma in it and this one had not, which is the wrong
    half of the loop to be the tolerant one - a verdict this cannot read is a paid pair
    of container runs thrown away, where a score it cannot read costs a model call.

    None rather than an exception is this caller's contract: winner_slot below is
    already the place that decides what an unreadable verdict means.
    """
    import forge_llm  # deferred like its other use below, which is the only caller
    try:
        return forge_llm.first_object(text)
    except ValueError:
        return None


def winner_slot(verdict):
    """The slot the judge picked, or None if it did not say so readably.

    "A", "B" and "tie" are the only answers the mapping can be read with. A reply of
    "Run A" or "a" used to fall through slots.get(..., "tie") and be recorded as a
    tie, which is not a missing verdict but a wrong one: with --probation a tie is
    enough to adopt, so an unreadable reply could install a skill nothing had judged.
    Obvious wrappers are normalized, and anything left is refused by name.
    """
    w = (verdict.get("winner") or "").strip().strip('"').lower()
    w = re.sub(r"^(run|arm|slot)\s+", "", w)
    if w in ("a", "b"):
        return w.upper()
    return "tie" if w in ("tie", "draw", "neither", "equal") else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--sample", default=os.environ.get("FORGE_SAMPLE"))
    ap.add_argument("--model", default=os.environ.get("FORGE_JUDGE_MODEL", "claude-opus-5"))
    args = ap.parse_args()

    brief = json.load(open(args.brief))
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    runs = os.path.join(root, "runs", brief["id"])
    if args.sample:
        runs = os.path.join(runs, f"s{args.sample}")

    arms = {}
    for arm in ("with", "without"):
        workdir = os.path.join(runs, arm)
        meta = workdir + ".meta"
        if not os.path.isdir(workdir) or not os.path.isdir(meta):
            sys.exit(f"missing arm: {workdir}")
        final = final_message(meta)
        final_path = os.path.join(meta, "final.txt")
        if not os.path.exists(final_path):
            open(final_path, "w").write(final)
        code, vout = run_verify(brief, workdir, final_path)
        trees = skill_trees(workdir, meta)
        run = json.load(open(os.path.join(meta, "run.json")))
        used, knowable = skills_loaded(meta, run.get("agent", "claude"))
        arms[arm] = {
            "verify_exit": code,
            "verify_out": vout,
            "tool_errors": tool_error_count(meta),
            "final": final[-3000:],
            "files": manifest(workdir, hide=trees.values()),
            "skills": sorted(trees),
            "loaded": sorted(used & set(trees)),
            "loads_knowable": knowable,
            "advertised": advertised_skills(meta),
            "transcript_bytes": transcript_bytes(meta),
            "run": run,
        }

    # Before the mapping and before the model call: a pair where an arm never started
    # has nothing to judge, and the two things this saves are the point. No mapping is
    # written, so the rerun that follows the fix draws its own blind slots; and no
    # judge call is spent reading two empty workdirs, which is what happened twice
    # tonight. Ordered ahead of both_arms_failed_verify because an arm that never ran
    # also fails verify, and that code sends the brief back for a rewrite it does not
    # need.
    dead = [a for a in ("with", "without") if never_ran(arms[a])]
    if dead:
        result = {
            "brief": brief["id"],
            "winner_arm": "invalid",
            "invalid": True,
            "invalid_code": "arm_never_ran",
            "invalid_reason": "; ".join(dead_reason(a, arms[a]) for a in dead),
            "verify": {a: arms[a]["verify_exit"] for a in arms},
            "tool_errors": {a: arms[a]["tool_errors"] for a in arms},
            "skills_installed": {a: arms[a]["skills"] for a in arms},
            "skills_loaded": {a: arms[a]["loaded"] for a in arms},
            "loads_knowable": {a: arms[a]["loads_knowable"] for a in arms},
            "skills_advertised": advertised_record(arms),
            "run": {a: arms[a]["run"] for a in arms},
        }
        path = os.path.join(runs, "verdict.json")
        json.dump(result, open(path, "w"), indent=1)
        print(json.dumps({k: result[k] for k in
                          ("brief", "winner_arm", "invalid_code", "invalid_reason")}, indent=1))
        print(f"-> {path}")
        return

    # Also before the mapping and before the model call, and for the same two reasons:
    # a baseline that could reach the candidate's skill is not a baseline, so there is
    # nothing here a judge could read, and the rerun after the skill is uninstalled
    # should draw its own slots rather than inherit this pair's. Ahead of every check
    # below it because those all compare two arms and this one says the two arms are
    # the same arm - skill_never_loaded in particular would fire on exactly this pair
    # from the other side, blaming the with-arm for a silence that came from the
    # baseline having the skill too.
    leaked = blind_broken(arms)
    if leaked:
        result = {
            "brief": brief["id"],
            "winner_arm": "invalid",
            "invalid": True,
            "invalid_code": "baseline_had_the_skill",
            "invalid_reason": (
                f"the without-arm was offered {', '.join(leaked)} without being "
                "handed it, so the baseline could reach the skill under test and "
                "this pair measures nothing. Uninstall it from the host or image the "
                "runner uses, then rerun the sample"),
            "verify": {a: arms[a]["verify_exit"] for a in arms},
            "tool_errors": {a: arms[a]["tool_errors"] for a in arms},
            "skills_installed": {a: arms[a]["skills"] for a in arms},
            "skills_loaded": {a: arms[a]["loaded"] for a in arms},
            "loads_knowable": {a: arms[a]["loads_knowable"] for a in arms},
            "skills_advertised": advertised_record(arms),
            "run": {a: arms[a]["run"] for a in arms},
        }
        path = os.path.join(runs, "verdict.json")
        json.dump(result, open(path, "w"), indent=1)
        print(json.dumps({k: result[k] for k in
                          ("brief", "winner_arm", "invalid_code", "invalid_reason")}, indent=1))
        print(f"-> {path}")
        return

    # Blind: random slot assignment, persisted privately, never reshuffled.
    map_path = os.path.join(runs, "mapping.private.json")
    if os.path.exists(map_path):
        slots = json.load(open(map_path))
    else:
        pair = ["with", "without"]
        if secrets.randbelow(2):
            pair.reverse()
        slots = {"A": pair[0], "B": pair[1]}
        json.dump(slots, open(map_path, "w"), indent=1)

    # Both arms failing the objective gate means the BRIEF is broken, not the
    # skill. A model verdict over two broken runs is noise - mark invalid.
    both_failed = all(a["verify_exit"] != 0 for a in arms.values())

    # A verdict is only worth recording if the judge could not tell the arms apart.
    installed = sorted({n for a in arms.values() for n in a["skills"]})
    spoken = sorted({n for a in arms.values() for n in named_skills(a["final"], installed)})

    prompt = JUDGE_PROMPT.format(
        prompt=brief["prompt"], rubric=brief.get("rubric", "correctness; completeness; brief adherence"),
        va=arms[slots["A"]]["verify_exit"], vb=arms[slots["B"]]["verify_exit"],
        ea=arms[slots["A"]]["tool_errors"], eb=arms[slots["B"]]["tool_errors"],
        fa=arms[slots["A"]]["final"] + "\n\nFILES:\n" + arms[slots["A"]]["files"],
        fb=arms[slots["B"]]["final"] + "\n\nFILES:\n" + arms[slots["B"]]["files"],
    )
    import forge_llm
    text, engine = forge_llm.call_model(prompt, args.model)
    print(f"  (judged by {engine})", file=sys.stderr)
    verdict = first_object(text)
    if verdict is None:
        sys.exit(f"no JSON object in judge output: {text[:300]}")
    slot = winner_slot(verdict)
    if slot is None:
        # Not a tie: a tie is a verdict, and this is the absence of one.
        sys.exit(f"judge did not name a readable winner: {verdict.get('winner')!r}")

    result = {
        "brief": brief["id"],
        "slots": slots,
        "winner_slot": slot,
        "winner_arm": "tie" if slot == "tie" else slots[slot],
        "verdict": verdict,
        "verify": {a: arms[a]["verify_exit"] for a in arms},
        "tool_errors": {a: arms[a]["tool_errors"] for a in arms},
        "skills_installed": {a: arms[a]["skills"] for a in arms},
        "skills_loaded": {a: arms[a]["loaded"] for a in arms},
        "loads_knowable": {a: arms[a]["loads_knowable"] for a in arms},
        "skills_advertised": advertised_record(arms),
        "run": {a: arms[a]["run"] for a in arms},
    }
    # An arm had a skill and its runner would have recorded the call, and there is no
    # call: the two arms were the same run twice, so this pair is not a comparison.
    # Checked on both arms rather than only the candidate's, because the baseline can
    # have one too - under --rival it holds the skill already installed for this
    # trigger - and a rival that was never loaded turns the head-to-head the ledger
    # will record back into the walkover it was meant to replace. Ordered ahead of a
    # broken brief, for the reason at that branch, and ahead of the blindness check,
    # which cannot fire on an arm that never read the skill it would have to name.
    silent = [a for a in ("with", "without") if never_used_its_skill(arms[a])]
    if silent:
        result["invalid"] = True
        result["invalid_code"] = "skill_never_loaded"
        result["invalid_reason"] = "; ".join(
            f"the {a}-arm never loaded {', '.join(arms[a]['skills'])}, so it ran the "
            "task without the skill it was given and this pair compares two runs, "
            "not a skill" for a in silent)
        result["winner_arm"] = "invalid"
        # Ahead of both_arms_failed_verify, which used to win this tie and was wrong
        # about it on the first Harbor pair. Both arms there failed the brief's gate,
        # which caps the reply at 150 words, and the verdict came back "fix the brief,
        # not the loop" - over a brief whose identical gate the local runner had just
        # passed three times out of three, 91, 82 and 88 words against a baseline's
        # 310, 312 and 280. The with-arm wrote 194 because it never loaded the skill,
        # and that skill's entire job is to make the reply short: the gate did not
        # fail independently of the silent arm, it failed BECAUSE of it. A gate that
        # was never once tested with the skill in place says nothing about the brief.
        # It also matters which code comes out, not just which is truer: two
        # both_arms_failed_verify in a row stop the brief, so a skill that keeps
        # failing to load would retire its own eval with the log blaming the brief,
        # while skill_never_loaded stops nothing and the next sample may well load it.
        # The verify failure stays in the reason rather than being dropped, because
        # the two together are what says the gate is still unmeasured.
        if both_failed:
            result["invalid_reason"] += (
                ". Both arms also failed verify, which is what a silent arm looks like "
                "when the skill's own job is to pass that gate: the brief is not "
                "implicated until a sample runs with the skill actually loaded")
    elif both_failed:
        result["invalid"] = True
        # Two invalid samples are not the same kind of problem, and the caller has to
        # tell them apart to know whether running the next sample is worth anything.
        # This one is a property of the brief: its gate was unpassable this time and
        # will be unpassable the next two times, so the remaining samples buy nothing
        # but an hour each. The one above is chance, and the next sample may be clean.
        result["invalid_code"] = "both_arms_failed_verify"
        result["invalid_reason"] = "both arms failed verify - fix the brief, not the loop"
        result["winner_arm"] = "invalid"
    elif spoken:
        result["invalid"] = True
        result["invalid_code"] = "skill_named_in_final"
        result["invalid_reason"] = ("an arm named the skill under test in its final message "
                                    f"({', '.join(spoken)}), so this pair was not judged blind")
        result["winner_arm"] = "invalid"
    path = os.path.join(runs, "verdict.json")
    json.dump(result, open(path, "w"), indent=1)
    keys = ("brief", "winner_arm", "verify") + (("invalid_code",) if result.get("invalid") else ())
    print(json.dumps({k: result[k] for k in keys}, indent=1))
    print(f"-> {path}")


if __name__ == "__main__":
    main()
