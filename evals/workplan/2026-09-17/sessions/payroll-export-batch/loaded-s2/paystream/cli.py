"""paystream command line interface."""
import argparse
import os
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing output file")
    p.add_argument("--no-sftp", action="store_true", help="skip SFTP upload even if configured")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, excluded = payrun.build(rows, settings)
    
    # PS-212: Report excluded rows
    if excluded:
        print("WARNING: %d rows excluded (empty cost_centre):" % len(excluded))
        for r in excluded:
            print("  - %s (%s), week %s, %d minutes" % (
                r["employee_id"], r["name"], r["week"], r["minutes"]))
        print()
    
    print("rows: %d" % len(entries))
    print("total_cents: %d" % payrun.total_cents(entries))
    
    if args.dry_run:
        print("\n(dry run - no file written)")
        return 0
    
    # Write bank file (frozen format, one row per employee per week)
    bankfile.write(entries, args.out, args.run_id)
    print("wrote: %s" % args.out)
    
    # PS-213: Also write reconciliation file (one row per employee for the month)
    base, ext = os.path.splitext(args.out)
    recon_path = base + "_reconciliation" + ext
    n_employees = bankfile.write_reconciliation(entries, recon_path, args.run_id)
    print("wrote: %s (%d employees)" % (recon_path, n_employees))
    
    # SFTP upload if configured
    if not args.no_sftp and "sftp" in settings:
        sftp_config = settings["sftp"]
        if all(sftp_config.get(k) for k in ["host", "username", "key_path", "remote_dir"]):
            from . import sftp
            print("\nUploading to finance SFTP...")
            if sftp.upload_to_finance(args.out, config=sftp_config):
                print("  uploaded: %s" % args.out)
            else:
                print("  WARNING: upload failed", file=sys.stderr)
        else:
            print("\nSFTP configured but missing credentials - skipping upload")
            print("  (add host, username, key_path, remote_dir to [sftp] section in paystream.ini)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
