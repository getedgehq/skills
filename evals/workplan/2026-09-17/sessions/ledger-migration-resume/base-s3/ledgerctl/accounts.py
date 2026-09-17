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
    
    Returns (rows, unmapped) where:
    - rows: list of row dicts with account codes remapped (or kept as-is if unmapped)
    - unmapped: list of unique unmapped account codes in order first seen
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        r_copy = dict(r)
        
        if code in MAP:
            r_copy["account"] = MAP[code]
        else:
            # Keep the unmapped code and track it
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r_copy)
    
    return out, unmapped
