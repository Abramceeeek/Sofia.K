"""D116: category cards, the visitors' onboarding (data/categories.yaml, after-9-nov #31).

Kinds of place ("big museums", "views from above") as tagged pseudo-places, like the swipe places, so an answer enters
the fit the same way. Shown only to people who answer "Visiting from abroad"; they are their own group (cohort
"visitor") and are left out of the Test B analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .features import moment_features
from .moments import Moment
from .personal import Observation
from .population import PopulationModel
from .scoring import swipe_observation

WANT_SCALE = 0.5   # GUESS: "I'd like to try it" is a stated choice, weaker than a this-or-that answer (as FEELING_SCALE)


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    line: str
    phrase: str          # inside a sentence: "You love big museums, …"
    example: str         # a ready London card whose photo the app shows
    moment: Moment       # the tags, as a pseudo-place


@dataclass(frozen=True)
class Categories:
    prompt: str
    note: str
    want_prompt: str
    items: dict[str, Category]


def load_categories(path: Path) -> Categories | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    items = {}
    for key, it in d["items"].items():
        m = Moment.model_validate({"id": f"cat_{key}", "title": it["title"], "place": {"name": it["title"]},
                                   "features": {"place": it["place"], "moment": it["moment"]},
                                   "cost_gbp": None, "source": "category-card"})
        items[key] = Category(key, it["title"], it["line"], it["phrase"], it["example"], m)
    return Categories(d["prompt"], d["note"], d["want_prompt"], items)


def category_observation(pop: PopulationModel, cat: Category, reaction: str, want: str | None) -> Observation | None:
    """Love it / Fine / Not for me: exactly like a place swipe. Never tried + "would you like to?": a stated choice."""
    if reaction in ("loved", "fine", "didnt_enjoy"):
        return swipe_observation(pop, cat.moment, reaction)
    if reaction == "never_tried" and want in ("yes", "no"):
        return Observation(x=pop.vector(moment_features(cat.moment)), y=1 if want == "yes" else 0,
                           scale=pop.scales["conjoint"] * WANT_SCALE)
    return None


def cohort(profile: dict | None) -> str:
    """D116: "visitor" (visiting from abroad: category cards, left out of the Test B analysis) or "resident"."""
    return "visitor" if (profile or {}).get("based") == "abroad" else "resident"
