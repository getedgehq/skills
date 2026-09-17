"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    buckets = {}
    order = []
    for r in rows:
        key = (r["employee_id"], r["week"])
        if key not in buckets:
            buckets[key] = {
                "employee_id": r["employee_id"],
                "name": r["name"],
                "week": r["week"],
                "cost_centre": r["cost_centre"],
                "rate_cents": r["rate_cents"],
                "minutes": 0,
            }
            order.append(key)
        buckets[key]["minutes"] += round_minutes(r["minutes"], settings["rounding_minutes"])

    out = []
    for key in order:
        b = dict(buckets[key])
        cap = settings["overtime_weekly_minutes"]
        regular = min(b["minutes"], cap)
        overtime = max(0, b["minutes"] - cap)
        rate = Decimal(b["rate_cents"])
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * Decimal("1.5") / 60)
        b["gross_cents"] = int(gross)
        out.append(b)
    return out


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
