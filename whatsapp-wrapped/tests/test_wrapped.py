"""Tests on SYNTHETIC data only. Run: python3 -m unittest discover -s tests -v (from the skill folder)."""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import make_synthetic  # noqa: E402
from parse import parse_file, parse_text  # noqa: E402
from render import build_cards, build_page  # noqa: E402
from stats import compute  # noqa: E402

LRM, NNBSP = "\u200e", "\u202f"


class FormatTests(unittest.TestCase):
    def one(self, text, **kw):
        c = parse_text(text, **kw)
        self.assertTrue(c.messages, text)
        return c

    def test_ios_us_12h(self):
        c = self.one(f"[1/2/24, 9:05:01{NNBSP}PM] Ana: hi\n[1/13/24, 12:10:00{NNBSP}AM] Ben: yo")
        self.assertEqual(c.date_order, "mdy")
        self.assertEqual((c.messages[0].ts.month, c.messages[0].ts.day, c.messages[0].ts.hour), (1, 2, 21))
        self.assertEqual(c.messages[1].ts.hour, 0)

    def test_ios_de(self):
        c = self.one("[31.12.23, 21:41:05] Ana: hallo\n[01.01.24, 00:01:00] Ben: frohes neues")
        self.assertEqual((c.messages[0].ts.day, c.messages[0].ts.month, c.messages[0].ts.year), (31, 12, 2023))

    def test_android_gb(self):
        c = self.one("31/12/2023, 21:41 - Ana: hi\n01/01/2024, 00:01 - Ben: happy new year")
        self.assertEqual(c.messages[0].ts.day, 31)
        self.assertEqual(c.platform, "android")

    def test_android_us_12h(self):
        c = self.one(f"12/31/23, 9:41{NNBSP}PM - Ana: hi\n1/1/24, 12:01{NNBSP}AM - Ben: hny")
        self.assertEqual((c.messages[0].ts.month, c.messages[0].ts.hour), (12, 21))

    def test_android_de_dots(self):
        c = self.one("31.12.23, 21:41 - Ana: hallo\n01.01.24, 00:01 - Ben: <Medien ausgeschlossen>")
        self.assertEqual(c.messages[1].kind, "media")

    def test_spanish_pm(self):
        c = self.one("31/12/23, 9:41 p. m. - Ana: hola\n1/1/24, 10:00 a. m. - Ben: feliz")
        self.assertEqual(c.messages[0].ts.hour, 21)
        self.assertEqual(c.messages[1].ts.hour, 10)

    def test_iso(self):
        c = self.one("2023-12-31, 21:41 - Ana: hi\n2024-01-01, 08:00 - Ben: hey")
        self.assertEqual(c.date_order, "ymd")

    def test_ambiguous_order_uses_chronology(self):
        # All values <= 12. As d/m: Jan 12, Feb 3, Feb 10 (in order). As m/d: Dec 1, Mar 2, Oct 2 (goes backwards).
        lines = "12/01/2024, 10:00 - Ana: a\n03/02/2024, 10:00 - Ben: b\n10/02/2024, 10:00 - Ana: c"
        self.assertEqual(parse_text(lines).date_order, "dmy")

    def test_multiline_and_system_and_media(self):
        text = (
            f"[1/2/24, 9:05:01{NNBSP}PM] Group: {LRM}Messages and calls are end-to-end encrypted.\n"
            f"[1/2/24, 9:06:01{NNBSP}PM] Ana: line one\nline two\n"
            f"{LRM}[1/2/24, 9:07:01{NNBSP}PM] Ben: {LRM}<attached: 00000003-AUDIO-2024-01-02-21-07-01.opus>\n"
            f"{LRM}[1/2/24, 9:08:01{NNBSP}PM] Ben: {LRM}image omitted\n"
            f"[1/2/24, 9:09:01{NNBSP}PM] Ana: edited text {LRM}<This message was edited>\n"
        )
        c = self.one(text)
        self.assertEqual(len(c.messages), 4)
        self.assertEqual(c.messages[0].text, "line one\nline two")
        self.assertEqual([m.kind for m in c.messages], ["text", "voice", "photo", "text"])
        self.assertTrue(c.messages[3].edited)

    def test_android_system_lines_skipped(self):
        c = self.one("01/01/2024, 10:00 - Messages and calls are end-to-end encrypted.\n"
                     "01/01/2024, 10:00 - Ana created group \"x\"\n01/01/2024, 10:01 - Ana: hi\n"
                     "01/01/2024, 10:02 - Ben: PTT-20240101-WA0001.opus (file attached)")
        self.assertEqual([m.kind for m in c.messages], ["text", "voice"])


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.n = make_synthetic.main(cls.dir)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_formats_same_core_stats(self):
        ref = None
        for f in ("ios_en_us.txt", "android_en_gb.txt", "ios_de.zip", "android_en_us.zip"):
            s = compute(parse_file(self.dir / f))
            core = (s["total_messages"], s["span_days"], s["streak"], s["peak_hour"], s["busiest_day"],
                    s["top_emojis"][:5], [p["name"] for p in s["people"]], s["media"]["voice"])
            self.assertEqual(s["total_messages"], self.n, f)
            ref = ref or core
            self.assertEqual(core, ref, f)

    def test_one_distinct_award_each(self):
        s = compute(parse_file(self.dir / "ios_en_us.txt"))
        names = [a["name"] for a in s["awards"]]
        titles = [a["award"] for a in s["awards"] if a["key"] != "lurker"]
        self.assertEqual(sorted(names), sorted(p["name"] for p in s["people"]))
        self.assertEqual(len(titles), len(set(titles)))

    def test_page_is_offline_and_escaped(self):
        text = "01/01/2024, 10:00 - <script>alert(1)</script>: hi <b>x</b>\n01/01/2024, 10:05 - Ben: hey 😂"
        s = compute(parse_text(text, title="<img src=x onerror=alert(1)>"))
        page = build_page(s, build_cards(s), None)
        self.assertNotIn("<script>alert", page)
        self.assertNotIn("<img src=x", page)
        for bad in ("http://", "https://fonts", "<link", "src=\"http"):
            self.assertNotIn(bad, page.replace("https://getedge.cc", ""))

    def test_top_words_skip_filler(self):
        s = compute(parse_file(self.dir / "ios_en_us.txt"))
        words = [w for w, _ in s["top_words"]]
        self.assertTrue(words)
        for filler in ("day", "last", "number", "week", "time", "people", "thing", "going", "that", "this"):
            self.assertNotIn(filler, words)
        self.assertTrue(all(len(w) >= 4 for w in words), words)

    def test_top_words_prefer_distinctive(self):
        # "today" style filler appears in every conversation; "padel" in a few, in bursts; "gelato" once only.
        lines, day = [], 1
        for conv in range(12):
            body = ["see you soon friend", "lovely weather again"]
            if conv % 4 == 0:
                body += ["padel tonight?", "padel padel", "bring the padel rackets"]
            for k, text in enumerate(body):
                lines.append(f"{day:02d}/03/2024, 1{k}:00 - {'Ana' if k % 2 else 'Ben'}: {text}")
            day += 2
        lines.append("28/03/2024, 10:00 - Ana: gelato gelato gelato")
        s = compute(parse_text("\n".join(lines)))
        words = [w for w, _ in s["top_words"]]
        self.assertEqual(words[0], "padel", words)
        self.assertNotIn("weather", words)   # in every conversation: no signal
        self.assertNotIn("gelato", words)    # one conversation only
        self.assertNotIn("ana", words)       # participant names never count

    def test_repeated_paste_counts_once(self):
        lines = []
        for day in range(1, 25):
            lines.append(f"{day:02d}/05/2024, 09:00 - Bot: Unipile check failed again today, please display the native application type")
            lines.append(f"{day:02d}/05/2024, 12:00 - Ana: tennis later?" if day % 3 == 0 else f"{day:02d}/05/2024, 12:00 - Ana: hello")
            lines.append(f"{day:02d}/05/2024, 12:05 - Ben: tennis tennis" if day % 3 == 0 else f"{day:02d}/05/2024, 12:05 - Ben: hi")
        s = compute(parse_text("\n".join(lines)))
        words = [w for w, _ in s["top_words"]]
        self.assertEqual(words[0], "tennis", words)
        self.assertNotIn("unipile", words)

    def test_no_banned_copy(self):
        s = compute(parse_file(self.dir / "ios_en_us.txt"))
        page = build_page(s, build_cards(s), None)
        self.assertNotIn("—", page)  # em dash
        import re
        visible = re.sub(r"<[^>]+>|base64,[A-Za-z0-9+/=]+", " ", page)
        self.assertIsNone(re.search(r"\bAI\b", visible))


if __name__ == "__main__":
    unittest.main()
