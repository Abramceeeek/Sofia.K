"""m363 (Abram, 26 Nov, batch 8): the first central person-to-place engine, **in shadow mode**. One answer to "is this
place right for this traveller on this day, and why?", from the same model and rules the planner uses, so the
planner's scattered judgements (`decisions/person-to-place-engine.md` §1.3) can be compared with one place that makes
them. It changes no plan: nothing in the planner calls it.

**Six classes**, the first that applies (Abram's decision, m363):
1. ``not_suitable``: a hard restriction or an explicit exclusion. Closed that date, an age rule, a place they didn't
   enjoy (or one of a kind they didn't enjoy, as the planner already rules), strenuous for a gentle pace,
   dry-weather only on a rainy day, more than the whole day's budget, or not plannable.
2. ``must_go``: the traveller asked for it. **Intent, not predicted enjoyment**; it never overrides 1.
3. ``low_confidence``: the score rests on the population. Nothing the person said touches this place's defining
   features, and no direct signal does (loved, disliked, rated, asked for, an interest, a feeling).
4. ``strong_match``: score at or above STRONG, with at least one reason that's strong on both sides.
5. ``good_discovery``: at or above the planner's floor.
6. ``poor_match``: below the floor.

**The score is a provisional ranking measure, never a chance** (Abram: "Do not claim a score of 0.75 means a 75% chance
of a good visit"). It is the person's utility, x·(b_population + δ_person), in the model's own units, exactly as the
planner ranks with it. FLOOR is the planner's own floor; STRONG is a GUESS (below).

**Evidence on both sides** (work package D): a reason needs evidence about the traveller (something they said or did,
or a clear lean their answers moved) **and** about the place (a tag at its top value, 2, meaning it defines the
place; or a checked fact). A tag of 1 is "partial" and never supports a claim. Where the evidence is thin, there is no
reason and the class says so. Every place fact is labelled with where it comes from: "checked" (an official page, with
its date), "card" (set by hand on the card: an inference, never verified against people), or "unknown".
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .aspiration import AspirationMap
from .features import Conditions, moment_features
from .moments import Moment
from .population import PopulationModel
from .reasons import FEELINGS, LINK_MIN, MIN_WEIGHT, PHRASE
from .scoring import contributions

CLASSES = ("not_suitable", "must_go", "low_confidence", "strong_match", "good_discovery", "poor_match")
FLOOR = -0.75        # the planner's floor (the rating model's 2|3 cut, `priors.yaml`): its own rule, unchanged
STRONG = 0.35        # GUESS: 1.1 above the floor, where the old "0.75" match word sat; a score cut-off, not a chance
LOW_KNOWN = 0.2      # GUESS: under this share of the score's weight on known features, with no direct signal, is
                     # "low confidence"
QUIET_MAX = 0        # a place is "quiet" on its card only at crowds 0
TAG_NAMES = ("movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel", "crowds",
             "walking_effort", "active", "outdoor_exposure", "photo_potential", "contrast_reveal", "absorption",
             "awe", "social_pull")


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
    must_go: tuple[str, ...] = ()         # card ids they asked for
    rated: dict[str, int] = field(default_factory=dict)      # card id → their 1-5 rating
    fields: frozenset[str] = frozenset()  # interests (aspiration codes)
    feelings: tuple[str, ...] = ()        # how they want to feel
    activity: str | None = None
    budget_gbp: float | None = None       # a day, per person
    children: tuple[int, ...] = ()
    n_answers: int = 0                    # swipes, choices and ratings that carry information


@dataclass(frozen=True)
class Day:
    weekday: str | None = None            # "mon".."sun"
    date: str | None = None               # ISO date
    temp_c: float | None = None
    rain_prob: float | None = None


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
    confidence: dict = field(default_factory=dict)            # person_known, place_checked, level
    basis: str = ""                                           # "verified", "inferred" or "assumed": what the class rests on

    def out(self) -> dict:
        return {"place": self.place, "title": self.title, "class": self.cls, "score": round(self.score, 3),
                "restrictions": self.restrictions, "positives": self.positives, "negatives": self.negatives,
                "evidence": self.evidence, "reason": self.reason, "against": self.against, "missing": self.missing,
                "confidence": self.confidence, "basis": self.basis}


def _tag(m: Moment, name: str) -> int:
    return int(m.tag(name) or 0)


def _person_side(pop: PopulationModel, t: Traveller, feature: str) -> tuple[str, str]:
    """Where a feature's personal weight comes from: ("theirs", how) if their answers moved it clearly, else
    ("population", "most people")."""
    names = pop.personal_names
    if feature not in names:
        return "population", "most people"
    i = names.index(feature)
    # δ starts at 0 (the population), so a weight their answers moved by more than the lean threshold is theirs. (A
    # first rule also asked for the spread to narrow under KNOWN_RATIO: after a few swipes it rarely does, and the
    # first bench run called a +0.29 that came wholly from their answers "most people".)
    moved = abs(float(t.delta[i])) > MIN_WEIGHT
    return ("theirs", "your answers") if moved else ("population", "most people")


def _place_side(m: Moment, feature: str, checked: dict | None) -> tuple[str, str]:
    """Where a feature's value on the place comes from, and how strongly the place has it."""
    if feature in TAG_NAMES:
        v = _tag(m, feature)
        strength = "defining" if v >= LINK_MIN else "partial" if v == 1 else "absent"
        return strength, "card"   # set by hand on the card: an inference, never verified against people
    if feature == "cost_per_10gbp":
        return ("defining" if (m.cost_gbp or 0) > 0 else "absent"), ("checked" if checked and "price" in checked else "card")
    return "partial", "conditions"


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


def restrictions_for(m: Moment, t: Traveller, day: Day) -> list[str]:
    """The hard rules, apart from ranking. The planner's own exclusions (dayplan.kept_out, the opening rules, the
    rain rule, the budget) are carried over as they are: shadow mode reports, it doesn't change them."""
    out = []
    if m.status != "ready":
        out.append("not a ready card: never planned")
    elif not m.plannable():
        out.append("the card is missing facts the planner needs")
    if not m.open_on(day.weekday, day.date):
        out.append(f"closed on {day.date or day.weekday}")
    if m.id in t.disliked:
        out.append(f"explicit exclusion: you didn't enjoy {t.disliked[m.id]}")
    elif m.id in t.kept_out:
        out.append(f"excluded by the planner's rule: {t.kept_out[m.id]}")
    if day.rain_prob is not None and day.rain_prob >= 0.5 and m.best_time.weather == ["dry"]:
        out.append("needs a dry day, and rain is likely")
    if t.budget_gbp is not None and (m.cost_gbp or 0) > t.budget_gbp:
        out.append(f"costs £{m.cost_gbp:g}, more than the day's budget of £{t.budget_gbp:g}")
    return out


def _reason(pop: PopulationModel, t: Traveller, m: Moment, amap: AspirationMap | None) -> tuple[str | None, list[dict]]:
    """The one sentence a stop may say about this traveller, with what it rests on, or None. Evidence on both sides,
    strongest first: the exact place loved or rated; an interest the place serves; a feature that defines the place
    and that the traveller clearly leans towards, through their answers, a feeling or a loved place it defines."""
    if m.id in t.loved:
        return (f"You loved {t.loved[m.id]}.",
                [{"traveller": f"loved {t.loved[m.id]}", "place": "this is that place", "place_source": "card"}])
    if t.rated.get(m.id, 0) >= 4:
        return (f"You rated it {t.rated[m.id]} of 5.",
                [{"traveller": f"rated it {t.rated[m.id]}", "place": "this place", "place_source": "card"}])
    if amap and t.fields:
        hit = amap.fields_of(m) & set(t.fields)
        if hit:
            label = amap.labels(hit)[0]
            return (f"It's one of London's places for your interest in {label.lower()}.",
                    [{"traveller": f"interest: {label}", "place": f"mapped to {label} (data/aspiration.yaml)",
                      "place_source": "card"}])
    d = dict(zip(pop.personal_names, (float(v) for v in t.delta)))
    felt = {f: w for w in t.feelings for f, v in FEELINGS.get(w, {}).items() if v > 0}
    for f in sorted((f for f in PHRASE if _tag(m, f) >= LINK_MIN), key=lambda f: -d.get(f, 0.0)):
        who, _ = _person_side(pop, t, f)
        # a place they loved that the same feature defines (both at 2): the m353 rule, now on both sides
        link = next((name for name, tags in t.loved_tags if (tags.get(f) or 0) >= LINK_MIN), None)
        # m363 (the first bench run: "You loved the NHM walk, and somewhere to bring people is what Borough Market is
        # about too"): a shared defining feature isn't enough; their answers must lean towards it too
        if link and who == "theirs" and d.get(f, 0) > MIN_WEIGHT:
            return (f"You loved {link}, and {PHRASE[f]} is what this place is about too.",
                    [{"traveller": f"loved {link} ({f} = 2 there)", "place": f"{f} = 2 (defines it)",
                      "place_source": "card"}])
        if who == "theirs" and d.get(f, 0) > MIN_WEIGHT:
            return (f"Your answers lean towards {PHRASE[f]}, and that's what this place is about.",
                    [{"traveller": f"your answers raised '{pop.spec(f).label}'", "place": f"{f} = 2 (defines it)",
                      "place_source": "card"}])
        if f in felt and d.get(f, 0) > 0:
            return (f"You go out to feel {felt[f]}, and {PHRASE[f]} is what this place is about.",
                    [{"traveller": f"feeling: {felt[f]}", "place": f"{f} = 2 (defines it)", "place_source": "card"}])
    if d.get("crowds", 0) < -MIN_WEIGHT and _person_side(pop, t, "crowds")[0] == "theirs" and _tag(m, "crowds") <= QUIET_MAX:
        return ("You picked quieter days, and this is a quiet place.",
                [{"traveller": "your answers lowered 'crowds'", "place": "crowds = 0 (quiet)", "place_source": "card"}])
    return None, []


def _against(pop: PopulationModel, t: Traveller, m: Moment) -> str | None:
    """Why it may not suit them, with evidence on both sides, or None."""
    d = dict(zip(pop.personal_names, (float(v) for v in t.delta)))
    if d.get("crowds", 0) < -MIN_WEIGHT and _person_side(pop, t, "crowds")[0] == "theirs" and _tag(m, "crowds") >= LINK_MIN:
        return "You picked quieter days, and this place is busy."
    for f in PHRASE:
        if _tag(m, f) >= LINK_MIN and d.get(f, 0) < -MIN_WEIGHT and _person_side(pop, t, f)[0] == "theirs":
            return f"Your answers lean away from {PHRASE[f]}, and that's what this place is about."
    return None


def match(pop: PopulationModel, t: Traveller, m: Moment, day: Day, *, amap: AspirationMap | None = None,
          checked: dict | None = None) -> Match:
    """The engine's judgement of one place for one traveller on one day. `checked` is the place's entry in the
    catalogue's checked layer (official facts with their dates), if it has one."""
    asp = amap.match(m, t.fields) if amap else 0.0
    x = moment_features(m, Conditions(day.temp_c, day.rain_prob), aspiration_match=asp)
    b = pop.b_person(t.delta)
    score = float(pop.vector(x) @ b)
    terms = contributions(pop, b, x, top=8)
    pos, neg, known_w, total_w = [], [], 0.0, 0.0
    for term in terms:
        if abs(term["contribution"]) < 0.005:   # a feature with no weight for this person says nothing
            continue
        who, who_text = _person_side(pop, t, term["feature"])
        strength, src = _place_side(m, term["feature"], checked)
        row = {"feature": term["feature"], "label": term["label"], "contribution": term["contribution"],
               "traveller": who_text, "place": strength, "place_source": src}
        (pos if term["contribution"] > 0 else neg).append(row)
        total_w += abs(term["contribution"])
        known_w += abs(term["contribution"]) if who == "theirs" else 0.0
    person_known = known_w / total_w if total_w else 0.0
    checked_keys = sorted(checked) if checked else []
    restrictions = restrictions_for(m, t, day)
    reason, evidence = _reason(pop, t, m, amap)
    against = _against(pop, t, m)
    # a direct signal: something the traveller said about this place, or a reason strong on both sides
    direct = m.id in t.loved or m.id in t.disliked or m.id in t.rated or m.id in t.must_go or asp > 0 \
        or reason is not None or against is not None
    # m363: having loved this very place, or rated it 4 or 5, is the strongest evidence there is, whatever the score
    known_good = m.id in t.loved or t.rated.get(m.id, 0) >= 4
    if restrictions:
        cls = "not_suitable"
        if m.id in t.must_go:
            restrictions.insert(0, "you asked for it, but a hard rule applies")
    elif m.id in t.must_go:
        cls = "must_go"
    elif not direct and person_known < LOW_KNOWN:
        cls = "low_confidence"
    elif known_good or (score >= STRONG and reason):
        cls = "strong_match"
    elif score >= FLOOR:
        cls = "good_discovery"
    else:
        cls = "poor_match"
    basis = ("verified" if restrictions and any(k in checked_keys for k in ("hours", "age", "notices"))
             else "inferred" if (direct or person_known >= LOW_KNOWN) else "assumed")
    level = "low" if cls == "low_confidence" else "high" if (direct and person_known >= 0.5) else "medium"
    return Match(place=m.id, title=m.display_title(), cls=cls, score=score, restrictions=restrictions,
                 positives=pos[:3], negatives=neg[:3],
                 # a reason is said only for a place recommended to them; a poor match says why not, when it can
                 evidence=evidence if cls in ("must_go", "strong_match", "good_discovery") else [],
                 reason=reason if cls in ("must_go", "strong_match", "good_discovery") else None,
                 against=against if cls in ("poor_match", "good_discovery", "must_go") else None,
                 missing=missing_facts(m, t, checked),
                 confidence={"person_known": round(person_known, 2), "direct_signal": direct,
                             "place_checked": checked_keys, "level": level},
                 basis=basis)


def rank(matches: list[Match]) -> list[Match]:
    """A personal ranking: must-go first, then by class, then by score within each class. Not suitable is last."""
    order = {c: i for i, c in enumerate(("must_go", "strong_match", "good_discovery", "low_confidence",
                                         "poor_match", "not_suitable"))}
    return sorted(matches, key=lambda r: (order[r.cls], -r.score))
