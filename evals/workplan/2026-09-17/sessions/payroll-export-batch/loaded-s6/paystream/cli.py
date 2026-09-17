"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet, sftp


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing files")
    p.add_argument("--no-upload", action="store_true", help="skip SFTP upload to finance server")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, excluded = payrun.build(rows, settings)
    
    # PS-212: Report excluded rows
    if excluded:
        print("WARNING: %d rows excluded (missing cost_centre):" % len(excluded))
        for ex in excluded:
            print("  - %s (%s) week %s day %s: %d minutes" % (
                ex["employee_id"], ex["name"], ex["week"], ex["day"], ex["minutes"]))
        print()
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("rows: %d" % len(entries))
        print("total_cents: %d" % total)
        if excluded:
            print("excluded_rows: %d" % len(excluded))
        return 0
    
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    if excluded:
        print("excluded_rows: %d" % len(excluded))
    
    # SFTP upload to finance server
    if not args.no_upload:
        sftp_config = sftp.load_sftp_config()
        if sftp_config:
            if not sftp.push_to_finance(args.out, sftp_config):
                print("WARNING: File written locally but SFTP upload failed", file=sys.stderr)
                return 1
        else:
            print("WARNING: SFTP credentials not configured (set FINANCE_SFTP_* env vars)", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
