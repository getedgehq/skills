"""Reading and normalising raw timesheet rows."""
import csv


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes, ties in the employee's favour."""
    if step <= 1:
        return int(minutes)
    q, r = divmod(int(minutes), step)
    return (q + 1) * step if r * 2 >= step else q * step


def split_missing_cost_centre(rows):
    """Return (rows with a cost centre, rows without one)."""
    kept, skipped = [], []
    for r in rows:
        (kept if r["cost_centre"] else skipped).append(r)
    return kept, skipped


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
