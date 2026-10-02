"""D117: short reactions between onboarding answers, and the "So far, I've learned…" list before the first plan.

Both come only from what the person actually answered: a place they loved or didn't, a kind of place, a feeling, the
made-up day they picked. Never from the fitted weights, and never a score. Each item on the list has an id, so the
person can mark it "not right"; a correction is stored (the export shows it) and that answer stops counting.

Item ids: feeling:<feeling>, place:<swipe item>, kind:<category key>, choice:<attribute>.
"""

from __future__ import annotations

from collections import Counter

from .features import conjoint_plan_features, leg_features
from .reasons import _mid

# The "this or that" attributes (conjoint_design.csv), in the order the app shows them, and the features each one
# moves. A corrected "choice:<attribute>" drops those features from every this-or-that answer.
ATTRIBUTES = ("transfer", "weather", "pace", "crowds", "cost", "walking")
ATTR_FEATURES = {
    "transfer": tuple(leg_features(50.0)), "weather": ("cold_outdoor", "rain_outdoor"), "pace": ("packed_pace",),
    "crowds": ("crowds",), "cost": ("cost_per_10gbp",), "walking": ("long_walk",)}
_WEATHER_ORDER = ("mild", "cold", "rainy")   # better to worse
MIN_DAYS = 3   # a pattern is named only after this many made-up days where the attribute differed

TEND_WORDS = {
    "pace": ("the relaxed day with fewer stops", "the fuller day with more stops"),
    "walking": ("less walking", "more walking"),
    "crowds": ("quieter places", "busier places"),
    "transfer": ("shorter journeys between stops", "longer journeys between stops"),
    "weather": ("better weather at the outdoor stops", "the day with worse weather"),
    "cost": ("the cheaper day", "the pricier day"),
}


def _level(attr: str, row: dict[str, str]) -> float:
    """A number per attribute level, where lower is the "less" side: shorter, better weather, relaxed, quiet, cheaper,
    less walking."""
    v = row[attr]
    if attr == "transfer":
        return float(v.split()[2])
    if attr == "weather":
        return float(next(i for i, w in enumerate(_WEATHER_ORDER) if v.startswith(w)))
    if attr == "pace":
        return 1.0 if v.startswith("5 stops") else 0.0
    if attr == "crowds":
        return 1.0 if v.startswith("busy") else 0.0
    if attr == "cost":
        return float(v.lstrip("£").split()[0])
    return 1.0 if "8 km" in v else 0.0


def task_levels(task: dict[str, dict[str, str]]) -> dict[str, list[float]]:
    """Each made-up day's level on every attribute (ATTRIBUTES order; lower is the "less" side), so the app can say
    "So far you've picked less walking every time" once an answer pattern shows. One choice alone can't: the two days
    differ on five or six things at once, so we can't tell which one decided it."""
    return {c: [_level(a, task[c]) for a in ATTRIBUTES] for c in ("A", "B")}


def tendency_words() -> list[dict[str, str]]:
    """The words for each attribute's two sides, for the app's reactions (same wording as the "So far" list)."""
    return [{"attr": a, "low": TEND_WORDS[a][0], "high": TEND_WORDS[a][1]} for a in ATTRIBUTES]


def place_reactions(phrase: str | None) -> dict[str, str]:
    """A place swipe or a kind of place: what the answer tells us, in the place's own words."""
    if not phrase:
        return {}
    return {"loved": f"Got it: {phrase}.", "didnt_enjoy": f"Noted: not so much {phrase}."}


def tendencies(choices: dict[int, str], tasks: dict[int, dict[str, dict[str, str]]],
               corrected: set[str] = frozenset()) -> list[dict]:
    """"In the example days, you chose less walking every time": an attribute the person leaned the same way on in
    every made-up day where it differed, and at least 3 of them (MIN_DAYS). With five choices and six attributes,
    "mostly" would often be chance (4 of 5 or more by chance alone: about 38%; 5 of 5: about 6%), so it isn't said."""
    out = []
    for attr in ATTRIBUTES:
        if f"choice:{attr}" in corrected:
            continue
        sides = Counter()
        for task, ch in choices.items():
            t = tasks.get(task)
            if t is None or ch not in ("A", "B"):
                continue
            a, b = _level(attr, t[ch]), _level(attr, t["B" if ch == "A" else "A"])
            if a != b:
                sides["low" if a < b else "high"] += 1
        k = sides["low"] + sides["high"]
        if k >= MIN_DAYS and len(sides) == 1:
            side = next(iter(sides))
            words = TEND_WORDS[attr][0 if side == "low" else 1]
            out.append({"id": f"choice:{attr}", "text": f"In the example days, you chose {words} every time.", "k": k})
    out.sort(key=lambda d: -d["k"])
    return [{"id": d["id"], "text": d["text"]} for d in out[:2]]


def without(x: dict[str, float], corrected: set[str]) -> dict[str, float]:
    """A this-or-that day's features, less the attributes the person said we'd read wrong."""
    drop = {f for a in ATTRIBUTES if f"choice:{a}" in corrected for f in ATTR_FEATURES[a]}
    return {k: v for k, v in x.items() if k not in drop}


def choice_features(row: dict[str, str], corrected: set[str]) -> dict[str, float]:
    return without(conjoint_plan_features(row), corrected)


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def items(*, feelings: list[str], swipes: list[tuple[int, str]], places: dict[int, tuple[str, str | None]],
          kinds: list[tuple[str, str, str | None]], phrases: dict[str, str], choices: dict[int, str],
          tasks: dict[int, dict[str, dict[str, str]]], corrected: set[str]) -> list[dict]:
    """The "So far, I've learned…" list, in plain words, from the person's answers only.

    swipes: (item, reaction), latest answer per item; places: item -> (name, phrase);
    kinds: (key, reaction, want); phrases: category key -> phrase.
    """
    out: list[dict] = []
    for f in feelings:
        out.append({"id": f"feeling:{f}", "text": f"You want to feel {f} on a day out."})
    latest = dict(swipes)
    for item, r in latest.items():
        if r == "loved" and item in places and f"place:{item}" not in corrected:
            name, phrase = places[item]
            out.append({"id": f"place:{item}", "text": f"You loved {_mid(name)}" + (f": {phrase}." if phrase else ".")})
    for key, r, want in kinds:
        if f"kind:{key}" in corrected or key not in phrases:
            continue
        if r == "loved":
            out.append({"id": f"kind:{key}", "text": f"You love {phrases[key]}."})
        elif r == "never_tried" and want == "yes":
            out.append({"id": f"kind:{key}", "text": f"You'd like to try {phrases[key]}."})
    out += tendencies(choices, tasks, corrected)
    for item, r in latest.items():
        if r == "didnt_enjoy" and item in places and f"place:{item}" not in corrected:
            out.append({"id": f"place:{item}", "text": f"{places[item][0]} wasn't for you."})
    for key, r, _ in kinds:
        if r == "didnt_enjoy" and key in phrases and f"kind:{key}" not in corrected:
            out.append({"id": f"kind:{key}", "text": f"{_cap(phrases[key])}: not really for you."})
    return out
