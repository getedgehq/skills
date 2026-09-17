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
    
    Returns: (mapped_rows, unmapped_codes)
        mapped_rows: all input rows with account codes replaced where known,
                     kept as-is where not in MAP
        unmapped_codes: list of codes not in MAP, in order first seen
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        r = dict(r)  # Don't mutate input
        
        if code in MAP:
            r["account"] = MAP[code]
        else:
            # Keep the unmapped code in the output
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(r)
    
    return out, unmapped
