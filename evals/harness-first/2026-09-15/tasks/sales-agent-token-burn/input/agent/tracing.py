"""Very small call logger. One JSON line per model call."""
import json
import os
import time

TRACE_PATH = os.environ.get("BK_TRACE_PATH", os.path.join(os.path.dirname(__file__), "..", "logs", "calls.jsonl"))


def log_call(conversation_id, lead_id, turn, resp):
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "conversation_id": conversation_id,
        "lead_id": lead_id,
        "turn": turn,
        "model": getattr(resp, "model", ""),
        "input_tokens": getattr(resp, "input_tokens", None),
        "output_tokens": getattr(resp, "output_tokens", None),
        "cost_usd": getattr(resp, "cost_usd", None),
        "tool_calls": [c.name for c in (getattr(resp, "tool_calls", None) or [])],
        "stop_reason": getattr(resp, "stop_reason", ""),
    }
    try:
        os.makedirs(os.path.dirname(TRACE_PATH), exist_ok=True)
        with open(TRACE_PATH, "a") as fh:
            fh.write(json.dumps(row) + "\n")
    except OSError:
        pass
