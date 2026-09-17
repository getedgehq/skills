"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing anything")
    p.add_argument("--sftp-host", help="SFTP host for finance upload")
    p.add_argument("--sftp-key", help="path to SFTP private key")
    p.add_argument("--sftp-user", default="payroll", help="SFTP username")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    
    if not args.dry_run and not args.out:
        print("error: --out is required unless --dry-run is specified", file=sys.stderr)
        return 1
    
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, skipped = payrun.build(rows, settings)
    
    total = payrun.total_cents(entries)
    
    # Report skipped rows (PS-212)
    if skipped:
        print("WARNING: %d rows skipped (no cost_centre):" % len(skipped), file=sys.stderr)
        for s in skipped:
            print("  - %s (%s) week %s, %d minutes" % (
                s["employee_id"], s["name"], s["week"], s["minutes"]
            ), file=sys.stderr)
        print("", file=sys.stderr)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("employees: %d" % len(entries))
        print("total_cents: %d" % total)
        print("total_amount: $%.2f" % (total / 100))
        return 0
    
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    
    # SFTP upload if credentials provided
    if args.sftp_host and args.sftp_key:
        try:
            from . import sftp_upload
            sftp_upload.upload(args.out, args.sftp_host, args.sftp_user, args.sftp_key)
            print("uploaded to %s" % args.sftp_host)
        except Exception as e:
            print("SFTP upload failed: %s" % e, file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
