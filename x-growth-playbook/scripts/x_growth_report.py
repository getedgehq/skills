#!/usr/bin/env python3
"""X Growth Playbook report. Method by Federico De Ponte.

Reads your own X posts and writes report.md and report.json with the
breakdowns the skill asks for: post kind, quote vs original, external links,
length, time of day in your timezone, media, topic names, replies, top and
bottom posts, and posting activity. Every bucket carries its n and a flag when
it is too small to read. Runs fully on this computer: no network calls.

Accepted inputs (detected automatically):
  * X API v2 JSON: {"data": [...]}, {"tweets": [...]} or a plain list of posts
    with created_at, text, public_metrics (fetch_x_posts.py writes this).
  * The X data archive: data/tweets.js (or the archive folder / .zip).
  * A CSV, for pasted posts or numbers read off screenshots. Columns (any
    order, header names are matched loosely): date, text, impressions, likes,
    replies, reposts, and optionally kind (original / quote / reply / repost)
    and media (yes / no).

Usage:
    python3 x_growth_report.py INPUT --tz Europe/Berlin [--out DIR]
        [--topic "Claude=claude|opus"] [--topic ...] [--metric impressions|likes]
"""
import argparse
import csv
import datetime as dt
import html
import io
import json
import os
import re
import statistics
import sys
import zipfile
from zoneinfo import ZoneInfo

TOO_FEW = 5   # fewer posts than this: too few to conclude anything
HINT = 10     # fewer than this: a hint, not a result
TCO = re.compile(r"https?://t\.co/\w+")
STATUS_URL = re.compile(r"https?://(?:www\.|mobile\.)?(?:twitter|x)\.com/\w+/status/\d+", re.I)
TIME_BUCKETS = [(0, 6, "00:00-05:59"), (6, 12, "06:00-11:59"), (12, 17, "12:00-16:59"), (17, 24, "17:00-23:59")]
LENGTH_BUCKETS = [(0, 140, "under 140 characters"), (140, 281, "140 to 280 characters"),
                  (281, 10 ** 9, "over 280 characters")]


# ---------- loading ----------

def read_input(path):
    """Return (posts, account, source label, notes). Each post is a normalized dict."""
    notes = []
    if os.path.isdir(path):
        for cand in ("data/tweets.js", "tweets.js", "data/tweet.js"):
            if os.path.exists(os.path.join(path, cand)):
                return read_archive(open(os.path.join(path, cand), encoding="utf-8").read(), notes)
        sys.exit(f"No data/tweets.js in {path}. Point to the unzipped X archive folder or its tweets.js file.")
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.endswith(("data/tweets.js", "data/tweet.js"))]
            if not names:
                sys.exit("This zip has no data/tweets.js. Is it the X data archive?")
            return read_archive(z.read(names[0]).decode("utf-8"), notes)
    raw = open(path, encoding="utf-8-sig").read()
    if path.lower().endswith(".js") or raw.lstrip().startswith("window.YTD"):
        return read_archive(raw, notes)
    if path.lower().endswith((".csv", ".tsv", ".txt")):
        return read_csv(raw, notes)
    return read_api(json.loads(raw), notes)


def read_api(doc, notes):
    account = None
    if isinstance(doc, dict):
        account = doc.get("me") or (doc.get("includes", {}).get("users") or [None])[0]
        items = doc.get("tweets") or doc.get("data") or []
    else:
        items = doc
    posts = []
    for x in items:
        refs = {r.get("type") for r in x.get("referenced_tweets") or []}
        text = (x.get("note_tweet") or {}).get("text") or x.get("text", "")
        m = x.get("public_metrics") or {}
        urls = (x.get("entities") or {}).get("urls")
        has_media = bool((x.get("attachments") or {}).get("media_keys"))
        kind = ("reply" if "replied_to" in refs else "repost" if "retweeted" in refs
                else "quote" if "quoted" in refs else "original")
        if urls is not None:
            ext = any(not STATUS_URL.match(u.get("expanded_url") or "") and not u.get("media_key")
                      and "/photo/" not in (u.get("expanded_url") or "") and "/video/" not in (u.get("expanded_url") or "")
                      for u in urls)
        else:
            ext = None
        posts.append(dict(id=str(x.get("id", "")), created=parse_time(x["created_at"]), text=html.unescape(text),
                          kind=kind, media=has_media, ext_link=ext, truncated_text=not x.get("note_tweet"),
                          impressions=m.get("impression_count"), likes=m.get("like_count"),
                          replies=m.get("reply_count"), reposts=m.get("retweet_count"),
                          quotes=m.get("quote_count"), bookmarks=m.get("bookmark_count")))
    if posts and all(p["ext_link"] is None for p in posts):
        notes.append("The file has no link details (entities), so a post counts as having an external link when it "
                     "has a t.co link besides the one X adds for attached media and the one for a quoted post.")
    if posts and not any((x.get("note_tweet") for x in items)):
        notes.append("No long-post text (note_tweet) in the file: posts over 280 characters are cut at about 280 "
                     "and end in a t.co link, which X counts as 23 characters. They still land in the "
                     "'over 280 characters' bucket.")
    return posts, account, "X API v2 JSON", notes


def read_archive(raw, notes):
    items = json.loads(raw[raw.index("["):])
    posts = []
    for it in items:
        x = it.get("tweet", it)
        text = html.unescape(x.get("full_text") or x.get("text") or "")
        ent = x.get("entities") or {}
        urls = [u.get("expanded_url") or "" for u in ent.get("urls") or []]
        has_media = bool((x.get("extended_entities") or ent).get("media"))
        if text.startswith("RT @"):
            kind = "repost"
        elif x.get("in_reply_to_status_id_str") or x.get("in_reply_to_status_id"):
            kind = "reply"
        elif any(STATUS_URL.match(u) for u in urls):
            kind = "quote"
        else:
            kind = "original"
        posts.append(dict(id=str(x.get("id_str") or x.get("id")), created=parse_time(x["created_at"]), text=text,
                          kind=kind, media=has_media, ext_link=any(not STATUS_URL.match(u) for u in urls),
                          truncated_text=False, impressions=None, likes=to_int(x.get("favorite_count")),
                          replies=None, reposts=to_int(x.get("retweet_count")), quotes=None, bookmarks=None))
    notes.append("The X data archive has no impressions and no reply counts per post: results use likes. Likes "
                 "measure reactions, not reach. For reach, export your post analytics from X or use the API.")
    return posts, None, "X data archive (tweets.js)", notes


def read_csv(raw, notes):
    dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    rows = list(csv.DictReader(io.StringIO(raw), dialect=dialect))
    if not rows:
        sys.exit("The CSV has no rows.")

    def col(*names):
        for h in rows[0]:
            k = re.sub(r"[^a-z]", "", (h or "").lower())
            if any(k == n or k.startswith(n) for n in names):
                return h
        return None
    c = dict(date=col("date", "time", "createdat", "posted"), text=col("text", "post", "content", "tweet"),
             imp=col("impressions", "views", "impression"), likes=col("likes", "like"),
             replies=col("replies", "reply"), reposts=col("reposts", "retweets", "repost"),
             kind=col("kind", "type"), media=col("media", "hasmedia"))
    if not c["date"] or not c["text"]:
        sys.exit(f"The CSV needs a date column and a text column. Found: {list(rows[0])}")
    posts = []
    for i, r in enumerate(rows):
        text = r[c["text"]] or ""
        kind = (r.get(c["kind"]) or "").strip().lower() if c["kind"] else ""
        kind = {"retweet": "repost", "rt": "repost"}.get(kind, kind)
        if kind not in ("original", "quote", "reply", "repost"):
            kind = "reply" if text.startswith("@") else "original"
        media = (r.get(c["media"]) or "").strip().lower() in ("yes", "y", "true", "1") if c["media"] else None
        posts.append(dict(id=str(i + 1), created=parse_time(r[c["date"]]), text=text, kind=kind, media=media,
                          ext_link=bool(re.search(r"https?://", text)) and not STATUS_URL.search(text),
                          truncated_text=False, impressions=to_int(r.get(c["imp"])) if c["imp"] else None,
                          likes=to_int(r.get(c["likes"])) if c["likes"] else None,
                          replies=to_int(r.get(c["replies"])) if c["replies"] else None,
                          reposts=to_int(r.get(c["reposts"])) if c["reposts"] else None, quotes=None, bookmarks=None))
    if not c["kind"]:
        notes.append("No kind column: posts starting with @ count as replies, all others as originals.")
    if not c["media"]:
        notes.append("No media column: the media breakdown is skipped.")
    return posts, None, "CSV", notes


def to_int(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().lower().replace(",", "").replace(" ", "")
    mult = 1000 if s.endswith("k") else 1_000_000 if s.endswith("m") else 1
    try:
        return int(round(float(s.rstrip("km")) * mult))
    except ValueError:
        return None


def parse_time(s):
    s = str(s).strip()
    for fmt in ("%a %b %d %H:%M:%S %z %Y",):
        try:
            return dt.datetime.strptime(s, fmt)
        except ValueError:
            pass
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(f"Cannot read the date {s!r}. Use ISO dates like 2026-09-16T14:05:00Z.")
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


# ---------- measuring ----------

def x_length(text):
    """Length the way X counts it: each link is 23, most emoji and CJK characters are 2."""
    n = 23 * len(TCO.findall(text)) + 23 * len(re.findall(r"https?://(?!t\.co/)\S+", text))
    rest = re.sub(r"https?://\S+", "", text)
    for ch in rest:
        o = ord(ch)
        n += 1 if (o <= 0x10FF or 0x2000 <= o <= 0x200D or 0x2010 <= o <= 0x201F or 0x2032 <= o <= 0x2037) else 2
    return n


def ext_link(p):
    if p["ext_link"] is not None:
        return p["ext_link"]
    n = len(TCO.findall(p["text"])) - (1 if p["media"] else 0) - (1 if p["kind"] == "quote" else 0)
    return n > 0


def median(vals):
    return statistics.median(vals) if vals else None


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.1f}"
    return f"{int(v):,}"


def flag(n):
    if n < TOO_FEW:
        return f"too few posts to conclude anything (n = {n})"
    if n < HINT:
        return f"a hint, not a result (n = {n})"
    return ""


def bucket(name, posts, metric):
    vals = [p[metric] for p in posts if p[metric] is not None]
    return dict(bucket=name, n=len(vals), median=median(vals), flag=flag(len(vals)))


def compare(title, a_name, a, b_name, b, metric):
    A, B = bucket(a_name, a, metric), bucket(b_name, b, metric)
    ratio = (A["median"] / B["median"]) if A["median"] and B["median"] else None
    return dict(title=title, rows=[A, B], ratio=ratio)


def snippet(text, k=90):
    t = re.sub(r"\s+", " ", TCO.sub("", text)).strip()
    return t if len(t) <= k else t[:k - 1].rstrip() + "…"


# ---------- report ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--tz", required=True, help="the user's timezone, e.g. America/Los_Angeles")
    ap.add_argument("--out", default=None)
    ap.add_argument("--topic", action="append", default=[], help='"Name=regex", case-insensitive; repeatable')
    ap.add_argument("--metric", choices=["impressions", "likes"], default=None)
    a = ap.parse_args()
    tz = ZoneInfo(a.tz)
    posts, account, source, notes = read_input(a.input)
    if not posts:
        sys.exit("No posts found in the input.")
    metric = a.metric or ("impressions" if any(p["impressions"] is not None for p in posts) else "likes")
    for p in posts:
        p["local"] = p["created"].astimezone(tz)
    reposts = [p for p in posts if p["kind"] == "repost"]
    replies = [p for p in posts if p["kind"] == "reply"]
    top = [p for p in posts if p["kind"] in ("original", "quote")]
    if len(top) < 20:
        notes.append(f"Only {len(top)} posts that are not replies or reposts: every breakdown below is small. "
                     "Treat it as a first look and come back with more posts.")

    comps = [
        compare("Quote posts vs original posts", "quote posts", [p for p in top if p["kind"] == "quote"],
                "original posts", [p for p in top if p["kind"] == "original"], metric),
        compare("External link in the post", "with an external link", [p for p in top if ext_link(p)],
                "without one", [p for p in top if not ext_link(p)], metric),
    ]
    if any(p["media"] is not None for p in top):
        comps.append(compare("Media (image or video) vs text only", "with media", [p for p in top if p["media"]],
                             "text only", [p for p in top if p["media"] is False], metric))
    for spec in a.topic:
        name, _, rx = spec.partition("=")
        r = re.compile(rx or re.escape(name), re.I)
        comps.append(compare(f"Topic: {name}", f"mentions {name}", [p for p in top if r.search(p["text"])],
                             f"does not mention {name}", [p for p in top if not r.search(p["text"])], metric))

    tables = {
        "Length (counted the way X counts it)": [
            bucket(lbl, [p for p in top if lo <= x_length(p["text"]) < hi], metric) for lo, hi, lbl in LENGTH_BUCKETS],
        f"Time of day ({a.tz})": [
            bucket(lbl, [p for p in top if lo <= p["local"].hour < hi], metric) for lo, hi, lbl in TIME_BUCKETS],
    }

    ranked = sorted([p for p in top if p[metric] is not None], key=lambda p: p[metric], reverse=True)
    days = {}
    for p in posts:
        days[p["local"].date()] = days.get(p["local"].date(), 0) + 1
    d0, d1 = min(days), max(days)
    best7 = max(((d0 + dt.timedelta(i), sum(days.get(d0 + dt.timedelta(i + k), 0) for k in range(7)))
                 for i in range((d1 - d0).days + 1)), key=lambda t: t[1])
    weeks = {}
    for p in posts:
        y, w, _ = p["local"].isocalendar()
        weeks.setdefault(f"{y}-W{w:02d}", []).append(p)

    def row(p):
        return dict(id=p["id"], date=p["local"].strftime("%Y-%m-%d %H:%M"), kind=p["kind"], metric=p[metric],
                    replies=p["replies"], likes=p["likes"], text=snippet(p["text"]))

    rep = dict(source=source, timezone=a.tz, metric=metric, account=account, notes=notes,
               counts=dict(total=len(posts), original=sum(p["kind"] == "original" for p in posts),
                           quote=sum(p["kind"] == "quote" for p in posts), reply=len(replies), repost=len(reposts)),
               first=min(p["local"] for p in posts).isoformat(), last=max(p["local"] for p in posts).isoformat(),
               top_level=bucket("original and quote posts", top, metric),
               replies=bucket("replies", replies, metric),
               comparisons=comps, tables=tables,
               top_posts=[row(p) for p in ranked[:10]], bottom_posts=[row(p) for p in ranked[-5:][::-1]],
               most_replied=[row(p) for p in sorted([p for p in posts if p["replies"] is not None],
                                                    key=lambda p: p["replies"], reverse=True)[:5]],
               busiest_7_days=dict(start=best7[0].isoformat(), end=(best7[0] + dt.timedelta(6)).isoformat(),
                                   posts=best7[1]),
               weeks=[dict(week=k, posts=len(v), median_top_level=median(
                   [p[metric] for p in v if p["kind"] in ("original", "quote") and p[metric] is not None]))
                   for k, v in sorted(weeks.items())])

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.input)), "x-growth-output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write(render(rep))
    print(f"wrote {out}/report.md and report.json ({len(posts)} posts, metric: {metric})")


def render(r):
    m = r["metric"]
    L = ["# X growth report", "",
         f"Source: {r['source']}. Timezone: {r['timezone']}. Numbers are median {m} per post.", ""]
    if r["account"]:
        pm = r["account"].get("public_metrics") or {}
        L += [f"Account: @{r['account'].get('username')} with {fmt(pm.get('followers_count'))} followers when the "
              "file was made.", ""]
    if r["notes"]:
        L += ["## Notes from reading the file", ""] + [f"- {n}" for n in r["notes"]] + [""]
    c = r["counts"]
    L += ["## What is in the file", "",
          f"{c['total']} posts from {r['first'][:10]} to {r['last'][:10]}: {c['original']} original, {c['quote']} "
          f"quote, {c['reply']} replies, {c['repost']} reposts. Reposts are left out of every number below.", "",
          f"Original and quote posts (n = {r['top_level']['n']}): median {fmt(r['top_level']['median'])} {m}. "
          f"Replies (n = {r['replies']['n']}): median {fmt(r['replies']['median'])} {m}.", "",
          "All breakdowns below use original and quote posts only.", ""]
    L += ["## Two-way comparisons", "", f"| Comparison | Group | n | Median {m} | Ratio | Flag |", "|---|---|---|---|---|---|"]
    for cp in r["comparisons"]:
        a, b = cp["rows"]
        ratio = f"{cp['ratio']:.1f}x" if cp["ratio"] else "-"
        L.append(f"| {cp['title']} | {a['bucket']} | {a['n']} | {fmt(a['median'])} | {ratio} | {a['flag']} |")
        L.append(f"| | {b['bucket']} | {b['n']} | {fmt(b['median'])} | | {b['flag']} |")
    for title, rows in r["tables"].items():
        L += ["", f"## {title}", "", f"| Bucket | n | Median {m} | Flag |", "|---|---|---|---|"]
        L += [f"| {x['bucket']} | {x['n']} | {fmt(x['median'])} | {x['flag']} |" for x in rows]

    def plist(title, rows):
        out = ["", f"## {title}", "", f"| Date | Kind | {m.capitalize()} | Replies | Post |", "|---|---|---|---|---|"]
        return out + [f"| {p['date']} | {p['kind']} | {fmt(p['metric'])} | {fmt(p['replies'])} | {p['text'].replace('|', '/')} |"
                      for p in rows]
    L += plist(f"Top 10 posts by {m}", r["top_posts"])
    L += plist(f"Bottom 5 posts by {m}", r["bottom_posts"])
    if r["most_replied"]:
        L += plist("Most replied-to posts (all kinds)", r["most_replied"])
    b = r["busiest_7_days"]
    L += ["", "## Activity", "", f"Busiest 7 days: {b['start']} to {b['end']}, {b['posts']} posts (all kinds).", "",
          f"| Week | Posts | Median {m}, original and quote |", "|---|---|---|"]
    L += [f"| {w['week']} | {w['posts']} | {fmt(w['median_top_level'])} |" for w in r["weeks"]]
    L += ["", "Follower history is not in this file. Ask the user for their follower count at the start and end "
          "of a busy stretch before saying anything about growth.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
