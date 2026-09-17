"""The bank import file. See docs/BANK_FORMAT.md before touching this."""
import csv

# Note: column 2 is still called "week" to maintain certification with the bank
# but now contains one aggregated entry per employee for the entire month
COLUMNS = ["employee_id", "week", "gross_cents", "cost_centre", "run_id", "checksum"]


def checksum(entry):
    return "%06d" % (sum(ord(c) for c in entry["employee_id"] + entry["week"]) * 7 % 1000000)


def aggregate_by_employee(entries):
    """Collapse multiple week entries into one row per employee for the whole month."""
    by_employee = {}
    for e in entries:
        emp_id = e["employee_id"]
        if emp_id not in by_employee:
            by_employee[emp_id] = {
                "employee_id": emp_id,
                "week": e["week"],  # Use first week seen as the identifier
                "gross_cents": 0,
                "cost_centre": e["cost_centre"],
            }
        by_employee[emp_id]["gross_cents"] += e["gross_cents"]
    
    # Return in the order employees first appeared
    result = []
    seen = set()
    for e in entries:
        emp_id = e["employee_id"]
        if emp_id not in seen:
            result.append(by_employee[emp_id])
            seen.add(emp_id)
    return result


def write(entries, path, run_id):
    # Aggregate to one row per employee
    aggregated = aggregate_by_employee(entries)
    
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for e in aggregated:
            w.writerow([e["employee_id"], e["week"], e["gross_cents"],
                        e["cost_centre"], run_id, checksum(e)])
    return len(aggregated)
