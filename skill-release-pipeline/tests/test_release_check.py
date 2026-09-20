from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_check", HERE / "scripts" / "release_check.py")
release_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(release_check)


class ReleaseCheckTests(unittest.TestCase):
    def test_ignored_cache_does_not_break_refreshed_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            files = {
                "SKILL.md": "---\nname: x\ndescription: y\n---\n",
                "LICENSE": "license",
                "EVALS.md": "not run",
            }
            for name, text in files.items():
                (bundle / name).write_text(text)
            cache = bundle / ".pytest_cache"
            cache.mkdir()
            (cache / "README.md").write_text("cache")
            entries = [
                {"path": name, "sha256": release_check.sha256(bundle / name), "size_bytes": (bundle / name).stat().st_size}
                for name in files
            ]
            material = "".join(
                f'{entry["path"]}:{entry["sha256"]}\n' for entry in sorted(entries, key=lambda row: row["path"])
            )
            rollup = release_check.hashlib.sha256(material.encode()).hexdigest()
            (bundle / "DERIVATION.json").write_text(json.dumps({"copy_files": entries, "copy_files_sha256": rollup}))
            self.assertEqual(release_check.check(bundle), [])

    def test_missing_contract_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            (bundle / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n")
            failures = release_check.check(bundle)
            self.assertIn("missing DERIVATION.json", failures)
            self.assertIn("missing EVALS.md", failures)

    def test_empty_or_unclosed_front_matter_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            files = {
                "SKILL.md": "---\nname:\ndescription:\n",
                "LICENSE": "license",
                "EVALS.md": "not run",
            }
            for name, text in files.items():
                (bundle / name).write_text(text)
            entries = [
                {"path": name, "sha256": release_check.sha256(bundle / name), "size_bytes": (bundle / name).stat().st_size}
                for name in files
            ]
            material = "".join(f'{row["path"]}:{row["sha256"]}\n' for row in sorted(entries, key=lambda row: row["path"]))
            rollup = release_check.hashlib.sha256(material.encode()).hexdigest()
            (bundle / "DERIVATION.json").write_text(json.dumps({"copy_files": entries, "copy_files_sha256": rollup}))
            self.assertIn("invalid SKILL.md front matter", release_check.check(bundle))

    def test_derivation_metadata_is_secret_scanned(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            files = {
                "SKILL.md": "---\nname: x\ndescription: y\n---\n",
                "LICENSE": "license",
                "EVALS.md": "not run",
            }
            for name, text in files.items():
                (bundle / name).write_text(text)
            entries = [
                {"path": name, "sha256": release_check.sha256(bundle / name), "size_bytes": (bundle / name).stat().st_size}
                for name in files
            ]
            material = "".join(f'{row["path"]}:{row["sha256"]}\n' for row in sorted(entries, key=lambda row: row["path"]))
            rollup = release_check.hashlib.sha256(material.encode()).hexdigest()
            token = "gh" + "p_" + "a" * 30
            (bundle / "DERIVATION.json").write_text(json.dumps({"copy_files": entries, "copy_files_sha256": rollup, "token": token}))
            self.assertTrue(any("DERIVATION.json" in failure for failure in release_check.check(bundle)))

    def test_secret_pattern_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            files = {
                "SKILL.md": "---\nname: x\ndescription: y\n---\n",
                "LICENSE": "license",
                "EVALS.md": "not run",
                "token.txt": "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456",
            }
            for name, text in files.items():
                (bundle / name).write_text(text)
            entries = []
            for name in files:
                path = bundle / name
                entries.append({"path": name, "sha256": release_check.sha256(path), "size_bytes": path.stat().st_size})
            rollup_material = "".join(
                f'{entry["path"]}:{entry["sha256"]}\n' for entry in sorted(entries, key=lambda row: row["path"])
            )
            rollup = release_check.hashlib.sha256(rollup_material.encode()).hexdigest()
            (bundle / "DERIVATION.json").write_text(json.dumps({"copy_files": entries, "copy_files_sha256": rollup}))
            self.assertTrue(any("possible secret" in item for item in release_check.check(bundle)))

    def test_wrong_rollup_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary)
            files = {
                "SKILL.md": "---\nname: x\ndescription: y\n---\n",
                "LICENSE": "license",
                "EVALS.md": "not run",
            }
            for name, text in files.items():
                (bundle / name).write_text(text)
            entries = [
                {"path": name, "sha256": release_check.sha256(bundle / name), "size_bytes": (bundle / name).stat().st_size}
                for name in files
            ]
            (bundle / "DERIVATION.json").write_text(
                json.dumps({"copy_files": entries, "copy_files_sha256": "0" * 64})
            )
            self.assertIn("DERIVATION.json rollup mismatch", release_check.check(bundle))


if __name__ == "__main__":
    unittest.main()
