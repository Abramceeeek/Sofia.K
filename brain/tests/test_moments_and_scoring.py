import csv
from pathlib import Path

import numpy as np

from brain.features import Conditions, conjoint_plan_features, leg_features, moment_features
from brain.moments import load_moments
from brain.scoring import contributions, named_weights, score_moment, update_person, conjoint_observation
from brain.personal import prior_only

from conftest import DATA

REPO = Path(__file__).resolve().parents[2]


def test_seed_moment_loads_and_is_not_plannable_until_the_gaps_are_filled():
    moments = {m.id: m for m in load_moments(DATA / "moments")}
    seed = moments["m_southken_nhm_reveal"]
    missing = seed.missing_for_planning()
    assert "approach.start_point" in missing
    assert "best_time.time_of_day" in missing
    assert "features.place.crowds" in missing
    assert seed.features.moment["contrast_reveal"] == 2
    assert not seed.plannable()


def test_complete_test_moment_is_plannable(test_moments):
    assert all(m.plannable() for m in test_moments)
    assert test_moments[2].windows() == [(600, 1050)]
    assert test_moments[2].duration_min() == 90


def test_transfer_hinges_are_thresholds_not_lines():
    assert leg_features(10) == {"transfer_15_30": 0.0, "transfer_30_plus": 0.0}
    assert leg_features(30) == {"transfer_15_30": 1.0, "transfer_30_plus": 0.0}
    assert leg_features(50) == {"transfer_15_30": 1.0, "transfer_30_plus": 1.0}


def test_heat_only_bites_outdoors(pop, test_moments):
    view, museum = test_moments[0], test_moments[2]
    hot, mild = Conditions(temp_c=31), Conditions(temp_c=20)
    b = pop.b_pop
    assert score_moment(pop, b, view, hot) < score_moment(pop, b, view, mild)
    assert score_moment(pop, b, museum, hot) == score_moment(pop, b, museum, mild)


def test_conjoint_design_copy_matches_validation_file():
    assert (DATA / "conjoint_design.csv").read_text() == (REPO / "validation/conjoint/design.csv").read_text()


def test_conjoint_rows_map_onto_model_features(pop):
    rows = list(csv.DictReader(open(DATA / "conjoint_design.csv", encoding="utf-8")))
    assert len(rows) == 20
    for r in rows:
        x = conjoint_plan_features(r)
        assert set(x) <= set(pop.names)
    by = {(r["task"], r["plan"]): r for r in rows}
    for r in rows:   # D95: the weather levels map onto cold_outdoor / rain_outdoor, mild and dry is the baseline
        x = conjoint_plan_features(r)
        assert x.get("cold_outdoor", 0.0) == (1.0 if r["weather"].startswith("cold") else 0.0)
        assert x.get("rain_outdoor", 0.0) == (1.0 if r["weather"].startswith("rainy") else 0.0)
        assert "hot_outdoor" not in x
    rainy = next(r for r in rows if r["weather"].startswith("rainy"))
    x = conjoint_plan_features(rainy)
    assert x["rain_outdoor"] == 1.0 and set(x) == {"transfer_15_30", "transfer_30_plus", "rain_outdoor", "packed_pace",
                                                   "crowds", "cost_per_10gbp", "long_walk"}
    assert len({r["weather"] for r in rows}) == 3 and len(by) == 20


def test_named_weights_start_unsure_and_become_confident(pop):
    prior = prior_only(pop.delta_prior_sd)
    w = {n.name: n for n in named_weights(pop, prior)}
    assert w["history_culture"].direction == "unsure"
    assert w["heat_walking"].direction == "population"
    # personal since D95; rain's prior (-1.0, sd 0.75) is already "confident", so the read-back flags it as the prior's
    assert w["rain_outdoor"].direction == "dislikes" and w["cold_outdoor"].direction == "unsure"
    from brain.testb import readback_lines
    rain_line = next(l for l in readback_lines(pop, prior) if l.startswith("rain outdoors"))
    assert rain_line.endswith("(mostly the population prior, not their answers)")
    # 10 identical choices for the plan without the hot hour
    xa, xb = {"hot_outdoor": 0.0}, {"hot_outdoor": 1.0}
    post = update_person(pop, [conjoint_observation(pop, xa, xb, chose_a=True) for _ in range(10)])
    w = {n.name: n for n in named_weights(pop, post)}
    assert w["hot_outdoor"].weight < pop.spec("hot_outdoor").mean
    assert w["hot_outdoor"].direction == "dislikes"


def test_contributions_name_the_drivers(pop, test_moments):
    x = moment_features(test_moments[5])  # expensive and crowded
    top = contributions(pop, pop.b_pop, x, top=2)
    assert [t["feature"] for t in top] == ["cost_per_10gbp", "crowds"]
    assert all(t["contribution"] < 0 for t in top)


def test_moment_template_is_a_complete_valid_record():
    from brain.moments import load_moment_file
    m = load_moment_file(DATA / "moment_template.yaml")
    assert m.missing_for_planning() == []


def test_value_in_pounds_ranks_like_the_score(pop, test_moments):
    # D88: "worth about £V to you"; ranking by V − price is the same as ranking by S
    from brain.scoring import value_gbp
    rng = np.random.default_rng(5)
    for _ in range(5):
        delta = rng.normal(0, 0.6, len(pop.personal_names))
        b = pop.b_person(delta)
        assert b[pop.names.index("cost_per_10gbp")] < 0          # the sign never flips
        s = [score_moment(pop, b, m) for m in test_moments]
        net = [value_gbp(pop, b, m) - (m.cost_gbp or 0.0) for m in test_moments]
        assert np.argsort(s).tolist() == np.argsort(net).tolist()
        scale = -b[pop.names.index("cost_per_10gbp")] / 10.0
        assert np.allclose(s, [scale * n for n in net])


def test_cost_weight_reads_as_stronger_or_weaker_not_as_a_sign(pop):
    from brain.testb import readback_lines
    w = {n.name: n for n in named_weights(pop, prior_only(pop.delta_prior_sd))}
    assert w["cost_per_10gbp"].direction == "unsure" and w["cost_per_10gbp"].p_negative == 1.0
    # many choices of the cheaper plan: more cost-sensitive than most people
    x_cheap = {"cost_per_10gbp": 0.0}
    x_dear = {"cost_per_10gbp": 2.0}
    post = update_person(pop, [conjoint_observation(pop, x_cheap, x_dear, True) for _ in range(30)])
    w = {n.name: n for n in named_weights(pop, post)}
    assert w["cost_per_10gbp"].direction == "stronger"
    assert w["cost_per_10gbp"].weight < pop.spec("cost_per_10gbp").mean
    assert any("matter more to them than to most people" in l for l in readback_lines(pop, post))


def test_days_keep_weekday_only_places_out_of_weekend_plans(test_moments):
    m = test_moments[2].model_copy(deep=True)
    assert m.open_on("sat") and m.open_on(None)          # no days listed: every day
    m.best_time.days = ["mon", "tue", "wed", "thu", "fri"]
    assert m.open_on("Mon") and not m.open_on("sat") and m.open_on(None)
    assert m.plannable()
    m.best_time.days = ["weekdays"]
    assert "best_time.days (format)" in m.missing_for_planning()


def test_match_words_follow_the_rating_models_chance_of_good(pop):
    """D127: words instead of "worth about £V", from P(rating >= Good) = F(u - c_2|3) with c = -0.75."""
    from brain.dayplan import match_label
    assert match_label(pop, 1.0) == "A strong match for you"     # F(1.75) = 0.85
    assert match_label(pop, -0.5) == "A good match for you"      # F(0.25) = 0.56
    assert match_label(pop, -1.5) == "Worth a try"               # F(-0.75) = 0.32


def test_about_you_answers_lean_the_weights_and_neutral_ones_say_nothing(pop):
    """D127: "Who do you usually go with?" and "How active?" now count, as stated leanings like the feelings."""
    from brain.reasons import about_you_observation
    assert about_you_observation(pop, "company", "solo") is None
    assert about_you_observation(pop, "activity", "medium") is None
    assert about_you_observation(pop, "activity", None) is None
    i_walk = pop.personal_names.index("walking_effort")
    i_social = pop.personal_names.index("social_pull")
    gentle = update_person(pop, [about_you_observation(pop, "activity", "gentle")])
    full = update_person(pop, [about_you_observation(pop, "activity", "full_on")])
    friends = update_person(pop, [about_you_observation(pop, "company", "friends")])
    assert gentle.mean[i_walk] < 0 < full.mean[i_walk]
    assert friends.mean[i_social] > 0
