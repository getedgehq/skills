#!/usr/bin/env python3
"""Compare a source manifest with a destination manifest after a data copy.

Each manifest is a text file with one object per line: key<TAB>size (a third column, a checksum, is optional).
Prints "N of N copied, 0 left" and exits 0 when every source object is in the destination with the same size
(and the same checksum when both sides give one). Otherwise lists what is missing or different and exits 1.
Objects that exist only in the destination are reported as a count and do not fail the check.

    python3 manifest_diff.py source.tsv dest.tsv [--show 20]

Standard library only. Reads files; changes nothing.
"""
import argparse
import sys


def load(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2 or not parts[1].strip().isdigit():
                sys.exit("%s line %d: expected key<TAB>size[<TAB>checksum]" % (path, n))
            if parts[0] in out:
                sys.exit("%s line %d: duplicate key %r" % (path, n, parts[0]))
            out[parts[0]] = (int(parts[1]), parts[2].strip() if len(parts) > 2 and parts[2].strip() else None)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source")
    ap.add_argument("dest")
    ap.add_argument("--show", type=int, default=20, help="how many problem keys to print (default 20)")
    a = ap.parse_args()
    src, dst = load(a.source), load(a.dest)
    missing = sorted(k for k in src if k not in dst)
    differ = sorted(k for k in src if k in dst and (src[k][0] != dst[k][0] or (src[k][1] and dst[k][1] and src[k][1] != dst[k][1])))
    extra = len(set(dst) - set(src))
    left = len(missing) + len(differ)
    print("%d of %d copied, %d left" % (len(src) - left, len(src), left))
    if extra:
        print("%d objects exist only in the destination (not an error)" % extra)
    for label, keys in (("missing", missing), ("size or checksum differs", differ)):
        for k in keys[:a.show]:
            print("%s: %s" % (label, k))
        if len(keys) > a.show:
            print("... and %d more %s" % (len(keys) - a.show, label))
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
