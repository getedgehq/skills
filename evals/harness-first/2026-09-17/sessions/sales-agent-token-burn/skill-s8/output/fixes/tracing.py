"""Tracing module for logging agent calls.

CHANGES:
- Added error parameter to log_call
- Handle None response object (for error cases)
"""
import json
import os
from datetime import datetime

TRACE_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


def log_call(conversation_id, lead_id, turn, response, error=None):
    """Log a single model call with metadata."""
    os.makedirs(TRACE_DIR, exist_ok=True)
    
    # Generate filename from current date
    filename = f"calls-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
    filepath = os.path.join(TRACE_DIR, filename)
    
    if error:
        # Log error case
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_id": conversation_id,
            "lead_id": lead_id,
            "turn": turn,
            "error": error,
            "input_tokens": None,
            "output_tokens": None,
            "cost_usd": None,
            "model": None,
            "stop_reason": "error"
        }
    elif response:
        # Log successful call
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_id": conversation_id,
            "lead_id": lead_id,
            "turn": turn,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "model": response.model,
            "stop_reason": response.stop_reason,
        }
    else:
        return  # Nothing to log
    
    with open(filepath, "a") as f:
        f.write(json.dumps(record) + "\n")
