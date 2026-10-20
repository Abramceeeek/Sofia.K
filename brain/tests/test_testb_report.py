"""D127: the Test B read-out script (brain/scripts/testb_report.py) on a made-up export."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("testb_report", Path(__file__).parents[1] / "scripts" / "testb_report.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


def _pair(uid, chose_personal, fit_p, fit_g, places, first_id):
    stops = [{"moment_id": m, "rateable": True} for m in places] + [{"moment_id": "m_food#lunch", "lunch": True}]
    intent = {"testb_pair": True, "sunset": "18:00"}
    return [{"id": first_id, "user_id": uid, "kind": "personal", "label": "1", "intent": intent, "stops": stops,
             "status": "chosen" if chose_personal else "not_chosen", "fit_rating": fit_p},
            {"id": first_id + 1, "user_id": uid, "kind": "generic", "label": "2", "intent": intent, "stops": [],
             "status": "not_chosen" if chose_personal else "chosen", "fit_rating": fit_g}]


def test_report_counts_choices_pairs_fits_and_leaves_out_visitors():
    plans = (_pair("a", True, 5, 3, ["m1", "m2", "m3"], 1) + _pair("b", True, 4, 4, ["m1", "m4", "m5"], 3)
             + _pair("c", False, 2, 4, ["m6", "m7", "m8"], 5) + _pair("v", True, 5, 1, ["m1", "m2", "m3"], 7))
    export = {"plans": plans, "cohorts": {"a": "uk", "b": "uk", "c": "uk", "v": "visitor"},
              "day_feedback": [{"plan_id": 1, "worth": "more", "again": True},
                               {"plan_id": 6, "worth": "less", "again": False}],
              "answers": [{"user_id": "a", "question": "best_hour", "input_mode": "voice"},
                          {"user_id": "a", "question": "survey:understood", "text": "5"},
                          {"user_id": "c", "question": "survey:understood", "text": "3"}]}
    out = "\n".join(tr.report(export, overlap=lambda sunset: ["m1", "m2", "m9"]))
    assert "3 UK testers" in out                                   # the visitor is left out
    assert "chose the personal plan: 2 of 3" in out and "3 of 3: not met" in out
    assert "mean +0.00" in out                                     # (+2, 0, -2): ties dropped by the sign test
    assert "rated higher by 1 of the 2" in out
    assert "Overlap" in out and "fully the same for 0 of 3" in out
    assert "personal plans, 1 days" in out and "generic plans, 1 days" in out
    assert "voice: 1 people, mean 5.0" in out and "skipped it: 1 people, mean 3.0" in out


def test_exact_tests():
    assert abs(tr.p_at_least(7, 10) - 0.171875) < 1e-9
    assert tr.sign_test([1, 1, 0, -1]) == (2, 3, tr.p_at_least(2, 3))
