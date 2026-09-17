"""Turn the data files into the status page html."""
import html
import os

TEMPLATES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

STATUS_LABELS = {
    "operational": "Operational",
    "degraded": "Degraded",
    "outage": "Outage",
}

IMPACT_LABELS = {
    "maintenance": "Maintenance",
    "degraded": "Degraded",
    "outage": "Outage",
}


def esc(value):
    return html.escape(str(value), quote=True)


def banner(services):
    if services and all(s.get("status") == "operational" for s in services):
        return '<div class="banner ok">All systems operational</div>'
    return ""


def uptime_label(key, uptime):
    value = (uptime or {}).get(key)
    if value is None:
        return ""
    return "%.2f%%" % float(value)


def service_rows(services, uptime):
    out = []
    for s in services:
        label = uptime_label(s.get("key"), uptime)
        right = esc(STATUS_LABELS.get(s["status"], s["status"]))
        if label:
            right = '<span class="uptime">%s</span> %s' % (esc(label), right)
        out.append(
            '<div class="service"><span>%s</span><span>%s</span></div>'
            % (esc(s["name"]), right))
    return "\n    ".join(out)


def incident_items(incidents):
    ordered = sorted(incidents, key=lambda i: i.get("started", ""), reverse=True)
    out = []
    for i in ordered:
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
