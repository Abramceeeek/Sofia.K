"""D120: trips: flights and stays from the providers' documented responses, the filters and sorts, links out, sample
mode, the cache and the hourly cap. Never a booking, never money."""
from datetime import date, timedelta

import pytest

from brain import trips
from brain.config import DATA_DIR

from test_api import client, install  # noqa: F401  (the client fixture)

AIRPORTS, DESTS = trips.load_places(DATA_DIR / "airports.yaml")


def _segment(o, d, dep, arr, dur, code="BA", num="123", bags=1):
    return {"origin": {"iata_code": o}, "destination": {"iata_code": d}, "departing_at": dep, "arriving_at": arr,
            "duration": dur, "marketing_carrier": {"name": "British Airways", "iata_code": code},
            "marketing_carrier_flight_number": num, "operating_carrier": {"name": "British Airways", "iata_code": code},
            "passengers": [{"baggages": [{"type": "checked", "quantity": bags}, {"type": "carry_on", "quantity": 1}]}]}


DUFFEL = {"data": {"offers": [
    {"id": "off_1", "total_amount": "512.40", "total_currency": "GBP",
     "owner": {"name": "British Airways", "iata_code": "BA"},
     "conditions": {"refund_before_departure": {"allowed": False}, "change_before_departure": {"allowed": True}},
     "slices": [{"duration": "PT7H10M", "segments": [_segment("TAS", "LHR", "2026-11-20T08:35:00", "2026-11-20T10:45:00",
                                                              "PT7H10M")]},
                {"duration": "PT6H50M", "segments": [_segment("LHR", "TAS", "2026-11-27T21:00:00", "2026-11-28T08:50:00",
                                                              "PT6H50M", num="124")]}]},
    {"id": "off_2", "total_amount": "389.00", "total_currency": "GBP",
     "owner": {"name": "Turkish Airlines", "iata_code": "TK"}, "conditions": {},
     "slices": [{"duration": "PT11H05M", "segments": [_segment("TAS", "IST", "2026-11-20T06:10:00", "2026-11-20T09:15:00",
                                                               "PT5H05M", "TK", "371", 0),
                                                      _segment("IST", "LHR", "2026-11-20T12:30:00", "2026-11-20T14:40:00",
                                                               "PT4H10M", "TK", "1971", 0)]},
                {"duration": "PT10H30M", "segments": [_segment("LHR", "IST", "2026-11-27T16:00:00", "2026-11-27T22:00:00",
                                                               "PT4H", "TK", "1972", 0),
                                                       _segment("IST", "TAS", "2026-11-28T00:30:00", "2026-11-28T07:30:00",
                                                                "PT5H", "TK", "370", 0)]}]},
]}}

LITEAPI = {
    "data": [
        {"hotelId": "lp1", "roomTypes": [
            {"offerId": "o1", "offerRetailRate": {"amount": 840.0, "currency": "GBP"},
             "rates": [{"name": "Double room", "boardType": "BB", "boardName": "Bed and breakfast",
                        "retailRate": {"total": [{"amount": 840.0, "currency": "GBP"}]},
                        "cancellationPolicies": {"refundableTag": "RFN"}}]},
            {"offerId": "o2", "offerRetailRate": {"amount": 700.0, "currency": "GBP"},
             "rates": [{"name": "Double room, no window", "boardType": "RO", "boardName": "Room only",
                        "retailRate": {"total": [{"amount": 700.0, "currency": "GBP"}]},
                        "cancellationPolicies": {"refundableTag": "NRFN"}}]}]},
        {"hotelId": "lp2", "roomTypes": [
            {"offerId": "o3", "offerRetailRate": {"amount": 1400.0, "currency": "GBP"},
             "rates": [{"name": "Suite", "boardType": "RO", "boardName": "Room only",
                        "retailRate": {"total": [{"amount": 1400.0, "currency": "GBP"}]},
                        "cancellationPolicies": {"refundableTag": "RFN"}}]}]},
    ],
    "hotels": [
        {"id": "lp1", "name": "The Strand Hotel", "main_photo": "https://example.org/a.jpg", "address": "1 Strand",
         "latitude": 51.5085, "longitude": -0.1235, "rating": 8.4, "stars": 4, "review_count": 1200},
        {"id": "lp2", "name": "Canary Suites", "address": "E14", "latitude": 51.5050, "longitude": -0.0200,
         "rating": 9.1, "stars": 5, "review_count": 300},
    ]}


def _fq(**kw):
    base = dict(origin="TAS", destination="LON", depart=date(2026, 11, 20), ret=date(2026, 11, 27), adults=2)
    return trips.FlightQuery(**{**base, **kw})


def _sq():
    return trips.StayQuery(city="London", country_code="GB", lat=51.507819, lon=-0.126137,
                           checkin=date(2026, 11, 20), checkout=date(2026, 11, 27), adults=2)


def test_duffel_offers_become_flights():
    fl = trips.parse_duffel(DUFFEL)
    ba, tk = fl
    assert (ba.airline, ba.price, ba.stops, ba.checked_bags, ba.refundable, ba.changeable) == \
        ("British Airways", 512.4, 0, 1, False, True)
    assert ba.outbound.depart_at == "2026-11-20T08:35" and ba.outbound.duration_min == 430
    assert (tk.stops, tk.outbound.via, tk.checked_bags, tk.refundable) == (1, ["IST"], 0, None)
    assert tk.duration_min == 665 + 630 and tk.outbound.flight_numbers == ["TK371", "TK1971"]
    body = trips.duffel_body(_fq(children=(7,)))["data"]
    assert [s["origin"] for s in body["slices"]] == ["TAS", "LON"] and body["passengers"][-1] == {"age": 7}


def test_flight_filters_and_sorts():
    fl = trips.parse_duffel(DUFFEL)
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(sort="cheapest"))] == ["off_2", "off_1"]
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(sort="fastest"))] == ["off_1", "off_2"]
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(max_stops=0))] == ["off_1"]
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(checked_bag=True))] == ["off_1"]
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(out_depart=(7 * 60, 12 * 60)))] == ["off_1"]
    assert [f.id for f in trips.filter_flights(fl, trips.FlightFilters(airlines=["Turkish Airlines"]))] == ["off_2"]
    assert trips.filter_flights(fl, trips.FlightFilters(max_price=300)) == []
    facets = trips.flight_facets(fl)
    assert facets["stops"] == [{"stops": 0, "min_price": 512.4}, {"stops": 1, "min_price": 389.0}]
    assert facets["tabs"]["cheapest"]["price"] == 389.0 and facets["price"] == [389.0, 512.4]


def test_liteapi_rates_become_stays_with_the_cheapest_room():
    st = trips.add_distances(trips.parse_liteapi(LITEAPI, _sq()), 51.507819, -0.126137)
    strand, canary = st
    assert (strand.name, strand.price_total, strand.price_night, strand.breakfast, strand.refundable) == \
        ("The Strand Hotel", 700.0, 100.0, False, False)
    assert strand.distance_km < 0.5 and canary.distance_km > 6
    body = trips.liteapi_body(_sq())
    assert body["guestNationality"] == "GB" and body["cityName"] == "London" and body["occupancies"] == \
        [{"adults": 2, "children": []}]
    assert [s.name for s in trips.filter_stays(st, trips.StayFilters(max_km=2))] == ["The Strand Hotel"]
    assert [s.name for s in trips.filter_stays(st, trips.StayFilters(sort="rating"))][0] == "Canary Suites"
    assert trips.filter_stays(st, trips.StayFilters(refundable=True)) == [canary]
    assert trips.stay_facets(st)["price_night"] == [100.0, 200.0]


def test_links_out_carry_the_same_search():
    sky, google = trips.flight_links(_fq(children=(4, 9)))
    assert "origin=TAS" in sky["url"] and "inboundDate=2026-11-27" in sky["url"] and "childrenv2=4%7C9" in sky["url"]
    assert "mediaPartnerId" not in sky["url"]          # no commission while testing (D120)
    assert google["url"].startswith("https://www.google.com/travel/flights?")
    booking, airbnb = trips.stay_links(_sq(), max_night=150)
    assert "checkin=2026-11-20" in booking["url"] and "group_adults=2" in booking["url"]
    assert airbnb["url"].startswith("https://www.airbnb.co.uk/s/London/homes?") and "price_max=150" in airbnb["url"]
    one = trips.stay_links(_sq(), stay=trips.parse_liteapi(LITEAPI, _sq())[0])
    assert "The+Strand+Hotel" in one[0]["url"] and one[1]["name"] == "The place's own website"


def test_sample_results_are_labelled_and_repeatable():
    a, b = trips.sample_flights(_fq(), AIRPORTS), trips.sample_flights(_fq(), AIRPORTS)
    assert [x.price for x in a] == [x.price for x in b] and all(x.sample for x in a)
    assert all(x.airline in {"Sample Air", "Demo Airways", "Test Wings", "Example Jet"} for x in a)
    stays = trips.sample_stays(_sq())
    assert all(s.sample and s.name.startswith("Sample ") for s in stays)


def test_cache_and_hourly_cap():
    calls = []
    now = [0.0]

    def fetch(url, headers, body):
        calls.append(url)
        return DUFFEL

    ts = trips.TripSearch(AIRPORTS, DESTS, duffel_token="duffel_test_x", fetch=fetch, per_hour=2,
                          clock=lambda: now[0])
    assert ts.flight_source == "duffel_test"
    ts.flights(_fq(), "u1")
    ts.flights(_fq(), "u1")                  # the same search: from the cache
    assert len(calls) == 1
    ts.flights(_fq(adults=1), "u1")
    with pytest.raises(trips.ProviderError, match="too_many"):
        ts.flights(_fq(adults=3), "u1")
    now[0] = 3601.0                          # an hour later
    ts.flights(_fq(adults=3), "u1")
    assert len(calls) == 3

    def broken(url, headers, body):
        raise RuntimeError("down")
    ts2 = trips.TripSearch(AIRPORTS, DESTS, liteapi_key="k", fetch=broken)
    assert ts2.stay_source == "liteapi"
    with pytest.raises(trips.ProviderError, match="unavailable"):   # never falls back to made-up results
        ts2.stays(_sq(), "u1")
    assert trips.TripSearch(AIRPORTS, DESTS, liteapi_key="sand_x").stay_source == "liteapi_sandbox"
    assert trips.TripSearch(AIRPORTS, DESTS).flight_source == "sample"


def test_trip_endpoints_in_sample_mode(client):
    h, uid = install(client)
    assert client.get("/v1/trips/places?q=tash", headers=h).json()[0]["code"] == "TAS"
    assert client.get("/v1/trips/destinations", headers=h).json()[0]["key"] == "london"
    soon = date.today() + timedelta(days=30)
    r = client.post("/v1/trips/flights", headers=h, json={
        "origin": "tas", "depart_date": soon.isoformat(), "return_date": (soon + timedelta(days=7)).isoformat(),
        "adults": 2, "filters": {"max_stops": 1, "sort": "cheapest"}})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["source"] == "sample" and d["note"].startswith("Sample results")
    assert d["shown"] <= d["total"] and all(x["stops"] <= 1 for x in d["results"])
    prices = [x["price"] for x in d["results"]]
    assert prices == sorted(prices) and {l["name"] for l in d["links"]} == {"Skyscanner", "Google Flights"}
    s = client.post("/v1/trips/stays", headers=h, json={
        "checkin": soon.isoformat(), "checkout": (soon + timedelta(days=3)).isoformat(), "adults": 2,
        "filters": {"max_km": 3, "sort": "price"}}).json()
    assert s["source"] == "sample" and all(x["distance_km"] <= 3 for x in s["results"])
    assert all(len(x["links"]) == 2 for x in s["results"]) and s["centre"] == "Charing Cross"
    # the test sees which filters were used, never where or when
    from test_api import ADMIN
    ev = [e for e in client.get("/v1/admin/export", headers=ADMIN).json()["events"]
          if e["user_id"] == uid and e["name"] == "trip_search"]
    assert {e["props"]["kind"] for e in ev} == {"flights", "stays"}
    assert all("TAS" not in str(e["props"]) and soon.isoformat() not in str(e["props"]) for e in ev)


def test_trip_endpoints_check_their_input(client):
    h, _ = install(client)
    soon = date.today() + timedelta(days=10)
    bad = [{"origin": "TAS", "depart_date": (date.today() - timedelta(days=1)).isoformat()},
           {"origin": "TAS", "depart_date": soon.isoformat(), "return_date": (soon - timedelta(days=2)).isoformat()},
           {"origin": "LON", "depart_date": soon.isoformat()},
           {"origin": "TAS", "destination": "paris", "depart_date": soon.isoformat()},
           {"origin": "TASHKENT", "depart_date": soon.isoformat()}]
    for b in bad:
        assert client.post("/v1/trips/flights", headers=h, json=b).status_code == 422, b
    assert client.post("/v1/trips/stays", headers=h, json={
        "checkin": soon.isoformat(), "checkout": soon.isoformat()}).status_code == 422
    assert client.post("/v1/trips/flights", json={"origin": "TAS", "depart_date": soon.isoformat()}).status_code == 401
