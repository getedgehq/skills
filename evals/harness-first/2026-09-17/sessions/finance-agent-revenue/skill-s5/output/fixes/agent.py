"""FinBot: Slack finance Q&A agent. Run: python agent.py "what was revenue last month?" """
import json
import sqlite3
import sys

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a read-only SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

MAX_TURNS = 10  # Prevent infinite loops


def run_sql(query):
    # Open in read-only mode to prevent accidental writes
    conn = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
    try:
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        return {"columns": cols, "rows": rows[: config.MAX_ROWS]}
    except Exception as e:
        # Return error to let model see it, but don't retry forever on deterministic errors
        return {"error": str(e)}
    finally:
        conn.close()


def answer(question):
    from llm_client import chat  # internal gateway client, needs FINBOT_GATEWAY_TOKEN

    system = open("prompt.md").read()
    messages = [{"role": "user", "content": question}]
    
    for turn in range(MAX_TURNS):
        resp = chat(model=config.MODEL, system=system, messages=messages, tools=TOOLS, temperature=config.TEMPERATURE)
        messages.append({"role": "assistant", "content": resp["content"]})
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        
        if not calls:
            # No more tool calls - return the text response
            return "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
        
        results = []
        for c in calls:
            out = run_sql(c["input"]["query"])
            results.append({"type": "tool_result", "tool_use_id": c["id"], "content": json.dumps(out, default=str)})
        
        messages.append({"role": "user", "content": results})
    
    # Hit max turns - graceful failure
    return "I couldn't answer that after 10 attempts. Please rephrase your question or contact #data for help."


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:])))
