"""Reading and normalising raw timesheet rows."""
import csv
import math


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Union agreement: partial units round in employee's favour.
    Halfway points round UP, never down.
    """
    if step <= 1:
        return int(minutes)
    # Use floor + 0.5 comparison to detect exact halfway points
    # and always round them up
    ratio = minutes / step
    lower = math.floor(ratio)
    if ratio - lower >= 0.5:
        # At or above halfway: round up
        return (lower + 1) * step
    else:
        # Below halfway: round down
        return lower * step


def read_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
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
