"""FinBot: Slack finance Q&A agent (FIXED VERSION with loop safety + tracing)
Run: python agent_fixed.py "what was revenue last month?"
"""
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

MAX_ITERATIONS = 10  # Prevent infinite loops
TRACE_LOG = Path("logs/finbot_trace.jsonl")


def log_trace(conversation_id, event_type, data):
    """Log every interaction for audit trail"""
    TRACE_LOG.parent.mkdir(exist_ok=True)
    with open(TRACE_LOG, "a") as f:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_id": conversation_id,
            "event": event_type,
            **data
        }
        f.write(json.dumps(entry) + "\n")


def run_sql(query, conversation_id):
    """Execute SQL query with tracing"""
    start = time.time()
    conn = sqlite3.connect(config.DB_PATH)
    try:
        log_trace(conversation_id, "sql_query", {"query": query})
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.commit()
        result = {"columns": cols, "rows": rows[: config.MAX_ROWS]}
        log_trace(conversation_id, "sql_result", {
            "query": query,
            "row_count": len(rows),
            "duration_ms": int((time.time() - start) * 1000)
        })
        return result
    except Exception as e:
        error = str(e)
        log_trace(conversation_id, "sql_error", {"query": query, "error": error})
        return {"error": error}
    finally:
        conn.close()


def answer(question, conversation_id=None):
    """Answer a question with loop safety and tracing"""
    if conversation_id is None:
        conversation_id = f"cli_{int(time.time())}"
    
    log_trace(conversation_id, "question", {"question": question})
    
    from llm_client import chat
    
    # Use the fixed prompt
    system = open("output/prompt_fixed.md").read()
    messages = [{"role": "user", "content": question}]
    
    seen_queries = set()  # Detect retry loops
    
    for iteration in range(MAX_ITERATIONS):
        resp = chat(model=config.MODEL, system=system, messages=messages, tools=TOOLS, temperature=config.TEMPERATURE)
        messages.append({"role": "assistant", "content": resp["content"]})
        
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        if not calls:
            # Final answer
            answer_text = "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
            log_trace(conversation_id, "answer", {
                "answer": answer_text,
                "iterations": iteration + 1
            })
            return answer_text
        
        results = []
        for c in calls:
            query = c["input"]["query"]
            
            # Detect retry loop (same query multiple times = deterministic error)
            if query in seen_queries:
                log_trace(conversation_id, "error", {
                    "error": "retry_loop_detected",
                    "query": query
                })
                return "⚠️ I encountered an error and couldn't complete this request. Please rephrase your question or contact the data team."
            
            seen_queries.add(query)
            out = run_sql(query, conversation_id)
            results.append({"type": "tool_result", "tool_use_id": c["id"], "content": json.dumps(out, default=str)})
        
        messages.append({"role": "user", "content": results})
    
    # Hit max iterations
    log_trace(conversation_id, "error", {"error": "max_iterations_exceeded"})
    return f"⚠️ I couldn't answer this question within {MAX_ITERATIONS} steps. Please simplify your question or contact the data team."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_fixed.py 'your question here'")
        sys.exit(1)
    print(answer(" ".join(sys.argv[1:])))
