"""m320 (Abram, 21 Nov: "Seville in the app, me only"): the Seville preview, read-only, behind its code."""
from datetime import date

from brain import preview

from test_api import client, install  # noqa: F401  (the API fixture)

SUNDAY = date(2026, 11, 22)


def test_without_the_code_nothing_shows_and_the_trip_list_is_unchanged(client):
    h, _ = install(client)
    assert client.get("/v1/me/previews", headers=h).json() == {"previews": []}
    assert client.get("/v1/me/previews/seville", headers=h).status_code == 404
    assert [d["key"] for d in client.get("/v1/trips/destinations", headers=h).json()] == ["london"]


def test_a_wrong_code_opens_nothing_and_stores_nothing(client):
    h, _ = install(client)
    r = client.post("/v1/me/previews", headers=h, json={"code": "seville"})
    assert r.status_code == 404 and r.json()["detail"] == "That code doesn't open a preview."
    assert client.get("/v1/me/previews", headers=h).json() == {"previews": []}


def test_the_code_opens_seville_for_this_install_only_and_survives_a_profile_save(client):
    h, _ = install(client)
    other, _ = install(client)
    r = client.post("/v1/me/previews", headers=h, json={"code": " odys seville "})   # typed loosely
    assert r.status_code == 200
    assert r.json()["previews"] == [{"key": "seville", "name": "Seville", "country": "ES", "country_name": "Spain",
                                     "label": "Preview: not fully supported", "emergency_number": "112"}]
    assert client.post("/v1/me/previews", headers=h, json={"code": "ODYS-SEVILLE"}).status_code == 200   # twice: once
    assert client.put("/v1/me/profile", headers=h, json={"company": "friends"}).status_code == 204
    assert [p["key"] for p in client.get("/v1/me/previews", headers=h).json()["previews"]] == ["seville"]
    assert client.get("/v1/me/previews", headers=other).json() == {"previews": []}
    assert client.get("/v1/me/previews/seville", headers=other).status_code == 404
    body = client.get("/v1/me/previews/seville", headers=h).json()
    assert body["emergency"]["number"] == "112" and len(body["places"]) == 20 and len(body["days"]) == 7
    # still not a trip destination: nothing can be planned, searched or booked for it
    assert [d["key"] for d in client.get("/v1/trips/destinations", headers=h).json()] == ["london"]
    assert client.post("/v1/trips/flights", headers=h, json={"origin": "LHR", "destination": "seville",
                                                             "depart_date": "2026-12-01"}).status_code == 422


def test_the_content_says_what_the_sheet_says():
    c = preview.content(preview.load_previews()["seville"], SUNDAY)
    assert c["label"] == "Preview: not fully supported" and "don't rely on it alone" in c["caveat"]
    assert c["timezone"] == "Europe/Madrid" and c["currency"] == "EUR"
    assert [d["label"] for d in c["days"]] == ["Sun 22", "Mon 23", "Tue 24", "Wed 25", "Thu 26", "Fri 27", "Sat 28"]
    by = {p["id"].split(":")[-1]: p for p in c["places"]}
    assert all(s == "shut" for s in (by[k]["states"][0] for k in ("mercado-triana", "mercado-feria",
                                                                  "mercado-encarnacion", "mercado-arenal")))
    assert by["mercado-triana"]["states"][1] == "open"
    assert by["bellas-artes"]["states"][:2] == ["open", "shut"]               # Sundays 09:00-15:00; closed Mondays
    assert by["archivo-indias"]["states"][2] == "check"                       # the 2025 leaflet: never "open"
    assert by["alcazar"]["price"] == "€15.50" and by["plaza-espana"]["price"].startswith("Free (as printed")
    assert by["casa-robles"]["price"] == "Price not printed"
    assert by["alcazar"]["access"] == "Step-free access not known"            # unknown, never "no"
    assert by["baile-flamenco"]["access"] == "Step-free (the venue says)"
    assert any("8 Dec 2026" in n for n in by["catedral"]["notices"])
    assert all(p["hours_source"] is None or p["hours_source"].startswith("http") for p in c["places"])
    kinds = [p["kind"] for p in c["places"]]
    assert kinds.index("Markets and food") > kinds.index("Museums and monuments")   # the sheet's order
    assert any("journey times" in n for n in c["not_covered"]) and c["airport"]
    words = str({k: v for k, v in c.items() if k != "places"}) + str([{k: v for k, v in p.items()
                                                                       if k not in ("lat", "lon")} for p in c["places"]])
    for word in ("vegetar", "vegan", "halal", "gluten", "allerg", "999"):   # (the coordinates hold "-5.999…")
        assert word not in words.lower(), word


def test_a_preview_day_is_the_destination_s_own_date():
    c = preview.content(preview.load_previews()["seville"])                   # no date: today in Madrid
    assert len(c["days"]) == 7 and c["days"][0]["date"] >= "2026-11-20"
