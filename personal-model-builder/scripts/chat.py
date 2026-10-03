#!/usr/bin/env python3
"""Talk to your model. Started by the "Talk to my model" launcher in the package folder.

Type a message (for example one you received) and press Enter to get a draft in your style.
  /better <your version>   "I would say it like this" - saved for the next update
  /forget <some words>     mark examples containing these words to be removed at the next update
  /quit                    leave
Drafts are for you to read and edit before you send anything.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from common import banned_phrases  # noqa: E402
from generate import Generator  # noqa: E402


def main():
    cfg = json.load(open(os.path.join(HERE, "package.json")))
    card = open(os.path.join(HERE, "style-card.md"), encoding="utf-8").read().strip()
    # system.md is the exact system prompt the check evaluated (style card + memory); never recomposed here
    system = open(os.path.join(HERE, "system.md"), encoding="utf-8").read().strip()
    banned = banned_phrases(card)
    feedback = os.path.join(cfg.get("work_dir", HERE), "feedback.jsonl")
    print("Loading your model (this can take a minute)...", flush=True)
    g = Generator(os.path.join(HERE, cfg["base"]), adapter=os.path.join(HERE, cfg["adapter"]),
                  backend=cfg["backend"], device=cfg.get("device", "cpu"))
    print("Ready. Type or paste a message and press Enter. /better, /forget, /quit\n")
    last_prompt, seed = None, 1
    for line in sys.stdin if not sys.stdin.isatty() else iter(lambda: input("> "), None):
        line = line.strip()
        if not line:
            continue
        if line == "/quit":
            break
        if line.startswith(("/better", "/forget")):
            kind, _, text = line.partition(" ")
            rec = {"kind": kind[1:], "text": text.strip(), "prompt": last_prompt,
                   "date": datetime.date.today().isoformat()}
            with open(feedback, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("Saved. It will be used next time you say 'update my model'.\n")
            continue
        last_prompt = line
        reply = g.reply(system, line, seed=seed)
        seed += 1
        if any(b.lower() in reply.lower() for b in banned):
            reply = g.reply(system, line, seed=seed + 1000)
            if any(b.lower() in reply.lower() for b in banned):
                print("(I could not write this one without a phrase you told me never to use, so I am not showing it. Try rephrasing.)\n")
                continue
        print(reply + "\n", flush=True)


if __name__ == "__main__":
    main()
