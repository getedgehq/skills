"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", help="where to write the bank import file (required unless --dry-run)")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing any files")
    p.add_argument("--sftp-push", action="store_true", help="push completed file to finance SFTP")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    
    if not args.dry_run and not args.out:
        print("error: --out is required unless --dry-run is specified", file=sys.stderr)
        return 1
    
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, excluded = payrun.build(rows, settings)
    
    # Report excluded entries
    if excluded:
        print("WARNING: %d employee-week(s) excluded due to missing cost_centre:" % len(excluded))
        for e in excluded:
            print("  - %s (%s) week %s: %d minutes, %d cents" % (
                e["employee_id"], e["name"], e["week"], e["minutes"], e["gross_cents"]))
        print()
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("rows: %d" % len(entries))
        print("total_cents: %d" % total)
        if excluded:
            print("excluded_rows: %d" % len(excluded))
            print("excluded_cents: %d" % payrun.total_cents(excluded))
        return 0
    
    # Write the bank file
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    print("wrote: %s" % args.out)
    
    # Push to SFTP if requested
    if args.sftp_push:
        print("\nERROR: SFTP push not yet implemented (credentials not available)", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
