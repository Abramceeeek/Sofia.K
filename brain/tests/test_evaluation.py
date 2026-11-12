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
