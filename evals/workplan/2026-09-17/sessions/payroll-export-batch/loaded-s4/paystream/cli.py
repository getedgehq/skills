"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing output file")
    p.add_argument("--sftp-push", action="store_true", help="push the output file to finance SFTP after writing")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    
    # PS-212: Report skipped rows
    skipped = payrun.get_skipped_rows(rows)
    if skipped:
        print("WARNING: %d rows skipped due to empty cost_centre:" % len(skipped), file=sys.stderr)
        for s in skipped:
            print("  - %s (%s), week %s, day %s, %d minutes" % 
                  (s["employee_id"], s["name"], s["week"], s["day"], s["minutes"]), 
                  file=sys.stderr)
    
    entries = payrun.build(rows, settings)
    total = payrun.total_cents(entries)
    
    print("rows: %d" % len(entries))
    print("total_cents: %d" % total)
    
    if args.dry_run:
        print("DRY RUN: no file written")
        return 0
    
    n = bankfile.write(entries, args.out, args.run_id)
    print("wrote: %s" % args.out)
    
    if args.sftp_push:
        try:
            from . import sftp_push
            sftp_push.push(args.out, settings)
            print("pushed to finance SFTP")
        except Exception as e:
            print("ERROR pushing to SFTP: %s" % e, file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
