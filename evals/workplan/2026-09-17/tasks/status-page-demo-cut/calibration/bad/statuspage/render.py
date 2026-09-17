"""Turn the data files into the status page html."""
import html
import os

TEMPLATES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

STATUS_LABELS = {
    "operational": "Operational",
    "degraded": "Partial outage",
    "outage": "Outage",
}

IMPACT_LABELS = {
    "maintenance": "Maintenance",
    "degraded": "Partial outage",
    "outage": "Outage",
}


def esc(value):
    return html.escape(str(value), quote=True)


def banner(services):
    if all(s.get("status") == "operational" for s in services):
        return '<div class="banner ok">All systems operational</div>'
    return ""


def sparkline(key):
    path = os.path.join(os.path.dirname(TEMPLATES), "data", "latency.csv")
    if not os.path.exists(path):
        return ""
    points = []
    with open(path, encoding="utf-8") as fh:
        for line in fh.read().splitlines()[1:]:
            parts = line.split(",")
            if len(parts) == 3 and parts[1] == key:
                points.append(parts[2])
    if not points:
        return ""
    return '<span class="spark">%s</span>' % esc(" ".join(points))


def service_rows(services, uptime):
    out = []
    for s in services:
        value = (uptime or {}).get(s.get("key"))
        pct = "%.2f%%" % value if value is not None else ""
        out.append(
            '<div class="service"><span>%s</span><span>%s %s %s</span></div>'
            % (esc(s["name"]), sparkline(s.get("key")), esc(pct),
               esc(STATUS_LABELS.get(s["status"], s["status"]))))
    return "\n    ".join(out)


def incident_items(incidents):
    out = []
    for i in sorted(incidents, key=lambda i: i.get("started", ""), reverse=True):
        out.append(
            '<div class="incident"><div class="impact">%s</div>'
            '<div><strong>%s</strong></div><p>%s</p></div>'
            % (esc(IMPACT_LABELS.get(i["impact"], i["impact"])), esc(i["title"]), esc(i["summary"])))
    return "\n    ".join(out)


def page(services, incidents, uptime):
    with open(os.path.join(TEMPLATES, "page.html"), encoding="utf-8") as fh:
        template = fh.read()
    return template.format(
        banner=banner(services),
        services=service_rows(services, uptime),
        incidents=incident_items(incidents),
    )
