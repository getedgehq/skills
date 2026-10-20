"""Share schema: what may leave the device, and what the browser refuses to render. SYNTHETIC data only.

Every rejection case runs through the Python validator (uploader and server) AND the viewer's JavaScript validator
(through node, when node is installed), so the two cannot drift apart.
"""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))

import canary  # noqa: E402
import share  # noqa: E402
from share_schema import SCHEMA, SchemaError, canonical_emoji, describe, validate, validate_teaser  # noqa: E402

VIEWER = HERE.parent / "share" / "static" / "viewer.js"
SCHEMA_FILE = HERE.parent / "share" / "schema-v1.json"


def good() -> dict:
    return {"v": 1, "kind": "group", "from": "2025-04", "to": "2025-10", "cards": [
        {"t": "messages", "n": 5849, "per_day": 29, "active_days": 189, "span_days": 201, "people": 6, "chats": 0},
        {"t": "peak", "hour": 21, "weekday": 6, "hist": [50] * 23 + [100]},
        {"t": "streak", "days": 87, "busiest_month": "2025-06", "busiest_n": 1010},
        {"t": "emojis", "top": [["😂", 176], ["🔥", 120]]},
        {"t": "media", "voice": 323, "photos": 219, "stickers": 115},
        {"t": "archetype", "id": "night_owls"}]}


def mutate(fn):
    p = good()
    fn(p)
    return p


BAD = {
    "extra top-level key (a title)": mutate(lambda p: p.update(title="Sunday League")),
    "missing cards": mutate(lambda p: p.pop("cards")),
    "wrong version": mutate(lambda p: p.update(v=2)),
    "version as string": mutate(lambda p: p.update(v="1")),
    "unknown kind": mutate(lambda p: p.update(kind="public")),
    "day-precise date": mutate(lambda p: p.update({"from": "2025-04-12"})),
    "month 13": mutate(lambda p: p.update(to="2025-13")),
    "from after to": mutate(lambda p: p.update({"from": "2026-01"})),
    "name smuggled as extra card field": mutate(lambda p: p["cards"][0].update(name="Maya Lindqvist")),
    "phone number as a number field string": mutate(lambda p: p["cards"][0].update(n="+4915123456789")),
    "float instead of int": mutate(lambda p: p["cards"][0].update(n=12.5)),
    "bool instead of int": mutate(lambda p: p["cards"][0].update(people=True)),
    "negative count": mutate(lambda p: p["cards"][4].update(voice=-1)),
    "count over cap": mutate(lambda p: p["cards"][0].update(n=10 ** 9)),
    "hour 24": mutate(lambda p: p["cards"][1].update(hour=24)),
    "histogram with 23 bars": mutate(lambda p: p["cards"][1].update(hist=[1] * 23)),
    "histogram value over 100": mutate(lambda p: p["cards"][1].update(hist=[101] + [1] * 23)),
    "free text in emoji slot": mutate(lambda p: p["cards"][3].update(top=[["Maya", 3]])),
    "flag emoji (not allowlisted)": mutate(lambda p: p["cards"][3].update(top=[["🇵🇹", 3]])),
    "emoji with skin tone": mutate(lambda p: p["cards"][3].update(top=[["👍🏽", 3]])),
    "duplicate emoji": mutate(lambda p: p["cards"][3].update(top=[["😂", 3], ["😂", 2]])),
    "six emojis": mutate(lambda p: p["cards"][3].update(top=[[e, 1] for e in SCHEMA["emoji"][:6]])),
    "unknown archetype": mutate(lambda p: p["cards"][5].update(id="Maya's crew")),
    "unknown card type": mutate(lambda p: p["cards"].insert(2, {"t": "names", "list": ["Maya"]})),
    "duplicate card": mutate(lambda p: p["cards"].insert(1, copy.deepcopy(p["cards"][0]))),
    "cards out of order": mutate(lambda p: p["cards"].reverse()),
    "missing required peak card": mutate(lambda p: p["cards"].pop(1)),
    "too few cards": mutate(lambda p: p.update(cards=p["cards"][:3])),
    "html in a month": mutate(lambda p: p["cards"][2].update(busiest_month="<img src=x>")),
    "cards not a list": mutate(lambda p: p.update(cards={"0": p["cards"][0]})),
    "payload is a list": [good()],
}

BAD_TEASERS = [
    {"tpl": "messages", "n": 5849, "title": "Sunday League"},
    {"tpl": "custom", "text": "Maya sent 27%"},
    {"tpl": "messages", "n": "5,849"},
    {"tpl": "generic", "n": 1},
    {"tpl": "streak"},
    "messages",
]


class SchemaRejects(unittest.TestCase):
    def test_good_payload_passes_both_validators(self):
        validate(good())
        if shutil.which("node"):
            self.assertEqual(run_node([good()]), [None])

    def test_python_rejects_every_bad_payload(self):
        for name, p in BAD.items():
            with self.subTest(name):
                with self.assertRaises(SchemaError):
                    validate(p)

    def test_viewer_rejects_every_bad_payload(self):
        if not shutil.which("node"):
            self.skipTest("node not installed")
        results = run_node(list(BAD.values()))
        for (name, _), err in zip(BAD.items(), results):
            with self.subTest(name):
                self.assertIsNotNone(err, f"viewer accepted: {name}")

    def test_bad_teasers(self):
        for t in BAD_TEASERS:
            with self.subTest(t=t):
                with self.assertRaises(SchemaError):
                    validate_teaser(t)
        for t in ({"tpl": "generic"}, {"tpl": "messages", "n": 1}, {"tpl": "streak", "days": 3}):
            validate_teaser(t)

    def test_emoji_canonicalisation(self):
        self.assertEqual(canonical_emoji("👍🏽"), "👍")
        self.assertEqual(canonical_emoji("🤷‍♀️"), "🤷")
        self.assertEqual(canonical_emoji("❤"), "❤️")
        self.assertIsNone(canonical_emoji("🇵🇹"))


class BuiltFromSyntheticChats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.group = canary.write_group(cls.tmp / "group.txt")
        cls.duo = canary.write_duo(cls.tmp / "duo.txt")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def payload(self, *argv):
        return share.build_payload(share.parser().parse_args(list(argv)))

    def test_group_payload_has_no_canaries(self):
        p = self.payload(str(self.group))
        validate(p)
        self.assertEqual(p["kind"], "group")
        blob = json.dumps(p, ensure_ascii=False).encode()
        self.assertEqual(canary.leaks(blob), [])
        self.assertEqual(canary.leaks("\n".join(describe(p)).encode()), [])
        self.assertTrue(4 <= len(p["cards"]) <= 6)

    def test_duo_needs_me_and_shows_only_the_creator(self):
        with self.assertRaises(SystemExit):
            self.payload(str(self.duo))
        with self.assertRaises(SystemExit):
            self.payload(str(self.duo), "--me", "Somebody Else")
        mine = self.payload(str(self.duo), "--me", "Zebulon Quixtarr")
        theirs = self.payload(str(self.duo), "--me", "Ottoline Wexbridge")
        self.assertEqual(mine["kind"], "duo")
        self.assertEqual(mine["cards"][0]["people"], 0)
        from parse import parse_file
        chat = parse_file(str(self.duo))
        own = sum(1 for m in chat.messages if m.sender == "Zebulon Quixtarr" and m.kind != "call")
        self.assertEqual(mine["cards"][0]["n"], own)
        self.assertNotEqual(mine["cards"][0]["n"], theirs["cards"][0]["n"])
        self.assertEqual(canary.leaks(json.dumps(mine, ensure_ascii=False).encode()), [])

    def test_personal_payload_from_a_folder(self):
        folder = self.tmp / "exports"
        folder.mkdir(exist_ok=True)
        canary.write_group(folder / "a.txt")
        canary.write_duo(folder / "b.txt")
        p = self.payload("--personal", str(folder), "--me", "Zebulon Quixtarr", "--all-time")
        validate(p)
        self.assertEqual(p["kind"], "personal")
        self.assertEqual(p["cards"][0]["people"], 0)
        self.assertEqual(p["cards"][0]["chats"], 2)
        self.assertEqual(canary.leaks(json.dumps(p, ensure_ascii=False).encode()), [])

    def test_dry_run_terminal_output_has_no_canaries(self):
        out = self.tmp / "dry"
        r = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "share.py"), str(self.group), "--dry-run",
                            "--out", str(out)], capture_output=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        self.assertIn(b"nothing uploaded", r.stdout)
        self.assertEqual(canary.leaks(r.stdout + r.stderr), [])
        self.assertEqual(canary.leaks((out / "share-payload.json").read_bytes()), [])

    def test_no_terminal_means_no_publish(self):
        r = subprocess.run([sys.executable, str(HERE.parent / "scripts" / "share.py"), str(self.group),
                            "--server", "http://127.0.0.1:9", "--out", str(self.tmp / "nt")],
                           input=b"COVER\nPUBLISH\n", capture_output=True, timeout=120, start_new_session=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b"typed by a person at a terminal", r.stdout + r.stderr)


def run_node(payloads: list) -> list:
    script = ("const v=require(process.argv[1]);const s=require(process.argv[2]);"
              "const ps=JSON.parse(require('fs').readFileSync(0,'utf8'));"
              "process.stdout.write(JSON.stringify(ps.map(p=>v.validate(s,p))));")
    r = subprocess.run(["node", "-e", script, str(VIEWER), str(SCHEMA_FILE)], input=json.dumps(payloads).encode(),
                       capture_output=True, timeout=60)
    if r.returncode:
        raise AssertionError(r.stderr.decode())
    return json.loads(r.stdout)


if __name__ == "__main__":
    unittest.main()
