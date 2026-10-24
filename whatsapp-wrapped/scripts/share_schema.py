"""The restricted share schema for hosted links. Standard library only.

Everything that may leave the device is defined in share/schema-v1.json: numbers with bounds, enums, allowlisted
emojis and month dates. There are no free-text fields, so a name, a phone number or a message cannot be expressed
in a valid payload. The viewer (share/static/viewer.js) validates against the same JSON file before it renders.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

SHARE_DIR = Path(__file__).resolve().parent.parent / "share"
SCHEMA = json.loads((SHARE_DIR / "schema-v1.json").read_text(encoding="utf-8"))
CONFIG = json.loads((SHARE_DIR / "config.json").read_text(encoding="utf-8"))
PRODUCT_NAME = CONFIG["product_name"]

MONTH = re.compile(r"^(20[0-9]{2}|2100)-(0[1-9]|1[0-2])$")
SKIN = re.compile("[\U0001F3FB-\U0001F3FF]")
_ALLOWED = {e.replace("\ufe0f", ""): e for e in SCHEMA["emoji"]}
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class SchemaError(ValueError):
    pass


def canonical_emoji(e: str) -> str | None:
    """Map an emoji to its allowlisted base form: no skin tone, first part of a ZWJ sequence. None if not allowed."""
    base = SKIN.sub("", e).split("\u200d")[0].replace("\ufe0f", "")
    return _ALLOWED.get(base)


def _is_int(x) -> bool:
    return type(x) is int  # bool is a subclass of int; reject it


def _check(kind: str, value, where: str) -> None:
    if kind.startswith("int:"):
        _, lo, hi = kind.split(":")
        if not _is_int(value) or not int(lo) <= value <= int(hi):
            raise SchemaError(f"{where}: expected an integer in [{lo}, {hi}]")
    elif kind == "month":
        if type(value) is not str or not MONTH.match(value):
            raise SchemaError(f"{where}: expected a month YYYY-MM")
    elif kind == "archetype":
        if value not in SCHEMA["archetypes"]:
            raise SchemaError(f"{where}: unknown archetype")
    elif kind == "hist24":
        if type(value) is not list or len(value) != 24 or not all(_is_int(v) and 0 <= v <= 100 for v in value):
            raise SchemaError(f"{where}: expected 24 integers in [0, 100]")
    elif kind.startswith("emojilist:"):
        _, lo, hi = kind.split(":")
        if type(value) is not list or not int(lo) <= len(value) <= int(hi):
            raise SchemaError(f"{where}: expected {lo} to {hi} emoji entries")
        seen = set()
        for i, item in enumerate(value):
            if (type(item) is not list or len(item) != 2 or item[0] not in SCHEMA["emoji"] or item[0] in seen
                    or not _is_int(item[1]) or not 1 <= item[1] <= 100000000):
                raise SchemaError(f"{where}[{i}]: expected [allowlisted emoji, count]")
            seen.add(item[0])
    else:  # pragma: no cover - schema file error
        raise SchemaError(f"{where}: unknown field type {kind}")


def _exact_keys(obj, keys: set, where: str) -> None:
    if type(obj) is not dict:
        raise SchemaError(f"{where}: expected an object")
    if set(obj) != keys:
        extra, missing = sorted(set(obj) - keys), sorted(keys - set(obj))
        raise SchemaError(f"{where}: unexpected keys {extra}, missing keys {missing}")


def validate(payload) -> dict:
    """Raise SchemaError unless payload is exactly a v1 share payload. Returns it unchanged."""
    _exact_keys(payload, {"v", "kind", "from", "to", "cards"}, "payload")
    if payload["v"] != SCHEMA["version"] or not _is_int(payload["v"]):
        raise SchemaError("payload.v: unsupported version")
    if payload["kind"] not in SCHEMA["kinds"]:
        raise SchemaError("payload.kind: unknown kind")
    for k in ("from", "to"):
        _check("month", payload[k], f"payload.{k}")
    if payload["from"] > payload["to"]:
        raise SchemaError("payload: from is after to")
    cards = payload["cards"]
    if type(cards) is not list or not SCHEMA["min_cards"] <= len(cards) <= SCHEMA["max_cards"]:
        raise SchemaError(f"payload.cards: expected {SCHEMA['min_cards']} to {SCHEMA['max_cards']} cards")
    order = SCHEMA["card_order"]
    last = -1
    for i, card in enumerate(cards):
        if type(card) is not dict or card.get("t") not in SCHEMA["cards"]:
            raise SchemaError(f"cards[{i}]: unknown card type")
        spec = SCHEMA["cards"][card["t"]]
        _exact_keys(card, set(spec) | {"t"}, f"cards[{i}]")
        pos = order.index(card["t"])
        if pos <= last:
            raise SchemaError(f"cards[{i}]: duplicate or out-of-order card")
        last = pos
        for field, kind in spec.items():
            _check(kind, card[field], f"cards[{i}].{field}")
    types = [c["t"] for c in cards]
    for req in SCHEMA["required_cards"]:
        if req not in types:
            raise SchemaError(f"payload.cards: missing required card {req}")
    if len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()) > SCHEMA["max_plain_bytes"]:
        raise SchemaError("payload: too large")
    return payload


def validate_teaser(teaser) -> dict:
    """The public OG teaser: one fixed template and its numbers, nothing else."""
    if type(teaser) is not dict or teaser.get("tpl") not in SCHEMA["teaser_templates"]:
        raise SchemaError("teaser: unknown template")
    spec = SCHEMA["teaser_templates"][teaser["tpl"]]
    _exact_keys(teaser, set(spec) | {"tpl"}, "teaser")
    for field, kind in spec.items():
        _check(kind, teaser[field], f"teaser.{field}")
    return teaser


# ---------------------------------------------------------------- build from local stats

def _hist(hours: list) -> list[int]:
    top = max(hours) or 1
    return [round(100 * h / top) for h in hours]


def _emojis(top_emojis) -> list:
    merged = Counter()
    for e, c in top_emojis:
        ce = canonical_emoji(e)
        if ce:
            merged[ce] += int(c)
    return [[e, c] for e, c in merged.most_common(5)]


def _busiest_month(day_counts: dict) -> tuple[str, int]:
    months = Counter()
    for d, c in day_counts.items():
        months[d[:7]] += c
    m, n = max(months.items(), key=lambda kv: (kv[1], kv[0]))
    return m, n


def peak_hour(hours: list) -> int:
    """The hour the peak card shows. The personality label must use this same value, so the two never disagree."""
    return max(range(24), key=lambda h: hours[h])


def archetype(n: int, hours: list, weekdays: list, voice: int, emojis: int, streak: int, per_day: float) -> str:
    """One label from group or self aggregates only. Time-of-day labels come from the peak hour on the peak card:
    night owls only when the peak is midnight to 4am, early birds only 5am to 8am, evening people 6pm to 11pm."""
    n = max(1, n)
    peak = peak_hour(hours)
    if peak <= 4:
        return "night_owls"
    if peak <= 8:
        return "early_birds"
    if peak >= 18:
        return "evening_people"
    if voice / n >= 0.08:
        return "voice_note_crew"
    if emojis / n >= 0.6:
        return "emoji_storm"
    if (weekdays[5] + weekdays[6]) / n >= 0.4:
        return "weekend_crew"
    if per_day >= 50:
        return "rapid_fire"
    if streak >= 30:
        return "streak_keepers"
    return "slow_burners"


def _silence(day_counts: dict):
    """Longest run of silent days between two active days, and the size of the comeback day."""
    from datetime import date as _d
    days = sorted(_d.fromisoformat(d) for d in day_counts)
    best = None
    for prev, nxt in zip(days, days[1:]):
        gap = (nxt - prev).days - 1
        if gap >= 2 and (best is None or gap > best[0]):
            best = (gap, nxt)
    if not best:
        return None
    return {"t": "silence", "days": best[0], "comeback_month": best[1].isoformat()[:7],
            "comeback_n": day_counts[best[1].isoformat()]}


def _assemble(kind, first, last, n, active_days, span_days, people, chats, hours, weekdays, streak_days,
              day_counts, top_emojis, voice, photos, stickers, emoji_total, words=0, busiest=None, reply_s=None,
              laughs=0) -> dict:
    """Cards in story order (schema card_order). Every optional card is left out when its number is missing."""
    from datetime import date as _d
    per_day = n / max(1, span_days)
    cards = [{"t": "messages", "n": n, "per_day": round(per_day), "active_days": active_days,
              "span_days": span_days, "people": people, "chats": chats}]
    if words >= 1:
        cards.append({"t": "words", "n": words})
    cards.append({"t": "peak", "hour": peak_hour(hours),
                  "weekday": max(range(7), key=lambda d: weekdays[d]), "hist": _hist(hours)})
    if busiest and busiest[1] >= 1:
        bd = _d.fromisoformat(busiest[0][:10])
        cards.append({"t": "busiest_day", "weekday": bd.weekday(), "month": bd.isoformat()[:7], "n": busiest[1]})
    if reply_s is not None and 1 <= round(reply_s) <= 21600:
        cards.append({"t": "reply", "median_s": max(1, round(reply_s))})
    if laughs >= 1:
        cards.append({"t": "laughs", "n": laughs})
    em = _emojis(top_emojis)
    if em:
        cards.append({"t": "emojis", "top": em})
    if voice + photos + stickers > 0:
        cards.append({"t": "media", "voice": voice, "photos": photos, "stickers": stickers})
    sil = _silence(day_counts) if day_counts else None
    if sil:
        cards.append(sil)
    if streak_days >= 1 and day_counts:
        bm, bn = _busiest_month(day_counts)
        cards.append({"t": "streak", "days": streak_days, "busiest_month": bm, "busiest_n": bn})
    cards.append({"t": "archetype", "id": archetype(n, hours, weekdays, voice, emoji_total, streak_days, per_day)})
    payload = {"v": 1, "kind": kind, "from": first[:7], "to": last[:7], "cards": cards}
    return validate(payload)


def from_chat_stats(s: dict, kind: str) -> dict:
    """Chat edition. kind 'group' (all aggregates) or 'duo' (s must be computed from the creator's messages only)."""
    if kind not in ("group", "duo"):
        raise ValueError("kind must be group or duo")
    m = s["media"]
    emoji_total = sum(p["emojis"] for p in s["people"])
    return _assemble(kind, s["first"], s["last"], s["total_messages"], s["active_days"], s["span_days"],
                     s["people_count"] if kind == "group" else 0, 0, s["hours"], s["weekdays"], s["streak"]["days"],
                     s["day_counts"], s["top_emojis"], m["voice"], m["photo"] + m["video"] + m["media"],
                     m["sticker"] + m["gif"], emoji_total, words=s["total_words"],
                     busiest=(s["busiest_day"]["date"], s["busiest_day"]["messages"]),
                     reply_s=s.get("reply_median_s"), laughs=sum(p["laughs"] for p in s["people"]))


def from_personal_stats(s: dict) -> dict:
    """Personal edition: only what the creator sent, plus how many chats. No people, no groups by name."""
    ms = s["media_sent"]
    return _assemble("personal", s["first"], s["last"], s["sent"], s["active_days"], s["span_days"], 0, s["chats"],
                     s["hours"], s["weekdays"], s["streak"]["days"], s["day_counts"], s["top_emojis"],
                     s["voice_sent"], ms["photo"] + ms["video"] + ms["media"], ms["sticker"] + ms["gif"],
                     sum(c for _, c in s["top_emojis"]), words=s["words_sent"],
                     busiest=(s["busiest_day"]["date"], s["busiest_day"]["sent"]),
                     reply_s=s.get("my_reply_median_s"))


# ---------------------------------------------------------------- what the creator sees before publishing

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def month_label(m: str) -> str:
    y, mm = m.split("-")
    return f"{MONTHS[int(mm) - 1]} {y}"


def hour_label(h: int) -> str:
    return "midnight" if h == 0 else "noon" if h == 12 else f"{h % 12}{'am' if h < 12 else 'pm'}"


def describe(payload: dict) -> list[str]:
    """Every value a link recipient will see, as plain lines (built from the validated payload only)."""
    out = [f"kind: {payload['kind']}, {month_label(payload['from'])} to {month_label(payload['to'])}"]
    for c in payload["cards"]:
        t = c["t"]
        if t == "messages":
            extra = f", {c['people']} people" if c["people"] else f", {c['chats']} chats" if c["chats"] else ""
            out.append(f"messages: {c['n']:,} over {c['span_days']} days ({c['active_days']} active, about "
                       f"{c['per_day']} a day{extra})")
        elif t == "peak":
            out.append(f"peak: {hour_label(c['hour'])}, busiest weekday {WEEKDAY_NAMES[c['weekday']]}, 24-hour chart")
        elif t == "streak":
            out.append(f"streak: {c['days']} days in a row; busiest month {month_label(c['busiest_month'])} "
                       f"({c['busiest_n']:,} messages)")
        elif t == "emojis":
            out.append("emojis: " + "  ".join(f"{e} {n:,}" for e, n in c["top"]))
        elif t == "media":
            out.append(f"media: {c['voice']:,} voice notes, {c['photos']:,} photos, videos and other media, "
                       f"{c['stickers']:,} stickers and GIFs")
        elif t == "words":
            out.append(f"words: {c['n']:,} written")
        elif t == "busiest_day":
            out.append(f"busiest day: a {WEEKDAY_NAMES[c['weekday']]} in {month_label(c['month'])}, "
                       f"{c['n']:,} messages")
        elif t == "reply":
            out.append(f"reply speed: typical reply in {c['median_s']:,} seconds")
        elif t == "laughs":
            out.append(f"laughs: {c['n']:,} messages with a haha, lol or laughing emoji")
        elif t == "silence":
            out.append(f"longest silence: {c['days']} days; comeback in {month_label(c['comeback_month'])} "
                       f"with {c['comeback_n']:,} messages")
        elif t == "archetype":
            out.append(f"personality: {c['id'].replace('_', ' ')}")
    return out


def teaser_lines(teaser: dict) -> tuple[str, str]:
    """The two text lines of the public cover. Shared by the OG renderer, the page title and the terminal preview."""
    if teaser["tpl"] == "messages":
        return f"{teaser['n']:,} messages.", "Can your group beat this?"
    if teaser["tpl"] == "streak":
        return f"{teaser['days']:,} days in a row.", "Can your group beat this?"
    return "A chat, replayed.", "Tap to watch the story."
