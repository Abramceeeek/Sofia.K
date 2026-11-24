"""m327 (Abram, 24 Nov): every plan records the Brain commit and the app build, so feedback is read per version."""
from datetime import date, timedelta

from brain import db, versions

from test_api import client, install  # noqa: F401  (the API fixture)


def test_a_plan_records_the_brain_commit_and_the_app_build(client, monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "c2513fa9f08b0a5e04af12e3ceffde488ce19354")
    h, uid = install(client)
    start = (date.today() + timedelta(days=3)).isoformat()
    r = client.post("/v1/me/trips/days", headers={**h, "X-ODYS-Build": "ios-114"},
                    json={"start_date": start, "nights": 0})
    assert r.status_code == 201, r.text
    with client.app.state.Session() as s:
        plans = s.query(db.Plan).filter_by(user_id=uid).all()
    assert plans and all(p.intent["versions"] == {"brain": "c2513fa", "app": "ios-114"} for p in plans)


def test_only_a_build_identifier_is_kept_never_free_text():
    assert versions.app_build("android-22") == "android-22" and versions.app_build(" iOS-114 ") == "ios-114"
    assert versions.app_build("ios-114; drop table") is None and versions.app_build("my name") is None
    assert versions.app_build(None) is None
