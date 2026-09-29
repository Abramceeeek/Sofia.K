"""Request and response bodies for the app (the "face") and for admin tools."""

from __future__ import annotations

from typing import Literal

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


class InstallOut(BaseModel):
    user_id: str
    token: str


class SwipeItem(BaseModel):
    item: int = Field(ge=1)          # one of the 16 locked swipe places (data/swipe_items.yaml, D107), as in Test A
    reaction: Literal["loved", "fine", "didnt_enjoy", "havent_been", "skip"]   # skip: "Not sure" (D110), no information


class SwipesIn(BaseModel):
    items: list[SwipeItem]


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
    why_travel: list[str] = Field(default_factory=list, max_length=2)
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
    exclude: list[str] = Field(default_factory=list, max_length=40)


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


class SafetyReplyIn(BaseModel):
    replied_by: str = Field(max_length=64)
