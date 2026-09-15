#!/usr/bin/env python3
import argparse, csv, json, os, sys, urllib.request

FIELDS = ("name", "current_title", "current_company", "location", "profile_url", "evidence_url")

def words(value):
    return [x.strip().lower() for x in (value or "").split(",") if x.strip()]

def plan(args):
    return {
        "objective": args.objective,
        "must_have": {"locations": words(args.locations), "current_titles": words(args.titles), "keywords": words(args.must_keywords)},
        "preferences": {"keywords": words(args.prefer_keywords)},
        "limits": {"requested_results": args.limit, "max_cost_usd": args.max_cost_usd},
    }

def score(row, search):
    haystack = " ".join(str(row.get(k, "")) for k in FIELDS).lower()
    hard = search["must_have"]
    checks = []
    for key, values in (("locations", hard["locations"]), ("titles", hard["current_titles"]), ("keywords", hard["keywords"])):
        if values:
            checks.append((key, any(v in haystack for v in values)))
    if any(not ok for _, ok in checks):
        return None
    prefs = search["preferences"]["keywords"]
    matched = [v for v in prefs if v in haystack]
    return {"score": len(matched), "matched_preferences": matched, "hard_checks": dict(checks)}

def rank_rows(rows, search):
    seen, ranked = set(), []
    for row in rows:
        key = (row.get("profile_url") or f'{row.get("name", "").lower()}|{row.get("current_company", "").lower()}').strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result = score(row, search)
        if result is not None:
            ranked.append({**{k: row.get(k, "") for k in FIELDS}, **result})
    return sorted(ranked, key=lambda x: (-x["score"], x["name"]))[:search["limits"]["requested_results"]]

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def provider_request(args, search):
    if not args.endpoint:
        raise ValueError("provider mode requires --endpoint")
    token = os.environ.get(args.token_env)
    if not token:
        raise ValueError(f"provider credential unavailable in {args.token_env}")
    payload = json.dumps({"query": search, "limit": min(args.limit, 5), "preview": True}).encode()
    request = urllib.request.Request(args.endpoint, data=payload, method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.load(response)
    return body.get("results", body if isinstance(body, list) else [])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "import", "provider"), default="plan")
    parser.add_argument("--objective", default="research")
    parser.add_argument("--locations", default="")
    parser.add_argument("--titles", default="")
    parser.add_argument("--must-keywords", default="")
    parser.add_argument("--prefer-keywords", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-cost-usd", type=float)
    parser.add_argument("--input")
    parser.add_argument("--endpoint")
    parser.add_argument("--token-env", default="PEOPLE_SEARCH_API_TOKEN")
    args = parser.parse_args()
    search = plan(args)
    output = {"mode": args.mode, "query": search, "filters": {"applied": [], "approximated": [], "dropped": [], "unsupported": []}, "cost": {"estimated_usd": 0 if args.mode != "provider" else None, "actual_usd": None}, "results": []}
    try:
        if args.mode == "import":
            if not args.input: raise ValueError("import mode requires --input")
            output["results"] = rank_rows(read_csv(args.input), search)
            output["coverage_note"] = "Ranks only supplied records; no net-new discovery."
        elif args.mode == "provider":
            output["results"] = rank_rows(provider_request(args, search), search)
            output["coverage_note"] = "Preview canary from the configured provider; coverage depends on that provider."
        else:
            output["coverage_note"] = "Search plan only; no discovery source was used."
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({**output, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
