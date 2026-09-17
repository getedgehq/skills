"""Tools exposed to the outreach agent.

CHANGES:
- Only retry transient errors (503, 429, 500, timeouts)
- Don't retry validation errors (400, 404, 422)
- Mark errors as retryable/non-retryable for model
- Reduced retry attempts from 4 to 3
"""
import functools
import os
import time

from agent import mailer

CRM_BASE = os.environ.get("CRM_BASE_URL", "https://crm.brightkiln.example/api/v3")
CRM_TOKEN_ENV = "BK_CRM_TOKEN"

# HTTP status codes that should be retried
RETRYABLE_STATUSES = {500, 502, 503, 504, 429}


class ToolError(Exception):
    def __init__(self, message, status=None, retryable=False):
        super().__init__(message)
        self.status = status
        self.retryable = retryable


def with_retries(fn, attempts=3, backoff=1.5):
    """Retry only transient errors (5xx, 429, timeouts)."""
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        last = None
        for i in range(attempts):
            try:
                return fn(*args, **kwargs)
            except ToolError as e:
                last = e
                # Only retry if error is marked retryable
                if not e.retryable:
                    raise
                if i < attempts - 1:  # Don't sleep after last attempt
                    time.sleep(backoff * (i + 1))
        raise last
    return wrapped


def _http(method, path, **kwargs):
    import requests  # imported lazily so unit tests don't need it

    try:
        r = requests.request(
            method,
            f"{CRM_BASE}{path}",
            headers={"Authorization": f"Bearer {os.environ.get(CRM_TOKEN_ENV, '')}"},
            timeout=20,
            **kwargs,
        )
    except requests.exceptions.Timeout:
        raise ToolError("Request timeout", status=None, retryable=True)
    except requests.exceptions.ConnectionError:
        raise ToolError("Connection failed", status=None, retryable=True)
    
    if r.status_code >= 400:
        retryable = r.status_code in RETRYABLE_STATUSES
        error_msg = f"{r.status_code} {r.reason}: {r.text[:500]}"
        raise ToolError(error_msg, status=r.status_code, retryable=retryable)
    
    return r.json()


class Toolbox:
    def schemas(self):
        return [
            {
                "name": "crm_get_account",
                "description": "Load the full account export (company, all contacts, activity history, past emails, notes).",
                "input_schema": {"type": "object", "properties": {"account_id": {"type": "string"}}, "required": ["account_id"]},
            },
            {
                "name": "crm_update_contact",
                "description": "Update fields on a CRM contact.",
                "input_schema": {
                    "type": "object",
                    "properties": {"contact_id": {"type": "string"}, "fields": {"type": "object"}},
                    "required": ["contact_id", "fields"],
                },
            },
            {
                "name": "send_email",
                "description": "Send an email to a prospect from the assigned rep's mailbox.",
                "input_schema": {
                    "type": "object",
                    "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                    "required": ["to", "subject", "body"],
                },
            },
        ]

    def execute(self, name, arguments):
        fn = getattr(self, name, None)
        if fn is None:
            raise ToolError(f"unknown tool {name}", status=400, retryable=False)
        return fn(**arguments)

    @with_retries
    def crm_get_account(self, account_id):
        # full export: contacts, activities, emails, notes. big accounts are 30-40KB of JSON.
        return _http("GET", f"/accounts/{account_id}/export", params={"include": "contacts,activities,emails,notes"})

    @with_retries
    def crm_update_contact(self, contact_id, fields):
        return _http("PATCH", f"/contacts/{contact_id}", json={"fields": fields})

    def send_email(self, to, subject, body):
        message_id = mailer.send(to=to, subject=subject, body=body)
        return {"sent": True, "message_id": message_id}
