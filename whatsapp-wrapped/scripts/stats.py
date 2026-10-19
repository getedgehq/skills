"""Compute Wrapped stats from parsed messages. Standard library only."""
from __future__ import annotations

import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, timedelta

from parse import Chat, Message
from stopwords import STOPWORDS

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Emoji: pictographs with optional skin tone / variation selector, joined by ZWJ; or flag pairs.
_PICT = (
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U00002B00-\U00002BFF"
    "\U00002300-\U000023FF\U00003030\U0000303D\U00003297\U00003299\U000024C2"
    "\U00002934\U00002935\U00002763\U00002764]"
)
EMOJI = re.compile(
    "(?:[\U0001F1E6-\U0001F1FF]{2})|(?:" + _PICT + "[\U0001F3FB-\U0001F3FF\uFE0F]?(?:\u200D" + _PICT + "[\U0001F3FB-\U0001F3FF\uFE0F]?)*)"
)
URL = re.compile(r"https?://\S+|www\.\S+")
WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.U)
LAUGH = re.compile(r"\b(a?ha(ha)+h?|he(he)+|lol+|lmao+|xd+|jaja(ja)*|kkkk+|mdr+|ahah(ah)*)\b|😂|🤣", re.I)

MIN_WORD_LEN = 4



def _content_word(w: str) -> bool:
    """A word worth showing: long enough, not a stopword, not a laugh, not one letter repeated (hmmmm, nooo)."""
    return (len(w) >= MIN_WORD_LEN and w not in STOPWORDS and not LAUGH.fullmatch(w)
            and len(set(w.replace("'", ""))) > 2)


def distinctive_words(counts: Counter, convs: dict, n_convs: int, n: int) -> list[tuple[str, int]]:
    """Rank words by TF-IDF against the chat's own baseline, where each conversation is a document.

    A word that turns up in more than half of the conversations (filler the stopword lists missed) is dropped;
    a word this chat keeps coming back to in bursts scores high. Words must be used at least 3 times and, when
    there are enough conversations, in at least 2 of them, so one pasted list cannot fill the card.
    Returns (word, times used) pairs, best first.
    """
    min_df = 2 if n_convs >= 4 else 1
    scored = []
    for w, tf in counts.items():
        df = len(convs.get(w, ()))
        if tf < 3 or df < min_df:
            continue
        idf = math.log((1 + n_convs) / (1 + df))
        if n_convs >= 4 and idf <= 0 or n_convs >= 8 and df > n_convs / 2:
            continue  # in most conversations: part of how this chat talks, not what it talks about
        scored.append((tf * (idf if n_convs >= 4 else 1.0), tf, w))
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return [(w, tf) for _, tf, w in scored[:n]]


def _day(m: Message) -> date:
    return m.ts.date()


def compute(chat: Chat, gap_hours: float = 4.0, reply_window_hours: float = 6.0, top_n: int = 8) -> dict:
    msgs = sorted([m for m in chat.messages if m.kind != "call"], key=lambda m: m.ts)
    if not msgs:
        raise ValueError("No messages found. Is this a WhatsApp 'Export chat' file?")
    people = Counter(m.sender for m in msgs)
    order = [p for p, _ in people.most_common()]

    first, last = msgs[0].ts, msgs[-1].ts
    span_days = (last.date() - first.date()).days + 1
    days = Counter(_day(m) for m in msgs)

    # Longest streak of consecutive days with at least one message
    best, best_end, run, prev = 0, None, 0, None
    for d in sorted(days):
        run = run + 1 if prev and d - prev == timedelta(days=1) else 1
        if run > best:
            best, best_end = run, d
        prev = d
    streak = {"days": best, "start": (best_end - timedelta(days=best - 1)).isoformat() if best_end else None,
              "end": best_end.isoformat() if best_end else None}

    hours = [0] * 24
    weekdays = [0] * 7
    for m in msgs:
        hours[m.ts.hour] += 1
        weekdays[m.ts.weekday()] += 1
    busiest_day, busiest_count = days.most_common(1)[0]

    # Per person
    per = {p: defaultdict(int) for p in order}
    words_by = {p: 0 for p in order}
    emoji_by = {p: Counter() for p in order}
    word_counter = Counter()
    word_convs = defaultdict(set)  # word -> conversations it appears in
    seen_texts = set()
    emoji_counter = Counter()
    name_tokens = {w for p in order for w in WORD.findall(p.lower())}
    conv = 0
    gap = timedelta(hours=gap_hours)
    for i, m in enumerate(msgs):
        if i > 0 and m.ts - msgs[i - 1].ts >= gap:
            conv += 1
        s = per[m.sender]
        s["messages"] += 1
        s[m.kind] += 1
        if m.edited:
            s["edited"] += 1
        h = m.ts.hour
        if h < 5:
            s["night"] += 1
        elif h < 9:
            s["early"] += 1
        if m.ts.weekday() >= 5:
            s["weekend"] += 1
        if m.kind == "text":
            t = URL.sub(" ", m.text)
            if URL.search(m.text):
                s["links"] += 1
            es = EMOJI.findall(t)
            emoji_by[m.sender].update(es)
            emoji_counter.update(es)
            s["emojis"] += len(es)
            ws = WORD.findall(EMOJI.sub(" ", t).lower())
            s["words"] += len(ws)
            if LAUGH.search(t):
                s["laughs"] += 1
            if "?" in t:
                s["questions"] += 1
            # A long text (8+ words) pasted or forwarded again and again (a bot alert, a copied template) counts once.
            key = " ".join(ws)
            repeat = len(ws) >= 8 and key in seen_texts
            kept = [] if repeat else [w for w in ws if _content_word(w) and w not in name_tokens]
            seen_texts.add(key)
            word_counter.update(kept)
            for w in kept:
                word_convs[w].add(conv)
            words_by[m.sender] += len(ws)

    # Conversation starters, closers, reply speed
    starts = Counter()
    closes = Counter()
    reply_secs = defaultdict(list)
    win = timedelta(hours=reply_window_hours)
    for i, m in enumerate(msgs):
        if i == 0 or m.ts - msgs[i - 1].ts >= gap:
            starts[m.sender] += 1
            if i > 0:
                closes[msgs[i - 1].sender] += 1
        elif m.sender != msgs[i - 1].sender and m.ts - msgs[i - 1].ts <= win:
            reply_secs[m.sender].append((m.ts - msgs[i - 1].ts).total_seconds())
    closes[msgs[-1].sender] += 1
    conversations = sum(starts.values())

    replies = {}
    for p in order:
        r = reply_secs.get(p, [])
        if len(r) >= 3:
            replies[p] = {"median_s": statistics.median(r), "count": len(r)}
    fastest = sorted(replies.items(), key=lambda kv: kv[1]["median_s"])

    media_kinds = ["voice", "photo", "video", "sticker", "gif", "document", "media"]
    media_totals = {k: sum(per[p][k] for p in order) for k in media_kinds}

    person_rows = []
    for p in order:
        s = per[p]
        texts = s["text"] if "text" in s else 0
        person_rows.append({
            "name": p,
            "messages": s["messages"],
            "share": s["messages"] / len(msgs),
            "words": s["words"],
            "avg_words": (s["words"] / texts) if texts else 0.0,
            "emojis": s["emojis"],
            "top_emoji": emoji_by[p].most_common(1)[0][0] if emoji_by[p] else None,
            "voice": s["voice"], "photo": s["photo"], "video": s["video"], "sticker": s["sticker"],
            "gif": s["gif"], "document": s["document"], "media": s["media"],
            "deleted": s["deleted"], "edited": s["edited"], "links": s["links"],
            "laughs": s["laughs"], "questions": s["questions"],
            "night": s["night"], "early": s["early"], "weekend": s["weekend"],
            "starts": starts.get(p, 0), "closes": closes.get(p, 0),
            "reply_median_s": replies.get(p, {}).get("median_s"),
        })

    stats = {
        "title": chat.title,
        "platform": chat.platform,
        "date_order": chat.date_order,
        "is_group": len(order) > 2,
        "first": first.isoformat(), "last": last.isoformat(),
        "span_days": span_days, "active_days": len(days),
        "total_messages": len(msgs),
        "total_words": sum(r["words"] for r in person_rows),
        "people": person_rows,
        "people_count": len(order),
        "hours": hours, "weekdays": weekdays,
        "peak_hour": max(range(24), key=lambda h: hours[h]),
        "peak_weekday": WEEKDAYS[max(range(7), key=lambda d: weekdays[d])],
        "busiest_day": {"date": busiest_day.isoformat(), "messages": busiest_count},
        "day_counts": {d.isoformat(): c for d, c in sorted(days.items())},
        "per_day_avg": len(msgs) / span_days,
        "streak": streak,
        "top_emojis": emoji_counter.most_common(top_n),
        "top_words": distinctive_words(word_counter, word_convs, conv + 1, top_n + 4),
        "conversations": conversations,
        "starters": starts.most_common(),
        "fastest": [(p, v["median_s"]) for p, v in fastest],
        "media": media_totals,
        "deleted_total": sum(r["deleted"] for r in person_rows),
    }
    stats["awards"] = assign_awards(stats)
    return stats


def pl(n: int, word: str, plural: str | None = None) -> str:
    return f"{n:,} {word if n == 1 else (plural or word + 's')}"


def fmt_duration(sec: float) -> str:
    if sec < 60:
        return f"{int(round(sec))}\u00a0sec"
    if sec < 3600:
        return f"{int(round(sec / 60))}\u00a0min"
    h = sec / 3600
    return f"{h:.1f}\u00a0h".replace(".0\u00a0h", "\u00a0h")


# Awards: (key, title, metric fn -> value per person, line fn, min value to qualify)
def _rate(r, k):
    return r[k] / r["messages"] if r["messages"] else 0


AWARDS = [
    ("narrator", "The Main Character", lambda r, s: r["share"], lambda r, s: f"{pl(r['messages'], 'message')}, {round(r['share'] * 100)}% of the whole chat"),
    ("voice", "Voice Note Royalty", lambda r, s: r["voice"], lambda r, s: f"{pl(r['voice'], 'voice note')}. Podcast when?"),
    ("speed", "Speed Demon", lambda r, s: (1 / (1 + r["reply_median_s"])) if r["reply_median_s"] is not None else 0, lambda r, s: f"Typically replies in {fmt_duration(r['reply_median_s'])}" if r["reply_median_s"] is not None else ""),
    ("icebreaker", "The Icebreaker", lambda r, s: r["starts"], lambda r, s: f"Restarted the chat {pl(r['starts'], 'time')} after the silence"),
    ("night", "Night Owl", lambda r, s: _rate(r, "night") if r["night"] >= 3 else 0, lambda r, s: f"{pl(r['night'], 'message')} between midnight and 5am"),
    ("early", "Early Bird", lambda r, s: _rate(r, "early") if r["early"] >= 3 else 0, lambda r, s: f"{pl(r['early'], 'message')} before 9am"),
    ("novelist", "The Novelist", lambda r, s: r["avg_words"], lambda r, s: f"{r['avg_words']:.1f} words per message, the longest in the chat"),
    ("emoji", "Emoji Artist", lambda r, s: r["emojis"] / max(1, r["messages"]), lambda r, s: f"{pl(r['emojis'], 'emoji')} sent" + (f", mostly {r['top_emoji']}" if r["top_emoji"] else "")),
    ("paparazzi", "The Paparazzi", lambda r, s: r["photo"] + r["video"], lambda r, s: f"{pl(r['photo'] + r['video'], 'photo or video', 'photos and videos')} shared"),
    ("sticker", "Sticker Machine", lambda r, s: r["sticker"] + r["gif"], lambda r, s: f"{pl(r['sticker'] + r['gif'], 'sticker or GIF', 'stickers and GIFs')}"),
    ("laugh", "Laugh Track", lambda r, s: _rate(r, "laughs") if r["laughs"] >= 3 else 0, lambda r, s: f"Laughed out loud {pl(r['laughs'], 'time')}"),
    ("curious", "The Curious One", lambda r, s: _rate(r, "questions") if r["questions"] >= 3 else 0, lambda r, s: f"Asked {pl(r['questions'], 'question')}"),
    ("closer", "The Closer", lambda r, s: r["closes"], lambda r, s: f"Had the last word {pl(r['closes'], 'time')}"),
    ("weekend", "Weekend Warrior", lambda r, s: _rate(r, "weekend") if r["weekend"] >= 3 else 0, lambda r, s: f"{round(_rate(r, 'weekend') * 100)}% of messages on weekends"),
    ("eraser", "The Eraser", lambda r, s: r["deleted"], lambda r, s: f"Deleted {pl(r['deleted'], 'message')}. We saw nothing."),
    ("librarian", "The Librarian", lambda r, s: r["links"] + r["document"], lambda r, s: f"Shared {pl(r['links'] + r['document'], 'link or file', 'links and files')}"),
    ("minimalist", "The Minimalist", lambda r, s: (1 / r["avg_words"]) if r["avg_words"] else 0, lambda r, s: f"{r['avg_words']:.1f} words per message. Efficient."),
]


def assign_awards(stats: dict, max_people: int = 12) -> list[dict]:
    """One distinct award per person. Score = how far a person leads the others on that metric."""
    rows = stats["people"][:max_people]
    if not rows:
        return []
    candidates = []
    for key, title, metric, line in AWARDS:
        vals = [metric(r, stats) for r in rows]
        if max(vals) <= 0:
            continue
        mean = sum(vals) / len(vals)
        for r, v in zip(rows, vals):
            if v <= 0:
                continue
            rank = sorted(vals, reverse=True).index(v)
            lead = v / mean if mean else 0
            candidates.append((rank, -lead, key, title, r, line))
    candidates.sort(key=lambda c: (c[0], c[1]))
    used_people, used_awards, out = set(), set(), {}
    for rank, neg_lead, key, title, r, line in candidates:
        if r["name"] in used_people or key in used_awards:
            continue
        text = line(r, stats)
        if not text:
            continue
        out[r["name"]] = {"name": r["name"], "award": title, "key": key, "line": text}
        used_people.add(r["name"])
        used_awards.add(key)
    # Anyone left without a unique award gets a friendly fallback
    for r in rows:
        if r["name"] not in out:
            out[r["name"]] = {"name": r["name"], "award": "The Loyal Lurker", "key": "lurker",
                              "line": f"{pl(r['messages'], 'message')}. Quality over quantity."}
    return [out[r["name"]] for r in rows]
