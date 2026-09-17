"""Reading and normalising raw timesheet rows."""
import csv
import math


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Halfway points round UP in the employee's favor per union agreement.
    """
    if step <= 1:
        return int(minutes)
    # Use floor((minutes + step/2) / step) * step to round halfway up
    return int(math.floor((minutes + step / 2) / step)) * step


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
