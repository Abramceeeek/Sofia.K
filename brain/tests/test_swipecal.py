import math

import numpy as np

from brain.calibration import Place
from brain.moments import Moment
from brain.personal import _F
from brain.population import load_population
from brain.scoring import SWIPE_LEVEL, score_moment, swipe_observation
from brain.swipecal import familiarity, fit_cutpoints, place_x

from conftest import DATA

POP = load_population(DATA / "priors.yaml")


def _place(i: int, tags: dict[str, int], item: int | None = None) -> Place:
    return Place(f"p{i}", f"Place {i}", "", "", "", tags, item)


def test_the_swiping_level_is_on_every_swipe_and_never_in_a_plan_score():
    m = Moment.model_validate({"id": "m", "title": "M", "place": {"name": "M"},
                               "features": {"place": {"food": 2}, "moment": {"awe": 1}}})
    x = swipe_observation(POP, m, "loved").x
    assert x[POP.names.index(SWIPE_LEVEL)] == 1.0
    delta = np.zeros(len(POP.personal_names))
    delta[POP.personal_names.index(SWIPE_LEVEL)] = 3.0     # someone who loves everything
    assert score_moment(POP, POP.b_person(delta), m) == score_moment(POP, POP.b_pop, m)


def test_familiarity_is_shrunk_toward_the_pooled_rate():
    places = [_place(1, {}, 1), _place(2, {}, 2)]
    rows = [(f"b{k}", "p1", "loved") for k in range(4)] + [(f"b{k}", "p2", "not_been") for k in range(4)]
    fam = familiarity(rows, places, prior_n=4)
    assert fam["p1"] == (round((4 + 4 * 0.5) / 8, 3), 4, 4)    # pooled rate 0.5: 4/4 been becomes 0.75
    assert fam["p2"] == (round((0 + 4 * 0.5) / 8, 3), 0, 4)


def test_fit_recovers_cutpoints_and_the_level_spread_from_simulated_swipes():
    rng = np.random.default_rng(3)
    tags = ("food", "green_nature", "history_culture", "awe", "crowds", "movement_views")
    places = [_place(i, {t: int(rng.integers(0, 3)) for t in tags}) for i in range(12)]
    c, sigma = (-3.0, 0.0), 1.2
    k = POP.personal_names.index(SWIPE_LEVEL)
    sd = POP.delta_prior_sd.copy()
    sd[k] = sigma
    rows = []
    for person in range(40):
        b = POP.b_person(rng.normal(0.0, sd))
        for p in places:
            eta = float(place_x(POP, p) @ b)
            u = eta + rng.logistic()
            rows.append((f"b{person}", p.id, ("didnt", "fine", "loved")[int(np.searchsorted(c, u))]))
    fit = fit_cutpoints(rows, places, POP)
    assert abs(fit.cutpoints[0] - c[0]) < 3 * fit.se[0] and abs(fit.cutpoints[1] - c[1]) < 3 * fit.se[1]
    assert abs(fit.sigma - sigma) < 3 * fit.se[2]
    assert fit.people == 40 and fit.answers == 480
    assert math.isclose(sum(fit.shares), 1.0, abs_tol=0.01)
