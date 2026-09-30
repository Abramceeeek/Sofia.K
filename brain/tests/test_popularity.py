"""D113: the popularity nudge (decisions/plan-variety.md)."""
from brain import dayplan
from brain.config import DATA_DIR
from brain.moments import Point, load_moments
from brain.personal import prior_only
from brain.popularity import load_popularity
from brain.population import load_population
from brain.travel import LondonEstimate

POP = load_population(DATA_DIR / "priors.yaml")
READY = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
BRIEF = dayplan.Brief(start_name="Charing Cross station", start=Point(lat=51.507819, lon=-0.126137),
                      start_time="12:00", end_time="17:00", stops=4, budget_gbp=40, weekday="sat", time_limit_s=0.5)


def cards(plan):
    return {dayplan._base(st.moment_id) for st in plan.stops if not st.moment_id.startswith("lunch@")}


def test_the_table_is_for_the_current_priors():
    """Regenerate data/popularity.yaml (python -m brain.popularity) when the priors change."""
    table = load_popularity(DATA_DIR / "popularity.yaml")
    assert table is not None and table.population_version == POP.version
    assert table.shares and all(0 < v <= 1 for v in table.shares.values())
    assert set(table.shares) <= {m.id for m in READY}


def test_the_nudge_never_costs_more_than_the_cap():
    post, travel = prior_only(POP.delta_prior_sd), LondonEstimate()
    usual, _, _, _ = dayplan.personal_plan(POP, post, READY, BRIEF, travel)
    heavy = {c: 1.0 for c in cards(usual)}              # every usual card as if it were in all plans
    plan, _, _, notes = dayplan.personal_plan(POP, post, READY, BRIEF, travel, popularity=heavy)
    assert notes.value_usual is not None
    if notes.nudged:
        assert notes.value >= notes.value_usual - dayplan.NUDGE_CAP - 1e-9
    else:
        assert notes.value == notes.value_usual
    # with room to spare, the nudge takes the other plan, and reports the person's own utilities
    plan, stops, _, notes = dayplan.personal_plan(POP, post, READY, BRIEF, travel, popularity=heavy, cap=100.0)
    assert notes.nudged and cards(plan) != cards(usual)
    by_id = {m.id: m for m in READY}
    assert all(s["predicted"] is None or s["moment_id"] in by_id for s in stops)


def test_no_table_no_nudge():
    post, travel = prior_only(POP.delta_prior_sd), LondonEstimate()
    _, _, _, notes = dayplan.personal_plan(POP, post, READY, BRIEF, travel)
    assert not notes.nudged and notes.value_usual is None
