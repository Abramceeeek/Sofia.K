"""Request and response bodies for the app (the "face") and for admin tools."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from .moments import Point


class Consent(BaseModel):
    version: str
    research: bool                    # agreed to take part (consent form)
    ai_processing: bool = False       # explicit permission to send their text to an AI service (App Review 5.1.2(i))


class InstallIn(BaseModel):
    channel: Literal["stranger", "friends_family"] = "stranger"   # D43
    src: str | None = Field(default=None, max_length=128)          # recruitment source, e.g. fb-ucl-hiking
    consent: Consent
    # Build 2: an optional tester code typed on the welcome screen. It names a group (where they heard about us),
    # never a person; data/tester_codes.yaml sets the channel for known codes
    code: str | None = Field(default=None, max_length=40)


class InstallOut(BaseModel):
    user_id: str
    token: str
    channel: str | None = None   # journey round 2: so the app can say when a tester code isn't known


class SwipeItem(BaseModel):
    item: int = Field(ge=1)          # one of the 16 locked swipe places (data/swipe_items.yaml, D107), as in Test A
    reaction: Literal["loved", "fine", "didnt_enjoy", "havent_been", "skip"]   # skip: "Not sure" (D110), no information


class SwipesIn(BaseModel):
    items: list[SwipeItem]


class CategoryItem(BaseModel):
    """D116: a visitor's answer to a category card (data/categories.yaml)."""
    key: str = Field(max_length=32)
    reaction: Literal["loved", "fine", "didnt_enjoy", "never_tried", "skip"]
    want: Literal["yes", "maybe", "no"] | None = None   # "Would you like to try it in London?", after never_tried


class CategoriesIn(BaseModel):
    items: list[CategoryItem]


class CorrectionsIn(BaseModel):
    """D117: the ids of the "So far, I've learned…" items the person marked "not right"."""
    items: list[str] = Field(max_length=20)


class ChoiceItem(BaseModel):
    task: int
    choice: Literal["A", "B", "N"]   # N: no preference (D110); stored, and left out of the fit


class ChoicesIn(BaseModel):
    items: list[ChoiceItem]


class AnswerItem(BaseModel):
    question: str = Field(max_length=64)
    text: str = Field(max_length=5000)
    input_mode: Literal["typed", "voice"] = "typed"


class AnswersIn(BaseModel):
    items: list[AnswerItem]


class ProfileIn(BaseModel):
    """Ask for what's needed, not the sensitive category (CLAUDE.md). All optional."""
    why_travel: list[str] = Field(default_factory=list, max_length=2)   # D115: feelings (reasons.FEELINGS)
    # D116: where they're based; "abroad" means the visitors' onboarding and cohort. A town or city, never nationality
    based: Literal["london", "uk", "abroad"] | None = None
    home_city: str | None = Field(default=None, max_length=80)
    budget_band: Literal["under_20", "20_40", "40_70", "70_plus"] | None = None
    company: Literal["solo", "friends", "partner", "family"] | None = None
    chronotype: Literal["morning", "night", "neither"] | None = None
    activity: Literal["gentle", "medium", "full_on"] | None = None
    grew_up: Literal["big_city", "town", "coast", "countryside"] | None = None
    foods_avoided: str | None = Field(default=None, max_length=200)   # D19: optional, no allergy question
    photos_matter: int | None = Field(default=None, ge=1, le=5)        # D16
    shot_card_appeal: int | None = Field(default=None, ge=1, le=5)     # D16
    fields: list[str] = Field(default_factory=list, max_length=5)      # inspiring fields (D77): aspiration.yaml codes


class ConditionsIn(BaseModel):
    temp_c: float | None = None
    rain_prob: float | None = Field(default=None, ge=0, le=1)


class PlanRequest(BaseModel):
    """A day to plan. The same engine as the Test B plans (brain.dayplan, D107)."""
    start: Point
    start_name: str = Field(default="your start point", max_length=80)
    start_time: str = Field(default="12:00", pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(default="17:00", pattern=r"^\d{2}:\d{2}$")
    date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")   # sets open days and sunset lines
    stops: int = Field(default=4, ge=2, le=6)          # including lunch when the day spans midday (D102)
    budget_gbp: float | None = Field(default=None, ge=0)   # per person; default: the profile's budget band
    conditions: ConditionsIn | None = None
    familiar: bool = True             # D103: one place they loved plus new places; on by default in the app
    intent: dict = Field(default_factory=dict)   # recharge/explore, who might come, must_do (D27)
    # D110, "swap this stop": the app sends the same request again with the other stops in `keep` and the
    # swapped-out cards (this one and any before it) in `exclude`
    keep: list[str] = Field(default_factory=list, max_length=6)
    exclude: list[str] = Field(default_factory=list, max_length=120)   # journey round 2: long trips exclude more
    # journey round 2: a trip day's feelings, so swap and regenerate plan it like the trip did (this plan only)
    feelings: list[str] = Field(default_factory=list, max_length=5)
    # D115: the blind Test B comparison: no reasons, no feeling line, no "worth to you", nothing that gives it away
    blind: bool = False


class CuratedStop(BaseModel):
    moment_id: str
    arrive: str = Field(pattern=r"^\d{2}:\d{2}$")


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


class SurveyIn(BaseModel):
    """Build 2, screen 16: the Test A survey (validation/interview-script.md §8). Every answer is optional."""
    understood: int | None = Field(default=None, ge=1, le=5)    # "I felt understood."
    like_person: int | None = Field(default=None, ge=1, le=5)   # "It felt like talking to a person, not filling in a form."
    typed_or_spoke: Literal["typed", "spoke", "both"] | None = None   # "Did you type or speak?" (D62)
    intrusive: str | None = Field(default=None, max_length=2000)      # "Was anything intrusive or tedious?"


class RatingIn(BaseModel):
    moment_id: str
    rating: int = Field(ge=1, le=5)
    plan_id: int | None = None
    would_bring: bool | None = None
    conditions: ConditionsIn | None = None
    travel_min: float | None = Field(default=None, ge=0)


class EventIn(BaseModel):
    name: str = Field(max_length=64)
    props: dict = Field(default_factory=dict)


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
    out_depart: tuple[Minutes, Minutes] | None = None      # minutes after midnight, local
    in_depart: tuple[Minutes, Minutes] | None = None
    max_leg_min: int | None = Field(default=None, ge=30, le=4000)
    airlines: list[str] = Field(default_factory=list, max_length=30)
    max_price: float | None = Field(default=None, ge=0)
    checked_bag: bool = False
    refundable: bool = False
    sort: Literal["best", "cheapest", "fastest"] = "best"


class FlightSearchIn(BaseModel):
    origin: str = Field(pattern=r"^[A-Za-z]{3}$")           # IATA airport or city code
    destination: str = "london"                            # a destination key (brain/data/airports.yaml)
    depart_date: date
    return_date: date | None = None
    adults: int = Field(default=1, ge=1, le=9)
    children: list[Annotated[int, Field(ge=0, le=17)]] = Field(default_factory=list, max_length=8)
    cabin: Literal["economy", "premium_economy", "business", "first"] = "economy"
    filters: FlightFiltersIn = Field(default_factory=FlightFiltersIn)


class StayFiltersIn(BaseModel):
    max_night: float | None = Field(default=None, ge=0)
    min_night: float | None = Field(default=None, ge=0)
    min_stars: float | None = Field(default=None, ge=0, le=5)
    min_rating: float | None = Field(default=None, ge=0, le=10)
    kinds: list[str] = Field(default_factory=list, max_length=10)
    refundable: bool = False
    breakfast: bool = False
    max_km: float | None = Field(default=None, gt=0, le=100)
    sort: Literal["recommended", "price", "rating", "distance"] = "recommended"


class StaySearchIn(BaseModel):
    destination: str = "london"
    checkin: date
    checkout: date
    adults: int = Field(default=2, ge=1, le=9)
    children: list[Annotated[int, Field(ge=0, le=17)]] = Field(default_factory=list, max_length=8)
    rooms: int = Field(default=1, ge=1, le=5)
    filters: StayFiltersIn = Field(default_factory=StayFiltersIn)


class TripEndIn(BaseModel):
    """D122: how a trip starts or ends: by flight (an airport code), train (a station code, brain/data/arrivals.yaml)
    or car, and the local time (landing, the train's arrival, or for the way home, the departure)."""
    mode: Literal["flight", "train", "car"]
    place: str | None = Field(default=None, max_length=8)
    time: str = Field(pattern=r"^\d{2}:\d{2}$")


class TripDaysIn(BaseModel):
    """D120: the days of a multi-day trip (ODYS Trips design: "How long for?", "How should the trip feel?")."""
    destination: str = "london"
    start_date: date
    nights: int = Field(ge=0, le=30)
    feelings: list[str] = Field(default_factory=list, max_length=2)      # reasons.FEELINGS
    stay: Point | None = None                                            # the chosen place to stay, if any
    stay_name: str | None = Field(default=None, max_length=120)
    arrive_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")   # landing on day 1, local
    leave_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")    # the flight home on the last day
    days: list[Annotated[int, Field(ge=0, le=30)]] = Field(default_factory=list, max_length=7)   # which days; default the first 7
    exclude: list[str] = Field(default_factory=list, max_length=200)     # moments already in the trip's other days
    # D122 (Abram, 6 Oct): the person's own day, and how the trip starts and ends
    day_start: str = Field(default="10:00", pattern=r"^\d{2}:\d{2}$")
    day_end: str = Field(default="18:00", pattern=r"^\d{2}:\d{2}$")
    stops_per_day: int = Field(default=4, ge=1, le=6)
    travel_light: bool = False                                           # no big bags on the first day
    arrive: TripEndIn | None = None                                      # replaces arrive_time when sent
    leave: TripEndIn | None = None                                       # replaces leave_time when sent
