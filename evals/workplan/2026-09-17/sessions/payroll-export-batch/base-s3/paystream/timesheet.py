"""Reading and normalising raw timesheet rows."""
import csv
from decimal import Decimal, ROUND_HALF_UP


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    At the halfway point, rounds up (in employee's favor) per union agreement.
    """
    if step <= 1:
        return int(minutes)
    # Use Decimal for proper ROUND_HALF_UP rounding
    return int((Decimal(minutes) / step).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * step)


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
