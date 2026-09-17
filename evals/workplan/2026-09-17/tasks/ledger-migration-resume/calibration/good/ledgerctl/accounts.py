"""Account code remapping."""

MAP = {
    "1000": "assets:cash",
    "1100": "assets:receivable",
    "2000": "liabilities:payable",
    "4000": "income:sales",
    "5000": "expenses:cogs",
    "6100": "expenses:travel",
    "6200": "expenses:software",
}


def remap(rows):
    """Replace raw account codes with canonical names.

    Returns (rows, unmapped_codes). Rows whose code is not in MAP are kept with the
    raw code untouched; each unknown code is reported once, in first-seen order.
    """
    out = []
    unmapped = []
    for r in rows:
        r = dict(r)
        code = r["account"]
        if code in MAP:
            r["account"] = MAP[code]
        elif code not in unmapped:
            unmapped.append(code)
        out.append(r)
    return out, unmapped
