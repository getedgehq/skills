"""Normalise raw ledger export rows into canonical rows."""
import csv
import re
from decimal import Decimal

CURRENCY_PREFIX = re.compile(r"^(EUR|USD|GBP)\s*", re.I)


def parse_amount(raw):
    """Return a Decimal for one raw amount cell.

    Cells in the exports look like 'EUR 1234.50', '1,234.50', 'EUR 1,234.50'.
    The new bank export also writes credits in parentheses, and the parenthesis
    wraps the whole cell including the currency prefix: '(EUR 340.00)'.
    """
    s = str(raw).strip()
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1].strip()
    s = CURRENCY_PREFIX.sub("", s).strip()
    s = s.replace(",", "")
    if s.startswith("-"):
        negative = not negative
        s = s[1:]
    value = Decimal(s)
    return -value if negative else value


def parse_currency(raw):
    return str(raw).strip().upper()


def read_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "txn_id": r["txn_id"].strip(),
                "booked_on": r["booked_on"].strip(),
                "updated_at": r["updated_at"].strip(),
                "account": r["account"].strip(),
                "currency": parse_currency(r["currency"]),
                "amount": parse_amount(r["amount"]),
                "memo": r["memo"].strip(),
            })
    return rows


def dedupe(rows):
    """Collapse rows that share a txn_id, keeping the most recently updated one."""
    seen = {}
    for r in rows:
        prev = seen.get(r["txn_id"])
        if prev is None or r["updated_at"] >= prev["updated_at"]:
            seen[r["txn_id"]] = r
    return list(seen.values())


def filter_since(rows, since):
    """Keep rows booked on or after `since` (YYYY-MM-DD)."""
    if not since:
        return rows
    return [r for r in rows if r["booked_on"] >= since]
