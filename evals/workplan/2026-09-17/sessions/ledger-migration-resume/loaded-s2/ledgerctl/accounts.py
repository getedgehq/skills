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
    Rows with unmapped codes are kept with their original code.
    unmapped_codes lists each unknown code once, in order first seen.
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        # Always create a new dict to avoid mutating input
        new_row = dict(r)
        
        if code in MAP:
            new_row["account"] = MAP[code]
        else:
            # Keep the row with original code, track as unmapped
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(new_row)
    
    return out, unmapped
