"""Hidden-preference synthetic travellers for the engine bench (batch 9, m364, work C). **Synthetic, not people.**

Independent of the engine by construction (Abram: "don't let the benchmark become circular again"):
- this module imports **nothing from `brain`**: no scoring, no features, no exclusion rules, no population model
  (`tests/test_hidden_bench.py` checks its imports);
- each place's hidden attributes come from the catalogue's kind and the card's own words (its id and title), with
  ODYS's tags, place records and aspiration map never read;
- each traveller's true taste includes dimensions the person model can't see (art, science, shopping, nightlife,
  architecture), and a private, place-by-place idiosyncrasy no feature can explain;
- what the app sees is noisy and incomplete: a reaction is the true enjoyment plus noise, some places are "haven't
  been", interests are picked only sometimes, "this or that" answers flip at random.

Every number here is a GUESS chosen to look like a plausible mix of people; none is evidence about real travellers.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

DIMS = ("art", "history", "science", "food", "nature", "views", "shopping", "nightlife", "kids", "active",
        "culture", "architecture", "walk", "ride")

# Each catalogue kind's attributes (0-1), by Claude's own reading of the kind's name, not from any ODYS tag.
KIND = {
    "museum": {"history": 0.5, "science": 0.3}, "gallery": {"art": 1.0}, "historic_site": {"history": 1.0},
    "market": {"food": 0.8, "shopping": 0.4}, "market_hall": {"food": 0.4, "architecture": 0.6, "shopping": 0.4},
    "food_street": {"food": 1.0, "nightlife": 0.3}, "restaurant": {"food": 1.0}, "bakery": {"food": 0.8},
    "cafe": {"food": 0.6}, "park": {"nature": 1.0, "walk": 0.5}, "garden": {"nature": 0.9},
    "wild_park": {"nature": 1.0, "walk": 0.8, "views": 0.4}, "roof_garden": {"views": 1.0, "nature": 0.3},
    "tower": {"views": 1.0, "architecture": 0.4}, "viewpoint": {"views": 1.0, "walk": 0.3},
    "bridge": {"views": 0.7, "walk": 0.5, "architecture": 0.3}, "river_bus": {"ride": 1.0, "views": 0.6},
    "riverside": {"views": 0.6, "walk": 0.6}, "riverside_walk": {"walk": 1.0, "views": 0.5},
    "waterfront": {"walk": 0.8, "views": 0.3}, "department_store": {"shopping": 1.0, "architecture": 0.4},
    "arcade": {"shopping": 0.8, "architecture": 0.5}, "karting": {"active": 1.0}, "cycling": {"active": 0.8,
    "nature": 0.4}, "swimming": {"active": 0.9, "nature": 0.3}, "performance": {"culture": 1.0},
    "arts_centre": {"culture": 0.7, "art": 0.4}, "evening_area": {"nightlife": 1.0, "food": 0.4},
    "area_walk": {"walk": 0.8, "shopping": 0.4, "food": 0.3}, "architecture_walk": {"architecture": 1.0, "walk": 0.6},
}
# Words in a card's id or title that add an attribute (Claude's reading of the words; never an ODYS tag).
WORDS = [
    (r"natural history|nhm|science", {"science": 1.0, "kids": 0.5}), (r"maritime|cutty|painted|queens",
    {"history": 0.8}), (r"gold|bank of england", {"history": 0.6, "science": 0.2}),
    (r"tate|gallery|courtauld|portrait|soane", {"art": 0.8}), (r"playground|diana", {"kids": 1.0}),
    (r"night|evening|late|sunset", {"nightlife": 0.4, "views": 0.3}), (r"dim sum|dishoom|padella|steak|flat iron|"
    r"poppies|wahaca|beigel", {"food": 0.4}), (r"library|dickens|johnson", {"history": 0.6, "culture": 0.4}),
    (r"evensong", {"culture": 0.6, "architecture": 0.5}), (r"liberty|timber", {"architecture": 0.6}),
    (r"boat", {"ride": 0.4}), (r"karting|bike|lido", {"active": 0.4, "kids": 0.3}),
]
BUSY = {"market": 0.9, "museum": 0.6, "gallery": 0.5, "roof_garden": 0.6, "tower": 0.5, "food_street": 0.7,
        "restaurant": 0.5, "department_store": 0.6, "historic_site": 0.4, "river_bus": 0.5, "evening_area": 0.7,
        "area_walk": 0.6, "market_hall": 0.6}
BUSY_WORDS = r"borough|covent|portobello|spitalfields|chinatown|camden|soho|great court|whale"

# The archetypes' mean tastes; every traveller adds their own noise. busy: dislike of crowds; cost: price sensitivity.
ARCHETYPES = {
    "food": {"food": 1.5}, "quiet": {"nature": 1.0, "busy": 1.5}, "history": {"history": 1.5, "culture": 0.5},
    "kids": {"kids": 1.5, "science": 0.6, "active": 0.4}, "budget": {"cost": 1.5}, "art": {"art": 1.5,
    "architecture": 0.5}, "views": {"views": 1.5, "architecture": 0.4}, "shopper": {"shopping": 1.5},
    "night": {"nightlife": 1.5, "food": 0.5}, "science": {"science": 1.5, "kids": 0.2},
}
BASE = 0.2         # everyone likes a bit of everything
TASTE_SD = 0.4     # how much one traveller differs from their archetype
PLACE_SD = 0.5     # the private, place-by-place part no feature explains
REACT_SD = 0.4     # noise between true enjoyment and the swipe they give
NOT_BEEN = 0.25    # the chance they haven't been to a swipe place
FLIP = 0.15        # the chance a "this or that" answer goes the other way


def _seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


@dataclass(frozen=True)
class Place:
    id: str
    title: str
    kind: str | None
    cost: float
    attrs: dict[str, float]
    busy: float


def load_world(data_dir: Path) -> tuple[dict[str, Place], dict[int, list[str]], list[int]]:
    """The ready places with their hidden attributes, the swipe items' cards, and the items the app shows."""
    cat = yaml.safe_load((data_dir / "catalogue" / "london.yaml").read_text()) or {}
    kinds = {k: v.get("type") for k, v in (cat.get("experiences") or {}).items()}
    places = {}
    for f in sorted((data_dir / "moments").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        if not isinstance(d, dict) or d.get("status") != "ready":
            continue
        cid, title = d["id"], str(d.get("title", ""))
        kind = kinds.get(cid)
        a = dict(KIND.get(kind, {}))
        text = f"{cid} {title}".lower().replace("_", " ")
        for pat, add in WORDS:
            if re.search(pat, text):
                for k, v in add.items():
                    a[k] = min(1.0, a.get(k, 0.0) + v)
        busy = BUSY.get(kind, 0.3) + (0.3 if re.search(BUSY_WORDS, text) else 0.0)
        places[cid] = Place(cid, title, kind, float(d.get("cost_gbp") or 0.0), a, min(busy, 1.0))
    sw = yaml.safe_load((data_dir / "swipe_items.yaml").read_text())
    items = {int(n): list(it.get("cards") or []) for n, it in sw["items"].items()}
    shown = list(sw.get("app_items") or []) + list(sw.get("app_items_later") or [])
    return places, items, shown


@dataclass(frozen=True)
class Hidden:
    key: str
    archetype: str
    taste: dict[str, float]      # weights on DIMS, plus "busy" and "cost"
    eps: dict[str, float]        # the private place-by-place part
    children: tuple[int, ...]

    def enjoy(self, p: Place) -> float:
        u = sum(self.taste.get(d, 0.0) * p.attrs.get(d, 0.0) for d in DIMS)
        u -= self.taste.get("busy", 0.0) * p.busy
        u -= self.taste.get("cost", 0.0) * p.cost / 20.0
        return u + self.eps.get(p.id, 0.0)


def make_traveller(archetype: str, n: int, places: dict[str, Place]) -> Hidden:
    rng = np.random.default_rng(_seed("taste", archetype, n))
    mean = ARCHETYPES[archetype]
    taste = {d: BASE + mean.get(d, 0.0) + float(rng.normal(0, TASTE_SD)) for d in DIMS}
    taste["busy"] = max(0.0, mean.get("busy", 0.2) + float(rng.normal(0, TASTE_SD)))
    taste["cost"] = max(0.0, mean.get("cost", 0.3) + float(rng.normal(0, TASTE_SD / 2)))
    eps = {pid: float(np.random.default_rng(_seed("eps", archetype, n, pid)).normal(0, PLACE_SD)) for pid in places}
    kids = (6, 9) if archetype == "kids" else ()
    return Hidden(f"{archetype}-{n}", archetype, taste, eps, kids)


def observe(h: Hidden, places: dict[str, Place], items: dict[int, list[str]], shown: list[int]) -> dict:
    """What the traveller tells the app: a profile, swipes and a rule for the "this or that" days. Noisy, partial."""
    rng = np.random.default_rng(_seed("observe", h.key))
    us = sorted(h.enjoy(p) for p in places.values())
    hi, lo = us[int(0.75 * len(us))], us[int(0.25 * len(us))]
    swipes = {}
    for it in shown:
        cards = [c for c in items.get(it, []) if c in places]
        if not cards or rng.random() < NOT_BEEN:
            swipes[it] = "havent_been"
            continue
        u = np.mean([h.enjoy(places[c]) for c in cards]) + rng.normal(0, REACT_SD)
        swipes[it] = "loved" if u >= hi else "didnt_enjoy" if u <= lo else "fine"
    t = h.taste
    fields = [f for f, d in (("food", "food"), ("history_culture", "history"), ("nature", "nature"))
              if t[d] > 1.0 and rng.random() < 0.8]
    why = [w for w, ok in (("peaceful", t["busy"] > 0.9), ("excited", t["active"] > 1.0 or t["nightlife"] > 1.0),
                           ("curious", t["history"] > 1.0 or t["science"] > 1.0 or t["art"] > 1.0),
                           ("connected", bool(h.children)), ("restored", t["nature"] > 1.0)) if ok][:2]   # the app takes two
    profile = {"based": "london", "company": "family" if h.children else str(rng.choice(["solo", "friends",
               "partner"])), "budget_band": "under_20" if t["cost"] > 1.0 else "40_70",
               "activity": "full_on" if t["active"] > 1.0 else "gentle" if t["busy"] > 1.2 else "medium",
               "chronotype": "neither", "fields": fields, "why_travel": why}
    return {"profile": profile, "swipes": swipes, "children": h.children,
            "prefers": "quiet" if t["busy"] > 0.9 else "cheap" if t["cost"] > 1.0 else
            "packed" if t["active"] > 1.0 else None, "flip_seed": _seed("flip", h.key)}


def choose(task: dict, prefers: str | None, rng: np.random.Generator) -> str:
    """A "this or that" answer from the hidden preference, with FLIP noise. Reads only the task's own words."""
    a, b = task["A"], task["B"]
    pick = "N"
    if prefers == "quiet":
        pick = "A" if "mostly quiet" in a and "mostly quiet" not in b else "B" if "mostly quiet" in b else "N"
    elif prefers == "cheap":
        ca, cb = (float(m.group(1)) if (m := re.search(r"£(\d+)", x)) else 0.0 for x in (a, b))
        pick = "A" if ca < cb else "B" if cb < ca else "N"
    elif prefers == "packed":
        pick = "A" if "5 stops" in a else "B" if "5 stops" in b else "N"
    if pick in ("A", "B") and rng.random() < FLIP:
        pick = "B" if pick == "A" else "A"
    return pick


def similarity(a: Hidden, b: Hidden) -> float:
    """Cosine similarity of two hidden tastes (centred), for "does overlap track real similarity?"."""
    keys = list(DIMS) + ["busy", "cost"]
    x = np.array([a.taste[k] for k in keys]) - BASE
    y = np.array([b.taste[k] for k in keys]) - BASE
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))
