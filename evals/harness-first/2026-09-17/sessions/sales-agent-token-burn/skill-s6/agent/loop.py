"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call


class MaxIterationsError(Exception):
    """Raised when conversation exceeds max allowed turns."""
    pass


class CostCapExceeded(Exception):
    """Raised when conversation exceeds cost limit."""
    pass


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, 
                     max_iterations=8, max_cost_usd=0.50):
    """Run the outreach agent conversation.
    
    Args:
        lead_id: CRM lead identifier
        llm: LLM client (uses config default if None)
        tools: Toolbox instance (creates new if None)
        conversation_id: unique conversation ID for tracing
        max_iterations: maximum turns before stopping (default 8)
        max_cost_usd: maximum cost in USD before stopping (default $0.50)
    
    Returns:
        Final text response from model
        
    Raises:
        MaxIterationsError: if max_iterations exceeded
        CostCapExceeded: if max_cost_usd exceeded
    """
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
        resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        log_call(conversation_id, lead_id, turn, resp)
        total_cost += resp.cost_usd
        
        # Check cost cap
        if total_cost > max_cost_usd:
            error_msg = f"Cost cap exceeded: ${total_cost:.4f} > ${max_cost_usd:.2f} after {turn} turns"
            log_call(conversation_id, lead_id, turn + 1, 
                    {"error": error_msg, "type": "cost_cap_exceeded"})
            raise CostCapExceeded(error_msg)
        
        messages.append({"role": "assistant", "content": resp.content})

        if not resp.tool_calls:
            return resp.text

        for call in resp.tool_calls:
            try:
                result = tools.execute(call.name, call.arguments)
            except tools_mod.ToolError as e:
                # let the model see the error and try again
                result = {"error": str(e), "status": e.status}
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
    
    # Max iterations reached
    error_msg = f"Max iterations ({max_iterations}) reached. Conversation incomplete."
    log_call(conversation_id, lead_id, turn + 1, 
            {"error": error_msg, "type": "max_iterations"})
    raise MaxIterationsError(error_msg)
