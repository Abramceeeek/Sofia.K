"""m260: the evaluation framework keeps predictions and observations apart, imputes nothing, and labels synthetic data."""
import numpy as np

from brain.evaluation import DayOutcome, Outcome, Prediction, evaluate, predictions_from_plans


def _synthetic(n=400, seed=1, informative=True):
    rng = np.random.default_rng(seed)
    preds, outs = [], []
    for i in range(n):
        p = float(rng.uniform(0.2, 0.95))
        good = rng.random() < (p if informative else 0.6)
        preds.append(Prediction(i, f"m{i}", p, "A good match for you" if p >= 0.5 else "Worth a try"))
        if rng.random() < 0.7:                                            # not every stop gets rated
            outs.append(Outcome(i, f"m{i}", 5 if good else 2, would_bring=bool(good)))
    return preds, outs


def test_a_calibrated_model_beats_the_base_rate_and_ranks_well():
    r = evaluate(*_synthetic(), [DayOutcome(1, "about_right", True)], synthetic=True)
    assert r["label"].startswith("SYNTHETIC") and r["synthetic"]
    assert r["brier"] < r["base_rate_brier"] and r["auc"] > 0.65
    assert 0.6 < r["rated_share"] < 0.8                                   # unrated stops are counted, not guessed
    assert {b["band"] for b in r["calibration"]} and r["day_again"] == 1.0


def test_an_uninformative_model_is_caught():
    r = evaluate(*_synthetic(informative=False), synthetic=True)
    assert abs(r["auc"] - 0.5) < 0.1


def test_no_ratings_means_nothing_is_claimed():
    preds, _ = _synthetic(10)
    r = evaluate(preds, [], synthetic=False)
    assert r["rated"] == 0 and "nothing can be said" in r["note"] and "brier" not in r


def test_stored_plans_give_predictions_and_lunch_slots_are_skipped():
    plans = [{"id": 7, "kind": "personal", "stops": [{"moment_id": "m_a", "predicted": 0.4, "match": "A good match for you"},
                                                    {"moment_id": "lunch@1", "predicted": None}]}]
    ps = predictions_from_plans(plans, scale=1.0, cut=0.0)
    assert [p.moment_id for p in ps] == ["m_a"] and 0.5 < ps[0].p_good < 1


def test_the_export_read_out_pairs_ratings_with_stored_predictions_and_says_when_it_is_too_few():   # m264
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("ev", Path(__file__).parents[1] / "scripts" / "evaluate_export.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    export = {"users": [{"id": "u1"}, {"id": "v1"}], "cohorts": {"u1": "london", "v1": "visitor"},
              "plans": [{"id": 1, "user_id": "u1", "kind": "personal",
                         "stops": [{"moment_id": "m_a", "predicted": 0.5, "match": "A good match for you"},
                                   {"moment_id": "lunch@1", "predicted": None}]},
                        {"id": 2, "user_id": "v1", "kind": "personal", "stops": [{"moment_id": "m_b", "predicted": 0.1}]}],
              "ratings": [{"user_id": "u1", "plan_id": 1, "moment_id": "m_a", "rating": 5, "would_bring": True},
                          {"user_id": "v1", "plan_id": 2, "moment_id": "m_b", "rating": 1}],
              "day_feedback": [{"user_id": "u1", "plan_id": 1, "worth": "more", "again": True}]}
    text = "\n".join(ev.read_out(export))
    assert "real ratings" in text and "rated: 1 (100%)" in text and "Exploratory only" in text
    assert "Would do the day again: 100%" in text                          # visitors left out (D116)


def test_ratings_are_split_by_whether_the_stops_facts_had_an_open_question():   # m268 (Abram, m260, priority C)
    preds = [Prediction(1, "a", 0.7), Prediction(1, "b", 0.7), Prediction(1, "c", 0.7), Prediction(2, "a", 0.7)]
    outs = [Outcome(1, "a", 5), Outcome(1, "b", 2), Outcome(1, "c", 4), Outcome(2, "a", 2)]
    r = evaluate(preds, outs, synthetic=True,
                 open_questions={(1, "a"): (), (1, "b"): ("hours",), (2, "a"): ("hours", "season")})
    oq = r["open_questions"]
    assert oq["none"] == {"n": 1, "observed_good": 1.0} and oq["some"] == {"n": 2, "observed_good": 0.0}
    assert oq["by_fact"]["hours"]["n"] == 2 and oq["by_fact"]["season"]["n"] == 1
    assert oq["not_in_catalogue"] == 1                                     # counted apart, never guessed
    assert "open_questions" not in evaluate(preds, outs, synthetic=True)   # only when asked for


def test_the_read_out_judges_each_stop_for_its_own_planned_day():         # m268
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("ev", Path(__file__).parents[1] / "scripts" / "evaluate_export.py")
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    plans = [{"id": 1, "date": "2026-11-21", "stops": [{"moment_id": "m_bm_great_court"},     # hours checked
                                                       {"moment_id": "a_covent_garden_soho"},  # hours as text
                                                       {"moment_id": "m_not_a_card"}]},
             {"id": 2, "date": None, "created_at": "2026-11-20T10:00:00+00:00",
              "stops": [{"moment_id": "a_covent_garden_soho"}]}]
    oq = ev.open_questions(plans)
    assert oq[(1, "m_bm_great_court")] == () and "hours" in oq[(1, "a_covent_garden_soho")]
    assert (1, "m_not_a_card") not in oq and (2, "a_covent_garden_soho") in oq   # created_at when no date
