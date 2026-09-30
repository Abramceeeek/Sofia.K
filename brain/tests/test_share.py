"""D114: the share card's link, its page and the referral funnel for Test C's K."""
import re

from brain import share

from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)


def test_one_code_per_person(client):
    h, _ = install(client)
    a = client.get("/v1/me/referral", headers=h).json()
    b = client.get("/v1/me/referral", headers=h).json()
    assert a["code"] == b["code"] and re.fullmatch(share.CODE_PATTERN, a["code"])
    assert a["text"] == "I think you'd love this day — try it"
    h2, _ = install(client)
    assert client.get("/v1/me/referral", headers=h2).json()["code"] != a["code"]


def test_the_page_names_the_moment_and_counts_only_from_its_script(client):
    h, _ = install(client)
    code = client.get("/v1/me/referral", headers=h).json()["code"]
    r = client.get(f"/r/{code}?m=m_waterloo_bridge_sunset")
    assert r.status_code == 200
    assert "Waterloo Bridge at sunset" in r.text and f"daysout://r/{code}?m=m_waterloo_bridge_sunset" in r.text
    assert f"/r/{code}/open" in r.text                       # the counting script
    assert "closed test" in r.text                           # no TestFlight link set yet
    assert "worth" not in r.text.lower()                     # never the model's "worth £X"
    # an unknown moment is left off; an unknown code gets the page but no counting script
    assert "Waterloo" not in client.get(f"/r/{code}?m=m_nope").text
    other = "ABCDEFGH" if code != "ABCDEFGH" else "HGFEDCBA"
    assert "/open" not in client.get(f"/r/{other}").text
    assert client.get("/r/bad").status_code == 422
    # fetching the page (a link preview does this) counts nothing
    assert client.get("/v1/admin/referrals", headers=ADMIN).json()["codes"][0]["opened"] == 0


def test_the_funnel_from_share_to_first_plan(client):
    h, sharer = install(client)
    code = client.get("/v1/me/referral", headers=h).json()["code"]
    client.post("/v1/me/events", headers=h, json={"name": "share_sheet", "props": {"moment": "m_waterloo_bridge_sunset"}})
    client.post("/v1/me/events", headers=h, json={"name": "share_sent", "props": {"to": "whatsapp"}})
    assert client.post(f"/r/{code}/open", json={"m": "m_waterloo_bridge_sunset"}).status_code == 204
    client.post(f"/r/{code}/open", json={"m": "<script>"})    # an unknown moment still counts the opening
    client.post("/r/ABCDEFGH/open", json={})                  # an unknown code counts nothing
    # two people install through the link; one finishes onboarding and gets a plan
    h1, u1 = install(client, src=f"ref:{code}")
    install(client, src=f"ref:{code}")
    install(client, src="fb-ucl-hiking")
    client.post("/v1/me/events", headers=h1, json={"name": "onboarding_done"})
    r = client.post(f"/v1/admin/users/{u1}/plans", headers=ADMIN,
                    json={"stops": [{"moment_id": "m_waterloo_bridge_sunset", "arrive": "17:00"}]})
    assert r.status_code == 201
    f = client.get("/v1/admin/referrals", headers=ADMIN).json()
    row = next(c for c in f["codes"] if c["code"] == code)
    assert {k: row[k] for k in ("share_sheets", "shared", "opened", "installed", "onboarded", "first_plan")} == \
        {"share_sheets": 1, "shared": 1, "opened": 2, "installed": 2, "onboarded": 1, "first_plan": 1}
    assert row["sharer_channel"] == "stranger" and f["by_channel"]["stranger"]["sharers"] == 1
    assert client.get("/v1/admin/referrals").status_code == 403


def test_deleting_the_sharer_removes_their_code(client):
    h, _ = install(client)
    code = client.get("/v1/me/referral", headers=h).json()["code"]
    assert client.delete("/v1/me", headers=h).status_code == 204
    assert all(c["code"] != code for c in client.get("/v1/admin/referrals", headers=ADMIN).json()["codes"])
    assert "/open" not in client.get(f"/r/{code}").text
