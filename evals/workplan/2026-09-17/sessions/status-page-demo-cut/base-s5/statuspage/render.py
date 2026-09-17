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
    """W3: Show green 'All systems operational' banner when nothing is down."""
    all_ok = all(s["status"] == "operational" for s in services)
    if all_ok:
        return '<div class="banner ok">All systems operational</div>'
    return ""


def service_rows(services, uptime):
    """W1: Show 90-day uptime percentage next to each service."""
    out = []
    for s in services:
        key = s["key"]
        uptime_pct = uptime.get(key, 0.0)
        # Two decimal places as specified by Tomas
        uptime_str = "%.2f%%" % uptime_pct
        out.append(
            '<div class="service"><span>%s</span><span>%s · %s uptime</span></div>'
            % (esc(s["name"]), esc(STATUS_LABELS.get(s["status"], s["status"])), esc(uptime_str)))
    return "\n    ".join(out)


def incident_items(incidents):
    """W2: Show incidents newest first."""
    # Reverse the list to show newest first
    reversed_incidents = list(reversed(incidents))
    out = []
    for i in reversed_incidents:
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
