"""The bank import file. See docs/BANK_FORMAT.md before touching this."""
import csv

COLUMNS = ["employee_id", "week", "gross_cents", "cost_centre", "run_id", "checksum"]


def checksum(entry):
    week = entry.get("week", "")
    return "%06d" % (sum(ord(c) for c in entry["employee_id"] + week) * 7 % 1000000)


def write(entries, path, run_id):
    """Write bank import file.
    
    NOTE: PS-213 requests one line per employee for the whole month.
    This conflicts with the frozen v2 format which specifies one line per employee per week.
    Implementing as requested, but this may need v3 certification.
    """
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for e in entries:
            # For monthly aggregation, use run_id as week identifier
            # This maintains column structure while collapsing to one row per employee
            w.writerow([e["employee_id"], run_id, e["gross_cents"],
                        e["cost_centre"], run_id, checksum({"employee_id": e["employee_id"], "week": run_id})])
    return len(entries)
