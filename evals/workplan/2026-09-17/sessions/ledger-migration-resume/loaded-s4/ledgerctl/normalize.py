"""Normalise raw ledger export rows into canonical rows."""
import csv
import re
from decimal import Decimal

CURRENCY_PREFIX = re.compile(r"^(EUR|USD|GBP)\s*", re.I)


def parse_amount(raw):
    """Return a Decimal for one raw amount cell.

    Cells in the exports look like 'EUR 1234.50', '1,234.50', 'EUR 1,234.50'.
    Parentheses indicate negative amounts: '(EUR 340.00)' or '(112.05)'.
    """
    s = str(raw).strip()
    
    # Check for parentheses (negative amount)
    is_negative = False
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()
    
    # Strip currency prefix
    s = CURRENCY_PREFIX.sub("", s)
    # Remove thousands separators
    s = s.replace(",", "")
    
    amount = Decimal(s)
    return -amount if is_negative else amount


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
    """Collapse rows that share a txn_id, keeping the most recently updated."""
    seen = {}
    for r in rows:
        tid = r["txn_id"]
        if tid not in seen or r["updated_at"] > seen[tid]["updated_at"]:
            seen[tid] = r
    return list(seen.values())
