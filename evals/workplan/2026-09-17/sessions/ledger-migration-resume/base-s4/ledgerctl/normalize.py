"""Normalise raw ledger export rows into canonical rows."""
import csv
import re
from decimal import Decimal
from datetime import datetime

CURRENCY_PREFIX = re.compile(r"^(EUR|USD|GBP)\s*", re.I)


def parse_amount(raw):
    """Return a Decimal for one raw amount cell.

    Cells in the exports look like 'EUR 1234.50', '1,234.50', 'EUR 1,234.50'.
    Amounts in parentheses like '(EUR 340.00)' are negative.
    """
    s = str(raw).strip()
    
    # Check if wrapped in parentheses (negative)
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1].strip()
    
    # Strip currency prefix
    s = CURRENCY_PREFIX.sub("", s)
    # Remove thousands separator
    s = s.replace(",", "")
    
    amount = Decimal(s)
    return -amount if negative else amount


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
    """Collapse rows that share a txn_id, keeping the most recently updated row."""
    seen = {}
    for r in rows:
        txn_id = r["txn_id"]
        if txn_id not in seen:
            seen[txn_id] = r
        else:
            # Keep the row with the latest updated_at timestamp
            if r["updated_at"] > seen[txn_id]["updated_at"]:
                seen[txn_id] = r
    return list(seen.values())


def filter_since(rows, since_date):
    """Filter rows to only those booked on or after since_date.
    
    Args:
        rows: List of row dicts with 'booked_on' field (YYYY-MM-DD format)
        since_date: String in YYYY-MM-DD format
    
    Returns:
        Filtered list of rows
    """
    if not since_date:
        return rows
    
    return [r for r in rows if r["booked_on"] >= since_date]
