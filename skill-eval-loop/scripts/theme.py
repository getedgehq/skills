#!/usr/bin/env python3
"""Derive a theme narrow enough for the production recheck to measure.

Usage: theme.py [--corrections FILE] [--skill NAME] [--ledger PATH] [--apply]

The recheck compares how often the user corrects this theme before and after a
skill was adopted, which only means anything if "this theme" can be told apart
from every other correction. Seven of the ten skills adopted so far fail that:
three carry no failure record at all, and four carry one lifted from the skill's
own description, which is long and written in ordinary words. Matched against real
sessions those four claimed 33-43% of everything the user ever corrected, so the
recheck refuses them, correctly and permanently.

The theme is not missing, though. It is in the corrections themselves. This finds
it the way a theme should be found, from the corpus rather than from the prose:

  1. Seed from the skill: its name, the first sentence of its description, and the
     user's own words quoted in the body, minus the words common to all corrections.
  2. Pull the episodes those seeds match. Fewer than MIN_SEED_EPISODES and it stops:
     a theme nobody was corrected about has nothing to measure.
  3. Rank every word in that subset by how many of those episodes use it, keeping the
     top MAX_SIGNATURE and dropping anything common across the whole corpus. Ranking
     by lift is the textbook answer and it does not work at this corpus size: inside a
     30-episode subset of 136, almost every content word appears nowhere else, so every
     candidate scores the same lift and the ranking only looks informative.
  3b. Check the result is still about this skill. A corpus-driven ranking can drift
     onto a neighbouring topic that shares a few ordinary words, so the derived words
     have to overlap the description and include the thing the skill is named after.
  4. Measure the result against the whole corpus, and refuse it unless it is
     actually narrow: at least MIN_SIGNATURE recurring words, at most MAX_SHARE of
     sessions, and at least MIN_BEFORE matching sessions before the adoption, or
     there is no baseline to improve on.
  5. Compare it to every other skill's matcher, on the sessions each one matches. Two
     that cannot be told apart are one matcher under two names, and a rate change
     could not be attributed to either of them.

Expect it to refuse. Run against 136 real correction episodes it derived nothing for
seven adopted skills, each for a different stated reason, and that is the finding: a
voice or format skill is corrected in words too ordinary to separate from every other
correction, and no amount of ranking fixes that.

The obvious next move is more history, and it was tried: a 340-episode corpus, two and
a half times the size. It derived nothing either, and on the way it exposed two bugs in
this tool that the smaller corpus had hidden, both now fixed here. So the answer does
not turn on corpus size. A looser matcher would return a number, and the number would
be about the vocabulary.

Prints the signature, its share and its before/after split. --apply writes it to
the ledger tagged `derived_from: corrections:<n> episodes`, so it is never mistaken
for a hand-written one. It writes a matcher, never a measurement: the recheck still
applies all of its own refusals to whatever comes out of here.
"""
import argparse
import json
import os
import re
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recheck import STOP, distinctive, kg_rate, tokens  # noqa: E402

MIN_SEED_EPISODES = 4   # below this the "theme" is one or two bad days, not a pattern
MAX_SIGNATURE = 10      # the recheck refuses above 20; aim well under it
MAX_SHARE = 0.25        # a theme claiming more than a quarter of sessions is not one theme
MIN_BEFORE = 2          # no baseline, nothing to improve on
MIN_THEME_DF = 4        # a word has to turn up in this many of the theme's own episodes
MIN_SIGNATURE = 4       # fewer words than this and one filler word decides the rate
MAX_SEED_SHARE = 0.25   # a seed matching more than this is the description problem, one step earlier
MAX_CROSS_JACCARD = 0.25  # two themes this alike are one matcher under two names
MIN_STEM = 4              # shorter than this, a stem match is a substring search


def find_skill_md(skill, root):
    for d in (os.path.join(root, "adopted"), os.path.join(root, "drafts"),
              os.path.expanduser("~/.agents/skills"), os.path.expanduser("~/.claude/skills")):
        p = os.path.join(d, skill, "SKILL.md")
        if os.path.isfile(p):
            return p
    return None


def seed_terms(skill, md_path):
    """What this skill says it is about, in as few words as possible."""
    terms = set(re.findall(r"[a-z][a-z0-9]{2,}", skill.lower()))
    if md_path:
        with open(md_path, errors="replace") as fh:
            text = fh.read()
        m = re.search(r"^---\n(.*?)\n---", text, re.S)
        front, body = (m.group(1), text[m.end():]) if m else ("", text)
        d = re.search(r"^description:\s*(.+?)(?=\n\w+:|\Z)", front, re.S | re.M)
        if d:
            # First sentence only: the rest lists variants and drags in half a dictionary.
            terms |= tokens(re.split(r"(?<=[.!?])\s", " ".join(d.group(1).split()))[0])
        for q in re.findall(r"[\"“]([^\"“”]{15,120})[\"”]", body)[:6]:
            terms |= tokens(q)
    return {t for t in terms if t not in STOP}


def rank(seed_eps, all_eps):
    """The words this theme's corrections actually keep coming back to.

    Ranking by lift, how much more often a word appears here than in the corpus at
    large, is the textbook answer and it does not survive contact with a real
    correction corpus. At 136 episodes almost every content word inside a 30-episode
    subset appears nowhere else in the corpus, so every candidate scores the same
    lift of n_all/n_seed and the ranking carries no information at all. It only looks
    like it does, which is worse than not ranking.

    So rank on what the corpus can actually support: how many of this theme's own
    episodes use the word, with a floor, and a ceiling on how common it is overall.
    That leaves ordinary filler in the list when the user happens to type it a lot,
    which is why nothing here is trusted on its own: the derived signature still has
    to pass the share and baseline checks below before it is written anywhere.
    """
    n_all, n_seed = len(all_eps), len(seed_eps)
    df_all, df_seed = {}, {}
    for eps, df in ((all_eps, df_all), (seed_eps, df_seed)):
        for e in eps:
            for w in tokens(e.get("corr", "")):
                df[w] = df.get(w, 0) + 1
    # An absolute floor, not a proportional one. A share of the seed looks like the
    # careful choice and does the opposite as the corpus grows: tripling the corpus took
    # one skill's seed from 58 episodes to 135, so a 20% floor went from 11 to 27 while
    # its most distinctive word only went from 6 to 15. The theme word got thrown away
    # for being outnumbered by a seed that was too broad in the first place, which is a
    # different problem, caught by MAX_SEED_SHARE above.
    floor = MIN_THEME_DF
    scored = []
    for w, k in df_seed.items():
        if k < floor:
            continue
        if df_all.get(w, 0) / n_all > MAX_SHARE:
            continue  # common everywhere, so it cannot separate this theme from the rest
        scored.append((k, w))
    scored.sort(reverse=True)
    return [w for _, w in scored]


def named(words, skill):
    """Whether any derived word is the thing the skill is named after.

    Matched on a shared prefix rather than whole words, because the name and the corpus
    rarely agree on the ending or the language: german-umlauts is corrected about in
    German, where the word is "umlaute", and the two names diverge at the last letter.
    MIN_STEM keeps that from becoming a substring search, both by ignoring short words
    ("ui" in match-existing-ui would otherwise match "build") and by requiring the
    agreement itself to be that long.
    """
    stems = [w for w in tokens(skill.replace("-", " ")) if len(w) >= MIN_STEM]
    return any(len(os.path.commonprefix([w, s])) >= MIN_STEM
               for w in words if len(w) >= MIN_STEM for s in stems)


def matched(sig, eps, sess):
    """The sessions a signature matches over the whole corpus.

    The same rule the recheck itself applies, so what is compared below is the matcher
    as it will actually be used, not a description of it.
    """
    words, rare = distinctive(set(sig.split()), eps)
    ids = {s["id"] for s in sess}
    hit = set()
    for e in eps:
        if e.get("session") not in ids:
            continue
        shared = words & tokens(e.get("corr", ""))
        if len(shared) >= 2 or (shared & rare):
            hit.add(e["session"])
    return hit


def collision(hits, skill, derived, keepers):
    """The other skill this theme cannot be told apart from, if there is one.

    A signature only measures one skill if it does not also measure the next one. On a
    340-episode corpus four skills produced ten-word themes that shared half their words
    and returned the same share and the same before/after counts to the episode, because
    all four were matching one generic cluster of content work. Each looked narrow on its
    own; together they were one matcher wearing four names, and a rate change could not
    have been attributed to any of them.

    Compared on the sessions each one matches, not on the words each one is made of.
    Word overlap is the convenient proxy and it misses exactly this case: two of those
    four shared only three words out of seventeen, a Jaccard of 0.18, while matching the
    same sessions to within one episode either side. Synonyms of one another read as
    distinct vocabularies and behave as one matcher, and it is the behaviour that decides
    whether a rate change can be attributed.
    """
    others = {r["skill"]: g["_hits"] for r, g in derived}
    others.update(keepers)
    worst, worst_j = None, 0.0
    for name, other in others.items():
        if name == skill or not (hits | other):
            continue
        j = len(hits & other) / len(hits | other)
        if j > worst_j:
            worst, worst_j = name, j
    return (worst, worst_j) if worst_j > MAX_CROSS_JACCARD else (None, worst_j)


def derive(skill, adopted_at, md_path, corr):
    eps, sess = corr.get("episodes", []), corr.get("session_index", [])
    if not eps or not sess:
        return None, "the corrections run produced no episodes to mine a theme from"
    seed = seed_terms(skill, md_path)
    keep, rare = distinctive(seed, eps)
    if not keep:
        return None, "every word this skill describes itself with is common across corrections"
    seed_eps = [e for e in eps
                if len(keep & tokens(e.get("corr", ""))) >= 2 or (keep & rare & tokens(e.get("corr", "")))]
    if len(seed_eps) < MIN_SEED_EPISODES:
        return None, (f"only {len(seed_eps)} corrections look like this skill's subject, "
                      f"need {MIN_SEED_EPISODES}: not enough to name a theme")
    seed_share = len(seed_eps) / len(eps)
    if seed_share > MAX_SEED_SHARE:
        # The words this skill describes itself with already match most of the corpus,
        # so there is no subset here to mine: whatever gets ranked out of it is ranked
        # out of everything. This is the same breadth that makes a description-derived
        # signature useless to the recheck, caught one step earlier and stated plainly
        # instead of surfacing later as "no word recurs often enough".
        return None, (f"the words this skill describes itself with already match "
                      f"{seed_share:.0%} of all corrections, over {MAX_SEED_SHARE:.0%}: "
                      "there is no subset of the corpus that is about this skill")
    words = rank(seed_eps, eps)[:MAX_SIGNATURE]
    if len(words) < MIN_SIGNATURE:
        # Two or three words is not a theme, it is a coincidence with a filler word in
        # it. "post real" and "much post text" both passed every statistical check here
        # while being, on inspection, about nothing: whatever rate they produce is
        # driven by the filler half of the pair.
        return None, (f"only {len(words)} word(s) recur across these corrections, need "
                      f"{MIN_SIGNATURE}: too thin to be a theme rather than a coincidence")
    # The ranking comes from the corpus, so it can drift off the skill entirely: the
    # first signature this produced for a "reuse what already exists" skill was
    # "find getedge monid post posts skill visuals", a perfectly real topic cluster
    # about one website's pages that has nothing to do with reusing assets. Statistics
    # cannot notice that; requiring the result to still overlap what the skill says it
    # is about can.
    #
    # Overlapping the description is not enough, though, and that same signature is why.
    # A description names its subject once and then spends a sentence on context, so
    # "find", "posts" and "visuals" are all in it and all ordinary enough to belong to
    # any topic, while "reuse", "existing" and "assets" appear 0-1 times in the whole
    # corpus. Rarity cannot separate those either: at 136 episodes every seed word sits
    # under the 12.5% bar, so the rare subset was the entire seed. What does separate
    # them is the skill's own name, which is the one place the subject is stated without
    # its context. A name word can still be an ordinary one ("post" in li-post-fede),
    # so this is a floor rather than a guarantee; what it rules out is the whole class
    # where the theme keeps a description's scenery and drops its subject.
    overlap = set(words) & keep
    if len(overlap) < 2 or not named(words, skill):
        return None, (f"the recurring words ({' '.join(words[:6])}) are a topic in the "
                      f"corpus but not what {skill} is named after: theme drifted off")
    sig = set(words)
    sig, sig_rare = distinctive(sig, eps)
    t_adopt = time.mktime(time.strptime(adopted_at, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    before, n_before, hits_before = kg_rate(eps, sig, sess, 0, t_adopt, sig_rare)
    after, n_after, hits_after = kg_rate(eps, sig, sess, t_adopt, time.time() + 86400, sig_rare)
    ids = {s["id"] for s in sess}
    hits_matched = matched(" ".join(sorted(sig)), eps, sess)
    share = len(hits_matched) / len(ids) if ids else 1.0
    if share > MAX_SHARE:
        return None, (f"the derived theme still matches {share:.0%} of sessions, over "
                      f"{MAX_SHARE:.0%}: this skill's subject is not distinguishable in "
                      "corrections")
    if hits_before < MIN_BEFORE:
        return None, (f"only {hits_before} matching sessions before adoption: no baseline "
                      "for the recheck to compare against")
    return {"signature": " ".join(sorted(sig)), "share": round(share, 4),
            "episodes_seeded": len(seed_eps), "_hits": hits_matched,
            "before": {"rate": round(before, 4), "sessions": n_before, "matching": hits_before},
            "after": {"rate": round(after, 4) if after is not None else None,
                      "sessions": n_after, "matching": hits_after}}, None


def main():
    ap = argparse.ArgumentParser()
    root = os.environ.get("FORGE_ROOT", os.path.expanduser("~/skill-forge"))
    ap.add_argument("--corrections", default=os.path.join(root, "mined", "corrections.json"),
                    help="output of corrections.py --no-llm")
    ap.add_argument("--ledger", default=os.path.join(root, "ledger.jsonl"))
    ap.add_argument("--skill", default=None, help="one skill; default is every adopted one")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--redo", action="store_true",
                    help="also re-derive skills whose signature came from a skill body")
    args = ap.parse_args()

    if not os.path.exists(args.corrections):
        sys.exit(f"no corrections report at {args.corrections}; run corrections.py --no-llm first")
    corr = json.load(open(args.corrections))
    rows = [json.loads(l) for l in open(args.ledger) if l.strip()]
    decided = {r["skill"] for r in rows if r.get("decision") in ("revoked", "reject-final")}

    # Derive first, decide after: whether a signature identifies one skill can only be
    # answered against the other signatures, so nothing is written until all of them exist.
    derived, keepers = [], {}
    for r in rows:
        if r.get("decision") not in ("adopt", "probation") or r.get("skill") in decided:
            continue
        f = r.get("failure") or {}
        src = str(f.get("derived_from", ""))
        settled = (f.get("signature") or "").strip() and not (args.redo and src.startswith("skill_md:"))
        if settled:
            if not src.startswith("skill_md:"):
                keepers[r["skill"]] = matched(f["signature"], corr.get("episodes", []),
                                              corr.get("session_index", []))
            continue
        if args.skill and r["skill"] != args.skill:
            continue
        md = find_skill_md(r["skill"], root)
        got, why = derive(r["skill"], r.get("adopted_at") or r.get("ts"), md, corr)
        if why:
            print(f"SKIP {r['skill']}: {why}")
            continue
        derived.append((r, got))

    changed = 0
    for r, got in derived:
        rival, overlap = collision(got["_hits"], r["skill"], derived, keepers)
        if rival:
            print(f"SKIP {r['skill']}: matches the same sessions as {rival} "
                  f"({overlap:.0%} of them), so a rate change could not be "
                  "attributed to either")
            continue
        print(f"{r['skill']}: {got['share']:.0%} of sessions, "
              f"{got['before']['matching']}/{got['before']['sessions']} before -> "
              f"{got['after']['matching']}/{got['after']['sessions']} after")
        print(f"     {got['signature']}")
        r["failure"] = {"kind": "correction", "signature": got["signature"],
                        "user_rules": (r.get("failure") or {}).get("user_rules", []),
                        "derived_from": f"corrections:{got['episodes_seeded']} episodes"}
        changed += 1

    if not changed:
        print("no themes derived")
        return
    if not args.apply:
        print(f"\n{changed} rows would change; rerun with --apply")
        return
    bak = args.ledger + ".bak-" + time.strftime("%Y%m%d%H%M%S")
    shutil.copy2(args.ledger, bak)
    with open(args.ledger, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"\n{changed} rows updated; previous ledger kept at {bak}")


if __name__ == "__main__":
    main()
