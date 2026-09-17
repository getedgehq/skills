"""FinBot: Slack finance Q&A agent (FIXED VERSION)

Changes from original:
- Added MAX_ITERATIONS to prevent infinite loops
- Added read-only database connection
- Removed unnecessary conn.commit() 
- Added basic logging
- Added per-run token tracking (placeholder for llm_client)

Run: python agent_fixed.py "what was revenue last month?"
"""
import json
import sqlite3
import sys
import logging
from datetime import datetime

import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('finbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOOLS = [{
    "name": "run_sql",
    "description": "Run a read-only SQL query against the finance warehouse and return the rows.",
    "input_schema": {
        "type": "object", 
        "properties": {
            "query": {"type": "string", "description": "SELECT query (read-only)"}
        }, 
        "required": ["query"]
    },
}]

MAX_ITERATIONS = 5  # Prevent infinite loops


def run_sql(query):
    """Execute read-only SQL query against warehouse."""
    # Read-only connection
    conn = sqlite3.connect(f'file:{config.DB_PATH}?mode=ro', uri=True)
    try:
        # Validate query is SELECT (basic safety check)
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            return {"error": "Only SELECT queries allowed (read-only mode)"}
        
        cur = conn.execute(query)
        rows = cur.fetchall() if cur.description else []
        cols = [d[0] for d in cur.description] if cur.description else []
        
        # Limit result size
        if len(rows) > config.MAX_ROWS:
            rows = rows[:config.MAX_ROWS]
            truncated = True
        else:
            truncated = False
        
        result = {
            "columns": cols, 
            "rows": rows,
            "row_count": len(rows)
        }
        if truncated:
            result["truncated"] = f"Limited to {config.MAX_ROWS} rows"
        
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


def answer(question, conversation_id=None):
    """Answer a finance question using the agent loop."""
    conversation_id = conversation_id or datetime.now().isoformat()
    
    logger.info(f"[{conversation_id}] Question: {question}")
    
    from llm_client import chat
    
    # Load system prompt with data dictionary
    system = open("prompt_fixed.md").read()
    
    messages = [{"role": "user", "content": question}]
    total_tokens = 0  # Track tokens (would need llm_client support)
    
    for iteration in range(MAX_ITERATIONS):
        logger.info(f"[{conversation_id}] Iteration {iteration + 1}/{MAX_ITERATIONS}")
        
        try:
            resp = chat(
                model=config.MODEL, 
                system=system, 
                messages=messages, 
                tools=TOOLS, 
                temperature=config.TEMPERATURE
            )
        except Exception as e:
            logger.error(f"[{conversation_id}] LLM call failed: {e}")
            return f"Error: Could not get response from model: {str(e)}"
        
        # Track tokens if available
        if 'usage' in resp:
            tokens = resp['usage'].get('total_tokens', 0)
            total_tokens += tokens
            logger.info(f"[{conversation_id}] Tokens this turn: {tokens}, Total: {total_tokens}")
        
        messages.append({"role": "assistant", "content": resp["content"]})
        
        # Check for tool calls
        calls = [b for b in resp["content"] if b.get("type") == "tool_use"]
        
        if not calls:
            # No more tool calls, extract final answer
            answer_text = "".join(
                b.get("text", "") 
                for b in resp["content"] 
                if b.get("type") == "text"
            )
            logger.info(f"[{conversation_id}] Final answer: {answer_text[:100]}...")
            logger.info(f"[{conversation_id}] Completed in {iteration + 1} iterations, {total_tokens} tokens")
            return answer_text
        
        # Execute tool calls
        results = []
        for c in calls:
            tool_name = c.get("name")
            logger.info(f"[{conversation_id}] Tool call: {tool_name}")
            
            if tool_name == "run_sql":
                query = c["input"]["query"]
                logger.info(f"[{conversation_id}] SQL: {query[:200]}")
                out = run_sql(query)
                
                if "error" in out:
                    logger.warning(f"[{conversation_id}] SQL error: {out['error']}")
                else:
                    logger.info(f"[{conversation_id}] SQL returned {out.get('row_count', 0)} rows")
            else:
                out = {"error": f"Unknown tool: {tool_name}"}
            
            results.append({
                "type": "tool_result", 
                "tool_use_id": c["id"], 
                "content": json.dumps(out, default=str)
            })
        
        messages.append({"role": "user", "content": results})
    
    # Hit max iterations
    logger.warning(f"[{conversation_id}] Hit max iterations ({MAX_ITERATIONS})")
    return f"Error: Could not answer question within {MAX_ITERATIONS} iterations. Please rephrase or simplify your question."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_fixed.py '<question>'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(answer(question))
