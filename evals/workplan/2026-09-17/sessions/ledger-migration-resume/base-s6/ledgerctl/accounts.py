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
    Rows with unmapped codes are kept with the original code.
    unmapped_codes lists each unknown code once, in order first seen.
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        # Always make a copy to avoid mutating input
        r = dict(r)
        
        if code in MAP:
            r["account"] = MAP[code]
        else:
            # Keep the row but track that the code is unmapped
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r)
    
    return out, unmapped
