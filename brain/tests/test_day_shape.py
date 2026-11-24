"""m331 (Abram, 24 Nov: "make gentle travellers' days geographically coherent"; regression tests for gentle
travellers given strenuous activities, extra stops with disproportionate travel, people sent across London without
need, loved places lost to journey costs, and extra stops that spoil the end of the day). Small made-up days, so the
solver's answer is certain, then one real London day."""
import importlib.util
from pathlib import Path

from brain import dayplan
from brain.moments import Point
from brain.planner import PACE_TRAVEL, Candidate, LegWeights, plan_day
from brain.travel import WalkingEstimate

START = Point(lat=51.5081, lon=-0.1281)
NEAR = Point(lat=51.5111, lon=-0.1281)    # about 6 min on foot
FAR = Point(lat=51.5281, lon=-0.1281)     # about 40 min on foot
DAY = ((600, 1080),)
PLAIN = LegWeights(-0.3, -0.7)
GENTLE = LegWeights(-0.3, -0.7, 0.0, *PACE_TRAVEL["gentle"])


def _one(cands, legs):
    plan = plan_day(cands, START, 600, 1080, WalkingEstimate(), legs, max_stops=1, time_limit_s=0.5)
    return [s.moment_id for s in plan.stops]


def test_a_gentle_pace_keeps_the_day_near_unless_the_far_place_is_loved():
    near = Candidate("near", NEAR, NEAR, 60, DAY, 0.0)
    far = Candidate("far", FAR, FAR, 60, DAY, 0.8)            # a little better, 40 min away
    assert _one([near, far], PLAIN) == ["far"]                 # worth the walk at an ordinary pace
    assert _one([near, far], GENTLE) == ["near"]               # not across town on a gentle day
    loved = Candidate("far", FAR, FAR, 60, DAY, 0.8, loved=True)
    assert _one([near, loved], GENTLE) == ["far"]              # unless they said they loved it


def test_moving_the_whole_day_later_never_counts_as_filling_it():
    """The solver once started days an hour late so they ended "on time": the same day, with the free hour moved
    from the evening to the morning."""
    only = Candidate("x", NEAR, NEAR, 120, DAY, 0.5)
    plan = plan_day([only], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=1, time_limit_s=0.5)
    first = plan.stops[0]
    assert first.arrive_min - first.travel_min <= 600 + 5     # sets off at the day's start


def test_an_extra_place_is_a_genuine_match_or_nothing():
    """Extra places (dayplan's Brief.extra) never lower the floor: no place below it joins a day just to fill it."""
    near = lambda k: Point(lat=51.5081 + 0.001 * k, lon=-0.1281)
    good = [Candidate(f"good{k}", near(k), near(k), 45, DAY, 0.5) for k in range(2)]
    poor = [Candidate(f"poor{k}", near(k + 2), near(k + 2), 45, DAY, -2.0) for k in range(2)]
    args = dict(max_stops=4, min_stops=4, time_limit_s=0.5)
    extra = plan_day(good + poor, START, 600, 1080, WalkingEstimate(), PLAIN, relax_floor=False, retry_min=False,
                     **args)
    assert {s.moment_id for s in extra.stops} == {"good0", "good1"}
    usual = plan_day(good + poor, START, 600, 1080, WalkingEstimate(), PLAIN, **args)   # the day's own places
    assert len(usual.stops) == 4                                # still never short of the places asked for


def test_a_wait_mid_day_is_avoidable_but_a_later_start_is_not():
    stop = lambda mid, a, d, t: {"moment_id": mid, "arrive": a, "depart": d, "travel_min": t, "title": mid}
    stops = [stop("x", "10:00", "11:00", 0), stop("y", "12:10", "13:00", 10)]
    assert dayplan.avoidable_wait(stops, "09:00", {}, "18:00", "fri", None) == 60   # not the hour before x
    dayplan.state_free_time(stops, "09:00", {}, "18:00", "fri", None)
    assert stops[0]["lines"][0].startswith("A gentle start") and stops[0]["free_before_kind"] == "start"
    assert stops[1]["lines"][0].startswith("Free time first") and stops[1]["free_before_kind"] == "wait"


def test_jonas_gentle_friday_in_london():
    """The real planner and cards: Jonas (scripts/london_examples.py) asked for a gentle, peaceful day."""
    import tempfile

    from fastapi.testclient import TestClient

    from brain.api import create_app
    from brain.config import DATA_DIR, Settings
    from brain.moments import load_moments

    path = Path(__file__).resolve().parents[1] / "scripts" / "london_examples.py"
    spec = importlib.util.spec_from_file_location("london_examples", path)
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    p = next(x for x in ex.PEOPLE if x["key"] == "jonas")
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    settings = Settings(database_url=f"sqlite:///{tempfile.mkdtemp()}/t.db", data_dir=DATA_DIR, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=1.0)
    with TestClient(create_app(settings)) as c:
        r = c.post("/v1/installs", json={"channel": "stranger", "src": "test", "consent": {
            "version": "2026-09", "research": True, "ai_processing": False}})
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        c.put("/v1/me/profile", headers=h, json=p["profile"])
        c.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": x} for i, x in p["swipes"].items()]})
        day = c.post("/v1/me/trips/days", headers=h, json={"start_date": ex.START.isoformat(), **p["trip"]}).json()
    stops = day["days"][0]["plan"]["stops"]
    places = [st for st in stops if not str(st["moment_id"]).startswith(("lunch@", "dinner@"))]
    assert len(places) >= 3
    for st in places:
        card = cards[st["moment_id"].split("#")[0]]
        assert card.features.place.get("active", 0) < 2, st["moment_id"]           # nothing strenuous
    assert not dayplan.disproportionate(stops)                                       # no journey longer than its visit
    for st in stops[1:]:
        assert st.get("free_before_min", 0) <= 45, st["moment_id"]                   # no long wait mid-day


def test_london_from_above_once_a_day():
    """m331: Horizon 22 and the Garden at 120 are minutes apart and both show the City from above (ChatGPT's review:
    "two tower viewpoints feel repetitive")."""
    assert {"m_horizon_22", "m_garden_at_120"} <= dayplan.high_views()
    assert "m_greenwich_wolfe_view" not in dayplan.high_views()       # a hilltop in a park is another experience


def test_a_day_never_starts_with_a_rest():
    """m331: "A rest in the Royal Festival Hall's free foyers" opened Margaret's and Sam's days at 10:13 and 11:13,
    before they had done anything."""
    rest = Candidate("rest", NEAR, NEAR, 40, DAY, 1.0, rest=True)
    sight = Candidate("sight", FAR, FAR, 60, DAY, 0.5)
    plan = plan_day([rest, sight], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=2, time_limit_s=0.5)
    assert [s.moment_id for s in plan.stops][0] == "sight"


def test_a_days_travel_stays_near_its_paces_budget():
    """m333 (Abram: "consider total daily travel burden"): places close together win over slightly better ones further
    apart once the day's travel would pass its budget, and the day keeps its places."""
    p = lambda dlat, dlon: Point(lat=51.5081 + dlat, lon=-0.1281 + dlon)
    near = [Candidate(f"near{k}", p(0.002 * k, 0.0), p(0.002 * k, 0.0), 45, DAY, 0.3) for k in range(1, 4)]
    far = [Candidate(f"far{k}", p(0.0125 * k, 0.0), p(0.0125 * k, 0.0), 45, DAY, 0.6) for k in range(1, 4)]
    run = lambda budget: plan_day(near + far, START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=3,
                                  time_limit_s=0.5, travel_budget_min=budget)
    unlimited, gentle = run(None), run(30)
    travel = lambda plan: sum(s.travel_min for s in plan.stops)
    assert len(gentle.stops) == 3 and travel(gentle) <= 30 < travel(unlimited)   # 28 min against 53


def test_a_ride_starts_from_somewhere_near_its_start():
    """m333 (Abram: "do not create a 50-minute transfer simply to reach a pier"): the boat from Greenwich comes after
    something at Greenwich, never straight after a long journey; with nothing there, no boat."""
    pier = Point(lat=51.5281, lon=-0.1281)                        # about 40 min on foot from the start
    hill = Point(lat=51.5291, lon=-0.1281)                        # a couple of minutes from the pier
    ride = Candidate("boat", pier, NEAR, 60, DAY, 1.0, ride=True)
    there = Candidate("hill", hill, hill, 45, DAY, 0.2)
    plan = plan_day([ride, there], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=2, time_limit_s=0.5)
    assert [s.moment_id for s in plan.stops] == ["hill", "boat"]
    alone = plan_day([ride], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=1, time_limit_s=0.5)
    assert alone.stops == []
    # …but a ride that's the day's must-do (a place they loved) is still planned: as a rule this once left the
    # solver no first solution, and the family's loved boat dropped out of their trip
    loved = plan_day([ride], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=1, time_limit_s=0.5,
                     must_include={"boat"})
    assert [s.moment_id for s in loved.stops] == ["boat"]
    with_hill = plan_day([ride, there], START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=2, time_limit_s=0.5,
                         must_include={"boat"})
    assert [s.moment_id for s in with_hill.stops] == ["hill", "boat"]   # Greenwich first where the day has it


def test_dinner_is_scored_by_the_persons_liking_for_food_and_can_be_a_named_place():
    """m334 (Abram: "Dinner should be scored against the person's food interest, budget and preferences, not inserted
    as an unpersonalised placeholder"; "use named, verified venues when possible")."""
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
    real = [dayplan.candidate_for(cards[k], 0.2) for k in ("m_beigel_bake_late", "m_borough_market_graze",
                                                          "m_waterloo_bridge_sunset")]
    brief = dayplan.Brief(start_name="Charing Cross", start=START, start_time="11:00", end_time="21:00", stops=3,
                          lunch_gbp=12.0)
    plain = dayplan.dinner_candidates(real, brief, cards, food_pull=0.0)
    keen = dayplan.dinner_candidates(real, brief, cards, food_pull=0.6)
    slot = lambda cs: next(c for c in cs if c.moment_id == "dinner@m_waterloo_bridge_sunset")
    assert abs(slot(keen).utility - slot(plain).utility - 0.6) < 1e-9 and all(c.dinner for c in keen)
    named = {c.moment_id for c in keen if "#dinner" in c.moment_id}
    assert named == {"m_beigel_bake_late#dinner"}                 # open to 23:30; Borough Market closes at 16:00
    beigel = next(c for c in keen if c.moment_id == "m_beigel_bake_late#dinner")
    assert all(lo >= dayplan.DINNER_START[0] for lo, _ in beigel.windows)
    early = replace_brief(brief, end_time="18:00")
    assert dayplan.dinner_candidates(real, early, cards) == []    # a day that ends before the evening has none


def replace_brief(brief, **kw):
    from dataclasses import replace
    return replace(brief, **kw)


def test_a_missing_dinner_is_said_with_its_reason():
    brief = dayplan.Brief(start_name="Charing Cross", start=START, start_time="11:00", end_time="20:00", stops=3,
                          lunch_gbp=12.0, budget_gbp=40.0)
    stops = [{"moment_id": "m_x", "key": "m_x", "cost_gbp": 30.0, "travel_min": 10, "travel_mode": "walk",
              "lines": ["Getting there: about 10 min on foot."]}]
    dayplan.say_no_dinner(stops, brief)
    assert stops[-1]["lines"][-1].startswith("Dinner isn't in the plan: with about £18 for it")
    fed = [{"moment_id": "m_x", "key": "dinner@m_x", "cost_gbp": 18.0, "lines": []}]
    dayplan.say_no_dinner(fed, brief)
    assert fed[-1]["lines"] == []


def test_places_beyond_the_persons_own_number_are_strong_matches():
    """m333 (Abram: "review every extra place... it must match the person's actual preferences"): a day may hold as
    many fair matches as the places the person asked for; every place beyond that is a strong match."""
    near = lambda k: Point(lat=51.5081 + 0.001 * k, lon=-0.1281)
    fair = [Candidate(f"fair{k}", near(k), near(k), 40, DAY, -0.5) for k in range(4)]      # a chance of Good ~0.56
    strong = [Candidate(f"strong{k}", near(k + 4), near(k + 4), 40, DAY, 0.3) for k in range(1)]
    plan = plan_day(fair + strong, START, 600, 1080, WalkingEstimate(), PLAIN, max_stops=5, time_limit_s=0.5,
                    weak_below=-0.131, weak_max=2)
    ids = [s.moment_id for s in plan.stops]
    assert sum(i.startswith("fair") for i in ids) <= 2 and "strong0" in ids


def test_a_days_title_names_its_own_places():
    """m337 (Abram: "titles should sound natural and describe the actual day, not repeat generic templates")."""
    from brain import reasons
    from brain.config import DATA_DIR
    from brain.moments import load_moments
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
    st = lambda mid, p: {"moment_id": mid, "predicted": p}
    day = [st("m_borough_market_graze", 0.5), st("m_beigel_bake_late", 0.9), st("lunch@start", None),
           st("a_old_spitalfields_market", 0.2), st("m_leadenhall_market", 0.1), st("m_alderman_stairs_sunset", 0.3)]
    assert reasons.day_title(day, cards) == "Borough Market, a Brick Lane bagel and Tower Bridge at sunset"
    assert reasons.day_title([st("m_national_gallery", 0.4)], cards) == "The National Gallery"
    assert len(reasons.day_title(day, cards)) <= 80
