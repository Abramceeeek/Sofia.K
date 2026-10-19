"""Stage 1, steps 5 and 6: the request log (no personal data), error alerts, rate limits and the sealed backup."""

import json
import logging
from dataclasses import replace

import pytest
from fastapi import HTTPException

from brain import backup, db, ops, trips
from brain.trips import ProviderError, TripSearch

from test_api import ADMIN, client, install  # noqa: F401  (the fixture)


@pytest.fixture
def lines(caplog):
    """The request log's lines (the brain logger doesn't pass its lines up, so listen to it directly)."""
    lg = logging.getLogger("brain.requests")
    lg.addHandler(caplog.handler)
    caplog.set_level(logging.INFO, logger="brain.requests")
    yield lambda: [r.getMessage() for r in caplog.records if r.name == "brain.requests"]
    lg.removeHandler(caplog.handler)


def test_the_request_log_holds_the_route_pattern_and_nothing_personal(client, lines):
    h, uid = install(client)
    token = h["Authorization"].split()[1]
    client.get("/v1/me/plans/12345?secret=abc", headers={**h, "X-Forwarded-For": "203.0.113.9"})
    text = "\n".join(lines())
    assert "GET /v1/me/plans/{plan_id} 404" in text and "POST /v1/installs 201" in text
    for private in (token, uid, "12345", "secret", "abc", "203.0.113.9", "testclient"):
        assert private not in text


def test_too_many_plans_from_one_phone_get_a_429_with_retry_after(client, monkeypatch):
    monkeypatch.setitem(ops.LIMITS, "plan", (2, 600))
    h, _ = install(client)
    other, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "12:00", "end_time": "15:00", "stops": 2}
    assert [client.post("/v1/me/plans", headers=h, json=body).status_code for _ in range(2)] == [201, 201]
    r = client.post("/v1/me/plans", headers=h, json=body)
    assert r.status_code == 429 and 1 <= int(r.headers["Retry-After"]) <= 601
    assert r.json()["detail"].startswith("That's a lot in a short time")
    assert client.post("/v1/me/plans", headers=other, json=body).status_code == 201   # another phone isn't held up
    assert client.get("/v1/me/plans", headers=h).status_code == 200                    # nor other requests


def test_new_installs_are_limited_per_address_and_overall(client, monkeypatch):
    monkeypatch.setitem(ops.LIMITS, "install", (2, 3600))
    monkeypatch.setattr(ops, "INSTALLS_ALL", (3, 3600))
    body = {"channel": "stranger", "consent": {"version": "2026-09", "research": True, "ai_processing": False}}
    at = lambda ip: client.post("/v1/installs", json=body, headers={"X-Forwarded-For": f"{ip}, 10.0.0.1"}).status_code
    assert [at("198.51.100.1"), at("198.51.100.1"), at("198.51.100.1")] == [201, 201, 429]
    assert at("198.51.100.2") == 201      # another address
    assert at("198.51.100.3") == 429      # but no more than INSTALLS_ALL from everyone, whatever the address says


def test_the_health_check_is_never_limited(client, monkeypatch):
    monkeypatch.setitem(ops.LIMITS, "public", (1, 60))
    assert all(client.get("/v1/health").status_code == 200 for _ in range(5))


def test_an_error_is_a_plain_500_and_one_alert_without_the_request(client, lines):
    posts = []
    client.app.state.alerts = ops.Alerts("https://hooks.example/ops", post=lambda url, body: posts.append(body))

    def boom(secret: str = "x"):
        raise KeyError("a tester's words")
    client.app.add_api_route("/v1/boom/{secret}", boom)
    for _ in range(3):
        r = client.get("/v1/boom/abc123")
        assert r.status_code == 500 and r.json()["detail"].startswith("Something went wrong on our side")
    assert len(posts) == 1                                  # once an hour for the same error
    msg = posts[0]["text"]
    assert "not a safety alert" in msg and "GET /v1/boom/{secret}" in msg and "KeyError" in msg
    assert "abc123" not in msg and "tester's words" not in msg
    assert "GET /v1/boom/{secret} 500" in "\n".join(lines())


def test_alerts_stop_at_twenty_a_day():
    t = [0.0]
    sent = []
    a = ops.Alerts("https://hooks.example/ops", clock=lambda: t[0], post=lambda u, b: sent.append(b))
    for i in range(30):
        a.error("GET", f"/v1/r{i}", "ValueError")
    assert len(sent) == ops.ALERTS_PER_DAY
    t[0] += 86400
    assert a.error("GET", "/v1/again", "ValueError") is True
    assert ops.Alerts(None).error("GET", "/x", "E") is False   # no webhook: logged only


def test_provider_searches_have_a_daily_cap_for_everyone():
    calls = []
    ts = TripSearch(airports=[], destinations={}, duffel_token="duffel_test_x", per_day_all=2,
                    fetch=lambda *a, **k: calls.append(1) or {"data": {"offers": []}})
    ts._cached("q1", "anna", lambda: [])
    ts._cached("q2", "ben", lambda: [])
    with pytest.raises(ProviderError, match="daily_cap"):
        ts._cached("q3", "cara", lambda: [])
    assert ts._cached("q1", "dan", lambda: 1 / 0) == []    # a kept result still answers


# ---- the sealed backup ----------------------------------------------------------------------------------------

def test_a_sealed_backup_opens_only_with_its_key_and_restores(client, tmp_path):
    public, private = backup.keygen()
    h, uid = install(client)
    client.post("/v1/me/safety", headers=h, json={"message": "lost", "contact": "07700 900123"})
    with client.app.state.Session() as s:
        assert s.query(db.SafetyContact).count() == 1    # held live, to reply…
    assert client.get("/v1/admin/backup", headers=ADMIN).status_code == 503        # no public key yet
    client.app.state.settings = replace(client.app.state.settings, backup_key=public, backup_token="nightly")
    assert client.get("/v1/admin/backup", headers={"Authorization": "Bearer wrong"}).status_code == 403
    r = client.get("/v1/admin/backup", headers={"Authorization": "Bearer nightly"})
    assert r.status_code == 200 and r.content.startswith(backup.MAGIC)
    assert b"07700" not in r.content and uid.encode() not in r.content               # sealed
    other_public, other_private = backup.keygen()
    with pytest.raises(backup.BackupError):
        backup.unseal(r.content, other_private)
    data = json.loads(backup.unseal(r.content, private))
    assert [u["id"] for u in data["tables"]["users"]] == [uid]
    assert "safety_contacts" not in data["tables"] and "moments" not in data["tables"]   # D118; rebuilt at start
    assert "07700" not in json.dumps(data)
    engine = db.make_engine(f"sqlite:///{tmp_path / 'restored.db'}")
    counts = backup.restore(engine, data)
    assert counts["users"] == 1 and counts["safety_alerts"] == 1
    Session = db.make_sessionmaker(engine)
    with Session() as s:
        u = s.get(db.User, uid)
        assert u.created_at is not None and u.token_hash == data["tables"]["users"][0]["token_hash"]
    with pytest.raises(backup.BackupError, match="already has rows"):
        backup.restore(engine, data)


def test_a_wrong_public_key_is_said_plainly():
    with pytest.raises(backup.BackupError, match="keygen"):
        backup.seal(b"x", "not-a-key")


def test_the_keygen_command_writes_the_private_key_once(tmp_path, capsys):
    out = tmp_path / "k.key"
    assert backup.main(["keygen", "--out", str(out)]) == 0
    printed = capsys.readouterr().out.strip().splitlines()
    public = printed[printed.index(next(x for x in printed if "BRAIN_BACKUP_PUBLIC_KEY" in x)) + 1]
    assert "BRAIN_BACKUP_TOKEN" in printed[-2] and len(printed[-1]) >= 40
    assert backup.unseal(backup.seal(b"hello", public), out.read_text()) == b"hello"
    assert backup.main(["keygen", "--out", str(out)]) == 1        # never overwrites a key


def test_keys_saved_under_other_names_are_found(monkeypatch):
    from brain.config import get_settings
    for n in list(__import__("os").environ):
        if any(w in n.upper() for w in ("TFL", "MET", "WEATHER", "DATAHUB")):
            monkeypatch.delenv(n, raising=False)
    assert get_settings().met_office_key is None and get_settings().tfl_app_key is None
    monkeypatch.setenv("Met Office DataHub api", " abc ")
    monkeypatch.setenv("TFL_UNIFIED_API_KEY", "xyz")
    s = get_settings()
    assert s.met_office_key == "abc" and s.tfl_app_key == "xyz"
    monkeypatch.setenv("MET_OFFICE_API_KEY", "exact")          # an exact name wins
    assert get_settings().met_office_key == "exact"
