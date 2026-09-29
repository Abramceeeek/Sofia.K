import math

import numpy as np
import yaml

from brain.dayplan import load_app_items, load_swipe_items
from brain.moments import MOMENT_TAGS, PLACE_TAGS
from brain.personal import Observation, loglik_terms
from brain.swipeinfo import SubsetScore, choose, ordered_info

from conftest import DATA


def test_ordered_info_is_the_expected_negative_second_derivative():
    cut = (-1.0, 1.0)
    for eta in (-2.0, 0.0, 0.7):
        c = (-math.inf, *cut, math.inf)
        probs = [1 / (1 + math.exp(-(c[k + 1] - eta))) - 1 / (1 + math.exp(-(c[k] - eta))) for k in range(3)]
        expected = sum(p * -loglik_terms(eta, Observation(np.zeros(1), k, cutpoints=cut))[2]
                       for k, p in enumerate(probs))
        assert math.isclose(ordered_info(eta, cut), expected, rel_tol=1e-9)


def test_choose_prefers_places_with_cards_only_within_the_tolerance():
    ranked = [SubsetScore((1, 2), 1.000, 0.0), SubsetScore((1, 3), 1.005, 0.0), SubsetScore((3, 4), 1.2, 0.0)]
    assert choose(ranked, with_cards={3}).items == (1, 3)          # 0.5% worse, one more place with cards
    assert choose(ranked, with_cards={4}).items == (1, 2)          # (3, 4) is 20% worse: information wins


def test_the_apps_places_are_locked_items_and_cover_every_taste_tag():
    """D110, D112: 6 before the first plan (each tag on at least one) and 4 later (each tag on two of the 10),
    all from the locked 16, so Test A answers stay comparable."""
    upfront = load_app_items(DATA / "swipe_items.yaml")
    later = load_app_items(DATA / "swipe_items.yaml", later=True)
    swipe = load_swipe_items(DATA / "swipe_items.yaml")
    assert len(upfront) == 6 and len(later) == 4 and not set(upfront) & set(later)
    assert set(upfront) | set(later) <= set(swipe)
    with open(DATA / "swipe_items.yaml", encoding="utf-8") as f:
        assert len(yaml.safe_load(f)["items"]) == 16
    for tag in PLACE_TAGS + MOMENT_TAGS:
        assert any((swipe[i].tag(tag) or 0) >= 1 for i in upfront), tag
        assert sum(1 for i in upfront + later if (swipe[i].tag(tag) or 0) >= 1) >= 2, tag


def test_exchange_search_finds_the_exhaustive_best_on_the_locked_16():
    """D111: the all-30 choice uses an exchange search; on the 16, where every subset can be checked, it must agree."""
    from brain.moments import load_moments
    from brain.population import load_population
    from brain.swipeinfo import best_subsets, search_subsets
    from brain.testb import load_tasks
    pop = load_population(DATA / "priors.yaml")
    swipe = load_swipe_items(DATA / "swipe_items.yaml")
    tasks = load_tasks(DATA / "conjoint_design.csv")
    cards = [m for m in load_moments(DATA / "moments") if m.status == "ready"]
    exhaustive = best_subsets(pop, swipe, tasks, cards, 10)[0]
    best, _ = search_subsets(pop, swipe, tasks, cards, 10, restarts=6)
    assert best.items == exhaustive.items and abs(best.v - exhaustive.v) < 1e-9
