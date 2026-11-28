"""The central person-to-place engine, **in shadow mode** (m363, revised in batch 9, m364). One answer to "is this
place right for this traveller on this day, and why?". It changes no plan: nothing in the planner calls it.

**Six classes** (Abram, m363), the first that applies:
1. ``not_suitable``: a hard rule (closed, an age rule, a gentle pace, dry weather only, the budget, not a ready card)
   or a **current explicit exclusion** ("not this place this trip", "no museums").
2. ``must_go``: they asked for it. Intent, not predicted enjoyment; never over a hard rule.
3. ``strong_match``: they loved or rated it highly, or clear evidence on both sides of an appeal the place is
   organised around (a primary appeal from a place record), a score at or above STRONG, and no conflict.
4. ``poor_match`` (decisive): they didn't enjoy it, or rated it low; or a clear lean away from what it's about.
5. ``low_confidence``: not enough evidence to judge: what the place offers isn't known about this traveller,
   the evidence conflicts, or the score rests on the population.
6. ``good_discovery`` at or above the planner's floor, else ``poor_match``.

**Batch 9 (Abram, m364):**
- **The most recent, specific instruction wins** over an older preference, subject to hard rules. A current request
  beats an older dislike ("Included because you specifically asked to visit."); a current "not this place" beats an
  older request. Every instruction carries its source and time, and the result says which won and over what.
- **No category bans from one dislike.** Three levels:
  - a place they didn't enjoy: a strong negative for that place, never a ban;
  - a similar experience: a smaller negative, by how similar;
  - an explicit category dislike: respected until they change it.
  The planner's own kind rule (`dayplan.kept_out`) still bans the kind in real plans: shadow mode reports the
  difference, and doesn't change the planner.
- **Context:** a negative said in one context (a weekend, with company) counts in full only in that context.
- **Missing evidence is never negative.** What the place is about but ODYS doesn't know about the traveller lowers
  confidence, never suitability (`decisions/evidence-rules.md` §5).
- **Confidence is its own axis** (`confidence`): the answers, how far they narrowed the posterior's predictive
  spread for this place, whether they touch the place's primary appeals, how complete the place's own evidence
  is, conflicts, and how much rests on the population. It is a level (low, medium, high) with its parts, never a
  calibrated probability: nothing yet can calibrate one.
- **Places hold experiences.** Where a place has a record (`brain/data/places/`), each experience is judged on its
  own appeals, with each appeal's evidence status. A strong reason needs a verified or researched appeal; a card's
  hand-set tags are inferred, so a place known only by its card is never a strong match unless they loved it.

**The score is a provisional ranking measure, never a chance:** the person's utility x·(b_population + δ_person),
from the card's features as the planner ranks, minus the dislike adjustments above. FLOOR is the planner's own.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

from .aspiration import AspirationMap
from .experiences import RANK, Place
from .experiences import appeals as record_appeals
from .experiences import atmosphere as record_atmosphere
from .experiences import closed_by_record, hard_facts, unverified_hard
from .features import Conditions, moment_features
from .moments import Moment
from .population import PopulationModel
from .reasons import FEELINGS, LINK_MIN, MIN_WEIGHT, PHRASE
from .scoring import contributions

CLASSES = ("not_suitable", "must_go", "low_confidence", "strong_match", "good_discovery", "poor_match")
FLOOR = -0.75        # the planner's floor (the rating model's 2|3 cut, `priors.yaml`): its own rule, unchanged
STRONG = 0.35        # GUESS: a score cut-off, not a chance
QUIET_MAX = 0        # a place is "quiet" on its card only at crowds 0
SIGN_CLEAR = 0.8     # GUESS: a lean is "your answers" only when the posterior puts this much on its sign
DISLIKE_PLACE = 1.5  # GUESS: the strong negative for a place they didn't enjoy (utility units)
DISLIKE_SIMILAR = 0.6   # GUESS: the most a similar place loses, scaled by how similar
LOW_RATING = 2       # a rating at or below this is a dislike of that place
CONTEXT_OTHER = 0.5  # a negative said in another context counts half
RATIO_LEARNED = 0.85  # their answers narrowed the predictive spread to under this share of the prior's
RATIO_LITTLE = 0.93   # over this share, their answers barely touch this place. Both set from the first hidden-bench
                      # run (travellers 0-3, where the score's error rose past ~0.93) and checked on fresh travellers
                      # (4-7) the thresholds never saw: `validation/engine-bench/hidden-*.md`. GUESSES until real
                      # ratings can check them.
TAG_NAMES = ("movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel", "crowds",
             "walking_effort", "active", "outdoor_exposure", "photo_potential", "contrast_reveal", "absorption",
             "awe", "social_pull")
KIND_RULE = "kinds they didn't enjoy"   # dayplan.kept_out's kind ban: here a similarity penalty, not a restriction

# The vocabulary's dimensions mapped onto the person model's features (place-vocabulary.md §4). Dimensions with no
# feature (art, architecture, science, play, shopping...) are learned only from places they loved or disliked.
DIM_FEATURE = {"history": "history_culture", "culture": "history_culture", "food_discovery": "food",
               "dining": "food", "nature": "green_nature", "views": "movement_views", "social": "social_pull",
               "adventure": "active"}
FIELD_DIMS = {"history_culture": ("history", "culture"), "food": ("food_discovery", "dining"),
              "nature": ("nature",)}   # finance_tech has no place dimension yet: it influences nothing here
FIELD_LABEL = {"history_culture": "history and culture", "food": "food", "nature": "nature"}
DIM_PHRASE = {"history": "history", "culture": "culture", "art": "art", "architecture": "architecture",
              "science": "science and natural history", "nature": "nature", "views": "views",
              "food_discovery": "trying food", "dining": "a good meal", "shopping": "shopping",
              "nightlife": "nightlife", "learning": "learning", "play": "play", "adventure": "adventure",
              "social": "time with others"}
INSTRUCTION_KINDS = ("must_go", "avoid", "dislike_place", "love_place", "fine_place", "rated", "dislike_kind")
SPECIFIC = {"must_go": 2, "avoid": 2, "dislike_place": 2, "love_place": 2, "fine_place": 2, "rated": 2,
            "dislike_kind": 1}
EPOCH = datetime(2000, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class Instruction:
    """Something the traveller said or did about a place or a kind of place, with when and where it came from."""
    kind: str                         # one of INSTRUCTION_KINDS
    target: str                       # a card id, or a catalogue kind for dislike_kind
    at: datetime = EPOCH              # when: the newest wins (Abram, m364)
    source: str = ""                  # "swipe", "rating", "request", "settings"
    label: str = ""                   # the place or kind in plain words
    value: int | None = None          # a rating's 1-5
    context: tuple[tuple[str, str], ...] = ()   # e.g. (("window", "weekend"),): where a negative was said


@dataclass(frozen=True)
class Traveller:
    """Everything the engine knows about one traveller, from their own answers. Nothing here is inferred about who
    they are: no age, nationality or health, only what they told or showed ODYS (CLAUDE.md guardrails)."""
    delta: np.ndarray                     # δ_person, posterior mean, over the personal features
    delta_sd: np.ndarray                  # its posterior spread
    loved: dict[str, str] = field(default_factory=dict)      # card id → the swipe place they loved
    disliked: dict[str, str] = field(default_factory=dict)   # card id → the swipe place they didn't enjoy
    loved_tags: tuple[tuple[str, dict], ...] = ()            # (a swipe place they loved, its tags), for links
    kept_out: dict[str, str] = field(default_factory=dict)   # card id → the planner's own exclusion rule (kept_out)
    must_go: tuple[str, ...] = ()         # card ids they asked for (now)
    rated: dict[str, int] = field(default_factory=dict)      # card id → their 1-5 rating
    fields: frozenset[str] = frozenset()  # interests (aspiration codes)
    feelings: tuple[str, ...] = ()        # how they want to feel
    activity: str | None = None
    budget_gbp: float | None = None       # a day, per person
    children: tuple[int, ...] = ()
    n_answers: int = 0                    # swipes, choices and ratings that carry information
    n_choices: int = 0                    # "this or that" days answered (A or B)
    instructions: tuple[Instruction, ...] = ()   # batch 9: with times; built from the fields above when empty
    delta_cov: np.ndarray | None = None   # the posterior covariance, for the predictive spread
    company: str | None = None


@dataclass(frozen=True)
class Day:
    weekday: str | None = None            # "mon".."sun"
    date: str | None = None               # ISO date
    temp_c: float | None = None
    rain_prob: float | None = None
    window: str | None = None             # e.g. "saturday_afternoon", where a time of day is known

    def context(self) -> dict[str, str]:
        out = {}
        if self.weekday:
            out["window"] = "weekend" if self.weekday in ("sat", "sun") else "weekday"
        return out


@dataclass(frozen=True)
class Knowledge:
    """What the engine knows about places beyond the cards: the records, and the planner's kinds."""
    records: dict[str, tuple[Place, tuple[str, ...]]] = field(default_factory=dict)  # card → (place, experiences)
    kinds: dict[str, str] = field(default_factory=dict)                               # card → catalogue kind
    today: str | None = None                                                          # ISO date facts are judged on

    @staticmethod
    def build(places: list[Place], kinds: dict[str, str] | None = None, today: str | None = None) -> "Knowledge":
        rec = {}
        for p in places:
            if p.legacy_card:
                rec[p.legacy_card] = (p, p.legacy_from or tuple(e.id for e in p.ready()[:1]))
        return Knowledge(records=rec, kinds=dict(kinds or {}), today=today)


@dataclass
class Match:
    place: str
    title: str
    cls: str                              # one of CLASSES
    score: float                          # provisional ranking measure (utility units), never a chance
    restrictions: list[str] = field(default_factory=list)     # why it's not suitable (empty otherwise)
    positives: list[dict] = field(default_factory=list)       # strongest terms raising the score
    negatives: list[dict] = field(default_factory=list)       # strongest terms lowering it
    evidence: list[dict] = field(default_factory=list)        # what the reason rests on, both sides
    reason: str | None = None                                 # one sentence, only with evidence on both sides
    against: str | None = None                                # why it may not suit them, with evidence
    missing: list[str] = field(default_factory=list)          # facts not known (place or traveller)
    confidence: dict = field(default_factory=dict)            # level, with its parts
    basis: str = ""                                           # what the class rests on
    preferences: list[dict] = field(default_factory=list)     # the instructions that applied, newest first
    experiences: list[dict] = field(default_factory=list)     # each experience's fit, where a record exists
    warnings: list[str] = field(default_factory=list)         # facts that can't drive a rule, said instead
    model_score: float = 0.0                                  # the score before the dislike adjustments
    misfit: bool = False                                      # loved, but the model scores it below the floor

    def out(self) -> dict:
        return {"place": self.place, "title": self.title, "class": self.cls, "score": round(self.score, 3),
                "model_score": round(self.model_score, 3), "restrictions": self.restrictions,
                "positives": self.positives, "negatives": self.negatives, "evidence": self.evidence,
                "reason": self.reason, "against": self.against, "missing": self.missing,
                "confidence": self.confidence, "basis": self.basis, "preferences": self.preferences,
                "experiences": self.experiences, "warnings": self.warnings, "misfit": self.misfit}


def _tag(m: Moment, name: str) -> int:
    return int(m.tag(name) or 0)


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def lean(pop: PopulationModel, t: Traveller, feature: str) -> tuple[int, float]:
    """The sign of their answers' lean on a feature (+1, -1 or 0) and the posterior's weight on that sign.

    Clear only when δ moved by more than MIN_WEIGHT **and** the posterior puts SIGN_CLEAR on its sign: the batch 8
    review's fix ("loosened because the data didn't meet it"); `delta_sd` is now read.
    """
    names = pop.personal_names
    if feature not in names:
        return 0, 0.5
    i = names.index(feature)
    d, sd = float(t.delta[i]), float(t.delta_sd[i]) if len(t.delta_sd) > i else 1.0
    p_pos = _phi(d / sd) if sd > 0 else (1.0 if d > 0 else 0.0)
    if d > MIN_WEIGHT and p_pos >= SIGN_CLEAR:
        return 1, p_pos
    if d < -MIN_WEIGHT and (1 - p_pos) >= SIGN_CLEAR:
        return -1, 1 - p_pos
    return 0, max(p_pos, 1 - p_pos)


def _person_side(pop: PopulationModel, t: Traveller, feature: str) -> tuple[str, str]:
    sign, _ = lean(pop, t, feature)
    return ("theirs", "your answers") if sign else ("population", "most people")


def instructions(t: Traveller) -> tuple[Instruction, ...]:
    """The traveller's instructions, with times. Built from the plain fields when none are given (tests, the bench's
    older calls): swipes first, then ratings, then today's requests."""
    if t.instructions:
        return t.instructions
    out = [Instruction("love_place", c, EPOCH, "swipe", n) for c, n in t.loved.items()]
    out += [Instruction("dislike_place", c, EPOCH, "swipe", n) for c, n in t.disliked.items()]
    later = datetime(2001, 1, 1, tzinfo=timezone.utc)
    out += [Instruction("rated", c, later, "rating", c, v) for c, v in t.rated.items()]
    now = datetime.now(timezone.utc)
    out += [Instruction("must_go", c, now, "request", c) for c in t.must_go]
    return tuple(out)


def _applies(i: Instruction, m: Moment, kind: str | None) -> bool:
    if i.kind == "dislike_kind":
        return kind is not None and i.target == kind
    return i.target == m.id


REQUESTS = ("must_go", "avoid", "dislike_kind")      # what they ask for: the newest decides (Abram, m364)


def recorded(t: Traveller, card: str) -> Instruction | None:
    """What they've recorded about one place, combined: their ratings (real visits) over their swipe, and the
    ratings averaged, never the newest alone (the batch 9 review: ratings 5, 5 then 2 made a poor match)."""
    rel = [i for i in instructions(t) if i.target == card and i.kind not in REQUESTS]
    rates = [i for i in rel if i.kind == "rated" and i.value is not None]
    if rates:
        mean = sum(i.value for i in rates) / len(rates)
        last = max(rates, key=lambda i: i.at)
        label = next((i.label for i in rel if i.source == "swipe"), last.label)
        return Instruction("rated", card, last.at, "rating", label, int(round(mean)), last.context)
    swipes = [i for i in rel if i.kind in ("love_place", "dislike_place", "fine_place")]
    return max(swipes, key=lambda i: i.at) if swipes else None


def evidence_by_place(t: Traveller) -> list[Instruction]:
    """Each place's recorded evidence, combined (`recorded`): what other places learn from, so an item a later one
    replaced (a love, then a rating of 1) no longer speaks for them (the batch 9 review)."""
    cards = dict.fromkeys(i.target for i in instructions(t) if i.kind not in REQUESTS)
    return [r for c in cards if (r := recorded(t, c)) is not None]


def stance(t: Traveller, m: Moment, kind: str | None) -> tuple[Instruction | None, list[Instruction]]:
    """What decides this place, and what it wins over (Abram's rule, m364, as the batch 9 review sharpened it).

    - **Requests** (a must-go, "not this place", "no museums") are instructions: the newest decides, and at the same
      time the more specific (a place over a kind), with "not this place" over a must-go when both are asked at once.
    - **A request beats what they've recorded** (swipes and ratings), however recent: it's this trip's instruction.
    - **What they've recorded** is evidence, combined (`recorded`), never "newest wins".
    Hard rules are judged elsewhere, and win over everything.
    """
    reqs = [i for i in instructions(t) if i.kind in REQUESTS and _applies(i, m, kind)]
    rec = recorded(t, m.id)
    if reqs:
        reqs.sort(key=lambda i: (i.at, SPECIFIC.get(i.kind, 0), i.kind == "avoid"))
        win = reqs[-1]
        older = list(reversed(reqs[:-1])) + ([rec] if rec else [])
        return win, older
    return (rec, []) if rec else (None, [])


def _negative_stance(i: Instruction | None) -> bool:
    return i is not None and (i.kind == "dislike_place" or (i.kind == "rated" and (i.value or 5) <= LOW_RATING))


def _positive_stance(i: Instruction | None) -> bool:
    return i is not None and (i.kind == "love_place" or (i.kind == "rated" and (i.value or 0) >= 4))


def _context_factor(i: Instruction, day: Day) -> tuple[float, str | None]:
    """A negative said in another context counts half, and says so."""
    if not i.context:
        return 1.0, None
    here = day.context()
    for k, v in i.context:
        if here.get(k) is not None and here[k] != v:
            return CONTEXT_OTHER, f"said about a {v} visit; this is a {here[k]}"
    return 1.0, None


def missing_facts(m: Moment, t: Traveller, checked: dict | None) -> list[str]:
    """Facts that would change the judgement and aren't known. Unknown is never read as "no" (quality.py's rule)."""
    out = [f"the card's {f}" for f in m.missing_for_planning()]
    if not checked or "hours" not in checked:
        out.append("opening hours from the place's own page (the card's own hours are used)")
    if not checked or "price" not in checked:
        out.append("the price from the place's own page")
    if m.approach.step_free is None and not (checked and "step_free" in checked):
        out.append("step-free access")
    if t.children and m.cost_gbp and m.child_cost_gbp is None:
        out.append("a child's price")
    if t.n_answers == 0:
        out.append("anything about the traveller: they haven't answered yet")
    return out


def restrictions_for(m: Moment, t: Traveller, day: Day, *, know: Knowledge | None = None,
                     checked: dict | None = None) -> list[tuple[str, str]]:
    """The hard rules, apart from ranking, each with its basis: (what, basis). Basis is "verified" only when a
    verified, current fact of the place drives it (the batch 8 review: it said "verified" for the kind rule)."""
    out: list[tuple[str, str]] = []
    rec = (know.records.get(m.id) if know else None)
    today = None
    if know and know.today:
        from datetime import date as _d
        today = _d.fromisoformat(know.today)
    verified_hours = bool(rec and today and "hours" in hard_facts(rec[0], today)) or bool(checked and "hours" in checked)
    if m.status != "ready":
        out.append(("not a ready card: never planned", "card"))
    elif not m.plannable():
        out.append(("the card is missing facts the planner needs", "card"))
    shut = closed_by_record(rec[0], day.date, today) if (rec and today and day.date) else None
    if shut is not None:
        # m366: the record's verified closure (the NHM, 24-26 Dec) even where the card doesn't list the date
        out.append((f"closed on {day.date} ({shut.claim}, {shut.source_type} page checked {shut.checked})",
                    "verified"))
    elif not m.open_on(day.weekday, day.date):
        out.append((f"closed on {day.date or day.weekday}", "verified" if verified_hours else "card"))
    rule = t.kept_out.get(m.id)
    if rule and not rule.startswith(KIND_RULE):     # the kind rule is a penalty here (Abram, m364)
        out.append((f"excluded by the planner's rule: {rule}", "planner rule"))
    if day.rain_prob is not None and day.rain_prob >= 0.5 and m.best_time.weather == ["dry"]:
        out.append(("needs a dry day, and rain is likely", "card"))
    if t.budget_gbp is not None and (m.cost_gbp or 0) > t.budget_gbp:
        out.append((f"costs £{m.cost_gbp:g}, more than the day's budget of £{t.budget_gbp:g}", "card"))
    return out


# ---- the person's evidence on the vocabulary's dimensions --------------------------------------------------------

def dim_evidence(pop: PopulationModel, t: Traveller, know: Knowledge | None) -> dict[str, list[dict]]:
    """What the traveller has shown about each dimension: positive or negative, how strong, and from what.

    Strengths: "clear" (their answers' lean, with a clear sign; a place they loved that's about it), "stated" (an
    interest or a feeling they picked: moderate), "weak" (a place they didn't enjoy that's about it: one dislike is
    never a verdict on a whole dimension).
    """
    ev: dict[str, list[dict]] = {}

    def add(dim, sign, strength, src):
        ev.setdefault(dim, []).append({"sign": sign, "strength": strength, "from": src})

    for dim, f in DIM_FEATURE.items():
        s, p = lean(pop, t, f)
        if s:
            add(dim, s, "clear", f"your answers {'raised' if s > 0 else 'lowered'} '{pop.spec(f).label}'")
    for fld in t.fields:
        for dim in FIELD_DIMS.get(fld, ()):
            add(dim, 1, "stated", f"you picked {FIELD_LABEL[fld]} as an interest")
    if t.children:
        add("play", 1, "stated", "you're travelling with children")
    if know:
        for i in evidence_by_place(t):
            rec = know.records.get(i.target)
            if not rec:
                continue
            place, exps = rec
            share: dict[str, float] = {}
            for e in exps:
                for d in place.experience(e).primary:
                    share[d] = share.get(d, 0.0) + 1.0 / len(exps)
            for d, sh in share.items():
                # m366 (the hidden bench: "You loved British Museum, which is about architecture" as a reason for
                # Liberty): a loved place speaks clearly only for what most of it is about; the Great Court's
                # architecture is one part of three, so it's weak evidence, never a reason
                if _positive_stance(i):
                    add(d, 1, "clear" if sh > 0.5 else "weak",
                        f"you loved {place.name}, which is about {DIM_PHRASE.get(d, d)}" if sh > 0.5 else
                        f"you loved {place.name}, part of which is about {DIM_PHRASE.get(d, d)}")
                elif _negative_stance(i):
                    add(d, -1, "weak", f"you didn't enjoy {place.name}, which is about {DIM_PHRASE.get(d, d)}")
    return ev


def _verdict(items: list[dict]) -> tuple[int, str, list[dict]]:
    """Combine a dimension's evidence: (sign, strength, the items). Clear beats stated beats weak; opposite clear
    signs are a conflict (sign 0, "conflict")."""
    if not items:
        return 0, "missing", []
    order = {"clear": 3, "stated": 2, "weak": 1}
    best = max(order[i["strength"]] for i in items)
    top = [i for i in items if order[i["strength"]] == best]
    signs = {i["sign"] for i in top}
    if len(signs) > 1:
        return 0, "conflict", top
    return signs.pop(), next(k for k, v in order.items() if v == best), top


# ---- similarity, for the experience-level dislike -----------------------------------------------------------------

def similarity(a: str, b: str, know: Knowledge | None) -> float:
    """How alike two places are as experiences: shared primary appeals where both have records, else half for the
    same catalogue kind. A GUESS until ratings show what people treat as alike."""
    if a == b or not know:
        return 0.0
    ra, rb = know.records.get(a), know.records.get(b)
    if ra and rb:
        pa = {d for e in ra[1] for d in ra[0].experience(e).primary}
        pb = {d for e in rb[1] for d in rb[0].experience(e).primary}
        return len(pa & pb) / len(pa | pb) if pa | pb else 0.0
    ka, kb = know.kinds.get(a), know.kinds.get(b)
    return 0.5 if ka and ka == kb else 0.0


def _predictive_ratio(pop: PopulationModel, t: Traveller, x: dict[str, float]) -> float | None:
    """sqrt(xᵀΣx) / sqrt(xᵀΣ₀x) on the personal features: 1 means their answers taught nothing about this place."""
    names = pop.personal_names
    v = np.array([x.get(n, 0.0) for n in names], dtype=float)
    if not np.any(v):
        return None
    # the score's gradient in δ: x on the linear features; x·b_pop·e^δ on the log-scale ones (cost, D88). The batch
    # 9 review found the Jacobian missing, so the spread tracked the price, not what they'd said.
    bp = pop.b_pop[pop.personal_idx]
    logm = pop.log_mask
    d = np.asarray(t.delta, dtype=float)
    g_post = np.where(logm, v * bp * np.exp(d), v)
    g_prior = np.where(logm, v * bp, v)
    prior = pop.delta_prior_sd
    cov = t.delta_cov if t.delta_cov is not None else np.diag(np.asarray(t.delta_sd, dtype=float) ** 2)
    num = float(g_post @ cov @ g_post)
    den = float(g_prior @ np.diag(prior ** 2) @ g_prior)
    return math.sqrt(num / den) if den > 0 else None


WINDOW_WORDS = {"weekend": "at weekends", "saturday_afternoon": "on Saturday afternoons",
                "weekend_afternoon": "on weekend afternoons", "school_holidays": "in school holidays"}


def _window_applies(w: str, day: Day) -> bool | None:
    """Whether a record's time window covers this visit: True, False, or None (can't tell).

    The batch 9 review: an afternoon window was applied to the whole of Saturday, and a spot inside a place
    ("around the Rosetta Stone") to the whole place every day. Now a time of day applies only when the visit's own
    time is known to match, and a spot is a caution, never the place's crowding."""
    wd = day.weekday
    if day.window and w == day.window:
        return True
    part = day.window.split("_")[-1] if day.window else None      # "saturday_afternoon" → "afternoon"
    if w == "weekend":
        return None if wd is None else wd in ("sat", "sun")
    if w in ("weekend_afternoon", "saturday_afternoon"):
        days = ("sat", "sun") if w == "weekend_afternoon" else ("sat",)
        if wd is not None and wd not in days:
            return False
        if part is None or wd is None:
            return None
        return part == "afternoon"
    return None     # school holidays (dates unknown here), or a spot within the place: a caution only


def crowded_for_day(place: Place, exp, day: Day) -> tuple[int | str, str | None, list[str], str | None]:
    """How crowded an experience is on this day, from its record: (value, status, busy windows not known to apply,
    the window that decided).

    A window that covers the day decides; else the whole-day value; else unknown, with the windows it's known to be
    busy in, so the engine can say them (missing, never negative)."""
    claims = place.claims()
    vals = exp.atmosphere.get("crowded", ())
    from .experiences import _best_status
    for s in vals:
        if s.window and _window_applies(s.window, day) and s.value != "unknown":
            return s.value, _best_status(s, claims, "crowded"), [], s.window
    base = next((s for s in vals if s.window is None), None)
    other = [s.window for s in vals if s.window and s.value == 2 and not _window_applies(s.window, day)]
    if base is not None and base.value != "unknown":
        return base.value, _best_status(base, claims, "crowded"), other, None
    return "unknown", None, other, None


# ---- the judgement --------------------------------------------------------------------------------------------------

def match(pop: PopulationModel, t: Traveller, m: Moment, day: Day, *, amap: AspirationMap | None = None,
          checked: dict | None = None, know: Knowledge | None = None) -> Match:
    """The engine's judgement of one place for one traveller on one day. `checked` is the place's entry in the
    catalogue's checked layer; `know` holds the place records and kinds (without it, cards only)."""
    asp = amap.match(m, t.fields) if amap else 0.0
    x = moment_features(m, Conditions(day.temp_c, day.rain_prob), aspiration_match=asp)
    b = pop.b_person(t.delta)
    model_score = float(pop.vector(x) @ b)
    kind = know.kinds.get(m.id) if know else None
    rec = know.records.get(m.id) if know else None

    # positives and negatives: the strongest terms, each labelled with whose it is
    pos, neg, known_w, total_w = [], [], 0.0, 0.0
    for term in contributions(pop, b, x, top=8):
        if abs(term["contribution"]) < 0.005:
            continue
        who, who_text = _person_side(pop, t, term["feature"])
        row = {"feature": term["feature"], "label": term["label"], "contribution": term["contribution"],
               "traveller": who_text}
        (pos if term["contribution"] > 0 else neg).append(row)
        total_w += abs(term["contribution"])
        known_w += abs(term["contribution"]) if who == "theirs" else 0.0
    person_known = known_w / total_w if total_w else 0.0

    # the instructions: which one decides, and what it won over
    win, older = stance(t, m, kind)
    prefs = []
    if win:
        prefs.append({"instruction": win.kind, "about": win.label or win.target, "source": win.source,
                      "at": win.at.isoformat(), "decides": True})
        for o in older:
            prefs.append({"instruction": o.kind, "about": o.label or o.target, "source": o.source,
                          "at": o.at.isoformat(), "decides": False, "overridden_by": win.kind})

    # the dislike adjustments: a place they didn't enjoy, and similar places (never a ban)
    score, against, adj_note = model_score, None, None
    if _negative_stance(win):
        f, why = _context_factor(win, day)
        score -= DISLIKE_PLACE * f
        what = (f"You rated it {win.value} of 5" if win.kind == "rated" else f"You said you didn't enjoy {win.label}")
        against = what + (f" ({why})." if why else ".")
        adj_note = {"adjustment": -round(DISLIKE_PLACE * f, 3), "why": "a place they didn't enjoy", "context": why}
    elif win is None or win.kind not in ("must_go", "love_place", "rated"):
        worst, src = 0.0, None
        for i in evidence_by_place(t):
            if not _negative_stance(i) or i.target == m.id:
                continue
            sim = similarity(m.id, i.target, know)
            if sim > worst:
                worst, src = sim, i
        # the planner's own caveat, kept: a similar place they loved or found fine halves it
        liked = max((similarity(m.id, i.target, know) for i in evidence_by_place(t)
                     if i.kind in ("love_place", "fine_place") or _positive_stance(i)), default=0.0)
        if src is not None:
            f, why = _context_factor(src, day)
            if liked >= worst:
                f *= 0.5
                why = (why + "; " if why else "") + "they enjoyed a similar place"
            cut = DISLIKE_SIMILAR * worst * f
            score -= cut
            adj_note = {"adjustment": -round(cut, 3), "why": f"similar to {src.label or src.target}, which they "
                        "didn't enjoy", "similarity": round(worst, 2), "context": why}
            if worst >= 0.5 and liked < worst:
                against = f"You didn't enjoy {src.label or src.target}, and this is a similar kind of place."

    # restrictions: hard rules and current explicit exclusions; the newest instruction wins over older exclusions
    restr = restrictions_for(m, t, day, know=know, checked=checked)
    if win and win.kind == "avoid":
        restr.append((f"explicit exclusion: you asked not to visit {win.label or 'it'}", "your instruction"))
    if win and win.kind == "dislike_kind":
        restr.append((f"explicit exclusion: you asked for no {win.label or win.target}", "your instruction"))
    warnings = []
    if rec:
        from datetime import date as _d
        today = _d.fromisoformat(know.today) if know and know.today else None
        if today:
            for c in unverified_hard(rec[0], today):
                if c.status == "verified":       # verified once, now out of date: say it, never drop it silently
                    hit = c.dates and day.date and c.closed_on(day.date)
                    warnings.append(f"{c.claim} (checked {c.checked}, now out of date"
                                    + ("; it may close on this date: check before going" if hit else "")
                                    + "; said, never applied)")
                elif c.status != "unknown":
                    warnings.append(f"{c.claim} ({c.status}, not verified: said, never applied)")

    # experience-level evidence, or the card's own tags where there's no record
    ev = dim_evidence(pop, t, know)
    exp_rows, place_pos, place_neg, missing_dims, conflict_dims = [], [], [], [], []
    place_status = "card (inferred)"
    if rec:
        place, covered = rec
        place_status = "record"
        for e in place.ready():
            ap = record_appeals(place, e)
            fit = {}
            for dim, a in ap.items():
                if a.role == "other" or a.value == 0:
                    continue
                s, strength, items = _verdict(ev.get(dim, []))
                fit[dim] = {"role": a.role, "value": a.value, "place_status": a.status,
                            "traveller": "missing" if strength == "missing" else
                            "conflict" if strength == "conflict" else ("positive" if s > 0 else "negative"),
                            "strength": strength, "from": [i["from"] for i in items]}
                if e.id not in covered:
                    continue
                strong_place = RANK.get(a.status, 0) >= RANK["researched"]
                row = {"dim": dim, "role": a.role, "experience": e.title, "place_status": a.status,
                       "strength": strength, "from": items[0]["from"] if items else None}
                if strength == "missing" and a.role == "primary":
                    missing_dims.append(dim)
                elif strength == "conflict":
                    conflict_dims.append(dim)
                elif s > 0 and strong_place and strength in ("clear", "stated"):
                    place_pos.append(row)
                elif s < 0 and strength != "weak" and strong_place and a.role == "primary":
                    place_neg.append(row)
            atm = record_atmosphere(place, e, day.window)
            exp_rows.append({"id": e.id, "title": e.title, "primary": list(e.primary), "covered_by_card": e.id in covered,
                             "fit": fit, "crowded": atm["crowded"].value if "crowded" in atm else "unknown"})
        coverage_dims = {d for e in covered for d in place.experience(e).primary}
    else:
        coverage_dims = {f for f in PHRASE if _tag(m, f) >= LINK_MIN}

    # crowds, with the day's window where the record has one
    crowd_sign, _ = lean(pop, t, "crowds")
    crowded, crowd_status, busy_when, busy_win = 0, None, [], None
    if rec:
        for e in rec[1]:
            v, st, other, w = crowded_for_day(rec[0], rec[0].experience(e), day)
            if isinstance(v, int) and v > crowded:
                crowded, crowd_status, busy_win = v, st, w
            busy_when += other
    else:
        crowded, crowd_status = _tag(m, "crowds"), "card (inferred)"
    busy_against, crowd_neg, crowd_unknown = None, False, False
    said = "You picked quieter days" if t.n_choices else "Your answers lean away from crowds"
    if crowd_sign < 0 and crowded >= 2:
        when = f" {WINDOW_WORDS[busy_win]}" if busy_win in WINDOW_WORDS else ""
        busy_against = f"{said}, and this place is busy{when}."
        crowd_neg = rec is not None and RANK.get(crowd_status or "", 0) >= RANK["researched"]
    elif crowd_sign < 0 and rec and busy_when:
        # known busy at other times, unknown today: say the caution, and it lowers confidence (missing, not negative)
        busy_against = f"{said}, and this place is busy {WINDOW_WORDS.get(busy_when[0], busy_when[0])}."
        crowd_unknown = True

    # reasons: the traveller's own stance first, then a primary appeal with clear evidence on both sides
    reason, evidence, strong_evidence = None, [], False
    if win and win.kind == "must_go":
        reason = "Included because you specifically asked to visit."
        evidence = [{"traveller": "you asked for it", "place": "this place", "place_source": "your request"}]
        if any(_negative_stance(o) for o in older):
            o = next(o for o in older if _negative_stance(o))
            prefs[0]["note"] = (f"You said you didn't enjoy {o.label or 'it'} before; the newer request wins.")
    elif _positive_stance(win):
        reason = (f"You loved {win.label}." if win.kind == "love_place" else f"You rated it {win.value} of 5.")
        evidence = [{"traveller": reason[:-1].replace("You", "you", 1), "place": "this is that place",
                     "place_source": "your own answer"}]
        strong_evidence = True
    elif place_pos:
        best = sorted(place_pos, key=lambda r: (r["role"] != "primary", r["strength"] != "clear"))[0]
        person = best["from"][0].upper() + best["from"][1:]
        reason = f"{person}, and {DIM_PHRASE.get(best['dim'], best['dim'])} is what {best['experience']} is about." \
            if best["role"] == "primary" else \
            f"{person}, and {best['experience']} has {DIM_PHRASE.get(best['dim'], best['dim'])} too."
        evidence = [{"traveller": best["from"], "place": f"{best['dim']} {best['role']} ({best['place_status']})",
                     "place_source": "place record"}]
        strong_evidence = best["role"] == "primary" and best["strength"] in ("clear", "stated")
    elif not rec:
        reason, evidence = _card_reason(pop, t, m, amap, kind)

    if against is None and place_neg and place_neg[0]["dim"] != "crowds":
        r = place_neg[0]
        against = f"Your answers lean away from {DIM_PHRASE.get(r['dim'], r['dim'])}, and that's what " \
                  f"{r['experience']} is about."
    if against is None and not rec:
        against = _card_against(pop, t, m, kind)
    if against is None and busy_against:
        against = busy_against

    # confidence: its own axis, with its parts
    ratio = _predictive_ratio(pop, t, x)
    direct = win is not None
    if win is not None and win.kind == "fine_place":
        direct = True      # they've been and it was fine: about this place, but neither for nor against
    covered_n = sum(1 for d in coverage_dims
                    if any(x["strength"] in ("clear", "stated") for x in ev.get(d, []))
                    or (not rec and lean(pop, t, d)[0]))
    coverage = covered_n / len(coverage_dims) if coverage_dims else 0.0
    if crowd_neg:
        place_neg.append({"dim": "crowds", "role": "atmosphere", "experience": m.display_title(),
                          "place_status": crowd_status, "strength": "clear", "from": "your answers lowered crowds"})
    conflict = bool(conflict_dims) or (bool(place_pos or (reason and not direct)) and bool(place_neg or busy_against))
    why_low = []
    if t.n_answers == 0:
        why_low.append("they haven't answered yet")
    if conflict:
        why_low.append("the evidence conflicts")
    if not direct and rec and missing_dims and not place_pos:
        # a record says what the place is about, so "missing" is known: the m364 case (history lover, food market)
        why_low.append("nothing they've said touches what this place is about")
    if crowd_unknown and not direct:
        why_low.append("how busy it is on this day isn't known, and they avoid crowds")
    if not direct and ratio is not None and ratio > RATIO_LITTLE:
        why_low.append("their answers barely narrowed the model's view of this place")
    if direct and win.kind != "fine_place":
        level = "high" if not conflict_dims else "medium"
    elif why_low:
        level = "low"
    elif rec and place_pos and coverage >= 0.5 and not missing_dims and (ratio is None or ratio < RATIO_LEARNED):
        level = "high"    # a positive on what the place is about, from a record, and their answers narrowed it
    else:
        level = "medium"
    if not rec and level == "high" and not direct:
        level = "medium"    # a card's tags are inferred: never high on them alone
    conf = {"level": level, "why_low": why_low, "answers": t.n_answers,
            "predictive_ratio": None if ratio is None else round(ratio, 2),
            "coverage_of_main_appeals": round(coverage, 2), "missing": sorted(set(missing_dims)),
            "conflicts": sorted(set(conflict_dims)) + (["crowds"] if conflict and busy_against else []),
            "population_share": round(1 - person_known, 2), "place_evidence": place_status,
            "person_known": round(person_known, 2), "direct_signal": direct,
            "place_checked": sorted(checked) if checked else []}

    # a low score is theirs only when their own answers drive its biggest negative term
    own_negative = bool(neg) and neg[0]["traveller"] == "your answers" and person_known >= 0.2
    # the class, the first that applies
    hard = [r for r, _ in restr]
    misfit = False
    if restr:
        cls = "not_suitable"
        if win and win.kind == "must_go":
            hard.insert(0, "you asked for it, but a hard rule applies")
        basis = restr[0][1]
    elif win and win.kind == "must_go":
        cls, basis = "must_go", "your instruction"
    elif _positive_stance(win):
        cls, basis = "strong_match", "your own answer"
        misfit = model_score < FLOOR
    elif _negative_stance(win) or (place_neg and not conflict):
        cls, basis = "poor_match", "your own answer" if _negative_stance(win) else "your evidence and the place record"
    elif level == "low":
        cls, basis = "low_confidence", "population" if t.n_answers == 0 else "too little evidence"
    elif strong_evidence and score >= STRONG and rec:
        cls, basis = "strong_match", "your evidence and the place record"
    elif score >= FLOOR:
        cls, basis = "good_discovery", "your evidence" if person_known >= 0.2 else "mostly the population"
    elif own_negative and not (rec and missing_dims):
        cls, basis = "poor_match", "your evidence"
    else:
        # m366 (the engine bench: the history enthusiast's Borough Market was still "poor", held back by most
        # people's weights on crowds and cost): below the floor on the population's weights, or with what the place
        # is about unknown for them, is "we don't know", not "it won't suit you" (Abram, m364, decision 5)
        cls, basis = "low_confidence", "mostly the population"
        conf["level"] = "low"
        conf["why_low"].append("its low score rests on most people's weights, not on anything they said"
                               if not own_negative else "what this place is about is unknown for them")
    if adj_note:
        prefs.append({"instruction": "adjustment", **adj_note})

    shown = cls in ("must_go", "strong_match", "good_discovery") or (cls == "low_confidence" and conflict)
    miss = missing_facts(m, t, checked)
    for d in sorted(set(missing_dims)):
        miss.append(f"whether you enjoy {DIM_PHRASE.get(d, d)}: ODYS doesn't know yet")
    if rec:
        for e in rec[1]:
            miss += [f"{rec[0].name}: {n}" for n in rec[0].experience(e).needs]
    return Match(place=m.id, title=m.display_title(), cls=cls, score=score, restrictions=hard,
                 positives=pos[:3], negatives=neg[:3],
                 evidence=evidence if shown and reason else [], reason=reason if shown else None,
                 against=against if cls in ("poor_match", "good_discovery", "must_go", "low_confidence",
                                            "strong_match") else None,
                 missing=miss, confidence=conf, basis=basis, preferences=prefs, experiences=exp_rows,
                 warnings=warnings, model_score=model_score, misfit=misfit)


ART_KINDS = ("gallery", "arts_centre")   # their cards' history_culture stands for art (the vocabulary splits them)
FIRST_READ = "ODYS's first reading of this place"   # a card's tags: hand-set, inferred, not yet checked


def _card_tags(m: Moment, kind: str | None) -> list[str]:
    """The card's tags at 2 a reason may name. history_culture on a gallery is art, so it isn't said as history
    (the batch 9 review: 185 "history" reasons at art galleries)."""
    return [f for f in PHRASE if _tag(m, f) >= LINK_MIN and not (f == "history_culture" and kind in ART_KINDS)]


def _card_reason(pop: PopulationModel, t: Traveller, m: Moment, amap: AspirationMap | None,
                 kind: str | None = None) -> tuple[str | None, list[dict]]:
    """A place known only by its card: the batch 8 reasons, with the sign test, **worded as ODYS's own first
    reading** (a card's tags are hand-set and inferred, never "what this place is about"; Abram, m364). It can make
    a place a good discovery, never a strong match."""
    if amap and t.fields:
        hit = amap.fields_of(m) & set(t.fields)
        if kind in ART_KINDS:
            hit -= {"history_culture"}
        if hit:
            label = amap.labels(hit)[0]
            return (f"You picked {label.lower()} as an interest, and ODYS lists this place under it (not yet checked "
                    "against its own pages).",
                    [{"traveller": f"interest: {label}", "place": f"mapped to {label} (data/aspiration.yaml)",
                      "place_source": "card (inferred)"}])
    d = dict(zip(pop.personal_names, (float(v) for v in t.delta)))
    felt = {f: w for w in t.feelings for f, v in FEELINGS.get(w, {}).items() if v > 0}
    for f in sorted(_card_tags(m, kind), key=lambda f: -d.get(f, 0.0)):
        sign, _ = lean(pop, t, f)
        link = next((name for name, tags in t.loved_tags if (tags.get(f) or 0) >= LINK_MIN), None)
        if link and sign > 0:
            return (f"You loved {link}, and {FIRST_READ} includes {PHRASE[f]} too.",
                    [{"traveller": f"loved {link} ({f} = 2 there)", "place": f"{f} = 2 on its card",
                      "place_source": "card (inferred)"}])
        if sign > 0:
            return (f"Your answers lean towards {PHRASE[f]}, and {FIRST_READ} includes it.",
                    [{"traveller": f"your answers raised '{pop.spec(f).label}'", "place": f"{f} = 2 on its card",
                      "place_source": "card (inferred)"}])
        if f in felt and d.get(f, 0) > 0:
            return (f"You go out to feel {felt[f]}, and {FIRST_READ} includes {PHRASE[f]}.",
                    [{"traveller": f"feeling: {felt[f]}", "place": f"{f} = 2 on its card",
                      "place_source": "card (inferred)"}])
    if lean(pop, t, "crowds")[0] < 0 and _tag(m, "crowds") <= QUIET_MAX:
        said = "You picked quieter days" if t.n_choices else "Your answers lean towards quieter places"
        return (f"{said}, and {FIRST_READ} is that it's quiet.",
                [{"traveller": "your answers lowered 'crowds'", "place": "crowds = 0 on its card",
                  "place_source": "card (inferred)"}])
    return None, []


def _card_against(pop: PopulationModel, t: Traveller, m: Moment, kind: str | None = None) -> str | None:
    """Why a card-only place may not suit them, with a clear lean and a tag of 2, worded as a first reading."""
    if lean(pop, t, "crowds")[0] < 0 and _tag(m, "crowds") >= LINK_MIN:
        return ("You picked quieter days" if t.n_choices else "Your answers lean away from crowds") + \
            f", and {FIRST_READ} is that it's busy."
    for f in _card_tags(m, kind):
        if f != "crowds" and lean(pop, t, f)[0] < 0:
            return f"Your answers lean away from {PHRASE[f]}, and {FIRST_READ} includes it."
    return None


def rank(matches: list[Match]) -> list[Match]:
    """A personal ranking: what they asked for first, not suitable last, and everything else by score.

    m366: the class is the label, not the order (the batch 8 review's "classes become only a display"). Ordering by
    class put a low-confidence place below a poor match, which made missing evidence count as negative (Abram,
    m364: it lowers certainty, never suitability), and it lowered the hidden bench's rank correlation from 0.20 to
    0.14 (`validation/engine-bench/hidden-*.md`). A place they didn't enjoy still sinks: its score carries the
    strong negative."""
    def key(r: Match):
        return (0 if r.cls == "must_go" else 2 if r.cls == "not_suitable" else 1, -r.score)
    return sorted(matches, key=key)
