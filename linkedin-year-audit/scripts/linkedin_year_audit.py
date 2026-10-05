#!/usr/bin/env python3
"""LinkedIn Year Audit. Method by Federico De Ponte.

Reads a LinkedIn creator analytics export (AggregateAnalytics_*.xlsx) and
writes report.json and report.md. Runs fully on this computer: no network
calls, nothing is uploaded.

Usage:
    python3 linkedin_year_audit.py EXPORT.xlsx [--out DIR] [--themes FILE]

--themes FILE is optional: a JSON object mapping post id to a theme label,
e.g. {"7000000000000000001": "personal story"}. Post ids are in report.json.
"""
import argparse
import calendar
import datetime as dt
import json
import math
import os
import re
import statistics
import sys
import unicodedata
import warnings
from urllib.parse import unquote, urlparse

try:
    import openpyxl
except ImportError:
    sys.exit("This script needs openpyxl. Install it with: python3 -m pip install openpyxl")

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

SMALL_N = 5  # buckets with fewer posts than this are flagged as too small to read
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_WORDS = {
    1: ["jan", "gen", "ene", "janv"],
    2: ["feb", "fev", "fév", "févr"],
    3: ["mar", "mär", "mrz", "maa", "mrt"],
    4: ["apr", "abr", "avr"],
    5: ["may", "mai", "mei", "mag"],
    6: ["jun", "juin", "giu"],
    7: ["jul", "juil", "lug"],
    8: ["aug", "ago", "aoû", "aou"],
    9: ["sep", "set"],
    10: ["oct", "okt", "out", "ott"],
    11: ["nov"],
    12: ["dec", "dez", "dic", "déc"],
}
NUM_RE = re.compile(r"^[\s  ]*\d[\d.,'\s  ]*$")
POST_RE = re.compile(r"^(?P<who>[^_]+)_(?:(?P<slug>.*?)-)?(?:share|ugcPost|activity)-(?P<id>\d{15,22})(?:-[\w-]*)?$")


# ---------- small parsers ----------

def to_int(v):
    """Cell to whole number, or None. Accepts 1234, '1234', '1,234', '1.234', '1 234'."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return int(round(v))
    s = str(v)
    if not NUM_RE.match(s):
        return None
    digits = re.sub(r"\D", "", s)
    return int(digits) if digits else None


def raw_date(v):
    """Cell to ('exact', date) or ('ambiguous', (a, b, year)) or None."""
    if isinstance(v, dt.datetime):
        return ("exact", v.date())
    if isinstance(v, dt.date):
        return ("exact", v)
    if v is None:
        return None
    s = str(v).strip()
    if not s or len(s) > 40:
        return None
    groups = re.findall(r"\d+", s)
    words = re.findall(r"[^\W\d_]+", s)
    try:
        if len(groups) == 3 and not words:
            a, b, c = groups
            if len(a) == 4:
                return ("exact", dt.date(int(a), int(b), int(c)))
            year = int(c) + (2000 if len(c) <= 2 else 0)
            return ("ambiguous", (int(a), int(b), year))
        if len(groups) == 2 and len(words) == 1 and len(words[0]) >= 3:  # month as a word
            if True:
                w = words[0].lower()
                best = None
                for month, keys in MONTH_WORDS.items():
                    for k in keys:
                        if w.startswith(k) and (best is None or len(k) > best[1]):
                            best = (month, len(k))
                if best:
                    nums = sorted(int(g) for g in groups)
                    year = nums[1] + (2000 if nums[1] < 100 else 0)
                    return ("exact", dt.date(year, best[0], nums[0]))
    except ValueError:
        return None
    return None


def detect_order(raws):
    """'DMY', 'MDY' or None from a list of raw_date results."""
    first_big = any(r[0] == "ambiguous" and r[1][0] > 12 for r in raws if r)
    second_big = any(r[0] == "ambiguous" and r[1][1] > 12 for r in raws if r)
    if first_big and not second_big:
        return "DMY"
    if second_big and not first_big:
        return "MDY"
    return None


def resolve(raw, order):
    if not raw:
        return None
    if raw[0] == "exact":
        return raw[1]
    a, b, y = raw[1]
    try:
        return dt.date(y, a, b) if order == "MDY" else dt.date(y, b, a)
    except ValueError:
        return None


def parse_post_url(url):
    """Return (post_id, hook). The hook is the first words of the post, recovered from the link."""
    path = unquote(urlparse(str(url)).path).rstrip("/")
    last = path.split("/")[-1]
    m = POST_RE.match(last)
    if m:
        post_id, slug = m.group("id"), m.group("slug") or ""
    else:
        ids = re.findall(r"\d{15,22}", unquote(str(url)))
        post_id, slug = (ids[-1] if ids else str(url)), ""
    # NFKC turns Unicode "bold" and "italic" letters back into plain letters
    hook = unicodedata.normalize("NFKC", slug).replace("-", " ")
    hook = re.sub(r"\s+", " ", hook).strip()
    if hook:
        hook = hook[0].upper() + hook[1:]
    return post_id, hook


def date_from_post_id(post_id):
    """LinkedIn post ids carry their creation time (UTC). Used only as a fallback."""
    try:
        ms = int(post_id) >> 22
        d = dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date()
        return d if 2003 <= d.year <= dt.date.today().year + 1 else None
    except (ValueError, OverflowError, OSError):
        return None


def pct(part, whole):
    return round(100.0 * part / whole, 1) if whole else None


def median(xs):
    return statistics.median(xs) if xs else None


# ---------- reading the workbook ----------

def load_sheets(path):
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheets = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        sheets.append((ws.title, rows))
    wb.close()
    return sheets


def cell(row, i):
    return row[i] if i < len(row) else None


def is_daily(rows, cols):
    hits = 0
    for r in rows:
        if raw_date(cell(r, 0)) and all(to_int(cell(r, c)) is not None for c in cols):
            hits += 1
    return hits


def identify(sheets):
    """Map sheet roles to rows. By English name first, then by shape (other languages)."""
    found, warnings_ = {}, []
    names = {"DISCOVERY": "discovery", "ENGAGEMENT": "engagement", "TOP POSTS": "top_posts", "FOLLOWERS": "followers"}
    rest = []
    for title, rows in sheets:
        role = names.get(title.strip().upper())
        if role and role not in found:
            found[role] = rows
        else:
            rest.append((title, rows))
    for title, rows in rest:
        has_link = any("linkedin.com/" in str(c) for r in rows[:60] for c in r if c)
        three = is_daily(rows, (1, 2))
        two = is_daily(rows, (1,))
        numeric_rows = [r for r in rows if to_int(cell(r, 1)) is not None]
        if has_link and "top_posts" not in found:
            role = "top_posts"
        elif three >= 5 and "engagement" not in found:
            role = "engagement"
        elif two >= 5 and three < 5 and "followers" not in found:
            role = "followers"
        elif 0 < len(rows) <= 8 and len(numeric_rows) >= 1 and two == 0 and "discovery" not in found \
                and not any("%" in str(c) for r in rows for c in r if c):
            role = "discovery"
        else:
            continue
        found[role] = rows
        warnings_.append(f"Sheet '{title}' was recognised by its layout as {role.replace('_', ' ')}.")
    return found, warnings_


def read_discovery(rows):
    out = {"period": None, "impressions": None, "members_reached": None}
    if not rows:
        return out
    if rows and len(rows[0]) > 1 and rows[0][1] and to_int(rows[0][1]) is None:
        out["period"] = str(rows[0][1]).strip()
    nums = []
    for r in rows:
        n = to_int(cell(r, 1))
        if n is None:
            continue
        label = str(cell(r, 0) or "").lower()
        if "impression" in label:
            out["impressions"] = n
        elif "reach" in label:
            out["members_reached"] = n
        nums.append(n)
    if out["impressions"] is None and nums:
        out["impressions"] = max(nums)
    if out["members_reached"] is None and len(nums) >= 2:
        out["members_reached"] = min(nums)
    return out


def read_daily(rows, value_cols):
    """Rows of (date, v1, v2...). Returns (list of tuples, date order, n unparsed)."""
    raws = []
    for r in rows or []:
        rd = raw_date(cell(r, 0))
        vals = [to_int(cell(r, c)) for c in value_cols]
        if rd and vals[0] is not None:
            raws.append((rd, [v or 0 for v in vals]))
    order = detect_order([rd for rd, _ in raws])
    out, bad = [], 0
    for rd, vals in raws:
        d = resolve(rd, order or "MDY")
        if d:
            out.append((d, *vals))
        else:
            bad += 1
    return out, order, bad


def read_followers(rows):
    total, total_label = None, None
    for r in rows or []:
        n = to_int(cell(r, 1))
        if n is not None and not raw_date(cell(r, 0)):
            total, total_label = n, str(cell(r, 0) or "").strip()
            break
    daily, order, bad = read_daily(rows, (1,))
    return total, total_label, daily, order, bad


def read_top_posts(rows, fallback_order):
    """Find the side-by-side tables. Returns dict with 'impressions' and 'engagements' lists."""
    tables = {}   # url column index -> list of [url, raw date, number]
    headers = {}
    for ri, r in enumerate(rows or []):
        for ci, c in enumerate(r):
            if isinstance(c, str) and "linkedin.com/" in c:
                n = to_int(cell(r, ci + 2))
                if n is None:
                    continue
                if ci not in tables:
                    tables[ci] = []
                    for back in range(ri - 1, -1, -1):  # header is the nearest text above the number
                        h = cell(rows[back], ci + 2)
                        if h not in (None, ""):
                            headers[ci] = str(h).strip().lower()
                            break
                tables[ci].append([c.strip(), raw_date(cell(r, ci + 1)), n])
    all_raw = [row[1] for t in tables.values() for row in t]
    order = detect_order(all_raw) or fallback_order
    notes = []
    if order is None and any(r and r[0] == "ambiguous" for r in all_raw):
        order = "MDY"
        notes.append("Post dates could be read as day/month or month/day. Month/day was assumed. Check a date you know.")
    parsed = {}
    for ci, t in tables.items():
        posts = []
        for url, rd, n in t:
            post_id, hook = parse_post_url(url)
            d = resolve(rd, order or "MDY")
            from_id = False
            if d is None:
                d, from_id = date_from_post_id(post_id), True
            posts.append({"id": post_id, "url": url, "date": d, "date_from_id": from_id and d is not None,
                          "hook": hook, "value": n})
        posts.sort(key=lambda p: -p["value"])
        parsed[ci] = posts
    out = {"impressions": [], "engagements": []}
    unlabeled = []
    for ci, posts in parsed.items():
        h = headers.get(ci, "")
        if "impression" in h and not out["impressions"]:
            out["impressions"] = posts
        elif "engagement" in h and not out["engagements"]:
            out["engagements"] = posts
        else:
            unlabeled.append(posts)
    if unlabeled:  # other language: the table with the bigger numbers is impressions
        unlabeled.sort(key=lambda t: -(t[0]["value"] if t else 0))
        for t in unlabeled:
            if not out["impressions"]:
                out["impressions"] = t
            elif not out["engagements"]:
                out["engagements"] = t
        notes.append("Top post tables were told apart by size of the numbers (larger = impressions).")
    return out, order, notes


# ---------- analysis ----------

def bucket_stats(posts, key, labels=None):
    groups = {}
    for p in posts:
        k = key(p)
        if k is None:
            continue
        groups.setdefault(k, []).append(p["impressions"])
    keys = labels if labels is not None else sorted(groups)
    return [{"bucket": k, "n": len(groups.get(k, [])), "impressions": sum(groups.get(k, [])),
             "median_impressions": median(groups.get(k, [])), "too_small": len(groups.get(k, [])) < SMALL_N}
            for k in keys]


def analyse(path, themes=None):
    sheets = load_sheets(path)
    found, warns = identify(sheets)
    for role in ("discovery", "engagement", "top_posts", "followers"):
        if role not in found:
            warns.append(f"No {role.replace('_', ' ')} sheet found. That part of the report is empty.")

    disc = read_discovery(found.get("discovery"))
    daily, order, bad = read_daily(found.get("engagement"), (1, 2))
    if bad:
        warns.append(f"{bad} daily rows had a date that could not be read and were skipped.")
    f_total, f_label, f_daily, f_order, f_bad = read_followers(found.get("followers"))
    order = order or f_order
    tops, _, notes = read_top_posts(found.get("top_posts"), order)
    warns += notes

    # totals
    daily_imp = sum(d[1] for d in daily)
    daily_eng = sum(d[2] for d in daily)
    impressions = disc["impressions"] if disc["impressions"] is not None else (daily_imp or None)
    if disc["impressions"] is None and daily_imp:
        warns.append("Total impressions were summed from the daily rows (no summary sheet).")
    new_followers = sum(d[1] for d in f_daily) if f_daily else None
    start_followers = f_total - new_followers if f_total is not None and new_followers is not None else None
    dates = [d[0] for d in daily] or [d[0] for d in f_daily]
    totals = {
        "period_label": disc["period"],
        "first_day": min(dates).isoformat() if dates else None,
        "last_day": max(dates).isoformat() if dates else None,
        "days": len(set(dates)),
        "impressions": impressions,
        "members_reached": disc["members_reached"],
        "engagements": daily_eng if daily else None,
        "engagement_rate_pct": pct(daily_eng, daily_imp) if daily else None,
        "followers_now": f_total,
        "new_followers": new_followers,
        "followers_at_start": start_followers,
        "follower_multiple": round(f_total / start_followers, 1) if start_followers and start_followers > 0 else None,
    }

    # monthly
    months = {}
    for d, imp, eng in daily:
        m = months.setdefault(d.strftime("%Y-%m"), {"impressions": 0, "engagements": 0, "new_followers": 0, "days": 0})
        m["impressions"] += imp
        m["engagements"] += eng
        m["days"] += 1
    for d, n in f_daily:
        m = months.setdefault(d.strftime("%Y-%m"), {"impressions": 0, "engagements": 0, "new_followers": 0, "days": 0})
        m["new_followers"] += n
        if not daily:
            m["days"] += 1
    monthly = []
    for k in sorted(months):
        dim = calendar.monthrange(int(k[:4]), int(k[5:]))[1]
        monthly.append({"month": k, **months[k], "days_in_month": dim, "partial": months[k]["days"] < dim})

    # posts: merge the two tables
    by_id = {}
    for rank, p in enumerate(tops["impressions"], 1):
        by_id[p["id"]] = {"id": p["id"], "date": p["date"], "date_from_id": p["date_from_id"], "hook": p["hook"],
                          "impressions": p["value"], "rank_impressions": rank,
                          "engagements": None, "rank_engagements": None, "url": p["url"]}
    for rank, p in enumerate(tops["engagements"], 1):
        e = by_id.setdefault(p["id"], {"id": p["id"], "date": p["date"], "date_from_id": p["date_from_id"],
                                       "hook": p["hook"], "impressions": None, "rank_impressions": None,
                                       "engagements": None, "rank_engagements": None, "url": p["url"]})
        e["engagements"], e["rank_engagements"] = p["value"], rank
    posts = list(by_id.values())
    for p in posts:
        p["engagement_rate_pct"] = round(100.0 * p["engagements"] / p["impressions"], 2) \
            if p["impressions"] and p["engagements"] is not None else None
        p["theme"] = (themes or {}).get(p["id"])
    if any(p["date_from_id"] for p in posts):
        warns.append("Some post dates could not be read and were taken from the post id instead (UTC, can be one day off).")
    imp_posts = sorted([p for p in posts if p["impressions"] is not None], key=lambda p: p["rank_impressions"])
    eng_posts = sorted([p for p in posts if p["engagements"] is not None], key=lambda p: p["rank_engagements"])
    both = [p for p in imp_posts if p["engagements"] is not None]
    n_imp, n_eng = len(imp_posts), len(eng_posts)

    # concentration
    def top_sum(n):
        return sum(p["impressions"] for p in imp_posts[:n])
    conc = {"posts_listed": n_imp, "total_impressions": impressions,
            "listed": {"n": n_imp, "impressions": top_sum(n_imp), "share_pct": pct(top_sum(n_imp), impressions)}}
    for n in (10, 1):
        if n_imp >= n:
            conc[f"top_{n}"] = {"n": n, "impressions": top_sum(n), "share_pct": pct(top_sum(n), impressions)}

    # engagement rate (only where both numbers are known)
    rates = sorted([p for p in both], key=lambda p: -p["engagement_rate_pct"])
    rate = {"n": len(both),
            "median_pct": round(median([p["engagement_rate_pct"] for p in both]), 2) if both else None,
            "min_pct": min((p["engagement_rate_pct"] for p in both), default=None),
            "max_pct": max((p["engagement_rate_pct"] for p in both), default=None),
            "highest": [p["id"] for p in rates[:5]], "lowest": [p["id"] for p in rates[-5:][::-1]] if len(rates) > 5 else []}

    # rank mismatches
    gap = max(3, math.ceil(0.2 * max(n_imp, n_eng, 1)))
    imp_capped, eng_capped = n_imp >= 50, n_eng >= 50
    mismatch = {
        "rank_gap_used": gap,
        "impressions_cutoff": imp_posts[-1]["impressions"] if imp_capped else None,
        "engagements_cutoff": eng_posts[-1]["engagements"] if eng_capped else None,
        "reactions_without_reach": {
            "only_in_engagement_table": [p["id"] for p in eng_posts if p["impressions"] is None],
            "both_tables_rank_gap": [p["id"] for p in sorted(both, key=lambda p: p["rank_engagements"] - p["rank_impressions"])
                                     if p["rank_impressions"] - p["rank_engagements"] >= gap],
        },
        "reach_without_reactions": {
            "only_in_impressions_table": [p["id"] for p in imp_posts if p["engagements"] is None],
            "both_tables_rank_gap": [p["id"] for p in sorted(both, key=lambda p: p["rank_impressions"] - p["rank_engagements"])
                                     if p["rank_engagements"] - p["rank_impressions"] >= gap],
        },
    }

    # timing of the top posts
    dated = [p for p in imp_posts if p["date"]]
    timing = {
        "n": len(dated),
        "by_month": bucket_stats(dated, lambda p: p["date"].strftime("%Y-%m")),
        "by_weekday": bucket_stats(dated, lambda p: WEEKDAYS[p["date"].weekday()], WEEKDAYS),
    }

    # themes (only if the agent supplied labels)
    theme_rows = None
    if themes:
        names = sorted({p["theme"] or "unlabelled" for p in posts})
        theme_rows = []
        listed_imp = top_sum(n_imp)
        for t in names:
            ti = [p for p in imp_posts if (p["theme"] or "unlabelled") == t]
            te = [p for p in eng_posts if (p["theme"] or "unlabelled") == t]
            tb = [p for p in ti if p["engagements"] is not None]
            theme_rows.append({
                "theme": t,
                "n_in_impressions_table": len(ti),
                "n_in_top10_impressions": sum(1 for p in ti if p["rank_impressions"] <= 10),
                "n_in_top10_engagements": sum(1 for p in te if p["rank_engagements"] <= 10),
                "impressions": sum(p["impressions"] for p in ti),
                "share_of_listed_impressions_pct": pct(sum(p["impressions"] for p in ti), listed_imp),
                "median_impressions": median([p["impressions"] for p in ti]),
                "n_in_engagement_table": len(te),
                "engagements": sum(p["engagements"] for p in te),
                "median_engagements": median([p["engagements"] for p in te]),
                "n_in_both": len(tb),
                "median_engagement_rate_pct": round(median([p["engagement_rate_pct"] for p in tb]), 2) if tb else None,
                "too_small": len(ti) < SMALL_N and len(te) < SMALL_N,
            })
        theme_rows.sort(key=lambda r: -r["impressions"])

    for p in posts:
        p["weekday"] = WEEKDAYS[p["date"].weekday()] if p["date"] else None
        p["date"] = p["date"].isoformat() if p["date"] else None
        del p["date_from_id"]
    posts.sort(key=lambda p: (p["rank_impressions"] or 10 ** 6, p["rank_engagements"] or 10 ** 6))

    return {
        "tool": "LinkedIn Year Audit. Method by Federico De Ponte.",
        "source_file": os.path.basename(path),
        "privacy": "Computed locally from the file above. Nothing was uploaded.",
        "totals": totals, "monthly": monthly, "concentration": conc,
        "engagement_rate": rate, "mismatch": mismatch, "timing_of_top_posts": timing,
        "themes": theme_rows,
        "counts": {"in_impressions_table": n_imp, "in_engagement_table": n_eng, "in_both": len(both),
                   "distinct_posts": len(posts), "small_bucket_below": SMALL_N},
        "limits": [
            "Only the top posts are in the export (at most 50 by impressions and 50 by engagements). Weak posts are missing, so nothing here shows what flopped.",
            "There is no post text. Hooks are the first words kept in each post link: no punctuation, cut short, and names of tagged people or companies can be mixed in.",
            "Engagements are known only for posts in the engagement table, impressions only for posts in the impressions table.",
            "The export does not say what kind of engagement it was (likes, comments, reposts), the post format, or the time of day.",
            "Post totals may include views from outside the chosen date range, so shares of the period total are approximate.",
        ],
        "warnings": warns,
        "posts": posts,
    }


# ---------- output ----------

def n_(x):
    return "n/a" if x is None else f"{int(round(x)):,}"


def p_(x):
    if x is None:
        return "n/a"
    return f"{x:.0f}%" if x >= 10 else f"{x:.1f}%"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def to_markdown(r):
    t, c, by_id = r["totals"], r["concentration"], {p["id"]: p for p in r["posts"]}
    hook = lambda p: (p["hook"] or "(no words in the link)").replace("|", "/")
    L = ["# LinkedIn Year Audit: report", "",
         f"Source: `{r['source_file']}`. Period: {t['period_label'] or 'n/a'} ({t['days']} days of daily data, {t['first_day']} to {t['last_day']}).",
         "Computed locally on this computer. Nothing was uploaded. Method by Federico De Ponte.", "",
         "## 1. Totals", ""]
    L += table(["Measure", "Value"], [
        ["Impressions", n_(t["impressions"])], ["Members reached", n_(t["members_reached"])],
        ["Engagements (sum of daily rows)", n_(t["engagements"])],
        ["Engagement rate (engagements / impressions)", p_(t["engagement_rate_pct"])],
        ["Followers now", n_(t["followers_now"])], ["New followers in the period", n_(t["new_followers"])],
        ["Followers at the start (now minus new)", n_(t["followers_at_start"])],
        ["Follower multiple", f"{t['follower_multiple']}x" if t["follower_multiple"] else "n/a"]])
    L += ["", "## 2. Month by month", ""]
    if r["monthly"]:
        L += table(["Month", "Impressions", "Engagements", "New followers", "Days in file"],
                   [[m["month"], n_(m["impressions"]), n_(m["engagements"]), n_(m["new_followers"]),
                     f"{m['days']} of {m['days_in_month']}" + (" (partial)" if m["partial"] else "")] for m in r["monthly"]])
        L += ["", "Do not compare partial months with full months."]
    else:
        L += ["No daily data found."]
    L += ["", "## 3. Concentration", ""]
    if c["posts_listed"]:
        rows = [[f"All {c['listed']['n']} listed top posts", n_(c["listed"]["impressions"]), p_(c["listed"]["share_pct"])]]
        for k in ("top_10", "top_1"):
            if k in c:
                rows.append([f"Top {c[k]['n']}", n_(c[k]["impressions"]), p_(c[k]["share_pct"])])
        L += table(["Posts", "Impressions", "Share of all impressions"], rows)
        L += ["", f"Total impressions in the period: {n_(c['total_impressions'])}. The rest came from posts not in the list."]
    else:
        L += ["No top posts found."]
    L += ["", f"## 4. Top posts by impressions (n = {r['counts']['in_impressions_table']})", "",
          "Hook = first words kept in the post link. Engagements are shown only where the post is also in the engagement table.", ""]
    imp = [p for p in r["posts"] if p["impressions"] is not None]
    cols = ["#", "Date", "Day", "Hook (from link)", "Impressions", "Engagements", "Eng. rate"]
    has_theme = bool(r["themes"])
    if has_theme:
        cols.append("Theme")
    rows = []
    for p in imp:
        row = [p["rank_impressions"], p["date"] or "n/a", (p["weekday"] or "")[:3], hook(p), n_(p["impressions"]),
               n_(p["engagements"]) if p["engagements"] is not None else "not in table",
               f"{p['engagement_rate_pct']:.2f}%" if p["engagement_rate_pct"] is not None else ""]
        if has_theme:
            row.append(p["theme"] or "unlabelled")
        rows.append(row)
    L += table(cols, rows) if rows else ["None."]

    e = r["engagement_rate"]
    L += ["", f"## 5. Engagement rate (n = {e['n']} posts present in both tables)", ""]
    if e["n"]:
        L += [f"Median {e['median_pct']:.2f} engagements per 100 impressions. Range {e['min_pct']:.2f} to {e['max_pct']:.2f}.",
              "This covers only posts that made both lists, so it is a rate for the strongest posts, not an average for the account.", ""]
        def rate_rows(ids):
            return [[hook(by_id[i]), by_id[i]["date"], n_(by_id[i]["impressions"]), n_(by_id[i]["engagements"]),
                     f"{by_id[i]['engagement_rate_pct']:.2f}%"] for i in ids]
        L += ["Highest:", ""] + table(["Hook", "Date", "Impressions", "Engagements", "Rate"], rate_rows(e["highest"]))
        if e["lowest"]:
            L += ["", "Lowest:", ""] + table(["Hook", "Date", "Impressions", "Engagements", "Rate"], rate_rows(e["lowest"]))
    else:
        L += ["No post appears in both tables."]

    m = r["mismatch"]
    L += ["", "## 6. Reach and reactions that do not match", ""]
    a, b = m["reactions_without_reach"], m["reach_without_reactions"]
    L += [f"### Reactions without reach (n = {len(a['only_in_engagement_table']) + len(a['both_tables_rank_gap'])})", ""]
    cut = f"below {n_(m['impressions_cutoff'])}" if m["impressions_cutoff"] is not None else "unknown"
    rows = [[hook(by_id[i]), by_id[i]["date"], n_(by_id[i]["engagements"]), f"#{by_id[i]['rank_engagements']}", f"not listed ({cut})"]
            for i in a["only_in_engagement_table"]]
    rows += [[hook(by_id[i]), by_id[i]["date"], n_(by_id[i]["engagements"]), f"#{by_id[i]['rank_engagements']}",
              f"{n_(by_id[i]['impressions'])} (#{by_id[i]['rank_impressions']})"] for i in a["both_tables_rank_gap"]]
    L += table(["Hook", "Date", "Engagements", "Eng. rank", "Impressions"], rows) if rows else ["None."]
    L += ["", f"### Reach without reactions (n = {len(b['only_in_impressions_table']) + len(b['both_tables_rank_gap'])})", ""]
    cut = f"below {n_(m['engagements_cutoff'])}" if m["engagements_cutoff"] is not None else "unknown"
    rows = [[hook(by_id[i]), by_id[i]["date"], n_(by_id[i]["impressions"]), f"#{by_id[i]['rank_impressions']}", f"not listed ({cut})"]
            for i in b["only_in_impressions_table"]]
    rows += [[hook(by_id[i]), by_id[i]["date"], n_(by_id[i]["impressions"]), f"#{by_id[i]['rank_impressions']}",
              f"{n_(by_id[i]['engagements'])} (#{by_id[i]['rank_engagements']})"] for i in b["both_tables_rank_gap"]]
    L += table(["Hook", "Date", "Impressions", "Imp. rank", "Engagements"], rows) if rows else ["None."]
    L += ["", f"A post is listed here if it is in one table only, or if its two ranks are {m['rank_gap_used']} or more places apart."]

    tm = r["timing_of_top_posts"]
    L += ["", f"## 7. When the top posts were published (n = {tm['n']})", "",
          "This counts top posts only. It cannot show a best day or month, because posts that did badly are not in the file.", ""]
    flag = lambda x: "too small to read" if x["too_small"] else ""
    L += table(["Publish month", "n", "Impressions", "Median impressions", "Note"],
               [[x["bucket"], x["n"], n_(x["impressions"]), n_(x["median_impressions"]), flag(x)] for x in tm["by_month"]])
    L += [""]
    L += table(["Weekday", "n", "Impressions", "Median impressions", "Note"],
               [[x["bucket"], x["n"], n_(x["impressions"]), n_(x["median_impressions"]), flag(x)] for x in tm["by_weekday"]])
    L += ["", f"Buckets with fewer than {r['counts']['small_bucket_below']} posts are marked. Even the larger ones are small."]

    if r["themes"]:
        L += ["", "## 8. Themes (labels added by the assistant from the hooks)", ""]
        L += table(["Theme", "n by impressions", "Impressions", "Share of listed", "Median imp.", "In top 10 by imp.",
                    "n by engagements", "Median eng.", "In top 10 by eng.", "n in both", "Median rate", "Note"],
                   [[x["theme"], x["n_in_impressions_table"], n_(x["impressions"]), p_(x["share_of_listed_impressions_pct"]),
                     n_(x["median_impressions"]), x["n_in_top10_impressions"], x["n_in_engagement_table"],
                     n_(x["median_engagements"]), x["n_in_top10_engagements"], x["n_in_both"],
                     f"{x['median_engagement_rate_pct']:.2f}%" if x["median_engagement_rate_pct"] is not None else "n/a",
                     "too small to read" if x["too_small"] else ""] for x in r["themes"]])

    L += ["", "## What this file cannot tell you", ""] + [f"- {x}" for x in r["limits"]]
    if r["warnings"]:
        L += ["", "## Notes from reading the file", ""] + [f"- {x}" for x in r["warnings"]]
    return "\n".join(L) + "\n"


def to_json(r):
    head = {k: v for k, v in r.items() if k != "posts"}
    body = json.dumps(head, ensure_ascii=False, indent=1)
    posts = ",\n  ".join(json.dumps(p, ensure_ascii=False, separators=(",", ":")) for p in r["posts"])
    return body[:-2] + ',\n "posts": [\n  ' + posts + "\n ]\n}\n"


def main():
    ap = argparse.ArgumentParser(description="LinkedIn Year Audit: analyse your own LinkedIn analytics export, locally.")
    ap.add_argument("export", help="path to AggregateAnalytics_*.xlsx")
    ap.add_argument("--out", help="folder for report.md and report.json (default: next to the export)")
    ap.add_argument("--themes", help="optional JSON file mapping post id to theme label")
    a = ap.parse_args()
    if not os.path.isfile(a.export):
        sys.exit(f"File not found: {a.export}")
    themes = None
    if a.themes:
        with open(a.themes, encoding="utf-8") as f:
            themes = {str(k): str(v) for k, v in json.load(f).items()}
    try:
        result = analyse(a.export, themes)
    except Exception as exc:  # unreadable or not an export
        sys.exit(f"Could not read this file as a LinkedIn analytics export ({type(exc).__name__}: {exc}).")
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.export)), "linkedin-year-audit-output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as f:
        f.write(to_json(result))
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write(to_markdown(result))
    t, c = result["totals"], result["concentration"]
    print(f"Impressions {n_(t['impressions'])} | members reached {n_(t['members_reached'])} | "
          f"followers {n_(t['followers_now'])} (+{n_(t['new_followers'])})")
    print(f"Top posts listed: {c['posts_listed']} = {p_(c['listed']['share_pct'])} of impressions")
    for w in result["warnings"]:
        print("Note:", w)
    print("Wrote", os.path.join(out, "report.md"))
    print("Wrote", os.path.join(out, "report.json"))


if __name__ == "__main__":
    main()
