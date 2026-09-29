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


def test_the_apps_places_are_locked_items_and_cover_every_taste_tag_twice():
    """D110: the 10 are a subset of the locked 16 (so Test A answers stay comparable) and keep each tag learnable."""
    items = load_app_items(DATA / "swipe_items.yaml")
    swipe = load_swipe_items(DATA / "swipe_items.yaml")
    assert len(items) == 10 and set(items) <= set(swipe)
    with open(DATA / "swipe_items.yaml", encoding="utf-8") as f:
        assert len(yaml.safe_load(f)["items"]) == 16
    for tag in PLACE_TAGS + MOMENT_TAGS:
        assert sum(1 for i in items if (swipe[i].tag(tag) or 0) >= 1) >= 2, tag
