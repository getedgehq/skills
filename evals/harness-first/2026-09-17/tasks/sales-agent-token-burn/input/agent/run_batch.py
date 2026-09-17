"""Nightly batch: work every new lead from the CRM queue.

    python -m agent.run_batch --queue inbound-sept
"""
import argparse
import json
import uuid

from agent.loop import run_conversation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--leads-file", help="json list of lead ids (for local runs)")
    args = ap.parse_args()
    leads = json.load(open(args.leads_file)) if args.leads_file else []
    for lead_id in leads:
        cid = "cv_" + uuid.uuid4().hex[:6]
        try:
            print(lead_id, run_conversation(lead_id, conversation_id=cid))
        except Exception as e:  # keep the batch going
            print(lead_id, "FAILED", type(e).__name__, e)


if __name__ == "__main__":
    main()
