"""Normalise raw ledger export rows into canonical rows."""
import csv
import re
from decimal import Decimal

CURRENCY_PREFIX = re.compile(r"^(EUR|USD|GBP)\s*", re.I)


def parse_amount(raw):
    s = str(raw).strip()
    s = CURRENCY_PREFIX.sub("", s)
    s = s.replace(",", "")
    if s.startswith("(") and s.endswith(")"):
        return -Decimal(s[1:-1])
    return Decimal(s)


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
    seen = {}
    for r in rows:
        prev = seen.get(r["txn_id"])
        if prev is None or r["updated_at"] > prev["updated_at"]:
            seen[r["txn_id"]] = r
    return list(seen.values())
