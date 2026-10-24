"""SYNTHETIC chats seeded with fake names, phone numbers and secrets ("canaries") that must never leave the device."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_synthetic  # noqa: E402

GROUP_PEOPLE = {
    "Zebulon Quixtarr": make_synthetic.PEOPLE["Maya Lindqvist"],
    "Ottoline Wexbridge": make_synthetic.PEOPLE["Tom Okafor"],
    "+49 151 2345 6789": make_synthetic.PEOPLE["Priya Raman"],   # unsaved contacts show up as phone numbers
    "Ignatius Vromm": make_synthetic.PEOPLE["Lukas Brenner"],
    "Philippa Drax": make_synthetic.PEOPLE["Sofia Marino"],
}
DUO_PEOPLE = {"Zebulon Quixtarr": make_synthetic.PEOPLE["Maya Lindqvist"],
              "Ottoline Wexbridge": make_synthetic.PEOPLE["Priya Raman"]}
TITLE = "Quixtarr Secret Society"
SECRETS = [
    "call me on +1 415 555 0199",
    "my password is hunter2-CANARY-pw",
    "token sk-live-CANARY9f8e7d6c5b4a3",
    "AKIACANARY1234567890 is the access key",
    "IBAN DE89370400440532013000 for the deposit",
    "write to zeb.quixtarr@example.org",
    "I live at 742 Evergreen Terrace",
    "the door code is 90210-CANARY",
]
CANARIES = [
    "Zebulon", "Quixtarr", "Ottoline", "Wexbridge", "Ignatius", "Vromm", "Philippa", "Drax", "Maya", "Lindqvist",
    "+49 151 2345 6789", "4915123456789", "151 2345", "+1 415 555 0199", "4155550199", "555 0199",
    "hunter2", "CANARY", "sk-live", "AKIA", "DE89370400440532013000", "zeb.quixtarr", "example.org",
    "Evergreen", "90210", "Secret Society", TITLE,
]


def inject(conv: list) -> list:
    out, k = [], 0
    for i, (ts, sender, kind, text) in enumerate(conv):
        if kind == "text" and i % 37 == 0:
            text = SECRETS[k % len(SECRETS)]
            k += 1
        out.append((ts, sender, kind, text))
    return out


def write_group(path: Path) -> Path:
    conv = inject(make_synthetic.build_conversation(seed=5, people=GROUP_PEOPLE))
    path.write_text(make_synthetic.write_android(conv, TITLE, "en_gb"), encoding="utf-8")
    return path


def write_duo(path: Path) -> Path:
    conv = inject(make_synthetic.build_conversation(seed=9, days=120, people=DUO_PEOPLE))
    path.write_text(make_synthetic.write_android(conv, "Ottoline Wexbridge", "en_gb", group=False), encoding="utf-8")
    return path


def leaks(blob: bytes) -> list[str]:
    """Every canary found in blob, as raw UTF-8, lower case, or URL-encoded."""
    from urllib.parse import quote, quote_plus
    low = blob.lower()
    found = []
    for c in CANARIES:
        forms = {c.encode(), quote(c).encode(), quote_plus(c).encode()}
        if any(f in blob for f in forms) or c.lower().encode() in low:
            found.append(c)
    return found
