"""Real weather from the Met Office (roadmap Stage 1, step 4).

The forecast fills the conditions the model already uses (D95): the rain and cold terms on outdoor stops
(`features.py`), and the rain swaps when rain is likely (`dayplan.py`). It is used only when the app doesn't send
conditions of its own (the "it's raining" re-plan does).

- **Source:** the Met Office Weather DataHub site-specific "Global spot" API
  (`https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/{hourly|daily}`). The key goes in the `apikey` header
  (the open-source datapoint-python client, read 19 Oct 2026). Hourly runs 48 h ahead and daily 7 days (one past,
  six ahead; DataHub's Global spot overview, read 19 Oct 2026).
- **One place for all of London:** central London. Day plans stay within a few miles of it.
- **Calls:** the hourly forecast is kept for an hour and the daily one for three hours, so at most about 32 calls
  a day, inside the free plan's 360 (sources.csv, 26 Sep). A failed call is retried no sooner than 10 minutes later,
  and the plan goes ahead without weather, as before.
- **For a plan's hours:** within 48 h, the mean temperature and the mean chance of rain over the plan's hours.
  Further ahead, the day's maximum temperature and the day's chance of rain × DAILY_RAIN_SHARE.
- **Field names:** hourly `screenTemperature` and `probOfPrecipitation` are confirmed (datapoint-python's
  documentation, read 19 Oct 2026). The daily names (`dayMaxScreenTemperature`, `dayProbabilityOfPrecipitation`)
  are UNVERIFIED, so they are looked up by pattern, and `/v1/health` says if they weren't found.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo

log = logging.getLogger("brain.weather")

MET_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/"
LONDON_CENTRE = (51.5074, -0.1278)   # Trafalgar Square, the start of most plans
LONDON = ZoneInfo("Europe/London")
HOURLY_TTL_S = 3600
DAILY_TTL_S = 3 * 3600
RETRY_AFTER_S = 600
# GUESS: the day's chance of rain is the chance of any rain in the daytime, which overstates the share of a 4–6 hour
# plan that is wet. The hourly mean (used within 48 h) is the better measure; this keeps the two roughly comparable.
DAILY_RAIN_SHARE = 0.7

Fetch = Callable[[str, dict[str, str], dict[str, str]], dict]


def _http_fetch(url: str, headers: dict[str, str], params: dict[str, str]) -> dict:
    import httpx
    r = httpx.get(url, headers=headers, params=params, timeout=10.0)
    r.raise_for_status()
    return r.json()


@dataclass(frozen=True)
class Outlook:
    """The weather for a plan's hours: what the model uses, and one line for the person."""
    temp_c: float | None
    rain_prob: float | None    # 0–1
    source: str                # "hourly" | "daily"

    @property
    def line(self) -> str:
        parts = []
        if self.temp_c is not None:
            parts.append(f"about {round(self.temp_c)}°C")
        if self.rain_prob is not None:
            parts.append(f"{int(round(self.rain_prob * 100, -1))}% chance of rain")
        return "Forecast: " + ", ".join(parts) + " (Met Office)" if parts else ""

    def out(self) -> dict[str, Any]:
        return {"temp_c": None if self.temp_c is None else round(self.temp_c, 1),
                "rain_prob": None if self.rain_prob is None else round(self.rain_prob, 2),
                "source": self.source, "line": self.line}


def _series(payload: dict) -> list[dict]:
    try:
        return list(payload["features"][0]["properties"]["timeSeries"])
    except (KeyError, IndexError, TypeError):
        return []


def _when(entry: dict) -> datetime | None:
    t = entry.get("time")
    if not isinstance(t, str):
        return None
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00"))
    except ValueError:
        return None


def _num(entry: dict, *names: str, contains: tuple[str, ...] = ()) -> float | None:
    """The first of `names` present, else the first key containing every word in `contains` (case-insensitive)."""
    for n in names:
        v = entry.get(n)
        if isinstance(v, (int, float)):
            return float(v)
    if contains:
        for k, v in entry.items():
            if isinstance(v, (int, float)) and all(w in k.lower() for w in contains):
                return float(v)
    return None


def _mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


class Forecast:
    """The Met Office forecast for central London, cached. Without a key it is off and returns nothing."""

    def __init__(self, api_key: str | None, fetch: Fetch | None = None, clock: Callable[[], float] = time.time):
        self.api_key = api_key
        self.fetch = fetch or _http_fetch
        self.clock = clock
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._failed: dict[str, float] = {}
        self._lock = threading.Lock()
        self.calls = 0
        self.daily_fields_ok: bool | None = None

    @property
    def status(self) -> str:
        """For /v1/health: "off" (no key), "met_office", or "met_office_error" (the last call failed)."""
        if not self.api_key:
            return "off"
        return "met_office_error" if self._failed else "met_office"

    def _get(self, kind: str) -> list[dict]:
        if not self.api_key:
            return []
        ttl = HOURLY_TTL_S if kind == "hourly" else DAILY_TTL_S
        now = self.clock()
        with self._lock:
            hit = self._cache.get(kind)
            if hit and now - hit[0] < ttl:
                return hit[1]
            if now - self._failed.get(kind, -1e18) < RETRY_AFTER_S:
                return hit[1] if hit else []
        try:
            lat, lon = LONDON_CENTRE
            payload = self.fetch(MET_URL + kind, {"apikey": self.api_key, "accept": "application/json"},
                                 {"latitude": str(lat), "longitude": str(lon), "includeLocationName": "false",
                                  "excludeParameterMetadata": "true"})
            series = _series(payload)
            if not series:
                raise ValueError("no timeSeries in the reply")
        except Exception as e:  # noqa: BLE001 - weather is a bonus: a plan never fails for it
            log.warning("Met Office %s forecast failed: %s", kind, type(e).__name__)
            with self._lock:
                self._failed[kind] = now
            return hit[1] if hit else []
        with self._lock:
            self.calls += 1
            self._cache[kind] = (now, series)
            self._failed.pop(kind, None)
        return series

    def for_window(self, day: date, start: str, end: str) -> Outlook | None:
        """The weather over a plan's hours ("12:00"–"17:00", London time) on `day`, or None if it isn't known."""
        if not self.api_key:
            return None
        h0, m0 = (int(x) for x in start[:5].split(":"))
        h1, m1 = (int(x) for x in end[:5].split(":"))
        t0 = datetime(day.year, day.month, day.day, h0, m0, tzinfo=LONDON).astimezone(timezone.utc)
        t1 = datetime(day.year, day.month, day.day, h1, m1, tzinfo=LONDON).astimezone(timezone.utc)
        if t1 <= t0:
            return None
        now = datetime.fromtimestamp(self.clock(), timezone.utc)
        if t1 < now - timedelta(hours=1):
            return None
        if t0 <= now + timedelta(hours=47):
            hours = [e for e in self._get("hourly") if (w := _when(e)) and t0 <= w < t1]
            if hours:
                temps = [v for e in hours if (v := _num(e, "screenTemperature")) is not None]
                rain = [v / 100 for e in hours if (v := _num(e, "probOfPrecipitation")) is not None]
                if temps or rain:
                    return Outlook(_mean(temps), _mean(rain), "hourly")
        for e in self._get("daily"):
            w = _when(e)
            if w is None or w.astimezone(LONDON).date() != day:
                continue
            temp = _num(e, "dayMaxScreenTemperature", contains=("day", "max", "temp"))
            rain = _num(e, "dayProbabilityOfPrecipitation", contains=("day", "probabilityof", "precip"))
            self.daily_fields_ok = temp is not None and rain is not None
            if temp is None and rain is None:
                return None
            return Outlook(temp, None if rain is None else min(1.0, rain / 100 * DAILY_RAIN_SHARE), "daily")
        return None

    def now(self) -> Outlook | None:
        """The weather this hour, saved with a rating (CLAUDE.md: ratings are logged with their conditions)."""
        if not self.api_key:
            return None
        now = datetime.fromtimestamp(self.clock(), timezone.utc)
        best: tuple[float, dict] | None = None
        for e in self._get("hourly"):
            w = _when(e)
            if w is None:
                continue
            gap = abs((w - now).total_seconds())
            if gap <= 3600 and (best is None or gap < best[0]):
                best = (gap, e)
        if best is None:
            return None
        e = best[1]
        rain = _num(e, "probOfPrecipitation")
        return Outlook(_num(e, "screenTemperature"), None if rain is None else rain / 100, "hourly")
