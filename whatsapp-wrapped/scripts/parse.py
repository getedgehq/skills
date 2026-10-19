"""Parse a WhatsApp "Export chat" file (.txt or .zip) into messages.

Standard library only. Nothing leaves the machine.

Handles:
- iOS:     [31/12/2023, 21:41:05] Name: text      (also 12/31/23, 9:41:05 PM, 31.12.23)
- Android: 31/12/2023, 21:41 - Name: text         (also 12/31/23, 9:41 PM - , 31.12.23, 21:41 - )
- ISO-ish: 2023-12-31, 21:41 - Name: text  /  [2023/12/31 21:41:05] Name: text
- Day/month order is detected from the data (values > 12, then chronological
  consistency), 12h clocks with AM/PM style markers in several languages,
  invisible direction marks, multi-line messages, system messages.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

INVISIBLE = re.compile(r"[\u200e\u200f\u200b\u200c\u200d\u2066-\u2069\ufeff\u202a-\u202e]")
SPACES = re.compile(r"[\u00a0\u202f\u2009\u2007]")

# Optional "[", date, separator, time, optional am/pm, optional "]", separator, rest
HEADER = re.compile(
    r"""^\[?
    (?P<date>\d{1,4}[./\-]\d{1,2}[./\-]\d{1,4})\.?
    [,\s]\s*
    (?P<ampm_pre>(?:午前|午後|오전|오후|上午|下午)\s?)?
    (?P<time>\d{1,2}[:.]\d{2}(?:[:.]\d{2})?)
    \s?(?P<ampm>[AaPp]\.?\s?[Mm]\.?|vorm\.|nachm\.|μ\.μ\.|π\.μ\.)?
    \]?
    (?:\s[-–]\s|\s|:\s)
    (?P<rest>.*)$""",
    re.X,
)

PM_WORDS = {"pm", "p.m.", "p. m.", "p.m", "nachm.", "μ.μ.", "午後", "오후", "下午"}
AM_WORDS = {"am", "a.m.", "a. m.", "a.m", "vorm.", "π.μ.", "午前", "오전", "上午"}

# Media / special markers, lower-cased, matched against the whole text.
MEDIA_PATTERNS = [
    ("voice", re.compile(r"(audio omitted|audio weggelassen|audio omitido|audio omesso|áudio ocultado|audio omis|ptt-\S+\.opus|\.opus\b|<attached: [^>]*-audio-[^>]*>|aud-\S+\.(?:opus|m4a|aac))")),
    ("photo", re.compile(r"(image omitted|bild weggelassen|imagen omitida|immagine omessa|imagem ocultada|image absente|img-\S+\.(?:jpe?g|png|webp)|<attached: [^>]*-photo-[^>]*>)")),
    ("video", re.compile(r"(video omitted|video weggelassen|video omitido|video omesso|vídeo ocultado|vidéo absente|vid-\S+\.(?:mp4|3gp|mov)|<attached: [^>]*-video-[^>]*>)")),
    ("sticker", re.compile(r"(sticker omitted|sticker weggelassen|sticker omitido|sticker omesso|figurinha omitida|stk-\S+\.webp|<attached: [^>]*-sticker-[^>]*>)")),
    ("gif", re.compile(r"(gif omitted|gif weggelassen|gif omitido|gif omessa|<attached: [^>]*-gif-[^>]*>)")),
    ("document", re.compile(r"(document omitted|dokument weggelassen|documento omitido|documento omesso|\(file attached\)|\(datei angehängt\)|<attached: [^>]*>)")),
    ("media", re.compile(r"^<(media omitted|medien ausgeschlossen|multimedia omitido|media omessi|mídia oculta|médias omis|fichier omis)>$")),
]
DELETED = re.compile(
    r"^(this message was deleted\.?|you deleted this message\.?|diese nachricht wurde gelöscht\.?|du hast diese nachricht gelöscht\.?|"
    r"se eliminó este mensaje\.?|eliminaste este mensaje\.?|questo messaggio è stato eliminato\.?|hai eliminato questo messaggio\.?|"
    r"mensagem apagada\.?|você apagou esta mensagem\.?|ce message a été supprimé\.?|vous avez supprimé ce message\.?)$"
)
EDITED = re.compile(r"\s*<(this message was edited|diese nachricht wurde bearbeitet|se editó este mensaje|messaggio modificato|mensagem editada|ce message a été modifié)>\s*$", re.I)
CALL = re.compile(r"(missed (voice|video) call|voice call|video call|verpasster (sprach|video)anruf|llamada perdida|chiamata persa)", re.I)
VIEW_ONCE = re.compile(r"^(null|view once (photo|video|voice message))$", re.I)


@dataclass
class Message:
    ts: datetime
    sender: str
    text: str
    kind: str = "text"  # text | voice | photo | video | sticker | gif | document | media | deleted | call
    edited: bool = False


@dataclass
class Chat:
    title: str
    messages: list[Message] = field(default_factory=list)
    platform: str = "unknown"  # ios | android | unknown
    date_order: str = "dmy"
    system_lines: int = 0


def read_export(path: str | Path) -> tuple[str, str]:
    """Return (title, text). Accepts a .txt or a WhatsApp .zip (reads only the chat .txt inside)."""
    p = Path(path)
    title = p.stem
    for prefix in ("WhatsApp Chat with ", "WhatsApp Chat - ", "WhatsApp-Chat mit ", "Chat de WhatsApp con ", "Chat WhatsApp con "):
        if title.startswith(prefix):
            title = title[len(prefix):]
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".txt") and not n.startswith("__MACOSX")]
            if not names:
                raise ValueError("No chat .txt found inside the zip")
            # _chat.txt (iOS) or "WhatsApp Chat with X.txt" (Android); pick the largest .txt
            name = max(names, key=lambda n: zf.getinfo(n).file_size)
            raw = zf.read(name)
            if not name.endswith("_chat.txt"):
                title = Path(name).stem.replace("WhatsApp Chat with ", "").replace("WhatsApp Chat - ", "")
    else:
        raw = p.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            text = raw.decode(enc)
            if enc == "utf-16" and "\x00" in text:
                continue
            return title, text
        except UnicodeDecodeError:
            continue
    return title, raw.decode("utf-8", errors="replace")


def _split_date(d: str) -> tuple[int, int, int, str]:
    parts = re.split(r"[./\-]", d)
    a, b, c = (int(x) for x in parts)
    sep = re.findall(r"[./\-]", d)[0]
    return a, b, c, sep


def _detect_order(dates: list[str], times: list[tuple[int, int]], twelve_hour: bool = False) -> str:
    """Return 'ymd', 'dmy' or 'mdy'."""
    if not dates:
        return "dmy"
    parsed = [_split_date(d) for d in dates]
    if all(len(d.split(re.findall(r"[./\-]", d)[0])[0]) == 4 for d in dates[:50]):
        return "ymd"
    if any(a > 12 for a, _, _, _ in parsed):
        return "dmy"
    if any(b > 12 for _, b, _, _ in parsed):
        return "mdy"
    # Ambiguous: pick the order that keeps the chat chronological.
    def backwards(order: str) -> int:
        prev, n = None, 0
        for (a, b, c, _), (h, m) in zip(parsed, times):
            y = c + 2000 if c < 100 else c
            mo, da = (b, a) if order == "dmy" else (a, b)
            key = (y, mo, da, h, m)
            if prev and key < prev:
                n += 1
            prev = key
        return n
    dmy, mdy = backwards("dmy"), backwards("mdy")
    if mdy < dmy:
        return "mdy"
    if dmy < mdy:
        return "dmy"
    # Still a tie (short chats). Month-first is mostly a US habit, and the US uses a 12h clock.
    return "mdy" if (twelve_hour and parsed[0][3] == "/") else "dmy"


def _hour(time_s: str, ampm: str | None) -> tuple[int, int, int]:
    bits = [int(x) for x in re.split(r"[:.]", time_s)]
    h, m = bits[0], bits[1]
    s = bits[2] if len(bits) > 2 else 0
    if ampm:
        word = ampm.strip().lower()
        if word in PM_WORDS or word.replace(" ", "") in {"pm", "p.m."}:
            h = h % 12 + 12
        elif word in AM_WORDS or word.replace(" ", "") in {"am", "a.m."}:
            h = h % 12
    return h, m, s


def classify(text: str) -> str:
    low = text.strip().lower()
    if DELETED.match(low):
        return "deleted"
    if VIEW_ONCE.match(low):
        return "media"
    for kind, rx in MEDIA_PATTERNS:
        if rx.search(low):
            return kind
    if len(low) < 60 and CALL.search(low):
        return "call"
    return "text"


def parse_text(text: str, title: str = "Chat", date_order: str | None = None) -> Chat:
    lines = text.splitlines()
    raw: list[dict] = []
    platform_votes = {"ios": 0, "android": 0}
    for line in lines:
        clean = SPACES.sub(" ", INVISIBLE.sub("", line))
        m = HEADER.match(clean)
        if m:
            platform_votes["ios" if clean.startswith("[") else "android"] += 1
            ampm = m.group("ampm") or m.group("ampm_pre")
            # iOS marks system notices and media with an invisible mark right after "Name: "
            inv_body = bool(re.search(r":\s[\u200e\u200f]", line[:200]))
            raw.append({"date": m.group("date"), "time": m.group("time"), "ampm": ampm,
                        "rest": m.group("rest"), "inv": inv_body})
        elif raw:
            raw[-1]["rest"] += "\n" + clean
    times = []
    for r in raw:
        h, mi, _ = _hour(r["time"], r["ampm"])
        times.append((h, mi))
    order = date_order or _detect_order([r["date"] for r in raw], times, any(r["ampm"] for r in raw))
    chat = Chat(title=title, date_order=order,
                platform=max(platform_votes, key=platform_votes.get) if raw else "unknown")
    for r in raw:
        a, b, c, _ = _split_date(r["date"])
        if order == "ymd":
            y, mo, d = a, b, c
        elif order == "mdy":
            mo, d, y = a, b, c
        else:
            d, mo, y = a, b, c
        if y < 100:
            y += 2000
        h, mi, s = _hour(r["time"], r["ampm"])
        try:
            ts = datetime(y, mo, d, h, mi, s)
        except ValueError:
            chat.system_lines += 1
            continue
        rest = r["rest"]
        # "Name: text". System lines have no "Name: " part.
        sm = re.match(r"^(?P<sender>[^:\n]{1,80}?):\s(?P<body>.*)$", rest, re.S) or re.match(r"^(?P<sender>[^:\n]{1,80}?):(?P<body>)$", rest, re.S)
        if not sm:
            chat.system_lines += 1
            continue
        sender = sm.group("sender").strip()
        body = sm.group("body")
        # iOS system lines are written as "<Group name>: \u200eMessages and calls are end-to-end encrypted..."
        body_clean = INVISIBLE.sub("", body)
        kind = classify(body_clean)
        if kind == "text" and r["inv"]:
            chat.system_lines += 1
            continue
        edited = bool(EDITED.search(body_clean))
        if edited:
            body_clean = EDITED.sub("", body_clean)
        chat.messages.append(Message(ts=ts, sender=sender, text=body_clean.strip(), kind=kind, edited=edited))
    _drop_group_name_sender(chat)
    return chat


def _drop_group_name_sender(chat: Chat) -> None:
    """A 'sender' equal to the chat title whose lines are all system notices is not a person."""
    by: dict[str, list[Message]] = {}
    for m in chat.messages:
        by.setdefault(m.sender, []).append(m)
    for name, msgs in by.items():
        if name == chat.title and len(by) > 2 and all(m.kind in ("text",) and len(m.text) > 30 for m in msgs) and len(msgs) <= 3:
            chat.messages = [m for m in chat.messages if m.sender != name]
            chat.system_lines += len(msgs)


def parse_file(path: str | Path, date_order: str | None = None) -> Chat:
    title, text = read_export(path)
    return parse_text(text, title=title, date_order=date_order)


if __name__ == "__main__":
    import sys
    c = parse_file(sys.argv[1])
    print(c.title, c.platform, c.date_order, len(c.messages), "messages", c.system_lines, "system lines")
    for m in c.messages[:5]:
        print(m)
