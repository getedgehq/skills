"""Main agent loop for the Brightkiln outreach agent.

One conversation = one lead. The model qualifies the lead, writes the score
back to the CRM and sends the first-touch email.
"""
import json

from agent import llm as llm_mod
from agent import tools as tools_mod
from agent.prompts import SYSTEM_PROMPT
from agent.tracing import log_call


class CostLimitExceeded(Exception):
    """Raised when conversation exceeds cost cap."""
    pass


class TurnLimitExceeded(Exception):
    """Raised when conversation exceeds max turns."""
    pass


def run_conversation(lead_id, llm=None, tools=None, conversation_id=None, max_turns=10, max_cost_usd=2.0):
    """Run one conversation for a lead.
    
    Args:
        lead_id: CRM lead ID to process
        llm: LLM client (default: from config)
        tools: Toolbox instance (default: new instance)
        conversation_id: Optional conversation ID for tracing
        max_turns: Maximum turns before giving up (default: 10)
        max_cost_usd: Maximum cost per conversation before stopping (default: $2.00)
    
    Returns:
        Final model response text
        
    Raises:
        TurnLimitExceeded: Conversation exceeded max_turns
        CostLimitExceeded: Conversation exceeded max_cost_usd
    """
    llm = llm or llm_mod.Client.from_config()
    tools = tools or tools_mod.Toolbox()
    messages = [{
        "role": "user",
        "content": f"Work lead {lead_id}: qualify it, update the CRM, and send the first-touch email if it's a fit.",
    }]

    turn = 0
    total_cost = 0.0
    
    while True:
        turn += 1
        
        # Check limits before making another call
        if turn > max_turns:
            raise TurnLimitExceeded(
                f"Conversation exceeded {max_turns} turns. "
                f"Last message: {messages[-1]['content'][:200] if messages else 'none'}"
            )
        
        resp = llm.complete(system=SYSTEM_PROMPT, messages=messages, tools=tools.schemas())
        log_call(conversation_id, lead_id, turn, resp)
        
        total_cost += resp.cost_usd
        if total_cost > max_cost_usd:
            raise CostLimitExceeded(
                f"Conversation cost ${total_cost:.4f} exceeded limit of ${max_cost_usd:.2f} after {turn} turns"
            )
        
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
