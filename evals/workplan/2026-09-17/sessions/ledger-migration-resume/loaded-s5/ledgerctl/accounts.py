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
    
    Returns a tuple of (remapped_rows, unmapped_codes_dict) where
    unmapped_codes_dict maps code -> count of occurrences.
    """
    out = []
    unmapped = {}
    
    for r in rows:
        code = r["account"]
        r_copy = dict(r)
        
        if code in MAP:
            r_copy["account"] = MAP[code]
        else:
            # Keep the row with the unmapped code, track it
            unmapped[code] = unmapped.get(code, 0) + 1
        
        out.append(r_copy)
    
    return out, unmapped
