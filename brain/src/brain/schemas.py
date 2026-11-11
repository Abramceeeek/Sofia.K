"""Request and response bodies for the app (the "face") and for admin tools."""

from __future__ import annotations

import json
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from .moments import Point

# Audit, 11 Nov 2026 (decisions/security-audit.md, SEC-02 to SEC-04): every list has a longest length, every number a
# range and no infinities, every clock time is a real one, and the two free-form dictionaries have a size. The limits
# sit well above what the apps send, so no real request changes.
HHMM = r"^([01]\d|2[0-3]):[0-5]\d$"          # a real time of day ("99:99" used to pass)
Tag = Annotated[str, Field(max_length=80)]   # a card id, a feeling, a filter value
Money = Annotated[float, Field(ge=0, le=1_000_000, allow_inf_nan=False)]
Lat = Annotated[float, Field(ge=-90, le=90, allow_inf_nan=False)]
Lon = Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]
MAX_FREE_JSON = 2000                          # bytes, for `intent` and an event's `props`


def _small(value: dict, what: str) -> dict:
    """A free-form dictionary no bigger than the apps ever make it (they send a few short strings)."""
    try:
        size = len(json.dumps(value, allow_nan=False))
    except (TypeError, ValueError) as e:
        raise ValueError(f"{what} must be plain JSON") from e
    if size > MAX_FREE_JSON or len(value) > 24:
        raise ValueError(f"{what} is too large")
    return value


class StartPoint(Point):
    """A point sent by a phone: on the globe, and a real number (the cards' own Point stays as it was)."""
    lat: Lat
    lon: Lon


class Consent(BaseModel):
    version: str = Field(max_length=32)   # the column's width: a longer one was an error on Postgres
    research: bool                    # agreed to take part (consent form)
    ai_processing: bool = False       # explicit permission to send their text to an AI service (App Review 5.1.2(i))


class InstallIn(BaseModel):
    channel: Literal["stranger", "friends_family"] = "stranger"   # D43
    src: str | None = Field(default=None, max_length=128)          # recruitment source, e.g. fb-ucl-hiking
    consent: Consent
    # Build 2: an optional tester code typed on the welcome screen. It names a group (where they heard about us),
    # never a person; data/tester_codes.yaml sets the channel for known codes
    code: str | None = Field(default=None, max_length=40)
    # D125: which app (the iPhone app sends nothing; the Android app sends "android"), kept as an event
    platform: Literal["ios", "android"] | None = None


class InstallOut(BaseModel):
    user_id: str
    token: str
    channel: str | None = None   # journey round 2: so the app can say when a tester code isn't known


class SwipeItem(BaseModel):
    item: int = Field(ge=1)          # one of the 16 locked swipe places (data/swipe_items.yaml, D107), as in Test A
    reaction: Literal["loved", "fine", "didnt_enjoy", "havent_been", "skip"]   # skip: "Not sure" (D110), no information


class SwipesIn(BaseModel):
    items: list[SwipeItem] = Field(max_length=64)


class CategoryItem(BaseModel):
    """D116: a visitor's answer to a category card (data/categories.yaml)."""
    key: str = Field(max_length=32)
    reaction: Literal["loved", "fine", "didnt_enjoy", "never_tried", "skip"]
    want: Literal["yes", "maybe", "no"] | None = None   # "Would you like to try it in London?", after never_tried


class CategoriesIn(BaseModel):
    items: list[CategoryItem] = Field(max_length=64)


class CorrectionsIn(BaseModel):
    """D117: the ids of the "So far, I've learned…" items the person marked "not right"."""
    items: list[Annotated[str, Field(max_length=48)]] = Field(max_length=20)


class ChoiceItem(BaseModel):
    task: int
    choice: Literal["A", "B", "N"]   # N: no preference (D110); stored, and left out of the fit


class ChoicesIn(BaseModel):
    items: list[ChoiceItem] = Field(max_length=64)


class AnswerItem(BaseModel):
    question: str = Field(max_length=64)
    text: str = Field(max_length=5000)
    input_mode: Literal["typed", "voice"] = "typed"


class AnswersIn(BaseModel):
    items: list[AnswerItem] = Field(max_length=20)


class ProfileIn(BaseModel):
    """Ask for what's needed, not the sensitive category (CLAUDE.md). All optional."""
    why_travel: list[Tag] = Field(default_factory=list, max_length=2)   # D115: feelings (reasons.FEELINGS)
    # D116: where they're based; "abroad" means the visitors' onboarding and cohort. A town or city, never nationality
    based: Literal["london", "uk", "abroad"] | None = None
    home_city: str | None = Field(default=None, max_length=80)
    budget_band: Literal["under_20", "20_40", "40_70", "70_plus"] | None = None
    company: Literal["solo", "friends", "partner", "family"] | None = None
    chronotype: Literal["morning", "night", "neither"] | None = None
    activity: Literal["gentle", "medium", "full_on"] | None = None
    grew_up: Literal["big_city", "town", "coast", "countryside"] | None = None
    # D19, D123, m223: no longer asked (D123), and never stored: free text here could hold beliefs or allergies, and
    # food needs wait for their DPIA (m215). Older builds may still send it, so it's accepted and dropped (api.py).
    foods_avoided: str | None = Field(default=None, max_length=200)
    photos_matter: int | None = Field(default=None, ge=1, le=5)        # D16
    shot_card_appeal: int | None = Field(default=None, ge=1, le=5)     # D16
    fields: list[Tag] = Field(default_factory=list, max_length=5)      # inspiring fields (D77): aspiration.yaml codes


class ConditionsIn(BaseModel):
    temp_c: float | None = Field(default=None, ge=-90, le=60, allow_inf_nan=False)   # the Earth's own range
    rain_prob: float | None = Field(default=None, ge=0, le=1)


class MyTimeIn(BaseModel):
    """m200: time that's the person's own on a trip day: "plans" (meeting someone, a booking) or "free"."""
    kind: Literal["plans", "free"]
    start: str = Field(pattern=HHMM)
    end: str = Field(pattern=HHMM)
    # m201 (Abram, 7 Nov): where the plans are, if they say; unknown leaves time to get there and back
    location: Literal["near", "elsewhere", "unknown"] = "unknown"
    meal: bool = False                 # m201: they'll eat during these plans, so no separate lunch stop


class PlanRequest(BaseModel):
    """A day to plan. The same engine as the Test B plans (brain.dayplan, D107)."""
    start: StartPoint
    # audit SEC-06: the start is the person's own position ("Start from where I am"), so it is used to plan and then
    # not kept with the plan. Older apps don't send this; they are recognised by the name they send ("where you are")
    start_is_here: bool = False
    start_name: str = Field(default="your start point", max_length=80)
    start_time: str = Field(default="12:00", pattern=HHMM)
    end_time: str = Field(default="17:00", pattern=HHMM)
    date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")   # sets open days and sunset lines
    stops: int = Field(default=4, ge=2, le=6)          # including lunch when the day spans midday (D102)
    budget_gbp: Money | None = None   # per person; default: the profile's budget band
    food_in_budget: bool = True       # m217: lunch is part of the budget unless the person leaves food out
    conditions: ConditionsIn | None = None
    familiar: bool = True             # D103: one place they loved plus new places; on by default in the app
    intent: dict = Field(default_factory=dict)   # recharge/explore, who might come, must_do (D27)
    # D110, "swap this stop": the app sends the same request again with the other stops in `keep` and the
    # swapped-out cards (this one and any before it) in `exclude`
    keep: list[Tag] = Field(default_factory=list, max_length=10)   # m200: 6 places, lunch and the person's own time
    exclude: list[Tag] = Field(default_factory=list, max_length=120)   # journey round 2: long trips exclude more
    # journey round 2: a trip day's feelings, so swap and regenerate plan it like the trip did (this plan only)
    feelings: list[Tag] = Field(default_factory=list, max_length=5)
    # D115: the blind Test B comparison: no reasons, no feeling line, no "worth to you", nothing that gives it away
    blind: bool = False
    # m200: a trip day's own time and pace, so swap, regenerate and "re-plan the rest of today" keep them
    mine: list[MyTimeIn] = Field(default_factory=list, max_length=2)
    relaxed: bool = False

    @field_validator("date")
    @classmethod
    def _real_date(cls, v: str | None) -> str | None:
        if v is not None:
            date.fromisoformat(v)   # "2026-13-45" matched the pattern and then failed inside the planner (a 500)
        return v

    @field_validator("intent")
    @classmethod
    def _small_intent(cls, v: dict) -> dict:
        return _small(v, "intent")


class CuratedStop(BaseModel):
    moment_id: str
    arrive: str = Field(pattern=HHMM)


class CuratedPlanIn(BaseModel):
    """A plan written by Abram (Wizard of Oz, Phase 3 Test B) and pushed to one tester."""
    kind: Literal["curated", "generic"] = "curated"
    label: str | None = Field(default=None, max_length=8)
    date: str | None = None
    intent: dict = Field(default_factory=dict)
    stops: list[CuratedStop]


class PlanFeedbackIn(BaseModel):
    chosen: bool
    fit_rating: int | None = Field(default=None, ge=1, le=5)
    reason: str | None = Field(default=None, max_length=2000)


class PairIn(BaseModel):
    """Build 2, screen 18 (trip intent, D27): asked just before the Test B pair and stored with both plans.
    It doesn't change either plan, so the comparison stays fair."""
    mood: Literal["recharge", "explore", "either"] | None = None
    company: Literal["solo", "friends", "partner", "family"] | None = None
    wish: str | None = Field(default=None, max_length=300)   # "Anything you'd want in it for sure?"


class PairFeedbackIn(BaseModel):
    """Build 2, screen 19: which they'd rather do (a gut reaction, D100), "This plan fits me" 1-5 for each, and why."""
    chosen: Literal["1", "2"]
    fit_1: int = Field(ge=1, le=5)
    fit_2: int = Field(ge=1, le=5)
    why: str | None = Field(default=None, max_length=2000)
    input_mode: Literal["typed", "voice"] = "typed"
    easier: Literal["1", "2", "same"] | None = None   # m196: "Which would be easier to actually do on the day?"


class SurveyIn(BaseModel):
    """Build 2, screen 16: the Test A survey (validation/interview-script.md §8). Every answer is optional."""
    understood: int | None = Field(default=None, ge=1, le=5)    # "I felt understood."
    like_person: int | None = Field(default=None, ge=1, le=5)   # "It felt like talking to a person, not filling in a form."
    typed_or_spoke: Literal["typed", "spoke", "both"] | None = None   # "Did you type or speak?" (D62)
    intrusive: str | None = Field(default=None, max_length=2000)      # "Was anything intrusive or tedious?"


class DayFeedbackIn(BaseModel):
    """D127: at the end of a day. Both optional, one tap each."""
    worth: Literal["less", "about_right", "more"] | None = None   # "Was today worth what you spent?"
    again: bool | None = None                                      # "Would you do this day again?"


class RatingIn(BaseModel):
    moment_id: str = Field(max_length=64)   # the column's width
    rating: int = Field(ge=1, le=5)
    plan_id: int | None = None
    would_bring: bool | None = None
    conditions: ConditionsIn | None = None
    # a day at most, and a real number: an infinity here was stored, then broke the admin export for everyone
    travel_min: float | None = Field(default=None, ge=0, le=1440, allow_inf_nan=False)


class EventIn(BaseModel):
    name: str = Field(max_length=64)
    props: dict = Field(default_factory=dict)

    @field_validator("props")
    @classmethod
    def _small_props(cls, v: dict) -> dict:
        return _small(v, "props")


class SafetyIn(BaseModel):
    message: str = Field(default="", max_length=2000)
    contact: str | None = Field(default=None, max_length=120)   # D118: optional phone or email, only to reply


class SafetyReplyIn(BaseModel):
    replied_by: str = Field(max_length=64)
    text: str | None = Field(default=None, max_length=2000)    # D118: shown to the person in Help & safety
    resolved: bool = False                                      # D118: deletes the contact they left


# ---- D120: trips (flights and stays; links out, never booked here) ------------------------------------------------

Minutes = Annotated[int, Field(ge=0, le=1439)]


class FlightFiltersIn(BaseModel):
    max_stops: int | None = Field(default=None, ge=0, le=2)
    stops: list[Annotated[int, Field(ge=0, le=2)]] = Field(default_factory=list, max_length=3)   # 2 = "2 or more"
    out_times: list[Literal["night", "morning", "afternoon", "evening"]] = Field(default_factory=list, max_length=4)
    in_times: list[Literal["night", "morning", "afternoon", "evening"]] = Field(default_factory=list, max_length=4)
    out_depart: tuple[Minutes, Minutes] | None = None      # minutes after midnight, local
    in_depart: tuple[Minutes, Minutes] | None = None
    max_leg_min: int | None = Field(default=None, ge=30, le=4000)
    airlines: list[Tag] = Field(default_factory=list, max_length=30)
    max_price: Money | None = None
    checked_bag: bool = False
    refundable: bool = False
    sort: Literal["best", "cheapest", "fastest"] = "best"


class FlightSearchIn(BaseModel):
    origin: str = Field(pattern=r"^[A-Za-z]{3}$")           # IATA airport or city code
    destination: str = Field(default="london", max_length=40)                            # a destination key (brain/data/airports.yaml)
    depart_date: date
    return_date: date | None = None
    adults: int = Field(default=1, ge=1, le=9)
    children: list[Annotated[int, Field(ge=0, le=17)]] = Field(default_factory=list, max_length=8)
    cabin: Literal["economy", "premium_economy", "business", "first"] = "economy"
    filters: FlightFiltersIn = Field(default_factory=FlightFiltersIn)
    display_currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$")   # m238: the person's currency (estimates only)


class StayFiltersIn(BaseModel):
    max_night: Money | None = None
    min_night: Money | None = None
    min_stars: float | None = Field(default=None, ge=0, le=5)
    min_rating: float | None = Field(default=None, ge=0, le=10)
    kinds: list[Tag] = Field(default_factory=list, max_length=10)
    refundable: bool = False
    breakfast: bool = False
    max_km: float | None = Field(default=None, gt=0, le=100)
    sort: Literal["recommended", "price", "rating", "distance"] = "recommended"


class StaySearchIn(BaseModel):
    destination: str = Field(default="london", max_length=40)
    checkin: date
    checkout: date
    adults: int = Field(default=2, ge=1, le=9)
    children: list[Annotated[int, Field(ge=0, le=17)]] = Field(default_factory=list, max_length=8)
    rooms: int = Field(default=1, ge=1, le=5)
    filters: StayFiltersIn = Field(default_factory=StayFiltersIn)
    display_currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$")   # m238: the person's currency (estimates only)


class StayRefIn(BaseModel):
    """m203: the stay the person is looking at, as the search found it."""
    id: str = Field(max_length=64)
    name: str = Field(max_length=200)
    lat: Lat | None = None
    lon: Lon | None = None
    price_total: float = Field(ge=0, le=100_000_000, allow_inf_nan=False)   # any currency, so a wide range
    nights: int = Field(ge=1, le=30)
    currency: str = Field(default="GBP", max_length=3)
    room: str = Field(default="", max_length=200)
    board: str = Field(default="", max_length=80)
    refundable: bool | None = None
    pay_there: float = Field(default=0.0, ge=0, le=100_000_000, allow_inf_nan=False)
    sample: bool = False


class DayEndsIn(BaseModel):
    """m203: one planned day's first and last place, so the stay can be judged against the trip."""
    index: int = Field(ge=0, le=30)
    first: StartPoint | None = None
    last: StartPoint | None = None


class StayCompareIn(BaseModel):
    """m203: a stay against the person's trip: their dates and guests, and their planned days."""
    destination: str = Field(default="london", max_length=40)
    checkin: date
    checkout: date
    adults: int = Field(default=2, ge=1, le=9)
    children: list[Annotated[int, Field(ge=0, le=17)]] = Field(default_factory=list, max_length=8)
    rooms: int = Field(default=1, ge=1, le=5)
    stay: StayRefIn
    days: list[DayEndsIn] = Field(default_factory=list, max_length=31)


class TripEndIn(BaseModel):
    """D122: how a trip starts or ends: by flight (an airport code), train (a station code, brain/data/arrivals.yaml)
    or car, and the local time (landing, the train's arrival, or for the way home, the departure)."""
    mode: Literal["flight", "train", "car"]
    place: str | None = Field(default=None, max_length=8)
    time: str = Field(pattern=HHMM)


class TripLengthIn(BaseModel):
    """m196: "How long should I stay?" The person's own day (hours, places a day) and, if chosen, their nights."""
    destination: str = Field(default="london", max_length=40)
    nights: int | None = Field(default=None, ge=0, le=30)
    feelings: list[Tag] = Field(default_factory=list, max_length=2)
    day_start: str = Field(default="10:00", pattern=HHMM)
    day_end: str = Field(default="18:00", pattern=HHMM)
    stops_per_day: int = Field(default=4, ge=1, le=6)


class DayTimeIn(BaseModel):
    """m200: how one day of a trip should leave room for the person (product direction, step 2)."""
    day: int = Field(ge=0, le=30)
    free_day: bool = False             # nothing planned: the day is theirs
    relaxed: bool = False              # one place fewer, longer at each
    mine: list[MyTimeIn] = Field(default_factory=list, max_length=2)


class TripDaysIn(BaseModel):
    """D120: the days of a multi-day trip (ODYS Trips design: "How long for?", "How should the trip feel?")."""
    destination: str = Field(default="london", max_length=40)
    start_date: date
    nights: int = Field(ge=0, le=30)
    feelings: list[Tag] = Field(default_factory=list, max_length=2)      # reasons.FEELINGS
    stay: StartPoint | None = None                                       # the chosen place to stay, if any
    stay_name: str | None = Field(default=None, max_length=120)
    arrive_time: str | None = Field(default=None, pattern=HHMM)   # landing on day 1, local
    leave_time: str | None = Field(default=None, pattern=HHMM)    # the flight home on the last day
    days: list[Annotated[int, Field(ge=0, le=30)]] = Field(default_factory=list, max_length=7)   # which days; default the first 7
    exclude: list[Tag] = Field(default_factory=list, max_length=200)     # moments already in the trip's other days
    # D122 (Abram, 6 Oct): the person's own day, and how the trip starts and ends
    day_start: str = Field(default="10:00", pattern=HHMM)
    day_end: str = Field(default="18:00", pattern=HHMM)
    stops_per_day: int = Field(default=4, ge=1, le=6)
    travel_light: bool = False                                           # no big bags on the first day
    arrive: TripEndIn | None = None                                      # replaces arrive_time when sent
    leave: TripEndIn | None = None                                       # replaces leave_time when sent
    personal: list[DayTimeIn] = Field(default_factory=list, max_length=31)   # m200: the person's own time, by day
