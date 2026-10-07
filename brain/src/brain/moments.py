"""The moment record (Area 2 schema, D9) and a loader for the YAML files in data/moments."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PLACE_TAGS = [
    "movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel",
    "crowds", "walking_effort", "active", "outdoor_exposure", "photo_potential",
]
MOMENT_TAGS = ["contrast_reveal", "absorption", "awe", "social_pull"]

_GENERIC_WORDS = {"Park", "Street", "Road", "Gate", "Square", "London", "City", "Station"}
_WINDOW = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


class Point(BaseModel):
    lat: float
    lon: float


class Place(BaseModel):
    name: str
    overture_id: str | None = None
    lat: float | None = None
    lon: float | None = None


class Approach(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str | None = Field(default=None, alias="from")
    start_point: Point | None = None
    path: str | None = None
    duration_min: float | None = None
    step_free: bool | None = None


class Experience(BaseModel):
    what_happens: str | None = None
    why_it_works: str | None = None
    # One number, or [min, max]; the planner uses the midpoint.
    duration_min: float | list[float] | None = None
    end_point: Point | None = None
    end_name: str | None = None   # where you are when it ends, e.g. "Westminster Pier" (the plan's "from" line)
    end_station: str | None = None   # D102: the station to walk to when leaving (default: approach.from if a station)
    queue_min: float | None = None   # D102: usual queue at a popular stop, added to the time there and told to people


class BestTime(BaseModel):
    time_of_day: list[str] = Field(default_factory=list)  # "hh:mm-hh:mm"
    light: str | None = None
    weather: list[str] = Field(default_factory=list)       # e.g. ["dry"] or ["any"]
    company: str | None = None
    crowd_window: str | None = None
    opening_hours: str | None = None
    # Journey audit (7 Oct): a booking the visit needs, said to the person on the stop ("Book a timed ticket…").
    # Only from the card's checked source; empty means none is needed or none was found.
    book_ahead: str | None = None
    # Days the card can be planned ("mon".."sun"); empty means every day. Keeps weekday-only
    # museums out of weekend plans. Different hours on different days still wait (after-9-nov #7).
    days: list[str] = Field(default_factory=list)
    # D100: when `light` is worth telling people ("hh:mm-hh:mm"). A plan shows "Best: <light>" only if the stop
    # overlaps one of these windows; with none, the line is never shown.
    best_window: list[str] = Field(default_factory=list)
    # D105: when the light line depends on sunset, the window in minutes from sunset, e.g. [-40, 20]. Used when the
    # brief gives the sunset time; `best_window` is the fallback (set for late October and November).
    best_around_sunset: list[int] | None = None


class Features(BaseModel):
    place: dict[str, int | None] = Field(default_factory=dict)
    moment: dict[str, int | None] = Field(default_factory=dict)


class StandAt(BaseModel):
    lat: float | None = None
    lon: float | None = None
    note: str | None = None


class ShotCard(BaseModel):
    stand_at: StandAt | None = None
    face: str | None = None
    frame: str | None = None
    when: str | None = None
    avoid: str | None = None


class Moment(BaseModel):
    id: str
    title: str
    plan_title: str | None = None  # D102: the title shown in plans, when the automatic "Place: title" reads badly
    feel_word: str | None = None   # D119: the word on "How the day moves" when the tags pick a poor one ("Drifting")
    status: str = "draft"          # draft | ready
    swipe: bool = False            # part of the onboarding swipe set
    # D72: "moment" is one specific experience; "area" is an area vibe (a wander, a street scene)
    # with a centre point instead of an approach path. The planner allows one area a day.
    kind: Literal["moment", "area"] = "moment"
    variant_of: str | None = None  # shared by variants of one moment (day / night): one per plan
    variant: str | None = None     # e.g. "day", "night"
    direction: str | None = None   # for routes where order matters, e.g. "Greenwich → Battersea"
    place: Place
    approach: Approach = Field(default_factory=Approach)
    experience: Experience = Field(default_factory=Experience)
    best_time: BestTime = Field(default_factory=BestTime)
    features: Features = Field(default_factory=Features)
    cost_gbp: float | None = None
    # D100: what the price pays for, so a plan never calls food "entry". Empty: food if the food tag is 2, else entry.
    cost_kind: Literal["food", "entry", "ticket", "hire"] | None = None
    # D104: a card that is a meal ("Lunch in the crypt…") is only ever planned as the day's lunch stop
    meal: Literal["lunch"] | None = None
    in_test_b: bool = True         # D105: False keeps a card out of Test B plans (e.g. booking plus price); the app keeps it
    shot_card: ShotCard | None = None
    source: str = "founder"
    last_checked: str | None = None

    # ---- derived values the planner needs ---------------------------------
    def tag(self, name: str) -> int | None:
        if name in PLACE_TAGS:
            return self.features.place.get(name)
        return self.features.moment.get(name)

    def duration_min(self) -> float | None:
        """Approach walk plus the experience itself. The approach is part of the moment."""
        exp = self.experience.duration_min
        if isinstance(exp, list):
            exp = sum(exp) / len(exp) if exp else None
        if exp is None or self.approach.duration_min is None:
            return None
        return float(self.approach.duration_min) + float(exp) + float(self.experience.queue_min or 0)

    def exit_station(self) -> str | None:
        """Where to walk to catch the Tube or bus onwards (D102)."""
        if self.experience.end_station:
            return self.experience.end_station
        if self.experience.end_point is None and self.approach.from_ and "station" in self.approach.from_.lower():
            return self.approach.from_
        return None

    def display_title(self) -> str:
        """The title with the place's name in front when the title doesn't already name it (D102), e.g.
        "The Garden at 120: a rooftop garden among the City towers"."""
        if self.plan_title:
            return self.plan_title
        place = re.split(r"[:,()]", self.place.name)[0].strip()
        words = {w for w in re.findall(r"[A-Z][\w'-]{3,}", place) if w not in _GENERIC_WORDS}
        if not words or any(w in self.title for w in words):
            return self.title
        first, _, rest = self.title.partition(" ")
        title = f"{first.lower()} {rest}" if first in ("A", "An", "The") else self.title
        return f"{place}: {title}"

    def start(self) -> Point | None:
        return self.approach.start_point

    def end(self) -> Point | None:
        return self.experience.end_point or self.approach.start_point

    def leave_name(self) -> str:
        """A short name for where you are when the moment ends ("from X" in the next stop's directions)."""
        if self.experience.end_name:
            return self.experience.end_name
        return re.split(r"[:,(]", self.place.name)[0].strip()

    def windows(self) -> list[tuple[int, int]]:
        """Allowed time windows in minutes from midnight, from best_time.time_of_day."""
        return parse_windows(self.best_time.time_of_day, self.id)

    def best_windows(self, sunset: int | None = None) -> list[tuple[int, int]]:
        """When the `light` line applies (D100), in minutes from midnight; relative to `sunset` when the card says
        so and a sunset time is known (D105)."""
        rel = self.best_time.best_around_sunset
        if rel and sunset is not None:
            return [(sunset + rel[0], sunset + rel[1])]
        return parse_windows(self.best_time.best_window, self.id)

    def price_kind(self) -> str:
        """What `cost_gbp` pays for: food, entry, ticket or hire (D100)."""
        if self.cost_kind:
            return self.cost_kind
        return "food" if (self.features.place.get("food") or 0) >= 2 else "entry"

    def missing_for_planning(self) -> list[str]:
        """Fields the planner needs that are still empty. An empty list means plannable."""
        missing = []
        if self.approach.start_point is None:
            missing.append("approach.start_point")
        if self.approach.duration_min is None:
            missing.append("approach.duration_min")
        if self.experience.duration_min is None:
            missing.append("experience.duration_min")
        if not self.best_time.time_of_day:
            missing.append("best_time.time_of_day")
        if self.cost_gbp is None:
            missing.append("cost_gbp")
        for t in PLACE_TAGS:
            if self.features.place.get(t) is None:
                missing.append(f"features.place.{t}")
        for t in MOMENT_TAGS:
            if self.features.moment.get(t) is None:
                missing.append(f"features.moment.{t}")
        try:
            self.windows()
        except ValueError:
            missing.append("best_time.time_of_day (format)")
        try:
            self.best_windows()
        except ValueError:
            missing.append("best_time.best_window (format)")
        if any(d.lower() not in WEEKDAYS for d in self.best_time.days):
            missing.append("best_time.days (format)")
        return missing

    def open_on(self, weekday: str | None) -> bool:
        """Can the card be planned on this day ("mon".."sun")? No listed days means every day."""
        if weekday is None or not self.best_time.days:
            return True
        return weekday.lower()[:3] in {d.lower() for d in self.best_time.days}

    def plannable(self) -> bool:
        return not self.missing_for_planning()


def parse_windows(windows: list[str], owner: str = "") -> list[tuple[int, int]]:
    """["hh:mm-hh:mm", ...] as sorted (start, end) minutes from midnight."""
    out = []
    for w in windows:
        m = _WINDOW.match(w)
        if not m:
            raise ValueError(f"{owner}: time window {w!r} is not 'hh:mm-hh:mm'")
        h1, m1, h2, m2 = (int(x) for x in m.groups())
        out.append((h1 * 60 + m1, h2 * 60 + m2))
    return sorted(out)


def load_moment_file(path: Path) -> Moment:
    with open(path, encoding="utf-8") as f:
        return Moment.model_validate(yaml.safe_load(f))


def load_moments(directory: Path) -> list[Moment]:
    return [load_moment_file(p) for p in sorted(Path(directory).glob("*.yaml"))]
