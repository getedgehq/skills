#!/usr/bin/env python3
"""Small, account-neutral Buffer GraphQL helper. Standard library only."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def call(query, variables=None):
    endpoint = os.environ.get("BUFFER_GRAPHQL_URL")
    token = os.environ.get("BUFFER_TOKEN")
    if not endpoint or not token:
        raise RuntimeError("Set BUFFER_GRAPHQL_URL and BUFFER_TOKEN in the process environment")
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(endpoint, data=payload, headers={
        "Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Buffer HTTP {exc.code}; check authentication or rate limit") from exc
    if result.get("errors") or result.get("data") is None:
        raise RuntimeError("Buffer GraphQL error: " + json.dumps(result.get("errors", result))[:500])
    return result["data"]


def channels():
    account = call("{ account { organizations { id } } }")["account"]
    organizations = account.get("organizations") or []
    if len(organizations) != 1:
        raise RuntimeError("Expected one organization; select an organization explicitly before using this helper")
    org_id = organizations[0]["id"]
    result = call("{ channels(input:{organizationId:" + json.dumps(org_id) + "}) { id name service } }")
    return result["channels"]


def create(args):
    available = channels()
    matches = [c for c in available if c["id"] == args.channel]
    if len(matches) != 1:
        raise RuntimeError("Channel ID was not found; run channels and use an exact ID")
    service = matches[0]["service"]
    text = Path(args.text_file).read_text().strip()
    if not text:
        raise RuntimeError("Text file is empty")
    assets = ([{"video": {"url": args.video}}] if args.video else
              [{"image": {"url": args.image}}] if args.image else [])
    metadata = {}
    if args.comment:
        if service == "twitter":
            metadata["twitter"] = {"thread": [
                {"text": text, "assets": assets}, {"text": args.comment, "assets": []}]}
        elif service in ("linkedin", "instagram", "facebook"):
            metadata[service] = {"firstComment": args.comment}
        else:
            raise RuntimeError(f"A follow-up comment is unsupported for {service}")
    if service == "instagram":
        metadata.setdefault("instagram", {}).update({
            "type": "reel" if args.video else "post", "shouldShareToFeed": True})
    if service not in ("twitter", "linkedin", "instagram", "facebook"):
        raise RuntimeError(f"This helper has no validated create metadata for {service}")
    post_input = {"channelId": args.channel, "text": text, "assets": assets,
                  "schedulingType": "automatic", "mode": "customScheduled",
                  "dueAt": args.at, "saveToDraft": not args.armed}
    if metadata:
        post_input["metadata"] = metadata
    if not args.armed:
        print("Creating a draft; nothing is armed to publish", file=sys.stderr)
    result = call("""mutation($input:CreatePostInput!){ createPost(input:$input){
      __typename ... on PostActionSuccess { post { id status dueAt channelId } }
      ... on MutationError { message } } }""", {"input": post_input})["createPost"]
    if result.get("__typename") != "PostActionSuccess":
        raise RuntimeError("Create failed: " + json.dumps(result))
    print(json.dumps(result["post"], indent=2))
    print("Read the post back and inspect network delivery before reporting completion", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("channels", help="List exact channel IDs")
    p = sub.add_parser("create", help="Create a draft by default; --armed schedules it")
    p.add_argument("--channel", required=True, help="Exact channel ID from channels")
    p.add_argument("--text-file", required=True)
    p.add_argument("--at", required=True, help="ISO 8601 due time with timezone")
    media = p.add_mutually_exclusive_group()
    media.add_argument("--image", help="Public image URL")
    media.add_argument("--video", help="Public video URL")
    p.add_argument("--comment", help="First comment or self reply")
    p.add_argument("--armed", action="store_true", help="Schedule the exact copy now")
    args = parser.parse_args()
    try:
        if args.command == "channels":
            print(json.dumps(channels(), indent=2))
        else:
            create(args)
    except (RuntimeError, OSError, KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
