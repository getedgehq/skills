import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "render_card.py"
SPEC = importlib.util.spec_from_file_location("render_card", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RenderCardTests(unittest.TestCase):
    def test_html_is_escaped_and_metrics_are_bounded(self):
        svg = MODULE.render_svg(
            {
                "title": "A < B",
                "metrics": [{"label": str(index), "value": index} for index in range(7)],
                "findings": ["one", "two", "three", "ignored"],
            }
        )
        self.assertIn("A &lt; B", svg)
        self.assertNotIn("A < B", svg)
        self.assertEqual(svg.count("<g transform=\"translate("), 4)
        self.assertNotIn("ignored", svg)


if __name__ == "__main__":
    unittest.main()
