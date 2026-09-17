"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.

CHANGES:
- Added MAX_ITERATIONS cap (default 10)
- Added per-conversation cost cap (default $1.00)
- Graceful degradation when limits exceeded
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call

MAX_ITERATIONS = 10
MAX_COST_PER_CONVERSATION = 1.0  # USD


class ConversationLimitExceeded(Exception):
    """Raised when conversation exceeds iteration or cost limits."""
    pass


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, max_iterations=MAX_ITERATIONS, max_cost=MAX_COST_PER_CONVERSATION):
    llm = llm or llm_mod.Client.from_config()
    tools = tools or tools_mod.Toolbox()
    messages = [{
        "role": "user",
        "content": f"Work lead {lead_id}: qualify it, update the CRM, and send the first-touch email if it's a fit.",
    }]

    turn = 0
    total_cost = 0.0
    
    while turn < max_iterations:
        turn += 1
        
        try:
            resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        except Exception as e:
            log_call(conversation_id, lead_id, turn, None, error=str(e))
            raise
        
        log_call(conversation_id, lead_id, turn, resp)
        total_cost += resp.cost_usd
        
        # Check cost cap
        if total_cost > max_cost:
            error_msg = f"Conversation cost exceeded ${max_cost:.2f} limit (spent ${total_cost:.2f}). Stopping gracefully."
            log_call(conversation_id, lead_id, turn + 1, None, error=error_msg)
            return f"ERROR: {error_msg} Lead {lead_id} requires manual review."
        
        messages.append({"role": "assistant", "content": resp.content})

        if not resp.tool_calls:
            return resp.text

        for call in resp.tool_calls:
            try:
                result = tools.execute(call.name, call.arguments)
            except tools_mod.ToolError as e:
                # Return error to model, let it see the problem
                result = {"error": str(e), "status": e.status, "retryable": e.retryable}
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
    
    # Hit iteration limit
    error_msg = f"Conversation exceeded {max_iterations} iterations. Likely stuck in a retry loop."
    log_call(conversation_id, lead_id, turn + 1, None, error=error_msg)
    return f"ERROR: {error_msg} Lead {lead_id} requires manual review."
