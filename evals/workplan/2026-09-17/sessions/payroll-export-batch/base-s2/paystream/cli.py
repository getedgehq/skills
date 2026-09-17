"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", 
                   help="print totals without writing the bank file")
    p.add_argument("--sftp-push", action="store_true",
                   help="push the bank file to finance SFTP after writing")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, excluded = payrun.build(rows, settings)
    
    # Report excluded rows (PS-212)
    if excluded:
        print("WARNING: %d rows excluded due to missing cost_centre:" % len(excluded), file=sys.stderr)
        # Group by employee for clearer reporting
        by_employee = {}
        for r in excluded:
            emp_id = r["employee_id"]
            if emp_id not in by_employee:
                by_employee[emp_id] = {"name": r["name"], "count": 0}
            by_employee[emp_id]["count"] += 1
        
        for emp_id in sorted(by_employee.keys()):
            info = by_employee[emp_id]
            print("  - %s (%s): %d rows" % (emp_id, info["name"], info["count"]), file=sys.stderr)
        print("", file=sys.stderr)
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no file written")
        print("rows: %d" % len(entries))
        print("total_cents: %d" % total)
        print("total_euros: %.2f" % (total / 100.0))
        if excluded:
            print("excluded_rows: %d" % len(excluded))
        return 0
    
    # Write the bank file
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    
    # SFTP push if requested
    if args.sftp_push:
        try:
            from . import sftp
            sftp.push_to_finance(args.out)
            print("Pushed to finance SFTP")
        except ImportError:
            print("ERROR: SFTP module not available", file=sys.stderr)
            return 1
        except Exception as e:
            print("ERROR: Failed to push to SFTP: %s" % e, file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
