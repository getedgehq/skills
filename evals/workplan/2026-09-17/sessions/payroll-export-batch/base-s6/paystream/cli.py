"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet
from . import sftp


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
    entries, skipped = payrun.build(rows, settings)
    
    # PS-212: Report skipped rows with no cost centre
    if skipped:
        print("WARNING: %d rows skipped (no cost_centre):" % len(skipped), file=sys.stderr)
        for s in skipped:
            print("  %s (%s) - week %s, day %s: %d minutes" % 
                  (s["employee_id"], s["name"], s["week"], s["day"], s["minutes"]),
                  file=sys.stderr)
        print(file=sys.stderr)
    
    # Print summary
    total = payrun.total_cents(entries)
    print("employees: %d" % len(set(e["employee_id"] for e in entries)))
    print("rows: %d" % len(entries))
    print("total_cents: %d" % total)
    print("total_eur: %.2f" % (total / 100.0))
    
    if args.dry_run:
        print("\n--dry-run: not writing output file")
        return 0
    
    # Write the bank file
    n = bankfile.write(entries, args.out, args.run_id)
    print("\nwrote %d rows to %s" % (n, args.out))
    
    # SFTP push if requested
    if args.sftp_push:
        print("\nPushing to finance SFTP...", file=sys.stderr)
        success = sftp.push_to_finance_sftp(args.out)
        if not success:
            print("WARNING: SFTP push failed - see above for details", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
