"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    """Return a list of {employee_id, week, cost_centre, minutes, gross_cents}, week order preserved.
    
    Also returns a list of excluded rows (those with missing cost_centre).
    Returns: (entries, excluded_rows)
    """
    # PS-212: Track rows with missing cost_centre
    excluded = []
    valid_rows = []
    
    for r in rows:
        if not r["cost_centre"]:
            excluded.append({
                "employee_id": r["employee_id"],
                "name": r["name"],
                "week": r["week"],
                "day": r["day"],
                "minutes": r["minutes"]
            })
        else:
            valid_rows.append(r)
    
    buckets = {}
    order = []
    for r in valid_rows:
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
        b = buckets[key]
        cap = settings["overtime_weekly_minutes"]
        regular = min(b["minutes"], cap)
        overtime = max(0, b["minutes"] - cap)
        rate = Decimal(b["rate_cents"])
        
        # PS-211: Overtime at 1.5x rate, calculated on rounded minutes
        regular_pay = Decimal(regular) * rate / 60
        overtime_pay = Decimal(overtime) * rate * Decimal("1.5") / 60
        gross = regular_pay + overtime_pay
        
        b = dict(b)
        b["regular_minutes"] = regular
        b["overtime_minutes"] = overtime
        b["gross_cents"] = int(gross)
        out.append(b)
    return out, excluded


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
