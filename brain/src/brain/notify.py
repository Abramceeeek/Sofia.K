"""Safety alerts to a person (CLAUDE.md, D46): Abram, and the named backup helper in his work hours.

The alert is saved first, then posted to a webhook if one is configured (for example a private
channel both of them watch). A failed post is logged and the alert stays in the database, so
`GET /v1/admin/safety` still shows it.
"""

from __future__ import annotations

import json
import logging
import urllib.request

log = logging.getLogger("brain.safety")

# What the user sees straight away. It never promises a faster reply than "a few hours".
# D118: says who replies and where the reply arrives (before, nothing carried a reply back).
USER_MESSAGE = ("If you or someone else is in danger or hurt, call 999 now. "
                "We've told a person: Abram, or whoever is covering for him. They'll reply within a few hours, "
                "here in Help & safety, and by phone or email if you left one.")


def send_alert(webhook_url: str | None, alert_id: int, user_id: str, message: str, contact: str | None = None) -> bool:
    log.warning("SAFETY ALERT %s from user %s: %s", alert_id, user_id, message)   # the contact is never logged
    if not webhook_url:
        return False
    reach = (f"Reply to: {contact}" if contact
             else f"No contact left: reply in the app (POST /v1/admin/safety/{alert_id}/reply with text)")
    body = json.dumps({"text": f"Safety alert #{alert_id} (user {user_id[:8]}): {message} | {reach}"}).encode()
    req = urllib.request.Request(webhook_url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception:  # noqa: BLE001 - the alert is already saved; never fail the user's request
        log.exception("safety alert %s: webhook post failed", alert_id)
        return False
