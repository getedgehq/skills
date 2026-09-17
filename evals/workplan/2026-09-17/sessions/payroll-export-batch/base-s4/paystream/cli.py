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
    p.add_argument("--sftp-host", help="finance SFTP host (overrides ops vault)")
    p.add_argument("--sftp-keyfile", help="SFTP private key file (overrides ops vault)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, skipped = payrun.build(rows, settings)
    
    # PS-212: Report skipped rows
    if skipped:
        print("WARNING: %d rows skipped (no cost_centre):" % len(skipped), file=sys.stderr)
        for r in skipped:
            print("  %s (%s) - week %s, day %s, %d minutes" % (
                r["employee_id"], r["name"], r["week"], r["day"], r["minutes"]
            ), file=sys.stderr)
        print(file=sys.stderr)
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("entries: %d" % len(entries))
        print("total_cents: %d" % total)
        # Show per-employee breakdown
        by_emp = {}
        for e in entries:
            emp_id = e["employee_id"]
            if emp_id not in by_emp:
                by_emp[emp_id] = {"name": e["name"], "gross_cents": 0}
            by_emp[emp_id]["gross_cents"] += e["gross_cents"]
        
        print("\nPer-employee totals:")
        for emp_id in sorted(by_emp.keys()):
            info = by_emp[emp_id]
            print("  %s (%s): %d cents" % (emp_id, info["name"], info["gross_cents"]))
        return 0
    
    # Write the file
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    
    # Push to SFTP if configured
    # Note: SFTP credentials should come from ops vault, but we don't have access
    # For now, we'll just print a message indicating this step needs manual completion
    if args.sftp_host and args.sftp_keyfile:
        try:
            from . import sftp_push
            sftp_push.upload(args.out, args.sftp_host, args.sftp_keyfile)
            print("Uploaded to finance SFTP: %s" % args.sftp_host)
        except ImportError:
            print("WARNING: SFTP push requested but sftp_push module not available", file=sys.stderr)
        except Exception as e:
            print("ERROR: SFTP push failed: %s" % e, file=sys.stderr)
            return 1
    else:
        print("NOTE: File not pushed to SFTP (use --sftp-host and --sftp-keyfile, or configure in ops vault)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
