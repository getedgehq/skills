"""ledgerctl command line interface."""
import argparse
import sys

from . import accounts, export, normalize


def build_parser():
    p = argparse.ArgumentParser(prog="ledgerctl")
    p.add_argument("--input", required=True, help="raw export csv")
    p.add_argument("--out", required=True, help="where to write the canonical json")
    p.add_argument("--since", help="only keep rows updated on or after this date")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    rows = normalize.read_rows(args.input)
    rows = normalize.dedupe(rows)
    if args.since:
        rows = [r for r in rows if r["updated_at"][:10] >= args.since]
    rows, unmapped = accounts.remap(rows)
    n = export.write_json(rows, args.out)
    print("wrote %d rows to %s" % (n, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
