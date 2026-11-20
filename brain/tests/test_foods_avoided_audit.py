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


def test_a_backup_can_be_counted_without_showing_a_value(tmp_path, capsys):
    """m266 (Abram, m260, step 7): a sealed backup made on main (which keeps the field) is counted on Abram's computer;
    only the three numbers reach the screen, and nothing is written next to it."""
    public, private = backup.keygen()
    key = tmp_path / "k.key"
    key.write_text(private, encoding="utf-8")
    older = {"format": 1, "tables": {"users": [{"id": 1, "profile": {"based": "london", "foods_avoided": SECRET}},
                                               {"id": 2, "profile": json.dumps({"foods_avoided": ""})},
                                               {"id": 3, "profile": None}]}}
    sealed = tmp_path / "odys.bak"
    sealed.write_bytes(backup.seal(json.dumps(older).encode(), public))
    before = set(tmp_path.iterdir())
    assert backup.main(["count-food", str(sealed)]) == 1                          # sealed: needs the key
    assert backup.main(["count-food", str(sealed), "--key", str(key)]) == 0
    out = capsys.readouterr()
    assert out.out.strip() == "profiles 3, with_key 2, non_empty 1"
    assert SECRET not in out.out + out.err and "pork" not in out.out + out.err
    assert set(tmp_path.iterdir()) == before                                       # nothing opened onto disk


def test_the_operator_command_counts_deletes_only_the_key_and_prints_no_value(client, capsys):   # m289
    from brain import foodfield
    _, uid_a = install(client)
    _, uid_b = install(client)
    _legacy(client, uid_a, SECRET)
    url = client.app.state.engine.url.render_as_string(hide_password=False)   # str() masks the password (Postgres CI)
    assert foodfield.main(["count", "--database-url", url]) == 0
    assert foodfield.main(["delete", "--database-url", url]) == 1                  # no --confirm: nothing changes
    assert foodfield.count(client.app.state.engine)["with_key"] == 1
    assert foodfield.main(["delete", "--database-url", url, "--confirm", "delete"]) == 0
    out = capsys.readouterr()
    assert "profiles 2, with_key 1, non_empty 1" in out.out and "updated 1 profiles" in out.out
    assert "after:  profiles 2, with_key 0, non_empty 0" in out.out and "COMMITTED" in out.out
    assert SECRET not in out.out + out.err and "pork" not in out.out + out.err
    with client.app.state.Session() as s:
        assert s.get(db.User, uid_a).profile == {"based": "london", "budget_band": "20_40"}   # the rest kept
        assert s.get(db.User, uid_b) is not None                                            # no record deleted


def test_the_operator_delete_rolls_back_unless_the_count_reaches_zero(client, monkeypatch):    # m289
    from brain import foodfield
    _, uid = install(client)
    _legacy(client, uid, SECRET)
    monkeypatch.setattr(food, "scrub_profile", lambda p: p)                         # a delete that fails to remove it
    r = foodfield.delete(client.app.state.engine)
    assert not r["committed"] and r["after"]["with_key"] == 1
    with client.app.state.Session() as s:
        assert s.get(db.User, uid).profile["foods_avoided"] == SECRET                # rolled back: unchanged


def test_a_backup_is_checked_after_a_restore_in_memory_and_counted_by_table(client, tmp_path, capsys):   # m289, m288
    _, uid = install(client)
    older = json.loads(json.dumps(backup.dump(client.app.state.engine)))
    next(u for u in older["tables"]["users"] if u["id"] == uid)["profile"]["foods_avoided"] = SECRET   # made on main
    public, private = backup.keygen()
    key = tmp_path / "k.key"
    key.write_text(private, encoding="utf-8")
    sealed = tmp_path / "odys.bak"
    sealed.write_bytes(backup.seal(json.dumps(older).encode(), public))
    before = set(tmp_path.iterdir())
    assert backup.main(["count-food", str(sealed), "--key", str(key), "--after-restore"]) == 0
    assert backup.main(["counts", str(sealed), "--key", str(key)]) == 0
    out = capsys.readouterr().out
    assert "with_key 1" in out and "after a restore (in memory, nothing written): profiles 1, with_key 0" in out
    assert "users 1" in out and SECRET not in out
    assert set(tmp_path.iterdir()) == before                                        # nothing written to disk
