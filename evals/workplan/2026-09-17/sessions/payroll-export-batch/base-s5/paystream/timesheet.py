"""Reading and normalising raw timesheet rows."""
import csv


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Per union agreement, partial units round in the employee's favour,
    so anything sitting exactly halfway goes up, never down.
    """
    if step <= 1:
        return int(minutes)
    # Calculate the remainder
    remainder = minutes % step
    # If remainder is exactly half or more, round up
    if remainder >= step / 2:
        return (minutes // step + 1) * step
    else:
        return (minutes // step) * step


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
