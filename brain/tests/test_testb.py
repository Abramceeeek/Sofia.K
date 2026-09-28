"""Test B plan generation, run against a filled-in copy of the real results-sheet template."""

import shutil
from pathlib import Path

import pytest
import yaml
from openpyxl import load_workbook

from brain import testb
from brain.planner import Candidate, LegWeights, plan_day
from brain.travel import LondonEstimate, WalkingEstimate
from brain.moments import Point

from conftest import DATA

REPO = Path(__file__).resolve().parents[2]
START = Point(lat=51.5081, lon=-0.1281)


def fill_results(path: Path):
    """Two made-up participants in the real template: P01 (label A) and P02 (label B)."""
    wb = load_workbook(REPO / "validation/results-sheet.xlsx")
    ws = wb["Participants"]
    ws["T6"], ws["T7"] = "stranger", "friends & family"
    ws["AG6"] = "Food, nature"          # Test A 5.7 (D77); P02 skipped the question
    sw = wb["Swipes"]
    rows = [("P01", 11, "Greenwich view", 1), ("P01", 7, "Camden Market", 3), ("P01", 13, "Primrose Hill", 1),
            ("P01", 3, "Borough Market", 3), ("P01", 1, "Big Ben", 4),
            ("P02", 3, "Borough Market", 1), ("P02", 14, "Brick Lane", 1), ("P02", 6, "Hyde Park", 3)]
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            sw.cell(row=6 + i, column=1 + j, value=v)
    ch = wb["Choices"]
    for i, t in enumerate(range(1, 11)):
        ch.cell(row=6 + i, column=1, value="P01")
        ch.cell(row=6 + i, column=2, value=t)
        ch.cell(row=6 + i, column=3, value="A" if t % 2 else "B")
    tb = wb["TestB"]
    tb["B6"], tb["B7"] = "A", "B"   # overwrite the pre-randomised labels for a known test
    wb.save(path)


@pytest.fixture
def data_dir(tmp_path, test_moments):
    d = tmp_path / "data"
    (d / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "swipe_items.yaml", "conjoint_design.csv", "aspiration.yaml"):
        shutil.copy(DATA / f, d / f)
    for m in test_moments:
        (d / "moments" / f"{m.id}.yaml").write_text(yaml.safe_dump(m.model_dump(by_alias=True)))
    return d


def test_load_results_reads_the_real_template(tmp_path):
    f = tmp_path / "results.xlsx"
    fill_results(f)
    people = testb.load_results(f)
    assert set(people) == {"P01", "P02"}           # the other pre-filled IDs have no Test A data
    p1 = people["P01"]
    assert p1.channel == "stranger" and p1.personal_label == "A"
    assert (11, "loved") in p1.swipes and (1, "havent_been") in p1.swipes
    assert len(p1.choices) == 10
    assert people["P02"].channel == "friends & family" and people["P02"].personal_label == "B"


def test_swipe_items_cover_all_16_and_use_known_tags(pop):
    items = testb.load_swipe_items(DATA / "swipe_items.yaml")
    assert sorted(items) == list(range(1, 17))
    assert items[12].id == "m_southken_nhm_reveal"
    for m in items.values():
        assert all(m.tag(t) is not None for t in ["crowds", "awe", "food", "green_nature"])


def test_weights_from_test_a_move_in_the_right_direction(pop, tmp_path):
    f = tmp_path / "results.xlsx"
    fill_results(f)
    p = testb.load_results(f)["P02"]
    items = testb.load_swipe_items(DATA / "swipe_items.yaml")
    post = testb.fit_participant(pop, p, items, testb.load_tasks(DATA / "conjoint_design.csv"))
    b = pop.b_person(post.mean)
    food = pop.names.index("food")
    assert b[food] > pop.spec("food").mean       # loved two food places


def test_planner_hits_exact_stops_budget_and_must_do(pop, test_moments):
    cands = [Candidate(m.id, m.start(), m.end(), int(m.duration_min()), tuple(m.windows()), 0.5, float(m.cost_gbp or 0))
             for m in test_moments]
    legs = LegWeights(-0.3, -0.7)
    plan = plan_day(cands, START, 600, 1080, WalkingEstimate(), legs, max_stops=3, min_stops=3,
                    budget_gbp=20, must_include={"t_park"}, time_limit_s=0.5)
    ids = [s.moment_id for s in plan.stops]
    assert len(ids) == 3 and "t_park" in ids
    assert "t_pricey" not in ids                 # £80 is over the £20 budget
    cost = {c.moment_id: c.cost_gbp for c in cands}
    assert sum(cost[i] for i in ids) <= 20


def test_planner_says_so_when_it_cannot_fit_the_stops(pop, test_moments):
    cands = [Candidate(m.id, m.start(), m.end(), int(m.duration_min()), tuple(m.windows()), 0.5)
             for m in test_moments]
    plan = plan_day(cands, START, 600, 700, WalkingEstimate(), LegWeights(-0.3, -0.7), max_stops=6, min_stops=6,
                    time_limit_s=0.3)
    assert plan.status.startswith("could not fit 6 stops") and len(plan.stops) < 6


def test_london_estimate_walks_short_legs_and_rides_long_ones():
    t = LondonEstimate()
    near, far = Point(lat=51.5081, lon=-0.1281), Point(lat=51.4769, lon=-0.0005)   # ~9 km apart
    assert t.mode(near, Point(lat=51.5100, lon=-0.1300)) == "walk"
    assert t.mode(near, far) == "transit"
    assert t.minutes(near, far) < WalkingEstimate().minutes(near, far)


def test_plans_command_writes_blind_identical_plans_and_a_review(tmp_path, data_dir):
    results = tmp_path / "results.xlsx"
    fill_results(results)
    brief = dict(yaml.safe_load((DATA / "testb" / "brief.example.yaml").read_text()))
    brief.update(stops=3, budget_gbp=40, time_limit_s=0.5)
    (tmp_path / "brief.yaml").write_text(yaml.safe_dump(brief))
    generic = yaml.safe_load((DATA / "testb" / "generic.example.yaml").read_text())
    generic["stops"] = generic["stops"][:3]
    (tmp_path / "generic.yaml").write_text(yaml.safe_dump(generic))
    (tmp_path / "intent.yaml").write_text(yaml.safe_dump({"P01": {"mode": "explore", "must_do": "t_view"}}))
    out = tmp_path / "out"
    rc = testb.main(["--data", str(data_dir), "plans", "--results", str(results), "--brief", str(tmp_path / "brief.yaml"),
                     "--generic", str(tmp_path / "generic.yaml"), "--intent", str(tmp_path / "intent.yaml"),
                     "--out", str(out)])
    assert rc == 0
    for pid in ("P01", "P02"):
        a = (out / f"{pid}_plan_A.txt").read_text()
        b = (out / f"{pid}_plan_B.txt").read_text()
        assert a.startswith("*Plan A:") and b.startswith("*Plan B:")
        for text in (a, b):   # blind: same shape, no reasons, no model words
            assert text.count("Cost:") == 3
            assert "predicted" not in text and "weight" not in text and "Chosen" not in text
        assert (out / f"{pid}_plan_A.pdf").read_bytes().startswith(b"%PDF")
        assert (out / f"{pid}_plan_B.pdf").stat().st_size > 1000
    p1_personal = (out / "P01_plan_A.txt").read_text()   # P01's personalised plan is A
    assert "Test moment t_view" in p1_personal            # the must-do stop
    review = (out / "P01_review.md").read_text()
    assert "Personalised plan is **A**" in review and "Read-back lines" in review
    assert "Inspiring fields (Test A 5.7): Food, Nature." in review
    assert "Said these fields inspire them: Food, Nature" in review
    assert "Inspiring fields (Test A 5.7): none given." in (out / "P02_review.md").read_text()
    assert "Big Ben and Parliament Square" in (out / "P02_plan_A.txt").read_text()   # P02's generic plan is A


def test_plans_command_refuses_without_enough_moments(tmp_path):
    d = tmp_path / "data"
    (d / "moments").mkdir(parents=True)
    for f in ("priors.yaml", "swipe_items.yaml", "conjoint_design.csv"):
        shutil.copy(DATA / f, d / f)
    shutil.copy(DATA / "moments" / "m_southken_nhm_reveal.yaml", d / "moments")
    results = tmp_path / "results.xlsx"
    fill_results(results)
    rc = testb.main(["--data", str(d), "plans", "--results", str(results),
                     "--brief", str(DATA / "testb" / "brief.example.yaml"),
                     "--generic", str(DATA / "testb" / "generic.example.yaml"), "--out", str(tmp_path / "o")])
    assert rc == 2


def test_weights_command_prints_readback(tmp_path, data_dir, capsys):
    results = tmp_path / "results.xlsx"
    fill_results(results)
    assert testb.main(["--data", str(data_dir), "weights", "--results", str(results), "--ids", "P01"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("P01 (stranger, 14 informative answers)")


def test_draft_moments_stay_out_of_real_plans(tmp_path, data_dir, capsys):
    # Drafts can hold Claude's GUESS values, so real Test B plans use only checked (ready) moments.
    for f in (data_dir / "moments").glob("*.yaml"):
        doc = yaml.safe_load(f.read_text())
        doc["status"] = "draft"
        f.write_text(yaml.safe_dump(doc))
    results = tmp_path / "results.xlsx"
    fill_results(results)
    args = ["--data", str(data_dir), "plans", "--results", str(results),
            "--brief", str(DATA / "testb" / "brief.example.yaml"),
            "--generic", str(DATA / "testb" / "generic.example.yaml"), "--out", str(tmp_path / "o"), "--no-pdf"]
    assert testb.main(args) == 2
    assert "Skipping" in capsys.readouterr().err
    assert testb.main(args + ["--include-drafts"]) == 0
    assert "DRY RUN" in capsys.readouterr().err


def test_plan_text_drops_internal_notes_and_names_the_last_place():
    assert testb.clean("Any time; at dusk the dome is lit (GUESS)") == "Any time; at dusk the dome is lit"
    assert testb.clean("Sunset; late autumn skies are best (CHECKED)") == "Sunset; late autumn skies are best"
    assert testb.clean("A walk (CHECKED: official page) here") == "A walk here"
    assert testb.clean("Pelicans (since 1664)") == "Pelicans (since 1664)"      # ordinary brackets stay
    from brain.moments import load_moments
    ms = {m.id: m for m in load_moments(DATA / "moments")}
    assert ms["m_uber_boat_west_night"].leave_name() == "Westminster Pier"
    assert ms["m_st_dunstan_garden"].leave_name() == "St Dunstan-in-the-East"
    assert ms["m_park_break_olympic"].leave_name() == "Queen Elizabeth Olympic Park"
