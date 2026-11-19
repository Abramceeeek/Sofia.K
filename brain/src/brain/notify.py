"""Safety alerts to a person (CLAUDE.md, D46): Abram, and the named backup helper in his work hours.

The alert is saved first, then posted to a webhook if one is configured (for example a private
channel both of them watch). A failed post is logged and the alert stays in the database, so
`GET /v1/admin/safety` still shows it.

SEC-09 (Abram, 12 Nov 2026): the post and the log say only that a message is waiting, its number and when. Never the
message, never a phone number or email left with it, never the person's id: those stay in the database, read with
`GET /v1/admin/safety`, and go when the person deletes their data. A chat service would keep its own copy for as long
as it keeps messages, out of reach of "Delete my data".
"""

from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

log = logging.getLogger("brain.safety")

# What the user sees straight away. It never promises a faster reply than "a few hours".
# D118: says who replies and where the reply arrives (before, nothing carried a reply back).
# D127 (screen reviews): it says plainly that nobody watches overnight, and names no one who hasn't signed Part A.
USER_MESSAGE = ("If you or someone else is in danger or hurt, call 999 now. A person reads every message and will reply "
                "here in Help & safety, and by phone or email if you left one, usually within a few hours. It isn't "
                "watched through the night: a message sent late is answered the next morning.")


def alert_text(alert_id: int, at: datetime | None = None) -> str:
    """The whole alert: that a message is waiting, its number and when (London time). Nothing the person wrote."""
    when = (at or datetime.now(timezone.utc)).astimezone(ZoneInfo("Europe/London")).strftime("%d %b %H:%M")
    return (f"ODYS Help & safety: message #{alert_id} is waiting (received {when}, London time). Read it and reply "
            f"with GET /v1/admin/safety; it isn't copied here.")


def send_alert(webhook_url: str | None, alert_id: int, at: datetime | None = None) -> bool:
    log.warning("SAFETY ALERT %s waiting (read it with GET /v1/admin/safety; never written here)", alert_id)
    if not webhook_url:
        return False
    body = json.dumps({"text": alert_text(alert_id, at)}).encode()
    req = urllib.request.Request(webhook_url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception:  # noqa: BLE001 - the alert is already saved; never fail the user's request
        log.exception("safety alert %s: webhook post failed", alert_id)
        return False
