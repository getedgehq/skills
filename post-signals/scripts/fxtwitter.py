#!/usr/bin/env python3
"""Read the public stats of X posts through the free fxtwitter API (api.fxtwitter.com). No key, no account.

  python3 fxtwitter.py https://x.com/user/status/123 [more urls or ids] [--csv posts.csv]

Prints one line per post; --csv appends rows in the post-signals posts.csv format (header written once).
Only public posts are readable. Numbers are whatever X shows at the time of the call."""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://api.fxtwitter.com/status/{}"
HEADER = ["platform", "author", "url", "date", "text", "views", "likes", "comments", "reposts", "saves", "followers", "format", "source"]


def post_id(s):
    m = re.search(r"/status(?:es)?/(\d+)", s) or re.fullmatch(r"\s*(\d{5,25})\s*", s)
    if not m:
        raise SystemExit(f"not an X post url or id: {s!r}")
    return m.group(1)


def fetch(pid):
    req = urllib.request.Request(API.format(pid), headers={"User-Agent": "post-signals/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    t = d.get("tweet")
    if d.get("code") != 200 or not t:
        return None, d.get("message") or "not found"
    return t, ""


def fmt(t):
    if t.get("quote"):
        return "quote"
    media = (t.get("media") or {})
    if media.get("videos"):
        return "video"
    if media.get("photos"):
        return "image" if len(media["photos"]) == 1 else "carousel"
    if t.get("poll"):
        return "poll"
    return "text"


def row(t):
    a = t.get("author") or {}
    ts = t.get("created_timestamp")
    date = dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else ""
    return {"platform": "x", "author": a.get("screen_name", ""), "url": t.get("url", ""), "date": date,
            "text": (t.get("text") or "").replace("\r", ""), "views": t.get("views") if t.get("views") is not None else "",
            "likes": t.get("likes", ""), "comments": t.get("replies", ""), "reposts": (t.get("retweets") or 0) + (t.get("quotes") or 0),
            "saves": t.get("bookmarks", ""), "followers": a.get("followers", ""), "format": fmt(t), "source": "fxtwitter"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--csv")
    a = ap.parse_args()
    rows = []
    for i, s in enumerate(a.posts):
        if i:
            time.sleep(1)   # be polite to a free service
        t, err = fetch(post_id(s))
        if not t:
            print(f"SKIP {s}: {err}", file=sys.stderr)
            continue
        r = row(t)
        rows.append(r)
        line1 = r["text"].strip().splitlines()[0][:80] if r["text"].strip() else ""
        print(f'@{r["author"]} {r["date"][:10]} views={r["views"] or "?"} likes={r["likes"]} replies={r["comments"]} '
              f'reposts={r["reposts"]} saves={r["saves"]} {r["format"]} | {line1}')
    if a.csv and rows:
        new = not os.path.exists(a.csv) or os.path.getsize(a.csv) == 0
        with open(a.csv, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            if new:
                w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} rows -> {a.csv}")


if __name__ == "__main__":
    main()
