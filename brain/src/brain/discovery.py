"""m239 (WS4, Global Destination Intelligence): discovering places when someone doesn't know where they want to go,
without a generic feed.

Every answer is **at most three things** (`LIMIT`), each a moment or a destination, never an endless list. Each says
**why**, from the inputs it was chosen by: the score's own taste terms by name (as "Why this stop?", m230), the
season note's source, the time and budget it fits. Each carries the four-perspective quality check (quality.py), and
anything weak on practicality, money or trust never outranks a sound suggestion.

The discovery kinds Abram listed:
- **destinations** worth going to, for this person, among those ODYS is ready to recommend (destination.readiness);
- **neighbourhoods** within one, by how well its moments fit;
- **hidden local** moments: local and new-to-you, and seldom in other people's plans (popularity.yaml);
- **seasonal**: the destination's dated season notes for the month, and the moments they name;
- **food**: interest in food experiences only, never a diet or a belief (food.py handles those, with consent);
- **time and budget**: what fits "two hours and £20".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import yaml

from . import quality
from .catalogue import Experience
from .config import DATA_DIR
from .destination import Profile
from .explain import p_good as _p_good
from .features import moment_features
from .moments import MOMENT_TAGS, PLACE_TAGS, Moment
from .population import PopulationModel
from .scoring import contributions

LIMIT = 3
TASTE_GROUPS = ("place", "moment", "person")


@dataclass(frozen=True)
class Suggestion:
    id: str                         # an experience id, or a destination key
    title: str
    why: tuple[str, ...]            # at most three, each from an input that chose it
    assessment: quality.Assessment | None


def cost_gbp(x: Experience, rates=None) -> float | None:
    """m249: the price in pounds for the model's cost term (it is per £10). Another currency is converted only with
    a rate (fx.Rates); without one the cost is unknown. Before m249 it was dropped, so every price outside the UK
    scored as free."""
    if not x.price.known:
        return None
    m = x.price.value
    if m.currency == "GBP":
        return m.amount
    if rates is not None and m.currency in rates.per_eur and "GBP" in rates.per_eur:
        return round(m.amount / rates.per_eur[m.currency] * rates.per_eur["GBP"], 2)
    return None


def _moment(x: Experience, rates=None) -> Moment:
    """The catalogue's features as a pseudo-moment, so the model scores any experience the same way."""
    place = {k: v for k, v in x.features.items() if k in PLACE_TAGS}
    mom = {k: v for k, v in x.features.items() if k in MOMENT_TAGS}
    cost = cost_gbp(x, rates)
    return Moment.model_validate({"id": x.id, "title": x.title, "place": {"name": x.name, "lat": x.geo.lat,
                                  "lon": x.geo.lon}, "features": {"place": place, "moment": mom},
                                  "cost_gbp": cost, "source": "catalogue"})


class Scorer:
    """One person's taste over experiences: utility, the chance of "Good" or better, and the taste terms behind it."""

    def __init__(self, pop: PopulationModel, delta: np.ndarray | None, rates=None):
        self.pop, self.b, self.rates = pop, pop.b_person(delta), rates
        self.taste = {n for n in pop.names if pop.spec(n).group in TASTE_GROUPS}

    def utility(self, x: Experience) -> float:
        return float(self.pop.vector(moment_features(_moment(x, self.rates))) @ self.b)

    def p_good(self, x: Experience) -> float:
        return _p_good(self.pop.scales["rating"], self.pop.cutpoints["rating"][1], self.utility(x))

    def likes(self, x: Experience, n: int = 2) -> list[str]:
        terms = contributions(self.pop, self.b, moment_features(_moment(x, self.rates)), top=6)
        return [t["label"] for t in terms if t["feature"] in self.taste and t["contribution"] >= 0.05][:n]


def _why_taste(s: Scorer, x: Experience) -> str | None:
    likes = s.likes(x)
    return f"From your answers, it has what you like: {', '.join(likes)}." if likes else None


def _assess(s: Scorer, x: Experience, today: date, **kw) -> quality.Assessment:
    return quality.assess(x, p_good=s.p_good(x), today=today, **kw)


def _top(s: Scorer, xs: list[Experience], today: date, extra: dict[str, list[str]] | None = None,
         **kw) -> list[Suggestion]:
    scored = quality.rank([(x, _assess(s, x, today, **kw)) for x in xs])
    out = []
    for x, a in scored[:LIMIT]:
        why = [w for w in [_why_taste(s, x), *(extra or {}).get(x.id, [])] if w]
        if a.practicality.level == "good" and (kw.get("minutes_free") is not None or kw.get("day") is not None):
            why.append(a.practicality.reason)
        out.append(Suggestion(x.id, x.title, tuple(why[:LIMIT]), a))
    return out


def destinations(s: Scorer, profiles: list[Profile], days: int, stops_a_day: int, today: date) -> list[Suggestion]:
    """Where to go: each ready destination by how well its best moments for this person fit, over the days asked
    (the mean chance of "Good" or better across its best days × stops). A destination that isn't ready is never
    suggested; it's listed as not ready, with what's missing."""
    out, not_ready = [], []
    need = max(1, days * stops_a_day)
    for prof in profiles:
        r = prof.readiness()
        poor = [x for x in prof.experiences if quality.trust(x, today).level == "poor"]
        if not r["ready"] or len(poor) * 2 > len(prof.experiences):
            why = (f"Not ready to recommend yet: {', '.join(r['missing'])}." if not r["ready"] and r["missing"] else
                   f"Not ready to recommend yet: {len(poor)} of its {len(prof.experiences)} moments aren't verified.")
            not_ready.append(Suggestion(prof.dest.key, prof.dest.name, (why,), None))
            continue
        ps = sorted((s.p_good(x) for x in prof.experiences), reverse=True)[:need]
        fit = sum(ps) / len(ps) if ps else 0.0
        strong = sum(1 for p in ps if p >= quality.STRONG)
        cats: dict[str, int] = {}
        for x in sorted(prof.experiences, key=s.p_good, reverse=True)[:need]:
            cats[x.category] = cats.get(x.category, 0) + 1
        mix = ", ".join(f"{n} {c.replace('_', ' ')}" for c, n in sorted(cats.items(), key=lambda kv: -kv[1])[:3])
        out.append((fit, Suggestion(prof.dest.key, prof.dest.name,
                                    (f"{strong} strong matches among its best {len(ps)} moments for you.",
                                     f"Its best for you: {mix}."), None)))
    out.sort(key=lambda t: -t[0])
    return [sg for _, sg in out[:LIMIT]] + not_ready


def neighbourhoods(s: Scorer, prof: Profile, today: date) -> list[Suggestion]:
    """Which areas to spend time in: by the mean chance of "Good" or better of their moments (two at least). Only
    moments whose own record names the area count."""
    by_area: dict[str, list[Experience]] = {}
    names = {a.name: a.key for a in prof.areas}
    for x in prof.experiences:   # only areas a source names: never the nearest centre (it can be across a river)
        key = names.get(x.geo.area.value) if x.geo.area.known else None
        if key:
            by_area.setdefault(key, []).append(x)
    ranked = []
    for a in prof.areas:
        xs = by_area.get(a.key, [])
        if len(xs) < 2:
            continue
        ps = [s.p_good(x) for x in xs]
        best = max(xs, key=s.p_good)
        ranked.append((sum(ps) / len(ps), Suggestion(a.key, a.name, (
            f"{len(xs)} moments here; the best for you is {best.title}.",
            *([_why_taste(s, best)] if _why_taste(s, best) else [])), None)))
    ranked.sort(key=lambda t: -t[0])
    return [sg for _, sg in ranked[:LIMIT]]


def load_popularity(path: Path = DATA_DIR / "popularity.yaml") -> dict[str, float]:
    return dict(yaml.safe_load(path.read_text(encoding="utf-8")).get("shares") or {})


def hidden_local(s: Scorer, prof: Profile, today: date, shares: dict[str, float] | None = None,
                 max_share: float = 0.05) -> list[Suggestion]:
    """Local, new-to-you moments that seldom appear in other people's plans (share ≤ 5%, GUESS) and fit this person
    at least as "a good match"."""
    shares = load_popularity() if shares is None else shares
    xs, extra = [], {}
    for x in prof.experiences:
        share = max((shares.get(i, 0.0) for i in x.legacy_ids), default=0.0)
        if x.features.get("local_novel", 0) >= 2 and share <= max_share and s.p_good(x) >= quality.GOOD:
            xs.append(x)
            extra[x.id] = ["Local, and in none of the simulated plans other people got." if share == 0 else
                           f"Local, and in only {round(share * 100)}% of the simulated plans other people got."]
    return _top(s, xs, today, extra)


def seasonal(s: Scorer, prof: Profile, month: int, today: date) -> list[Suggestion]:
    """The destination's dated season notes for the month, and the moments a note names. With no checked notes,
    nothing is suggested as seasonal (London today): it's said, not guessed from the weather."""
    notes = prof.seasons_in(month)
    if not notes:
        return []
    xs, extra = [], {}
    for x in prof.experiences:
        named = [n for n in notes if x.id in n.experiences]
        if named:
            xs.append(x)
            extra[x.id] = [f"{named[0].note} ({named[0].source})."]
    return _top(s, xs, today, extra)


def food(s: Scorer, prof: Profile, today: date) -> list[Suggestion]:
    """Food experiences for someone whose answers favour food: markets, food streets, a meal worth the trip. It's
    about interest in food, never a diet or a belief."""
    xs = [x for x in prof.experiences if x.category == "food_drink" or x.features.get("food", 0) >= 2]
    return _top(s, xs, today)


def fits(s: Scorer, prof: Profile, minutes: float, budget: float, today: date, day: date | None = None,
         currency: str | None = None) -> list[Suggestion]:
    """What fits the time and money they have: practical and affordable first (quality.rank), then the best match."""
    return _top(s, list(prof.experiences), today, minutes_free=minutes, budget_left=budget, day=day,
                currency=currency or prof.dest.currency)
