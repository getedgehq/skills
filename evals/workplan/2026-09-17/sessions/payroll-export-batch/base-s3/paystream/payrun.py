"""Turn timesheet rows into per employee-week gross pay."""
from decimal import Decimal

from .timesheet import round_minutes


def build(rows, settings):
    """Return a list of {employee_id, name, cost_centre, minutes, gross_cents}.
    
    Returns one entry per employee for all weeks combined (PS-213).
    Filters out rows with empty cost_centre and reports them (PS-212).
    Applies overtime rate of 1.5x for weekly minutes over the threshold (PS-211).
    """
    # Filter out rows with no cost_centre and track them
    filtered_rows = []
    missing_cost_centre = []
    
    for r in rows:
        if not r["cost_centre"]:
            missing_cost_centre.append(r)
        else:
            filtered_rows.append(r)
    
    # First, aggregate by employee and week to calculate weekly overtime
    week_buckets = {}
    week_order = []
    
    for r in filtered_rows:
        key = (r["employee_id"], r["week"])
        if key not in week_buckets:
            week_buckets[key] = {
                "employee_id": r["employee_id"],
                "name": r["name"],
                "week": r["week"],
                "cost_centre": r["cost_centre"],
                "rate_cents": r["rate_cents"],
                "minutes": 0,
            }
            week_order.append(key)
        week_buckets[key]["minutes"] += round_minutes(r["minutes"], settings["rounding_minutes"])

    # Calculate gross pay per week with overtime
    weekly_entries = []
    for key in week_order:
        b = week_buckets[key]
        cap = settings["overtime_weekly_minutes"]
        regular = min(b["minutes"], cap)
        overtime = max(0, b["minutes"] - cap)
        rate = Decimal(b["rate_cents"])
        
        # Regular pay + overtime at 1.5x (PS-211)
        gross = (Decimal(regular) * rate / 60) + (Decimal(overtime) * rate * Decimal("1.5") / 60)
        
        weekly_entries.append({
            "employee_id": b["employee_id"],
            "name": b["name"],
            "week": b["week"],
            "cost_centre": b["cost_centre"],
            "regular_minutes": regular,
            "overtime_minutes": overtime,
            "gross_cents": int(gross),
        })
    
    # Now collapse by employee (PS-213)
    employee_buckets = {}
    employee_order = []
    
    for entry in weekly_entries:
        emp_id = entry["employee_id"]
        if emp_id not in employee_buckets:
            employee_buckets[emp_id] = {
                "employee_id": emp_id,
                "name": entry["name"],
                "cost_centre": entry["cost_centre"],
                "regular_minutes": 0,
                "overtime_minutes": 0,
                "gross_cents": 0,
            }
            employee_order.append(emp_id)
        
        employee_buckets[emp_id]["regular_minutes"] += entry["regular_minutes"]
        employee_buckets[emp_id]["overtime_minutes"] += entry["overtime_minutes"]
        employee_buckets[emp_id]["gross_cents"] += entry["gross_cents"]
    
    # Build final output list
    out = [employee_buckets[emp_id] for emp_id in employee_order]
    
    return out, missing_cost_centre


def total_cents(entries):
    return sum(e["gross_cents"] for e in entries)
