"""The bank import file."""
import csv

COLUMNS = ["employee_id", "gross_cents", "cost_centre", "run_id", "checksum"]


def checksum(entry):
    return "%06d" % (sum(ord(c) for c in entry["employee_id"]) * 7 % 1000000)


def write(entries, path, run_id):
    merged = {}
    for e in entries:
        m = merged.setdefault(e["employee_id"], dict(e, gross_cents=0))
        m["gross_cents"] += e["gross_cents"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for e in merged.values():
            w.writerow([e["employee_id"], e["gross_cents"], e["cost_centre"], run_id, checksum(e)])
    return len(merged)
