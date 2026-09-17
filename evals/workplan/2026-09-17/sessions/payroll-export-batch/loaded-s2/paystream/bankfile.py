"""The bank import file. See docs/BANK_FORMAT.md before touching this."""
import csv

COLUMNS = ["employee_id", "week", "gross_cents", "cost_centre", "run_id", "checksum"]


def checksum(entry):
    return "%06d" % (sum(ord(c) for c in entry["employee_id"] + entry["week"]) * 7 % 1000000)


def write(entries, path, run_id):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for e in entries:
            w.writerow([e["employee_id"], e["week"], e["gross_cents"],
                        e["cost_centre"], run_id, checksum(e)])
    return len(entries)


def write_reconciliation(entries, path, run_id):
    """PS-213: Write a collapsed reconciliation file with one row per employee for the month.
    
    This is separate from the bank file because the bank format is frozen/certified.
    """
    # Group entries by employee
    by_employee = {}
    for e in entries:
        emp_id = e["employee_id"]
        if emp_id not in by_employee:
            by_employee[emp_id] = {
                "employee_id": emp_id,
                "name": e["name"],
                "cost_centre": e["cost_centre"],
                "gross_cents": 0,
                "regular_minutes": 0,
                "overtime_minutes": 0,
            }
        by_employee[emp_id]["gross_cents"] += e["gross_cents"]
        by_employee[emp_id]["regular_minutes"] += e["regular_minutes"]
        by_employee[emp_id]["overtime_minutes"] += e["overtime_minutes"]
    
    # Write in employee_id order for consistency
    rows = sorted(by_employee.values(), key=lambda x: x["employee_id"])
    
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["employee_id", "name", "cost_centre", "regular_minutes", 
                    "overtime_minutes", "gross_cents", "run_id"])
        for r in rows:
            w.writerow([r["employee_id"], r["name"], r["cost_centre"],
                       r["regular_minutes"], r["overtime_minutes"],
                       r["gross_cents"], run_id])
    
    return len(rows)
