#!/usr/bin/env python3
"""Keyless source lookup and DOI verification for the openpaper skill.

No API key. Crossref, OpenAlex and DataCite are open endpoints. Every printed
DOI is checked against Crossref, then DataCite, and a source whose DOI does not
resolve is never returned as verified.

    sources.py find "topic"  [--n 12]
    sources.py verify 10.1038/s41598-023-41032-5 [more DOIs...]
"""
import json, sys, time, urllib.parse, urllib.request

UA = "openpaper-skill/1.0 (mailto:team@openpaper.dev)"

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

# Crossref indexes peer-review reports, decision letters, corrections and
# component parts as first-class works. A bibliographic query returns them
# ranked alongside the papers, so an unfiltered `find` can hand back a citation
# list made entirely of review artifacts. Only these types are citable.
CITABLE_TYPES = {"journal-article", "proceedings-article", "posted-content",
                 "book-chapter", "monograph", "report"}
# Titles Crossref gives review/decision/correction records, matched case-folded.
_JUNK_PREFIXES = ("review for ", "decision letter for ", "author response",
                  "reviewer report", "peer review of ", "correction to",
                  "corrigendum", "erratum", "retraction")


def _citable(title, doi):
    t = (title or "").strip().lower()
    if not t or t.startswith(_JUNK_PREFIXES):
        return False
    # Review artifacts hang off the parent DOI as /vN/reviewN or /vN/decisionN.
    tail = doi.rsplit("/", 2)[-2:] if doi.count("/") >= 2 else []
    return not any(s.startswith(("review", "decision", "sup")) for s in tail)


def find(topic, n=12):
    out, seen = [], set()
    try:
        # Over-fetch: the type filter removes a large share of Crossref hits.
        q = urllib.parse.urlencode({
            "query.bibliographic": topic, "rows": max(n * 4, 40),
            "filter": ",".join(f"type:{t}" for t in sorted(CITABLE_TYPES)),
            "select": "DOI,title,author,issued,container-title,type"})
        for it in _get(f"https://api.crossref.org/works?{q}")["message"]["items"]:
            if len(out) >= n: break
            doi = (it.get("DOI") or "").lower()
            title = (it.get("title") or [""])[0]
            if not doi or doi in seen: continue
            if it.get("type") not in CITABLE_TYPES: continue
            if not _citable(title, doi): continue
            au = [f"{a.get('family','')}".strip() for a in (it.get("author") or []) if a.get("family")]
            if not au: continue          # a paper with no named author is not citable
            seen.add(doi)
            out.append({"doi": doi, "title": title, "authors": au[:6],
                        "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                        "venue": (it.get("container-title") or [""])[0],
                        "type": it.get("type"), "source": "crossref"})
    except Exception as e:
        print(f"# crossref failed: {e}", file=sys.stderr)
    if len(out) < n:
        try:
            q = urllib.parse.urlencode({"search": topic, "per-page": (n - len(out)) * 3,
                                        "filter": "type:article"})
            for w in _get(f"https://api.openalex.org/works?{q}").get("results", []):
                if len(out) >= n: break
                doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                title = w.get("title") or ""
                if not doi or doi in seen or not _citable(title, doi): continue
                au = [a["author"]["display_name"].split()[-1]
                      for a in (w.get("authorships") or []) if a.get("author")]
                if not au: continue
                if verify(doi)["status"] != "resolved": continue
                seen.add(doi)
                out.append({"doi": doi, "title": title, "authors": au[:6],
                            "year": w.get("publication_year"),
                            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
                            "type": w.get("type"), "source": "openalex"})
        except Exception as e:
            print(f"# openalex failed: {e}", file=sys.stderr)
    return out

def verify(doi):
    """resolved | absent | unknown | invalid. Unknown never becomes absent."""
    d = doi.strip().lower().replace("https://doi.org/", "")
    if not d:
        return {"doi": d, "status": "invalid", "agency": None,
                "error": "DOI is empty"}
    for name, url in (("crossref", f"https://api.crossref.org/works/{urllib.parse.quote(d)}"),
                      ("datacite", f"https://api.datacite.org/dois/{urllib.parse.quote(d)}")):
        try:
            j = _get(url)
            t = (j.get("message", {}).get("title") or [""])[0] if name == "crossref" \
                else (j.get("data", {}).get("attributes", {}).get("titles") or [{}])[0].get("title", "")
            return {"doi": d, "status": "resolved", "agency": name, "title": t}
        except urllib.error.HTTPError as e:
            if e.code != 404:
                return {"doi": d, "status": "unknown", "agency": name, "error": f"HTTP {e.code}"}
        except Exception as e:
            return {"doi": d, "status": "unknown", "agency": name, "error": str(e)}
        time.sleep(0.1)
    return {"doi": d, "status": "absent", "agency": None}

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "find":
        n = 12
        if "--n" in sys.argv: n = int(sys.argv[sys.argv.index("--n") + 1])
        print(json.dumps(find(sys.argv[2], n), indent=2, ensure_ascii=False))
    elif cmd == "verify":
        res = [verify(d) for d in sys.argv[2:]]
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(1 if any(r["status"] != "resolved" for r in res) else 0)
    else:
        print(__doc__); sys.exit(2)
