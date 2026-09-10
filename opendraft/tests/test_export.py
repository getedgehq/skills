"""Export metadata: the exported paper has to carry its own title.

`pandoc -s` with no title metadata falls back to the source filename, so every
paper this bundle exported to HTML arrived titled "final" in the browser tab,
in the bookmark, and in every link preview that reads that element. Nothing
caught it: the file existed, the exit code was 0, and nobody reads a `<title>`
during a run. An end-to-end run found it by opening the output.

These tests exercise the extraction directly rather than through pandoc, so
they run on a machine that has no pandoc installed.
"""
import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


def _load(name, filename):
    script = Path(__file__).parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXPORT = _load("opendraft_export", "export.py")


class DocumentTitleTests(unittest.TestCase):
    def _write(self, text):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "final.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_the_first_level_one_heading_is_the_title(self):
        path = self._write(
            "# Grounded but Unproven: A Narrative Review\n"
            "\n"
            "# Introduction\n"
            "\n"
            "Every section heading in this pipeline is also level one, so the\n"
            "first one has to win.\n")
        self.assertEqual(EXPORT._document_title(path),
                         "Grounded but Unproven: A Narrative Review")

    def test_a_comment_inside_a_code_fence_is_not_the_title(self):
        path = self._write(
            "```bash\n"
            "# python3 scripts/export.py final.md --format html\n"
            "```\n"
            "\n"
            "# The Real Title\n")
        self.assertEqual(EXPORT._document_title(path), "The Real Title")

    def test_a_document_with_no_level_one_heading_has_no_title(self):
        path = self._write("## Introduction\n\nText.\n")
        self.assertIsNone(EXPORT._document_title(path))

    def test_an_empty_heading_is_not_a_title(self):
        path = self._write("# \n\nText.\n")
        self.assertIsNone(EXPORT._document_title(path))

    def test_the_title_reaches_pandoc_as_metadata(self):
        path = self._write("# A Real Title\n")
        self.assertEqual(EXPORT._title_metadata(path),
                         ["--metadata", "title=A Real Title"])

    def test_no_metadata_flag_is_passed_when_there_is_no_title(self):
        path = self._write("Text with no heading at all.\n")
        self.assertEqual(EXPORT._title_metadata(path), [])

    def test_a_missing_file_yields_no_title_rather_than_an_error(self):
        self.assertIsNone(EXPORT._document_title(Path("/nonexistent/final.md")))


class HtmlCommandTests(unittest.TestCase):
    """The title has to reach pandoc, not merely be extractable.

    Testing `_title_metadata` alone would pass whether or not anything called
    it, which is the shape of guard that lets a fix be reverted silently. These
    capture the command the exporter actually builds.
    """

    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.src = Path(tmp.name) / "final.md"
        self.src.write_text("# A Real Title\n\nBody text.\n", encoding="utf-8")
        self.out = Path(tmp.name) / "final.html"
        self.seen = []
        original = EXPORT._run
        self.addCleanup(lambda: setattr(EXPORT, "_run", original))
        EXPORT._run = self._capture

    def _capture(self, cmd, **kwargs):
        self.seen.append(cmd)
        return 0, "", ""

    def test_export_html_passes_the_title_to_pandoc(self):
        EXPORT.export_html(self.src, self.out, {"pandoc": True})
        cmd = self.seen[0]
        self.assertIn("--metadata", cmd)
        self.assertIn("title=A Real Title", cmd)

    def test_the_citeproc_html_path_passes_the_title_too(self):
        # The bibliography/CSL branch builds its own command and was the easier
        # of the two to leave behind.
        EXPORT._export_with_extra_args(
            self.src, self.out, "html", {"pandoc": True, "pdf_engine": None},
            ["--citeproc"])
        cmd = self.seen[0]
        self.assertIn("--metadata", cmd)
        self.assertIn("title=A Real Title", cmd)

    def test_a_titleless_document_adds_no_metadata_flag(self):
        self.src.write_text("Body text with no heading.\n", encoding="utf-8")
        EXPORT.export_html(self.src, self.out, {"pandoc": True})
        self.assertNotIn("--metadata", self.seen[0])


if __name__ == "__main__":
    unittest.main()
