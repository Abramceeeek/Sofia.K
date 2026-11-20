"""m308: plans stored before the A2 hotfix are counted without showing anything, and cleaned only as A2 stores them.
The rows below copy what the frozen code (80a0da3) stored, read from its own output on 20 Nov."""
import json

from sqlalchemy import create_engine, insert, select

from brain import storedplaces as sp

STAY = "Zed Private Stay"
HERE_DAY = [{"moment_id": "lunch@start", "title": "Lunch near where you are", "pin": {"lat": 51.5081, "lon": -0.1281},
             "travel_text": ""},
            {"moment_id": "m_boat", "title": "Uber Boat", "pin": {"lat": 51.5071, "lon": -0.1218},
             "travel_text": "Getting there: about 6 min on foot from where you are."}]
STATION_DAY = [{"moment_id": "lunch@start", "title": "Lunch near Charing Cross", "pin": {"lat": 51.5081, "lon": -0.12}},
               {"moment_id": "m_boat", "title": "Uber Boat", "pin": {"lat": 51.5071, "lon": -0.1218}}]
TRIP_DAY = [{"moment_id": "lunch@start", "title": f"Lunch near {STAY}", "pin": {"lat": 51.5123, "lon": -0.1357}},
            {"moment_id": "m_tate", "title": "Tate Modern", "pin": {"lat": 51.5076, "lon": -0.0994},
             "travel_text": f"Getting there: about 12 min on foot from {STAY}.",
             "lines": [f"Getting there: about 12 min on foot from {STAY}."]}]
TRIP_DAY_2 = [{"moment_id": "m_bank", "title": "Bank", "pin": {"lat": 51.513, "lon": -0.089},
               "travel_text": f"Getting there: about 29 min by Tube or bus from {STAY} to Bank station.",
               "lines": [f"Getting there: about 29 min by Tube or bus from {STAY} to Bank station."]}]
TRIP_CENTRE = [{"moment_id": "m_bank", "title": "Bank",
                "travel_text": "Getting there: about 9 min by Tube or bus from Charing Cross to Bank station."}]


def _db(tmp_path, rows):
    engine = create_engine(f"sqlite:///{tmp_path / 'p.db'}")
    sp._PLANS.metadata.create_all(engine)
    with engine.begin() as c:
        for intent, stops in rows:
            c.execute(insert(sp._PLANS).values(intent=intent, stops=stops))
    return engine


ROWS = [({}, HERE_DAY), ({}, STATION_DAY), ({"trip": True, "day": 0}, TRIP_DAY), ({"trip": True, "day": 1}, TRIP_DAY_2),
        ({"trip": True, "day": 0}, TRIP_CENTRE)]


def test_count_finds_both_and_shows_nothing(tmp_path, capsys):
    engine = _db(tmp_path, ROWS)
    assert sp.count(engine) == {"plans": 5, "here_pins": 1, "stay_names": 2}
    sp.main(["count", "--database-url", str(engine.url)])
    out = capsys.readouterr().out
    assert out.strip() == "plans 5, here_pins 1, stay_names 2"
    for private in (STAY, "51.5", "where you are", "Zed"):
        assert private not in out


def test_clean_changes_only_the_pin_and_the_stay_name(tmp_path, capsys):
    engine = _db(tmp_path, ROWS)
    assert sp.main(["clean", "--database-url", str(engine.url)]) == 1           # no --confirm: nothing changes
    assert sp.count(engine)["here_pins"] == 1
    assert sp.main(["clean", "--database-url", str(engine.url), "--confirm", "clean"]) == 0
    out = capsys.readouterr().out
    assert "updated 3 plans" in out and "COMMITTED" in out and STAY not in out
    assert sp.count(engine) == {"plans": 5, "here_pins": 0, "stay_names": 0}
    with engine.connect() as c:
        kept = [r.stops for r in c.execute(select(sp._PLANS.c.stops).order_by(sp._PLANS.c.id))]
    assert kept[0][0]["pin"] is None and kept[0][1] == HERE_DAY[1]               # only lunch's pin went
    assert kept[1] == STATION_DAY and kept[4] == TRIP_CENTRE                     # public starts untouched
    assert STAY not in json.dumps(kept) and kept[2][0]["title"] == "Lunch near your stay"
    assert kept[2][0]["pin"] == TRIP_DAY[0]["pin"]                               # the stay's location is kept, as the notice says
    assert kept[3][0]["travel_text"] == "Getting there: about 29 min by Tube or bus from your stay to Bank station."


def test_clean_rolls_back_if_anything_is_left(tmp_path, monkeypatch):
    engine = _db(tmp_path, ROWS)
    monkeypatch.setattr(sp, "cleaned", lambda intent, stops, public: stops)      # a clean that changes nothing
    r = sp.clean(engine)
    assert not r["committed"] and r["after"] == r["before"]


def test_a_clean_database_has_nothing_to_do(tmp_path):
    engine = _db(tmp_path, [({}, STATION_DAY), ({"trip": True}, TRIP_CENTRE)])
    r = sp.clean(engine)
    assert r["committed"] and r["updated"] == 0
