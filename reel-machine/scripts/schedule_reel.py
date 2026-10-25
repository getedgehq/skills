#!/usr/bin/env python3
"""Schedule a finished reel to Instagram Reels, TikTok and YouTube Shorts through Buffer.

  schedule_reel.py channels
  schedule_reel.py schedule (--url URL | --file reel.mp4) --at 2026-11-02T12:00:00-08:00 \\
        --caption "post caption" --title "YouTube title" [--platforms instagram,tiktok,youtube] \\
        [--story] [--link https://your.landing/page] [--credits bundle/credits.txt] [--armed]
  schedule_reel.py swap --caption-start "first words of the caption" (--url URL | --file F) --title "YT title" [--days 35]

Auth: BUFFER_TOKEN in the environment (Buffer's GraphQL API at https://api.buffer.com/).
If different platforms sit in different Buffer accounts, set BUFFER_TOKEN_INSTAGRAM /
BUFFER_TOKEN_TIKTOK / BUFFER_TOKEN_YOUTUBE; each falls back to BUFFER_TOKEN.
Channels: BUFFER_<PLATFORM>_CHANNEL in config, a channel id or the channel's handle.

Media: Buffer has no upload; it fetches the file from a PUBLIC https URL when the post fires,
so the URL must stay reachable until then and serve byte ranges. --file uploads with
REEL_UPLOAD_CMD and builds the URL from REEL_PUBLIC_BASE_URL.

Platform requirements (Buffer rejects the post otherwise):
  Instagram: metadata.instagram = {type: "reel", shouldShareToFeed: true}
  YouTube:   metadata.youtube   = {title (<= 100 chars), categoryId, privacy, madeForKids, notifySubscribers}
  TikTok:    no metadata needed

Story: --story also creates an Instagram Story with the same video REEL_STORY_DELAY_MIN (60)
minutes after the reel (metadata.instagram.type = "story"): the reel gets a second push to
followers who watch Stories but not the feed.
Pace gate: --armed runs vadgaps.py on the exact file first (downloaded from the URL when only
--url is given) and refuses to arm a reel with dead air. --skip-pace-gate "reason" for a reel
without speech.

Safety: `schedule` creates DRAFTS unless --armed. Arm only after the owner approved the exact
file and caption. `swap` re-points already scheduled posts to a new file (same caption, time,
title), e.g. after a re-render, and only touches posts whose caption starts with --caption-start.
"""
import argparse, json, os, shlex, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmconf

API = "https://api.buffer.com/"
PLATFORMS = ("instagram", "tiktok", "youtube")
CP = """mutation($input: CreatePostInput!){ createPost(input:$input){ __typename
  ... on PostActionSuccess { post { id status dueAt channelId } }
  ... on InvalidInputError { message } ... on UnauthorizedError { message }
  ... on RestProxyError { message } ... on LimitReachedError { message }
  ... on UnexpectedError { message } ... on NotFoundError { message } } }"""
EP = CP.replace("CreatePostInput", "EditPostInput").replace("createPost", "editPost")
POSTS = """query($i: PostsInput!, $f: Int, $a: String){ posts(input:$i, first:$f, after:$a){
  pageInfo{ hasNextPage endCursor } edges{ node{ id status dueAt text channelId channelService
  assets{ __typename ... on ImageAsset { source } ... on VideoAsset { source } } } } } }"""


def token(platform):
    t = os.environ.get(f"BUFFER_TOKEN_{platform.upper()}") or os.environ.get("BUFFER_TOKEN")
    if not t:
        sys.exit(f"no Buffer token for {platform}: set BUFFER_TOKEN (or BUFFER_TOKEN_{platform.upper()})")
    return t


def call(platform, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": "Bearer " + token(platform),
                                                          "Content-Type": "application/json"})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"Buffer HTTP {e.code}: {e.read().decode()[:300]}")
    if not d.get("data"):  # Buffer answers errors with 200 and no data
        sys.exit(f"Buffer API error: {json.dumps(d)[:400]}")
    return d["data"]


_org, _chans = {}, {}


def org(platform):
    t = token(platform)
    if t not in _org:
        _org[t] = call(platform, "{ account { organizations { id name } } }")["account"]["organizations"][0]["id"]
    return _org[t]


def channels(platform):
    t = token(platform)
    if t not in _chans:
        _chans[t] = call(platform, '{ channels(input: {organizationId: "%s"}) { id service name } }' % org(platform))["channels"]
    return _chans[t]


def channel_id(platform):
    want = rmconf.get(f"BUFFER_{platform.upper()}_CHANNEL")
    cs = [c for c in channels(platform) if c["service"] == platform]
    hits = [c for c in cs if want in (c["id"], c["name"])] if want else cs
    if len(hits) != 1:
        names = ", ".join(f"{c['name']} ({c['id']})" for c in cs) or "none connected"
        sys.exit(f"{platform}: set BUFFER_{platform.upper()}_CHANNEL to one of: {names}")
    return hits[0]["id"]


def metadata(platform, title, story=False):
    if platform == "instagram":
        m = {"type": "story" if story else "reel", "shouldShareToFeed": True}
        collab = [c.strip().lstrip("@") for c in rmconf.get("BUFFER_IG_COLLAB").split(",") if c.strip()]
        if collab and not story:
            m["collaborators"] = collab  # shows on both profiles once the collaborator accepts in the app
        return {"instagram": m}
    if platform == "youtube":
        if not title:
            sys.exit("youtube needs --title (max 100 chars)")
        return {"youtube": {"title": title[:100], "categoryId": rmconf.get("YOUTUBE_CATEGORY_ID"), "privacy": "public",
                            "madeForKids": False, "notifySubscribers": True}}
    return {}


def public_url(a):
    if a.url:
        url = a.url
    else:
        cmd, base = rmconf.get("REEL_UPLOAD_CMD"), rmconf.get("REEL_PUBLIC_BASE_URL")
        if not (cmd and base):
            sys.exit("--file needs REEL_UPLOAD_CMD and REEL_PUBLIC_BASE_URL in config (or pass --url)")
        subprocess.run(cmd.replace("{file}", shlex.quote(a.file)), shell=True, check=True)
        url = base.rstrip("/") + "/" + os.path.basename(a.file)
    req = urllib.request.Request(url, method="HEAD")
    try:
        h = urllib.request.urlopen(req, timeout=30).headers
    except Exception as e:
        sys.exit(f"video not reachable at {url}: {e}")
    if h.get("Accept-Ranges", "").lower() != "bytes":
        print(f"WARNING: {url} does not advertise Accept-Ranges: bytes; platforms may fail to fetch it")
    return url


def check_text(*texts):
    for t in texts:
        if t and ("—" in t or "–" in t):
            sys.exit(f"em/en dash in: {t[:60]!r}")


def cmd_channels(_a):
    seen = set()
    for p in PLATFORMS:
        try:
            t = token(p)
        except SystemExit:
            continue
        if t in seen:
            continue
        seen.add(t)
        for c in channels(p):
            print(f"{c['service']:10s} {c['name']:30s} {c['id']}")


def pace_gate(a, url):
    """vadgaps.py on the exact file that will be posted; exits on FAIL."""
    if a.skip_pace_gate:
        print("pace gate skipped:", a.skip_pace_gate); return
    import tempfile
    f = a.file
    if not f:
        f = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        urllib.request.urlretrieve(url, f)
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "vadgaps.py"), f], capture_output=True, text=True)
    if not a.file:
        os.unlink(f)
    print(r.stdout.strip() or r.stderr.strip()[-300:])
    if r.returncode:
        sys.exit("pace gate FAILED: jump-cut it with pcut.py (or finish.sh) before arming")


def cmd_schedule(a):
    from datetime import datetime, timedelta
    caption = a.caption
    if a.link and a.link not in caption:
        caption = caption.rstrip() + "\n\n" + a.link
    if a.credits:
        caption = caption.rstrip() + "\n\n" + Path(a.credits).read_text().strip()
    check_text(caption, a.title)
    url = public_url(a)
    if a.armed:
        pace_gate(a, url)
    jobs = [(p, a.at, False) for p in a.platforms.split(",")]
    if a.story:
        later = (datetime.fromisoformat(a.at) + timedelta(minutes=int(rmconf.get("REEL_STORY_DELAY_MIN")))).isoformat()
        jobs.append(("instagram", later, True))
    for p, due, story in jobs:
        inp = {"channelId": channel_id(p), "text": caption, "assets": [{"video": {"url": url}}],
               "schedulingType": "automatic", "mode": "customScheduled", "dueAt": due}
        if not a.armed:
            inp["saveToDraft"] = True
        md = metadata(p, a.title, story)
        if md:
            inp["metadata"] = md
        r = call(p, CP, {"input": inp})["createPost"]
        post = r.get("post") or {}
        print(p + (" story" if story else ""), r["__typename"], post.get("id", ""), post.get("status", ""),
              post.get("dueAt", ""), r.get("message", ""))
    if not a.armed:
        print("Created as drafts. Re-run with --armed once the owner approved this exact file and caption.")


def cmd_swap(a):
    from datetime import datetime, timedelta, timezone
    url = public_url(a); n = 0
    for p in PLATFORMS:
        try:
            cid = channel_id(p)
        except SystemExit as e:
            print(f"skip {p}: {e}"); continue
        now = datetime.now(timezone.utc)
        inp = {"organizationId": org(p), "filter": {"channelIds": [cid], "dueAt": {
            "start": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "end": (now + timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")}},
               "sort": [{"field": "dueAt", "direction": "asc"}]}
        after, posts = None, []
        for _ in range(10):
            pg = call(p, POSTS, {"i": inp, "f": 100, "a": after})["posts"]
            posts += [e["node"] for e in pg["edges"]]
            if not pg["pageInfo"]["hasNextPage"]:
                break
            after = pg["pageInfo"]["endCursor"]
        hits = [q for q in posts if q.get("status") in (None, "scheduled") and (q.get("text") or "").startswith(a.caption_start)]
        # the Story reshare sits REEL_STORY_DELAY_MIN after its reel with the same caption: keep it a story
        due = {datetime.fromisoformat(q["dueAt"].replace("Z", "+00:00")) for q in hits}
        delay = timedelta(minutes=int(rmconf.get("REEL_STORY_DELAY_MIN")))
        for post in hits:
            story = p == "instagram" and datetime.fromisoformat(post["dueAt"].replace("Z", "+00:00")) - delay in due
            # editPost is a full replace: re-pass text, time and the platform metadata or they are lost
            e = {"id": post["id"], "text": post["text"], "assets": [{"video": {"url": url}}],
                 "dueAt": post["dueAt"], "mode": "customScheduled", "saveToDraft": False}
            md = metadata(p, a.title, story)
            if md:
                e["metadata"] = md
            r = call(p, EP, {"input": e})["editPost"]
            print(p, post["id"], post["dueAt"], r["__typename"], r.get("message", "")); n += 1
    print(n, "post(s) swapped")
    raise SystemExit(0 if n else 1)


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
sub.add_parser("channels")
for name in ("schedule", "swap"):
    s = sub.add_parser(name)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--url"); g.add_argument("--file")
    s.add_argument("--title", help="YouTube title, max 100 chars")
    if name == "schedule":
        s.add_argument("--at", required=True, help="ISO time with offset")
        s.add_argument("--caption", required=True)
        s.add_argument("--platforms", default=",".join(PLATFORMS))
        s.add_argument("--armed", action="store_true")
        s.add_argument("--story", action="store_true", help="also an Instagram Story, REEL_STORY_DELAY_MIN after the reel")
        s.add_argument("--link", help="landing page URL appended to the caption (product reels)")
        s.add_argument("--credits", help="credits.txt from the bundle (photo credits for cutaways)")
        s.add_argument("--skip-pace-gate", metavar="REASON", help="only for a reel without speech")
    else:
        s.add_argument("--caption-start", required=True)
        s.add_argument("--days", type=int, default=35)
a = ap.parse_args()
{"channels": cmd_channels, "schedule": cmd_schedule, "swap": cmd_swap}[a.cmd](a)
