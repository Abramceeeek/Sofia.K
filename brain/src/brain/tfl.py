"""Real journey times from the TfL Journey Planner (roadmap Stage 1, step 3).

The planner asks for the time between every pair of candidate stops (thousands per plan), so TfL can't be asked
while planning. Instead:

1. **A table, filled in the background.** Every pair of ready cards (one's end, the next one's start) and Charing
   Cross to each card, when the pair is beyond a 20-minute walk. That's about 2,000 journeys for 49 cards
   (19 Oct). They're asked for a weekday at 13:00, at most WARM_PER_MIN a minute (TfL allows 500 a minute with a
   key), kept in the database, and refreshed after REFRESH_DAYS. Shorter pairs stay walks, as before.
2. **The chosen day, checked for its date.** After a plan is made, its Tube and bus legs are asked for that day
   (weekend closures change journeys), and the day is planned once more with what TfL said: the times and the
   lines' names. At most CHECK_MAX legs, in parallel, within CHECK_TIMEOUT_S; whatever doesn't answer keeps the
   table's time. A leg already checked for that day (within DAY_TTL_S) isn't asked again.

Without a key, or before a pair is in the table, the straight-line estimate is used (`travel.LondonEstimate`), so
nothing breaks. The reply's legs give the words: "walk to Westminster Station, then Jubilee line to London
Bridge". TfL's terms ask for "Powered by TfL Open Data" in the app's credits (DfT's catalogue entry, read 9 Oct).
API: `GET https://api.tfl.gov.uk/Journey/JourneyResults/{lat,lon}/to/{lat,lon}` with `app_key`, `date`, `time`
(one keyless call checked 19 Oct: `journeys[].duration` in minutes, `legs[].mode.id`, `legs[].instruction.summary`).
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable, Iterable

from .moments import Point
from .travel import LondonEstimate

log = logging.getLogger("brain.tfl")

TFL_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/{a}/to/{b}"
WARM_PER_MIN = 200          # well under TfL's 500 a minute, leaving room for the day checks
REFRESH_DAYS = 14           # timetables change; weekend works are caught by the day check instead
CHECK_MAX = 12              # legs checked per plan (a day has at most 7)
CHECK_TIMEOUT_S = 8.0
DAY_TTL_S = 6 * 3600        # a day's checked leg is reused for six hours

Fetch = Callable[[str, dict[str, str]], dict]


def _http_fetch(url: str, params: dict[str, str]) -> dict:
    import httpx
    r = httpx.get(url, params=params, timeout=10.0)
    r.raise_for_status()
    return r.json()


def key(p: Point) -> str:
    """~100 m: close enough that two points on the same corner share a journey."""
    return f"{p.lat:.3f},{p.lon:.3f}"


@dataclass(frozen=True)
class Journey:
    minutes: float
    mode: str                  # "walk" | "transit"
    route: str | None = None   # "walk to Westminster Station, then Jubilee line to London Bridge"


def _cap(s: str) -> str:
    return s[:1].lower() + s[1:] if s.startswith("Walk") else s


def summarise(legs: list[dict]) -> str | None:
    """The legs in words: the walk to the first station, then each Tube, bus or train leg (TfL's own summaries)."""
    parts: list[str] = []
    for i, leg in enumerate(legs):
        mode = ((leg.get("mode") or {}).get("id") or "").lower()
        text = ((leg.get("instruction") or {}).get("summary") or "").strip()
        if not text:
            continue
        if mode == "walking":
            nxt = legs[i + 1] if i + 1 < len(legs) else None
            if i == 0 and nxt and ((nxt.get("mode") or {}).get("id") or "").lower() != "walking":
                parts.append(_cap(text))
            continue
        parts.append(text)
    return ", then ".join(parts) or None


def parse(payload: dict) -> Journey | None:
    """The journey arriving first. All-walking journeys count as walks."""
    best, best_arrival = None, None
    for j in payload.get("journeys") or []:
        if not isinstance(j.get("duration"), (int, float)):
            continue
        arrival = j.get("arrivalDateTime") or ""
        if best is None or (arrival and (not best_arrival or arrival < best_arrival)):
            best, best_arrival = j, arrival
    if best is None:
        return None
    legs = best.get("legs") or []
    modes = {((leg.get("mode") or {}).get("id") or "").lower() for leg in legs}
    mode = "walk" if modes <= {"walking"} else "transit"
    return Journey(float(best["duration"]), mode, None if mode == "walk" else summarise(legs))


class TflClient:
    def __init__(self, app_key: str, fetch: Fetch | None = None):
        self.app_key = app_key
        self.fetch = fetch or _http_fetch
        self.calls = 0
        self.errors = 0

    def journey(self, a: Point, b: Point, when: datetime) -> Journey | None:
        url = TFL_URL.format(a=f"{a.lat:.5f},{a.lon:.5f}", b=f"{b.lat:.5f},{b.lon:.5f}")
        params = {"app_key": self.app_key, "date": when.strftime("%Y%m%d"), "time": when.strftime("%H%M"),
                  "timeIs": "Departing", "journeyPreference": "LeastTime"}
        self.calls += 1
        try:
            return parse(self.fetch(url, params))
        except Exception as e:  # noqa: BLE001 - one journey failing never fails a plan
            self.errors += 1
            log.warning("TfL journey failed: %s", type(e).__name__)   # the key is in the URL params: never logged
            return None


class TravelStore:
    """The table in the database (`db.TravelTime`), so a restart doesn't ask TfL again."""

    def __init__(self, Session):
        self.Session = Session

    def load(self) -> dict[tuple[str, str], tuple[float, Journey]]:
        from sqlalchemy import select

        from . import db
        with self.Session() as s:
            return {(r.a, r.b): (r.fetched_at.timestamp() if r.fetched_at.tzinfo else
                                 r.fetched_at.replace(tzinfo=timezone.utc).timestamp(),
                                 Journey(r.minutes, r.mode, r.route))
                    for r in s.scalars(select(db.TravelTime))}

    def save(self, a: str, b: str, j: Journey) -> None:
        from sqlalchemy import select

        from . import db
        try:
            with self.Session() as s:
                row = s.scalar(select(db.TravelTime).where(db.TravelTime.a == a, db.TravelTime.b == b))
                if row is None:
                    s.add(db.TravelTime(a=a, b=b, minutes=j.minutes, mode=j.mode, route=j.route))
                else:
                    row.minutes, row.mode, row.route, row.fetched_at = j.minutes, j.mode, j.route, db.now()
                s.commit()
        except Exception:  # noqa: BLE001 - the table in memory still has it
            log.exception("TfL table: saving a journey failed")


def next_weekday_1pm(today: date) -> datetime:
    """The table's reference time: the coming Wednesday at 13:00, a normal weekday service."""
    d = today + timedelta(days=(2 - today.weekday()) % 7 or 7)
    return datetime(d.year, d.month, d.day, 13, 0)


class TflTravel(LondonEstimate):
    """`LondonEstimate`, with TfL's time wherever the table has the pair."""

    def __init__(self, app_key: str, store=None, fetch: Fetch | None = None, clock: Callable[[], float] = time.time,
                 **kw):
        super().__init__(**kw)
        self.client = TflClient(app_key, fetch)
        self.store = store                     # TravelStore: keeps the table across restarts
        self.clock = clock
        self.table: dict[tuple[str, str], tuple[float, Journey]] = {}     # (a, b) → (fetched_at, journey)
        self.day: dict[tuple[str, str, str], tuple[float, Journey]] = {}  # (a, b, yyyy-mm-dd) → …
        self.wanted = 0
        self._stop = threading.Event()
        if store is not None:
            self.table.update(store.load())

    # ---- what the planner asks -------------------------------------------------------------------
    def _known(self, a: Point, b: Point) -> Journey | None:
        hit = self.table.get((key(a), key(b)))
        return hit[1] if hit else None

    def minutes(self, a: Point, b: Point) -> float:
        walk = self.walking.minutes(a, b)
        if walk <= self.walk_max_min:
            return walk
        j = self._known(a, b)
        return min(walk, j.minutes) if j else super().minutes(a, b)

    def mode(self, a: Point, b: Point) -> str:
        if self.walking.minutes(a, b) <= self.walk_max_min:
            return "walk"
        j = self._known(a, b)
        return j.mode if j else super().mode(a, b)

    def route(self, a: Point, b: Point) -> str | None:
        j = self._known(a, b)
        return j.route if j else None

    def for_day(self, day: date | None, start: str = "12:00") -> "DayView":
        return DayView(self, day, start)

    @property
    def status(self) -> str:
        """For /v1/health: "tfl" once the table is full, "tfl_filling n/N" while it fills."""
        have = len(self.table)
        return "tfl" if self.wanted and have >= self.wanted else f"tfl_filling {have}/{self.wanted or '?'}"

    # ---- filling the table -----------------------------------------------------------------------
    def pairs(self, points: Iterable[tuple[Point, Point]]) -> list[tuple[Point, Point]]:
        """The pairs worth asking TfL about: beyond a walk, one per ~100 m corner pair."""
        seen, out = set(), []
        for a, b in points:
            if a is None or b is None:   # a draft card without its points
                continue
            k = (key(a), key(b))
            if k in seen or k[0] == k[1] or self.walking.minutes(a, b) <= self.walk_max_min:
                continue
            seen.add(k)
            out.append((a, b))
        return out

    def fill(self, pairs: list[tuple[Point, Point]], when: datetime, per_min: int = WARM_PER_MIN,
             sleep: Callable[[float], None] = time.sleep) -> int:
        """Asks TfL for the pairs not in the table (or older than REFRESH_DAYS). Returns how many were added."""
        self.wanted = len(pairs)
        now = self.clock()
        todo = [(a, b) for a, b in pairs
                if (hit := self.table.get((key(a), key(b)))) is None or now - hit[0] > REFRESH_DAYS * 86400]
        added = 0
        for a, b in todo:
            if self._stop.is_set():
                break
            j = self.client.journey(a, b, when)
            if j is not None:
                self.table[(key(a), key(b))] = (self.clock(), j)
                if self.store is not None:
                    self.store.save(key(a), key(b), j)
                added += 1
            sleep(60.0 / per_min)
        if added:
            log.info("TfL table: %s journeys added, %s of %s known", added, len(self.table), self.wanted)
        return added

    def fill_in_background(self, pairs: list[tuple[Point, Point]], when: datetime) -> threading.Thread:
        t = threading.Thread(target=self.fill, args=(pairs, when), name="tfl-table", daemon=True)
        t.start()
        return t

    def stop(self) -> None:
        self._stop.set()


class DayView:
    """One plan's view of the times: the day's checked legs first, then the table, then the estimate. It notes the
    legs the plan chose (`mode` is asked for each one), so `check` can ask TfL about them for that day."""

    def __init__(self, base: TflTravel, day: date | None, start: str):
        self.base, self.day_ = base, day
        self.walking, self.walk_max_min = base.walking, base.walk_max_min
        h, m = (int(x) for x in start[:5].split(":"))
        self.when = datetime(day.year, day.month, day.day, h, m) if day else None
        self.chosen: dict[tuple[str, str], tuple[Point, Point, float]] = {}   # legs the plan chose
        self.checks = 0

    def _dated(self, a: Point, b: Point) -> Journey | None:
        if self.day_ is None:
            return None
        hit = self.base.day.get((key(a), key(b), self.day_.isoformat()))
        return hit[1] if hit and self.base.clock() - hit[0] < DAY_TTL_S else None

    def minutes(self, a: Point, b: Point) -> float:
        j = self._dated(a, b)
        if j and self.walking.minutes(a, b) > self.walk_max_min:
            return min(self.walking.minutes(a, b), j.minutes)
        return self.base.minutes(a, b)

    def mode(self, a: Point, b: Point) -> str:
        self.chosen.setdefault((key(a), key(b)), (a, b, self.minutes(a, b)))
        j = self._dated(a, b)
        if j and self.walking.minutes(a, b) > self.walk_max_min:
            return j.mode
        return self.base.mode(a, b)

    def route(self, a: Point, b: Point) -> str | None:
        j = self._dated(a, b)
        return j.route if j else self.base.route(a, b)

    def check(self) -> bool:
        """Asks TfL about the chosen Tube and bus legs on this day. True if it learned something, so the day is
        planned again with it (the times, and the words for each leg)."""
        if self.when is None:
            return False
        today = datetime.now(timezone.utc).date()
        if not (today - timedelta(days=1) <= self.day_ <= today + timedelta(days=28)):
            return False   # GUESS: TfL plans about four weeks ahead; further out, the table's weekday time stands
        todo = [(a, b, used) for (ka, kb), (a, b, used) in self.chosen.items()
                if self.walking.minutes(a, b) > self.walk_max_min
                and (ka, kb, self.day_.isoformat()) not in self.base.day][:CHECK_MAX]
        if not todo:
            return False
        learned = False
        pool = ThreadPoolExecutor(max_workers=min(6, len(todo)))
        try:
            futures = {pool.submit(self.base.client.journey, a, b, self.when): (a, b) for a, b, _ in todo}
            done, _ = wait(futures, timeout=CHECK_TIMEOUT_S)
            for f in done:
                a, b = futures[f]
                j = f.result()
                if j is None:
                    continue
                self.base.day[(key(a), key(b), self.day_.isoformat())] = (self.base.clock(), j)
                learned = True
        finally:
            pool.shutdown(wait=False, cancel_futures=True)   # a slow answer never holds up the plan
        self.checks += len(todo)
        self.chosen.clear()
        return learned
