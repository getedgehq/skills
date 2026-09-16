#!/usr/bin/env python3
"""Read the public Rocketlist job surface. No account, no credential, no /api/ call.

Subcommands
-----------
job    Fetch one public job detail page and print its structured record as JSON.
       Takes a full URL, a slug, or a UUID. The page is server rendered, so a plain
       HTTP GET is enough here.

scan   Download the public job sitemaps once, cache them, and count how many live
       postings contain each title pattern. Use this to throw away invented titles
       before spending rendered search calls on them.

The search page itself (/jobs?q=...) renders results in the browser and is NOT
fetchable this way. Drive that with a JavaScript capable fetch. See
references/search-surface.md.
"""

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request

BASE = "https://rocketlist.ai"
UA = "rocketlist-skill/1.0 (+https://github.com/getedgehq/skills)"
SITEMAPS = ["sitemap-jobs.xml", "sitemap-jobs-2.xml", "sitemap-jobs-3.xml"]

FIELDS = [
    "job_title_original",
    "company",
    "company_vertical_primary",
    "company_stage",
    "company_founded_year",
    "company_total_raised_usd",
    "job_city_primary",
    "job_country_primary",
    "job_location_type",
    "job_salary_range",
    "job_category",
    "job_functional_role",
    "job_subcategory",
    "job_seniority",
    "job_url",
    "job_tech_stack",
    "job_role_summary",
    "job_experience_required",
    "job_benefits_perks",
    "job_required_skills",
    "job_nice_to_have_skills",
]


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def undollar(value):
    """The page state escapes a leading '$' by doubling it."""
    if isinstance(value, str) and value.startswith("$$"):
        return value[1:]
    return value


def extract_field(html, key):
    """Pull one field out of the escaped page state.

    The state is embedded inside a JavaScript string literal, so every quote is
    backslash escaped. Match the escaped key, then the escaped value.
    """
    marker = '\\"%s\\":' % key
    start = html.find(marker)
    if start < 0:
        return None
    pos = start + len(marker)
    rest = html[pos:pos + 4000]

    if rest.startswith("null"):
        return None
    if rest.startswith('\\"'):
        m = re.match(r'\\"((?:[^\\]|\\[^"])*)\\"', rest)
        if not m:
            return None
        return undollar(unescape(m.group(1)))
    if rest.startswith("["):
        m = re.match(r"\[(.*?)\]", rest, re.S)
        if not m:
            return None
        items = re.findall(r'\\"((?:[^\\]|\\[^"])*)\\"', m.group(1))
        return [undollar(unescape(i)) for i in items]
    m = re.match(r"(-?\d+(?:\.\d+)?)", rest)
    if m:
        text = m.group(1)
        return float(text) if "." in text else int(text)
    return None


def unescape(text):
    text = text.replace('\\\\"', '"').replace("\\u0026", "&")
    try:
        return json.loads('"%s"' % text.replace('\\"', '"').replace('"', '\\"'))
    except ValueError:
        return text


def json_ld(html):
    out = []
    for m in re.finditer(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    ):
        try:
            out.append(json.loads(m.group(1)))
        except ValueError:
            continue
    return out


def job_url(ref):
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref.split("?")[0]
    return "%s/jobs/%s" % (BASE, ref.strip("/").split("?")[0])


def cmd_job(args):
    url = job_url(args.ref)
    html = get(url)
    record = {"rocketlist_url": url}
    for field in FIELDS:
        record[field] = extract_field(html, field)

    for block in json_ld(html):
        if isinstance(block, dict) and block.get("@type") == "JobPosting":
            record.setdefault("job_title_original", block.get("title"))
            if args.description:
                record["description_html"] = block.get("description")

    if record.get("job_salary_range") in (None, "Not specified"):
        record["salary_published"] = False
    else:
        record["salary_published"] = True

    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


def cache_dir():
    path = os.path.join(tempfile.gettempdir(), "rocketlist-sitemaps")
    os.makedirs(path, exist_ok=True)
    return path


def cmd_scan(args):
    blob = []
    for name in SITEMAPS:
        cached = os.path.join(cache_dir(), name)
        if os.path.exists(cached) and not args.refresh:
            with open(cached, encoding="utf-8") as fh:
                text = fh.read()
        else:
            try:
                text = get("%s/%s" % (BASE, name), timeout=180)
            except urllib.error.HTTPError as err:
                print("skip %s: HTTP %s" % (name, err.code), file=sys.stderr)
                continue
            with open(cached, "w", encoding="utf-8") as fh:
                fh.write(text)
        blob.append(text)

    slugs = []
    for text in blob:
        slugs.extend(re.findall(r"<loc>https://rocketlist\.ai/jobs/([^<]+)</loc>", text))
    print("indexed %d live job slugs" % len(slugs), file=sys.stderr)

    for pattern in args.pattern:
        needle = pattern.strip().lower().replace(" ", "-")
        hits = [s for s in slugs if needle in s]
        print("%6d  %s" % (len(hits), pattern))
        for slug in hits[: args.examples]:
            print("        %s/jobs/%s" % (BASE, slug))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_job = sub.add_parser("job", help="print one public job record as JSON")
    p_job.add_argument("ref", help="job URL, slug, or UUID")
    p_job.add_argument(
        "--description",
        action="store_true",
        help="include the full HTML description from the JobPosting JSON-LD",
    )
    p_job.set_defaults(func=cmd_job)

    p_scan = sub.add_parser("scan", help="count live postings per title pattern")
    p_scan.add_argument(
        "--pattern", action="append", required=True, help="title text, repeatable"
    )
    p_scan.add_argument("--examples", type=int, default=3, help="example URLs per hit")
    p_scan.add_argument("--refresh", action="store_true", help="ignore the local cache")
    p_scan.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
