import unittest

from statuspage import render

SERVICES = [
    {"key": "api", "name": "Public API", "status": "operational"},
    {"key": "webhooks", "name": "Webhook delivery", "status": "degraded"},
]
INCIDENTS = [
    {"id": "INC-01", "title": "Test & escape", "impact": "degraded",
     "started": "2026-01-01T00:00:00Z", "resolved": "2026-01-01T01:00:00Z",
     "summary": "A <b>summary</b>."},
]
UPTIME = {"api": 99.95, "webhooks": 99.8}


class RenderTests(unittest.TestCase):
    def test_every_service_appears(self):
        markup = render.service_rows(SERVICES, UPTIME)
        self.assertIn("Public API", markup)
        self.assertIn("Webhook delivery", markup)

    def test_status_labels(self):
        markup = render.service_rows(SERVICES, UPTIME)
        self.assertIn("Operational", markup)

    def test_incident_markup_is_escaped(self):
        markup = render.incident_items(INCIDENTS)
        self.assertIn("Test &amp; escape", markup)
        self.assertNotIn("<b>summary</b>", markup)

    def test_page_renders_the_template(self):
        markup = render.page(SERVICES, INCIDENTS, UPTIME)
        self.assertIn("<!doctype html>", markup)
        self.assertIn("Northwind Status", markup)


if __name__ == "__main__":
    unittest.main()
