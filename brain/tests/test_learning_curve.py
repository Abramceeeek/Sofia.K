"""The audit's learning-curve benchmark (scripts/learning_curve.py) runs, and meets the same people in every arm."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import learning_curve as lc  # noqa: E402


def test_every_arm_meets_the_same_people_with_the_same_onboarding_answers():
    app, random_days = lc.run(4, 1, 0.0, "app"), lc.run(4, 1, 0.0, "random")
    assert [r["rated"] for r in app] == [0, 4]
    assert app[0] == random_days[0]                      # before any rating the two arms are the same people
    assert all(-1.0 <= r["rho"] <= 1.0 and 0 <= r["top"] <= 8 for r in app + random_days)


def test_a_taste_the_tags_cannot_describe_changes_the_truth_not_the_answers_before_rating():
    plain, own = lc.run(4, 0, 0.0, "app"), lc.run(4, 0, 0.75, "app")
    assert plain[0]["n"] == own[0]["n"] == 4 and plain[0]["rho"] != own[0]["rho"]


def test_the_proposed_rating_level_sees_the_same_people_and_answers_as_today_s_model():
    today, proposed = lc.run(4, 1, 0.0, "random", level_sd=1.0), lc.run(4, 1, 0.0, "random", level_sd=1.0, fit_level=True)
    assert today[0]["rho"] == proposed[0]["rho"]          # before any rating the extra term changes nothing
    assert today[1]["n"] == proposed[1]["n"] == 4
