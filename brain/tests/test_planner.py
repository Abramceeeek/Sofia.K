from brain.features import Conditions
from brain.moments import Point
from brain.planner import Candidate, LegWeights, plan_day
from brain.scoring import score_moment
from brain.travel import WalkingEstimate

START = Point(lat=51.5081, lon=-0.1281)   # a made-up start near Charing Cross
LEGS = LegWeights(transfer_15_30=-0.3, transfer_30_plus=-0.7)


def candidates(pop, moments, b=None, cond=None, util=None):
    b = pop.b_pop if b is None else b
    out = []
    for m in moments:
        u = util[m.id] if util and m.id in util else score_moment(pop, b, m, cond)
        out.append(Candidate(m.id, m.start(), m.end(), int(m.duration_min()), tuple(m.windows()), u))
    return out


def check_feasible(plan, cands, day_start, day_end):
    by_id = {c.moment_id: c for c in cands}
    t = day_start
    for s in plan.stops:
        c = by_id[s.moment_id]
        assert s.arrive_min >= t, "stops overlap"
        assert any(lo <= s.arrive_min and s.depart_min <= hi for lo, hi in c.windows), "outside its window"
        assert s.depart_min - s.arrive_min == c.duration_min
        t = s.depart_min
    assert t <= day_end


def test_plan_respects_windows_day_length_and_max_stops(pop, test_moments):
    cands = candidates(pop, test_moments, util={m.id: 0.5 for m in test_moments})
    plan = plan_day(cands, START, 10 * 60, 18 * 60, WalkingEstimate(), LEGS, max_stops=4, time_limit_s=0.5)
    assert plan.status == "ok"
    assert 1 <= len(plan.stops) <= 4
    check_feasible(plan, cands, 600, 1080)
    assert len({s.moment_id for s in plan.stops}) == len(plan.stops)


def test_moments_below_the_floor_are_never_planned(pop, test_moments):
    util = {m.id: 0.5 for m in test_moments}
    util["t_pricey"] = -2.0
    plan = plan_day(candidates(pop, test_moments, util=util), START, 600, 1080, WalkingEstimate(), LEGS,
                    time_limit_s=0.5)
    assert "t_pricey" not in [s.moment_id for s in plan.stops]
    assert "t_pricey" in plan.dropped


def test_best_moment_is_kept_when_only_one_fits(pop, test_moments):
    util = {m.id: 0.0 for m in test_moments}
    util["t_museum"] = 2.0
    # ~57 min walk to the museum plus 90 min inside: fits in 10:00-13:00, not in 10:00-11:40.
    plan = plan_day(candidates(pop, test_moments, util=util), START, 600, 780, WalkingEstimate(), LEGS,
                    max_stops=1, time_limit_s=0.5)
    assert [s.moment_id for s in plan.stops] == ["t_museum"]
    assert plan.peak_moment_id == "t_museum"
    short = plan_day(candidates(pop, test_moments, util=util), START, 600, 700, WalkingEstimate(), LEGS,
                     max_stops=1, time_limit_s=0.5)
    assert "t_museum" not in [s.moment_id for s in short.stops]


def test_window_that_closes_before_the_day_starts_is_skipped(pop, test_moments):
    cands = candidates(pop, test_moments, util={m.id: 0.5 for m in test_moments})
    plan = plan_day(cands, START, 18 * 60, 21 * 60, WalkingEstimate(), LEGS, time_limit_s=0.5)
    assert "t_museum" not in [s.moment_id for s in plan.stops]   # closes 17:30
    check_feasible(plan, cands, 1080, 1260)


def test_peak_end_toggle_finishes_on_a_strong_stop(pop, test_moments):
    util = {"t_view": 1.5, "t_market": 0.2, "t_museum": 0.3, "t_park": 0.2, "t_boat": 0.3, "t_pricey": 0.1}
    cands = candidates(pop, test_moments, util=util)
    off = plan_day(cands, START, 600, 1080, WalkingEstimate(), LEGS, time_limit_s=0.3)
    on = plan_day(cands, START, 600, 1080, WalkingEstimate(), LEGS, peak_end=True, n_end_candidates=3,
                  time_limit_s=0.3)
    assert not off.end_bonus_applied
    assert on.end_bonus_applied
    assert on.stops[-1].moment_id == "t_view"
    check_feasible(on, cands, 600, 1080)


def test_heat_changes_the_plan_inputs(pop, test_moments):
    hot = candidates(pop, test_moments, cond=Conditions(temp_c=32))
    mild = candidates(pop, test_moments, cond=Conditions(temp_c=18))
    u_hot = {c.moment_id: c.utility for c in hot}
    u_mild = {c.moment_id: c.utility for c in mild}
    assert u_hot["t_park"] < u_mild["t_park"]
    assert u_hot["t_museum"] == u_mild["t_museum"]
