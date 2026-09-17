"""FinBot: Slack finance Q&A agent. Run: python agent.py "what was revenue last month?" """
import json
import sqlite3
import sys
import os

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

# Safety limits
MAX_ITERATIONS = 5


def run_sql(query):
    """Execute SQL with READ-ONLY connection and logging."""
    # Open read-only connection to prevent accidental writes
    conn = sqlite3.connect(f'file:{config.DB_PATH}?mode=ro', uri=True)
    try:
        # Log the query (in production, send to tracing system)
        if os.environ.get('FINBOT_DEBUG'):
            print(f"[SQL] {query}", file=sys.stderr)
        
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        return {"columns": cols, "rows": rows[: config.MAX_ROWS]}
    except sqlite3.OperationalError as e:
        # Read-only violations get a clear error
        if "readonly" in str(e).lower() or "attempt to write" in str(e).lower():
            return {"error": "Database is read-only. FinBot can only query data, not modify it."}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


def answer(question):
    """Answer a question with safety limits and tracing."""
    from llm_client import chat  # internal gateway client, needs FINBOT_GATEWAY_TOKEN

    system = open("prompt.md").read()
    messages = [{"role": "user", "content": question}]
    
    iterations = 0
    while iterations < MAX_ITERATIONS:
        iterations += 1
        
        # Log iteration (in production, send to tracing system)
        if os.environ.get('FINBOT_DEBUG'):
            print(f"[Iteration {iterations}/{MAX_ITERATIONS}]", file=sys.stderr)
        
        resp = chat(model=config.MODEL, system=system, messages=messages, tools=TOOLS, temperature=config.TEMPERATURE)
        messages.append({"role": "assistant", "content": resp["content"]})
        
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        if not calls:
            # Model returned final answer
            return "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
        
        # Execute tool calls
        results = []
        for c in calls:
            out = run_sql(c["input"]["query"])
            results.append({"type": "tool_result", "tool_use_id": c["id"], "content": json.dumps(out, default=str)})
        
        messages.append({"role": "user", "content": results})
    
    # Hit iteration limit
    return f"I couldn't complete that query within {MAX_ITERATIONS} steps. Please try rephrasing your question or contact #data-eng if this persists."


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:])))
