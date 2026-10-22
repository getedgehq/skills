#!/usr/bin/env python3
"""caption_review.py BUNDLE_OR_CAPS.json --hook "..." --post "post caption" [--transcript T.json]

Second-model review of everything a viewer reads: on-screen captions, the hook and the
post caption. The model that wrote them should not be the one that approves them.

Builds one review prompt (captions with times, the transcript as ground truth, the
sensitivity rules, the caption rules) and:
  - with REEL_REVIEW_CMD set (e.g. "codex exec -", "claude -p"), pipes the prompt to that
    command and prints the answer. Exit 0 if the answer's first line starts with AGREED,
    2 otherwise (apply the fixes, run again, same model, until it says AGREED);
  - without it, writes the prompt to review_prompt.txt next to the captions for you to paste
    into a second model by hand. Exit 2.
"""
import argparse, json, shlex, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rmconf

ap = argparse.ArgumentParser()
ap.add_argument("target"); ap.add_argument("--hook", required=True); ap.add_argument("--post", required=True)
ap.add_argument("--transcript")
a = ap.parse_args()
t = Path(a.target)
caps_p = t / "caps.json" if t.is_dir() else t
tr_p = Path(a.transcript) if a.transcript else (t / "transcript.json" if t.is_dir() else None)
caps = json.load(open(caps_p))
said = ""
if tr_p and tr_p.exists():
    said = json.load(open(tr_p)).get("text", "")
rules = (HERE.parent / "references" / "sensitivity-rules.md").read_text()
banned = rmconf.get("REEL_BANNED_WORDS")

prompt = f"""You are reviewing the text of a short vertical video (Instagram Reel / TikTok / YouTube Short)
before it is scheduled. Be strict. Reply with AGREED on the first line if nothing must change.
Otherwise reply CHANGES on the first line, then one line per fix: the caption number (or HOOK / POST),
the problem, and the exact replacement text.

Check:
1. Captions say what was actually said (compare with the transcript). Fix speech-to-text errors;
   never put words in the speaker's mouth. Filler may go.
2. Each caption reads cleanly on its own, splits on a phrase boundary, no periods, no em or en dashes.
3. The hook is true to the clip, makes a stranger want to keep watching, and is at most two short lines.
4. The post caption sounds like the speaker, has no em or en dashes, no hashtag spam, no engagement bait.
5. Nothing breaks the sensitivity rules below.
{f"6. None of these words appear anywhere: {banned}" if banned else ""}

HOOK:
{a.hook}

POST CAPTION:
{a.post}

CAPTIONS (number, start-end seconds on the cut, text):
""" + "\n".join(f"{i}. {c['start']:.2f}-{c['end']:.2f} {c['text']}" + (f" / {c['en']}" if c.get("en") else "")
                for i, c in enumerate(caps)) + f"""

TRANSCRIPT OF THE FULL CLIP (ground truth, may contain parts that were cut):
{said[:6000]}

SENSITIVITY RULES:
{rules}
"""
cmd = rmconf.get("REEL_REVIEW_CMD")
if not cmd:
    out = caps_p.parent / "review_prompt.txt"; out.write_text(prompt)
    print(f"REEL_REVIEW_CMD not set. Paste {out} into a second model and loop until it says AGREED.")
    raise SystemExit(2)
r = subprocess.run(shlex.split(cmd), input=prompt, capture_output=True, text=True)
ans = (r.stdout or r.stderr).strip()
print(ans)
first = next((l for l in ans.splitlines() if l.strip()), "")
raise SystemExit(0 if first.strip().upper().startswith("AGREED") else 2)
