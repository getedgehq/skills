"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    """Return a list of {employee_id, name, week, cost_centre, minutes, gross_cents}.
    
    Rows with empty cost_centre are excluded and reported separately.
    Returns (entries, excluded_rows) tuple.
    """
    # First, filter out rows with no cost centre
    excluded = []
    valid_rows = []
    for r in rows:
        if not r["cost_centre"]:
            excluded.append(r)
        else:
            valid_rows.append(r)
    
    # Build per-employee-week buckets
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
                "raw_minutes": [],
            }
            order.append(key)
        # Store raw minutes - we'll round each shift individually before summing
        buckets[key]["raw_minutes"].append(r["minutes"])
    
    # Calculate overtime per week on rounded minutes
    out = []
    for key in order:
        b = buckets[key]
        
        # Round each shift individually, then sum for the week
        rounded_minutes = [round_minutes(m, settings["rounding_minutes"]) for m in b["raw_minutes"]]
        total_minutes = sum(rounded_minutes)
        
        cap = settings["overtime_weekly_minutes"]
        regular = min(total_minutes, cap)
        overtime = max(0, total_minutes - cap)
        
        rate = Decimal(b["rate_cents"])
        # Regular time: minutes * rate / 60
        # Overtime: minutes * rate * 1.5 / 60
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * Decimal("1.5") / 60)
        
        entry = {
            "employee_id": b["employee_id"],
            "name": b["name"],
            "week": b["week"],
            "cost_centre": b["cost_centre"],
            "minutes": total_minutes,
            "regular_minutes": regular,
            "overtime_minutes": overtime,
            "gross_cents": int(gross),
        }
        out.append(entry)
    
    return out, excluded


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
