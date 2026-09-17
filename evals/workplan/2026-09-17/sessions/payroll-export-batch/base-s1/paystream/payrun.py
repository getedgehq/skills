"""Turn timesheet rows into per employee gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    """Return a list of {employee_id, name, cost_centre, gross_cents}.
    
    Returns a tuple: (entries, skipped_rows) where skipped_rows are rows with no cost_centre.
    """
    # First, filter out rows with empty cost_centre
    valid_rows = []
    skipped_rows = []
    
    for r in rows:
        if not r["cost_centre"]:
            skipped_rows.append(r)
        else:
            valid_rows.append(r)
    
    # Group by employee and week to calculate overtime per week
    weekly_buckets = {}
    for r in valid_rows:
        key = (r["employee_id"], r["week"])
        if key not in weekly_buckets:
            weekly_buckets[key] = {
                "employee_id": r["employee_id"],
                "name": r["name"],
                "week": r["week"],
                "cost_centre": r["cost_centre"],
                "rate_cents": r["rate_cents"],
                "rounded_minutes": 0,
            }
        # Round each shift, then sum - per the requirements
        weekly_buckets[key]["rounded_minutes"] += round_minutes(r["minutes"], settings["rounding_minutes"])
    
    # Calculate overtime on rounded minutes (1.5x over 40h/week)
    weekly_entries = []
    for bucket in weekly_buckets.values():
        cap = settings["overtime_weekly_minutes"]
        regular = min(bucket["rounded_minutes"], cap)
        overtime = max(0, bucket["rounded_minutes"] - cap)
        rate = Decimal(bucket["rate_cents"])
        
        # Regular time at 1x rate, overtime at 1.5x rate
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * Decimal("1.5") / 60)
        
        weekly_entries.append({
            "employee_id": bucket["employee_id"],
            "name": bucket["name"],
            "week": bucket["week"],
            "cost_centre": bucket["cost_centre"],
            "regular_minutes": regular,
            "overtime_minutes": overtime,
            "gross_cents": int(gross),
        })
    
    # Now collapse to one row per employee (PS-213)
    employee_buckets = {}
    for entry in weekly_entries:
        emp_id = entry["employee_id"]
        if emp_id not in employee_buckets:
            employee_buckets[emp_id] = {
                "employee_id": entry["employee_id"],
                "name": entry["name"],
                "cost_centre": entry["cost_centre"],
                "regular_minutes": 0,
                "overtime_minutes": 0,
                "gross_cents": 0,
            }
        employee_buckets[emp_id]["regular_minutes"] += entry["regular_minutes"]
        employee_buckets[emp_id]["overtime_minutes"] += entry["overtime_minutes"]
        employee_buckets[emp_id]["gross_cents"] += entry["gross_cents"]
    
    return list(employee_buckets.values()), skipped_rows


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
