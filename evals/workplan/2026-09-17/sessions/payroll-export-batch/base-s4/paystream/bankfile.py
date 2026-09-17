"""The bank import file. See docs/BANK_FORMAT.md before touching this."""
import csv

COLUMNS = ["employee_id", "week", "gross_cents", "cost_centre", "run_id", "checksum"]


def checksum(entry):
    return "%06d" % (sum(ord(c) for c in entry["employee_id"] + entry["week"]) * 7 % 1000000)


def collapse_by_employee(entries):
    """PS-213: Collapse multiple week entries per employee into one row per employee.
    
    Uses the first week found as the week field, sums gross_cents.
    """
    by_employee = {}
    for e in entries:
        emp_id = e["employee_id"]
        if emp_id not in by_employee:
            by_employee[emp_id] = {
                "employee_id": emp_id,
                "week": e["week"],  # Use first week
                "gross_cents": 0,
                "cost_centre": e["cost_centre"],
            }
        by_employee[emp_id]["gross_cents"] += e["gross_cents"]
    
    # Return in original order of first appearance
    seen = set()
    result = []
    for e in entries:
        if e["employee_id"] not in seen:
            result.append(by_employee[e["employee_id"]])
            seen.add(e["employee_id"])
    return result


def write(entries, path, run_id):
    # PS-213: Collapse to one row per employee
    collapsed = collapse_by_employee(entries)
    
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for e in collapsed:
            w.writerow([e["employee_id"], e["week"], e["gross_cents"],
                        e["cost_centre"], run_id, checksum(e)])
    return len(collapsed)
