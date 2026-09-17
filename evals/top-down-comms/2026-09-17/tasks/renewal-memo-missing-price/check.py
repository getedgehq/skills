#!/usr/bin/env python3
"""Hard checks for top-down-comms.renewal-memo-missing-price.  Usage: python3 check.py <collected_dir>

Planted ground truth:
  - notice deadline: clause 9.2, thirty days before the 31 Oct 2026 term end -> Thu 1 Oct 2026.
    The channel says twice that there is "until the end of October", which is wrong.
  - the renewal price cannot be known in time: clause 3.2 is the then-current list price, Tallow
    publish the new list in "early October" (after the notice deadline) and Lukas is out until 28 Sep.
  - trap figure: Marek's ~EUR 52,800 (a 10% guess), repeated three times and already pasted into the
    FY27 board pack as a placeholder. It must never be presented as next year's cost.
  - seat data: 60 assigned, 38 active (Aug export). Clause 3.3: a reduction must be requested in
    writing BEFORE the 9.2 notice deadline, which contradicts Lukas's "applied at the renewal date"
    and Marek's "raise it when we renew".
  - decoy: clause 9.4's sixty (60) day cure period for material breach is not the notice period.
  - baseline: EUR 48,000 (60 seats at EUR 800). FY27 board pack needs a number by 8 Oct.

The three gates the v1 checker got wrong (paragraph-scoped hedge context, a bare `by` trigger on the
wrong-deadline gate, and a word cap that counted headings) are rewritten here to test substance:
is the missing price surfaced, is the decision at the top, is the guessed number kept out of the
"what it costs" slot, and is the wrong deadline not asserted.
"""
import json
import os
import re
import sys

TEXT_EXT = {".md", ".txt", ".eml", ".html", ".htm", ".rst", ""}
INPUT_NAMES = {"tallow_contract_excerpt.md", "emails_with_tallow.md", "ops_channel_notes.txt",
               "seat_usage_aug2026.csv"}


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
    """Prose length. Headings, table rules and list markers are not reading time (paper_check style)."""
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


def top_limit(total):
    return int(min(130, max(60, 0.35 * total)))


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if s.strip()]


# 1 Oct 2026 (or the conservative 30 Sep)
OCT1 = (r"(oct(ober)?\.?\s*0?1(st)?\b|\b0?1(st)?\s*(of\s*)?oct(ober)?\b|\b10/0?1\b|\b0?1\.10\.|2026-10-01"
        r"|sep(t(ember)?)?\.?\s*30(th)?\b|\b30(th)?\s*(of\s*)?sep(t(ember)?)?\b|2026-09-30)")
ACTION = (r"recommend|propos|we should|my advice|suggest|do not renew|don'?t renew|serve (written )?notice|"
          r"send (written )?notice|give (written )?notice|notice of non-?renewal|decision|decide|you need to|"
          r"needs? a decision|act (now|by|before)")
# the price for the renewal term is not knowable in time
UNKNOWN = (r"unknown|not (yet )?(known|available|published|confirmed|received|quoted|out)|no (firm |written |confirmed )?(quote|price|number|figure)|"
           r"(haven'?t|have not|hasn'?t|has not|won'?t|will not)[^.\n]{0,40}(quote|price|publish|confirm|receive|share)|"
           r"(can'?t|cannot|won'?t) (yet )?(know|say|tell|answer|be answered)|unconfirmed|\btbd\b|\btbc\b|to be confirmed|"
           r"only after|after the (notice )?(window|deadline)|not until (early )?october|no way to know")
PRICEWORD = r"price|pricing|quote|cost|list|fee|rate|number|figure|renewal term|next year"
# an epistemic hedge, NOT a mere approximation marker ("about", "approx", "~" do not count)
HEDGE = (r"assum|guess|placeholder|unconfirmed|not confirmed|unknown|no(t)? (yet )?(known|published|available|quoted|confirmed)|"
         r"illustrat|scenario|hypothetic|for planning|planning number|working number|provisional|indicative|marek'?s\b|"
         r"at (today'?s?|current) (price|rate|list)|current (list|price|rate)|per seat|worst case|best case|"
         r"\btbd\b|\btbc\b|not a quote|no quote|extrapolat|internal estimate|our estimate|"
         r"finance'?s? (estimate|guess|number)|years? ago|not (a|an) (offer|quote|price)|has not been quoted")
NOT_A_COST = (r"sav(e|es|ing|ings)\b|if tallow quotes|quotes? above|above eur|below eur|threshold|kill condition|"
              r"cobbleworth|competitor|alternative vendor|other vendor")
# "wrong deadline" exemptions that hold for a whole sentence, not just the clause they sit in
STRONG_EXEMPT = r"\bwrong\b|incorrect|misread|mistaken|actually|no longer|too late|is later than|after the notice|rather than|instead"


def clauses(sentence):
    return [c for c in re.split(r",\s*(?=so\b|and\b|but\b|which\b)|;", sentence) if c.strip()]
WRONG_TRIG = (r"end of (the )?octo|end-of-octo|all of october|rest of october|by (the )?31st?\b|31\s*oct|"
              r"oct(ober)?\.?\s*31|until (the end of )?october")
WRONG_MEAN = r"deadline|decide|decision|notice|respond|reply|act\b|have until|we have|time to|to make|before we"
WRONG_EXEMPT = (r"term ends|term end|contract (runs|ends|expires|is up)|contract end|end date|expires|expiry|renewal date|renews on|"
                r"auto-?renew|end of (the )?(then-?current )?term|current term|\bnot\b|wrong|incorrect|actually|"
                r"rather than|instead|misread|no longer|too late|is later than|after the notice")


def money_values(text):
    """Yield (span_start, literal, value) for every currency-sized number in the text."""
    pat = re.compile(r"(?:eur|€|\$)?\s?(\d{1,3}(?:[,. ]\d{3})+(?:\.\d{1,2})?|\d{2,3}(?:[.,]\d)?\s*k\b|\b\d{5,6}\b)", re.I)
    for m in pat.finditer(text):
        lit = m.group(1)
        if re.search(r"([A-Za-z]{1,6}-|#|\bno\.?\s?|ticket\s)$", text[max(0, m.start(1) - 8): m.start(1)], re.I):
            continue  # an identifier such as TS-88417, not an amount
        raw = lit.strip()
        try:
            if raw.lower().rstrip().endswith("k"):
                val = float(re.sub(r"[^\d.]", "", raw.replace(",", "."))) * 1000
            else:
                val = float(re.sub(r"[^\d]", "", raw))
        except ValueError:
            continue
        yield m.start(1), raw, val


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

    # --- gate 1: the missing price is surfaced as a fact about the price ---
    surfaced = False
    for m in re.finditer(UNKNOWN, doc, re.I):
        ctx = doc[max(0, m.start() - 200): m.end() + 200]
        if re.search(PRICEWORD, ctx, re.I):
            surfaced = True
            break
    item("says plainly that next year's price is not known / not published yet", surfaced, gate=True)

    # --- gate 2: no guessed figure is presented as the cost ---
    invented = []
    for pos, lit, val in money_values(doc):
        if abs(val - 48000) < 1 or val < 10000 or val > 500000:
            continue
        if val % 800 == 0 and val / 800 <= 60:
            continue  # seat arithmetic at the known current per-seat price
        ls, le = doc.rfind("\n", 0, pos) + 1, doc.find("\n", pos)
        if re.search(NOT_A_COST, doc[ls: le if le != -1 else len(doc)], re.I):
            continue  # a saving, a threshold or another vendor's quote, not next year's Tallow cost
        ctx = doc[max(0, pos - 400): pos + 400]
        if not re.search(HEDGE, ctx, re.I):
            invented.append(lit)
    item(f"no guessed renewal figure presented as fact (unhedged within 400 chars: {invented})",
         not invented, gate=True)

    # --- gate 3: the decision and the real notice date are at the top ---
    top = " ".join(words(doc)[:lim])
    has_action = bool(re.search(ACTION, top, re.I))
    i_oct1 = first_word_index(doc, OCT1)
    item(f"decision and the 1 Oct notice date are in the top window (action={has_action}, oct1@{i_oct1})",
         has_action and i_oct1 is not None and i_oct1 <= lim + 25, gate=True)

    # --- gate 4: the stale "end of October" is not asserted as the deadline ---
    wrong = []
    for s in sentences(doc):
        if re.search(STRONG_EXEMPT, s, re.I):
            continue
        for c in clauses(s):
            if (re.search(WRONG_TRIG, c, re.I) and re.search(WRONG_MEAN, c, re.I)
                    and not re.search(WRONG_EXEMPT, c, re.I) and not re.search(OCT1, c, re.I)):
                wrong.append(c.strip())
                break
    item(f"does not present end of October as the decision deadline (offending: {wrong[:1]})", not wrong, gate=True)

    # --- items ---
    item("the unknown price is flagged early, not only at the end",
         any(re.search(PRICEWORD, doc[max(0, m.start() - 200): m.end() + 200], re.I)
             and len(words(doc[:m.start()])) <= lim + 40
             for m in re.finditer(UNKNOWN, doc, re.I)))
    item("explains the automatic renewal",
         bool(re.search(r"auto(matic(ally)?)?[- ]?renew|renews? (itself )?automatically|rolls? over|roll ?over|"
                        r"renews? us|renews? for (a further |another )?(twelve|12|one)|another (twelve|12) months?|"
                        r"another year|for (a further |another )?(twelve|12) months?", doc, re.I)))
    item("uses the 30 day notice period from the agreement", bool(re.search(r"30[- ]day|thirty \(?30\)?|thirty day", doc, re.I)))
    sixty = any(re.search(r"\b60[- ]day|sixty \(?60\)?", s, re.I) and re.search(r"notice|deadline|non-?renewal|renew", s, re.I)
                and not re.search(r"breach|cure|uncured|material|9\.4", s, re.I) for s in sentences(doc))
    item("does not mistake the 60 day breach cure period for the notice period", not sixty)
    item("states the trap: the window closes before the price exists",
         bool(re.search(r"(before|ahead of|earlier than)[^.\n]{0,80}(price|quote|list|publish)|"
                        r"(price|quote|list)[^.\n]{0,80}(after|too late|once the (window|deadline))|"
                        r"(window|deadline|notice)[^.\n]{0,80}(closes?|passes?|expires?)[^.\n]{0,60}(before|without)", doc, re.I)))
    item("uses the August seat data (38 active of 60)", bool(re.search(r"\b38\b", doc)) and bool(re.search(r"\b60\b", doc)))
    item("says a seat reduction must be requested in writing before the notice deadline",
         bool(re.search(r"(seat|licence|license)[^.\n]{0,140}(before|by)[^.\n]{0,60}(notice|deadline|1 oct|oct(ober)?\.?\s*1)|"
                        r"(reduc\w+|cut\w*|drop\w*|fewer seats)[^.\n]{0,140}(in writing|written request|written notice|in the same written)|"
                        r"(in writing|written request)[^.\n]{0,140}(reduc\w+|fewer seats|seat count)", doc, re.I)))
    item("gives the current EUR 48,000 baseline", bool(re.search(r"48[,. ]?000|48\s*k\b", doc, re.I)))
    item("asks Tallow for a firm written quote before the deadline",
         bool(re.search(r"(firm|written|binding|confirmed)[^.\n]{0,25}(quote|price|offer|number)|"
                        r"(quote|pricing|price)[^.\n]{0,60}(before|by) (thu|fri|mon|1 oct|oct|29|30|sep)", doc, re.I)))
    item("names an owner for the next steps (Jonas / Priya)", bool(re.search(r"\bjonas\b|\bpriya\b", doc, re.I)))
    item("handles the 8 Oct board budget number without inventing one",
         bool(re.search(r"oct(ober)?\.?\s*0?8|\b0?8\s*oct|board pack|fy27|budget draft", doc, re.I)))
    item("names how notice must be given (email to contracts@tallow.example)",
         bool(re.search(r"contracts@tallow|in writing|written notice|by email", doc, re.I)))
    item(f"one page ({prose} prose words <= 500)", prose <= 500)

    allitems = gates + items
    score = round(sum(allitems) / len(allitems), 3)
    print(json.dumps({"pass": all(gates), "score": score, "details": details}))


if __name__ == "__main__":
    main()
