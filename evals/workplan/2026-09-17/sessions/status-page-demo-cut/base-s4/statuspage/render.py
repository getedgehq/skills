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
    """Show green banner if all services are operational."""
    all_ok = all(s.get("status") == "operational" for s in services)
    if all_ok:
        return '<div class="banner ok">All systems operational</div>'
    return ""


def service_rows(services, uptime):
    """Render service rows with uptime percentages."""
    out = []
    for s in services:
        key = s.get("key", "")
        uptime_pct = uptime.get(key, None)
        status_text = STATUS_LABELS.get(s["status"], s["status"])
        
        if uptime_pct is not None:
            # Format to exactly 2 decimal places
            uptime_str = f"{uptime_pct:.2f}%"
            out.append(
                '<div class="service"><span>%s</span><span class="uptime">%s</span><span>%s</span></div>'
                % (esc(s["name"]), uptime_str, esc(status_text)))
        else:
            out.append(
                '<div class="service"><span>%s</span><span>%s</span></div>'
                % (esc(s["name"]), esc(status_text)))
    return "\n    ".join(out)


def incident_items(incidents):
    """Render incidents in reverse order (newest first)."""
    out = []
    # Reverse the list to show newest first
    for i in reversed(incidents):
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
