"""Places, the experiences inside them, and the claims behind every judgement (batch 9, m364).

The reusable structure for any city (`decisions/place-knowledge-model.md`). Every London record and every future
record is held to the same checks, so the standard lives here as code, not in a review:
- the vocabulary and the 0-2 rubric, with primary and secondary appeals (`decisions/place-vocabulary.md`);
- the evidence rules: verified, researched, inferred and unknown; facts and interpretations; expiry; and
  missing is never negative (`decisions/evidence-rules.md`).

Nothing here changes a plan. The planner still reads the moment cards. `legacy_tags` works out the cards' 15 tags
from a place's experiences so the two can be compared (`scripts/place_knowledge_report.py`); the planner keeps
the cards' own tags until Abram approves the switch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import yaml

# ---- the vocabulary (place-vocabulary.md) -------------------------------------------------------------------------

INTERESTS = (
    "history", "culture", "art", "architecture", "science", "nature", "views", "food_discovery", "dining",
    "shopping", "nightlife", "learning", "play", "adventure", "social",
)

ATMOSPHERE = {
    "energy": ("peaceful", "quiet", "lively"),
    "sensory": ("crowded", "noisy"),
    "social_character": ("intimate", "romantic", "family_friendly"),
    "visual": ("grand", "unusual"),
    "intellectual": ("thought_provoking", "immersive"),
    "cultural": ("traditional", "contemporary", "historic"),
    "environment": ("outdoors", "sheltered", "green", "urban"),
    "adventure": ("challenging", "playful"),
}
ATMOSPHERE_TERMS = tuple(t for terms in ATMOSPHERE.values() for t in terms)

# Terms no source can verify (place-vocabulary.md §2): a claim for them is inferred at most.
INFERRED_ONLY = frozenset({"romantic", "thought_provoking", "intimate", "noisy"})
# Interpretations (evidence-rules.md §3): researched at most, never verified, whatever the source says.
INTERPRETIVE = frozenset({"peaceful", "grand", "unusual", "immersive", "lively"}) | INFERRED_ONLY

ACTIVITIES = ("look", "walk", "eat", "ride", "learn", "play", "shop", "rest", "climb", "swim")

# ---- the evidence rules (evidence-rules.md) -----------------------------------------------------------------------

STATUSES = ("verified", "researched", "inferred", "unknown")
RANK = {"verified": 3, "researched": 2, "inferred": 1, "unknown": 0}
KINDS = ("fact", "interpretation")
SOURCE_TYPES = (
    "official",      # the place's own site or the body that runs it
    "reference",     # another identifiable reference: a listing body, an encyclopedia, a museum map
    "map_data",      # Overture, OSM coordinates and names
    "crowd_label",   # an open-data category or tag: inferred at best (§3)
    "founder",       # Abram's own visit: first-hand, but one person's account
    "odys",          # ODYS's own reading or estimate
)
CONFIDENCE = ("high", "medium", "low")
FACT_TYPES = ("hours", "closure", "price", "access", "booking", "age", "contents", "history", "location",
              "crowding", "interpretation")
HARD_TYPES = frozenset({"hours", "closure", "access", "age"})   # may drive a hard rule, when verified

# How long each kind of evidence holds (evidence-rules.md §4), in days.
EXPIRY_DAYS = {"hours": 90, "closure": 90, "price": 180, "access": 365, "booking": 180, "age": 180,
               "contents": 365, "history": 3650, "location": 3650, "crowding": 365, "interpretation": 365}

# The cards' 15 tags, worked out from the vocabulary. A tag with no source term isn't derived: the planner keeps
# the card's value, and the report says which tags the vocabulary can't yet speak for.
LEGACY_FROM = {
    "movement_views": ("views",),
    "food": ("food_discovery", "dining"),
    "green_nature": ("nature", "green"),
    "history_culture": ("history", "culture"),
    "crowds": ("crowded",),
    "outdoor_exposure": ("outdoors",),
    "active": ("adventure", "challenging"),
    "social_pull": ("social",),
}
NOT_DERIVED = ("iconic", "local_novel", "walking_effort", "photo_potential", "contrast_reveal", "absorption",
               "awe")
WALKING_FROM_EFFORT = True   # walking_effort comes from the experience's own `effort`, where recorded

UNKNOWN = "unknown"


@dataclass(frozen=True)
class Claim:
    id: str
    claim: str
    kind: str
    fact_type: str
    status: str
    source: str | None
    source_type: str
    checked: date | None
    confidence: str
    quote: str | None = None
    central: bool = False         # the source is about this, not merely mentions it (the primary-appeal test)
    note: str | None = None
    expires: date | None = None

    def expiry(self) -> date | None:
        if self.expires:
            return self.expires
        if self.checked is None:
            return None
        return self.checked + timedelta(days=EXPIRY_DAYS.get(self.fact_type, 365))

    def current_confidence(self, today: date) -> str:
        """An expired fact drops to medium (or stays low) until it's checked again: never silently verified."""
        exp = self.expiry()
        if exp is not None and today > exp:
            return "low" if self.confidence == "low" else "medium"
        return self.confidence

    def is_current(self, today: date) -> bool:
        exp = self.expiry()
        return exp is None or today <= exp


@dataclass(frozen=True)
class Score:
    value: int | str              # 0, 1, 2 or "unknown"
    claims: tuple[str, ...] = ()
    window: str | None = None     # a time window or season the value holds for, where the evidence gives one


@dataclass(frozen=True)
class Experience:
    id: str
    title: str
    what_you_do: str
    activity: str
    status: str                   # ready | draft (a draft never reaches the engine)
    scores: dict[str, Score]
    atmosphere: dict[str, tuple[Score, ...]]
    primary: tuple[str, ...]
    secondary: tuple[str, ...]
    claims: tuple[Claim, ...]
    effort: Score | None = None   # 0 easy, 1 some walking, 2 demanding
    duration_min: tuple[int, int] | None = None
    duration_status: str = UNKNOWN
    cautions: tuple[str, ...] = ()   # claim ids for what may not suit someone
    needs: tuple[str, ...] = ()      # what's still unknown, said plainly

    def score(self, dim: str) -> int | str:
        s = self.scores.get(dim)
        return s.value if s else UNKNOWN

    def atmos(self, term: str, window: str | None = None) -> int | str:
        """The term's value for a window: the window's own if recorded, else the whole-day value, else unknown."""
        vals = self.atmosphere.get(term, ())
        for s in vals:
            if window is not None and s.window == window:
                return s.value
        for s in vals:
            if s.window is None:
                return s.value
        return UNKNOWN

    def atmos_max(self, term: str) -> int | str:
        known = [s.value for s in self.atmosphere.get(term, ()) if s.value != UNKNOWN]
        return max(known) if known else UNKNOWN


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    kind: str
    area: str | None
    official_url: str | None
    lat: float | None
    lon: float | None
    facts: tuple[Claim, ...]
    experiences: tuple[Experience, ...]
    legacy_card: str | None
    legacy_from: tuple[str, ...]
    other_cards: tuple[str, ...] = ()
    notes: str | None = None
    path: str | None = None

    def claims(self) -> dict[str, Claim]:
        out = {c.id: c for c in self.facts}
        for e in self.experiences:
            out.update({c.id: c for c in e.claims})
        return out

    def experience(self, eid: str) -> Experience:
        return next(e for e in self.experiences if e.id == eid)

    def ready(self) -> tuple[Experience, ...]:
        return tuple(e for e in self.experiences if e.status == "ready")


# ---- loading ------------------------------------------------------------------------------------------------------

def _date(v) -> date | None:
    if v is None or isinstance(v, date):
        return v
    return date.fromisoformat(str(v))


def _claim(d: dict) -> Claim:
    return Claim(
        id=str(d["id"]), claim=str(d["claim"]), kind=d.get("kind", "fact"), fact_type=d.get("fact_type", "contents"),
        status=d.get("status", UNKNOWN), source=d.get("source"), source_type=d.get("source_type", "official"),
        checked=_date(d.get("checked")), confidence=d.get("confidence", "low"), quote=d.get("quote"),
        central=bool(d.get("central", False)), note=d.get("note"), expires=_date(d.get("expires")))


def _score(v) -> Score:
    if isinstance(v, dict):
        return Score(value=v.get("value", UNKNOWN), claims=tuple(v.get("claims", ())), window=v.get("window"))
    return Score(value=v)


def _experience(d: dict) -> Experience:
    atm: dict[str, tuple[Score, ...]] = {}
    for term, v in (d.get("atmosphere") or {}).items():
        vals = v if isinstance(v, list) else [v]
        atm[term] = tuple(_score(x) for x in vals)
    dur = d.get("duration_min")
    return Experience(
        id=str(d["id"]), title=str(d["title"]), what_you_do=str(d.get("what_you_do", "")),
        activity=d.get("activity", "look"), status=d.get("status", "draft"),
        scores={k: _score(v) for k, v in (d.get("scores") or {}).items()}, atmosphere=atm,
        primary=tuple(d.get("primary") or ()), secondary=tuple(d.get("secondary") or ()),
        claims=tuple(_claim(c) for c in d.get("claims") or ()),
        effort=_score(d["effort"]) if d.get("effort") is not None else None,
        duration_min=tuple(dur) if dur else None, duration_status=d.get("duration_status", UNKNOWN),
        cautions=tuple(d.get("cautions") or ()), needs=tuple(d.get("needs") or ()))


def parse_place(d: dict, path: str | None = None) -> Place:
    loc = d.get("location") or {}
    leg = d.get("legacy") or {}
    return Place(
        id=str(d["id"]), name=str(d["name"]), kind=str(d.get("kind", "")), area=d.get("area"),
        official_url=d.get("official_url"), lat=loc.get("lat"), lon=loc.get("lon"),
        facts=tuple(_claim(c) for c in d.get("facts") or ()),
        experiences=tuple(_experience(e) for e in d.get("experiences") or ()),
        legacy_card=leg.get("card"), legacy_from=tuple(leg.get("from") or ()),
        other_cards=tuple(leg.get("other_cards") or ()), notes=d.get("notes"), path=path)


def load_places(directory: str | Path) -> list[Place]:
    out = []
    for p in sorted(Path(directory).glob("*.yaml")):
        out.append(parse_place(yaml.safe_load(p.read_text()), str(p)))
    return out


# ---- the checks (the standard, as code) ---------------------------------------------------------------------------

def _claim_problems(c: Claim, where: str) -> list[str]:
    bad = []
    if c.kind not in KINDS:
        bad.append(f"{where}: claim {c.id} kind {c.kind!r}")
    if c.status not in STATUSES:
        bad.append(f"{where}: claim {c.id} status {c.status!r}")
    if c.source_type not in SOURCE_TYPES:
        bad.append(f"{where}: claim {c.id} source_type {c.source_type!r}")
    if c.confidence not in CONFIDENCE:
        bad.append(f"{where}: claim {c.id} confidence {c.confidence!r}")
    if c.fact_type not in FACT_TYPES:
        bad.append(f"{where}: claim {c.id} fact_type {c.fact_type!r}")
    if c.status in ("verified", "researched") and not c.source:
        bad.append(f"{where}: claim {c.id} is {c.status} with no source")
    if c.status in ("verified", "researched") and c.checked is None:
        bad.append(f"{where}: claim {c.id} is {c.status} with no date checked")
    # Facts and interpretations (evidence-rules.md §3): an interpretation is never verified.
    if c.kind == "interpretation" and c.status == "verified":
        bad.append(f"{where}: claim {c.id} is an interpretation marked verified")
    # A crowd label is inferred at best; ODYS's own estimate too.
    if c.source_type in ("crowd_label", "odys") and RANK.get(c.status, 0) > RANK["inferred"]:
        bad.append(f"{where}: claim {c.id} from {c.source_type} is above inferred")
    # A founder's account is first-hand, but one person's: researched at most.
    if c.source_type == "founder" and c.status == "verified":
        bad.append(f"{where}: claim {c.id} from the founder's visit marked verified")
    # Confidence follows status (evidence-rules.md §2).
    if c.status in ("inferred", "unknown") and c.confidence != "low":
        bad.append(f"{where}: claim {c.id} is {c.status} but confidence {c.confidence}")
    if c.status == "researched" and c.confidence == "high":
        bad.append(f"{where}: claim {c.id} is researched but confidence high")
    return bad


def cap(term: str) -> str:
    """The highest status a term can carry, whatever its sources (evidence-rules.md §3).

    An interpretation built on a verified fact is researched: a 25-metre skeleton is verified, "grand" is ODYS's
    reading of it. Terms no source can establish (romantic, intimate...) stay inferred.
    """
    if term in INFERRED_ONLY:
        return "inferred"
    if term in INTERPRETIVE:
        return "researched"
    return "verified"


def _best_status(score: Score, claims: dict[str, Claim], term: str | None = None) -> str:
    ranks = [RANK.get(claims[c].status, 0) for c in score.claims if c in claims]
    if not ranks:
        return UNKNOWN
    best = min(max(ranks), RANK[cap(term)] if term else RANK["verified"])
    return next(s for s, r in RANK.items() if r == best)


def _score_problems(name: str, s: Score, claims: dict[str, Claim], where: str, *, term: bool) -> list[str]:
    bad = []
    if s.value not in (0, 1, 2, UNKNOWN):
        bad.append(f"{where}: {name} = {s.value!r} (0, 1, 2 or unknown)")
        return bad
    missing = [c for c in s.claims if c not in claims]
    if missing:
        bad.append(f"{where}: {name} cites unknown claims {missing}")
    if s.value == UNKNOWN:
        return bad
    # Every 0, 1 or 2 rests on a source that was read (place-vocabulary.md §3: 0 isn't unknown).
    if not s.claims:
        bad.append(f"{where}: {name} = {s.value} cites no claim")
        return bad
    best = _best_status(s, claims, name if term else None)
    if s.value == 2 and RANK[best] < RANK["researched"]:
        # Includes the inferred-only terms: they can never be a 2 (place-vocabulary.md §2).
        bad.append(f"{where}: {name} = 2 rests only on {best} evidence (a 2 needs verified or researched)")
    return bad


def problems(place: Place, *, card_ids: set[str] | None = None) -> list[str]:
    """Everything that breaks the standard. An empty list means the record passes."""
    bad: list[str] = []
    where = place.id
    for c in place.facts:
        bad += _claim_problems(c, where)
    claims = place.claims()
    ids = [c.id for c in place.facts] + [c.id for e in place.experiences for c in e.claims]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        bad.append(f"{where}: duplicate claim ids {sorted(dupes)}")
    eids = [e.id for e in place.experiences]
    if len(set(eids)) != len(eids):
        bad.append(f"{where}: duplicate experience ids")
    if not place.experiences:
        bad.append(f"{where}: no experiences")
    for lf in place.legacy_from:
        if lf not in eids:
            bad.append(f"{where}: legacy.from names {lf}, which isn't an experience")
    if card_ids is not None:
        for card in (place.legacy_card, *place.other_cards):
            if card and card not in card_ids:
                bad.append(f"{where}: legacy card {card} doesn't exist")
    for e in place.experiences:
        w = f"{where}/{e.id}"
        for c in e.claims:
            bad += _claim_problems(c, w)
        if e.activity not in ACTIVITIES:
            bad.append(f"{w}: activity {e.activity!r}")
        if e.status not in ("ready", "draft"):
            bad.append(f"{w}: status {e.status!r}")
        for dim, s in e.scores.items():
            if dim not in INTERESTS:
                bad.append(f"{w}: {dim} isn't in the vocabulary")
                continue
            bad += _score_problems(dim, s, claims, w, term=False)
        for term, vals in e.atmosphere.items():
            if term not in ATMOSPHERE_TERMS:
                bad.append(f"{w}: atmosphere {term} isn't in the vocabulary")
                continue
            for s in vals:
                bad += _score_problems(term, s, claims, w, term=True)
        if e.effort is not None:
            bad += _score_problems("effort", e.effort, claims, w, term=False)
        # Primary appeals (place-vocabulary.md §3): at most two, each a 2, each organised around, never inferred.
        if len(e.primary) > 2:
            bad.append(f"{w}: {len(e.primary)} primary appeals (at most 2)")
        if e.status == "ready" and not e.primary:
            bad.append(f"{w}: a ready experience with no primary appeal")
        for dim in e.primary:
            s = e.scores.get(dim)
            if s is None or s.value != 2:
                bad.append(f"{w}: primary {dim} doesn't score 2")
                continue
            central = [claims[c] for c in s.claims if c in claims and claims[c].central]
            if not central:
                bad.append(f"{w}: primary {dim} has no claim the experience is organised around it")
            elif max(RANK[c.status] for c in central) < RANK["researched"]:
                bad.append(f"{w}: primary {dim} rests on inferred evidence alone")
        for dim in e.secondary:
            if dim in e.primary:
                bad.append(f"{w}: {dim} is both primary and secondary")
            s = e.scores.get(dim)
            if s is None or s.value not in (1, 2):
                bad.append(f"{w}: secondary {dim} doesn't score 1 or 2")
        for cid in e.cautions:
            if cid not in claims:
                bad.append(f"{w}: caution cites unknown claim {cid}")
    return bad


# ---- what the engine and the report read --------------------------------------------------------------------------

@dataclass(frozen=True)
class Appeal:
    dimension: str
    value: int | str
    role: str                     # primary | secondary | other
    status: str                   # the best evidence behind it
    claims: tuple[str, ...]


def appeals(place: Place, exp: Experience) -> dict[str, Appeal]:
    """Each scored dimension with its role and the best evidence behind it (unknowns are left out: missing)."""
    claims = place.claims()
    out = {}
    for dim, s in exp.scores.items():
        if s.value == UNKNOWN:
            continue
        role = "primary" if dim in exp.primary else "secondary" if dim in exp.secondary else "other"
        out[dim] = Appeal(dim, s.value, role, _best_status(s, claims), s.claims)
    return out


def atmosphere(place: Place, exp: Experience, window: str | None = None) -> dict[str, Appeal]:
    """Each recorded atmosphere term for a window, with its status capped as an interpretation where it is one."""
    claims = place.claims()
    out = {}
    for term, vals in exp.atmosphere.items():
        chosen = next((s for s in vals if window is not None and s.window == window), None)
        chosen = chosen or next((s for s in vals if s.window is None), None)
        if chosen is None or chosen.value == UNKNOWN:
            continue
        out[term] = Appeal(term, chosen.value, "atmosphere", _best_status(chosen, claims, term), chosen.claims)
    return out


def hard_facts(place: Place, today: date) -> dict[str, list[Claim]]:
    """The facts a hard rule may use: verified, current and of a hard type. Everything else is said, not applied."""
    out: dict[str, list[Claim]] = {}
    for c in place.facts:
        if c.fact_type in HARD_TYPES and c.status == "verified" and c.is_current(today):
            out.setdefault(c.fact_type, []).append(c)
    return out


def unverified_hard(place: Place, today: date) -> list[Claim]:
    """Hard-type facts that can't drive a rule: researched, inferred, unknown or expired. The engine says them."""
    return [c for c in place.facts
            if c.fact_type in HARD_TYPES and not (c.status == "verified" and c.is_current(today))]


def _num(v) -> int:
    return v if isinstance(v, int) else 0


def legacy_tags(place: Place) -> dict[str, int | None]:
    """The cards' tags worked out from the experiences the card covers. Unknown reads as 0 *for the planner only*.

    None means the vocabulary can't speak for that tag yet; the planner keeps the card's value.
    """
    exps = [place.experience(e) for e in place.legacy_from] or list(place.ready()[:1])
    out: dict[str, int | None] = {}
    for tag, sources in LEGACY_FROM.items():
        best = 0
        for e in exps:
            for s in sources:
                v = e.score(s) if s in INTERESTS else e.atmos_max(s)
                best = max(best, _num(v))
        out[tag] = best
    efforts = [e.effort.value for e in exps if e.effort is not None and e.effort.value != UNKNOWN]
    out["walking_effort"] = max(efforts) if efforts else None
    for tag in NOT_DERIVED:
        if tag != "walking_effort":
            out[tag] = None
    return out


def unknown_share(exp: Experience) -> float:
    """The share of interest dimensions with no assessment yet: how much ODYS doesn't know about this experience."""
    known = sum(1 for d in INTERESTS if exp.score(d) != UNKNOWN)
    return 1.0 - known / len(INTERESTS)
