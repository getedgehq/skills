"""FinBot: Slack finance Q&A agent - SAFETY PATCHED VERSION

CHANGES FROM ORIGINAL:
1. Added MAX_ITERATIONS cap to prevent infinite loops
2. Read-only database connection (no commits)
3. Per-conversation cost tracking (placeholder - needs gateway integration)
4. Better error handling (don't retry deterministic errors)

Run: python agent_safe.py "what was revenue last month?"
"""
import json
import sqlite3
import sys
from typing import Dict, List, Any

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

# SAFETY: Hard caps
MAX_ITERATIONS = 10  # Prevent infinite tool loops
MAX_COST_PER_QUERY = 1.0  # $1 per conversation (placeholder - integrate with gateway)


def run_sql(query: str) -> Dict[str, Any]:
    """Execute SQL query with read-only connection.
    
    SAFETY CHANGE: Open connection in read-only mode to prevent writes.
    """
    # Check for dangerous operations (defense in depth)
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
    query_upper = query.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return {
                "error": f"Permission denied: {keyword} operations are not allowed. This tool is read-only.",
                "query": query
            }
    
    # Open in read-only mode (URI format)
    # Note: SQLite URI mode requires sqlite3 version 3.4.0+
    try:
        conn = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        # Fallback: open normally but don't commit
        conn = sqlite3.connect(config.DB_PATH)
        conn.execute("PRAGMA query_only = ON;")  # Read-only pragma
    
    try:
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        # SAFETY: No conn.commit() - read-only
        return {"columns": cols, "rows": rows[:config.MAX_ROWS]}
    except sqlite3.OperationalError as e:
        # Deterministic error (syntax, table not found, etc.) - don't retry
        return {"error": f"SQL error: {str(e)}", "query": query, "retryable": False}
    except Exception as e:
        # Other errors might be transient
        return {"error": f"Error: {str(e)}", "query": query, "retryable": True}
    finally:
        conn.close()


def answer(question: str) -> str:
    """Answer a finance question using the LLM agent loop.
    
    SAFETY CHANGES:
    - Added MAX_ITERATIONS cap
    - Don't retry on non-retryable errors
    - Track cost per conversation (placeholder)
    """
    from llm_client import chat  # internal gateway client, needs FINBOT_GATEWAY_TOKEN

    system = open("prompt.md").read()
    messages = [{"role": "user", "content": question}]
    
    iterations = 0
    total_cost = 0.0  # Placeholder - would need gateway to return cost per call
    
    while iterations < MAX_ITERATIONS:
        iterations += 1
        
        # SAFETY: Check cost cap (placeholder - integrate with gateway)
        if total_cost >= MAX_COST_PER_QUERY:
            return (f"⚠️ Cost limit reached (${MAX_COST_PER_QUERY}). "
                    f"Partial answer after {iterations} steps: "
                    f"{messages[-1].get('content', 'No response yet')}")
        
        try:
            resp = chat(model=config.MODEL, system=system, messages=messages, 
                       tools=TOOLS, temperature=config.TEMPERATURE)
        except Exception as e:
            return f"❌ Error calling LLM: {str(e)}"
        
        # TODO: Extract cost from response and add to total_cost
        # total_cost += resp.get('usage', {}).get('cost', 0)
        
        messages.append({"role": "assistant", "content": resp["content"]})
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        
        if not calls:
            # No more tool calls, return the answer
            return "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
        
        # Execute tool calls
        results = []
        for c in calls:
            out = run_sql(c["input"]["query"])
            
            # SAFETY: Don't retry non-retryable errors
            if out.get("error") and not out.get("retryable", True):
                # Return error immediately instead of letting model retry
                error_msg = out.get("error", "Unknown error")
                return f"❌ Query failed: {error_msg}"
            
            results.append({
                "type": "tool_result", 
                "tool_use_id": c["id"], 
                "content": json.dumps(out, default=str)
            })
        
        messages.append({"role": "user", "content": results})
    
    # SAFETY: Hit max iterations
    return (f"⚠️ Maximum iterations ({MAX_ITERATIONS}) reached. "
            f"The query may be too complex or there may be an error. "
            f"Last response: {messages[-1].get('content', 'No response')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_safe.py 'your question here'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(answer(question))
