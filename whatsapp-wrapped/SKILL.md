---
name: whatsapp-wrapped
description: Turn a WhatsApp "Export chat" file (.txt or .zip, iOS or Android, any date locale) into a Spotify-Wrapped-style recap, with a self-contained HTML page and 9:16 PNG story cards ready to post. Everything runs on this device and no chat content is uploaded. Use when someone wants a WhatsApp Wrapped, a recap or stats of a group chat or a chat with one person, who texts the most, chat awards, or shareable story cards from a chat export.
license: Apache-2.0
metadata:
  version: "1.0.1"
---

# WhatsApp Wrapped

A Spotify-Wrapped-style recap of one WhatsApp chat, made on this device.

## Privacy rules (read first)

- Run only on an export the user gives you. Never go looking for chat files on the machine.
- Everything stays on this device: the parser and stats use the Python standard library only. The page and cards
  contain no external URLs, and the PNG renderer blocks every network request.
- Do not read or quote the chat content back into the conversation. Run the script and report the output paths
  and the headline numbers it prints. Open the rendered PNGs only if you need to check how they look.
- The cards show names, counts, top emojis and top words. Before the user shares them, remind them that
  everyone in the chat appears on them. `--no-words` leaves the top words off.

## Step 1: get the export

Tell the user how, if they do not have it yet:
- **iPhone:** open the chat > tap the name at the top > Export Chat > Without Media. This gives a `.zip` with `_chat.txt`.
- **Android:** open the chat > three dots > More > Export chat > Without media. This gives a `.txt` (sometimes a `.zip`).

"Without media" is enough. Voice notes, photos and stickers are still counted from the placeholders in the text.

## Step 2: run it

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/wrapped.py "<path to export .zip or .txt>" --out "<folder>"
```

Options:
- `--title "Sunday League"`: the chat name to show. Without it, the name comes from the file name, which is
  `_chat.txt` for some exports, so pass a title when the file name is not the chat name.
- `--no-words`: leave the top words off the cards.
- `--date-order dmy|mdy|ymd`: override day/month detection. Only needed for very short chats where every date is
  ambiguous (for example everything on 03/04).
- `--no-png`: write only the HTML page.
- `--json`: also write `stats.json`.

The script prints the detected platform and date order. If a date looks wrong to the user, rerun with `--date-order`.

## Step 3: what comes out

- `<folder>/wrapped.html`: one self-contained page with every card and a per-person table. It opens offline and works on a phone.
- `<folder>/cards/NN-*.png`: 1080x1920 story cards. Order: cover, who talked the most (a head-to-head for two-person chats),
  when the chat comes alive, longest streak, emojis and words, fastest replies and who starts conversations,
  voice notes and media, awards (one per person), summary.
- The summary card is the one to post if they post only one.

PNG rendering needs a headless Chromium: Playwright for Python if installed, otherwise a local Chrome, Chromium, Edge or
Brave. Without either, the HTML page still has every card; suggest `pip install playwright && playwright install chromium`.

## What it measures

- Messages per person and share, words, words per message.
- Peak hour, weekday split, busiest single day, messages on an average day.
- Longest streak of consecutive days with at least one message, plus a day grid.
- Top emojis (skin tones, flags and joined emojis count as one).
- Top words: the words this chat keeps coming back to, not the most common ones. Stopwords and chat filler in
  EN, DE, IT and ES (plus short PT and FR lists) are removed, words need 4 or more letters, names of people in the
  chat never count, a long message pasted or forwarded again and again counts once, and the rest are ranked by TF-IDF against the chat's own baseline (each conversation is a
  document), so a word that shows up in most conversations is dropped and a word the chat returns to in bursts wins.
- Typical reply time: the median time a person takes to answer someone else, counting gaps up to 6 hours.
- Who starts conversations: a conversation starts after 4 hours of silence.
- Voice notes, photos, videos, stickers, GIFs, files and deleted messages. Android exports only say "Media omitted"
  for most media, so photos, videos and stickers are shown as one number there. Voice notes are still counted.
- One distinct award per person (The Main Character, Voice Note Royalty, Speed Demon, The Icebreaker, Night Owl,
  Early Bird, The Novelist, Emoji Artist, The Paparazzi, Sticker Machine, Laugh Track, The Closer, The Eraser and more),
  each with the number behind it.

## Formats handled

iOS and Android, `.txt` or `.zip`; `[date, time] Name:` and `date, time - Name:`; day-first, month-first and year-first dates
with `/`, `.` or `-`; 24h and 12h clocks (AM/PM, a. m./p. m., vorm./nachm. and others); invisible direction marks and narrow
spaces; multi-line messages; system notices (encryption notice, group created, added) are skipped; edited messages
are counted once. Day/month order is detected from values over 12, then from which order keeps the chat in time order.

## Testing

```bash
cd ${CLAUDE_SKILL_DIR} && python3 -m unittest discover -s tests -v
python3 tests/make_synthetic.py /tmp/wa-synthetic   # fake chats in 5 export formats, no real data
```

Tests use synthetic chats only.
