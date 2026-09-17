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
    
    Returns (remapped_rows, unmapped_codes).
    Unmapped codes are kept as-is in the output, and reported once each
    in the order first seen.
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        # Copy the row so we don't mutate input
        r_out = dict(r)
        
        if code in MAP:
            r_out["account"] = MAP[code]
        else:
            # Keep the unmapped code as-is
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r_out)
    
    return out, unmapped
