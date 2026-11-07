"""m217 (Abram, 7 Nov): lunch stays inside the day's budget by default and never disappears silently; fares count
towards the budget; one total; an overrun is explained. Budgets from £5 to £100."""
import pytest

from brain import daybudget

from test_api import client, install  # noqa: F401  (the client fixture)

DAY = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "Charing Cross station",
       "start_time": "10:00", "end_time": "18:00", "conditions": {"temp_c": 18, "rain_prob": 0.1}}


@pytest.mark.parametrize("budget,want", [(None, "usual"), (100, "usual"), (15, "usual"), (14.99, "cheaper"),
                                         (6, "cheaper"), (5.99, "own"), (0, "own")])
def test_the_first_lunch_is_the_most_comfortable_the_budget_can_cover(budget, want):
    assert daybudget.choose_lunch(budget).key == want
    assert daybudget.choose_lunch(budget, food_in_budget=False).key == "usual"   # outside the budget: the usual
    steps = [daybudget.LUNCHES[0]]
    while (n := daybudget.next_lunch(steps[-1])) is not None:
        steps.append(n)
    assert [s.key for s in steps] == ["usual", "cheaper", "own"]               # steps down, never to "none"


def _stop(mid, cost, lunch=False, mode="walk", minutes=10, mine=None):
    return {"moment_id": mid, "title": mid, "cost_gbp": cost, "lunch": lunch, "travel_mode": mode,
            "travel_min": minutes, "mine": mine}


def test_the_block_adds_up_and_says_what_each_figure_is():
    stops = [_stop("a", 0.0, mode="transit"), _stop("lunch@a", 6.0, lunch=True), _stop("b", 2.0, mode="transit")]
    b = daybudget.block(12.0, stops, daybudget.LUNCHES[1])
    assert [ln["label"] for ln in b["lines"]] == ["Lunch", "Getting around", "Places"]
    assert (b["total_gbp"], b["left_gbp"]) == (14.0, -2.0) and b["status"] == "over"
    assert b["message"] == "This day comes to £14, £2 over your £12: most of it is lunch."
    assert "Bring lunch, or buy it from a supermarket or market" in b["options"]
    assert b["lines"][0]["kind"] == "estimate" and b["lines"][2]["kind"] == "price"


def test_no_lunch_is_never_silent():
    b = daybudget.block(8.0, [_stop("a", 0.0)], daybudget.LUNCHES[2], lunch_expected=True)
    assert b["lines"][0] == {"label": "Lunch", "gbp": None, "kind": "missing", "in_budget": True,
                             "note": "There's no room for a lunch stop on this day, so eat before or after."}


def test_food_left_out_of_the_budget_is_shown_on_its_own():
    stops = [_stop("a", 4.0), _stop("lunch@a", 0.0, lunch=True)]
    b = daybudget.block(10.0, stops, daybudget.LUNCHES[0], food_in_budget=False)
    lunch = b["lines"][0]
    assert lunch["in_budget"] is False and lunch["gbp"] == 15.0 and lunch["note"].endswith("not in your budget")
    assert b["total_gbp"] == 4.0 and b["status"] == "fits"


@pytest.mark.parametrize("budget", [5, 8, 10, 12, 15, 20, 25, 40, 70, 100])
def test_every_budget_from_5_to_100_keeps_lunch_said_and_one_total(client, budget):
    h, _ = install(client)
    r = client.post("/v1/me/plans", headers=h, json={**DAY, "budget_gbp": budget})
    assert r.status_code == 201, r.text
    plan = r.json()
    b = plan["budget"]
    lunch = b["lines"][0]
    assert lunch["label"] == "Lunch"                                        # always said, whatever it is
    has_lunch = any(st["lunch"] for st in plan["stops"])
    assert (lunch["kind"] != "missing") == has_lunch
    assert b["total_gbp"] == plan["totals"]["cost_gbp"]                    # one total, never two that disagree
    first = daybudget.choose_lunch(budget)
    steps = [first.key] + [n.key for n in (daybudget.next_lunch(first), ) if n] + ["own"]
    assert b["lunch_choice"] in steps                                       # the first choice, or a step down
    if b["status"] == "over":
        assert b["message"].startswith("This day comes to") and b["options"]
    else:
        assert b["left_gbp"] >= 0


def test_the_blind_comparison_has_no_budget_block_and_plans_as_before(client):
    h, _ = install(client)
    plan = client.post("/v1/me/plans", headers=h, json={**DAY, "budget_gbp": 10, "blind": True}).json()
    assert plan["budget"] is None
    lunch = [st for st in plan["stops"] if st["lunch"] and st["moment_id"].startswith("lunch@")]
    assert all(st["cost_gbp"] == 15.0 for st in lunch)                     # the usual lunch, as Test B always had


@pytest.fixture
def real_client(tmp_path):
    """The app with every real card, for days that need Tube and bus fares (the test cards are all close by)."""
    import shutil
    from fastapi.testclient import TestClient
    from brain.api import create_app
    from brain.config import DATA_DIR, Settings
    data = tmp_path / "data"
    (data / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "onboarding.yaml", "conjoint_design.csv", "swipe_items.yaml", "aspiration.yaml",
              "privacy_app.html", "categories.yaml", "destinations.yaml"):
        shutil.copy(DATA_DIR / f, data / f)
    for f in (DATA_DIR / "moments").glob("*.yaml"):
        shutil.copy(f, data / "moments")
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'r.db'}", data_dir=data, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=0.3)
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.mark.parametrize("budget", [8, 12, 15, 20])
def test_fares_never_squeeze_lunch_out_it_steps_down_instead(real_client, budget):
    """From Greenwich the day needs Tube and bus fares. Setting them aside used to leave no room for lunch, and the
    lunchless day won because it was cheaper (7 Nov). Now lunch steps down (usual, cheaper, bring lunch) and stays."""
    h, _ = install(real_client)
    greenwich = {**DAY, "start": {"lat": 51.4826, "lon": -0.0077}, "start_name": "Greenwich"}
    plan = real_client.post("/v1/me/plans", headers=h, json={**greenwich, "budget_gbp": budget}).json()
    b = plan["budget"]
    assert b["lines"][0]["kind"] != "missing" and any(st["lunch"] for st in plan["stops"])
    assert b["status"] != "over" and b["total_gbp"] == plan["totals"]["cost_gbp"] <= budget
