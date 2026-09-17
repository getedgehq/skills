"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    """Return a list of {employee_id, week, cost_centre, minutes, gross_cents}, week order preserved.
    
    Also returns a list of skipped rows that had no cost_centre.
    """
    buckets = {}
    order = []
    skipped = []
    
    for r in rows:
        # PS-212: Filter out rows with no cost centre
        if not r["cost_centre"]:
            skipped.append({
                "employee_id": r["employee_id"],
                "name": r["name"],
                "week": r["week"],
                "day": r["day"],
                "minutes": r["minutes"]
            })
            continue
            
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
        
        # PS-211: Split into regular and overtime on rounded minutes
        regular = min(b["minutes"], cap)
        overtime = max(0, b["minutes"] - cap)
        
        # Pay overtime at 1.5x rate
        rate = Decimal(b["rate_cents"])
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * Decimal("1.5") / 60)
        
        b = dict(b)
        b["regular_minutes"] = regular
        b["overtime_minutes"] = overtime
        b["gross_cents"] = int(gross)
        out.append(b)
    
    return out, skipped


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
