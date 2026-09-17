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
    out = []
    unmapped = []
    for r in rows:
        r = dict(r)
        code = r["account"]
        if code in MAP:
            r["account"] = MAP[code]
        else:
            unmapped.append(code)
        out.append(r)
    return out, unmapped
