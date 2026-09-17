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
    """Replace raw account codes with canonical account names.
    
    Returns a tuple of (rows, unmapped_codes) where:
    - rows: all input rows with mapped codes replaced, unmapped codes left as-is
    - unmapped_codes: list of unmapped codes in order first seen
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        r_out = dict(r)
        
        if code in MAP:
            r_out["account"] = MAP[code]
        else:
            # Keep the row with the unmapped code
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r_out)
    
    return out, unmapped
