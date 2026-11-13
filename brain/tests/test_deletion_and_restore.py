"""SEC-09 and SEC-10 (Abram, 12 Nov 2026), and the per-install search quota: decisions/security-release-proposal.md.

SEC-10's rule: a restored backup never brings back an install whose data was deleted, whether the deletion is in that
backup or in a newer one passed with it, however many times it is restored; and a damaged or incomplete backup is
refused before anything is written."""

import json
from dataclasses import replace
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from fastapi.testclient import TestClient

from brain import backup, db, notify, trips
from brain.api import create_app
from brain.trips import ProviderError, TripSearch

from test_api import ADMIN, client, install  # noqa: F401  (the fixture)


def _with_backups(client):
    public, private = backup.keygen()
    client.app.state.settings = replace(client.app.state.settings, backup_key=public, backup_token="nightly")
    return private


def _backup(client, private) -> dict:
    r = client.get("/v1/admin/backup", headers={"Authorization": "Bearer nightly"})
    assert r.status_code == 200
    return json.loads(backup.unseal(r.content, private))


def _someone(client, words="PRIVATE ANSWER"):
    h, uid = install(client)
    client.post("/v1/me/answers", headers=h, json={"items": [{"question": "best_hour", "text": words}]})
    client.post("/v1/me/safety", headers=h, json={"message": "a worry", "contact": "someone@example.com"})
    client.post("/v1/me/ratings", headers=h, json={"moment_id": "t_view", "rating": 4})
    return h, uid


def _restored(tmp_path, name, data, extra=()):
    engine = db.make_engine(f"sqlite:///{tmp_path / name}")
    counts = backup.restore(engine, data, list(extra))
    with db.make_sessionmaker(engine)() as s:
        users = {u.id for u in s.scalars(select(db.User))}
        text = json.dumps([[a.text for a in s.scalars(select(db.Answer))],
                           [m.message for m in s.scalars(select(db.SafetyAlert))]])
        hashes = {d.user_hash for d in s.scalars(select(db.Deletion))}
    return counts, users, text, hashes


# ---- deletion leaves only a one-way record --------------------------------------------------------------------

def test_deleting_keeps_a_one_way_code_and_nothing_else(client):
    h, uid = _someone(client)
    assert client.delete("/v1/me", headers=h).status_code == 204
    with client.app.state.Session() as s:
        rows = list(s.scalars(select(db.Deletion)))
        assert [r.user_hash for r in rows] == [backup.deleted_key(uid)]
        assert s.get(db.User, uid) is None
    assert uid not in rows[0].user_hash and len(rows[0].user_hash) == 64
    assert backup.deleted_key(uid) != backup.deleted_key(uid + "x")


def test_the_admin_export_never_lists_deletions(client):
    h, _ = _someone(client)
    client.delete("/v1/me", headers=h)
    assert "deletions" not in client.get("/v1/admin/export", headers=ADMIN).json()


# ---- backup, restore, reapply ---------------------------------------------------------------------------------

def test_a_backup_carries_the_deletions_and_a_restore_keeps_the_person_deleted(client, tmp_path):
    private = _with_backups(client)
    stay_h, stay = _someone(client, "KEEP ME")
    gone_h, gone = _someone(client, "DELETED WORDS")
    client.delete("/v1/me", headers=gone_h)
    data = _backup(client, private)
    assert [d["user_hash"] for d in data["tables"]["deletions"]] == [backup.deleted_key(gone)]
    counts, users, text, hashes = _restored(tmp_path, "a.db", data)
    assert users == {stay} and "KEEP ME" in text and "DELETED WORDS" not in text
    assert hashes == {backup.deleted_key(gone)}


def test_an_older_backup_restored_with_the_newest_one_doesn_t_bring_back_a_later_deletion(client, tmp_path):
    private = _with_backups(client)
    h, uid = _someone(client, "SAID BEFORE THE OLD BACKUP")
    old = _backup(client, private)                     # made while they were still there
    client.delete("/v1/me", headers=h)
    new = _backup(client, private)                     # made after they deleted
    _, users, text, _ = _restored(tmp_path, "without.db", old)
    assert uid in users                                 # the risk SEC-10 closes: an old backup alone brings them back
    counts, users, text, hashes = _restored(tmp_path, "with.db", old, backup.deletions_in(new))
    assert uid not in users and "SAID BEFORE" not in text and "a worry" not in text
    assert counts["removed_again"] == 1 and hashes == {backup.deleted_key(uid)}


def test_restoring_again_from_a_restored_database_s_backup_still_leaves_them_out(client, tmp_path):
    private = _with_backups(client)
    h, uid = _someone(client)
    old = _backup(client, private)
    client.delete("/v1/me", headers=h)
    new = _backup(client, private)
    first = db.make_engine(f"sqlite:///{tmp_path / 'first.db'}")
    backup.restore(first, old, backup.deletions_in(new))
    again = backup.dump(first)                           # the restored database's own next backup
    for n in range(2):                                   # restored twice more, with nothing passed alongside
        _, users, _, hashes = _restored(tmp_path, f"again{n}.db", again)
        assert uid not in users and hashes == {backup.deleted_key(uid)}


def test_a_restore_without_deletions_is_unchanged(client, tmp_path):
    private = _with_backups(client)
    _, a = _someone(client)
    _, b = _someone(client)
    counts, users, _, hashes = _restored(tmp_path, "plain.db", _backup(client, private))
    assert users == {a, b} and hashes == set() and counts["removed_again"] == 0


# ---- damaged or incomplete backups ------------------------------------------------------------------------------

def test_a_sealed_backup_changed_by_one_byte_is_refused(client, tmp_path):
    private = _with_backups(client)
    _someone(client)
    sealed = client.get("/v1/admin/backup", headers={"Authorization": "Bearer nightly"}).content
    damaged = sealed[:-10] + bytes([sealed[-10] ^ 1]) + sealed[-9:]
    with pytest.raises(backup.BackupError):
        backup.unseal(damaged, private)
    with pytest.raises(backup.BackupError):
        backup.unseal(sealed[: len(sealed) // 2], private)          # cut short


@pytest.mark.parametrize("data, why", [
    ({"format": 2, "tables": {}}, "this version can read"),
    ({"format": 1}, "no tables"),
    ({"format": 1, "tables": {"users": "x"}}, "not a list"),
    ({"format": 1, "tables": {"answers": [{"id": 1, "user_id": "u1", "question": "q", "text": "t",
                                          "input_mode": "typed"}]}}, "no users table"),
    ({"format": 1, "tables": {"users": [], "ratings": [{"id": 1, "user_id": "u1", "moment_id": "m",
                                                     "rating": 3}]}}, "point at users"),
])
def test_an_incomplete_or_inconsistent_backup_is_refused_and_nothing_is_written(tmp_path, data, why):
    problems, _ = backup.check(data)
    assert problems and any(why in p for p in problems)
    engine = db.make_engine(f"sqlite:///{tmp_path / 'x.db'}")
    with pytest.raises(backup.BackupError, match="can't be restored"):
        backup.restore(engine, data)
    with db.make_sessionmaker(engine)() as s:
        assert s.scalar(select(db.User)) is None


def test_a_table_the_backup_predates_is_noted_not_refused(tmp_path):
    data = {"format": 1, "tables": {"users": []}}          # e.g. a backup from before deletions existed
    problems, notes = backup.check(data)
    assert problems == [] and "deletions" in notes[0]
    assert backup.restore(db.make_engine(f"sqlite:///{tmp_path / 'old.db'}"), data)["deletions"] == 0


def test_the_verify_and_restore_commands(client, tmp_path, capsys):
    private = _with_backups(client)
    h, uid = _someone(client)
    old_sealed = client.get("/v1/admin/backup", headers={"Authorization": "Bearer nightly"}).content
    client.delete("/v1/me", headers=h)
    client.app.state.limiter = type(client.app.state.limiter)()     # a new night: the backup cap starts again
    new_sealed = client.get("/v1/admin/backup", headers={"Authorization": "Bearer nightly"}).content
    key, old, new = tmp_path / "k.key", tmp_path / "old.odysbk", tmp_path / "new.odysbk"
    key.write_text(private)
    old.write_bytes(old_sealed)
    new.write_bytes(new_sealed)
    assert backup.main(["verify", str(old), "--key", str(key)]) == 0
    assert "Whole and consistent." in capsys.readouterr().out
    cut = tmp_path / "cut.json"
    cut.write_text(json.dumps(json.loads(backup.unseal(old_sealed, private)))[:200])
    assert backup.main(["verify", str(cut)]) == 1
    assert "isn't a whole backup" in capsys.readouterr().err
    url = f"sqlite:///{tmp_path / 'r.db'}"
    assert backup.main(["restore", str(old), "--key", str(key), "--deletions", str(new), "--database-url", url]) == 0
    assert "removed_again 1" in capsys.readouterr().out
    with db.make_sessionmaker(db.make_engine(url))() as s:
        assert s.get(db.User, uid) is None


# ---- SEC-09: the alert says only that a message is waiting -----------------------------------------------------

def test_the_alert_carries_no_message_contact_or_id(client, monkeypatch, caplog):
    sent = []

    class Resp:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(notify.urllib.request, "urlopen", lambda req, timeout: (sent.append(req.data), Resp())[1])
    # the webhook is read when the app starts, so start one with it set (same data and database as the fixture)
    with_hook = create_app(replace(client.app.state.settings, alert_webhook_url="https://hooks.example/x"))
    lg = notify.log
    lg.addHandler(caplog.handler)
    caplog.set_level("INFO", logger="brain.safety")
    try:
        with TestClient(with_hook) as c:
            h, uid = install(c)
            r = c.post("/v1/me/safety", headers=h, json={"message": "MY PRIVATE WORRY", "contact": "07700 900123"})
    finally:
        lg.removeHandler(caplog.handler)
    assert r.status_code == 201
    posted = json.loads(sent[0])["text"]
    logged = "\n".join(rec.getMessage() for rec in caplog.records)
    for private in ("MY PRIVATE WORRY", "07700", uid, uid[:8]):
        assert private not in posted and private not in logged
    assert f"#{r.json()['alert_id']}" in posted and "GET /v1/admin/safety" in posted
    with client.app.state.Session() as s:                  # the message and contact are still there to read
        a = s.get(db.SafetyAlert, r.json()["alert_id"])
        assert a.message == "MY PRIVATE WORRY" and a.contact.contact == "07700 900123" and a.notified


def test_the_alert_text_is_fixed_wording():
    at = datetime(2026, 11, 12, 14, 5, tzinfo=timezone.utc)
    assert notify.alert_text(7, at) == ("ODYS Help & safety: message #7 is waiting (received 12 Nov 14:05, London "
                                        "time). Read it and reply with GET /v1/admin/safety; it isn't copied here.")


# ---- one install can't use up the day's searches -------------------------------------------------------------------

def test_one_install_uses_at_most_its_share_of_the_day_s_searches():
    ts = TripSearch(airports=[], destinations={}, per_hour=1000, per_day_each=3, per_day_all=10)
    for i in range(3):
        ts._cached(f"q{i}", "one", lambda: [])
    with pytest.raises(ProviderError, match="too_many_today"):
        ts._cached("q9", "one", lambda: [])
    for i in range(3):                                      # others still can
        ts._cached(f"r{i}", "two", lambda: [])
    assert ts._cached("q0", "one", lambda: 1 / 0) == []     # a kept result still answers


def test_the_day_s_limit_is_said_plainly(client, monkeypatch):
    h, _ = install(client)

    def no_more(*a, **k):
        raise ProviderError("too_many_today")
    monkeypatch.setattr(client.app.state.trips, "flights", no_more)
    r = client.post("/v1/trips/flights", headers=h, json={"origin": "EDI", "depart_date": "2026-12-05"})
    assert r.status_code == 429 and "for one day" in r.json()["detail"]


# ---- SEC-05: the address check is the admin's own, and keeps nothing --------------------------------------------

def test_the_address_check_is_admin_only_and_shows_the_header_chain(client):
    h, _ = install(client)
    assert client.get("/v1/admin/client-address", headers=h).status_code == 403
    r = client.get("/v1/admin/client-address", headers={**ADMIN, "CF-Connecting-IP": "203.0.113.5",
                                                        "X-Forwarded-For": "10.9.9.9, 198.51.100.1"}).json()
    assert r["cf_connecting_ip"] == "203.0.113.5" and r["x_forwarded_for"] == ["10.9.9.9", "198.51.100.1"]
    assert r["counted_as"] == "203.0.113.5"
