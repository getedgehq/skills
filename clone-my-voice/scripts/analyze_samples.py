#!/usr/bin/env python3
"""Print style aggregates from local UTF-8 samples without printing source text."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

FORMATS = {"dm", "message", "messages", "post", "posts", "email", "emails"}
STYLE_WORDS = {
    "actually", "also", "anyway", "basically", "could", "just", "maybe",
    "really", "still", "think", "want", "would", "yeah", "eig", "einfach",
    "gerade", "kurz", "vielleicht", "wir", "mal", "schon",
}
WORD = re.compile(r"[A-Za-zÀ-ÿ]+(?:'[A-Za-zÀ-ÿ]+)?")


def sample_paths(args):
    for arg in args:
        p = Path(arg).expanduser()
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            yield p
        elif p.is_dir():
            yield from (q for q in sorted(p.rglob("*")) if q.is_file() and not q.is_symlink() and q.suffix.lower() in {".txt", ".md"})


def label(path):
    for part in reversed(path.parts[:-1]):
        if part.lower() in FORMATS:
            return {"message": "dm", "messages": "dm", "posts": "post", "emails": "email"}.get(part.lower(), part.lower())
    return "unsorted"


def summarize(texts):
    lines = [line.strip() for text in texts for line in text.splitlines() if line.strip()]
    words = [word for line in lines for word in WORD.findall(line)]
    sentences = [s.strip() for line in lines for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]
    word_lengths = [len(WORD.findall(s)) for s in sentences if WORD.search(s)]
    starts = [WORD.search(line).group() for line in lines if WORD.search(line)]
    punct = Counter(c for text in texts for c in text if c in ".,!?;:…—–-()")
    lower_starts = sum(w[0].islower() for w in starts)
    lead_words = Counter(w.lower() for w in starts if w.lower() in STYLE_WORDS)
    style_words = Counter(w.lower() for w in words if w.lower() in STYLE_WORDS)
    return {
        "sample_count": len(texts),
        "nonblank_lines": len(lines),
        "median_words_per_sentence": sorted(word_lengths)[len(word_lengths)//2] if word_lengths else 0,
        "mean_words_per_line": round(len(words)/len(lines), 1) if lines else 0,
        "lowercase_line_start_percent": round(100*lower_starts/len(starts)) if starts else 0,
        "blank_lines_per_sample": round(sum(t.splitlines().count("") for t in texts)/len(texts), 1) if texts else 0,
        "question_start_percent": round(100*sum(line.endswith("?") for line in lines)/len(lines)) if lines else 0,
        "digit_line_percent": round(100*sum(any(c.isdigit() for c in line) for line in lines)/len(lines)) if lines else 0,
        "punctuation_counts": dict(sorted(punct.items())),
        "style_word_counts": dict(sorted(style_words.items())),
        "opening_style_word_counts": dict(sorted(lead_words.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Local .txt/.md files or directories, grouped by format folders when possible")
    args = parser.parse_args()
    groups = defaultdict(list)
    for p in sample_paths(args.paths):
        groups[label(p)].append(p.read_text(encoding="utf-8"))
    if not groups:
        parser.error("no local .txt or .md samples found")
    print(json.dumps({kind: summarize(texts) for kind, texts in sorted(groups.items())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
