"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, max_turns=10):
    """Run a conversation for a single lead.
    
    Args:
        lead_id: Lead ID to process
        llm: LLM client (defaults to config)
        tools: Toolbox (defaults to standard tools)
        conversation_id: Optional conversation ID for logging
        max_turns: Maximum number of turns before aborting (safety limit)
    """
    llm = llm or llm_mod.Client.from_config()
    tools = tools or tools_mod.Toolbox()
    messages = [{
        "role": "user",
        "content": f"Work lead {lead_id}: qualify it, update the CRM, and send the first-touch email if it's a fit.",
    }]

    turn = 0
    while turn < max_turns:
        turn += 1
        resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        log_call(conversation_id, lead_id, turn, resp)
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
    
    # Hit max turns - abort to prevent runaway costs
    return f"Lead {lead_id}: aborted after {max_turns} turns (max limit reached)"
