"""Cards and page for the personal edition, plus the share-safe name option for both editions.

Same visual system as render.py: same CSS, fonts, colours, sky image and "made with Edge" footer.
"""
from __future__ import annotations

import copy
import re
from collections import Counter
from datetime import date

import render as R
from personal import LANGS
from stats import fmt_duration

e = R.html.escape


# ---------- share-safe names ----------

def initials(name: str) -> str:
    """First and last initial: "Ana Maria Lima" -> "A.L.". Skips emoji and symbols."""
    parts = [p for p in re.split(r"\s+", name) if p and p[0].isalpha()]
    if not parts:
        return "?"
    pick = [parts[0]] + ([parts[-1]] if len(parts) > 1 else [])
    return ".".join(p[0].upper() for p in pick) + "."


def safe_label(rank: int, name: str) -> str:
    return f"Person #{rank} · {initials(name)}"


def share_safe_chat(s: dict) -> dict:
    """Single-chat edition: replace every name with "Person #n · A.L." (n = rank by messages) and the title."""
    s = copy.deepcopy(s)
    alias = {p["name"]: safe_label(i, p["name"]) for i, p in enumerate(s["people"], 1)}
    for p in s["people"]:
        p["name"] = alias[p["name"]]
    for a in s["awards"]:
        a["name"] = alias.get(a["name"], a["name"])
    s["fastest"] = [(alias.get(n, n), v) for n, v in s["fastest"]]
    s["starters"] = [(alias.get(n, n), c) for n, c in s["starters"]]
    s["title"] = "Our group chat" if s["is_group"] else "Our chat"
    return s


def namer(s: dict, safe: bool):
    """Display-name functions for people and groups. Share-safe numbers people by first appearance on the cards."""
    pid = {}
    for n in ([p["name"] for p in s["top_people"]] + [p["name"] for p in s["new_top"]]
              + [n for n, _ in s["fastest_to_me"] + s["i_reply_fastest"] + s["i_start_top"]]):
        pid.setdefault(n, len(pid) + 1)
    gid = {g["name"]: i for i, g in enumerate(s["top_groups"], 1)}
    firsts = Counter(n.split()[0] for n in pid if n.split())

    def person(n):
        if n[:1] in "+0123456789":  # an unsaved contact: never print the phone number
            return "Unsaved number" if not safe else f"Person #{pid.get(n, len(pid) + 1)}"
        if safe:
            return safe_label(pid.get(n, len(pid) + 1), n)
        f = n.split()[0] if n.split() else n
        return f if firsts[f] == 1 else " ".join(n.split()[:2])

    def group(n):
        return f"Group #{gid.get(n, len(gid) + 1)}" if safe else n
    return person, group


# ---------- building blocks ----------

def bar_rows(items, fmt, bar_bg="rgba(255,255,255,.18)", bar_fg="#fff", nm=None):
    mx = max((v for _, v in items), default=1) or 1
    st = f' style="font-size:{nm}px"' if nm else ""
    return "".join(
        f'<div class="row"><span class="rk num">{i}</span><span class="nm"{st}>{e(n)}</span><span class="ct"{st}>{fmt(v)}</span>'
        f'<div class="bar" style="background:{bar_bg}"><div style="height:100%;width:{max(3, round(v / mx * 100))}%;background:{bar_fg};border-radius:11px"></div></div></div>'
        for i, (n, v) in enumerate(items, 1))


def plain_rows(items, fmt, nm=64):
    return "".join(f'<div class="row" style="grid-template-columns:64px 1fr auto"><span class="rk num">{i}</span>'
                   f'<span class="nm" style="font-size:{nm}px">{e(n)}</span><span class="ct" style="font-size:{nm}px">{fmt(v)}</span></div>'
                   for i, (n, v) in enumerate(items, 1))


def join_and(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def pct(v: int, total: int) -> str:
    p = v / max(1, total) * 100
    return "<1%" if 0 < p < 1 else f"{round(p)}%"


def period(s: dict) -> tuple[str, str]:
    """(big title, short label) for the date range."""
    f, l = date.fromisoformat(s["first"]), date.fromisoformat(s["last"])
    if s.get("since") and s["since"][5:] == "01-01" and f.year == l.year:
        return str(f.year), str(f.year)
    if not s.get("since"):
        return "All of it", (str(f.year) if f.year == l.year else f"{f.year} to {l.year}")
    if f.year != l.year:
        return f"Since {f.year}", f"{f.year} to {l.year}"
    return f"Since {R.nice_date(s['first'], False)}", f"{R.nice_date(s['first'])} to {R.nice_date(s['last'])}"


# ---------- cards ----------

def build_personal_cards(s: dict, owner: str = "", safe: bool = False) -> list[tuple[str, str]]:
    person, group = namer(s, safe)
    big_title, label = period(s)
    whose = f"{owner}'s" if owner else "My"
    span = f"{R.nice_date(s['first'])} to {R.nice_date(s['last'])}"
    sky = f'<img class="sky" src="data:image/png;base64,{R._b64("sky.png")}" alt="">'
    nm = 58 if safe else None
    cards = []

    # cover
    body = f"""
      {R.wa_kicker(f"{whose} WhatsApp, wrapped", "margin-top:760px")}
      <div class="h1" style="font-size:{R.fit(big_title, 150, 10, 96)}px">{e(big_title)}</div>
      <div class="lead muted" style="margin-top:36px">{e(span)}</div>
      <div style="margin-top:auto;margin-bottom:40px">
        <div class="huge num" style="font-size:{min(300, 1680 // len(f"{s['total']:,}"))}px">{s['total']:,}</div>
        <div class="lead" style="margin-top:20px">messages across {s['chats']:,} chats. {s['sent']:,} from me, {s['received']:,} to me.</div>
      </div>"""
    cards.append(("cover", R.card("paper", body, sky)))

    # volume
    ps = round(s["sent"] / s["total"] * 100)
    body = f"""
      <div class="kicker">The volume</div>
      <div class="h1">I sent {s['sent']:,} messages.</div>
      <div class="lead" style="margin-top:28px;opacity:.85">That is {round(s['sent'] / s['span_days']):,} a day, every day.</div>
      <div style="margin-top:110px">
        <div style="display:flex;justify-content:space-between;font-size:56px;letter-spacing:-.035em"><span>Sent</span><span>Received</span></div>
        <div style="display:flex;height:64px;border-radius:32px;overflow:hidden;margin-top:22px"><div style="width:{ps}%;background:#fff"></div><div style="flex:1;background:rgba(255,255,255,.25)"></div></div>
        <div style="display:flex;justify-content:space-between;font-size:48px;margin-top:18px"><span class="num">{s['sent']:,}</span><span class="num">{s['received']:,}</span></div>
      </div>
      <div class="mgrid" style="margin-top:110px">
        <div class="panel" style="background:rgba(255,255,255,.1)"><div class="v">{s['people_chats']:,}</div><div class="l">one-to-one chats</div></div>
        <div class="panel" style="background:rgba(255,255,255,.1)"><div class="v">{s['group_chats']:,}</div><div class="l">groups I write in</div></div>
        <div class="panel" style="background:rgba(255,255,255,.1);grid-column:1/3"><div class="v">{s['words_sent']:,}</div><div class="l">words typed. About {max(1, round(s['words_sent'] / 250)):,} book pages.</div></div>
      </div>"""
    cards.append(("volume", R.card("blue", body)))

    # top people
    tp = s["top_people"]
    if tp:
        lead = person(tp[0]["name"])
        body = f"""
          <div class="kicker">My top {len(tp)} people</div>
          <div class="h1" style="font-size:{R.fit(lead, 120, 10, 84)}px">{e(lead)} is number one.</div>
          <div class="rows">{bar_rows([(person(p['name']), p['total']) for p in tp], lambda v: f'{v:,}', nm=nm)}</div>
          <div class="lead" style="margin-top:auto;margin-bottom:24px;opacity:.8">{tp[0]['total']:,} messages in one chat. {tp[0]['me']:,} of them from me.</div>"""
        cards.append(("top-people", R.card("blue", body)))

    # top groups
    tg = s["top_groups"]
    if tg:
        lead = group(tg[0]["name"])
        out = (f"{s['excluded_groups']:,} big {'group' if s['excluded_groups'] == 1 else 'groups'} where I mostly read along "
               f"{'is' if s['excluded_groups'] == 1 else 'are'} left out.") if s["excluded_groups"] else ""
        body = f"""
          <div class="kicker">My top groups</div>
          <div class="h1" style="font-size:{R.fit(lead, 108, 16, 72)}px">{e(lead)} gets the most from me.</div>
          <div class="rows">{bar_rows([(group(g['name']), g['me']) for g in tg], lambda v: f'{v:,}', bar_bg='rgba(22,37,30,.1)', bar_fg=R.BLUE, nm=60)}</div>
          <div class="lead muted" style="margin-top:auto;margin-bottom:24px">Messages I sent. {out}</div>"""
        cards.append(("top-groups", R.card("paper", body)))

    # when
    hmax = max(s["hours"]) or 1
    bars = "".join(f'<i style="height:{max(2, round(v / hmax * 100))}%;background:{R.BLUE_DETAIL if h != s["peak_hour"] else "#fff"}"></i>'
                   for h, v in enumerate(s["hours"]))
    wmax, wtot = max(s["weekdays"]) or 1, sum(s["weekdays"]) or 1
    wk = "".join(f'<div class="wk"><span>{d}</span><div class="track" style="background:rgba(245,243,235,.1)"><div class="fill" style="width:{round(v / wmax * 100)}%;background:{"#fff" if v == wmax else R.BLUE_DETAIL}"></div></div><span class="num muted" style="text-align:right">{round(v / wtot * 100)}%</span></div>'
                 for d, v in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], s["weekdays"]))
    bd = s["busiest_day"]
    body = f"""
      <div class="kicker">When I text</div>
      <div class="big" style="margin-top:20px">{R.hour_label(s['peak_hour'])}</div>
      <div class="lead muted" style="margin-top:20px">is my peak hour. {e(s['peak_weekday'])}s are the busiest.</div>
      <div class="hist" style="height:380px;margin-top:56px">{bars}</div>
      <div class="axis"><span>midnight</span><span>6am</span><span>noon</span><span>6pm</span><span>11pm</span></div>
      <div style="margin-top:36px;margin-bottom:48px">{wk}</div>
      <div class="lead" style="margin-top:auto;margin-bottom:24px">Busiest day ever: <span style="color:{R.BLUE_DETAIL}">{R.nice_date(bd['date'])}</span>, {bd['messages']:,} messages, {bd['sent']:,} from me.</div>"""
    cards.append(("when", R.card("ink", body)))

    # streak
    st = s["streak"]
    strip = R.day_strip({"first": s["first"], "last": s["last"], "streak": st, "day_counts": s["day_counts"]}).replace(
        "Each square is a day.", "Each square is a day I sent something.")
    body = f"""
      <div class="kicker">Longest streak</div>
      <div class="huge" style="color:{R.BLUE};margin-top:72px;font-size:400px">{st['days']}</div>
      <div class="h1" style="margin-top:8px">{'day' if st['days'] == 1 else 'days'} in a row.</div>
      <div class="lead muted" style="margin-top:28px">I sent at least one message every day from {R.nice_date(st['start'])} to {R.nice_date(st['end'])}.</div>
      {strip}
      <div class="stat3">
        <div><div class="v">{s['active_days']:,}</div><div class="l">days I texted, out of {s['span_days']:,}</div></div>
        <div><div class="v">{round(s['sent'] / max(1, s['active_days'])):,}</div><div class="l">messages on an active day</div></div>
        <div><div class="v">{s['conversations_1to1']:,}</div><div class="l">one-to-one conversations</div></div>
      </div>"""
    cards.append(("streak", R.card("paper", body)))

    # voice notes and media
    m = s["media_sent"]
    tiles = [(m["photo"] + m["media"], "photos sent"), (m["video"], "videos sent"), (m["sticker"] + m["gif"], "stickers and GIFs"),
             (m["document"], "files sent"), (m["deleted"], "messages I deleted")]
    tiles_html = "".join(f'<div class="panel" style="background:rgba(245,243,235,.08){";grid-column:1/3" if i == len(tiles) - 1 else ""}"><div class="v">{v:,}</div><div class="l">{lab}</div></div>'
                         for i, (v, lab) in enumerate(tiles))
    vs, vr = s["voice_sent"], s["voice_received"]
    verdict = ("I talk more than I listen." if vs > vr else "I listen more than I talk." if vr > vs else "Perfectly even.")
    body = f"""
      <div class="kicker">Voice notes</div>
      <div style="display:flex;gap:80px;margin-top:40px;align-items:flex-end">
        <div><div class="big" style="color:{R.BLUE_DETAIL}">{vs:,}</div><div class="lead">sent</div></div>
        <div><div class="big" style="opacity:.55">{vr:,}</div><div class="lead muted">received</div></div>
      </div>
      <div class="lead" style="margin-top:36px">{verdict}</div>
      <div class="mgrid" style="margin-top:72px">{tiles_html}</div>"""
    cards.append(("voice-media", R.card("ink", body)))

    # emojis and words
    if s["top_emojis"] or s["top_words"]:
        te = s["top_emojis"][0][0] if s["top_emojis"] else ""
        emo = "".join(f'<div><div class="g">{e(g)}</div><div class="c">{c:,}</div></div>' for g, c in s["top_emojis"][:5])
        words = "".join(f'<span class="chip" style="background:#fff">{e(w)}<span class="num muted" style="font-size:32px">{c:,}</span></span>'
                        for w, c in s["top_words"][:9])
        body = f"""
          <div class="kicker">{'My emojis and words' if words else 'My emojis'}</div>
          <div class="h1">{'My official emoji' if te else 'Words over emojis.'}</div>
          {f'<div style="font-size:300px;line-height:1.15;margin-top:24px">{e(te)}</div><div class="emo" style="margin-top:24px">{emo}</div>' if te else ''}
          {f'<div class="kicker" style="margin-top:auto">Words I could not stop saying</div><div class="words">{words}</div>' if words else ''}"""
        cards.append(("emojis-words", R.card("soft", body)))

    # speed
    if s["fastest_to_me"] or s["i_reply_fastest"]:
        head = (f"{e(person(s['fastest_to_me'][0][0]))} answers me in {fmt_duration(s['fastest_to_me'][0][1])}."
                if s["fastest_to_me"] else f"I answer in {fmt_duration(s['my_reply_median_s'])}.")
        part_a = (f'<div class="kicker" style="margin-top:48px">Who replies to me fastest</div>'
                  f'<div class="rows" style="margin-top:28px;gap:22px">{plain_rows([(person(n), v) for n, v in s["fastest_to_me"]], fmt_duration, nm or 64)}</div>') if s["fastest_to_me"] else ""
        part_b = (f'<div class="kicker" style="margin-top:56px">Who I reply to fastest</div>'
                  f'<div class="rows" style="margin-top:28px;gap:22px">{plain_rows([(person(n), v) for n, v in s["i_reply_fastest"]], fmt_duration, nm or 64)}</div>') if s["i_reply_fastest"] else ""
        mine = f"My typical reply: {fmt_duration(s['my_reply_median_s'])}." if s["my_reply_median_s"] is not None else ""
        body = f"""
          <div class="kicker">Fastest thumbs</div>
          <div class="h1" style="font-size:{R.fit(head, 100, 30, 72)}px">{head}</div>
          {part_a}{part_b}
          <div class="lead" style="margin-top:auto;margin-bottom:24px;opacity:.8">{mine}</div>"""
        cards.append(("speed", R.card("blue", body)))

    # who I text first
    if s["i_start_top"]:
        body = f"""
          <div class="kicker">Who I text first</div>
          <div class="big" style="color:{R.BLUE};margin-top:40px">{round(s['i_start_share'] * 100)}%</div>
          <div class="lead" style="margin-top:20px">of my one-to-one conversations start with me.</div>
          <div class="kicker" style="margin-top:110px">I start it most with</div>
          <div class="rows" style="margin-top:28px;gap:26px">{plain_rows([(person(n), v) for n, v in s['i_start_top']], lambda v: f'{v:,}×', nm or 66)}</div>
          <div class="lead muted" style="margin-top:auto;margin-bottom:24px">A conversation starts after 4 hours of silence.</div>"""
        cards.append(("starters", R.card("paper", body)))

    # new people
    if s["new_people"]:
        body = f"""
          <div class="kicker">New this {'year' if big_title.isdigit() else 'time'}</div>
          <div class="huge" style="margin-top:40px">{s['new_people']:,}</div>
          <div class="lead" style="margin-top:20px">new people I really talk to. First message since {R.nice_date(s['since'])}, 20 messages or more.</div>
          <div class="kicker" style="margin-top:96px">The biggest new chats</div>
          <div class="rows" style="margin-top:36px">{bar_rows([(person(p['name']), p['total']) for p in s['new_top']], lambda v: f'{v:,}', nm=nm)}</div>"""
        cards.append(("new-people", R.card("blue", body)))

    # languages
    L = {k: v for k, v in s["langs"].items() if v >= 0.002 * max(1, s["lang_classified"])}
    if L:
        tl = sum(L.values())
        order = sorted(L, key=lambda k: -L[k])[:4]
        lrows = "".join(f'<div class="wk" style="grid-template-columns:260px 1fr 150px;font-size:58px;margin-top:44px"><span>{LANGS[k]}</span><div class="track" style="background:rgba(245,243,235,.1);height:48px;border-radius:24px"><div class="fill" style="width:{round(L[k] / L[order[0]] * 100)}%;background:{"#fff" if i == 0 else R.BLUE_DETAIL};border-radius:24px"></div></div><span class="num" style="text-align:right">{pct(L[k], tl)}</span></div>'
                        for i, k in enumerate(order))
        rest = f"Then {join_and([LANGS[k] for k in order[1:]])}, depending on who is on the other end." if len(order) > 1 else "One language, every chat."
        body = f"""
          <div class="kicker">Languages I write in</div>
          <div class="h1">Mostly {LANGS[order[0]]}.</div>
          <div class="lead muted" style="margin-top:28px">{rest}</div>
          <div style="margin-top:96px">{lrows}</div>
          <div class="lead muted" style="margin-top:auto;margin-bottom:24px">Based on {s['lang_classified']:,} of my messages with a clear language.</div>"""
        cards.append(("languages", R.card("ink", body)))

    # archetype
    a = s["archetype"]
    runners = "".join(f'<div class="aw"><div class="ti" style="font-size:64px">{e(t)}</div><div class="ln">{e(ln)}</div></div>' for t, ln in a["runners"])
    body = f"""
      <div class="kicker">My WhatsApp archetype</div>
      <div class="h1" style="font-size:{R.fit(a['title'], 150, 12, 110)}px;color:{R.BLUE};margin-top:640px;max-width:900px">{e(a['title'])}</div>
      <div class="lead" style="margin-top:36px">{e(a['line'])}</div>
      <div class="kicker" style="margin-top:auto;margin-bottom:12px">Runner-up titles</div>
      <div style="margin-bottom:24px">{runners}</div>"""
    cards.append(("archetype", R.card("paper", body, sky)))

    # summary
    te = s["top_emojis"][0] if s["top_emojis"] else ("none", 0)
    top = person(tp[0]["name"]) if tp else "n/a"
    lead_lang = LANGS[max(s["langs"], key=s["langs"].get)] if s["langs"] else ""
    body = f"""
      <div class="kicker">{e(owner or 'Me')} · {e(label)}</div>
      <div class="h1" style="font-size:112px">My WhatsApp, wrapped.</div>
      <div class="sum">
        <div class="panel"><div class="k">Messages sent</div><div class="v num">{s['sent']:,}</div><div class="s">{s['received']:,} received</div></div>
        <div class="panel"><div class="k">Top person</div><div class="v" style="font-size:{56 if safe else 64}px">{e(top)}</div><div class="s">{tp[0]['total'] if tp else 0:,} messages</div></div>
        <div class="panel"><div class="k">Longest streak</div><div class="v num">{st['days']} days</div><div class="s">{R.nice_date(st['start'], False)} to {R.nice_date(st['end'], False)}</div></div>
        <div class="panel"><div class="k">Peak hour</div><div class="v">{R.hour_label(s['peak_hour'])}</div><div class="s">{e(s['peak_weekday'])}s busiest</div></div>
        <div class="panel"><div class="k">Top emoji</div><div class="v">{e(te[0])}</div><div class="s">{te[1]:,} times</div></div>
        <div class="panel"><div class="k">Voice notes</div><div class="v num">{vs:,}</div><div class="s">sent, {vr:,} received</div></div>
      </div>
      <div class="panel" style="margin-top:22px;background:rgba(255,255,255,.1)"><div class="k" style="font-size:32px;opacity:.75;margin-bottom:6px">Archetype</div><div class="awl" style="font-size:56px">{e(a['title'])}</div><div class="awl">{s['chats']:,} chats{(' · ' + lead_lang + ' first') if lead_lang else ''}</div></div>"""
    cards.append(("summary", R.card("blue", body)))
    return cards


def build_personal_page(s: dict, cards, png_names, owner: str = "", safe: bool = False, notes: str = "") -> str:
    person, _ = namer(s, safe)
    slots = "".join(f'<div><div class="slot">{h}</div>' + (f'<a class="dl" href="cards/{e(n)}" download>Save {e(k.replace("-", " "))} card</a>' if n else "") + "</div>"
                    for (k, h), n in zip(cards, png_names or [None] * len(cards)))
    trs = "".join(f"<tr><td>{e(person(p['name']))}</td><td>{p['total']:,}</td><td>{p['me']:,}</td><td>{p['total'] - p['me']:,}</td></tr>"
                  for p in s["top_people"])
    _, label = period(s)
    title = f"{owner + chr(39) + 's' if owner else 'My'} WhatsApp, wrapped · {label}" + (" (share-safe)" if safe else "")
    span = f"{R.nice_date(s['first'])} to {R.nice_date(s['last'])}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; font-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>{e(title)}</title><style>{R.font_face()}{R.CARD_CSS}{R.PAGE_CSS}</style></head>
<body><div class="wrap"><header><h1>{e(title)}</h1>
<p>{s['total']:,} messages across {s['chats']:,} chats, {e(span)}. Made on this device. Nothing was uploaded.{' Names are replaced with numbers and initials.' if safe else ''}</p></header>
<div class="deck">{slots}</div>
<h2>Top people</h2><div class="tbl"><table><thead><tr><th>Person</th><th>Messages</th><th>From me</th><th>To me</th></tr></thead><tbody>{trs}</tbody></table></div>
<p class="note">Made with Edge · <a href="https://getedge.cc">getedge.cc</a>. {R.NOT_AFFILIATED} {e(notes)} Typical reply = median time to answer within 6 hours, in one-to-one chats with 150+ messages. A conversation starts after 4 hours of silence.</p>
</div><script>
function fitCards(){{document.querySelectorAll('.slot').forEach(function(s){{var c=s.querySelector('.card');c.style.transform='scale('+(s.clientWidth/1080)+')';}});}}
window.addEventListener('resize',fitCards);fitCards();</script></body></html>"""
