"""D115: "Why we picked this for you" in plain words, the plan's one-line feeling summary, and the feelings on
screen 5 ("Why you go out") as evidence in the fit.

**Honesty rule:** a reason names something the person told us that really raises this stop's score *for them*:
- the place they loved, when this stop is at it (the familiar favourite, D103);
- a place they loved that shares a feature with this stop, when their own weight on that feature is positive;
- a feeling they go out for (screen 5), which enters the fit as a stated choice (`feeling_observation`);
- a stop they rated highly that shares a feature with this one;
- an interest they picked (the aspiration term);
- a trade-off from "this or that" (quieter or cheaper days), when their weight is clearly off the population's.
If none applies it says so: "we don't know much about you yet". Reasons and the feeling line are never shown in the
blind Test B comparison (the plan request's `blind`).
"""

from __future__ import annotations

import numpy as np

from .moments import Moment
from .personal import Observation
from .population import PopulationModel

# Screen 5 (D115): feelings people go out for, each mapped onto existing features (feature units: a tag of 2 = 1.0)
FEELINGS: dict[str, dict[str, float]] = {
    "restored": {"green_nature": 1.0, "awe": 0.5},
    "excited": {"absorption": 1.0, "active": 0.5, "contrast_reveal": 0.5},
    "connected": {"social_pull": 1.0, "food": 0.5},
    "curious": {"history_culture": 1.0, "local_novel": 0.5},
    "peaceful": {"crowds": -1.0, "movement_views": 0.5},
}
FEELING_SCALE = 0.5   # GUESS: a general reason for going out is weaker evidence than a concrete this-or-that choice

# D127 (algorithm reviews: "use the answers you collect, or stop collecting them"): the "about you" answers from
# "Improve future plans", as stated leanings in the same way as the feelings and at the same weight. GUESS directions
# and sizes; the person's own ratings soon outweigh them. Going alone, a medium day and "neither" say nothing.
ABOUT_YOU: dict[tuple[str, str], dict[str, float]] = {
    ("company", "friends"): {"social_pull": 1.0},
    ("company", "partner"): {"social_pull": 1.0},
    ("company", "family"): {"social_pull": 1.0},
    ("activity", "gentle"): {"walking_effort": -1.0, "active": -0.5},
    ("activity", "full_on"): {"walking_effort": 0.5, "active": 1.0},
}

PHRASE = {   # a feature in plain words, as "this has …"
    "movement_views": "views", "food": "good food", "green_nature": "green space", "history_culture": "history",
    "iconic": "a famous sight", "local_novel": "somewhere local and new", "walking_effort": "a good walk",
    "active": "something active", "outdoor_exposure": "time outdoors", "photo_potential": "a great photo spot",
    "contrast_reveal": "a big reveal", "absorption": "something absorbing to do", "awe": "a sense of awe",
    "social_pull": "somewhere to bring people",
}
MIN_WEIGHT = 0.15    # a personal weight this far above the population's counts as a real lean
MAX_REASONS = 2


def feeling_observation(pop: PopulationModel, feeling: str) -> Observation | None:
    """"I go out to feel peaceful" as one stated choice: a day with those features over one without."""
    x = FEELINGS.get(feeling)
    if not x:
        return None
    return Observation(x=pop.vector(x), y=1, scale=pop.scales["conjoint"] * FEELING_SCALE)


def about_you_observation(pop: PopulationModel, key: str, value: str | None) -> Observation | None:
    """D127: "Who do you usually go with?" or "How active do you like a day to be?" as one stated choice."""
    x = ABOUT_YOU.get((key, value or ""))
    if not x:
        return None
    return Observation(x=pop.vector(x), y=1, scale=pop.scales["conjoint"] * FEELING_SCALE)


def _tags(m: Moment) -> dict[str, float]:
    return {k: float(v or 0) for k, v in {**m.features.place, **m.features.moment}.items()}


def _r(you: str, me: str | None) -> dict:
    return {"you": you, "me": me}


def _mid(name: str) -> str:
    """A place name inside a sentence: "The view from…" → "the view from…", "Walking from…" → "walking from…"."""
    first, _, rest = name.partition(" ")
    return (first.lower() + " " + rest) if first in ("The", "Walking") and rest else name


def stop_reasons(pop: PopulationModel, delta: np.ndarray, m: Moment, *, loved: list[tuple[str, list[str], Moment]],
                 feelings: list[str], rated: list[tuple[Moment, int]], interests: list[str], n_choices: int,
                 loved_kinds: list[tuple[str, Moment]] = (), wanted: list[tuple[str, Moment]] = (),
                 taken: set[str] | None = None) -> list[dict]:
    """Up to two reasons for one stop, each as "you" (the app) and "me" (the share card) wording.

    `taken` (m187, the algorithm review): what the plan's earlier stops already said (their places, feelings and
    lines). They're avoided first, so a day doesn't repeat "You loved the British Museum…" at every stop; if nothing
    else fits, the stop may say it again rather than "We don't know much about you". Updated in place."""
    args = (pop, delta, m, loved, feelings, rated, interests, n_choices, loved_kinds, wanted)
    out, said = _reasons(*args, used=set(taken or ()))
    if taken and out and out[0]["me"] is None:
        out, said = _reasons(*args, used=set())
    if taken is not None:
        taken |= said
    return out


def _reasons(pop, delta, m, loved, feelings, rated, interests, n_choices, loved_kinds, wanted,
             used: set[str]) -> tuple[list[dict], set[str]]:
    d = dict(zip(pop.personal_names, (float(v) for v in delta)))   # δ is over the personal features only
    tags = _tags(m)
    out: list[dict] = []
    before = set(used)

    for name, cards, _ in loved:                                   # the familiar favourite
        if m.id in cards:
            out.append(_r(f"You loved {_mid(name)}.", f"I loved {_mid(name)}."))
            used.add(name)
            break

    # this stop's features that the person leans towards, strongest first. A feeling they picked is itself the
    # evidence, so any positive lean it gives counts; a loved place or a rating needs a clear lean (MIN_WEIGHT)
    leans = sorted((f for f in PHRASE if tags.get(f, 0) >= 1 and d.get(f, 0) > 0), key=lambda f: -tags[f] * d[f])
    for f in leans:
        if len(out) >= MAX_REASONS:
            break
        phrase = PHRASE[f]
        clear = d[f] > MIN_WEIGHT
        place = None if not clear else next((n for n, cards, pm in loved if n not in used and m.id not in cards and _tags(pm).get(f, 0) >= 1),
                     None)
        kind = None if not clear else next((k for k, km in loved_kinds if k not in used and _tags(km).get(f, 0) >= 1),
                                           None)
        if kind and not place:   # D116: a visitor's category card
            out.append(_r(f"You love {kind}, and this has {phrase}.", f"I love {kind}, and this has {phrase}."))
            used.add(kind)
            continue
        try_it = next((k for k, km in wanted if k not in used and _tags(km).get(f, 0) >= 1), None)
        if try_it and not place:
            out.append(_r(f"You'd like to try {try_it}, and this has {phrase}.",
                          f"I wanted to try {try_it}, and this has {phrase}."))
            used.add(try_it)
            continue
        if place:
            out.append(_r(f"You loved {_mid(place)}, and this has {phrase} too.",
                          f"I loved {_mid(place)}, and this has {phrase} too."))
            used.add(place)
            continue
        feel = next((w for w in feelings if FEELINGS.get(w, {}).get(f, 0) > 0 and w not in used), None)
        if feel:
            out.append(_r(f"You go out to feel {feel}, and this has {phrase}.",
                          f"I go out to feel {feel}, and this has {phrase}."))
            used.add(feel)
            continue
        good = None if not clear else next((rm for rm, r in rated if r >= 4 and rm.id != m.id
                                            and _tags(rm).get(f, 0) >= 1 and rm.title not in used), None)
        if good:
            out.append(_r(f"You rated {good.title} highly, and this has {phrase} too.",
                          f"I rated {good.title} highly, and this has {phrase} too."))
            used.add(good.title)

    general = []
    if interests:
        general.append(_r(f"It fits your interest in {interests[0].lower()}.", f"It fits my interest in {interests[0].lower()}."))
    if n_choices and tags.get("crowds", 0) == 0 and d.get("crowds", 0) < -MIN_WEIGHT:
        general.append(_r("You picked quieter days, and this is a quiet one.", "I like quieter places, and this is a quiet one."))
    if n_choices and not (m.cost_gbp or 0) and d.get("cost_per_10gbp", 0) > MIN_WEIGHT:
        # log scale (D88): δ > 0 means more sensitive to cost than most people
        general.append(_r("You picked cheaper days, and this one is free.", "I like days that don't cost much, and this one is free."))
    for g in general:
        if len(out) < MAX_REASONS and g["you"] not in used:
            out.append(g)
    if not out:
        out.append(_r("We don't know much about you yet: this one suits most people and fits your route.", None))
    out = out[:MAX_REASONS]
    return out, (used - before) | {r["you"] for r in out}


def basis(n_places: int, n_choices: int, n_ratings: int, n_feelings: int, n_kinds: int = 0) -> dict:
    """What the reasons rest on so far, for the "so far" line."""
    return {"places": n_places, "choices": n_choices, "ratings": n_ratings, "feelings": n_feelings, "kinds": n_kinds}


# ---- the plan's one-line feeling summary (D115) --------------------------------------------------------------

STOP_FEEL = [   # (feature, phrase for a stop, phrase for the day's high point), in order of preference on ties
    ("contrast_reveal", "a reveal", "one big reveal"),
    ("movement_views", "a big view", "the view of the day"),
    ("awe", "a wow moment", "one big wow"),
    ("history_culture", "some history", "one big discovery"),
    ("absorption", "something hands-on", "one thing to get lost in"),
    ("local_novel", "somewhere new", "one big discovery"),
    ("green_nature", "a green break", "a long green break"),
    ("active", "something active", "one active high point"),
    ("iconic", "a famous sight", "one famous sight"),
    ("social_pull", "a place to share", "one place to share"),
    ("photo_potential", "a photo spot", "one great photo"),
    ("food", "good food", "a proper feast"),
]
RIVER_WORDS = ("thames", "river", "boat", "bridge", "south bank", "riverside")


def _stop_feel(m: Moment | None, lunch_slot: bool, peak: bool, first: bool, taken: set[str]) -> tuple[str, str]:
    """(phrase, feature used). Each feature is used once a day, so two stops never read the same."""
    if lunch_slot or m is None:
        return ("lunch to start" if first else "lunch"), "lunch"
    text = f"{m.title} {m.place.name}".lower()
    if any(w in text for w in RIVER_WORDS) and "river" not in taken:
        return "the river", "river"
    tags = _tags(m)
    for f, plain, high in sorted(STOP_FEEL, key=lambda t: -tags.get(t[0], 0)):
        if tags.get(f, 0) <= 0:
            break
        if f not in taken:
            return (high if peak else plain), f
    return "one more stop", "other"


# D118: the feelings as words for a day ("A curious, peaceful day: …"), used only when the stops really match
FEELING_ADJ = {"restored": "restoring", "excited": "lively", "connected": "sociable", "curious": "curious",
               "peaceful": "peaceful"}
FIT = 0.75   # a stop fits a feeling when its tags (0-1) score at least this on the feeling's features


def _fits(m: Moment, feeling: str) -> bool:
    """A stop fits a feeling when its own tags carry it: positive features as tagged (0-1), and a negative one (crowds,
    for "peaceful") as its absence, so a quiet place counts and a crowded one doesn't."""
    t = {k: v / 2.0 for k, v in _tags(m).items()}
    score = sum(w * t.get(k, 0.0) if w > 0 else -w * (1.0 - t.get(k, 0.0))
                for k, w in FEELINGS.get(feeling, {}).items())
    return score >= FIT


def day_feelings(stops: list[dict], by_id: dict[str, Moment], feelings: list[str]) -> list[str]:
    """The person's own feelings (screen 5) that this day really carries: at least half its stops with a card fit, and
    at least two of them when there are two or more. Never a feeling they didn't pick."""
    cards = [by_id[s["moment_id"].split("#")[0]] for s in stops
             if not s["moment_id"].startswith("lunch@") and s["moment_id"].split("#")[0] in by_id]
    out = []
    for f in feelings:
        n = sum(_fits(m, f) for m in cards)
        if cards and n * 2 >= len(cards) and n >= min(2, len(cards)):
            out.append(f)
    return out


def feel_line(stops: list[dict], by_id: dict[str, Moment], feelings: list[str] = ()) -> str:
    """"Some history, one big reveal, good food, then the river": one phrase per stop, the day's high point (the
    highest predicted stop) marked, the last after "then". Plain words from the cards' own tags.
    D118: with the person's feelings, "A curious, peaceful day: some history, …" when the stops really carry them."""
    if not stops:
        return ""
    preds = [(s.get("predicted") if s.get("predicted") is not None else -99, i) for i, s in enumerate(stops)]
    peak = max(preds)[1] if any(p > -99 for p, _ in preds) else -1
    taken: set[str] = set()
    phrases = []
    for i, s in enumerate(stops):
        mid = s["moment_id"]
        m = by_id.get(mid.split("#")[0])
        if s.get("lunch") and m is not None and "food" not in taken:   # a food card as the lunch stop
            p, f = "good food", "food"
        else:
            p, f = _stop_feel(m, mid.startswith("lunch@"), i == peak, i == 0, taken)
        taken.add(f)
        phrases.append(p)
    if len(phrases) == 1:
        text = phrases[0]
    else:
        text = ", ".join(phrases[:-1]) + ", then " + phrases[-1]
    words = [FEELING_ADJ[f] for f in day_feelings(stops, by_id, list(feelings)) if f in FEELING_ADJ]
    if words:
        text = f"A {', '.join(words)} day: {text}"
    return text[:1].upper() + text[1:]
