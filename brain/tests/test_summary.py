"""D117: reactions between answers, "So far, I've learned…", and corrections that are stored and stop counting."""
import csv

from brain import summary
from brain.config import DATA_DIR

from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)

TASKS: dict[int, dict] = {}
for _r in csv.DictReader(open(DATA_DIR / "conjoint_design.csv", encoding="utf-8")):
    TASKS.setdefault(int(_r["task"]), {})[_r["plan"]] = _r


def test_patterns_need_three_days_and_no_exceptions():
    # relaxed pace every time in 5 upfront days; walking and crowds go both ways
    relaxed = {2: "B", 4: "A", 6: "B", 8: "B", 9: "B"}
    assert summary.tendencies(relaxed, TASKS) == [
        {"id": "choice:pace", "text": "In the example days, you chose the relaxed day with fewer stops every time."}]
    assert summary.tendencies({2: "B", 4: "A"}, TASKS) == []                      # two days isn't a pattern
    assert summary.tendencies(relaxed, TASKS, corrected={"choice:pace"}) == []
    assert summary.tendencies({**relaxed, 2: "A"}, TASKS)[:1] != [               # one exception: not said
        {"id": "choice:pace", "text": "In the example days, you chose the relaxed day with fewer stops every time."}]


def test_a_corrected_attribute_drops_its_features():
    x = summary.choice_features(TASKS[2]["A"], set())
    assert x["long_walk"] == 1.0 and "transfer_30_plus" in x
    y = summary.choice_features(TASKS[2]["A"], {"choice:walking", "choice:transfer"})
    assert "long_walk" not in y and not any(k.startswith("transfer") for k in y) and y["packed_pace"] == 1.0


def test_onboarding_carries_the_reactions(client):
    h, _ = install(client)
    ob = client.get("/v1/onboarding", headers=h).json()
    brick = next(p for p in ob["swipe_places"] if p["item"] == 14)
    assert brick["reactions"] == {"loved": "Got it: local food with a bit of history.",
                                  "didnt_enjoy": "Noted: not so much local food with a bit of history."}
    assert brick["photo_ids"] == ["m_beigel_bake_late"]                           # D119: for its photo
    museums = next(c for c in ob["category_cards"] if c["key"] == "big_museums")
    assert museums["reactions"]["want_yes"] == "Noted: you'd like to try big museums."
    assert set(ob["conjoint_tasks"][0]["levels"]) == {"A", "B"} and len(ob["conjoint_tasks"][0]["levels"]["A"]) == 6
    assert [w["attr"] for w in ob["conjoint_words"]] == list(summary.ATTRIBUTES)
    assert ob["conjoint"]["prompt"].endswith("There are no wrong answers.")
    assert ob["summary"]["title"] == "So far, I've learned…"


def test_so_far_then_corrections_are_stored_and_stop_counting(client):
    h, uid = install(client)
    client.put("/v1/me/profile", headers=h, json={"why_travel": ["restored", "curious"]})
    client.post("/v1/me/swipes", headers=h, json={"items": [
        {"item": 14, "reaction": "loved"}, {"item": 6, "reaction": "didnt_enjoy"}, {"item": 4, "reaction": "fine"}]})
    client.post("/v1/me/conjoint", headers=h, json={"items": [
        {"task": t, "choice": c} for t, c in {2: "B", 4: "A", 6: "B", 8: "B", 9: "B"}.items()]})
    n_before = client.get("/v1/me/weights", headers=h).json()["n_observations"]
    items = client.get("/v1/me/summary", headers=h).json()["items"]
    texts = {i["id"]: i["text"] for i in items}
    assert texts["feeling:restored"] == "You want to feel restored on a day out."
    assert texts["place:14"] == "You loved Brick Lane for food: local food with a bit of history."
    assert texts["place:6"] == "Hyde Park wasn't for you."
    assert "choice:pace" in texts and "place:4" not in texts          # "it was fine" teaches too little to say
    assert [i["id"] for i in items][0] == "feeling:restored"          # feelings first, things not liked last

    assert client.post("/v1/me/corrections", headers=h, json={"items": ["nope"]}).status_code == 422
    r = client.post("/v1/me/corrections", headers=h, json={"items": ["place:6", "feeling:restored", "choice:pace"]})
    assert r.status_code == 204
    after = {i["id"] for i in client.get("/v1/me/summary", headers=h).json()["items"]}
    assert after.isdisjoint({"place:6", "feeling:restored", "choice:pace"}) and "place:14" in after
    # the swipe and the feeling no longer count (the choices still do, without the pace attribute)
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == n_before - 2
    ex = client.get("/v1/admin/export", headers=ADMIN).json()
    mine = [c for c in ex["corrections"] if c["user_id"] == uid]
    assert {c["item"]: c["text"] for c in mine}["place:6"] == "Hyde Park wasn't for you." and len(mine) == 3
    users = {u["id"]: u for u in ex["users"]}
    assert users[uid]["profile"]["why_travel"] == ["curious"]
    # a place name that starts "The" reads mid-sentence
    client.post("/v1/me/swipes", headers=h, json={"items": [{"item": 11, "reaction": "loved"}]})
    texts = {i["id"]: i["text"] for i in client.get("/v1/me/summary", headers=h).json()["items"]}
    assert texts["place:11"] == "You loved the view from the top of Greenwich Park: a climb to a big view."
    # deleting the person deletes their corrections too
    client.delete("/v1/me", headers=h)
    assert not [c for c in client.get("/v1/admin/export", headers=ADMIN).json()["corrections"]
                if c["user_id"] == uid]
