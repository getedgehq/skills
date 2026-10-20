"""Personal edition: one Wrapped of YOUR WhatsApp across all your chats. Standard library only.

Two sources, both chosen by the user and both read on this device:
- the WhatsApp Desktop database on a Mac (ChatStorage.sqlite). It is copied to a private temp folder first and
  only the copy is opened, so the original is never touched.
- a folder of "Export chat" files (.txt or .zip), one per chat. Your own name is taken from --me, or found as the
  one sender who appears in every chat.

Broadcast lists, status updates, channels and your notes-to-self chat are left out. Groups you never or barely
write in (fewer than 5 messages, or under 2% of a group with 50+ members) are left out too, so a big community
group you only read does not drown your own chats.
"""
from __future__ import annotations

import os
import re
import shutil
import sqlite3
import statistics
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from parse import parse_file
from stats import EMAIL, EMOJI, URL, WORD, _content_word, case_update, distinctive_words, fmt_duration, proper_nouns
import stopwords as SW

APPLE_EPOCH = 978307200  # 2001-01-01 in Unix seconds; Core Data timestamps count from here
GAP = timedelta(hours=4)
REPLY_WIN = timedelta(hours=6)
MIN_GROUP_SENT, BIG_GROUP, BIG_GROUP_SHARE = 5, 50, 0.02

# WhatsApp Desktop (Mac) ZMESSAGETYPE values that are real messages. The rest are system notices, calls, reactions.
DB_KINDS = {0: "text", 1: "photo", 2: "video", 3: "voice", 4: "contact", 5: "location", 7: "text", 8: "document",
            11: "gif", 14: "deleted", 15: "sticker", 46: "poll"}
DB_SESSION_DIRECT, DB_SESSION_GROUP, DB_SESSION_COMMUNITY = 0, 1, 4  # 2 broadcast, 3 status, 5 channel: skipped

# Zones the auto mode chooses between, one per region, for estimating where you were each week.
TZ_CANDIDATES = ["America/Los_Angeles", "America/Denver", "America/Chicago", "America/New_York", "America/Sao_Paulo",
                 "Europe/London", "Europe/Berlin", "Europe/Athens", "Asia/Dubai", "Asia/Kolkata", "Asia/Bangkok",
                 "Asia/Shanghai", "Asia/Tokyo", "Australia/Sydney"]
MAC_DB_RELATIVE = "Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite"
NO_MAC_DB = """No WhatsApp Desktop database on this Mac. Two ways to get your data:
  1. Install WhatsApp from the Mac App Store, link it to your phone (WhatsApp > Settings > Linked devices), wait
     for the chats to sync, then run this again.
  2. Or export the chats you care about from your phone (chat > Export chat > Without media) into one folder and
     run: wrapped.py --personal <that folder>"""
NO_ACCESS = """macOS blocked access to the WhatsApp Desktop database. Give your terminal app Full Disk Access
(System Settings > Privacy & Security > Full Disk Access), restart it, then run this again."""


def mac_desktop_db() -> Path:
    """Where WhatsApp Desktop for Mac keeps its messages."""
    return Path.home() / MAC_DB_RELATIVE


INVISIBLE = re.compile(r"[‎‏‪-‮⁦-⁩﻿]")


@dataclass
class Rec:
    ts: datetime          # timezone-aware (UTC) from the database, naive local time from exports
    chat: str             # chat id
    chat_name: str
    group: bool
    size: int             # group members (database) or distinct senders (exports)
    person: str           # merge key: the other person for one-to-one chats, the chat id for groups
    me: bool
    kind: str
    text: str | None = None


# ---------- sources ----------

def load_desktop_db(path: str | Path) -> tuple[list[Rec], dict]:
    """Read a WhatsApp Desktop ChatStorage.sqlite. Copies it (with -wal and -shm) to a temp folder first."""
    src = Path(path)
    tmp = Path(tempfile.mkdtemp(prefix="wa-personal-"))
    os.chmod(tmp, 0o700)
    try:
        try:
            for suffix in ("", "-wal", "-shm"):
                f = Path(str(src) + suffix)
                if f.exists():
                    shutil.copy2(f, tmp / (src.name + suffix))
        except PermissionError as exc:
            raise PermissionError(NO_ACCESS) from exc
        con = sqlite3.connect(tmp / src.name)
        sessions, skipped = {}, Counter()
        for pk, stype, jid, name in con.execute("select Z_PK, ZSESSIONTYPE, ZCONTACTJID, ZPARTNERNAME from ZWACHATSESSION"):
            if stype not in (DB_SESSION_DIRECT, DB_SESSION_GROUP, DB_SESSION_COMMUNITY):
                skipped["broadcast, status or channel"] += 1
                continue
            clean = INVISIBLE.sub("", name or "").strip() or (jid or "unknown").split("@")[0]
            if stype == DB_SESSION_DIRECT and clean == "You":
                skipped["notes to self"] += 1
                continue
            sessions[pk] = (clean, stype != DB_SESSION_DIRECT)
        size = Counter(r[0] for r in con.execute("select ZCHATSESSION from ZWAGROUPMEMBER"))
        contact_names = {INVISIBLE.sub("", n) for (n,) in con.execute(
            "select ZCONTACTNAME from ZWAGROUPMEMBER where ZCONTACTNAME is not null")}
        recs = []
        q = (f"select ZCHATSESSION, ZISFROMME, ZMESSAGETYPE, ZMESSAGEDATE, ZTEXT from ZWAMESSAGE "
             f"where ZMESSAGETYPE in ({','.join(map(str, DB_KINDS))}) and ZMESSAGEDATE is not null")
        for sess, me, mtype, ts, text in con.execute(q):
            if sess not in sessions:
                continue
            name, group = sessions[sess]
            recs.append(Rec(ts=datetime.fromtimestamp(ts + APPLE_EPOCH, timezone.utc), chat=str(sess), chat_name=name,
                            group=group, size=size.get(sess, 0) if group else 2,
                            person=f"g:{sess}" if group else "p:" + name.lower(), me=bool(me), kind=DB_KINDS[mtype],
                            text=text if DB_KINDS[mtype] == "text" else None))
        con.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    recs.sort(key=lambda r: r.ts)
    return recs, {"source": "WhatsApp Desktop database", "skipped_chats": dict(skipped),
                  "name_tokens": {w for n in contact_names for w in WORD.findall(n.lower())}}


def load_exports(folder: str | Path, me: str | None = None, date_order: str | None = None) -> tuple[list[Rec], dict]:
    """Read every .txt / .zip export in a folder, one chat per file."""
    files = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in (".txt", ".zip"))
    chats = [c for c in (parse_file(f, date_order=date_order) for f in files) if c.messages]
    if not chats:
        raise ValueError(f"no WhatsApp exports with messages in {folder}")
    if me is None:
        in_chats = Counter(s for c in chats for s in {m.sender for m in c.messages})
        best = in_chats.most_common(2)
        if len(chats) < 2 or (len(best) > 1 and best[0][1] == best[1][1]):
            raise ValueError("could not tell which sender is you: pass --me \"Your Name\" as it appears in the exports")
        me = best[0][0]
    recs = []
    for i, c in enumerate(chats):
        senders = {m.sender for m in c.messages}
        if me not in senders:
            continue
        group = len(senders) > 2
        other = next((s for s in senders if s != me), c.title)
        for m in c.messages:
            if m.kind == "call":
                continue
            recs.append(Rec(ts=m.ts, chat=f"x{i}", chat_name=c.title if group else other, group=group, size=len(senders),
                            person=f"g:x{i}" if group else "p:" + other.lower(), me=m.sender == me, kind=m.kind,
                            text=m.text if m.kind == "text" else None))
    recs.sort(key=lambda r: r.ts)
    names = {s for c in chats for m in c.messages for s in [m.sender]}
    return recs, {"source": "exported chats", "me": me, "skipped_chats": {},
                  "name_tokens": {w for n in names for w in WORD.findall(n.lower())}}


# ---------- local time ----------

def localize(recs: list[Rec], tz: str = "auto") -> dict:
    """Turn aware timestamps into naive local time, in place. Exports are already local and stay as they are.

    tz="auto" estimates where you were, week by week: it finds the quietest six hours of your own messages
    (over that week and its neighbours), puts their middle at 4am, and picks the matching zone. It only moves to
    a new zone when the current one would put that quiet stretch more than two hours away from 4am.
    Returns the number of weeks spent in each zone.
    """
    aware = [r for r in recs if r.ts.tzinfo is not None]
    if not aware:
        return {}
    if tz != "auto":
        z = ZoneInfo(tz)
        for r in aware:
            r.ts = r.ts.astimezone(z).replace(tzinfo=None)
        return {tz: len({r.ts.isocalendar()[:2] for r in aware})}
    zones = {n: ZoneInfo(n) for n in TZ_CANDIDATES}
    by_week = defaultdict(list)
    for r in aware:
        if r.me:
            by_week[r.ts.isocalendar()[:2]].append(r.ts)
    weeks = sorted(by_week)

    def quiet_center(sample):
        """UTC moment (hours, 0-24) in the middle of the quietest stretch of the day."""
        hist = [0] * 24
        for t in sample:
            hist[t.astimezone(timezone.utc).hour] += 1
        win = [sum(hist[(h + i) % 24] for i in range(6)) for h in range(24)]
        low = min(win) + 0.01 * len(sample)
        quiet = [win[h] <= low for h in range(24)]
        if all(quiet):
            return None
        best_len, best_start, h0 = 0, 0, quiet.index(False)
        run = 0
        for k in range(1, 25):  # longest circular run of quiet window starts
            h = (h0 + k) % 24
            run = run + 1 if quiet[h] else 0
            if run > best_len:
                best_len, best_start = run, (h - run + 1) % 24
        return (best_start + (best_len - 1) / 2 + 3) % 24

    def miss(z, center, when):
        """How far (hours) the quiet centre sits from 4am local in zone z."""
        off = when.astimezone(zones[z]).utcoffset().total_seconds() / 3600
        d = abs((center + off) % 24 - 4)
        return min(d, 24 - d)
    pick, cur = {}, None
    for i, w in enumerate(weeks):
        sample = [t for ww in weeks[max(0, i - 1):i + 2] for t in by_week[ww]]
        center = quiet_center(sample) if len(sample) >= 40 else None
        if center is not None:
            when = by_week[w][0]
            if cur is None or miss(cur, center, when) > 2:
                cur = min(TZ_CANDIDATES, key=lambda z: (miss(z, center, when), TZ_CANDIDATES.index(z)))
        pick[w] = cur
    fallback = next((z for z in pick.values() if z), "UTC")
    first_known = fallback
    for w in weeks:  # weeks before the first confident estimate take the first one
        if pick[w] is None:
            pick[w] = first_known
    for r in aware:
        z = pick.get(r.ts.isocalendar()[:2])
        if z is None:  # a week with only incoming messages: use the nearest earlier estimate
            earlier = [w for w in weeks if w <= r.ts.isocalendar()[:2]]
            z = pick[earlier[-1]] if earlier else fallback
        r.ts = r.ts.astimezone(ZoneInfo(z)).replace(tzinfo=None)
    return dict(Counter(pick.values()))


# ---------- stats ----------

LANGS = {"EN": "English", "DE": "German", "IT": "Italian", "ES": "Spanish"}
_LANG_SETS = {k: set(getattr(SW, k).split()) for k in LANGS}
LANG_ONLY = {k: v - set().union(*(o for kk, o in _LANG_SETS.items() if kk != k)) for k, v in _LANG_SETS.items()}


def language_of(words: list[str]) -> str | None:
    """EN/DE/IT/ES by function words that belong to one language only. None when unclear."""
    sc = {k: sum(1 for w in words if w in v) for k, v in LANG_ONLY.items()}
    top = max(sc.values())
    if top < 1 or list(sc.values()).count(top) > 1:
        return None
    return max(sc, key=sc.get)


def compute_personal(recs: list[Rec], since: date | None = None, until: date | None = None,
                     name_tokens: set | None = None, owner: str = "") -> dict:
    """Stats for the personal edition. recs must already be in local time (see localize)."""
    first_seen = {}
    for r in recs:
        first_seen.setdefault(r.person, r.ts)
    history_start = recs[0].ts.date() if recs else None
    msgs = [r for r in recs if (since is None or r.ts.date() >= since) and (until is None or r.ts.date() <= until)]
    if not msgs:
        raise ValueError("no messages in this date range")
    g_tot, g_me, g_size = Counter(), Counter(), {}
    for r in msgs:
        if r.group:
            g_tot[r.chat] += 1
            g_me[r.chat] += r.me
            g_size[r.chat] = r.size
    excluded = {g for g in g_tot if g_me[g] < MIN_GROUP_SENT or (g_size[g] >= BIG_GROUP and g_me[g] / g_tot[g] < BIG_GROUP_SHARE)}
    msgs = [r for r in msgs if r.chat not in excluded]
    if not any(r.me for r in msgs):
        raise ValueError("none of the messages in this range are yours")
    sent = [r for r in msgs if r.me]
    recv = [r for r in msgs if not r.me]
    tokens = (name_tokens or set()) | set(WORD.findall(owner.lower())) | {w for r in msgs if not r.group for w in WORD.findall(r.chat_name.lower())}

    per, names, sizes = defaultdict(Counter), {}, {}
    for r in msgs:
        per[r.person]["total"] += 1
        per[r.person]["me"] += r.me
        names[r.person] = r.chat_name
        sizes[r.person] = r.size
    people = [k for k in per if k.startswith("p:")]
    groups = [k for k in per if k.startswith("g:")]

    hours, weekdays = [0] * 24, [0] * 7
    day_all, day_me = Counter(), Counter()
    for r in msgs:
        day_all[r.ts.date()] += 1
        if r.me:
            hours[r.ts.hour] += 1
            weekdays[r.ts.weekday()] += 1
            day_me[r.ts.date()] += 1
    bday, bcount = max(day_all.items(), key=lambda kv: (kv[1], kv[0]))
    best, best_end, run, prev = 0, None, 0, None
    for d in sorted(day_me):
        run = run + 1 if prev and d - prev == timedelta(days=1) else 1
        if run > best:
            best, best_end = run, d
        prev = d
    first_d, last_d = msgs[0].ts.date(), msgs[-1].ts.date()

    k_me, k_them = Counter(r.kind for r in sent), Counter(r.kind for r in recv)

    emo, words, convs, langs = Counter(), Counter(), defaultdict(set), Counter()
    case_mid, case_cap = Counter(), Counter()
    seen, n_words, n_texts, conv_id, last_in = set(), 0, 0, 0, {}
    for r in msgs:
        if r.ts - last_in.get(r.chat, datetime.min) >= GAP:
            conv_id += 1
        last_in[r.chat] = r.ts
        if not r.me or not r.text:
            continue
        txt = EMAIL.sub(" ", URL.sub(" ", r.text))
        case_update(txt, case_mid, case_cap)
        emo.update(EMOJI.findall(txt))
        ws = WORD.findall(EMOJI.sub(" ", txt).lower())
        n_words += len(ws)
        n_texts += 1
        key = " ".join(ws)
        repeat = len(ws) >= 8 and key in seen
        seen.add(key)
        if repeat:
            continue
        kept = [w for w in ws if _content_word(w) and w not in tokens]
        words.update(kept)
        for w in kept:
            convs[w].add(conv_id)
        if len(ws) >= 3:
            lang = language_of(ws)
            if lang:
                langs[lang] += 1

    seqs = defaultdict(list)
    for r in msgs:
        if not r.group:
            seqs[r.person].append((r.ts, r.me))
    they_reply, i_reply = defaultdict(list), defaultdict(list)
    i_start, they_start = Counter(), Counter()
    for k, seq in seqs.items():
        for i, (t, me) in enumerate(seq):
            if i == 0 or t - seq[i - 1][0] >= GAP:
                (i_start if me else they_start)[k] += 1
            elif me != seq[i - 1][1] and t - seq[i - 1][0] <= REPLY_WIN:
                (i_reply if me else they_reply)[k].append((t - seq[i - 1][0]).total_seconds())
    regular = {k for k in seqs if per[k]["total"] >= 150} or set(seqs)

    def ranked(d):
        # A median under 10 seconds is an auto-reply or a bot, not a person: left out of the rankings.
        meds = ((names[k], statistics.median(v)) for k, v in d.items() if k in regular and len(v) >= 20)
        return sorted((x for x in meds if x[1] >= 10), key=lambda x: x[1])[:5]
    my_replies = [x for v in i_reply.values() for x in v]
    starts = sum(i_start.values()) + sum(they_start.values())

    # "New" needs real history before the range: at least 30 days and 5% as many messages as the range itself.
    before = sum(1 for r in recs if since and r.ts.date() < since)
    new_people = []
    if since and history_start and (since - history_start).days >= 30 and before >= 0.05 * len(msgs):
        new_people = sorted((k for k in people if first_seen[k].date() >= since and per[k]["total"] >= 20),
                            key=lambda k: -per[k]["total"])

    def P(k):
        return {"name": names[k], "total": per[k]["total"], "me": per[k]["me"], "size": sizes[k]}
    s = {
        "first": first_d.isoformat(), "last": last_d.isoformat(), "history_start": history_start.isoformat(),
        "since": since.isoformat() if since else None,
        "span_days": (last_d - first_d).days + 1, "active_days": len(day_me),
        "sent": len(sent), "received": len(recv), "total": len(msgs),
        "chats": len(per), "people_chats": len(people), "group_chats": len(groups),
        "excluded_groups": len(excluded), "excluded_group_messages": sum(g_tot[g] for g in excluded),
        "top_people": [P(k) for k in sorted(people, key=lambda k: -per[k]["total"])[:5]],
        "top_groups": [P(k) for k in sorted(groups, key=lambda k: -per[k]["me"])[:5]],
        "hours": hours, "weekdays": weekdays, "peak_hour": max(range(24), key=lambda h: hours[h]),
        "peak_weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][max(range(7), key=lambda d: weekdays[d])],
        "busiest_day": {"date": bday.isoformat(), "messages": bcount, "sent": day_me[bday]},
        "day_counts": {d.isoformat(): c for d, c in sorted(day_me.items())},
        "streak": {"days": best, "start": (best_end - timedelta(days=best - 1)).isoformat(), "end": best_end.isoformat()},
        "voice_sent": k_me["voice"], "voice_received": k_them["voice"],
        "media_sent": {k: k_me[k] for k in ("photo", "video", "sticker", "gif", "document", "deleted", "media")},
        "words_sent": n_words, "avg_words": n_words / max(1, n_texts), "texts_sent": n_texts,
        "top_emojis": emo.most_common(8), "top_words": distinctive_words(words, convs, conv_id, 12),
        "proper_words": proper_nouns(case_mid, case_cap),
        "langs": dict(langs.most_common()), "lang_classified": sum(langs.values()),
        "fastest_to_me": ranked(they_reply), "i_reply_fastest": ranked(i_reply),
        "my_reply_median_s": statistics.median(my_replies) if my_replies else None,
        "i_start_top": [(names[k], c) for k, c in i_start.most_common(5)],
        "i_start_share": sum(i_start.values()) / max(1, starts), "conversations_1to1": starts,
        "new_people": len(new_people), "new_top": [P(k) for k in new_people[:5]],
        "night_share": sum(hours[0:5]) / len(sent), "group_share": sum(1 for r in sent if r.group) / len(sent),
    }
    s["archetype"] = archetype(s)
    return s


def archetype(s: dict) -> dict:
    """One headline title plus two runner-up titles, each scored against a typical-user baseline."""
    lv = sorted(s["langs"].values(), reverse=True)
    rep = s["my_reply_median_s"]
    c = [
        ("The Connector", s["people_chats"] / 150,
         f"{s['people_chats']:,} one-to-one chats and {s['group_chats']:,} groups. Everyone has your number."),
        ("The Instant Replier", (120 / rep) if rep else 0,
         f"Your typical reply lands in {fmt_duration(rep or 0)}. Nobody waits on you."),
        ("The Icebreaker", s["i_start_share"] / 0.55, f"You start {round(s['i_start_share'] * 100)}% of your one-to-one conversations."),
        ("Night Owl", s["night_share"] / 0.10, f"{round(s['night_share'] * 100)}% of your messages go out between midnight and 5am."),
        ("The Polyglot", (lv[1] / lv[0] / 0.2) if len(lv) > 1 else 0,
         f"You write in {sum(1 for v in lv if v >= 0.01 * sum(lv))} languages and switch chat by chat."),
        ("Voice Note Royalty", s["voice_sent"] / max(20, s["voice_received"]),
         f"{s['voice_sent']:,} voice notes sent, {s['voice_received']:,} received."),
        ("The Group Chat Captain", s["group_share"] / 0.4, f"{round(s['group_share'] * 100)}% of what you send goes to groups."),
        ("The Novelist", s["avg_words"] / 12, f"{s['avg_words']:.1f} words per message. You write letters."),
    ]
    c.sort(key=lambda x: -x[1])
    return {"title": c[0][0], "line": c[0][2], "runners": [[t, ln] for t, _, ln in c[1:3]]}
