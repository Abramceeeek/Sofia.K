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
USER_MESSAGE = ("If you or someone else is in danger or hurt, call 999 now. "
                "We've told a person on our team, and they will reply within a few hours.")


def send_alert(webhook_url: str | None, alert_id: int, user_id: str, message: str) -> bool:
    log.warning("SAFETY ALERT %s from user %s: %s", alert_id, user_id, message)
    if not webhook_url:
        return False
    body = json.dumps({"text": f"Safety alert #{alert_id} (user {user_id[:8]}): {message}"}).encode()
    req = urllib.request.Request(webhook_url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception:  # noqa: BLE001 - the alert is already saved; never fail the user's request
        log.exception("safety alert %s: webhook post failed", alert_id)
        return False
