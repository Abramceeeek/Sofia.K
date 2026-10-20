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


def test_the_floor_never_leaves_a_day_short_of_its_places(pop, test_moments):
    """m187: when too few cards clear the floor, the person's own best ones fill the day; when enough do, a card
    below the floor still stays out."""
    low = {m.id: -1.5 - 0.1 * i for i, m in enumerate(test_moments)}       # every card below "Good"
    plan = plan_day(candidates(pop, test_moments, util=low), START, 600, 1080, WalkingEstimate(), LEGS,
                    max_stops=2, min_stops=2, time_limit_s=0.5)
    assert len(plan.stops) == 2 and plan.status == "ok"
    assert {s.moment_id for s in plan.stops} <= {m.id for m in test_moments[:4]}   # among the best of them
    fine = {m.id: 0.5 for m in test_moments}
    fine["t_pricey"] = -2.0
    plan = plan_day(candidates(pop, test_moments, util=fine), START, 600, 1080, WalkingEstimate(), LEGS,
                    max_stops=2, min_stops=2, time_limit_s=0.5)
    assert "t_pricey" not in [s.moment_id for s in plan.stops]


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


def test_variants_of_one_moment_are_never_planned_together(pop, test_moments):
    from dataclasses import replace
    cands = candidates(pop, test_moments, util={m.id: 1.0 for m in test_moments})
    free = plan_day(cands, START, 9 * 60, 21 * 60, WalkingEstimate(), LEGS, max_stops=6, time_limit_s=0.5)
    both = [s.moment_id for s in free.stops][:2]
    assert len(both) == 2, "control: without a group, both stops fit"
    grouped = [replace(c, group="boat") if c.moment_id in both else c for c in cands]
    plan = plan_day(grouped, START, 9 * 60, 21 * 60, WalkingEstimate(), LEGS, max_stops=6, time_limit_s=0.5)
    assert len(set(both) & {s.moment_id for s in plan.stops}) <= 1


def test_one_area_vibe_a_day_and_never_the_peak(pop, test_moments):
    from dataclasses import replace
    cands = candidates(pop, test_moments, util={m.id: 0.5 for m in test_moments})
    areas = {cands[0].moment_id, cands[1].moment_id}
    cands = [replace(c, kind="area", utility=2.0) if c.moment_id in areas else c for c in cands]
    plan = plan_day(cands, START, 9 * 60, 21 * 60, WalkingEstimate(), LEGS, max_stops=6, time_limit_s=0.5)
    planned = {s.moment_id for s in plan.stops}
    assert len(planned & areas) == 1
    assert plan.peak_moment_id not in areas


def test_spread_to_end_moves_stops_later_inside_their_windows():
    # D97: a pair of Test B plans must end within 30 min of each other
    from brain.planner import DayPlan, PlannedStop, spread_to_end
    p = Point(lat=51.5, lon=-0.1)
    a = Candidate("a", p, p, 60, ((600, 720),), 1.0)            # 10:00-12:00 only
    b = Candidate("b", p, p, 60, ((600, 1080),), 1.0)           # 10:00-18:00
    plan = DayPlan([PlannedStop("a", 600, 660, 10, 1.0, 0.0), PlannedStop("b", 680, 740, 20, 1.0, 0.0)], 2.0, "a", False)
    assert spread_to_end(plan, {"a": a, "b": b}, min_end=840, day_end=900)   # must end by 14:00 or later
    sa, sb = plan.stops
    assert sa.arrive_min <= 720 - 60                      # "a" still fits its window
    assert sb.arrive_min >= sa.depart_min + 20            # travel time kept
    assert sb.depart_min >= 840 and sb.depart_min <= 900
    # nothing to do when the plan already ends late enough
    assert spread_to_end(plan, {"a": a, "b": b}, min_end=700, day_end=900)



def test_buffer_leaves_breathing_space_between_stops():
    """D100: a few minutes between stops; the travel minutes shown stay the estimate."""
    from brain.moments import Point
    from brain.planner import Candidate, LegWeights, plan_day
    from brain.travel import WalkingEstimate
    a, b = Point(lat=51.5081, lon=-0.1281), Point(lat=51.5095, lon=-0.1281)
    cands = [Candidate("x", a, a, 30, ((600, 900),), 1.0), Candidate("y", b, b, 30, ((600, 900),), 1.0)]
    plain = plan_day(cands, a, 600, 900, WalkingEstimate(), LegWeights(0, 0), max_stops=2, min_stops=2, time_limit_s=0.3)
    buf = plan_day(cands, a, 600, 900, WalkingEstimate(), LegWeights(0, 0), max_stops=2, min_stops=2, time_limit_s=0.3,
                   buffer_walk_min=5, buffer_transit_min=10)
    gap = lambda p: p.stops[1].arrive_min - p.stops[0].depart_min
    assert gap(buf) >= gap(plain) + 5 and buf.stops[1].travel_min == plain.stops[1].travel_min


def test_extend_dwell_lengthens_stays_where_the_day_has_room():
    """D102: longer stays for a relaxed person, moving later stops back, never past a window or the day's end."""
    from brain.moments import Point
    from brain.planner import Candidate, DayPlan, PlannedStop, extend_dwell
    p = Point(lat=51.5, lon=-0.1)
    cands = {"a": Candidate("a", p, p, 30, ((600, 700),), 1.0), "b": Candidate("b", p, p, 30, ((600, 760),), 1.0)}
    plan = DayPlan([PlannedStop("a", 600, 630, 0, 1.0, 0.0), PlannedStop("b", 640, 670, 5, 1.0, 0.0)], 2.0, "a", False)
    extend_dwell(plan, cands, {"a": 50, "b": 60}, latest_end=720)
    a, b = plan.stops
    assert a.depart_min - a.arrive_min == 50                     # 20 more minutes at a
    assert b.arrive_min == 660 and b.depart_min <= 720           # b moved back by 20, then lengthened to the end
    assert b.depart_min - b.arrive_min == 60
