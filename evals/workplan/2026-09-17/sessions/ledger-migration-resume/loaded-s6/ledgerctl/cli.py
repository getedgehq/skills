"""ledgerctl command line interface."""
import argparse
import sys

from . import accounts, export, normalize


def build_parser():
    p = argparse.ArgumentParser(prog="ledgerctl")
    p.add_argument("--input", required=True, help="raw export csv")
    p.add_argument("--out", required=True, help="where to write the canonical json")
    p.add_argument("--since", help="filter to rows booked on or after this date (YYYY-MM-DD)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    rows = normalize.read_rows(args.input)
    rows = normalize.dedupe(rows)
    
    if args.since:
        rows = [r for r in rows if r["booked_on"] >= args.since]
    
    rows, unmapped = accounts.remap(rows)
    n = export.write_json(rows, args.out)
    
    print("wrote %d rows to %s" % (n, args.out))
    if unmapped:
        print("WARNING: %d unmapped account code(s): %s" % (len(unmapped), ", ".join(unmapped)))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
