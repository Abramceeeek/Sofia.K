"""m358 (Abram, 25 Nov: "Include actual collaborative trip creation with separate adult accounts"; "test whether two or
three people can actually create one together, contribute their individual preferences and produce something they
all want to do"): an organiser starts a trip, friends join from their own accounts with a code and their consent, and
the shared days come from everyone's own answers. Nobody is named without agreeing, and leaving or deleting an
account removes the person's part."""
from datetime import date, timedelta

from test_api import client, install  # noqa: F401  (the client fixture)

START = (date.today() + timedelta(days=10)).isoformat()


def _trip(client, h, **kw):
    r = client.post("/v1/me/groups", headers=h, json={"start_date": START, "nights": 1, "per_day": 3,
                                                       "consent": True, **kw})
    assert r.status_code == 201, r.text
    return r.json()


def _join(client, h, code, **kw):
    return client.post("/v1/me/groups/join", headers=h, json={"code": code, "consent": True, **kw})


def _swipes(client, h, loved, disliked):
    r = client.post("/v1/me/swipes", headers=h, json={"items": [{"item": i, "reaction": "loved"} for i in loved] + [
        {"item": i, "reaction": "didnt_enjoy"} for i in disliked]})
    assert r.status_code == 204, r.text


def test_two_people_from_their_own_accounts_plan_one_trip_together(client):
    a, _ = install(client)
    b, _ = install(client)
    _swipes(client, a, loved=[4], disliked=[3])        # different tastes, so the plan has to weigh both
    _swipes(client, b, loved=[3], disliked=[4])
    g = _trip(client, a, share_preferences=True)
    assert g["you"] == "Member A" and g["code"]
    r = _join(client, b, g["code"])
    assert r.status_code == 201, r.text
    seen_by_b = r.json()
    assert seen_by_b["you"] == "Member B" and seen_by_b["code"] is None   # only the organiser holds the code
    assert [m["label"] for m in seen_by_b["members"]] == ["Member A", "Member B"]
    assert _join(client, b, g["code"]).json()["you"] == "Member B"        # joining again changes nothing
    assert [x["id"] for x in client.get("/v1/me/groups", headers=b).json()["groups"]] == [g["id"]]

    r = client.post(f"/v1/me/groups/{g['id']}/plan", headers=b)
    assert r.status_code == 200, r.text
    out = r.json()
    assert len(out["days"]) == 2 and all(len(d) == 3 for d in out["days"])
    assert all(st["title"] and st["why"] for d in out["days"] for st in d)
    assert out["your_share"].endswith("among your favourites")             # said to them, not about them
    assert len({st["id"] for d in out["days"] for st in d}) == 6          # no place twice


def test_a_shared_day_has_variety_and_stays_in_one_part_of_london():
    """m358: the first real group plan was six museums, and its first day went Greenwich → Docklands → Marylebone.
    Over 40 seeded groups of 2-4 people (2 days of 3 places), before m358: 25 of 80 days held more than two history
    stops and 62 spread over 3 km; members left without a favourite: 3. Now no day breaks D127's shape, the spread
    is measured (22 when m358 was made; held under 26 here), and fairness doesn't get worse."""
    import numpy as np
    from brain import group as grp
    from brain.catalogue import DATA_DIR, load_catalogue
    from brain.discovery import Scorer
    from brain.population import load_population
    from brain.travel import haversine_m
    pop = load_population(DATA_DIR / "priors.yaml")
    cands = [x for x in load_catalogue() if x.status == "ready"]
    rng = np.random.default_rng(7)
    spread = without = 0
    for trial in range(40):
        ms = [grp.Member(f"Member {c}", Scorer(pop, rng.normal(0, pop.delta_prior_sd))) for c in "ABCD"[:2 + trial % 3]]
        out = grp.plan(ms, cands, days=2, per_day=3)
        without += sum(not v for v in out.proportional.values())
        for day in out.days:
            assert sum((x.features.get("history_culture") or 0) >= 2 for x in day) <= 2, [x.title for x in day]
            spread += max(haversine_m(day[0].geo, x.geo) for x in day) > 3000
    assert spread <= 25 and without <= 3, (spread, without)


def test_each_members_own_no_is_kept_and_a_place_they_loved_comes_in(client):
    """m358: the apps say "a place one of you said no to is left out", so a member's "Didn't enjoy it" places are a
    veto; and each member's first loved place with a ready card is their must-see (the example trip had no food for
    the person who loved Borough Market), said first in its reason."""
    a, _ = install(client)
    b, _ = install(client)
    _swipes(client, a, loved=[3], disliked=[])     # Borough Market (m_borough_market_graze)
    _swipes(client, b, loved=[], disliked=[2])     # the Uber Boat (m_uber_boat_west_day and _night)
    g = _trip(client, a)
    assert _join(client, b, g["code"]).status_code == 201
    out = client.post(f"/v1/me/groups/{g['id']}/plan", headers=b).json()
    stops = {st["id"]: st for d in out["days"] for st in d}
    market = next(i for i in stops if "borough-market" in i)
    assert stops[market]["why"].startswith("A place someone in the group loved")   # neither agreed (m361)
    assert not any("uber-boat" in i for i in stops)
    assert any("rejected" in n for n in out["notes"])


def test_nobody_is_named_without_agreeing(client):
    a, _ = install(client)
    b, _ = install(client)
    c, _ = install(client)
    g = _trip(client, a, share_preferences=True)
    assert _join(client, b, g["code"]).status_code == 201                  # B didn't agree to be named
    assert _join(client, c, g["code"], share_preferences=True).status_code == 201
    out = client.post(f"/v1/me/groups/{g['id']}/plan", headers=a).json()
    text = " ".join([st["why"] for d in out["days"] for st in d] + out["notes"])
    assert "Member B" not in text
    members = out["group"]["members"]
    assert [m["named"] for m in members] == [True, False, True]
    assert set(out["group"]) == {"id", "settings", "you", "code", "members"}   # no one's answers, budget or pace


def test_consent_and_membership_are_checked(client):
    a, _ = install(client)
    b, _ = install(client)
    stranger, _ = install(client)
    g = _trip(client, a)
    assert client.post("/v1/me/groups/join", headers=b, json={"code": g["code"]}).status_code == 422
    assert client.post("/v1/me/groups/join", headers=b, json={"code": g["code"], "consent": False}).status_code == 422
    assert client.post("/v1/me/groups", headers=a, json={"start_date": START}).status_code == 422
    assert _join(client, b, "ZZZZZZZZ").status_code == 404
    assert client.post(f"/v1/me/groups/{g['id']}/plan", headers=a).status_code == 422   # alone isn't a group
    for path in (f"/v1/me/groups/{g['id']}",):
        assert client.get(path, headers=stranger).status_code == 404       # not found, never "forbidden"
    assert client.post(f"/v1/me/groups/{g['id']}/plan", headers=stranger).status_code == 404
    assert client.post(f"/v1/me/groups/{g['id']}/leave", headers=stranger).status_code == 404


def test_a_trip_holds_six_people(client):
    a, _ = install(client)
    g = _trip(client, a)
    for _ in range(5):
        h, _ = install(client)
        assert _join(client, h, g["code"]).status_code == 201
    late, _ = install(client)
    assert _join(client, late, g["code"]).status_code == 409


def test_leaving_and_deleting_an_account_remove_the_persons_part(client):
    a, _ = install(client)
    b, _ = install(client)
    c, _ = install(client)
    g = _trip(client, a)
    for h in (b, c):
        assert _join(client, h, g["code"]).status_code == 201
    assert client.post(f"/v1/me/groups/{g['id']}/leave", headers=b).status_code == 204
    assert client.get(f"/v1/me/groups/{g['id']}", headers=b).status_code == 404
    assert [m["label"] for m in client.get(f"/v1/me/groups/{g['id']}", headers=a).json()["members"]] == [
        "Member A", "Member C"]
    assert client.delete("/v1/me", headers=c).status_code == 204             # deleting the account removes them too
    assert [m["label"] for m in client.get(f"/v1/me/groups/{g['id']}", headers=a).json()["members"]] == ["Member A"]
    d, _ = install(client)
    assert _join(client, d, g["code"]).json()["you"] == "Member B"           # a free label is reused
    assert client.post(f"/v1/me/groups/{g['id']}/leave", headers=a).status_code == 204   # the organiser ends it
    assert client.get(f"/v1/me/groups/{g['id']}", headers=d).status_code == 404


def test_deleting_the_organisers_account_ends_the_trip(client):
    a, _ = install(client)
    b, _ = install(client)
    g = _trip(client, a)
    assert _join(client, b, g["code"]).status_code == 201
    assert client.delete("/v1/me", headers=a).status_code == 204
    assert client.get(f"/v1/me/groups/{g['id']}", headers=b).status_code == 404
    assert _join(client, b, g["code"]).status_code == 404
