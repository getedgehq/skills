"""Generate SYNTHETIC WhatsApp exports (fake people, fake messages) for testing.

The same fake conversation is written in several real export formats so the
parser can be checked for parity:
  ios_en_us.txt        [12/31/25, 9:41:05 PM] Name: text      (iOS, US locale, 12h)
  ios_de.zip           [31.12.25, 21:41:05] Name: text         (iOS, German locale, zip with _chat.txt)
  android_en_gb.txt    31/12/2025, 21:41 - Name: text          (Android, UK locale, 24h)
  android_en_us.zip    12/31/25, 9:41 PM - Name: text          (Android, US locale, 12h, zip)
  duo_android.txt      a two-person chat (Android, 24h)
"""
from __future__ import annotations

import random
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

NNBSP = "\u202f"
LRM = "\u200e"

PEOPLE = {
    # name: (weight, night_bias, voice_rate, emoji_rate, length, reply_speed_min, media_rate, sticker_rate, starter_bias)
    "Maya Lindqvist": (1.6, 0.05, 0.02, 0.55, 9, 2, 0.04, 0.01, 1.8),
    "Tom Okafor": (1.2, 0.35, 0.03, 0.15, 6, 6, 0.03, 0.06, 0.8),
    "Priya Raman": (1.0, 0.02, 0.22, 0.25, 7, 12, 0.03, 0.01, 1.0),
    "Lukas Brenner": (0.8, 0.04, 0.01, 0.05, 19, 25, 0.02, 0.0, 0.7),
    "Sofia Marino": (0.9, 0.08, 0.03, 0.35, 5, 4, 0.15, 0.02, 1.0),
    "Jonah Weiss": (0.45, 0.10, 0.02, 0.10, 4, 45, 0.02, 0.12, 0.5),
}

TOPICS = {
    "football": ["kickoff is at 7 tomorrow", "who is bringing the ball", "we need a keeper again", "pitch 3 is booked",
                 "that last goal was unreal", "same team as last week?", "my knee says no but I am coming", "bibs are in my car"],
    "food": ["pizza after?", "that ramen place on Elm is open again", "who ordered the tacos", "I am starving",
             "brunch on sunday?", "the dumplings were elite", "bringing banana bread", "coffee first"],
    "trip": ["Lisbon flights dropped to 89", "airbnb link in a sec", "we land at 10:40", "pack sunscreen",
             "who has the gate number", "beach day or castle day", "the sunset tonight", "train leaves 9:15"],
    "plans": ["are we still on for friday", "running 10 min late", "on my way", "here", "saved you a seat",
              "can someone grab ice", "doors at 8", "see you there"],
    "banter": ["no way", "this is the best chat", "who said that", "classic", "I cannot believe this", "stop it",
               "you are so right", "honestly iconic", "never again", "ok fair"],
}
EMOJIS = ["😂", "🔥", "⚽", "🙌", "❤️", "😭", "👀", "🍕", "🎉", "👍", "🥲", "😅", "🌊", "🤝", "👏🏽", "🇵🇹"]
LAUGHS = ["haha", "hahaha", "lol", "lmao"]


def build_conversation(seed: int = 7, start=datetime(2025, 4, 1, 8, 0), days: int = 200, people=PEOPLE):
    rnd = random.Random(seed)
    names = list(people)
    out = []  # (ts, sender, kind, text)
    day = start
    for d in range(days):
        date0 = start + timedelta(days=d)
        weekend = date0.weekday() >= 5
        # some quiet days break streaks, a long run in the middle
        if 60 <= d <= 101:
            p_active = 1.0
        else:
            p_active = 0.86 if not weekend else 0.93
        if rnd.random() > p_active:
            continue
        n_bursts = rnd.choice([1, 1, 2, 2, 3, 4]) + (1 if weekend else 0)
        if d in (130, 131):  # the trip: very busy days
            n_bursts = 9
        for _ in range(n_bursts):
            starter = rnd.choices(names, weights=[people[n][0] * people[n][8] for n in names])[0]
            night = rnd.random() < people[starter][1] * 2.2
            hour = rnd.choice([0, 1, 1, 2, 23]) if night else rnd.choices(range(7, 23), weights=[1, 2, 3, 3, 4, 4, 3, 3, 3, 4, 5, 7, 8, 9, 7, 5])[0]
            ts = date0.replace(hour=hour, minute=rnd.randrange(60), second=rnd.randrange(60))
            topic = rnd.choice(list(TOPICS))
            sender = starter
            for _k in range(rnd.randint(3, 22) + (10 if d in (130, 131) else 0)):
                out.append((ts, sender, *make_message(rnd, sender, topic, people)))
                # next speaker
                nxt = rnd.choices(names, weights=[people[n][0] * (0.35 if n == sender else 1) for n in names])[0]
                speed = people[nxt][5] if nxt != sender else 1.5
                ts = ts + timedelta(seconds=max(4, int(rnd.expovariate(1 / (speed * 60)))))
                sender = nxt
    out.sort(key=lambda x: x[0])
    return out


def make_message(rnd, sender, topic, people):
    w, night, voice, emo, length, _s, media, sticker, _st = people[sender]
    r = rnd.random()
    if r < voice:
        return "voice", ""
    r -= voice
    if r < media:
        return rnd.choice(["photo", "photo", "photo", "video"]), ""
    r -= media
    if r < sticker:
        return rnd.choice(["sticker", "sticker", "gif"]), ""
    if rnd.random() < 0.004:
        return "deleted", ""
    base = rnd.choice(TOPICS[topic])
    extra = []
    while len(" ".join([base] + extra).split()) < rnd.randint(max(1, length - 4), length + 4):
        extra.append(rnd.choice(TOPICS[rnd.choice(list(TOPICS))]))
        if length < 8:
            break
    text = ", ".join([base] + extra) if length >= 12 else base
    if rnd.random() < 0.18:
        text = rnd.choice(LAUGHS) + " " + text
    if rnd.random() < 0.08:
        text += "?"
    if rnd.random() < emo:
        text += " " + "".join(rnd.choice(EMOJIS) for _ in range(rnd.choice([1, 1, 2, 3])))
    if rnd.random() < 0.01:
        text += " https://example.com/" + str(rnd.randrange(9999))
    if rnd.random() < 0.04:
        text = text + "\nalso " + rnd.choice(TOPICS["plans"])  # multi-line message
    return "text", text


# ---- writers ----

def _ios_media(kind, ts, n, locale):
    stamp = ts.strftime("%Y-%m-%d-%H-%M-%S")
    if locale == "de":
        omitted = {"photo": "Bild weggelassen", "video": "Video weggelassen", "sticker": "Sticker weggelassen",
                   "gif": "GIF weggelassen", "voice": "Audio weggelassen"}
        return LRM + omitted[kind]
    tag = {"photo": "PHOTO", "video": "VIDEO", "sticker": "STICKER", "gif": "GIF", "voice": "AUDIO"}[kind]
    ext = {"photo": "jpg", "video": "mp4", "sticker": "webp", "gif": "mp4", "voice": "opus"}[kind]
    return f"{LRM}<attached: {n:08d}-{tag}-{stamp}.{ext}>"


def write_ios(conv, title, locale="en_us"):
    lines = []
    first = conv[0][0] - timedelta(minutes=5)
    if locale == "en_us":
        hdr = lambda ts: f"[{ts.month}/{ts.day}/{ts:%y}, {ts.hour % 12 or 12}:{ts:%M:%S}{NNBSP}{'PM' if ts.hour >= 12 else 'AM'}]"
        sys_line = f"{hdr(first)} {title}: {LRM}Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them."
        deleted = LRM + "This message was deleted."
    else:
        hdr = lambda ts: f"[{ts:%d.%m.%y}, {ts:%H:%M:%S}]"
        sys_line = f"{hdr(first)} {title}: {LRM}Nachrichten und Anrufe sind Ende-zu-Ende-verschlüsselt."
        deleted = LRM + "Diese Nachricht wurde gelöscht."
    lines.append(sys_line)
    lines.append(f"{LRM}{hdr(first)} {title}: {LRM}Maya Lindqvist created group “{title}”")
    for n, (ts, sender, kind, text) in enumerate(conv, 1):
        if kind == "text":
            body = text
        elif kind == "deleted":
            body = deleted
        else:
            body = _ios_media(kind, ts, n, locale)
        prefix = LRM if kind not in ("text",) else ""
        lines.append(f"{prefix}{hdr(ts)} {sender}: {body}")
    return "\n".join(lines) + "\n"


def write_android(conv, title, locale="en_gb", group=True):
    lines = []
    if locale == "en_gb":
        hdr = lambda ts: f"{ts:%d/%m/%Y}, {ts:%H:%M} -"
    else:
        hdr = lambda ts: f"{ts.month}/{ts.day}/{ts:%y}, {ts.hour % 12 or 12}:{ts:%M}{NNBSP}{'PM' if ts.hour >= 12 else 'AM'} -"
    first = conv[0][0] - timedelta(minutes=5)
    lines.append(f"{hdr(first)} Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.")
    if group:
        lines.append(f"{hdr(first)} Maya Lindqvist created group \"{title}\"")
        lines.append(f"{hdr(first)} Maya Lindqvist added you")
    for n, (ts, sender, kind, text) in enumerate(conv, 1):
        if kind == "text":
            body = text
        elif kind == "deleted":
            body = "This message was deleted"
        elif kind == "voice":
            body = f"PTT-{ts:%Y%m%d}-WA{n % 10000:04d}.opus (file attached)"
        else:
            body = "<Media omitted>"
        lines.append(f"{hdr(ts)} {sender}: {body}")
    return "\n".join(lines) + "\n"


def main(outdir: str):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    title = "Sunday League ⚽"
    conv = build_conversation()
    (out / "ios_en_us.txt").write_text(write_ios(conv, title, "en_us"), encoding="utf-8")
    (out / "android_en_gb.txt").write_text(write_android(conv, title, "en_gb"), encoding="utf-8")
    with zipfile.ZipFile(out / "ios_de.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("_chat.txt", write_ios(conv, title, "de"))
    with zipfile.ZipFile(out / "android_en_us.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"WhatsApp Chat with {title}.txt", write_android(conv, title, "en_us"))
    duo_people = {k: PEOPLE[k] for k in ("Maya Lindqvist", "Priya Raman")}
    duo = build_conversation(seed=11, days=120, people=duo_people)
    (out / "duo_android.txt").write_text(write_android(duo, "Priya Raman", "en_gb", group=False), encoding="utf-8")
    print(f"wrote {len(conv)} synthetic group messages and {len(duo)} duo messages to {out}")
    return len(conv)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "synthetic")
