"""Render Wrapped stats into story cards (1080x1920 HTML) and a self-contained page.

All assets are inlined. The cards never load anything from the network.
"""
from __future__ import annotations

import base64
import html
from datetime import date, datetime
from pathlib import Path

from stats import fmt_duration

ASSETS = Path(__file__).resolve().parent.parent / "assets"

PAPER, SURFACE, INK, MUTED, LINE = "#f5f3eb", "#fbfaf6", "#16251e", "#59685f", "#d3d9cf"
BLUE, BLUE_BASE, BLUE_SOFT, BLUE_LIGHT, BLUE_DETAIL = "#154cff", "#0c35ba", "#e9efff", "#527eff", "#82a2ff"

ARCH = ('<svg class="arch" viewBox="0 0 64 40" aria-hidden="true"><path fill="currentColor" '
        'd="M0 40V36C0 16.1 14.3 0 32 0s32 16.1 32 36v4z"/></svg>')

e = html.escape


def _b64(name: str) -> str:
    return base64.b64encode((ASSETS / name).read_bytes()).decode()


def font_face() -> str:
    return ("@font-face{font-family:'Inter W';src:url(data:font/woff2;base64,%s) format('woff2');"
            "font-weight:100 900;font-display:block}" % _b64("InterVariable-subset.woff2"))


def short_names(people: list[dict]) -> dict[str, str]:
    firsts = [p["name"].split()[0] for p in people]
    out = {}
    for p, f in zip(people, firsts):
        out[p["name"]] = f if firsts.count(f) == 1 else p["name"]
    return out


def hour_label(h: int) -> str:
    if h == 0:
        return "midnight"
    if h == 12:
        return "noon"
    return f"{h % 12}{'am' if h < 12 else 'pm'}"


def nice_date(iso: str, year: bool = True) -> str:
    d = date.fromisoformat(iso[:10])
    return f"{d.strftime('%b')}\u00a0{d.day}" + (f", {d.year}" if year else "")


def pl(n: int, word: str) -> str:
    return f"{n:,} {word}{'' if n == 1 else 's'}"


def fit(text: str, base: int, max_chars: int, floor: int) -> int:
    n = len(text)
    if n <= max_chars:
        return base
    return max(floor, int(base * max_chars / n))


CARD_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
.card{width:1080px;height:1920px;position:relative;overflow:hidden;display:flex;flex-direction:column;
  padding:120px 96px 190px;font-family:'Inter W','Inter Display','Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif,
  'Apple Color Emoji','Noto Color Emoji','Segoe UI Emoji';font-weight:450;letter-spacing:-.02em;
  -webkit-font-smoothing:antialiased;font-feature-settings:'ss01','cv11'}
.t-paper{background:%(PAPER)s;color:%(INK)s} .t-blue{background:%(BLUE)s;color:#fff}
.t-ink{background:%(INK)s;color:%(PAPER)s} .t-soft{background:%(BLUE_SOFT)s;color:%(INK)s}
.kicker{font-size:44px;line-height:1.2;opacity:.72;letter-spacing:-.01em}
.h1{font-size:120px;line-height:1.02;letter-spacing:-.052em;margin-top:24px}
.huge{font-size:300px;line-height:.9;letter-spacing:-.06em;font-variant-numeric:tabular-nums}
.big{font-size:230px;line-height:.95;letter-spacing:-.055em;font-variant-numeric:tabular-nums}
.lead{font-size:52px;line-height:1.25;letter-spacing:-.025em}
.muted{opacity:.68}
.num{font-variant-numeric:tabular-nums}
.foot{position:absolute;left:96px;right:96px;bottom:56px;height:80px;display:flex;align-items:center;gap:16px;font-size:30px;letter-spacing:-.01em;opacity:.62}
.foot .arch{width:40px;height:25px}
.foot b{font-weight:560}
.rows{display:flex;flex-direction:column;gap:46px;margin-top:96px}
.row{display:grid;grid-template-columns:64px 1fr auto;align-items:baseline;gap:20px}
.row .rk{font-size:44px;opacity:.6}
.row .nm{font-size:74px;letter-spacing:-.035em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row .ct{font-size:74px;letter-spacing:-.035em;font-variant-numeric:tabular-nums}
.bar{grid-column:2/4;height:26px;border-radius:13px;margin-top:-4px}
.chip{display:inline-flex;align-items:baseline;gap:14px;padding:20px 34px;border-radius:999px;font-size:54px;letter-spacing:-.03em}
.stat3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;margin-top:auto;margin-bottom:24px}
.stat3 .v{font-size:104px;letter-spacing:-.05em;line-height:1;font-variant-numeric:tabular-nums}
.stat3 .l{font-size:38px;line-height:1.25;margin-top:14px;opacity:.7}
.panel{border-radius:28px;padding:40px 44px}
.hist{display:flex;align-items:flex-end;gap:9px;height:480px;margin-top:72px}
.hist i{flex:1;border-radius:8px 8px 3px 3px;display:block;min-height:6px}
.axis{display:flex;justify-content:space-between;font-size:34px;opacity:.6;margin-top:16px}
.wk{display:grid;grid-template-columns:130px 1fr 130px;align-items:center;gap:24px;font-size:46px;margin-top:30px}
.wk .track{height:36px;border-radius:18px;overflow:hidden}
.wk .fill{height:100%%;border-radius:18px}
.emo{display:grid;grid-template-columns:repeat(5,1fr);gap:20px;margin-top:56px;text-align:center}
.emo .g{font-size:140px;line-height:1.1}
.emo .c{font-size:42px;opacity:.7;margin-top:8px;font-variant-numeric:tabular-nums}
.words{display:flex;flex-wrap:wrap;gap:18px;margin-top:40px}
.aw{display:flex;flex-direction:column;gap:8px;padding:34px 0;border-top:2px solid %(LINE)s}
.aw:first-child{border-top:0}
.aw .ti{font-size:72px;letter-spacing:-.045em;line-height:1.05}
.aw .who{font-size:48px}
.aw .ln{font-size:40px;opacity:.7;line-height:1.3}
.duel-r{display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:baseline;padding:26px 0;border-top:2px solid rgba(255,255,255,.2);font-size:60px;letter-spacing:-.035em}
.duel-r .lab{font-size:36px;opacity:.75;text-align:center}
.aw.lg{padding:48px 0;gap:12px}.aw.lg .ti{font-size:100px}.aw.lg .who{font-size:58px}.aw.lg .ln{font-size:46px}
.aw.cmp{padding:24px 0;gap:4px}.aw.cmp .ti{font-size:60px}.aw.cmp .who{font-size:42px}.aw.cmp .ln{font-size:36px}
.strip{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,1fr);gap:4px;margin-top:64px}
.strip i{display:block;border-radius:3px}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:56px}
.mgrid .panel .v{font-size:130px;letter-spacing:-.055em;line-height:1;font-variant-numeric:tabular-nums}
.mgrid .panel .l{font-size:42px;margin-top:12px;opacity:.75}
.sky{position:absolute;right:-150px;top:-90px;width:700px;opacity:1;pointer-events:none}
.sum{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:56px}
.sum .panel{background:rgba(255,255,255,.1)}
.sum .k{font-size:32px;opacity:.75}
.sum .v{font-size:64px;letter-spacing:-.045em;line-height:1.08;margin-top:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sum .s,.awl{font-size:34px;opacity:.75;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.awl{font-size:40px;opacity:.92;margin-top:10px}
""" % dict(PAPER=PAPER, INK=INK, BLUE=BLUE, BLUE_SOFT=BLUE_SOFT, LINE=LINE)


def day_strip(s: dict) -> str:
    """GitHub-style grid of days (weeks as columns), streak in Edge blue. Up to 53 weeks around the streak."""
    from datetime import timedelta
    counts = s.get("day_counts", {})
    first = date.fromisoformat(s["first"][:10])
    last = date.fromisoformat(s["last"][:10])
    st_end = date.fromisoformat(s["streak"]["end"]) if s["streak"]["end"] else last
    st_start = date.fromisoformat(s["streak"]["start"]) if s["streak"]["start"] else last
    end = min(last, max(st_end + timedelta(days=120), first + timedelta(days=370)))
    start = max(first, end - timedelta(days=370))
    start -= timedelta(days=start.weekday())
    cells, d = [], start
    while d <= end:
        c = counts.get(d.isoformat(), 0)
        if d < first or d > last:
            col = "transparent"
        elif st_start <= d <= st_end:
            col = BLUE
        elif c:
            col = "#b4c6ff"
        else:
            col = LINE
        cells.append(f'<i style="background:{col}"></i>')
        d += timedelta(days=1)
    weeks = (len(cells) + 6) // 7
    cell = max(6, min(44, (888 - 4 * (weeks - 1)) // weeks))
    return (f'<div class="strip" style="grid-template-columns:repeat({weeks},{cell}px);grid-template-rows:repeat(7,{cell}px)">{"".join(cells)}</div>'
            f'<div style="font-size:32px;opacity:.6;margin-top:18px">Each square is a day. The streak is in blue.</div>')


def duel(s: dict, names: dict) -> str:
    """Head-to-head layout for a two-person chat."""
    a, b = s["people"][0], s["people"][1]
    pa = round(a["messages"] / (a["messages"] + b["messages"]) * 100)

    def rep(p):
        return fmt_duration(p["reply_median_s"]) if p["reply_median_s"] is not None else "n/a"
    rows = [("messages", f"{a['messages']:,}", f"{b['messages']:,}"),
            ("words per message", f"{a['avg_words']:.1f}", f"{b['avg_words']:.1f}"),
            ("voice notes", f"{a['voice']:,}", f"{b['voice']:,}"),
            ("emojis", f"{a['emojis']:,}", f"{b['emojis']:,}"),
            ("typical reply", rep(a), rep(b))]
    trs = "".join(f'<div class="duel-r"><span class="num">{x}</span><span class="lab">{k}</span><span class="num" style="text-align:right">{y}</span></div>'
                  for k, x, y in rows)
    return f"""<div style="margin-top:96px">
      <div style="display:flex;justify-content:space-between;font-size:74px;letter-spacing:-.04em"><span>{e(names[a['name']])}</span><span>{e(names[b['name']])}</span></div>
      <div style="display:flex;height:64px;border-radius:32px;overflow:hidden;margin-top:24px"><div style="width:{pa}%;background:#fff"></div><div style="flex:1;background:rgba(255,255,255,.25)"></div></div>
      <div style="display:flex;justify-content:space-between;font-size:44px;margin-top:16px;opacity:.8"><span class="num">{pa}%</span><span class="num">{100 - pa}%</span></div>
      <div style="margin-top:64px">{trs}</div></div>"""


def foot() -> str:
    return f'<div class="foot">{ARCH}<span>made with <b>Edge</b> · getedge.cc</span></div>'


def card(theme: str, body: str, extra: str = "") -> str:
    return f'<section class="card t-{theme}">{extra}{body}{foot()}</section>'


def build_cards(s: dict, show_words: bool = True) -> list[tuple[str, str]]:
    names = short_names(s["people"])
    title = s["title"]
    cards: list[tuple[str, str]] = []
    first, last = s["first"], s["last"]
    span = f"{nice_date(first)} to {nice_date(last)}"

    # 1. Cover
    tsize = fit(title, 150, 11, 84)
    sky = f'<img class="sky" src="data:image/png;base64,{_b64("sky.png")}" alt="">'
    people_line = f"{s['people_count']} people" if s["is_group"] else " and ".join(names[p["name"]] for p in s["people"][:2])
    body = f"""
      <div class="kicker" style="margin-top:820px">Your chat, wrapped</div>
      <div class="h1" style="font-size:{tsize}px;max-width:900px">{e(title)}</div>
      <div class="lead muted" style="margin-top:40px">{e(span)}</div>
      <div style="margin-top:auto;margin-bottom:40px">
        <div class="huge num">{s['total_messages']:,}</div>
        <div class="lead" style="margin-top:20px">{'message' if s['total_messages'] == 1 else 'messages'} between {e(people_line)}, across {pl(s['span_days'], 'day')}.</div>
      </div>"""
    cards.append(("cover", card("paper", body, sky)))

    # 2. Top senders
    top = s["people"][:6]
    mx = top[0]["messages"]
    rows = "".join(
        f"""<div class="row"><span class="rk num">{i}</span><span class="nm">{e(names[p['name']])}</span><span class="ct">{p['messages']:,}</span>
        <div class="bar" style="background:rgba(255,255,255,.18)"><div style="height:100%;width:{max(3, round(p['messages'] / mx * 100))}%;background:#fff;border-radius:11px"></div></div></div>"""
        for i, p in enumerate(top, 1))
    leader = top[0]
    body = f"""
      <div class="kicker">Who talked the most</div>
      <div class="h1">{e(names[leader['name']])} sent {round(leader['share'] * 100)}% of everything.</div>
      {duel(s, names) if len(s["people"]) == 2 else f'<div class="rows">{rows}</div>'}
      <div class="lead" style="margin-top:auto;margin-bottom:24px;opacity:.8">{s['total_words']:,} words in total. That is about {max(1, round(s['total_words'] / 250)):,} book pages.</div>"""
    cards.append(("top-senders", card("blue", body)))

    # 3. When
    hmax = max(s["hours"]) or 1
    bars = "".join(
        f'<i style="height:{max(2, round(v / hmax * 100))}%;background:{BLUE_DETAIL if h != s["peak_hour"] else "#fff"}"></i>'
        for h, v in enumerate(s["hours"]))
    wmax = max(s["weekdays"]) or 1
    wdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    total = s["total_messages"]
    wk = "".join(
        f"""<div class="wk"><span>{d}</span><div class="track" style="background:rgba(245,243,235,.1)"><div class="fill" style="width:{round(v / wmax * 100)}%;background:{'#fff' if v == wmax else BLUE_DETAIL}"></div></div><span class="num muted" style="text-align:right">{round(v / total * 100)}%</span></div>"""
        for d, v in zip(wdays, s["weekdays"]))
    bd = s["busiest_day"]
    body = f"""
      <div class="kicker">When this chat comes alive</div>
      <div class="big" style="margin-top:20px">{hour_label(s['peak_hour'])}</div>
      <div class="lead muted" style="margin-top:20px">is peak hour. {e(s['peak_weekday'])}s are the busiest.</div>
      <div class="hist" style="height:400px;margin-top:56px">{bars}</div>
      <div class="axis"><span>midnight</span><span>6am</span><span>noon</span><span>6pm</span><span>11pm</span></div>
      <div style="margin-top:40px;margin-bottom:56px">{wk}</div>
      <div class="lead" style="margin-top:auto;margin-bottom:24px">Busiest day ever: <span style="color:{BLUE_DETAIL}">{nice_date(bd['date'])}</span>, {pl(bd['messages'], 'message')}.</div>"""
    cards.append(("when", card("ink", body)))

    # 4. Streak
    st = s["streak"]
    body = f"""
      <div class="kicker">Longest streak</div>
      <div class="huge" style="color:{BLUE};margin-top:72px;font-size:400px">{st['days']}</div>
      <div class="h1" style="margin-top:8px">{'day' if st['days'] == 1 else 'days'} in a row.</div>
      <div class="lead muted" style="margin-top:28px">Nobody let the chat go quiet from {nice_date(st['start'], False)} to {nice_date(st['end'])}.</div>
      {day_strip(s)}
      <div class="stat3">
        <div><div class="v">{s['active_days']:,}</div><div class="l">days with messages, out of {s['span_days']:,}</div></div>
        <div><div class="v">{round(s['per_day_avg']):,}</div><div class="l">messages on an average day</div></div>
        <div><div class="v">{s['conversations']:,}</div><div class="l">separate conversations</div></div>
      </div>"""
    cards.append(("streak", card("paper", body)))

    # 5. Emojis and words
    emo = "".join(f'<div><div class="g">{e(g)}</div><div class="c">{c:,}</div></div>' for g, c in s["top_emojis"][:5])
    words = "".join(f'<span class="chip" style="background:#fff">{e(w)}<span class="num muted" style="font-size:32px">{c:,}</span></span>'
                    for w, c in s["top_words"][:9]) if show_words else ""
    if s["top_emojis"] or (show_words and s["top_words"]):
        top_e = s["top_emojis"][0][0] if s["top_emojis"] else ""
        body = f"""
          <div class="kicker">The chat in emojis</div>
          <div class="h1">{'The official emoji' if top_e else 'Words over emojis.'}</div>
          {f'<div style="font-size:300px;line-height:1.15;margin-top:24px">{e(top_e)}</div>' if top_e else ''}
          <div class="emo" style="margin-top:24px">{emo}</div>
          {'<div class="kicker" style="margin-top:auto">Words you could not stop saying</div><div class="words">' + words + '</div>' if words else ''}"""
        cards.append(("emojis-words", card("soft", body)))

    # 6. Speed and starters
    fast = s["fastest"][:5]
    starters = s["starters"][:5]
    if fast or starters:
        frows = "".join(f'<div class="row" style="grid-template-columns:64px 1fr auto"><span class="rk num">{i}</span><span class="nm">{e(names[n])}</span><span class="ct">{fmt_duration(v)}</span></div>'
                        for i, (n, v) in enumerate(fast, 1))
        conv = max(1, s["conversations"])
        srows = "".join(f'<div class="row" style="grid-template-columns:64px 1fr auto"><span class="rk num">{i}</span><span class="nm">{e(names[n])}</span><span class="ct">{round(c / conv * 100)}%</span></div>'
                        for i, (n, c) in enumerate(starters[:3], 1))
        if fast:
            top_part = f"""
          <div class="kicker">Fastest thumbs</div>
          <div class="h1">{e(names[fast[0][0]])} replies in {fmt_duration(fast[0][1])}.</div>
          <div class="lead" style="margin-top:20px;opacity:.75">Typical reply time</div>
          <div class="rows" style="margin-top:36px;gap:26px">{frows}</div>
          <div class="kicker" style="margin-top:96px">Who starts the conversation</div>"""
        else:
            lead_s = starters[0]
            top_part = f"""
          <div class="kicker">Who starts the conversation</div>
          <div class="h1">{e(names[lead_s[0]])} breaks the silence.</div>"""
        body = f"""{top_part}
          <div class="rows" style="margin-top:36px;gap:26px">{srows}</div>"""
        cards.append(("speed-starters", card("blue", body)))

    # 7. Voice notes and media
    m = s["media"]
    voice_top = max(s["people"], key=lambda p: p["voice"])
    known_kinds = m["photo"] + m["video"] + m["sticker"] + m["gif"]
    tiles = []
    if known_kinds:
        for k, label in (("photo", "photos"), ("video", "videos"), ("sticker", "stickers"), ("gif", "GIFs")):
            tiles.append((m[k], label))
    else:
        tiles.append((m["media"], "photos, videos and stickers"))
    if m["document"]:
        tiles.append((m["document"], "files"))
    tiles.append((s["deleted_total"], "deleted messages"))
    tiles = tiles[:6]
    tiles_html = "".join(
        f'<div class="panel" style="background:rgba(245,243,235,.08){";grid-column:1/3" if (i == len(tiles) - 1 and len(tiles) % 2) else ""}"><div class="v">{v:,}</div><div class="l">{label}</div></div>'
        for i, (v, label) in enumerate(tiles))
    if m["voice"] or sum(v for v, _ in tiles):
        vline = (f"{e(names[voice_top['name']])} sent {voice_top['voice']:,} of them." if voice_top["voice"] else "")
        body = f"""
          <div class="kicker">Voice notes</div>
          <div class="huge" style="color:{BLUE_DETAIL};margin-top:40px">{m['voice']:,}</div>
          <div class="lead" style="margin-top:24px">{'voice note' if m['voice'] == 1 else 'voice notes'}. {vline}</div>
          <div class="mgrid">{tiles_html}</div>"""
        cards.append(("voice-media", card("ink", body)))

    # 8. Awards (one per person, 5 per card)
    aw = s["awards"]
    per_card = 6
    for i in range(0, len(aw), per_card):
        chunk = aw[i:i + per_card]
        compact = len(chunk) > 4
        size = " cmp" if compact else (" lg" if len(chunk) <= 3 else "")
        items = "".join(f'<div class="aw{size}"><div class="ti">{e(a["award"])}</div><div class="who" style="color:{BLUE}">{e(names.get(a["name"], a["name"]))}</div><div class="ln">{e(a["line"])}</div></div>'
                        for a in chunk)
        part = "" if len(aw) <= per_card else f" ({i // per_card + 1} of {(len(aw) + per_card - 1) // per_card})"
        body = f"""
          <div class="kicker">The awards{part}</div>
          <div class="h1" style="font-size:{80 if compact else 96}px">Everyone gets one.</div>
          <div style="margin-top:36px">{items}</div>"""
        cards.append((f"awards-{i // per_card + 1}", card("paper", body)))

    # 9. Summary (the one to post)
    lead = s["people"][0]
    top_e = s["top_emojis"][0][0] if s["top_emojis"] else "none"
    fastest = f"{names[s['fastest'][0][0]]}, {fmt_duration(s['fastest'][0][1])}" if s["fastest"] else "n/a"
    award_lines = "".join(f'<div class="awl">{e(a["award"])}: {e(names.get(a["name"], a["name"]))}</div>' for a in aw[:4])
    body = f"""
      <div class="kicker">{e(title)} · {date.fromisoformat(first[:10]).year if first[:4] == last[:4] else first[:4] + ' to ' + last[:4]}</div>
      <div class="h1" style="font-size:{fit(title, 112, 14, 72)}px">Our chat, wrapped.</div>
      <div class="sum">
        <div class="panel"><div class="k">Messages</div><div class="v num">{s['total_messages']:,}</div><div class="s">{pl(s['span_days'], 'day')}</div></div>
        <div class="panel"><div class="k">Top sender</div><div class="v">{e(names[lead['name']])}</div><div class="s">{pl(lead['messages'], 'message')}</div></div>
        <div class="panel"><div class="k">Longest streak</div><div class="v num">{pl(st['days'], 'day')}</div><div class="s">{nice_date(st['start'], False)} to {nice_date(st['end'], False)}</div></div>
        <div class="panel"><div class="k">Peak hour</div><div class="v">{hour_label(s['peak_hour'])}</div><div class="s">{e(s['peak_weekday'])}s busiest</div></div>
        <div class="panel"><div class="k">Top emoji</div><div class="v">{e(top_e)}</div><div class="s">{pl(s['top_emojis'][0][1] if s['top_emojis'] else 0, 'time')}</div></div>
        <div class="panel"><div class="k">Voice notes</div><div class="v num">{m['voice']:,}</div><div class="s">fastest reply: {e(fastest)}</div></div>
      </div>
      <div class="panel" style="margin-top:22px;background:rgba(255,255,255,.1)"><div class="k" style="font-size:32px;opacity:.75;margin-bottom:6px">Awards</div>{award_lines}</div>"""
    cards.append(("summary", card("blue", body)))
    return cards


def card_document(card_html: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_face()}{CARD_CSS}"
            "html,body{width:1080px;height:1920px;overflow:hidden}</style></head><body>" + card_html + "</body></html>")


PAGE_CSS = """
:root{--paper:%(PAPER)s;--ink:%(INK)s;--muted:%(MUTED)s;--line:%(LINE)s;--blue:%(BLUE)s;--surface:%(SURFACE)s}
@media (prefers-color-scheme:dark){:root{--paper:#111914;--ink:#eceee6;--muted:#a4b1a8;--line:#2d3b33;--surface:#18221c}}
html{background:var(--paper);color:var(--ink)}
body{margin:0;font-family:'Inter W','Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;font-weight:450;
  -webkit-font-smoothing:antialiased;padding:0 20px 80px}
.wrap{max-width:1180px;margin:0 auto}
header{padding:64px 0 24px}
header p{color:var(--muted);font-size:18px;margin:12px 0 0;max-width:60ch;line-height:1.55}
h1{font-size:clamp(36px,6vw,72px);letter-spacing:-.052em;line-height:1.04;font-weight:450;margin:0}
.deck{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px;margin-top:32px}
.slot{position:relative;width:100%%;aspect-ratio:9/16;border-radius:22px;overflow:hidden;box-shadow:0 1px 0 rgba(0,0,0,.04),0 12px 30px rgba(22,37,30,.12)}
.slot .card{transform-origin:0 0;position:absolute;left:0;top:0}
.dl{display:inline-block;margin-top:10px;font-size:14px;color:var(--blue);text-decoration:none}
.dl:hover{text-decoration:underline}
h2{font-size:32px;letter-spacing:-.04em;font-weight:450;margin:72px 0 16px}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:var(--surface)}
table{border-collapse:collapse;width:100%%;font-size:15px;font-variant-numeric:tabular-nums}
th,td{padding:12px 14px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:500}
tr:last-child td{border-bottom:0}
.note{color:var(--muted);font-size:14px;margin-top:40px;line-height:1.6}
.note a{color:inherit}
""" % dict(PAPER=PAPER, INK=INK, MUTED=MUTED, LINE=LINE, BLUE=BLUE, SURFACE=SURFACE)


def build_page(s: dict, cards: list[tuple[str, str]], png_names: list[str] | None) -> str:
    names = short_names(s["people"])
    slots = []
    for i, (key, html_card) in enumerate(cards):
        dl = f'<a class="dl" href="cards/{e(png_names[i])}" download>Save {e(key.replace("-", " "))} card</a>' if png_names else ""
        slots.append(f'<div><div class="slot">{html_card}</div>{dl}</div>')
    head = ["Person", "Messages", "Words", "Avg words", "Emojis", "Voice notes", "Media", "Starts", "Typical reply", "Award"]
    awards = {a["name"]: a["award"] for a in s["awards"]}
    rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in [
            e(p["name"]), f"{p['messages']:,}", f"{p['words']:,}", f"{p['avg_words']:.1f}", f"{p['emojis']:,}", f"{p['voice']:,}",
            f"{p['photo'] + p['video'] + p['sticker'] + p['gif'] + p['media']:,}", f"{p['starts']:,}",
            fmt_duration(p["reply_median_s"]) if p["reply_median_s"] is not None else "n/a", e(awards.get(p["name"], ""))]) + "</tr>"
        for p in s["people"])
    span = f"{nice_date(s['first'])} to {nice_date(s['last'])}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; font-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
<title>{e(s['title'])}, wrapped</title>
<style>{font_face()}{CARD_CSS}{PAGE_CSS}</style></head>
<body><div class="wrap">
<header><h1>{e(s['title'])}, wrapped</h1>
<p>{s['total_messages']:,} messages from {s['people_count']} people, {e(span)}. Made on this device from a WhatsApp export. Nothing was uploaded.</p></header>
<div class="deck">{''.join(slots)}</div>
<h2>Everyone, in numbers</h2>
<div class="tbl"><table><thead><tr>{''.join(f'<th>{h}</th>' for h in head)}</tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Made with Edge · <a href="https://getedge.cc">getedge.cc</a>. Typical reply = median time to answer someone else within 6 hours. A conversation starts after 4 hours of silence.</p>
</div>
<script>
function fitCards(){{document.querySelectorAll('.slot').forEach(function(s){{var c=s.querySelector('.card');c.style.transform='scale('+(s.clientWidth/1080)+')';}});}}
window.addEventListener('resize',fitCards);fitCards();
</script>
</body></html>"""
