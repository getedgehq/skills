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


def filter_since(rows, since_date):
    """Filter rows to only those booked on or after since_date."""
    if not since_date:
        return rows
    return [r for r in rows if r["booked_on"] >= since_date]


def main(argv=None):
    args = build_parser().parse_args(argv)
    rows = normalize.read_rows(args.input)
    rows = normalize.dedupe(rows)
    rows, unmapped = accounts.remap(rows)
    
    if args.since:
        before = len(rows)
        rows = filter_since(rows, args.since)
        after = len(rows)
        if before > after:
            print("filtered %d rows before %s" % (before - after, args.since), file=sys.stderr)
    
    if unmapped:
        print("WARNING: %d unmapped account code(s): %s" % (len(unmapped), ", ".join(unmapped)), file=sys.stderr)
    
    n = export.write_json(rows, args.out)
    print("wrote %d rows to %s" % (n, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
