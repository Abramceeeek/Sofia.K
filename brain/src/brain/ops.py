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
- **Hardening (audit, 11 Nov 2026; decisions/security-audit.md):** the limiter holds a bounded number of counters
  (before, a made-up token on every request gave each request a fresh counter: no limit, and memory and time that
  grew with every one); requests that carry a token also count against their network address; request bodies are
  capped; every answer carries safe-browser headers; and the address comes from the edge's own header when there
  is one.
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
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
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
    # everything that carries a token, real or made up, from one network address: so made-up tokens can't each start
    # a fresh count. Several phones can share an address (a home, an office, a campus), hence well above "any"
    "address": (900, 60),
}
INSTALLS_ALL: tuple[int, int] = (300, 3600)   # new installs from everyone together

PLAN_ROUTES = {("POST", "/v1/me/plans"), ("POST", "/v1/me/testb/pair"),
               ("POST", "/v1/admin/users/{user_id}/plans")}
TRIP_ROUTES = {("POST", "/v1/me/trips/days")}
EXEMPT = {"/v1/health", "/healthz"}

MAX_KEYS = 20_000            # counters held at once; the least recently used go first (GUESS: ~3 MB at most)
# The largest real request is a trip's days with every day's own time (under 20 KB); a free-text answer is 5,000
# characters. Anything bigger isn't from the apps.
MAX_BODY_BYTES = 128 * 1024

# Safe-browser headers on every answer. The apps ignore them; they matter for the two pages a browser opens (the
# privacy notice and the share page) and keep personal answers out of any shared or on-disk cache.
HEADERS_ALL = {"X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer",
               "Strict-Transport-Security": "max-age=31536000"}
HEADERS_HTML = {"X-Frame-Options": "DENY",
                # the two pages carry their own inline style, and the share page one inline script that posts to us
                "Content-Security-Policy": ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                                            "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
                                            "form-action 'none'; frame-ancestors 'none'")}

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
    """Sliding windows in memory. Keys are hashed with a salt made at start, so not even memory holds an address.

    Two kinds of counter. Per-phone and per-address counters (made by `key`) live in a bounded table: at most
    `max_keys`, the least recently used dropped first, so a flood of made-up tokens or addresses can't grow memory
    or slow every request down (dropping a counter only ever lets someone through). Named counters ("installs-all",
    "backups-all") are few, fixed, and never dropped, so that flood can't reset an overall cap either."""
    clock: Callable[[], float] = time.monotonic
    max_keys: int = MAX_KEYS
    _salt: bytes = field(default_factory=lambda: secrets.token_bytes(16))
    _hits: OrderedDict = field(default_factory=OrderedDict)    # per phone or address: bounded
    _named: dict[str, deque] = field(default_factory=dict)     # overall caps: never dropped
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def key(self, *parts: str) -> str:
        return "k:" + hashlib.sha256(self._salt + "|".join(parts).encode()).hexdigest()[:24]

    def hit(self, key: str, limit: int, window_s: int) -> int | None:
        """Count one request; None if allowed, else the seconds until the oldest counted request leaves the window."""
        now = self.clock()
        with self._lock:
            if key.startswith("k:"):
                q = self._hits.get(key)
                if q is None:
                    q = self._hits[key] = deque()
                    while len(self._hits) > self.max_keys:     # one in, one out: never a sweep of the whole table
                        self._hits.popitem(last=False)
                else:
                    self._hits.move_to_end(key)
            else:
                q = self._named.setdefault(key, deque())
            while q and now - q[0] >= window_s:
                q.popleft()
            if len(q) >= limit:
                return max(1, int(window_s - (now - q[0])) + 1)
            q.append(now)
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
    """The phone's network address, for counting only. Render's edge is Cloudflare, which sets CF-Connecting-IP itself
    and overwrites whatever a client sent (developers.cloudflare.com/fundamentals/reference/http-headers, read
    11 Nov 2026), so it comes first. X-Forwarded-For is the fallback: the edge appends to what the client sent, so
    its first entry can be faked (Render community reports, UNVERIFIED by Render's own docs), which is why the
    overall caps exist."""
    for name in ("cf-connecting-ip", "true-client-ip"):
        if (v := request.headers.get(name, "").strip()):
            return v[:64]
    fwd = request.headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() or (request.client.host if request.client else "?"))[:64]


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


class BodyLimit:
    """Turns away request bodies over `max_bytes` with a 413, before anything reads them: by the declared length when
    there is one, else by counting what arrives. Before this, one request could carry megabytes of text into the
    database, and a few hundred could fill it (audit SEC-02)."""

    def __init__(self, app, max_bytes: int = MAX_BODY_BYTES):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        declared = dict(scope.get("headers") or []).get(b"content-length", b"")
        if declared.isdigit() and int(declared) > self.max_bytes:
            return await self._refuse(scope, send)
        seen, over, started = 0, False, False

        async def counted():
            nonlocal seen, over
            msg = await receive()
            if msg["type"] == "http.request":
                seen += len(msg.get("body") or b"")
                if seen > self.max_bytes:
                    over = True   # end the body here: nothing past the cap reaches the app
                    return {"type": "http.request", "body": b"", "more_body": False}
            return msg

        async def guarded(msg):
            nonlocal started
            if over and not started:   # the app answered a cut-off body: say what really happened instead
                started = True
                return await self._refuse(scope, send)
            if over:
                return   # the rest of the app's own answer is dropped
            await send(msg)

        await self.app(scope, counted, guarded)

    async def _refuse(self, scope, send):
        log.info("%s (body over %d bytes) 413", scope.get("method", "?"), self.max_bytes)
        body = json.dumps({"detail": "That's more than the app ever sends at once."}).encode()
        await send({"type": "http.response.start", "status": 413,
                    "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()),
                                *((k.lower().encode(), v.encode()) for k, v in HEADERS_ALL.items())]})
        await send({"type": "http.response.body", "body": body})


def _safe_headers(path: str, response) -> None:
    for k, v in HEADERS_ALL.items():
        response.headers.setdefault(k, v)
    if path.startswith("/v1/"):
        response.headers.setdefault("Cache-Control", "no-store")   # a person's answers are never cached
    if response.headers.get("content-type", "").startswith("text/html"):
        for k, v in HEADERS_HTML.items():
            response.headers.setdefault(k, v)


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
            if wait is None and who[0] == "tok":   # a token, real or made up, also counts against its address
                wait = limiter.hit(limiter.key("address", _address(request)), *LIMITS["address"])
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
        _safe_headers(path, response)
        ms = (time.perf_counter() - t0) * 1000
        log.info("%s %s %d %.0fms", method, _route(request) if route == "(no route)" else route,
                 response.status_code, ms)
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid(request: Request, exc: RequestValidationError):
        """A 422 that says where and why, and never echoes what was sent. FastAPI's own answer repeats the input: that
        can be personal, and when the input held a NaN or an infinity it couldn't be written as JSON at all, so a
        refused number became a 500 and an error alert (audit SEC-04)."""
        return JSONResponse({"detail": [{"loc": [str(x) for x in e.get("loc", ())], "msg": str(e.get("msg", "")),
                                         "type": str(e.get("type", ""))} for e in exc.errors()]}, status_code=422)

    app.add_middleware(BodyLimit)   # outermost: an oversized body is turned away before anything else runs
