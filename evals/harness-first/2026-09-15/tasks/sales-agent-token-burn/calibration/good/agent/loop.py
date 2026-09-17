"""Main agent loop for the Brightkiln outreach agent."""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call

MAX_TURNS = 8                 # a normal lead needs 3-4 turns
MAX_TOKENS_PER_CONVERSATION = 150_000
MAX_SAME_TOOL_ERRORS = 2


class BudgetExceeded(Exception):
    pass


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None):
    llm = llm or llm_mod.Client.from_config()
    tools = tools or tools_mod.Toolbox()
    messages = [{
        "role": "user",
        "content": f"Work lead {lead_id}: qualify it, update the CRM, and send the first-touch email if it's a fit.",
    }]
    spent = 0
    errors = {}
    for turn in range(1, MAX_TURNS + 1):
        resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        log_call(conversation_id, lead_id, turn, resp)
        spent += (getattr(resp, "input_tokens", 0) or 0) + (getattr(resp, "output_tokens", 0) or 0)
        if spent > MAX_TOKENS_PER_CONVERSATION:
            raise BudgetExceeded(f"{conversation_id}: {spent} tokens > {MAX_TOKENS_PER_CONVERSATION}")
        messages.append({"role": "assistant", "content": resp.content})
        if not resp.tool_calls:
            return resp.text
        for call in resp.tool_calls:
            try:
                result = tools.execute(call.name, call.arguments)
            except tools_mod.ToolError as e:
                key = (call.name, getattr(e, "status", None))
                errors[key] = errors.get(key, 0) + 1
                if not tools_mod.is_transient(e) or errors[key] >= MAX_SAME_TOOL_ERRORS:
                    return f"STOPPED {lead_id}: {call.name} failed with non-retryable error: {e}"
                result = {"error": str(e), "status": e.status}
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return f"STOPPED {lead_id}: hit MAX_TURNS={MAX_TURNS}"
