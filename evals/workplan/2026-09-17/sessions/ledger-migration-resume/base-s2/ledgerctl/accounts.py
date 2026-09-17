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
    
    Returns:
        (remapped_rows, unmapped_codes): A tuple of the list of remapped rows
        (with unmapped codes kept as-is) and a list of unique unmapped codes
        in the order they were first encountered.
    """
    out = []
    unmapped = []
    seen_unmapped = set()
    
    for r in rows:
        code = r["account"]
        # Always make a copy to avoid mutating the input
        row_copy = dict(r)
        
        if code in MAP:
            row_copy["account"] = MAP[code]
        else:
            # Keep the row but track unmapped codes
            if code not in seen_unmapped:
                unmapped.append(code)
                seen_unmapped.add(code)
        
        out.append(row_copy)
    
    return out, unmapped
