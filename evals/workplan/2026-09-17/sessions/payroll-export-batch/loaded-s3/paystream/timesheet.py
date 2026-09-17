"""Reading and normalising raw timesheet rows."""
import csv
from math import floor


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Union agreement: halfway points round in the employee's favour (up).
    """
    if step <= 1:
        return int(minutes)
    # Calculate how many half-steps we have
    half_steps = minutes / (step / 2)
    # Round up at .0 (exact) and at 1.0 (halfway), down elsewhere
    # This is equivalent to: if on or above halfway, go up
    full_steps = int(floor((half_steps + 1) / 2))
    return full_steps * step


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
