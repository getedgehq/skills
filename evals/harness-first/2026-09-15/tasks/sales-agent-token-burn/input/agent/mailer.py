"""Outbound mail via the company relay. Sends from the assigned rep's mailbox."""
import os
import smtplib
import uuid
from email.message import EmailMessage

RELAY = os.environ.get("BK_SMTP_RELAY", "relay.brightkiln.example")
FROM_DEFAULT = "sales@brightkiln.example"


def send(to, subject, body, sender=FROM_DEFAULT):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg["Message-ID"] = f"<{uuid.uuid4()}@brightkiln.example>"
    msg.set_content(body)
    with smtplib.SMTP(RELAY, 587, timeout=15) as s:
        s.starttls()
        s.login(os.environ.get("BK_SMTP_USER", ""), os.environ.get("BK_SMTP_PASS", ""))
        s.send_message(msg)
    return msg["Message-ID"]
