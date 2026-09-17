"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call


MAX_ITERATIONS = 8  # 2x normal workflow (typical: 3-4 turns)
MAX_COST_PER_RUN = 0.50  # $0.50 per lead


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, 
                     max_iterations=MAX_ITERATIONS, max_cost_usd=MAX_COST_PER_RUN):
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
            error_msg = f"[ERROR] Cost cap (${max_cost_usd:.2f}) exceeded for lead {lead_id}. Total spent: ${total_cost:.3f}. Manual review needed."
            return error_msg
        
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
    
    # Graceful degradation if max iterations reached
    error_msg = f"[ERROR] Max iterations ({max_iterations}) reached for lead {lead_id}. Total cost: ${total_cost:.3f}. Manual review needed."
    return error_msg
