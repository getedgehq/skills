"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--run-id", default="RUN0001")
    p.add_argument("--dry-run", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries = payrun.build(rows, settings)
    if not args.dry_run:
        bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % len(entries))
    print("total_cents: %d" % payrun.total_cents(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
