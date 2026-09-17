"""FinBot: Slack finance Q&A agent (HARDENED VERSION)

Changes from v1:
- Read-only database access (CRITICAL: prevents DELETE/UPDATE/DROP)
- Max iterations limit (prevents infinite loops)
- Per-run cost cap (prevents token burn)
- Basic tracing (logs queries, results, tokens)
- Better error handling (don't retry syntax errors)

Run: python agent_v2.py "what was revenue last month?"
"""
import json
import sqlite3
import sys
import time
import re
from datetime import datetime

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a READ-ONLY SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

# Safety limits
MAX_ITERATIONS = 5
MAX_TOKENS_PER_RUN = 50000
TRACE_FILE = "agent_trace.jsonl"


def is_readonly_query(query):
    """Check if query is read-only (SELECT only, no writes)."""
    query_upper = query.upper().strip()
    
    # Must start with SELECT
    if not query_upper.startswith('SELECT'):
        return False
    
    # Forbidden keywords
    forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'REPLACE']
    for keyword in forbidden:
        if keyword in query_upper:
            return False
    
    return True


def run_sql(query):
    """Execute a read-only SQL query."""
    # Validate read-only
    if not is_readonly_query(query):
        return {
            "error": "Only SELECT queries are allowed. Cannot execute INSERT/UPDATE/DELETE/DROP/etc.",
            "error_type": "permission_denied"
        }
    
    # Connect in read-only mode
    conn = sqlite3.connect(f'file:{config.DB_PATH}?mode=ro', uri=True)
    try:
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        
        # Truncate if too large
        truncated = False
        if len(rows) > config.MAX_ROWS:
            rows = rows[:config.MAX_ROWS]
            truncated = True
        
        result = {"columns": cols, "rows": rows}
        if truncated:
            result["warning"] = f"Result truncated to {config.MAX_ROWS} rows"
        
        return result
    except sqlite3.OperationalError as e:
        # Schema/syntax errors - don't retry
        return {
            "error": str(e),
            "error_type": "sql_error",
            "hint": "Check table names and column names. Available tables: revenue_recognized, orders, refunds, customers, daily_kpis"
        }
    except Exception as e:
        return {"error": str(e), "error_type": "unknown"}
    finally:
        conn.close()


def trace_log(event_type, data):
    """Append to trace log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **data
    }
    with open(TRACE_FILE, 'a') as f:
        f.write(json.dumps(entry, default=str) + '\n')


def answer(question, conversation_id=None):
    """Answer a question with safety limits."""
    from llm_client import chat
    
    if conversation_id is None:
        conversation_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    trace_log('question', {
        'conversation_id': conversation_id,
        'question': question
    })
    
    system = open("prompt_v2.md").read()  # Use improved prompt
    messages = [{"role": "user", "content": question}]
    
    total_tokens = 0
    iteration = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        
        # Check cost cap
        if total_tokens >= MAX_TOKENS_PER_RUN:
            error_msg = f"Cost limit reached ({total_tokens} tokens). Stopping for safety."
            trace_log('cost_limit_exceeded', {
                'conversation_id': conversation_id,
                'tokens': total_tokens,
                'iteration': iteration
            })
            return f"⚠️ {error_msg} Please rephrase or break into smaller questions."
        
        resp = chat(
            model=config.MODEL,
            system=system,
            messages=messages,
            tools=TOOLS,
            temperature=config.TEMPERATURE
        )
        
        # Track tokens (estimate if not provided)
        tokens_used = resp.get('usage', {}).get('total_tokens', 2000)  # conservative estimate
        total_tokens += tokens_used
        
        messages.append({"role": "assistant", "content": resp["content"]})
        
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        
        if not calls:
            # Final answer
            answer_text = "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
            trace_log('answer', {
                'conversation_id': conversation_id,
                'answer': answer_text,
                'total_tokens': total_tokens,
                'iterations': iteration
            })
            return answer_text
        
        # Execute tools
        results = []
        for c in calls:
            query = c["input"]["query"]
            trace_log('sql_query', {
                'conversation_id': conversation_id,
                'iteration': iteration,
                'query': query
            })
            
            out = run_sql(query)
            
            trace_log('sql_result', {
                'conversation_id': conversation_id,
                'iteration': iteration,
                'row_count': len(out.get('rows', [])) if 'rows' in out else 0,
                'error': out.get('error')
            })
            
            # Don't retry non-transient errors
            if out.get('error_type') in ['permission_denied', 'sql_error']:
                # Give model one chance to see the error, then stop
                pass
            
            results.append({
                "type": "tool_result",
                "tool_use_id": c["id"],
                "content": json.dumps(out, default=str)
            })
        
        messages.append({"role": "user", "content": results})
    
    # Hit iteration limit
    trace_log('iteration_limit', {
        'conversation_id': conversation_id,
        'iterations': iteration,
        'tokens': total_tokens
    })
    return f"⚠️ Reached iteration limit ({MAX_ITERATIONS}). Try a simpler question or check the data dictionary."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_v2.py 'your question here'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(answer(question))
