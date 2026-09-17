"""Outbound mail via the company relay. Sends from the assigned rep's mailbox."""
import os
import smtplib
import uuid
from email.message import EmailMessage
import logging

RELAY = os.environ.get("BK_SMTP_RELAY", "relay.brightkiln.example")
FROM_DEFAULT = "sales@brightkiln.example"
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

logger = logging.getLogger(__name__)


def send(to, subject, body, sender=FROM_DEFAULT):
    """Send an email. In dry-run mode (DRY_RUN=1), logs instead of sending."""
    msg_id = f"<{uuid.uuid4()}@brightkiln.example>"
    
    if DRY_RUN:
        log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "emails_dryrun.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"{msg_id} [DRY RUN] To: {to}, Subject: {subject}, Body: {body[:100]}...\n")
        logger.info(f"DRY RUN: would send email {msg_id} to {to}")
        return msg_id
    
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg["Message-ID"] = msg_id
    msg.set_content(body)
    with smtplib.SMTP(RELAY, 587, timeout=15) as s:
        s.starttls()
        s.login(os.environ.get("BK_SMTP_USER", ""), os.environ.get("BK_SMTP_PASS", ""))
        s.send_message(msg)
    return msg_id
