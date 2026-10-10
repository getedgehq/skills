#!/usr/bin/env python3
"""Fetch your own recent X posts with the X API v2 and save them as JSON for x_growth_report.py.

Reads the bearer token from the X_BEARER_TOKEN environment variable (never pass it as an
argument or paste it into a chat). Calls only api.x.com, only these two read endpoints:
  GET /2/users/by/username/:username   (your follower count)
  GET /2/users/:id/tweets              (your posts with public metrics, up to 3,200)
X may bill these reads on your developer plan.

Usage:
    X_BEARER_TOKEN=... python3 fetch_x_posts.py USERNAME [--out posts.json] [--max 3200]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.x.com/2"
TWEET_FIELDS = "created_at,public_metrics,referenced_tweets,attachments,entities,note_tweet"


def get(path, params, token):
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"X API returned {e.code} for {path}: {e.read().decode(errors='replace')[:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username")
    ap.add_argument("--out", default="posts.json")
    ap.add_argument("--max", type=int, default=3200)
    a = ap.parse_args()
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        sys.exit("Set X_BEARER_TOKEN in your environment first.")
    me = get(f"/users/by/username/{a.username.lstrip('@')}", {"user.fields": "public_metrics,created_at"}, token)["data"]
    tweets, page = [], None
    while len(tweets) < a.max:
        params = {"max_results": 100, "tweet.fields": TWEET_FIELDS}
        if page:
            params["pagination_token"] = page
        res = get(f"/users/{me['id']}/tweets", params, token)
        tweets += res.get("data", [])
        page = res.get("meta", {}).get("next_token")
        if not page:
            break
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"me": me, "tweets": tweets[:a.max]}, f, ensure_ascii=False, indent=1)
    print(f"saved {len(tweets[:a.max])} posts for @{me['username']} to {a.out}")


if __name__ == "__main__":
    main()
