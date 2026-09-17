"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal, ROUND_HALF_UP

from .timesheet import round_minutes

OVERTIME_MULTIPLIER = Decimal("1.5")


def build(rows, settings):
    """Return a list of per employee-week entries, week order preserved."""
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
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * OVERTIME_MULTIPLIER / 60)
        b["regular_minutes"] = regular
        b["overtime_minutes"] = overtime
        b["gross_cents"] = int(gross.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        out.append(b)
    return out


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
