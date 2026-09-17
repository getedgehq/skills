"""FinBot v2: Slack finance Q&A agent with safety rails and tracing.
Run: python agent-v2.py "what was revenue last month?"
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
    "description": "Run a READ-ONLY SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]

# Safety limits
MAX_ITERATIONS = 10
MAX_ROWS = 200

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def run_sql(query):
    """Execute a read-only SQL query against the warehouse."""
    # Check for obviously dangerous operations
    query_upper = query.upper()
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'REPLACE']
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return {"error": f"Forbidden: {keyword} operations are not allowed. This is a read-only tool."}
    
    try:
        # Open connection with read-only mode
        conn = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        
        result = {"columns": cols, "rows": rows[:MAX_ROWS]}
        
        # Log the query
        log_query(query, result)
        
        return result
    except sqlite3.OperationalError as e:
        # Don't retry on deterministic errors (syntax, missing table, etc.)
        return {"error": f"SQL error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def log_query(query, result):
    """Log SQL query and result to file."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "row_count": len(result.get("rows", [])) if "rows" in result else 0,
        "has_error": "error" in result
    }
    
    log_file = LOG_DIR / "queries.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_conversation(conversation_id, question, answer, iterations, error=None):
    """Log full conversation for audit trail."""
    log_entry = {
        "conversation_id": conversation_id,
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "iterations": iterations,
        "model": config.MODEL,
        "error": error
    }
    
    log_file = LOG_DIR / "conversations.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def answer(question):
    """Answer a question using the LLM + SQL tools."""
    from llm_client import chat
    
    conversation_id = f"{int(time.time()*1000)}"
    system = open("prompt.md").read()
    messages = [{"role": "user", "content": question}]
    iterations = 0
    
    try:
        while iterations < MAX_ITERATIONS:
            iterations += 1
            
            resp = chat(
                model=config.MODEL,
                system=system,
                messages=messages,
                tools=TOOLS,
                temperature=config.TEMPERATURE
            )
            
            messages.append({"role": "assistant", "content": resp["content"]})
            
            # Check for tool calls
            calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
            if not calls:
                # No more tool calls, we have a final answer
                answer_text = "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
                log_conversation(conversation_id, question, answer_text, iterations)
                return answer_text
            
            # Execute tool calls
            results = []
            for c in calls:
                out = run_sql(c["input"]["query"])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": c["id"],
                    "content": json.dumps(out, default=str)
                })
            
            messages.append({"role": "user", "content": results})
        
        # Hit max iterations
        error_msg = f"Sorry, I couldn't answer that after {MAX_ITERATIONS} attempts. Please try rephrasing your question or contact the data team."
        log_conversation(conversation_id, question, error_msg, iterations, error="max_iterations_exceeded")
        return error_msg
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log_conversation(conversation_id, question, error_msg, iterations, error=str(e))
        return error_msg


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent-v2.py 'your question here'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(answer(question))
