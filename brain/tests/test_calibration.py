import uuid

import pytest
import yaml
from fastapi.testclient import TestClient

from brain.calibration import CalibrationSettings, DATA_DIR, create_app, database_url, load_places, rank_places

from conftest import DATA

TOKEN = "test-admin-token"


@pytest.fixture
def client(tmp_path):
    settings = CalibrationSettings(database_url=f"sqlite:///{tmp_path / 'cal.db'}", data_dir=DATA_DIR,
                                   admin_token=TOKEN, contact="hello@example.org")
    return TestClient(create_app(settings))


def test_candidates_are_about_30_and_the_draft_16_keep_their_tags():
    places = load_places(DATA_DIR / "places.yaml")
    assert 28 <= len(places) <= 32
    items = yaml.safe_load((DATA / "swipe_items.yaml").read_text())["items"]
    linked = [p for p in places if p.swipe_item]
    assert sorted(p.swipe_item for p in linked) == sorted(items)
    for p in linked:
        it = items[p.swipe_item]
        assert p.name == it["name"]
        assert p.tags == {**it["place"], **it["moment"]}


def test_render_postgres_urls_get_the_psycopg_driver():
    assert database_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert database_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert database_url("sqlite:///./x.db") == "sqlite:///./x.db"


def test_page_is_private_by_default_and_names_the_contact(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'content="hello@example.org"' in r.text
    assert "We don't store your IP address" in r.text
    assert r.headers["referrer-policy"] == "no-referrer"
    assert "noindex" in r.headers["x-robots-tag"]
    # nothing loaded from other sites (fonts, analytics), which would pass the IP address to them
    assert "https://" not in r.text.split("<body>")[0]


def test_answers_upsert_and_delete(client):
    bid = str(uuid.uuid4())
    places = client.get("/api/places").json()["places"]
    assert "tags" not in places[0]
    a, b = places[0]["id"], places[1]["id"]
    r = client.post("/api/answers", json={"browser_id": bid, "answers": [
        {"place_id": a, "answer": "loved"}, {"place_id": b, "answer": "not_been"}]})
    assert r.json() == {"saved": 2}
    # changing an answer replaces it rather than adding a row
    client.post("/api/answers", json={"browser_id": bid, "answers": [{"place_id": a, "answer": "didnt"}]})
    raw = client.get("/api/export.csv", headers={"X-Admin-Token": TOKEN}).text.strip().splitlines()
    assert raw[0] == "browser_id,place_id,answer,day"
    assert len(raw) == 3 and f"{bid},{a},didnt" in raw[1]
    assert client.delete(f"/api/answers/{bid}").json() == {"deleted": 2}
    assert len(client.get("/api/export.csv", headers={"X-Admin-Token": TOKEN}).text.strip().splitlines()) == 1


def test_bad_input_is_refused(client):
    ok = {"place_id": "big_ben", "answer": "loved"}
    assert client.post("/api/answers", json={"browser_id": "not-a-uuid", "answers": [ok]}).status_code == 422
    assert client.post("/api/answers", json={"browser_id": str(uuid.uuid4()),
                                             "answers": [{"place_id": "nowhere", "answer": "loved"}]}).status_code == 422
    assert client.post("/api/answers", json={"browser_id": str(uuid.uuid4()),
                                             "answers": [{"place_id": "big_ben", "answer": "meh"}]}).status_code == 422


def test_results_need_the_token(client):
    assert client.get("/api/results").status_code == 401
    assert client.get("/api/results", headers={"X-Admin-Token": "wrong"}).status_code == 401
    assert client.get("/api/results", headers={"X-Admin-Token": TOKEN}).status_code == 200


def test_results_are_off_without_a_token(tmp_path):
    settings = CalibrationSettings(database_url=f"sqlite:///{tmp_path / 'c.db'}", data_dir=DATA_DIR, admin_token=None)
    assert TestClient(create_app(settings)).get("/api/results", headers={"X-Admin-Token": ""}).status_code == 404


def test_ranking_prefers_familiar_and_divisive_places():
    places = load_places(DATA_DIR / "places.yaml")
    ids = [p.id for p in places]
    rows = []
    for i in range(20):
        b = f"b{i}"
        # everyone answers every place "haven't been" unless set below
        answers = {pid: "not_been" for pid in ids}
        answers["big_ben"] = "fine"                                 # familiar, everyone agrees
        answers["borough_market"] = "loved" if i % 2 else "didnt"   # familiar and split
        answers["kew_gardens"] = "loved" if i % 2 else "didnt" if i < 4 else "not_been"  # split, but few have been
        rows += [(b, pid, a) for pid, a in answers.items()]
    rows += [("drive_by", "big_ben", "loved")]                      # too few answers: not counted
    res = rank_places(rows, places, n_pick=16, min_visitors=5)
    by = {p["place_id"]: p for p in res["places"]}
    assert res["browsers_total"] == 21 and res["browsers_included"] == 20
    assert by["borough_market"]["familiarity"] == 1.0 and by["borough_market"]["divisiveness"] == 1.0
    assert by["borough_market"]["rank"] == 1 and by["borough_market"]["recommended"]
    assert by["big_ben"]["divisiveness"] == 0.0 and by["big_ben"]["score"] == 0.0
    assert by["kew_gardens"]["answers"] == 20 and by["kew_gardens"]["loved"] == 10
    assert not by["hyde_park"]["recommended"] and by["hyde_park"]["low_n"]  # nobody has been


def test_coverage_warns_when_a_tag_is_missing_from_the_picks():
    places = load_places(DATA_DIR / "places.yaml")
    rows = [(f"b{i}", p.id, ("loved" if i % 2 else "didnt")) for i in range(12) for p in places]
    res = rank_places(rows, places, n_pick=2, min_visitors=5)
    assert res["n_recommended"] == 2
    assert res["coverage"], "two picks can't carry every tag twice"
    assert all({"tag", "in_set", "best_outside"} <= set(w) for w in res["coverage"])


def test_render_blueprint_stays_free_and_log_free():
    from conftest import DATA
    bp = yaml.safe_load((DATA.parents[1] / "render.yaml").read_text())
    db, = bp["databases"]                                        # one free Postgres per workspace (D109)
    assert db["plan"] == "free" and db["ipAllowList"] == []
    assert {w["name"] for w in bp["services"]} == {"london-places-swipe", "moments-brain"}
    for web in bp["services"]:
        assert web["plan"] == "free"                             # left out, Render picks paid plans
        assert "--no-access-log" in web["startCommand"]
        assert (DATA.parent / web["buildCommand"].split()[-1]).exists()


def test_app_api_needs_only_its_own_requirements():
    """The app API on Render installs requirements-app.txt, without the Test B CLI's openpyxl and reportlab."""
    import subprocess
    import sys
    code = "import sys; sys.modules['openpyxl'] = None; sys.modules['reportlab'] = None; import brain.api"
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_calibration_app_needs_only_its_own_small_requirements():
    import ast
    import brain.calibration as cal
    tree = ast.parse(open(cal.__file__, encoding="utf-8").read())
    imported = {(n.module or "").split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    imported |= {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    third_party = imported - {"__future__", "csv", "hmac", "html", "io", "os", "collections", "dataclasses",
                              "datetime", "pathlib", "typing", "uuid", ""}
    assert third_party == {"yaml", "fastapi", "pydantic", "sqlalchemy"}
