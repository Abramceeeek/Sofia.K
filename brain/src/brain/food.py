"""WS2 (m208): food needs and what a venue can honestly be said to offer. Design and tests only: **nothing here is
stored, sent or used in a plan yet** (decisions/food-preferences-and-privacy.md: consent, a DPIA and a checked data
source come first).

Three rules, enforced here rather than left to good intentions:
1. **Nothing is inferred.** A venue's status comes only from evidence with a source and a date: a certifier's own
   directory, the venue's own words, or a community map tag. Cuisine, ownership, neighbourhood, a name or a photo are
   never evidence, and no function here accepts them.
2. **Certified means a named certifier, a source and a recent check.** Anything else is said for what it is: "the
   venue says…", "mapped as…", or unknown.
3. **One purpose.** A person's food needs are used only for their own suggestions. Any other use (matching people,
   advertising, analytics) raises, so it can't happen by accident.

Allergies are different: ODYS never says a venue is safe for an allergy. Allergen information is the venue's to give
for each dish (Food Standards Agency guidance), so the app only ever says "ask the venue".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from .places import PlaceRecord

NEEDS = ("halal", "kosher", "vegetarian", "vegan", "no_alcohol")   # what someone may choose; each is optional
# The 14 allergens UK law names (Food Standards Agency, allergen guidance for food businesses)
ALLERGENS = ("celery", "cereals_gluten", "crustaceans", "eggs", "fish", "lupin", "milk", "molluscs", "mustard",
             "tree_nuts", "peanuts", "sesame", "soya", "sulphites")
PURPOSE = "own_suggestions"
CERTIFIED_MAX_AGE_DAYS = 90   # GUESS: a certifier's listing older than this is shown as "last confirmed on <date>"

Status = Literal["certified", "whole_menu", "some_dishes", "not_suitable", "unknown"]
Evidence = Literal["certifier_directory", "venue_own", "community_tag", "our_visit"]


class PurposeError(PermissionError):
    """Food needs used for anything but the person's own suggestions."""


@dataclass(frozen=True)
class Consent:
    """Explicit consent, recorded as given: which text, when, for what. Withdrawing deletes the needs."""
    text_version: str
    given_on: date
    purpose: str = PURPOSE


@dataclass(frozen=True)
class FoodNeeds:
    needs: frozenset[str]
    strict: frozenset[str] = frozenset()    # e.g. {"halal"}: certified only, not "the venue says"
    consent: Consent | None = None

    def __post_init__(self):
        unknown = (self.needs | self.strict) - set(NEEDS)
        if unknown:
            raise ValueError(f"not food needs ODYS offers: {sorted(unknown)}")
        if not self.strict <= self.needs:
            raise ValueError("strict needs must be among the needs")
        if self.needs and self.consent is None:
            raise ValueError("food needs are kept only with the person's explicit consent")

    def use(self, purpose: str) -> frozenset[str]:
        """The needs, for one purpose only. Matching people, advertising or analytics raise (CLAUDE.md, D19)."""
        if purpose != PURPOSE or (self.consent and self.consent.purpose != PURPOSE):
            raise PurposeError(f"food needs are used only for the person's own suggestions, not {purpose!r}")
        return self.needs


@dataclass(frozen=True)
class VenueFood:
    """What is known about one need at one venue, with where it came from."""
    need: str
    status: Status
    evidence: Evidence | None = None
    source: str | None = None               # a URL: the certifier's listing, the venue's page, the map element
    certifier: str | None = None            # e.g. "Halal Monitoring Committee": only with certifier_directory
    verified_on: date | None = None         # when that source last showed it
    venue_says: str | None = None           # the venue's own words, quoted, when it has said something
    dishes: tuple[str, ...] = ()            # dishes the source names as suitable, if it names any

    def __post_init__(self):
        if self.need not in NEEDS:
            raise ValueError(f"unknown need {self.need!r}")
        if self.status == "certified" and not (self.evidence == "certifier_directory" and self.certifier
                                               and self.source and self.verified_on):
            raise ValueError("certified needs a certifier, its directory as the source, and the date it showed it")
        if self.status != "unknown" and (self.evidence is None or not self.source):
            raise ValueError("any status but unknown needs its evidence and source")
        if self.evidence == "community_tag" and self.status == "certified":
            raise ValueError("a map tag is never certification")


def unknown(need: str) -> VenueFood:
    return VenueFood(need, "unknown")


Fit = Literal["suits", "may_suit", "not_suitable", "unknown"]


@dataclass(frozen=True)
class FitLine:
    need: str
    fit: Fit
    line: str                                # what the person reads


def fit(need: str, v: VenueFood, strict: bool, today: date) -> FitLine:
    """How a venue fits one need, in words that never claim more than the evidence."""
    label = {"halal": "halal", "kosher": "kosher", "vegetarian": "vegetarian", "vegan": "vegan",
             "no_alcohol": "alcohol-free"}[need]
    if v.status == "unknown":
        return FitLine(need, "unknown", f"Not known whether it's {label}: check with the venue.")
    if v.status == "not_suitable":
        return FitLine(need, "not_suitable", f"Not {label}, according to {_who(v)}.")
    if v.status == "certified":
        age = (today - v.verified_on).days
        when = f"{v.verified_on.day} {v.verified_on:%b %Y}"
        if age > CERTIFIED_MAX_AGE_DAYS:
            return FitLine(need, "may_suit", f"Listed by {v.certifier} when last checked on {when}: check it's current.")
        return FitLine(need, "suits", f"Certified {label} by {v.certifier} (their listing, checked {when}).")
    what = "its whole menu is" if v.status == "whole_menu" else "some dishes are"
    line = f"{_who(v).capitalize()} says {what} {label}"
    line += f": {', '.join(v.dishes)}." if v.dishes else "."
    if strict:
        line += " Not certified."
    return FitLine(need, "may_suit", line)


def _who(v: VenueFood) -> str:
    return {"venue_own": "the venue", "community_tag": "a community map", "our_visit": "our visit",
            "certifier_directory": v.certifier or "the certifier"}.get(v.evidence or "", "a source")


def allergy_line(allergens: frozenset[str]) -> str:
    """Never "safe": the venue gives allergen information dish by dish (FSA)."""
    if not allergens:
        return ""
    return ("For allergies, ask the venue before ordering: they must tell you which of the 14 allergens are in each "
            "dish. ODYS can't confirm what's safe for you.")


def from_place(rec: PlaceRecord) -> dict[str, VenueFood]:
    """A place record's food claims (e.g. OSM `diet:halal`) as statuses. A community tag is at most "some dishes" or
    "whole menu", never certified; a need the record says nothing about is unknown."""
    out = {n: unknown(n) for n in NEEDS if n != "no_alcohol"}
    for need, f in rec.diet.items():
        if need not in out or not f.known:
            continue
        status = {"only": "whole_menu", "yes": "some_dishes", "limited": "some_dishes", "no": "not_suitable"}[f.value]
        out[need] = VenueFood(need, status, "community_tag" if rec.provider == "osm" else "venue_own",
                              f.source or rec.id, verified_on=date.fromisoformat(f.checked) if f.checked else None)
    return out


@dataclass
class Suggestion:
    """A food stop for one person: how it fits each of their needs, and the allergy line. Never ranked by a guess."""
    venue: str
    lines: list[FitLine] = field(default_factory=list)
    allergy: str = ""

    @property
    def fits(self) -> bool:
        return all(l.fit == "suits" for l in self.lines)


def suggest(needs: FoodNeeds, venues: dict[str, dict[str, VenueFood]], today: date,
            allergens: frozenset[str] = frozenset()) -> list[Suggestion]:
    """Venues with each need's fit. Venues that don't suit a need are left out; the rest are sorted so evidence comes
    first (suits, then may suit, then unknown), never by anything inferred."""
    wanted = needs.use(PURPOSE)
    order = {"suits": 0, "may_suit": 1, "unknown": 2}
    out = []
    for name, food in venues.items():
        lines = [fit(n, food.get(n, unknown(n)), n in needs.strict, today) for n in sorted(wanted)]
        if any(l.fit == "not_suitable" for l in lines):
            continue
        if any(l.fit != "suits" for l in lines if l.need in needs.strict):
            continue   # a strict need: certified (and current) only
        out.append(Suggestion(name, lines, allergy_line(allergens)))
    return sorted(out, key=lambda s: (max(order[l.fit] for l in s.lines) if s.lines else 0, s.venue))
