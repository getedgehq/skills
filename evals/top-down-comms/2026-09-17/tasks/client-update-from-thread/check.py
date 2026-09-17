#!/usr/bin/env python3
"""Hard checks for top-down-comms.client-update-from-thread.  Usage: python3 check.py <collected_dir>

Planted ground truth (input/slack_export_halden-migration.txt + call notes). Nobody in the thread
states any of these conclusions; each has to be assembled from the evidence:
  - recommendation: option B. Go live Mon Oct 5 with Jan 2019+ records (2.09M, all passing),
    pre-2019 archive cleansed and loaded read-only by Mon Nov 30. Option A (Oct 19) lands inside
    the Oct 12 - Dec 20 peak freeze Rosa ruled out, and costs 3x.
  - decision deadline: Fri Sep 18 EOD. Stratacore need the freeze window 10 business days before
    the Oct 5 cutover (Mon Sep 21) plus a day to file. The thread's explicit "by the 25th" is stale.
  - signer: Mira Castellanos, IT Director (SOW 7.2). NOT Tomasz (parental leave), NOT Rosa (sponsor).
  - failure count: 312,004 / 13% of 2.4M, in a pasted log. The prose number "roughly 40k" was a
    skewed morning sample and is never retracted in words.
  - option B cost: EUR 6,200 after Jonas re-scoped. The earlier "roughly 9k" is stale. A = 18,400.
  - content that belongs elsewhere: the ops dashboard upsell (35k), and Jonas's "not on us" framing,
    neither of which anyone in the thread pushes back on.
"""
import json
import os
import re
import sys

TEXT_EXT = {".md", ".txt", ".eml", ".html", ".htm", ".rst", ""}
INPUT_NAMES = {"slack_export_halden-migration.txt", "call_notes_halden_2026-09-10.md"}


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def collect(root):
    files = {}
    for dp, _, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            if os.path.splitext(fn)[1].lower() in TEXT_EXT and os.path.getsize(p) < 500_000:
                files[rel] = read(p)
    return files


def primary_doc(files):
    def is_input(rel):
        return os.path.basename(rel).lower() in INPUT_NAMES

    out = {k: v for k, v in files.items() if k.replace("\\", "/").startswith("output/") and not is_input(k)}
    pool = out or {k: v for k, v in files.items() if k != "final_message.md" and not is_input(k)}
    pool = {k: v for k, v in pool.items() if len(v.split()) >= 40}
    if pool:
        k = max(pool, key=lambda k: len(pool[k]))
        return k, pool[k]
    return "final_message.md", files.get("final_message.md", "")


def unwrap(text):
    """Join hard-wrapped prose lines so sentence-level regexes are not defeated by line breaks.
    Table rows, headings and list items stay on their own line."""
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        prev = out[-1].strip() if out else ""
        joinable = (
            out and prev and s
            and not prev.endswith(("|", ".", "!", "?", ":", ";"))
            and not prev.startswith(("#", "|"))
            and not s.startswith(("#", "|", "-", "*", ">", "=", "_"))
            and not re.match(r"^\d{1,2}[.)]\s", s)
        )
        if joinable:
            out[-1] = out[-1].rstrip() + " " + s
        else:
            out.append(ln)
    return "\n".join(out)


def strip_html(t):
    return re.sub(r"<[^>]+>", " ", t)


def words(t):
    return re.findall(r"\S+", t)


def body_words(t):
    keep = []
    for ln in t.splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if re.fullmatch(r"[|:\-\s+=_*]+", s):
            continue
        keep.append(re.sub(r"^\s*([-*>]|\d{1,2}[.)])\s+", "", ln))
    return len(words("\n".join(keep)))


def first_word_index(text, pattern):
    m = re.search(pattern, text, re.I | re.S)
    if not m:
        return None
    return len(words(text[: m.start()]))


def body_without_greeting(text):
    out = []
    for ln in text.splitlines():
        if re.match(r"^\s*(hi|hello|dear|hey)\b[^.!?]{0,40}[,!]?\s*$", ln, re.I):
            continue
        out.append(ln)
    return "\n".join(out)


def strip_subject(text):
    return re.sub(r"(?im)^\s*(\*\*)?subject(\*\*)?\s*:.*$", "", text)


def top_limit(total):
    return int(min(130, max(60, 0.35 * total)))


SEP18 = r"(sep(t(ember)?)?\.?\s*18(th)?\b|\b18(th)?\s*(of\s*)?sep(t(ember)?)?\b|\b0?9/18\b|\b18\.0?9\b|2026-09-18|fri(day)?,?\s*(the\s*)?18(th)?\b)"
SEP25 = r"(sep(t(ember)?)?\.?\s*25(th)?\b|\b25(th)?\s*(of\s*)?sep(t(ember)?)?\b|\b0?9/25\b|\b25\.0?9\b|2026-09-25|\bthe\s*25th\b)"
OCT5 = r"(oct(ober)?\.?\s*0?5(th)?\b|\b0?5(th)?\s*(of\s*)?oct|\b10/0?5\b|\b0?5\.10\b|2026-10-05)"


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]


def main():
    root = sys.argv[1]
    files = collect(root)
    name, doc = primary_doc(files)
    doc = unwrap(body_without_greeting(strip_html(doc)))
    total = len(words(doc))
    prose = body_words(doc)
    lim = top_limit(total)
    details = [f"primary doc: {name} ({total} words, {prose} prose words, top window {lim} words)"]
    gates, items = [], []

    def item(label, ok, gate=False):
        (gates if gate else items).append(bool(ok))
        details.append(("PASS " if ok else "FAIL ") + ("[gate] " if gate else "") + label)

    # --- gate 1: the recommendation (option B) is what the reader meets first
    i_oct5 = first_word_index(doc, OCT5)
    i_2019 = first_word_index(doc, r"\b2019\b")
    rec_top = i_oct5 is not None and i_2019 is not None and max(i_oct5, i_2019) <= lim + 30
    item(f"recommendation (Oct 5 go-live, 2019+ records) in the top section (oct5@{i_oct5}, 2019@{i_2019})", rec_top, gate=True)

    # --- gate 2: the real deadline, near the top
    i18 = first_word_index(doc, SEP18)
    item(f"Fri Sep 18 decision deadline in the top section (first at word {i18})", i18 is not None and i18 <= lim + 25, gate=True)

    # --- gate 3: the corrected failure count, not the morning sample
    item("uses the full-run failure count (312,000 / 13%)",
         bool(re.search(r"312[,. ]?0?0?4?\b|312\s*k\b|\b13\s*%|\b13 percent", doc, re.I)), gate=True)

    # --- gate 4: the right signer
    mira = bool(re.search(r"\bmira\b|castellanos", doc, re.I))
    tom_signs = bool(re.search(r"tomasz[^.\n]{0,60}(sign|approv|countersign)", doc, re.I)) and not re.search(
        r"tomasz[^.\n]{0,80}(leave|out|away|absent|no longer)", doc, re.I)
    item("routes sign-off to Mira Castellanos and not to Tomasz", mira and not tom_signs, gate=True)

    # --- gate 5: the stale informal date is not repeated as the deadline
    stale25 = any(re.search(SEP25, s, re.I) and not re.search(
        r"\bnot\b|instead|earlier|correct|disregard|too late|rather than|supersed|replac|no longer|ignore|apolog|mistake|wrong|please treat", s, re.I)
        for s in sentences(doc))
    item("does not state 'the 25th' as the decision deadline", not stale25, gate=True)

    # --- gate 6: option A's price is not the headline number
    i18400 = first_word_index(doc, r"18[,. ]?400|18\.4\s*k")
    i6200 = first_word_index(doc, r"6[,. ]?200|6\.2\s*k")
    # Listing option A before option B is not headlining A. Fail only if 18,400 sits in the opening, or is
    # attached to the recommendation, or option B's 6,200 never appears.
    a_recommended = any(re.search(r"18[,. ]?400|18\.4\s*k", ln, re.I) and re.search(r"recommend|propos|our advice|we suggest", ln, re.I)
                        and not re.search(r"not recommend|option b|\bB\)", ln, re.I) for ln in doc.splitlines())
    a_not_headline = i18400 is None or (i18400 > 60 and i6200 is not None and not a_recommended)
    item(f"option A's EUR 18,400 is not the leading figure (18400@{i18400}, 6200@{i6200})", a_not_headline, gate=True)

    # --- gate 7: the opening carries an ask, a date and an owner
    opening = " ".join(words(strip_subject(doc))[:70])
    has_ask = bool(re.search(r"recommend|propos|we suggest|our advice|we plan to|need (you|your|mira|a decision|sign)|asking|ask you|please sign|sign(ed|ing|-off| off)?\b|approv|decision|decide|confirm|go live|going live|proceed", opening, re.I))
    has_date = bool(re.search(r"(sep|oct)\w*\.?\s*\d{1,2}|\b\d{1,2}\s*(sep|oct)\w*|fri(day)?[^.]{0,14}\b\d{1,2}|\b(18|5)th\b|\b\d{1,2}/\d{1,2}\b", opening, re.I))
    has_owner = bool(re.search(r"\bmira\b|castellanos|it director|\bros[ae]\b|\byou\b|\byour\b|halden", opening, re.I))
    item(f"first 70 words carry an ask, a date and an owner (ask={has_ask}, date={has_date}, owner={has_owner})",
         has_ask and has_date and has_owner, gate=True)

    # --- items
    item("excludes the ops dashboard upsell", not re.search(r"dashboard|\b35[,. ]?000\b|\b35\s*k\b", doc, re.I))

    first_chunk = " ".join(words(strip_subject(doc))[:40])
    blame = re.search(r"not (on|caused by|due to|the result of) (us|northpine|our)|not our (fault|doing|responsib)|"
                      r"originat\w+ in (the |their )?legacy|legacy system'?s? (fault|data quality)|not responsible|"
                      r"outside (of )?our (scope|control)|\bfault\b|inherited", first_chunk, re.I)
    item("opening is not a blame or self-defence line", not blame)

    item("explains the timing mechanism (Stratacore / freeze window / 10 business days / peak)",
         bool(re.search(r"stratacore|freeze|peak|10 business|ten business|10 working", doc, re.I)))
    item("both options are visible with their cost (18,400 and 6,200)",
         bool(re.search(r"18[,. ]?400|18\.4\s*k", doc, re.I)) and bool(re.search(r"6[,. ]?200|6\.2\s*k", doc, re.I)))
    stale9k = any(re.search(r"\b9[,. ]?000\b|\b9\s*k\b|\bEUR\s*9\b", s, re.I) and not re.search(
        r"\bnot\b|earlier|initial|first|revis|re-?scop|correct|instead|was\b", s, re.I) for s in sentences(doc))
    item("does not quote the superseded ~EUR 9k figure for option B", not stale9k)
    item("names the Nov 30 read-only archive date", bool(re.search(r"nov(ember)?\.?\s*30|30\s*nov", doc, re.I)))
    item("says the old WMS / archive covers pre-2019 lookups in the meantime",
         bool(re.search(r"read[- ]only|old (wms|system)|legacy (wms|system)[^.\n]{0,40}(until|stays|remains|available)|archive", doc, re.I)))
    item("says option A would land inside the peak-season freeze (Oct 19 / Oct 12)",
         bool(re.search(r"oct(ober)?\.?\s*19|19\s*oct", doc, re.I)) and bool(re.search(r"peak|freeze|oct(ober)?\.?\s*12", doc, re.I)))
    item("ends with a concrete, checkable next step (who does what, by when)",
         bool(re.search(r"(sign|approv|confirm|reply|respond)[^.\n]{0,80}(fri|sep|18|eod|end of day|by )", doc, re.I)))
    item(f"phone-length ({prose} prose words <= 340)", prose <= 340)

    allitems = gates + items
    score = round(sum(allitems) / len(allitems), 3)
    print(json.dumps({"pass": all(gates), "score": score, "details": details}))


if __name__ == "__main__":
    main()
