"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call


MAX_TURNS = 10
MAX_COST_PER_CONVERSATION = 0.50


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None):
    llm = llm or llm_mod.Client.from_config()
    tools = tools or tools_mod.Toolbox()
    messages = [{
        "role": "user",
        "content": f"Work lead {lead_id}: qualify it, update the CRM, and send the first-touch email if it's a fit.\n\n"
                   f"Call crm_get_account once to load the account data, then proceed with your analysis.",
    }]

    turn = 0
    total_cost = 0.0
    while True:
        turn += 1
        
        # Cost governance
        if turn > MAX_TURNS:
            return f"Lead {lead_id}: Max iterations ({MAX_TURNS}) reached. Escalating to human review."
        
        resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        total_cost += resp.cost_usd
        log_call(conversation_id, lead_id, turn, resp)
        
        if total_cost > MAX_COST_PER_CONVERSATION:
            return f"Lead {lead_id}: Cost limit (${MAX_COST_PER_CONVERSATION}) exceeded. Escalating to human review."
        
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
