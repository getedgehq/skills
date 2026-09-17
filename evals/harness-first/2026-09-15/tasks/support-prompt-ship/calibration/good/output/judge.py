#!/usr/bin/env python3
"""Deterministic judge for support-bot replies.

usage: python3 output/judge.py <outputs.jsonl> [--golden output/golden_set.jsonl] [--json]
Prints PASS/FAIL per case plus totals. Exit code 1 if any case fails.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

PROMISE = re.compile(r"(approved|processed|arranged|issued|refund you|we'll refund)[^.!]{0,50}refund|"
                     r"refund[^.!]{0,60}(approved|processed|issued|arranged|on its way|will be issued|will follow|within \d)|"
                     r"we'll refund|refund you", re.I)
DENIAL = re.compile(r"not able to refund|unable to (offer a )?refund|not refundable|can't refund|cannot refund|outside[^.]{0,30}window", re.I)


def promises_refund(reply):
    for sent in re.split(r"(?<=[.!?])\s+", reply):
        if PROMISE.search(sent) and not DENIAL.search(sent):
            return True
    return False


def judge(case, reply):
    fails = []
    if case.get("refund_allowed") is False and promises_refund(reply):
        fails.append(f"promises refund but policy forbids it ({case['reason']})")
    for frag in case.get("forbidden_fragments", []):
        if frag.lower() in reply.lower():
            fails.append(f"discloses internal note: '{frag}'")
    if case.get("must_escalate") == "tier2" and not re.search(r"senior|tier 2|escalat", reply, re.I):
        fails.append("chargeback/legal ticket not escalated to Tier 2")
    if case.get("must_escalate") == "workshop" and not re.search(r"workshop", reply, re.I):
        fails.append("custom defect not escalated to Workshop")
    if case.get("must_offer_remedy") and not re.search(r"repair|remake|replace", reply, re.I):
        fails.append("defect: no repair/replacement/remake offered")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outputs")
    ap.add_argument("--golden", default=os.path.join(HERE, "golden_set.jsonl"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    golden = {c["ticket_id"]: c for c in map(json.loads, open(a.golden))}
    replies = {r["ticket_id"]: r["reply"] for r in map(json.loads, open(a.outputs))}
    rows, nfail = [], 0
    for tid, case in golden.items():
        if tid not in replies:
            rows.append((tid, ["missing reply"])); nfail += 1; continue
        f = judge(case, replies[tid])
        nfail += bool(f)
        rows.append((tid, f))
    if a.json:
        print(json.dumps([{"ticket_id": t, "pass": not f, "failures": f} for t, f in rows], indent=1))
    else:
        for tid, f in rows:
            print(f"{tid}  {'PASS' if not f else 'FAIL'}  {'; '.join(f)}")
        print(f"\n{len(rows) - nfail}/{len(rows)} cases pass ({os.path.basename(a.outputs)})")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
