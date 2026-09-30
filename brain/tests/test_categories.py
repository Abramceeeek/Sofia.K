"""D116: "Where are you based?", the visitors' category cards and their own cohort."""
from brain.categories import category_observation, cohort, load_categories
from brain.config import DATA_DIR
from brain.moments import load_moments
from brain.population import load_population
from brain.scoring import update_person

from test_api import ADMIN, client, install  # noqa: F401  (the client fixture)

POP = load_population(DATA_DIR / "priors.yaml")
CATS = load_categories(DATA_DIR / "categories.yaml")
READY = {m.id for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}


def test_every_card_has_a_ready_example_with_a_photo_and_real_features():
    import json
    photos = json.load(open(DATA_DIR.parent.parent / "app/Sources/Photos/photo-credits.json"))
    assert len(CATS.items) == 8
    for c in CATS.items.values():
        assert c.example in READY and c.example in photos, c.key
        assert set(c.moment.features.place) | set(c.moment.features.moment) <= set(POP.names)
        assert c.phrase == c.phrase.lower()


def test_answers_move_the_right_weights():
    names = POP.personal_names
    museums, views = CATS.items["big_museums"], CATS.items["views_above"]
    loved = update_person(POP, [category_observation(POP, museums, "loved", None)])
    assert loved.mean[names.index("history_culture")] > 0.1
    want = update_person(POP, [category_observation(POP, views, "never_tried", "yes")])
    assert want.mean[names.index("awe")] > 0
    assert category_observation(POP, views, "never_tried", "maybe") is None
    assert category_observation(POP, views, "skip", None) is None


def test_cohort():
    assert cohort({"based": "abroad"}) == "visitor"
    assert cohort({"based": "london"}) == cohort({"based": "uk"}) == cohort({}) == cohort(None) == "resident"


def test_a_visitor_answers_categories_and_is_its_own_cohort(client):
    h, uid = install(client)
    ob = client.get("/v1/onboarding", headers=h).json()
    assert ob["based"]["options"] == ["london", "uk", "abroad"]
    assert [c["key"] for c in ob["category_cards"]][:2] == ["big_museums", "art_galleries"]
    assert ob["categories"]["want_prompt"] == "Would you like to try it in London?"
    assert client.put("/v1/me/profile", headers=h, json={"based": "abroad", "home_city": "Tashkent"}).status_code == 204
    r = client.post("/v1/me/categories", headers=h, json={"items": [
        {"key": "big_museums", "reaction": "loved"}, {"key": "views_above", "reaction": "never_tried", "want": "yes"},
        {"key": "parks", "reaction": "skip"}]})
    assert r.status_code == 204
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == 2
    assert client.post("/v1/me/categories", headers=h,
                       json={"items": [{"key": "nope", "reaction": "loved"}]}).status_code == 422
    assert client.put("/v1/me/profile", headers=h, json={"based": "mars"}).status_code == 422
    # a later save without "based" (e.g. "Improve future plans") keeps it, so the cohort can't flip
    assert client.put("/v1/me/profile", headers=h, json={"company": "solo"}).status_code == 204
    h2, uid2 = install(client)
    client.put("/v1/me/profile", headers=h2, json={"based": "london"})
    ex = client.get("/v1/admin/export", headers=ADMIN).json()
    assert ex["cohorts"][uid] == "visitor" and ex["cohorts"][uid2] == "resident"
    assert len(ex["category_answers"]) == 3
    p = client.post("/v1/me/plans", headers=h, json={"start": {"lat": 51.507819, "lon": -0.126137},
                                                     "start_name": "Charing Cross station", "date": "2026-10-31"}).json()
    assert p["basis"]["kinds"] == 2


def test_visitor_reasons_name_the_kind_of_place():
    import numpy as np
    from brain import reasons
    ready = {m.id: m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
    names = POP.personal_names
    d = np.zeros(len(names)); d[names.index("history_culture")] = 0.5; d[names.index("awe")] = 0.1
    museums, views = CATS.items["big_museums"], CATS.items["views_above"]
    r = reasons.stop_reasons(POP, d, ready["m_national_gallery"], loved=[], feelings=[], rated=[], interests=[],
                             n_choices=0, loved_kinds=[(museums.phrase, museums.moment)],
                             wanted=[(views.phrase, views.moment)])
    assert r[0] == {"you": "You love big museums, and this has history.",
                    "me": "I love big museums, and this has history."}
