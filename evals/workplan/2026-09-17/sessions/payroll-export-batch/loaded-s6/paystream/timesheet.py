"""Reading and normalising raw timesheet rows."""
import csv
from decimal import Decimal, ROUND_HALF_UP


def round_minutes(minutes, step):
    """Round worked minutes to the nearest `step` minutes.
    
    Halfway points round UP in favor of the employee per union agreement.
    """
    if step <= 1:
        return int(minutes)
    # Use Decimal with ROUND_HALF_UP to ensure halfway points go up
    d = Decimal(minutes) / Decimal(step)
    rounded = d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(rounded * step)


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
