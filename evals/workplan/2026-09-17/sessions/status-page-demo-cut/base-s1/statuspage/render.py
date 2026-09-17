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
    """Generate the status banner. Shows green 'All systems operational' when everything is up."""
    all_operational = all(s.get("status") == "operational" for s in services)
    if all_operational:
        return '<div class="banner ok">All systems operational</div>'
    return ""


def service_rows(services, uptime):
    """Render service rows with uptime percentages."""
    out = []
    for s in services:
        key = s.get("key", "")
        uptime_pct = uptime.get(key)
        uptime_display = ""
        if uptime_pct is not None:
            # Format to exactly 2 decimal places as Tomas specified
            uptime_display = '<span class="uptime">%.2f%%</span>' % uptime_pct
        
        out.append(
            '<div class="service"><span>%s</span><span class="status-info">%s%s</span></div>'
            % (esc(s["name"]), uptime_display, esc(STATUS_LABELS.get(s["status"], s["status"]))))
    return "\n    ".join(out)


def incident_items(incidents):
    """Render incidents in reverse chronological order (newest first)."""
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
