"""ledgerctl command line interface."""
import argparse
import sys

from . import accounts, export, normalize


def build_parser():
    p = argparse.ArgumentParser(prog="ledgerctl")
    p.add_argument("--input", required=True, help="raw export csv")
    p.add_argument("--out", required=True, help="where to write the canonical json")
    p.add_argument("--since", help="only include transactions booked on or after this date (YYYY-MM-DD)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    rows = normalize.read_rows(args.input)
    rows = normalize.dedupe(rows)
    
    if args.since:
        rows = normalize.filter_since(rows, args.since)
    
    rows, unmapped = accounts.remap(rows)
    
    if unmapped:
        print("WARNING: unmapped account codes found:", file=sys.stderr)
        for code, count in sorted(unmapped.items()):
            print(f"  {code}: {count} transactions", file=sys.stderr)
    
    n = export.write_json(rows, args.out)
    print("wrote %d rows to %s" % (n, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
