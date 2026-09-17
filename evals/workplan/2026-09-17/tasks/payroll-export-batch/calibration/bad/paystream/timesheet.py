"""Reading and normalising raw timesheet rows."""
import csv
from decimal import Decimal, ROUND_HALF_UP


def round_minutes(minutes, step):
    if step <= 1:
        return int(minutes)
    q = (Decimal(int(minutes)) / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(q) * step


def read_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r["cost_centre"].strip():
                continue
            rows.append({
                "employee_id": r["employee_id"].strip(),
                "name": r["name"].strip(),
                "cost_centre": r["cost_centre"].strip(),
                "week": r["week"].strip(),
                "day": r["day"].strip(),
                "minutes": int(r["minutes"]),
                "rate_cents": int(r["rate_cents"]),
            })
    return rows
