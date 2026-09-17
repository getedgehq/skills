"""Reading and normalising raw timesheet rows."""
import csv
from math import floor


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Halfway values round in the employee's favor (up), per union agreement.
    """
    if step <= 1:
        return int(minutes)
    # Add 0.5 then floor to get "round half up" behavior
    return int(floor(minutes / step + 0.5)) * step


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
