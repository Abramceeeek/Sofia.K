"""D118: a Help & safety message can now be answered: in the app, and by phone or email if the person left one."""
from datetime import datetime, timedelta, timezone

from brain import db, notify, reasons
from brain.config import DATA_DIR
from brain.moments import load_moments

from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)


def test_reply_reaches_the_person_and_the_contact_is_deleted_when_resolved(client):
    h, uid = install(client)
    r = client.post("/v1/me/safety", headers=h, json={"message": "Lost my group", "contact": " 07700 900123 "})
    assert r.status_code == 201
    assert "999" in r.json()["message"] and "within a few hours" in r.json()["message"]
    assert "here in Help & safety" in r.json()["message"]
    alert = client.get("/v1/admin/safety", headers=ADMIN).json()[0]
    assert alert["contact"] == "07700 900123" and alert["replies"] == []
    mine = client.get("/v1/me/safety", headers=h).json()
    assert mine[0]["message"] == "Lost my group" and mine[0]["contact_kept"] and mine[0]["replies"] == []

    r = client.post(f"/v1/admin/safety/{alert['id']}/reply", headers=ADMIN,
                    json={"replied_by": "abram", "text": "Hi, it's Abram. Are you somewhere safe?"})
    assert r.status_code == 200 and r.json()["resolved"] is False
    assert client.get("/v1/admin/safety", headers=ADMIN).json() == []          # no longer waiting for a first reply
    mine = client.get("/v1/me/safety", headers=h).json()
    assert mine[0]["replies"][0]["text"] == "Hi, it's Abram. Are you somewhere safe?" and mine[0]["contact_kept"]

    client.post(f"/v1/admin/safety/{alert['id']}/reply", headers=ADMIN, json={"replied_by": "abram", "resolved": True})
    every = client.get("/v1/admin/safety?all=true", headers=ADMIN).json()
    assert every[0]["contact"] is None and len(every[0]["replies"]) == 1
    assert client.get("/v1/me/safety", headers=h).json()[0]["contact_kept"] is False
    ex = client.get("/v1/admin/export", headers=ADMIN).json()
    assert "safety_contacts" not in ex and len(ex["safety_replies"]) == 1
    # another person never sees it, and deleting the person deletes it all
    h2, _ = install(client)
    assert client.get("/v1/me/safety", headers=h2).json() == []
    client.delete("/v1/me", headers=h)
    assert client.get("/v1/admin/safety?all=true", headers=ADMIN).json() == []


def test_a_blank_contact_is_not_kept_and_old_contacts_are_purged(client):
    h, _ = install(client)
    client.post("/v1/me/safety", headers=h, json={"message": "x", "contact": "   "})
    assert client.get("/v1/admin/safety", headers=ADMIN).json()[0]["contact"] is None
    client.post("/v1/me/safety", headers=h, json={"message": "y", "contact": "me@example.com"})
    with client.app.state.Session() as s:   # pretend it was left 31 days ago
        c = s.query(db.SafetyContact).one()
        c.created_at = datetime.now(timezone.utc) - timedelta(days=31)
        s.commit()
    assert all(a["contact"] is None for a in client.get("/v1/admin/safety", headers=ADMIN).json())


def test_the_alert_text_never_promises_faster_than_a_few_hours():
    assert "within a few hours" in notify.USER_MESSAGE and "minutes" not in notify.USER_MESSAGE
    assert notify.USER_MESSAGE.startswith("If you or someone else is in danger or hurt, call 999 now.")


def test_feeling_words_only_when_the_stops_carry_them():
    ms = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
    green = [{"moment_id": "m_park_break_battersea"}, {"moment_id": "m_greenwich_wolfe_view"}]
    assert reasons.day_feelings(green, ms, ["restored", "excited"]) == ["restored"]
    assert reasons.day_feelings(green, ms, []) == []
    line = reasons.feel_line([{**st, "lunch": False} for st in green], ms, ["restored"])
    assert line.startswith("A restoring day: ")
    plain = reasons.feel_line([{**st, "lunch": False} for st in green], ms)
    assert reasons.feel_line([{**st, "lunch": False} for st in green], ms, ["excited"]) == plain   # not carried
    assert line == "A restoring day: " + plain[:1].lower() + plain[1:]
