import json, subprocess, re, sys
P = json.load(open("passages.json"))
out = {}
try: out = json.load(open("prompts.json"))
except FileNotFoundError: pass
INSTR = """For each passage below (from a 1922 etiquette book), write the ONE short question or situation a reader might send that this passage would answer, as a modern reader would type it (one line, plain words, max 30 words). Rules: do not copy any phrase of 4+ words from the passage; do not describe the author's style; do not mention the book. Return ONLY a JSON object mapping id -> prompt, no prose, no code fence.

"""
todo = [p for p in P if p["id"] not in out]
for i in range(0, len(todo), 30):
    batch = todo[i:i+30]
    body = INSTR + "\n\n".join(f"[{p['id']}]\n{p['answer']}" for p in batch)
    r = subprocess.run(["claude","-p","--model","sonnet"], input=body, capture_output=True, text=True, timeout=600)
    txt = r.stdout.strip()
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        got = json.loads(m.group(0))
    except Exception as e:
        print("parse fail", i, txt[:300], r.stderr[-300:]); continue
    out.update({k:v for k,v in got.items() if any(p["id"]==k for p in batch)})
    json.dump(out, open("prompts.json","w"), indent=1)
    print(i, len(got), flush=True)
print("total", len(out), "of", len(P))
