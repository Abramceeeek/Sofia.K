"""WS7: the benchmark's own checks are tested, so a clean report means the plans are clean, not that the checks are
blind. Synthetic travellers only (scripts/benchmark_planner.py)."""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import benchmark_planner as bp  # noqa: E402
from brain.dayplan import Block  # noqa: E402

CTX = bp.load_context(0.3)
BY_ID = CTX["by_id"]
PROF = next(p for p in bp.PROFILES if p.name == "museums_architecture")


def _brief(name, **kw):
    sc = next(s for s in bp.SCENARIOS if s.name == name)
    return replace(bp.brief_for(sc, PROF, 0.3), **kw)


def _open_card(day="sat"):
    """A card open on `day` with a daytime window, and one closed then (if any)."""
    open_ = next(m for m in CTX["moments"] if m.plannable() and m.open_on(day) and not m.meal
                 and any(lo <= 660 and hi >= 780 for lo, hi in m.windows()) and m.kind == "moment"
                 and bp.moment_features(m).get("history_culture", 0) < 1)
    closed = next((m for m in CTX["moments"] if m.plannable() and not m.open_on(day)), None)
    return open_, closed


def test_a_clean_plan_has_no_violations():
    m, _ = _open_card()
    d = int(round(m.duration_min()))
    stops = [bp.Stop(m.id, 660, 660 + d, 10)]
    assert bp.violations(stops, _brief("full_day_sat"), BY_ID, 15.0) == []


def test_the_checks_catch_overlaps_hours_closed_days_and_budget():
    m, closed = _open_card()
    d = int(round(m.duration_min()))
    brief = _brief("full_day_sat", budget_gbp=0.0)
    bad = bp.violations([bp.Stop(m.id, 660, 660 + d, 0), bp.Stop("lunch@x", 660 + d - 5, 705 + d, 0)], brief, BY_ID, 15.0)
    assert any(v.startswith("overlap") for v in bad) and any(v.startswith("over budget") for v in bad)
    assert any(v.startswith("outside its hours") for v in bp.violations([bp.Stop(m.id, 120, 120 + d, 0)],
                                                                          _brief("full_day_sat", start_time="01:00"),
                                                                          BY_ID, 15.0))
    if closed is not None:
        assert any(v.startswith("closed that day") for v in bp.violations(
            [bp.Stop(closed.id, 660, 661, 0)], _brief("full_day_sat"), BY_ID, 15.0))


def test_the_checks_catch_history_back_to_back_but_a_block_or_lunch_between_breaks_it():
    hist = [m for m in CTX["moments"] if m.plannable() and bp.moment_features(m).get("history_culture", 0) >= 1][:2]
    a, b = (bp.Stop(m.id, 600 + 100 * i, 640 + 100 * i, 0) for i, m in enumerate(hist))
    assert "history-and-culture back to back" in bp.violations([a, b], _brief("full_day_sat"), BY_ID, 15.0)
    brk = bp.Stop("mine0@x", 645, 695, 0)
    brief = _brief("full_day_sat", mine=(Block("plans", 650, 690),))
    assert "history-and-culture back to back" not in bp.violations([a, brk, b], brief, BY_ID, 15.0)


def test_the_checks_catch_a_block_that_is_not_kept():
    m, _ = _open_card()
    brief = _brief("plans_near_14")
    d = int(round(m.duration_min()))
    out = bp.violations([bp.Stop(m.id, 830, 830 + d, 0)], brief, BY_ID, 15.0)
    assert "block 0 not kept" in out and any(v.startswith("stop inside block") for v in out)


def test_greedy_keeps_the_hard_rules_lunch_and_blocks():
    pop = CTX["pop"]
    b = pop.b_person(bp.delta_of(pop, PROF))
    for name in ("full_day_sat", "plans_unknown_lunch", "rain_sat"):
        brief = _brief(name)
        usable = [m for m in CTX["moments"] if m.plannable() and m.open_on(brief.weekday) and not m.meal]
        stops = bp.greedy_plan(pop, b, brief, usable, CTX["travel"])
        assert bp.violations(stops, brief, BY_ID, 15.0) == [], name
    stops = bp.greedy_plan(pop, b, _brief("full_day_sat"), usable, CTX["travel"])
    assert any(s.id.startswith("lunch@") for s in stops)


def test_one_traveller_one_day_end_to_end():
    pi = bp.PROFILES.index(PROF)
    si = next(i for i, s in enumerate(bp.SCENARIOS) if s.name == "testb_sat")
    rows = bp.run_one((pi, si))
    assert [r["plan"] for r in rows] == ["personal_known", "personal_onboarded", "personal_onboarded", "no_answers",
                                         "greedy"]
    assert all(r["violations"] == [] for r in rows)
    known, none = rows[0], rows[3]
    assert known["value"] >= none["value"]   # told the tastes exactly, the planner does at least as well as knowing none


def test_the_profiles_are_on_the_models_own_features():
    pop = CTX["pop"]
    for p in bp.PROFILES:
        bp.delta_of(pop, p)   # raises on a feature the model doesn't have
