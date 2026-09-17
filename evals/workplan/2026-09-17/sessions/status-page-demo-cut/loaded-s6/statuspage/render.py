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
    """Generate the status banner. Green if all operational, empty otherwise."""
    all_ok = all(s["status"] == "operational" for s in services)
    if all_ok:
        return '<div class="banner ok">All systems operational</div>'
    return ""


def service_rows(services, uptime):
    """Generate service rows with uptime percentages."""
    out = []
    for s in services:
        service_key = s["key"]
        uptime_pct = uptime.get(service_key, 0.0)
        # Format with exactly 2 decimal places
        uptime_str = "{:.2f}%".format(uptime_pct)
        out.append(
            '<div class="service"><span>%s</span><span>%s · %s uptime</span></div>'
            % (esc(s["name"]), esc(STATUS_LABELS.get(s["status"], s["status"])), uptime_str))
    return "\n    ".join(out)


def incident_items(incidents):
    """Generate incident history items, newest first."""
    # Reverse the incidents list so newest appears first
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
