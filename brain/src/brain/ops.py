"""Running the Brain for real testers (roadmap Stage 1, steps 5 and 6): a request log with no personal data, error
alerts to a person, and rate limits.

- **The request log:** one line per request: the method, the route's pattern (`/v1/me/plans/{plan_id}`, never the
  address as typed), the status and the time taken. No network address, token, query, body or user id. uvicorn's
  own access log stays off (render.yaml: `--no-access-log`).
- **Error alerts:** an unexpected error is logged with its traceback (Render's logs, which only Abram can open) and
  posted to `BRAIN_OPS_WEBHOOK_URL`, or else to the safety alert webhook marked "not a safety alert". The post names
  the route and the kind of error only, never anything from the request. At most one post per route and kind of
  error an hour, and 20 a day, so a broken deploy can't bury a safety alert.
- **Rate limits:** counted in memory only, by a salted hash of the install token or, before a phone has one, of its
  network address. Nothing is stored or logged, and a restart forgets them all. The limits are GUESSES, set well
  above what one person tapping through the app does (the busiest screen sends about 5 requests), and are checked
  against the request log during the friends' round. Overall caps, which no one can get round by faking an address,
  sit behind the per-phone ones: new installs (here) and provider searches (`trips.py`).
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import sys
import threading
import time
import urllib.request
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

log = logging.getLogger("brain.requests")
errors = logging.getLogger("brain.errors")

ALERTS_PER_HOUR_EACH = 1
ALERTS_PER_DAY = 20

# (requests, seconds) per phone, by kind of request. GUESSES (see above).
LIMITS: dict[str, tuple[int, int]] = {
    "install": (10, 3600),       # new installs from one network address
    "plan": (30, 600),           # plans, swaps, the Test B pair: each runs the planner (~1 s of CPU)
    "trip": (10, 600),           # a trip's days: the planner once per day (~6 s for a long trip)
    "any": (180, 60),            # everything else from a phone with a token
    "public": (60, 60),          # pages without a token (share links, the privacy notice)
}
INSTALLS_ALL: tuple[int, int] = (300, 3600)   # new installs from everyone together

PLAN_ROUTES = {("POST", "/v1/me/plans"), ("POST", "/v1/me/testb/pair"),
               ("POST", "/v1/admin/users/{user_id}/plans")}
TRIP_ROUTES = {("POST", "/v1/me/trips/days")}
EXEMPT = {"/v1/health", "/healthz"}

LONDON = ZoneInfo("Europe/London")


def configure_logging() -> None:
    """The Brain's own log lines (brain.*) on standard output, which Render keeps. Once per process."""
    root = logging.getLogger("brain")
    if root.handlers:
        return
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root.addHandler(h)
    root.setLevel(logging.INFO)
    root.propagate = False


@dataclass
class Limiter:
    """Sliding windows in memory. Keys are hashed with a salt made at start, so not even memory holds an address."""
    clock: Callable[[], float] = time.monotonic
    _salt: bytes = field(default_factory=lambda: secrets.token_bytes(16))
    _hits: dict[str, deque] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def key(self, *parts: str) -> str:
        return hashlib.sha256(self._salt + "|".join(parts).encode()).hexdigest()[:24]

    def hit(self, key: str, limit: int, window_s: int) -> int | None:
        """Count one request; None if allowed, else the seconds until the oldest counted request leaves the window."""
        now = self.clock()
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= window_s:
                q.popleft()
            if len(q) >= limit:
                return max(1, int(window_s - (now - q[0])) + 1)
            q.append(now)
            if len(self._hits) > 50_000:   # forget idle phones so memory stays small
                for k in [k for k, v in self._hits.items() if not v or now - v[-1] > 3600]:
                    del self._hits[k]
            return None


class Alerts:
    """Error posts to a person, rate-limited, with nothing from the request in them."""

    def __init__(self, webhook_url: str | None, clock: Callable[[], float] = time.time,
                 post: Callable[[str, dict], None] | None = None):
        self.webhook_url = webhook_url
        self.clock = clock
        self.post = post or _post_json
        self._last: dict[str, float] = {}
        self._day: deque = deque()
        self._lock = threading.Lock()
        self.sent: list[str] = []

    def error(self, method: str, route: str, kind: str) -> bool:
        if not self.webhook_url:
            return False
        now = self.clock()
        with self._lock:
            k = f"{method} {route} {kind}"
            if now - self._last.get(k, -1e18) < 3600 / ALERTS_PER_HOUR_EACH:
                return False
            while self._day and now - self._day[0] >= 86400:
                self._day.popleft()
            if len(self._day) >= ALERTS_PER_DAY:
                return False
            self._last[k] = now
            self._day.append(now)
        at = datetime.fromtimestamp(now, LONDON).strftime("%d %b %H:%M")
        text = (f"ODYS Brain error (not a safety alert): {method} {route} failed with {kind} at {at} London time. "
                f"The traceback is in Render's logs. At most one message an hour for this error.")
        try:
            self.post(self.webhook_url, {"text": text})
        except Exception:  # noqa: BLE001 - an alert that can't be sent is logged; it never fails a request
            errors.warning("the error alert couldn't be posted")
            return False
        self.sent.append(text)
        return True


def _post_json(url: str, body: dict) -> None:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        if not 200 <= resp.status < 300:
            raise OSError(f"webhook answered {resp.status}")


def _address(request: Request) -> str:
    """The phone's network address, for counting only. Render puts the client first in X-Forwarded-For; a client can
    fake that header, which is why the overall caps exist."""
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() or (request.client.host if request.client else "?")


def _route(request: Request) -> str:
    r = request.scope.get("route")
    return getattr(r, "path", None) or "(no route)"


def _match(app: FastAPI, request: Request) -> str:
    """The route's pattern before the request runs (the router sets it only once it has run)."""
    from starlette.routing import Match
    for r in app.router.routes:
        m, _ = r.matches(request.scope)
        if m == Match.FULL:
            return getattr(r, "path", "(no route)")
    return "(no route)"


def _kind(method: str, route: str, request: Request) -> tuple[str, tuple[str, ...]]:
    if method == "POST" and route == "/v1/installs":
        return "install", ("ip", _address(request))
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not token:
        return "public", ("ip", _address(request))
    who = ("tok", token)
    if (method, route) in PLAN_ROUTES:
        return "plan", who
    if (method, route) in TRIP_ROUTES:
        return "trip", who
    return "any", who


def too_many(retry_after: int) -> JSONResponse:
    return JSONResponse({"detail": "That's a lot in a short time. Please wait a minute, then try again."},
                        status_code=429, headers={"Retry-After": str(retry_after)})


def install(app: FastAPI) -> None:
    """The request log, the rate limits and the error alerts, as one middleware around every request. The limiter
    and the alerts are `app.state.limiter` and `app.state.alerts`."""

    @app.middleware("http")
    async def ops(request: Request, call_next):
        limiter, alerts = app.state.limiter, app.state.alerts
        t0 = time.perf_counter()
        method, path = request.method, request.url.path
        route = _match(app, request)
        if path not in EXEMPT and method != "OPTIONS":
            kind, who = _kind(method, route, request)
            wait = limiter.hit(limiter.key(kind, *who), *LIMITS[kind])
            if wait is None and kind == "install":
                wait = limiter.hit("installs-all", *INSTALLS_ALL)
            if wait is not None:
                log.info("%s %s 429 (%s limit)", method, route, kind)
                return too_many(wait)
        try:
            response = await call_next(request)
        except Exception as e:  # noqa: BLE001 - logged and alerted, then a plain 500 the apps can word
            errors.exception("%s %s failed", method, route)
            alerts.error(method, route, type(e).__name__)
            response = JSONResponse({"detail": "Something went wrong on our side. Please try again in a minute."},
                                    status_code=500)
        ms = (time.perf_counter() - t0) * 1000
        log.info("%s %s %d %.0fms", method, _route(request) if route == "(no route)" else route,
                 response.status_code, ms)
        return response
