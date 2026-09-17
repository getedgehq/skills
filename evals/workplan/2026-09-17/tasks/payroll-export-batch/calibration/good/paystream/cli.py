"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, sftp, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true",
                   help="print the totals without writing the bank file")
    p.add_argument("--upload", action="store_true",
                   help="push the written bank file to the finance sftp (needs vault credentials)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    rows, skipped = timesheet.split_missing_cost_centre(rows)
    entries = payrun.build(rows, settings)

    if args.dry_run:
        print("dry run, nothing written")
        print("rows: %d" % len(entries))
    else:
        bankfile.write(entries, args.out, args.run_id)
        print("rows: %d" % len(entries))
    print("total_cents: %d" % payrun.total_cents(entries))

    if skipped:
        who = sorted({"%s %s" % (r["employee_id"], r["name"]) for r in skipped})
        print("skipped %d row(s) with no cost centre: %s" % (len(skipped), "; ".join(who)))

    if args.upload:
        if args.dry_run:
            print("dry run, not uploading")
        else:
            sftp.push(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
