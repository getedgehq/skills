"""Personal edition and share-safe names, on SYNTHETIC data only (a fake ChatStorage.sqlite and fake exports)."""
import hashlib
import random
import sqlite3
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import make_synthetic  # noqa: E402
import wrapped  # noqa: E402
from parse import parse_file  # noqa: E402
from personal import APPLE_EPOCH, compute_personal, language_of, load_desktop_db, load_exports, localize  # noqa: E402
from render import build_cards  # noqa: E402
from render_personal import build_personal_cards, build_personal_page, initials, share_safe_chat  # noqa: E402
from stats import compute  # noqa: E402

TOKYO = timezone(timedelta(hours=9))
LINES = {
    "en": ["are you coming to the climbing gym tonight", "that sounds great, see you there", "what time does the train leave"],
    "de": ["ich bin heute abend nicht da", "kannst du mir bitte das schicken", "wir sehen uns dann morgen"],
    "it": ["ci vediamo domani sera allora", "non lo so ancora, ti faccio sapere", "che bello questo posto"],
}
# Chats in the fake database: (pk, session type, jid, name, language, members)
SESSIONS = [
    (1, 0, "111@s.whatsapp.net", "Ana Lima", "en", 0),
    (2, 0, "222@s.whatsapp.net", "Ben Vogel", "de", 0),
    (3, 0, "222222@lid", "Ben Vogel", "de", 0),          # same person after WhatsApp's id migration
    (4, 0, "333@s.whatsapp.net", "Carla Rossi", "it", 0),  # only from 2026: a new person
    (5, 1, "9001@g.us", "Climbing Crew", "en", 6),
    (6, 1, "9002@g.us", "Flat Market Buy&Sell", "en", 400),  # big group I barely write in
    (7, 0, "999@s.whatsapp.net", "‎You", "en", 0),   # notes to self
    (8, 2, "status@broadcast", "Broadcast", "en", 0),
    (9, 3, "status@status", "Status", "en", 0),
]


def visible(html: str) -> str:
    """Page text without inlined fonts, images and CSS, so base64 noise cannot match a name."""
    import re
    return re.sub(r"<style>.*?</style>|data:[^\"')]+", "", html, flags=re.S)


def apple(dt):
    return dt.timestamp() - APPLE_EPOCH


def make_db(path: Path) -> dict:
    """A tiny WhatsApp Desktop database with the tables and columns the loader reads. Times are Tokyo daytime."""
    rnd = random.Random(3)
    con = sqlite3.connect(path)
    con.executescript("""
      create table ZWACHATSESSION (Z_PK integer primary key, ZSESSIONTYPE integer, ZCONTACTJID varchar, ZPARTNERNAME varchar);
      create table ZWAGROUPMEMBER (Z_PK integer primary key, ZCHATSESSION integer, ZCONTACTNAME varchar, ZMEMBERJID varchar);
      create table ZWAMESSAGE (Z_PK integer primary key, ZCHATSESSION integer, ZISFROMME integer, ZMESSAGETYPE integer,
                               ZMESSAGEDATE timestamp, ZTEXT varchar);""")
    for pk, st, jid, name, _, members in SESSIONS:
        con.execute("insert into ZWACHATSESSION values (?,?,?,?)", (pk, st, jid, name))
        for i in range(members):
            con.execute("insert into ZWAGROUPMEMBER (ZCHATSESSION, ZCONTACTNAME) values (?,?)", (pk, f"Member{i} Zeta"))
    expect = {"sent": 0, "received": 0, "voice_sent": 0}
    lang = {pk: lg for pk, _, _, _, lg, _ in SESSIONS}

    def add(pk, me, mtype, when, text=None, counted=True):
        con.execute("insert into ZWAMESSAGE (ZCHATSESSION, ZISFROMME, ZMESSAGETYPE, ZMESSAGEDATE, ZTEXT) values (?,?,?,?,?)",
                    (pk, int(me), mtype, apple(when), text))
        if counted:
            expect["sent" if me else "received"] += 1
            expect["voice_sent"] += int(me and mtype == 3)

    day = datetime(2025, 9, 1, tzinfo=TOKYO)
    while day.date() <= date(2026, 3, 31):
        for pk in (1, 2, 3, 4, 5):
            if pk == 4 and day.year < 2026:
                continue
            if pk == 2 and day.year >= 2026 or pk == 3 and day.year < 2026:
                continue  # Ben's chat moves to a new id in 2026
            t = day.replace(hour=rnd.randint(9, 21), minute=rnd.randint(0, 59))
            for k in range(4):
                me = k % 2 == 0
                if pk == 1 and k == 0 and day.day % 5 == 0:
                    add(pk, me, 3, t)  # a voice note
                else:
                    add(pk, me, 0, t, rnd.choice(LINES[lang[pk]]) + (" 😂" if me and k == 2 else ""))
                t += timedelta(minutes=rnd.randint(1, 5))
        # Big market group: lots of others, me twice. Self chat, broadcast, status, system rows: never counted.
        for _ in range(5):
            add(6, False, 0, day.replace(hour=12), "selling a bike", counted=False)
        add(7, True, 0, day.replace(hour=13), "note to self", counted=False)
        add(8, True, 0, day.replace(hour=13), "broadcast", counted=False)
        add(9, False, 1, day.replace(hour=13), None, counted=False)
        add(1, False, 6, day.replace(hour=14), None, counted=False)  # system notice
        add(1, False, 59, day.replace(hour=14), None, counted=False)  # not a message
        day += timedelta(days=1)
    add(6, True, 0, datetime(2025, 10, 2, 12, tzinfo=TOKYO), "is it still available", counted=False)
    add(6, True, 0, datetime(2026, 2, 2, 12, tzinfo=TOKYO), "thanks", counted=False)
    con.commit()
    con.close()
    return expect


class DesktopDbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / "ChatStorage.sqlite"
        cls.expect = make_db(cls.db)
        cls.digest = hashlib.sha256(cls.db.read_bytes()).hexdigest()
        cls.recs, cls.info = load_desktop_db(cls.db)
        cls.zones = localize(cls.recs, "auto")
        cls.s = compute_personal(cls.recs, name_tokens=cls.info["name_tokens"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_original_untouched(self):
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), self.digest)

    def test_counts_and_exclusions(self):
        s = self.s
        self.assertEqual(s["sent"], self.expect["sent"])
        self.assertEqual(s["received"], self.expect["received"])
        self.assertEqual(s["voice_sent"], self.expect["voice_sent"])
        self.assertEqual(s["excluded_groups"], 1)  # the market group
        self.assertEqual(s["people_chats"], 3)     # Ana, Ben (two ids merged), Carla; no self chat
        self.assertEqual(s["group_chats"], 1)
        self.assertEqual(self.info["skipped_chats"], {"broadcast, status or channel": 2, "notes to self": 1})

    def test_auto_time_zone_finds_tokyo_offset(self):
        self.assertTrue(all(z in ("Asia/Tokyo",) for z in self.zones), self.zones)
        self.assertTrue(all(9 <= r.ts.hour <= 22 for r in self.recs if r.me))

    def test_fixed_time_zone(self):
        recs, _ = load_desktop_db(self.db)
        localize(recs, "UTC")
        self.assertTrue(all(0 <= r.ts.hour <= 13 for r in recs if r.me))

    def test_since_and_new_people(self):
        s = compute_personal(self.recs, since=date(2026, 1, 1), name_tokens=self.info["name_tokens"])
        self.assertEqual(s["first"], "2026-01-01")
        self.assertEqual([p["name"] for p in s["new_top"]], ["Carla Rossi"])  # Ben moved ids but is not new
        self.assertEqual(s["streak"]["days"], 90)

    def test_languages(self):
        self.assertEqual(set(self.s["langs"]), {"EN", "DE", "IT"})
        self.assertEqual(language_of("ich bin heute nicht da".split()), "DE")
        self.assertEqual(language_of("ci vediamo domani sera".split()), "IT")
        self.assertIsNone(language_of("ok ok".split()))

    def test_names_never_count_as_words(self):
        words = {w for w, _ in self.s["top_words"]}
        self.assertFalse(words & {"ana", "lima", "vogel", "carla", "rossi", "zeta"})

    def test_share_safe_cards_hide_names(self):
        cards = build_personal_cards(self.s, owner="Sam", safe=True)
        page = visible(build_personal_page(self.s, cards, None, owner="Sam", safe=True))
        for name in ("Ana", "Lima", "Ben", "Vogel", "Carla", "Rossi", "Climbing"):
            self.assertNotIn(name, page)
        self.assertIn("Person #1 · ", page)
        self.assertIn("Group #1", page)

    def test_real_cards_show_names_and_footer(self):
        cards = build_personal_cards(self.s, owner="Sam")
        keys = [k for k, _ in cards]
        self.assertEqual(keys[0], "cover")
        self.assertEqual(keys[-1], "summary")
        for k in ("top-people", "top-groups", "when", "streak", "voice-media", "speed", "starters", "languages", "archetype"):
            self.assertIn(k, keys)
        html = "".join(h for _, h in cards)
        self.assertIn("Climbing Crew", html)
        self.assertNotIn("Buy&amp;Sell", html)
        self.assertEqual(html.count("made with <b>Edge</b>"), len(cards))
        self.assertNotIn("—", html)

    def test_cli_end_to_end(self):
        out = Path(self.tmp.name) / "out"
        rc = wrapped.main(["--personal", str(self.db), "--since", "2026-01-01", "--owner", "Sam", "--share-safe",
                           "--no-png", "--json", "--out", str(out)])
        self.assertEqual(rc, 0)
        page = visible((out / "wrapped.html").read_text())
        self.assertNotIn("Carla", page)
        self.assertNotIn("http://", page.replace("https://getedge.cc", ""))
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), self.digest)


    def test_cli_defaults_to_this_year(self):
        out = Path(self.tmp.name) / "out-default"
        self.assertEqual(wrapped.main(["--personal", str(self.db), "--no-png", "--json", "--out", str(out)]), 0)
        import json
        self.assertEqual(json.loads((out / "stats.json").read_text())["first"], "2026-01-01")
        out2 = Path(self.tmp.name) / "out-all"
        self.assertEqual(wrapped.main(["--personal", str(self.db), "--all-time", "--no-png", "--json", "--out", str(out2)]), 0)
        self.assertEqual(json.loads((out2 / "stats.json").read_text())["first"], "2025-09-01")


    def test_mac_source_finds_desktop_db(self):
        import os
        import shutil
        from unittest import mock
        from personal import MAC_DB_RELATIVE
        home = Path(self.tmp.name) / "home"
        (home / MAC_DB_RELATIVE).parent.mkdir(parents=True)
        shutil.copy(self.db, home / MAC_DB_RELATIVE)
        with mock.patch.dict(os.environ, {"HOME": str(home)}):
            self.assertEqual(wrapped.main(["--personal", "mac", "--no-png", "--out", str(home / "out")]), 0)
            self.assertTrue((home / "out" / "wrapped.html").exists())
        with mock.patch.dict(os.environ, {"HOME": str(Path(self.tmp.name) / "empty")}):
            self.assertEqual(wrapped.main(["--personal", "mac", "--no-png", "--out", str(home / "out2")]), 2)


    def test_share_cards_write_only_pngs(self):
        from unittest import mock
        out = Path(self.tmp.name) / "share-cards"

        def fake_render(docs, dst):
            for name, doc in docs:
                self.assertNotIn("Carla", visible(doc))
                (dst / name).write_bytes(b"png")
            return "fake"
        with mock.patch.object(wrapped, "render_pngs", fake_render):
            self.assertEqual(wrapped.main(["--personal", str(self.db), "--share-cards", "--out", str(out)]), 0)
        files = sorted(p.name for p in out.iterdir())
        self.assertTrue(files and all(f.endswith(".png") for f in files), files)

    def test_themes(self):
        import render
        try:
            render.set_theme("edge")
            self.assertIn("#154cff", render.CARD_CSS)
            render.set_theme("green")
            self.assertIn("#315f43", render.CARD_CSS)
            self.assertNotIn("#25d366", render.CARD_CSS.lower())  # never WhatsApp's own brand green as a theme
        finally:
            render.set_theme("green")


class WordFilterTests(unittest.TestCase):
    def test_share_safe_words_drop_proper_nouns(self):
        from collections import Counter
        from stats import case_update, proper_nouns, share_safe_words
        mid, cap = Counter(), Counter()
        for t in ["we land in Lisbon tomorrow", "see you in Lisbon soon", "the climbing gym was great",
                  "more climbing please", "mail me at sam@example.com today"]:
            case_update(t, mid, cap)
        proper = proper_nouns(mid, cap)
        self.assertIn("lisbon", proper)
        self.assertNotIn("climbing", proper)
        self.assertNotIn("example", mid)  # emails are stripped before counting
        self.assertEqual(share_safe_words([("lisbon", 9), ("climbing", 5)], proper), [("climbing", 5)])


class ExportFolderTests(unittest.TestCase):
    def test_folder_of_exports_finds_me(self):
        me, other = "Sam Reed", "Ana Lima"
        with tempfile.TemporaryDirectory() as d:
            lines_a, lines_b = [], []
            t = datetime(2026, 1, 5, 9, 0)
            for i in range(120):
                lines_a.append(f"{t:%d/%m/%Y}, {t:%H:%M} - {me if i % 2 else other}: {LINES['en'][i % 3]}")
                lines_b.append(f"{t:%d/%m/%Y}, {t:%H:%M} - {[me, 'Yan Ito', 'Zed Quinn'][i % 3]}: {LINES['de'][i % 3]}")
                t += timedelta(hours=7)
            Path(d, "WhatsApp Chat with Ana Lima.txt").write_text("\n".join(lines_a), encoding="utf-8")
            Path(d, "Trip.txt").write_text("\n".join(lines_b), encoding="utf-8")
            recs, info = load_exports(d)
            self.assertEqual(info["me"], me)
            self.assertEqual(localize(recs), {})  # exports stay in their own local time
            s = compute_personal(recs, name_tokens=info["name_tokens"])
            self.assertEqual((s["people_chats"], s["group_chats"]), (1, 1))
            self.assertEqual(s["sent"], 60 + 40)
            self.assertEqual(s["top_people"][0]["name"], other)

    def test_needs_me_when_ambiguous(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.txt").write_text("01/02/2026, 10:00 - Ana: hi\n01/02/2026, 10:01 - Ben: hey", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_exports(d)


class ShareSafeChatTests(unittest.TestCase):
    def test_single_chat_share_safe(self):
        with tempfile.TemporaryDirectory() as d:
            make_synthetic.main(d)
            f = sorted(Path(d).iterdir())[0]
            s = compute(parse_file(f))
            real = [p["name"] for p in s["people"]]
            safe = share_safe_chat(s)
            html = visible("".join(h for _, h in build_cards(safe)))
            for n in real:
                self.assertNotIn(n, html)
            self.assertIn("Person #1 · ", html)
            self.assertEqual(s["people"][0]["name"], real[0])  # the original stats are not changed

    def test_unsaved_numbers_never_printed(self):
        from render_personal import namer
        s = {"top_people": [{"name": "+1 415 555 0100"}], "new_top": [], "fastest_to_me": [], "i_reply_fastest": [],
             "i_start_top": [], "top_groups": []}
        for safe in (False, True):
            person, _ = namer(s, safe)
            self.assertNotIn("415", person("+1 415 555 0100"))

    def test_initials(self):
        self.assertEqual(initials("Ana Maria Lima"), "A.L.")
        self.assertEqual(initials("Bo"), "B.")
        self.assertEqual(initials("🍊 Orange Cam"), "O.C.")


if __name__ == "__main__":
    unittest.main()
