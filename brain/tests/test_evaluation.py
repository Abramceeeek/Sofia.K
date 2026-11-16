"""m260: the evaluation framework keeps predictions and observations apart, imputes nothing, and labels synthetic data."""
import numpy as np

from brain.evaluation import DayOutcome, Outcome, Prediction, evaluate, predictions_from_plans
from test_api import client  # noqa: F401  (the client fixture)


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


def test_the_internal_bands_are_checked_on_ratings_and_use_the_planners_own_lines():
    """m275 (Abram, 12 Nov): no match words or chances are shown; the bands behind the old words are what real ratings
    must support before any wording of a chance comes back."""
    from brain import dayplan, evaluation
    assert (evaluation.STRONG_LINE, evaluation.GOOD_LINE) == (dayplan.MATCH_STRONG, dayplan.MATCH_GOOD)
    r = evaluate(*_synthetic(), synthetic=True)
    bands = r["match_bands"]
    assert set(bands) == {"strong", "good", "other"} and sum(v["n"] for v in bands.values()) == r["rated"]
    assert bands["strong"]["observed_good"] > bands["other"]["observed_good"]   # an informative (synthetic) model


def test_ratings_from_plans_that_kept_no_prediction_are_counted_and_checked_by_their_words():
    """m276: plans made before m276 (the frozen round's included) kept no prediction. Their ratings are never reported
    as "no rated stops": they're counted, and checked by the words shown with them (D127's bands)."""
    from brain.evaluation import shown_from_plans
    plans = [{"id": 1, "kind": "personal", "stops": [{"moment_id": "a", "match": "A strong match for you"},
                                                    {"moment_id": "b", "match": "Worth a try"},
                                                    {"moment_id": "lunch@1", "match": None}]}]
    outs = [Outcome(1, "a", 5), Outcome(1, "b", 2), Outcome(1, "lunch@1", 4)]
    r = evaluate(predictions_from_plans(plans, 1.0, 0.0), outs, synthetic=False, shown=shown_from_plans(plans))
    assert r["rated"] == 0 and r["rated_without_prediction"] == 3 and "kept no prediction" in r["note"]
    assert r["match_words"] == {"A strong match for you": {"n": 1, "observed_good": 1.0},
                                "Worth a try": {"n": 1, "observed_good": 0.0}}
    assert "brier" not in r                                               # nothing is imputed
    assert evaluate([], [], synthetic=False)["note"].startswith("No rated stops yet")


def test_the_milestone_is_how_much_the_person_had_told_us_when_the_plan_was_made():
    """Abram, 12 Nov (part 3B): after onboarding, the first rating, 2 days out, 5 days out, 20 ratings."""
    from brain.evaluation import MILESTONES, milestone
    assert milestone(0, 0) == MILESTONES[0] and milestone(1, 1) == MILESTONES[1] and milestone(7, 1) == MILESTONES[1]
    assert milestone(3, 2) == MILESTONES[2] and milestone(9, 5) == MILESTONES[3]
    assert milestone(20, 3) == MILESTONES[4]                       # twenty ratings before five days out: the further


def test_learning_by_milestone_judges_each_rating_by_its_own_plans_prediction():
    """SYNTHETIC timings and predictions, to test the bookkeeping only: never evidence about real people."""
    from brain.evaluation import PlanMade, learning_by_milestone
    made = {1: PlanMade("u", "2026-11-01T09:00:00+00:00"),    # before any rating: after onboarding
            2: PlanMade("u", "2026-11-03T09:00:00+00:00"),    # after ratings on 1 and 2 Nov: 2 days out
            3: PlanMade("w", "2026-11-03T09:00:00+00:00")}    # w rated once, the same morning: the first rating
    rated_at = {"u": ["2026-11-01T15:00:00+00:00", "2026-11-02T23:30:00+00:00", "2026-11-03T15:00:00+00:00"],
                "w": ["2026-11-03T08:00:00+00:00"]}           # 23:30 UTC on 2 Nov is still 2 Nov in London (GMT)
    preds = [Prediction(1, "a", 0.8), Prediction(2, "b", 0.6), Prediction(3, "c", 0.3)]
    outs = [Outcome(1, "a", 5), Outcome(2, "b", 2), Outcome(3, "c", 2), Outcome(9, "z", 4)]
    r = learning_by_milestone(preds, outs, made, rated_at, {(1, "a"): 0.6, (2, "b"): 0.6}, synthetic=True)
    rows = {x["milestone"]: x for x in r["rows"]}
    assert r["label"].startswith("SYNTHETIC") and r["rated_without_prediction"] == 1   # plan 9: counted, not guessed
    assert rows["after onboarding"]["n"] == 1 and rows["after onboarding"]["gain"] == round(0.16 - 0.04, 4)
    assert rows["after 2 days out"]["n"] == 1 and rows["after 2 days out"]["gain"] == 0.0
    assert rows["after the first rating"]["n"] == 1 and "gain" not in rows["after the first rating"]   # no baseline
    assert rows["after 20 ratings"] == {"milestone": "after 20 ratings", "n": 0, "people": 0}
    assert all(x["exploratory"] for x in r["rows"] if x["n"])


def test_the_milestone_read_out_runs_on_a_real_export_and_says_how_little_it_can_claim(client):
    """End to end on the Brain: a plan after onboarding, a rating, then a plan after the first rating."""
    import importlib.util
    from pathlib import Path
    from test_api import ADMIN, install
    spec = importlib.util.spec_from_file_location("lm", Path(__file__).parents[1] / "scripts" / "learning_milestones.py")
    lm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lm)
    h, _ = install(client)
    day = {"start": {"lat": 51.507819, "lon": -0.126137}, "start_name": "Charing Cross station", "date": "2026-10-31"}
    first = client.post("/v1/me/plans", headers=h, json=day).json()
    stop = next(s for s in first["stops"] if s["rateable"])
    assert client.post("/v1/me/ratings", headers=h, json={"plan_id": first["id"], "moment_id": stop["moment_id"],
                                                          "rating": 5}).status_code == 201
    second = client.post("/v1/me/plans", headers=h, json=day).json()
    stop2 = next(s for s in second["stops"] if s["rateable"])
    client.post("/v1/me/ratings", headers=h, json={"plan_id": second["id"], "moment_id": stop2["moment_id"], "rating": 2})
    text = "\n".join(lm.read_out(client.get("/v1/admin/export", headers=ADMIN).json()))
    assert "real ratings" in text and "exploratory" in text
    assert "after onboarding (exploratory): 1 rated stops from 1 people" in text
    assert "after the first rating (exploratory): 1 rated stops from 1 people" in text
    assert "after 20 ratings: no rated stops yet." in text and "gain" in text
