#!/usr/bin/env python3
"""Recheck adopted and probationary skills: did the failure rate drop after adoption?

Usage: recheck.py [--projects DIR] [--sessions N] [--sources claude,opencode,codex] [--dry-run]

For each ledger entry with a recorded baseline whose recheck_due <= today, this
re-mines recent sessions and compares the failure's session-rate against the
baseline recorded at adoption. Rate dropped -> KEEP (decision: adopt-confirmed).
No drop -> REVOKE: uninstalls the skill and records decision: revoked.

Knowledge-gap skills (the ones drafted from correction themes) have no tool-error
signature to count, so they are rechecked differently: corrections.py re-extracts the
user's correction episodes with --no-llm, and the rate of corrections about that theme
is measured on both sides of the adoption date with one matcher. A recheck never needs
a model call.

Three rules keep a recheck from confirming a skill on no evidence:
  - an entry with no baseline rate is SKIPPED, not confirmed;
  - an entry whose failure signature was never recorded is SKIPPED too. Without a
    signature nothing can match a fresh cluster, so a "rate of 0.0" would mean
    "we cannot look", not "the failure stopped";
  - a knowledge-gap entry with fewer than 10 sessions on either side of the adoption
    is SKIPPED until there are enough to compare, and so is one whose sessions since
    adoption span less than MIN_AFTER_DAYS days;
  - signature words that are common across all corrections are dropped before
    matching. A theme described in ordinary words ("post", "reply", "status") would
    otherwise match nearly every correction and return noise as a measurement;
  - a signature lifted from the skill's own description is SKIPPED on sight, however
    narrow it looks. It describes the skill, not the mistake, and width alone cannot
    tell the two apart: extending the stopword list pulled three such signatures from
    35-42 distinct words down to 18-20, under the cap, without making a single one of
    them more about one theme. Mine a real one with theme.py instead;
  - a rate that improved while the skill was never once loaded confirms nothing. Every
    other guard here asks whether the rate moved; none of them asks whether the thing
    under test ever ran, and a skill only reaches the model when it is loaded. The
    session index now carries the skills each session loaded, and a drop with zero loads
    is a SKIP, never an adopt-confirmed - and never a revoke either, because a skill that
    never ran has not failed, it has had no chance, so the entry stays due;
  - and the denominator holds only sessions that could have carried a correction. A
    correction episode needs a previous user turn and a previous assistant turn, so a
    one-shot question cannot produce one; counting it measures the window's mix of work
    instead of the skill. On the real corpus that mix moved from 70% single-turn sessions
    before the adoptions to 6% after, which by itself took the rate from 22% to 75% - a
    verdict of "ten skills made the agent worse" from a change in what the days looked
    like. After the floor the same windows read 74% and 80%. A second guard catches what
    the floor leaves: each window's expected rate is read off session lengths alone, and
    the comparison is refused when those differ by as much as the verdict threshold.

--dry-run prints every decision and touches nothing: no ledger row, no uninstall.
Run it once before the timer fires on a machine where skills are installed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time


def uninstall(skill, root, dry):
    """Remove every install of `skill`, keeping the copy as evidence.

    Installs are usually a real directory in ~/.agents/skills plus a symlink from
    ~/.claude/skills. rmtree() raises on a symlink, so unlink those, and move the
    real directory into $FORGE_ROOT/revoked/ instead of deleting the evidence.
    """
    done = []
    for d in (os.path.expanduser("~/.agents/skills"), os.path.expanduser("~/.claude/skills")):
        p = os.path.join(d, skill)
        if os.path.islink(p):
            if not dry:
                os.unlink(p)
            done.append(f"unlinked {p}")
        elif os.path.isdir(p):
            keep = os.path.join(root, "revoked", f"{skill}-{time.strftime('%Y%m%d%H%M%S')}")
            if not dry:
                os.makedirs(os.path.dirname(keep), exist_ok=True)
                shutil.move(p, keep)
            done.append(f"moved {p} -> {keep}")
    return done or ["not installed"]


MIN_AFTER_DAYS = 5  # a skill adopted this morning has no production record yet
MAX_THEME_TOKENS = 20  # a matcher this wide stops being about one theme
IMPROVED = 0.7  # the drop a rate must show to confirm a skill; also what the guard below allows
MIN_TURNS = 2  # below this a session cannot contain a correction episode at all
TURN_EDGES = (2, 4, 8, 20)  # buckets for reading a window's expected rate off its lengths

# Corrections are typed in a hurry, so they are mostly function words. Anything left
# here turns up in a third of every user's corrections and can only dilute a theme:
# a derived signature of "but can dont have" passed every statistical check before
# these words were removed, which is the exact failure this whole matcher guards against.
STOP = set("the a an and or of to in on for with is are was were be been being am it its "
           "this that these those there here what which who whom whose why how when where "
           "not no never always too very more less than as at by from into out up down off "
           "over under again just only also else still even really actually maybe "
           "i you he she they we my your his her their our me him them us mine yours ours "
           "do does did done doing dont doesnt didnt cant cannot couldnt wont wouldnt "
           "shouldnt isnt arent wasnt werent havent hasnt hadnt aint "
           "can could will would shall should may might must have has had "
           "make makes made get gets got give gives gave take takes took put puts "
           "use uses used using say says said tell tells told see sees saw seen look looks "
           "go goes went going come comes came know knows knew think thinks thought "
           "want wants need needs let lets like likes please thanks thank ok okay yes yeah "
           "one two three first last next then now thing things way ways time times "
           "some any all both each every other another same such own but so if because "
           "much many few lot lots bit still yet already back around about into "
           "agent claude user "
           # The user corrects in German as often as in English, and "nicht" landed in a
           # derived signature the same way "dont" did.
           "der die das den dem des ein eine einen einem eines und oder aber auch noch "
           "nicht kein keine nur schon mal bitte danke ist sind war waren sein ich du wir "
           "ihr sie er es mit für auf aus bei von zum zur nach vor über unter wie was wo "
           "wann warum wenn dass dann doch mehr weniger sehr immer nie hier dort jetzt "
           "haben hat hatte werden wird wurde kann kannst koennen soll sollte muss "
           "machen macht gemacht bitte mach".split())


def tokens(text):
    return {w for w in re.findall(r"[a-z][a-z0-9]{2,}", (text or "").lower()) if w not in STOP}


def distinctive(sig_tokens, episodes, ceiling=0.25):
    """Drop signature tokens that are common across all corrections.

    A theme signature taken from a skill description is long and mostly ordinary
    words: "post", "message", "review", "status". Matching on any two of those
    marks almost every correction as being about this theme, which turns the
    before/after comparison into noise dressed as a measurement. Keep only tokens
    that appear in fewer than `ceiling` of correction episodes.

    Returns (keep, rare). A token in `rare` is distinctive enough on its own:
    "umlaut" or "mdash" appearing in a correction is about this theme and nothing
    else, and demanding a second matching word would miss most real episodes.
    """
    if not episodes:
        return sig_tokens, set()
    df = {}
    for e in episodes:
        for w in tokens(e.get("corr", "")) & sig_tokens:
            df[w] = df.get(w, 0) + 1
    cut = max(1, int(len(episodes) * ceiling))
    rare_cut = max(1, int(len(episodes) * ceiling / 2))
    keep = {w for w in sig_tokens if df.get(w, 0) <= cut}
    return keep, {w for w in keep if 0 < df.get(w, 0) <= rare_cut}


def eligible(sessions):
    """The sessions that could have carried a correction at all.

    corrections.py only emits an episode where it has both a previous user message and a
    previous assistant message, so a session with fewer than MIN_TURNS typed turns cannot
    contribute to the numerator whatever happened in it. Leaving those in the denominator
    is not conservative, it makes the rate a measure of how many one-shot questions the
    window happened to hold: on the real corpus 188 of 296 sessions were single-turn, none
    of them carried an episode, and their share fell from 70% of the window before the
    adoptions to 6% after. That alone moved the raw rate from 22% to 75%, which the verdict
    would have read as ten skills making the agent worse. Dropping them discards no session
    that actually carried a correction, at this floor or any lower one.
    """
    return [s for s in sessions if s.get("turns", 0) >= MIN_TURNS]


def bucket(session):
    n = session.get("turns", 0)
    return max([i for i, edge in enumerate(TURN_EDGES) if n >= edge] or [0])


def length_shift(sessions, episodes, t_adopt, until):
    """How far the two windows' session lengths can move the rate on their own.

    The floor above removes the sessions that could not contribute; it does not make what
    is left comparable, because the correction rate keeps climbing with length well past
    it - 0% at two turns, 92% past twelve. So each window's expected rate is read off the
    pooled corpus by length alone, and the two are compared using the same factor the
    verdict uses. Tying the guard to IMPROVED rather than to a threshold of its own is the
    point: it refuses exactly when length by itself could produce the verdict, and stays
    quiet when it could not. Measured this way the shipped denominator shifted 3.11x across
    the real adoption date and the floored one 1.10x.
    """
    hit = {e.get("session") for e in episodes}
    base = {}
    for i in range(len(TURN_EDGES)):
        grp = [s for s in sessions if bucket(s) == i]
        base[i] = len([s for s in grp if s["id"] in hit]) / len(grp) if grp else 0.0
    rates = []
    for since, stop in ((0, t_adopt), (t_adopt, until)):
        win = [s for s in sessions if since <= s.get("ts", 0) < stop]
        rates.append(sum(base[bucket(s)] for s in win) / len(win) if win else 0.0)
    before, after = rates
    if before:
        return after / before
    # Nothing in the before window was the kind of session that carries a correction.
    # Treating that as "comparable" would wave through the widest shift there is, so it
    # is the opposite: unbounded unless the after window is the same way.
    return 1.0 if not after else float("inf")


def loads(skill, sessions, since, until):
    """How many sessions in a window actually loaded this skill.

    A skill only reaches the model when it is loaded; until then its body is not in
    context and it cannot have changed an answer. So a correction rate that fell across
    a window where the skill was never once loaded fell for some other reason - the work
    moved on, the theme stopped coming up, the window caught a quiet week - and reading
    it as proof would write an adopt-confirmed row for a win the skill had no part in.
    Nothing else in this file can catch that: every other guard asks whether the rate
    moved, and none of them asks whether the thing under test ever ran.

    Counted across all sources, and low for a reason that is not the skill's fault more
    often than it looks: Codex transcripts record no skill load at all, so a window that
    is mostly Codex reads zero however much the skill ran. That only ever costs a SKIP
    and a later recheck, never a revoke, which is the right way round for a count that
    can be wrong low.
    """
    n = 0
    for s in sessions:
        if since <= s.get("ts", 0) < until and skill in (s.get("skills") or ()):
            n += 1
    return n


def installed(skill, roots=None):
    """The roots this process can see the skill installed in, newest definition of
    "installed" being the same two directories uninstall() would clear.

    Zero loads has two causes that look identical in the count and need opposite fixes,
    and the loop spent an afternoon telling them apart by hand: either the skill is
    installed where the sessions ran and the model never chose it, which is a discovery
    problem in the description, or it is not installed in a root those sessions could
    reach at all, which is a plumbing problem and says nothing about the skill. On the
    live machine that was not hypothetical: all seven adopted skills existed only under
    root's home, so every session mined from the user's own home reported zero loads for
    a reason that had nothing to do with any of them.

    A negative here is weaker than a positive: the recheck sees its own roots, not the
    roots of whoever typed the sessions, so an empty list means "not reachable from
    here", never "nowhere on this machine". That is why it only ever colours a SKIP
    message and never decides one.
    """
    if roots is None:
        roots = (os.path.expanduser("~/.agents/skills"), os.path.expanduser("~/.claude/skills"))
    return [d for d in roots if os.path.exists(os.path.join(d, skill))]


def usage_report(entries, sessions, roots=None):
    """One line per open entry: sessions since adoption, and how many loaded the skill.

    The verdict guard can only withhold a confirmation once the window has already
    passed. This is the same measurement asked early, while a zero is still fixable,
    and it exists because reading it by hand off the ledger and a session index is what
    turned up the finding that six of seven adopted skills had never once been loaded -
    in a corpus where twenty other skills were loaded forty times between them, so the
    zero was about those six and not about whether loads get recorded at all.

    Sorted by loads so the zeros come first, which is the only row worth acting on.
    """
    now = time.time()
    rows = []
    for e in entries:
        adopted = e.get("adopted_at") or e.get("ts")
        try:
            t = time.mktime(time.strptime(adopted, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
        except (TypeError, ValueError):
            continue
        after = sum(1 for s in sessions if t <= s.get("ts", 0) < now)
        rows.append((loads(e["skill"], sessions, t, now), after, e["skill"],
                     ", ".join(installed(e["skill"], roots)) or "not installed here"))
    if not rows:
        return "no open entries with a readable adoption time"
    rows.sort()
    out = [f"{'skill':34s} {'loads':>5s} {'sessions since':>14s}  installed in"]
    out += [f"{s:34s} {n:5d} {a:14d}  {w}" for n, a, s, w in rows]
    silent = [r for r in rows if r[0] == 0]
    if silent:
        out.append(f"\n{len(silent)} of {len(rows)} were never loaded once since adoption. A rate "
                   "that moves in those windows moved for some other reason, and recheck.py "
                   "will refuse to confirm them.")
    return "\n".join(out)


def kg_rate(episodes, sig_tokens, sessions, since, until, rare=frozenset()):
    """Session-rate of corrections about this theme in a time window.

    One matcher, both windows: a knowledge-gap skill has no tool-error signature to
    count, so the comparison is the user's own corrections before vs after adoption.
    A denominator of all sessions in the window, not just the ones with episodes.
    """
    ids = {s["id"] for s in sessions if since <= s.get("ts", 0) < until}
    if not ids:
        return None, 0, 0
    hit = set()
    for e in episodes:
        if e.get("session") not in ids:
            continue
        shared = sig_tokens & tokens(e.get("corr", ""))
        # Two ordinary theme words, or one word that only this theme uses.
        if len(shared) >= 2 or (shared & rare):
            hit.add(e["session"])
    return len(hit) / len(ids), len(ids), len(hit)


def recheck_kg(entry, corr, dry):
    """Compare correction rates on this theme before and after the adoption timestamp."""
    failure = entry.get("failure") or {}
    if str(failure.get("derived_from", "")).startswith("skill_md:"):
        # Lifted from the skill's own description, which describes the skill rather than
        # the mistake. Such a matcher can pass every width and share check and still be
        # measuring vocabulary: extending the stopword list shrank three of these from
        # 35-42 distinct words to 18-20, under the cap, without making any of them more
        # about one theme. A verdict from one would uninstall a working skill on the
        # strength of its own prose. theme.py mines a real theme; until it does, skip.
        return None, ("signature was lifted from the skill's own description, which "
                      "measures its vocabulary rather than the mistake: mine a theme "
                      "with theme.py before this skill can be rechecked")
    sig_tokens = tokens(failure.get("signature", ""))
    sig_tokens |= tokens(" ".join(failure.get("user_rules", []) or []))
    if len(sig_tokens) < 3:
        return None, "theme signature too thin to match corrections"
    adopted = entry.get("adopted_at") or entry.get("ts")
    t_adopt = time.mktime(time.strptime(adopted, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    eps, sess = corr.get("episodes", []), corr.get("session_index", [])
    if not sess:
        return None, "no session index in the corrections run"
    if any("turns" not in s for s in sess):
        # An index mined before the length control cannot say which of its sessions could
        # have carried a correction, so its denominator counts sessions that never could.
        return None, ("this corrections run predates the session-length control and its "
                      "denominator cannot be trusted: re-mine before rechecking")
    if any("skills" not in s for s in sess):
        # Same standard as the line above. Without the per-session skill loads there is no
        # way to tell a skill that earned its improvement from one that never ran, and the
        # count reads zero either way - which would block every confirmation rather than
        # the ones that deserve it. Re-mining is what recheck.py does on every run anyway.
        return None, ("this corrections run predates the skill-usage index, so whether the "
                      "skill ever loaded cannot be told from it: re-mine before rechecking")
    after_span = (max((s.get("ts", 0) for s in sess), default=0) - t_adopt) / 86400
    if after_span < MIN_AFTER_DAYS:
        return None, (f"only {after_span:.1f} days of sessions since adoption, "
                      f"need {MIN_AFTER_DAYS}: a day of work cannot show a rate change")
    sess = eligible(sess)
    if not sess:
        return None, (f"no scanned session ran to {MIN_TURNS} typed turns, so none of them "
                      "could have carried a correction either way")
    sig_tokens, rare = distinctive(sig_tokens, eps)
    if len(sig_tokens) < 2:
        return None, ("every word in this theme is common across corrections, "
                      "so nothing distinguishes a session about it")
    if len(sig_tokens) > MAX_THEME_TOKENS:
        # A signature pasted from a whole skill body matches a bit of everything.
        # Whatever rate that produces is about the vocabulary, not about the theme.
        return None, (f"signature matches on {len(sig_tokens)} distinct words, more than "
                      f"{MAX_THEME_TOKENS}: too broad to be about one theme")
    until = time.time() + 86400
    before, n_before, hits_before = kg_rate(eps, sig_tokens, sess, 0, t_adopt, rare)
    after, n_after, hits_after = kg_rate(eps, sig_tokens, sess, t_adopt, until, rare)
    if n_after < 10 or n_before < 10:
        return None, f"not enough sessions to compare ({n_before} before, {n_after} after adoption)"
    shift = length_shift(sess, eps, t_adopt, until)
    if not IMPROVED <= shift <= 1 / IMPROVED:
        return None, (f"session length alone moves the correction rate {shift:.2f}x across the "
                      f"adoption date, as far as the {IMPROVED:.0%} the verdict turns on: this "
                      "window measures the shape of the work, not the skill")
    if hits_before < 2:
        # Nothing to improve on. A rate that was already zero cannot drop, and reading
        # that as "no improvement" would uninstall a working skill on no evidence.
        return None, (f"no baseline signal in the scanned window ({hits_before} matching "
                      f"sessions before adoption): widen --sessions or run where the user types")
    return {"baseline_failure_rate": round(before, 4), "current_failure_rate": round(after, 4),
            "sessions_scanned": n_before + n_after, "sessions_before": n_before,
            "sessions_after": n_after, "matching_before": hits_before,
            "matching_after": hits_after, "length_shift": round(shift, 3),
            # Carried on every verdict, not only the ones it blocks: a confirmation that
            # says how many times the skill actually ran is evidence, and one that cannot
            # is a rate with a story attached.
            "loads_after": loads(entry["skill"], sess, t_adopt, until),
            "metric": "correction_rate"}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--sources", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--usage", action="store_true",
                    help="report loads since adoption for every open entry and exit")
    args = ap.parse_args()

    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    src = ["--sources", args.sources] if args.sources else []

    ledger = os.path.join(root, "ledger.jsonl")
    rows = [json.loads(l) for l in open(ledger)]
    today = time.strftime("%Y-%m-%d")
    due = [r for r in rows if r.get("decision") in ("probation", "adopt")
           and r.get("recheck_due", "9999") <= today]
    already = {r.get("skill") for r in rows if r.get("decision") in ("adopt-confirmed", "revoked")}
    due = [r for r in due if r["skill"] not in already]
    if args.usage:
        # Every open entry, not just the ones a date has come due for: the question this
        # answers - is anything actually loading this skill - is most worth asking in the
        # weeks before the verdict, while there is still time to fix a description or an
        # install path. Reports and exits; no ledger row, no uninstall, whatever it finds.
        due = [r for r in rows if r.get("decision") in ("probation", "adopt")
               and r["skill"] not in already]
    if not due:
        print("no rechecks due")
        return

    here = os.path.dirname(os.path.abspath(__file__))
    # mine.py and corrections.py live in the sibling skill-miner skill
    miner = os.environ.get("MINER_SCRIPTS") or os.path.join(here, "..", "..", "skill-miner", "scripts")
    if not os.path.isfile(os.path.join(miner, "mine.py")):
        miner = here
    is_kg = lambda r: (r.get("failure") or {}).get("kind") == "correction"  # noqa: E731

    fresh, corr = None, None
    # A fresh $FORGE_ROOT has no mined/ yet; the miner writes into it, not around it.
    os.makedirs(os.path.join(root, "mined"), exist_ok=True)
    if any(not is_kg(r) for r in due):
        tmp = os.path.join(root, "mined", "recheck-failures.json")
        subprocess.run([sys.executable, os.path.join(miner, "mine.py"), "--sessions", str(args.sessions),
                        "--projects", args.projects, "--out", tmp] + src, check=True)
        fresh = json.load(open(tmp))
    if any(is_kg(r) for r in due) or args.usage:
        # --no-llm: episode extraction only. A recheck must never depend on a model call.
        tmp = os.path.join(root, "mined", "recheck-corrections.json")
        subprocess.run([sys.executable, os.path.join(miner, "corrections.py"), "--sessions",
                        str(args.sessions), "--max-episodes", "2000", "--per-session", "20",
                        "--projects", args.projects, "--no-llm", "--out", tmp] + src, check=True)
        corr = json.load(open(tmp))

    if args.usage:
        print(usage_report(due, corr.get("session_index", [])))
        return

    for entry in due:
        skill = entry["skill"]
        sig = (entry.get("failure") or {}).get("signature") or ""
        baseline = entry.get("baseline_failure_rate")
        if is_kg(entry):
            measured, why = recheck_kg(entry, corr, args.dry_run)
            if measured is None:
                print(f"SKIP {skill}: {why}")
                continue
            baseline, rate_now, total = (measured["baseline_failure_rate"],
                                         measured["current_failure_rate"],
                                         measured["sessions_scanned"])
            detail = (f"{measured['sessions_before']} sessions before, "
                      f"{measured['sessions_after']} after")
        else:
            if baseline is None:
                print(f"SKIP {skill}: no baseline rate recorded")
                continue
            if baseline <= 0:
                print(f"SKIP {skill}: baseline rate is 0, nothing to show an improvement against")
                continue
            if not sig.strip():
                print(f"SKIP {skill}: no failure signature recorded, nothing to match against")
                continue
            sig_tokens = set(re.findall(r"[a-z0-9]+", sig.lower()))
            rate_now = 0.0
            total = fresh.get("sessions_scanned", 0) or 1
            for c in fresh.get("clusters", []):
                ct = set(re.findall(r"[a-z0-9]+", c["signature"].lower()))
                if len(sig_tokens & ct) >= max(2, len(sig_tokens) // 2):
                    rate_now = c["session_count"] / total
                    break
            measured = {"baseline_failure_rate": baseline, "current_failure_rate": round(rate_now, 4),
                        "sessions_scanned": total, "metric": "tool_failure_rate"}
            detail = f"{total} sessions"
        improved = rate_now < baseline * IMPROVED
        if improved and measured.get("loads_after") == 0:
            # The rate fell in a window where this skill was never loaded once, so it fell
            # for some other reason. Not a revoke either: a skill that never ran has not
            # been shown to fail, only to have had no chance, and the entry stays due so a
            # window that does load it can decide. This is the one verdict the rate alone
            # gets backwards, and it gets it backwards in the direction that writes down a
            # win - which is how a loop that measures itself starts believing its own press.
            where = installed(skill)
            why = ("it is installed in " + ", ".join(where) + ", so the sessions could reach it "
                   "and did not choose it: the description is not matching the moment"
                   ) if where else (
                   "it is not installed in any root this recheck can see, so those sessions "
                   "could not have loaded it whatever its description says: install it where "
                   "the work happens, or recheck on the machine that has it")
            print(f"SKIP {skill}: correction rate fell {baseline:.2%} -> {rate_now:.2%}, but the "
                  f"skill was never loaded in the {measured['sessions_after']} sessions since "
                  f"adoption, so the drop is not evidence about it. {why}")
            continue
        verdict = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill": skill,
            "decision": "adopt-confirmed" if improved else "revoked",
            "from": entry["decision"],
        }
        verdict.update(measured)
        tag = "KEEP" if improved else "REVOKE"
        note = " [dry-run]" if args.dry_run else ""
        print(f"{tag}{note} {skill}: {baseline:.2%} -> {rate_now:.2%} ({detail})")
        if not improved:
            for line in uninstall(skill, root, args.dry_run):
                print(f"  {line}")
        if not args.dry_run:
            with open(ledger, "a") as fh:
                fh.write(json.dumps(verdict) + "\n")


if __name__ == "__main__":
    main()
