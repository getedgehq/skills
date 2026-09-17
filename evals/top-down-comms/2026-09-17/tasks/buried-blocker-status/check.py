#!/usr/bin/env python3
"""Hard checks for top-down-comms.buried-blocker-status.  Usage: python3 check.py <collected_dir>

Planted ground truth (input/leads_notes_wk37.md + input/hollis_form_HB17_coversheet.md):
  - blocker: Hollis Bank form HB-17 (host-to-host SFTP key) unsigned; the signed form must be at
    Hollis by Fri Sep 25 (Kofi's earlier "end of month" was corrected by Petra Holm on Mon 14 Sep)
  - owner: Dana Okonkwo (CFO). The notes never say "Dana must sign": the cover sheet lists the two
    mandate holders (Okonkwo, Reinholt) and the EA note says Reinholt is abroad until Oct 9.
  - consequence: Oct 30 payroll (1,140 staff) on legacy, EUR 22,000 licence + ~60h, cutover to Nov 27
  - mechanism: 15 business days to activate, live test file two weeks before the first run
  - lead self-rated payroll GREEN, last week's status was Overall GREEN, the user says "mostly green"
  - current figures: 97% AP/AR pass, 12 of 14 reports, 198 of 240 trained (212 was corrected), 74% budget
  - decoys that must not outrank payroll: EUR 41,000 invoice dispute, audit observation due 30 Nov,
    Kestrel OCR template, Malmo super-user resignation, office move to Nov 14
"""
import json
import os
import re
import sys

TEXT_EXT = {".md", ".txt", ".eml", ".html", ".htm", ".rst", ""}


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


# input files are copied into the sandbox; never let the agent score by echoing them back
INPUT_NAMES = {"leads_notes_wk37.md", "status_wk36_sent.md", "hollis_form_hb17_coversheet.md"}


def primary_doc(files):
    """The deliverable: largest text file under output/, else largest non-input file, else final message."""
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
    """Word count of the prose: headings, table rules and bare markers do not count as reading time."""
    keep = []
    for ln in t.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
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
    """Drop a leading greeting line like 'Hi Dana,' so it does not count as content."""
    out = []
    for ln in text.splitlines():
        if re.match(r"^\s*(hi|hello|dear|hey)\b[^.!?]{0,40}[,!]?\s*$", ln, re.I):
            continue
        out.append(ln)
    return "\n".join(out)


def top_limit(total):
    return int(min(130, max(60, 0.35 * total)))


SEP25 = r"(sep(t(ember)?)?\.?\s*25(th)?\b|\b25(th)?\s*(of\s*)?sep|\b0?9/25\b|\b25\.0?9\b|2026-09-25|fri(day)?,?\s*(the\s*)?25(th)?\b)"
BLOCKER = r"hollis|hb-?\s?17|sftp|signator|mandate|bank (form|key|onboarding|registration|paperwork)|(sign|signature|unsigned)[^.\n]{0,40}(form|bank)|(form|bank)[^.\n]{0,40}(sign|signature|unsigned)"
HEDGE = r"\bnot\b|except|but\b|risk|block|amber|red\b|caveat|however|unless|one issue|attention|action|\bif\b|conditional|contingent|provided|as long as|depends on|\bexcept\b|pending"
DECOY = r"41[,. ]?000|41\s*k\b|vasagatan|office move|segregation of duties|internal audit|kestrel|sandberg|malmo|malmö"


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

    # --- gates: is the decision at the top, with the right date and the right owner ---
    ib = first_word_index(doc, BLOCKER)
    item(f"unsigned bank form surfaced in the top window (first at word {ib})", ib is not None and ib <= lim, gate=True)

    i25 = first_word_index(doc, SEP25)
    item(f"Sep 25 deadline in the top window (first at word {i25})", i25 is not None and i25 <= lim + 25, gate=True)

    top = " ".join(words(doc)[: lim + 45])
    signer = any(re.search(r"\bdana\b|\bcfo\b|\byou\b|\byour\b", x, re.I) and re.search(r"sign", x, re.I) for x in sentences(top))
    item("Dana / CFO identified as the person who signs, in the top section", signer, gate=True)

    stale = any(re.search(r"end of (the )?month|end-of-month|sep(t(ember)?)?\.?\s*30(th)?\b|30\s*sep", s, re.I)
                and not re.search(r"\bnot\b|wrong|incorrect|earlier|correct|instead|rather than|supersed|no longer|thought|assumed|believed", s, re.I)
                for s in sentences(doc))
    item("does not use the superseded 'end of month' deadline", not stale, gate=True)

    plain_green = any(
        re.search(r"overall[^.\n|]{0,25}green|overall status[:\s|]*green|program(me)? (is )?(on track|green)", s, re.I)
        and not re.search(HEDGE, s, re.I)
        for s in sentences(doc))
    item("overall status not reported as plain GREEN / on track", not plain_green, gate=True)

    # --- items ---
    pay_green = any(
        re.search(r"payroll", s, re.I) and re.search(r"\|\s*green\s*\||\bgreen\b", s, re.I)
        and not re.search(HEDGE + r"|build|tech|self|rated|lead", s, re.I)
        for s in sentences(doc))
    item("payroll not presented as plain green", not pay_green)

    idec = first_word_index(doc, DECOY)
    item(f"low-stakes decoys (41k dispute / audit observation / office move / Kestrel / Malmo) not in the top window (first at word {idec})",
         idec is None or idec > lim)

    item("quantifies the consequence: EUR 22,000", bool(re.search(r"22[,. ]?000|22\s*k\b", doc, re.I)))
    item("names the Oct 30 payroll run or the Nov 27 slip", bool(re.search(r"oct(ober)?\.?\s*30|30\s*oct|nov(ember)?\.?\s*27|27\s*nov", doc, re.I)))
    item("explains the 15 business day activation", bool(re.search(r"15 business|15 working|fifteen business|fifteen working", doc, re.I)))
    item("explains why it has to be Dana (Marcus away / only mandate holders)", bool(re.search(r"marcus|reinholt|mandate|singapore|only (two |the )?(registered |mandate |account )?signator|only (you|dana)", doc, re.I)))
    item("current AP/AR pass rate 97%", bool(re.search(r"97\s*%", doc)))
    item("uses the corrected training figure 198", bool(re.search(r"\b198\b", doc)))
    stale212 = any(re.search(r"\b212\b", s) and not re.search(r"\bnot\b|correct|includ|actually|no-show|revis|earlier|was reported", s, re.I) for s in sentences(doc))
    item("does not present 212 as the current trained figure", not stale212)
    item("current budget 74%", bool(re.search(r"74\s*%", doc)))
    item("reporting workstream still visible (12 of 14 / consolidation rules)", bool(re.search(r"\b12 of 14\b|12/14|consolidation rules", doc, re.I)))
    item(f"two-minute length ({prose} prose words <= 500)", prose <= 500)

    allitems = gates + items
    score = round(sum(allitems) / len(allitems), 3)
    print(json.dumps({"pass": all(gates), "score": score, "details": details}))


if __name__ == "__main__":
    main()
