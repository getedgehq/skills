"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing anything")
    p.add_argument("--sftp-push", action="store_true", help="push file to finance SFTP after writing")
    return p


def push_to_sftp(filepath):
    """Push the bank file to finance SFTP.
    
    Note: SFTP host and key are in the ops vault. This is a placeholder
    that would need vault credentials to implement.
    """
    print("ERROR: SFTP push requires ops vault credentials (host and key)")
    print("Please manually upload %s to finance SFTP" % filepath)
    return False


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, excluded = payrun.build(rows, settings)
    
    # Report on excluded rows (PS-212)
    if excluded:
        print("WARNING: %d rows excluded due to missing cost_centre:" % len(excluded))
        by_employee = {}
        for r in excluded:
            emp_id = r["employee_id"]
            name = r["name"]
            key = "%s (%s)" % (name, emp_id)
            by_employee[key] = by_employee.get(key, 0) + 1
        for emp, count in sorted(by_employee.items()):
            print("  - %s: %d rows" % (emp, count))
        print()
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("employees: %d" % len(set(e["employee_id"] for e in entries)))
        print("total_cents: %d" % total)
        print("total_dollars: %.2f" % (total / 100.0))
        return 0
    
    n = bankfile.write(entries, args.out, args.run_id)
    print("wrote: %s" % args.out)
    print("employees: %d" % n)
    print("total_cents: %d" % total)
    print("total_dollars: %.2f" % (total / 100.0))
    
    if args.sftp_push:
        if not push_to_sftp(args.out):
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
