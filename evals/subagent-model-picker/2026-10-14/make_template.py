import pathlib, sys
root = pathlib.Path(sys.argv[1])
files = {
"ledgerkit/__init__.py": '"""ledgerkit: tiny bookkeeping helpers."""\n',
"ledgerkit/dates.py": '''from datetime import date


def parse_date(text):
    """Parse a date string into a datetime.date.

    Accepted formats:
      - ISO: YYYY-MM-DD           e.g. 2026-03-04 -> 4 March 2026
      - European: DD/MM/YYYY      e.g. 04/03/2026 -> 4 March 2026
      - European short: DD/MM/YY  e.g. 04/03/26   -> 4 March 2026 (years 00-69 -> 20xx, 70-99 -> 19xx)
    Surrounding whitespace is ignored. Anything else raises ValueError.
    """
    text = text.strip()
    if "-" in text:
        y, m, d = text.split("-")
        return date(int(y), int(m), int(d))
    if "/" in text:
        m, d, y = text.split("/")
        y = int(y)
        if len(str(y)) == 2:
            y += 2000
        return date(y, int(m), int(d))
    raise ValueError(f"unrecognised date: {text!r}")


def days_between(a, b):
    return abs((parse_date(b) - parse_date(a)).days)


def is_weekend(text):
    return parse_date(text).weekday() >= 5
''',
"ledgerkit/money.py": '''def to_cents(amount):
    """Convert a decimal string like "12.34" or "-0.5" to integer cents."""
    neg = amount.strip().startswith("-")
    whole, _, frac = amount.strip().lstrip("-").partition(".")
    cents = int(whole or 0) * 100 + int((frac + "00")[:2])
    return -cents if neg else cents


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def allocate(total_cents, weights):
    """Split total_cents into integer parts proportional to weights.

    Contract:
      - Returns a list of ints, same length as weights, summing exactly to total_cents.
      - Use the largest remainder method: give each part floor(total * w / sum(w)),
        then hand the leftover cents one by one to the parts with the largest
        fractional remainders. Ties go to the lower index.
      - A weight of 0 always gets 0.
      - Negative total_cents: allocate abs(total_cents) as above, then negate every part.
      - weights must be non-negative numbers (ints or floats). Raise ValueError if any
        weight is negative, if weights is empty, or if all weights are 0.
      - Exact arithmetic: do not let float rounding change the result for integer weights.
    """
    raise NotImplementedError


def total(amounts):
    return sum(to_cents(a) for a in amounts)
''',
"ledgerkit/report.py": '''from .money import format_cents, total


def summary_line(label, amounts):
    """Return 'label: <total>' with the total formatted as money."""
    return f"{label}: {format_cents(total(amounts))}"


def pad_label(label, width):
    return label.ljust(width)


def table(rows):
    width = max(len(r[0]) for r in rows) if rows else 0
    return "\\n".join(pad_label(l, width) + "  " + format_cents(c) for l, c in rows)


def _internal_helper(x):
    return x
''',
"tests/test_dates.py": '''from datetime import date
from ledgerkit.dates import parse_date


def test_iso():
    assert parse_date("2026-03-04") == date(2026, 3, 4)


def test_european():
    assert parse_date("04/03/2026") == date(2026, 3, 4)
''',
"config.ini": """[server]
host = ledger.internal
port = 8443
debug = no
timeout_s = 12.5

[export]
formats = csv, xlsx ,json
currency = EUR
round_half_even = yes
max_rows = 50000

[alerts]
emails = ops@example.com,finance@example.com
threshold = 0.75
enabled = true
""",
"TASKS.md": """# Tasks

Four independent tasks in this repo. Each one is self-contained.

1. **Inventory.** Create `INVENTORY.md` listing every public function (name not starting with `_`) defined at module level in `ledgerkit/` that has no docstring. One per line, formatted `module.function` (for example `dates.days_between`), sorted alphabetically, nothing else in the file.

2. **Date bug.** `tests/test_dates.py::test_european` fails. Fix `parse_date` in `ledgerkit/dates.py` so it honours its full docstring, including the short-year rule.

3. **Allocation.** Implement `allocate` in `ledgerkit/money.py` exactly as its docstring specifies.

4. **Config.** Convert `config.ini` to `config.json`: one JSON object per section, keys unchanged. Values: integers become JSON numbers, decimals become JSON numbers, `yes`/`true` become `true` and `no`/`false` become `false`, any value containing a comma becomes a list of trimmed strings, everything else stays a string. Do not delete `config.ini`.
""",
}
for k, v in files.items():
    p = root / k
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(v)
print("wrote", len(files))
