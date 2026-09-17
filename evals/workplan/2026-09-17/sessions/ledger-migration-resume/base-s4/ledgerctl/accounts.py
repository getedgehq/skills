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
    
    Returns a tuple: (remapped_rows, list_of_unmapped_codes)
    Unmapped codes are kept in the output and reported once in order of first appearance.
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        # Make a copy to avoid mutating the input
        r = dict(r)
        
        if code in MAP:
            r["account"] = MAP[code]
        else:
            # Keep the row with the original code
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r)
    
    return out, unmapped
