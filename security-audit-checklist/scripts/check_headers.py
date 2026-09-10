#!/usr/bin/env python3
"""Check security headers on a live URL."""

import argparse
import sys
import urllib.request

EXPECTED = {
    "strict-transport-security": "warning",
    "content-security-policy": "critical",
    "x-frame-options": "critical",
    "x-content-type-options": "critical",
    "referrer-policy": "warning",
    "permissions-policy": "info",
}


def check(url: str) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD")
        response = urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}", file=sys.stderr)
        return 1

    headers = {k.lower(): v for k, v in response.headers.items()}
    issues = 0

    for header, severity in EXPECTED.items():
        value = headers.get(header)
        if value:
            print(f"  ✅ {header}: {value}")
        else:
            icon = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "⚪"
            print(f"  {icon} Missing {header} ({severity})")
            if severity == "critical":
                issues += 1

    # Extra checks
    if headers.get("x-powered-by"):
        print(f"  🟡 x-powered-by exposes framework: {headers['x-powered-by']}")
        issues += 1
    if headers.get("server"):
        print(f"  🟡 server header exposes version: {headers['server']}")

    return 1 if issues else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check security headers on a URL.")
    parser.add_argument("url", help="URL to check")
    args = parser.parse_args()
    print(f"Checking {args.url} ...\n")
    return check(args.url)


if __name__ == "__main__":
    sys.exit(main())
