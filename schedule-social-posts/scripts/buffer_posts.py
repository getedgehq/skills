#!/usr/bin/env python3
"""Schedule LinkedIn, X, Threads, Bluesky, Instagram, TikTok and YouTube posts through Buffer's GraphQL API.

  buffer_posts.py channels
  buffer_posts.py queue [--days 14]
  buffer_posts.py slots --channel <handle|id> [--days 14] [--cap 1]
  buffer_posts.py schedule --channel <handle|id> --text-file post.txt --at 2026-11-03T08:00:00-08:00 \\
        [--comment "first comment or X reply"]... [--image URL[,URL]] [--video URL] [--reel] [--title "YouTube title"] \\
        [--cap 1] [--armed] [--dry-run]
  buffer_posts.py delete --id <postId>
  buffer_posts.py analytics [--days 30]

Auth: BUFFER_TOKEN in the environment (create it in Buffer's settings; https://api.buffer.com/ only).
Never pass the token as an argument or print it.
Approval: schedule saves a DRAFT unless --armed. Arm only the exact text the owner approved.
There is no publish-now command on purpose: posts go into a real slot.
Media: Buffer has no upload; it fetches the file from a public https URL when the post fires."""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.buffer.com/"
FIRST_COMMENT = {"linkedin", "instagram", "facebook"}
THREAD = {"twitter", "bluesky", "threads", "mastodon"}
CP = """mutation($input: CreatePostInput!){ createPost(input:$input){ __typename
  ... on PostActionSuccess { post { id status dueAt channelId } }
  ... on InvalidInputError { message } ... on UnauthorizedError { message }
  ... on RestProxyError { message } ... on LimitReachedError { message }
  ... on UnexpectedError { message } ... on NotFoundError { message } } }"""
Q = """query($i: PostsInput!, $f: Int){ posts(input:$i, first:$f){ edges{ node{
  id status dueAt text channelService channel{ id name } } } } }"""
AGG = """query($i: AggregatedPostMetricsInput!){ aggregatedPostMetrics(input:$i){ metrics{ name value unit } } }"""


def call(query, variables=None):
    tok = os.environ.get("BUFFER_TOKEN")
    if not tok:
        raise SystemExit("BUFFER_TOKEN is not set. Create a token in Buffer and export it in your own terminal.")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Buffer HTTP {e.code}: {e.read().decode()[:300]}")
    if out.get("errors") or out.get("data") is None:
        # Buffer answers many errors with HTTP 200 and no data. Never read that as an empty result.
        raise SystemExit(f"Buffer error: {json.dumps(out.get('errors'))[:400]}")
    return out["data"]


_ORG, _CH = [], []


def org():
    if not _ORG:
        _ORG.append(call("{ account { organizations { id name } } }")["account"]["organizations"][0]["id"])
    return _ORG[0]


def channels():
    if not _CH:
        _CH.extend(call('{ channels(input: {organizationId: %s}) { id service name } }' % json.dumps(org()))["channels"])
    return _CH


def resolve(ch):
    cs = channels()
    hits = [c for c in cs if ch in (c["id"], c["name"])] or [c for c in cs if c["service"] == ch]
    if not hits:
        raise SystemExit(f"channel {ch!r} not found; run `channels`")
    if len(hits) > 1:
        raise SystemExit(f"{ch!r} is ambiguous: " + ", ".join(f"{c['name']} ({c['service']}, {c['id']})" for c in hits))
    return hits[0]


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def queue(days, lookback_h=24, ids=None):
    now = dt.datetime.now(dt.timezone.utc)
    inp = {"organizationId": org(),
           "filter": {"channelIds": ids or [c["id"] for c in channels()],
                      "dueAt": {"start": iso(now - dt.timedelta(hours=lookback_h)), "end": iso(now + dt.timedelta(days=days))}},
           "sort": [{"field": "dueAt", "direction": "asc"}]}
    rows = [e["node"] for e in call(Q, {"i": inp, "f": 100})["posts"]["edges"]]   # Buffer refuses first > 100
    if len(rows) == 100:
        # Later days would look empty. A cap check on a cut-off queue is how double posts get scheduled.
        raise SystemExit("queue read hit Buffer's 100-post page limit; use a shorter --days window")
    return rows


def day_counts(cid, days):
    out = {}
    for p in queue(days, ids=[cid]):
        if p.get("dueAt") and p.get("status") not in ("error",):
            out.setdefault(p["dueAt"][:10], []).append(p)   # drafts count as taken: they are reservations
    return out


def build_input(c, text, at, comments, image, video, reel, title, armed):
    assets = [{"video": {"url": video}}] if video else [{"image": {"url": u.strip()}} for u in (image or "").split(",") if u.strip()]
    inp = {"channelId": c["id"], "text": text, "assets": assets, "schedulingType": "automatic",
           "mode": "customScheduled", "dueAt": at}
    if not armed:
        inp["saveToDraft"] = True
    meta, svc = {}, c["service"]
    if comments:
        if svc in FIRST_COMMENT:
            meta[svc] = {"firstComment": "\n\n".join(comments)}
        elif svc in THREAD:
            # Buffer's thread is the whole list, main post first; a thread with only the reply drops the main post.
            meta[svc] = {"thread": [{"text": text, "assets": assets}] + [{"text": x} for x in comments]}
        else:
            raise SystemExit(f"--comment is not supported on {svc}")
    if svc == "instagram":
        meta.setdefault("instagram", {}).update({"type": "reel" if (reel or video) else "post", "shouldShareToFeed": True})
    if svc == "youtube":
        if not title:
            raise SystemExit("YouTube needs --title")
        meta["youtube"] = {"title": title[:100], "categoryId": "28", "privacy": "public", "madeForKids": False, "notifySubscribers": True}
    if meta:
        inp["metadata"] = meta
    return inp


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("channels")
    q = sub.add_parser("queue"); q.add_argument("--days", type=int, default=14)
    s = sub.add_parser("slots"); s.add_argument("--channel", required=True); s.add_argument("--days", type=int, default=14); s.add_argument("--cap", type=int, default=1)
    sc = sub.add_parser("schedule")
    sc.add_argument("--channel", required=True); sc.add_argument("--text-file", required=True); sc.add_argument("--at", required=True)
    sc.add_argument("--comment", action="append", default=[]); sc.add_argument("--image"); sc.add_argument("--video")
    sc.add_argument("--reel", action="store_true"); sc.add_argument("--title"); sc.add_argument("--cap", type=int, default=1)
    sc.add_argument("--armed", action="store_true"); sc.add_argument("--dry-run", action="store_true")
    d = sub.add_parser("delete"); d.add_argument("--id", required=True)
    an = sub.add_parser("analytics"); an.add_argument("--days", type=int, default=30)
    a = ap.parse_args()

    if a.cmd == "channels":
        for c in channels():
            print(f"{c['service']:10} {c['name']:30} {c['id']}")
    elif a.cmd == "queue":
        names = {c["id"]: f"{c['service']}/{c['name']}" for c in channels()}
        for p in queue(a.days):
            print(f"{p['dueAt']}  {p['status']:9} {names.get((p.get('channel') or {}).get('id'), p.get('channelService')):28} {p['id']}  {(p['text'] or '')[:60]!r}")
    elif a.cmd == "slots":
        c = resolve(a.channel); counts = day_counts(c["id"], a.days)
        today = dt.date.today()
        for i in range(a.days):
            day = (today + dt.timedelta(days=i)).isoformat(); n = len(counts.get(day, []))
            print(f"{day}  {n}/{a.cap}  {'open' if n < a.cap else 'FULL'}")
    elif a.cmd == "schedule":
        c = resolve(a.channel)
        text = open(a.text_file).read().strip()
        at = dt.datetime.fromisoformat(a.at)
        if at.tzinfo is None:
            raise SystemExit("--at needs a timezone offset, for example 2026-11-03T08:00:00-08:00")
        if at <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10):
            raise SystemExit("--at must be at least 10 minutes in the future: posts go into a slot, never out on the spot")
        if c["service"] == "twitter" and len(text) > 280:
            raise SystemExit(f"X main post is {len(text)} characters (max 280)")
        if (a.image or a.video) and not all(u.strip().startswith("https://") for u in (a.video or a.image).split(",")):
            raise SystemExit("media must be public https URLs")
        inp = build_input(c, text, iso(at), a.comment, a.image, a.video, a.reel, a.title, a.armed)
        taken = day_counts(c["id"], (at.date() - dt.date.today()).days + 1).get(iso(at)[:10], [])
        if len(taken) >= a.cap:
            raise SystemExit(f"{iso(at)[:10]} already has {len(taken)} post(s) on {c['name']} (cap {a.cap}). Pick an open day from `slots`.")
        if a.dry_run:
            print(json.dumps(inp, indent=2, ensure_ascii=False)); return
        r = call(CP, {"input": inp})["createPost"]
        if r["__typename"] != "PostActionSuccess":
            raise SystemExit(f"Buffer refused: {r}")
        p = r["post"]
        print(f"{'ARMED' if a.armed else 'DRAFT'} {p['id']} {c['service']}/{c['name']} at {p['dueAt']} status={p['status']}")
    elif a.cmd == "delete":
        print(call("mutation($i: DeletePostInput!){ deletePost(input:$i){ __typename } }", {"i": {"id": a.id}}))
    elif a.cmd == "analytics":
        end = dt.datetime.now(dt.timezone.utc); start = end - dt.timedelta(days=a.days)
        for c in channels():
            inp = {"organizationId": org(), "channelIds": [c["id"]], "startDateTime": iso(start), "endDateTime": iso(end)}
            try:
                ms = call(AGG, {"i": inp})["aggregatedPostMetrics"]["metrics"]
            except SystemExit as e:
                print(f"{c['service']}/{c['name']}: {e}"); continue
            print(f"{c['service']}/{c['name']:24} " + "  ".join(f"{m['name']}={m['value']}{'%' if m['unit'] == 'percentage' else ''}" for m in ms))


if __name__ == "__main__":
    main()
