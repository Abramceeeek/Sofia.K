"""m233 (Abram, m224): the old free-text food field (`foods_avoided`, D19, unasked since D123) is counted, never read
out, and deleted only on a confirmed request. Backups neither carry it nor bring it back. Synthetic data only."""
import json
import logging

from brain import backup, db, food

from test_api import ADMIN, client, install  # noqa: F401  (the fixture)

SECRET = "SYNTHETIC-pork-and-peanuts"   # stands in for what a person might have typed


def _legacy(client, uid, value):
    """A profile as an old build stored it, written straight to the database (today's API drops the field)."""
    with client.app.state.Session() as s:
        s.get(db.User, uid).profile = {"based": "london", "budget_band": "20_40", "foods_avoided": value}
        s.commit()


def test_the_audit_gives_counts_and_never_a_value(client, caplog):
    caplog.set_level(logging.DEBUG)
    a, uid_a = install(client)
    b, uid_b = install(client)
    install(client)
    _legacy(client, uid_a, SECRET)
    _legacy(client, uid_b, "")
    assert client.get("/v1/admin/audit/foods-avoided", headers=a).status_code == 403   # admin only
    r = client.get("/v1/admin/audit/foods-avoided", headers=ADMIN)
    assert {k: v for k, v in r.json().items() if k != "old_app_saves_dropped_since_start"} == {"profiles": 3, "with_key": 2, "non_empty": 1}
    assert SECRET not in r.text and SECRET not in caplog.text and "pork" not in caplog.text


def test_deleting_needs_a_confirmation_and_keeps_the_rest_of_the_profile(client, caplog):
    caplog.set_level(logging.DEBUG)
    h, uid = install(client)
    _legacy(client, uid, SECRET)
    assert client.post("/v1/admin/audit/foods-avoided/delete", headers=h, json={"confirm": "delete"}).status_code == 403
    assert client.post("/v1/admin/audit/foods-avoided/delete", headers=ADMIN, json={}).status_code == 400
    assert client.get("/v1/admin/audit/foods-avoided", headers=ADMIN).json()["with_key"] == 1   # nothing gone yet
    r = client.post("/v1/admin/audit/foods-avoided/delete", headers=ADMIN, json={"confirm": "delete"})
    assert r.json() == {"before": {"profiles": 1, "with_key": 1, "non_empty": 1},
                        "after": {"profiles": 1, "with_key": 0, "non_empty": 0}}
    with client.app.state.Session() as s:
        assert s.get(db.User, uid).profile == {"based": "london", "budget_band": "20_40"}   # the rest is kept
    assert SECRET not in r.text and SECRET not in caplog.text
    again = client.post("/v1/admin/audit/foods-avoided/delete", headers=ADMIN, json={"confirm": "delete"})
    assert again.json()["before"]["with_key"] == 0                                         # safe to run twice


def test_a_backup_never_carries_it_and_an_older_backup_cannot_bring_it_back(client, tmp_path):
    h, uid = install(client)
    _legacy(client, uid, SECRET)
    made = backup.dump(client.app.state.engine)
    assert SECRET not in json.dumps(made)                                                   # new backups: never in
    older = json.loads(json.dumps(made))
    older["tables"]["users"][0]["profile"]["foods_avoided"] = SECRET                        # one made before m233
    engine = db.make_engine(f"sqlite:///{tmp_path / 'restored.db'}")
    backup.restore(engine, older)
    with db.make_sessionmaker(engine)() as s:
        profile = s.get(db.User, uid).profile
    assert "foods_avoided" not in profile and profile["based"] == "london"
    assert food.audit_profiles([profile]) == {"profiles": 1, "with_key": 0, "non_empty": 0}
