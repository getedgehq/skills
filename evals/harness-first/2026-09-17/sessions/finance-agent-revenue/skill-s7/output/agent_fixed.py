"""FinBot: Slack finance Q&A agent. Run: python agent.py "what was revenue last month?" """
import json
import sqlite3
import sys
import time
from datetime import datetime

import config

TOOLS = [{
    "name": "run_sql",
    "description": "Run a read-only SQL query against the finance warehouse and return the rows.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}]


def run_sql(query):
    """Execute SQL with read-only connection and error handling."""
    # Force read-only mode
    conn = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
    try:
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        return {"columns": cols, "rows": rows[: config.MAX_ROWS]}
    except sqlite3.OperationalError as e:
        # Database locked, file not found - don't retry
        return {"error": f"Database error: {str(e)}"}
    except sqlite3.Error as e:
        # Syntax errors, schema errors - don't retry
        return {"error": f"SQL error: {str(e)}"}
    finally:
        conn.close()


def answer(question, conversation_id=None):
    """Answer a question with tracing and iteration limits."""
    from llm_client import chat  # internal gateway client, needs FINBOT_GATEWAY_TOKEN

    # Tracing setup
    conversation_id = conversation_id or f"cli_{int(time.time())}"
    start_time = time.time()
    iterations = 0
    total_tokens = 0
    queries_run = []

    system = open("prompt.md").read()
    messages = [{"role": "user", "content": question}]
    
    try:
        while iterations < config.MAX_ITERATIONS:
            iterations += 1
            
            resp = chat(
                model=config.MODEL, 
                system=system, 
                messages=messages, 
                tools=TOOLS, 
                temperature=config.TEMPERATURE
            )
            
            # Track tokens if available
            if "usage" in resp:
                total_tokens += resp["usage"].get("total_tokens", 0)
            
            messages.append({"role": "assistant", "content": resp["content"]})
            calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
            
            if not calls:
                answer_text = "".join(b.get("text", "") for b in resp["content"] if b.get("type") == "text")
                
                # Log successful completion
                log_trace(
                    conversation_id=conversation_id,
                    question=question,
                    answer=answer_text,
                    iterations=iterations,
                    queries=queries_run,
                    tokens=total_tokens,
                    latency_sec=time.time() - start_time,
                    error=None
                )
                
                return answer_text
            
            results = []
            for c in calls:
                query = c["input"]["query"]
                queries_run.append(query)
                
                out = run_sql(query)
                
                # Log query execution
                log_query(
                    conversation_id=conversation_id,
                    iteration=iterations,
                    query=query,
                    result=out,
                    error=out.get("error")
                )
                
                results.append({
                    "type": "tool_result", 
                    "tool_use_id": c["id"], 
                    "content": json.dumps(out, default=str)
                })
            
            messages.append({"role": "user", "content": results})
        
        # Hit max iterations
        error_msg = f"Stopped after {config.MAX_ITERATIONS} iterations. Please rephrase your question or contact support."
        log_trace(
            conversation_id=conversation_id,
            question=question,
            answer=None,
            iterations=iterations,
            queries=queries_run,
            tokens=total_tokens,
            latency_sec=time.time() - start_time,
            error="MAX_ITERATIONS_EXCEEDED"
        )
        return error_msg
        
    except Exception as e:
        # Unexpected error
        log_trace(
            conversation_id=conversation_id,
            question=question,
            answer=None,
            iterations=iterations,
            queries=queries_run,
            tokens=total_tokens,
            latency_sec=time.time() - start_time,
            error=str(e)
        )
        return f"Error: {str(e)}"


def log_query(conversation_id, iteration, query, result, error):
    """Log individual query execution."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "conversation_id": conversation_id,
        "iteration": iteration,
        "query": query,
        "row_count": len(result.get("rows", [])) if not error else 0,
        "error": error
    }
    
    # Append to log file
    with open("logs/queries.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def log_trace(conversation_id, question, answer, iterations, queries, tokens, latency_sec, error):
    """Log full conversation trace."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "conversation_id": conversation_id,
        "question": question,
        "answer": answer,
        "iterations": iterations,
        "queries_run": queries,
        "tokens": tokens,
        "latency_sec": round(latency_sec, 2),
        "error": error
    }
    
    # Append to log file
    with open("logs/conversations.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    import os
    os.makedirs("logs", exist_ok=True)
    print(answer(" ".join(sys.argv[1:])))
