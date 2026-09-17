"""Reading and normalising raw timesheet rows."""
import csv
import math


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Per union agreement, partial units round in the employee's favour -
    anything at the halfway point goes up, not down.
    """
    if step <= 1:
        return int(minutes)
    # Use ceil at the halfway point to round in employee's favor
    remainder = minutes % step
    if remainder >= step / 2:
        return int(math.ceil(minutes / step)) * step
    else:
        return int(math.floor(minutes / step)) * step


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
