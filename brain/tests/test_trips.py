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
    assert trips.duffel_body(_fq())["data"]["max_connections"] == 2   # 1-stop and 2-stop flights too
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
    booking, airbnb, premier, travelodge = trips.stay_links(_sq(), max_night=150)
    assert premier["name"] == "Premier Inn" and travelodge["note"].startswith("Sells mostly on its own site")
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
    assert client.get("/v1/health").json() | {"flights": "sample", "stays": "sample"} == client.get("/v1/health").json()
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


def test_design_filters_tabs_and_tags():
    """ODYS Trips design: stops as a multi-choice (2 = 2 or more), leaving-time buckets, and each sort's top."""
    fl = trips.parse_duffel(DUFFEL)
    ids = lambda f: [x.id for x in trips.filter_flights(fl, f)]
    assert ids(trips.FlightFilters(stops=[1])) == ["off_2"] and ids(trips.FlightFilters(stops=[0, 2])) == ["off_1"]
    assert ids(trips.FlightFilters(out_times=["night"])) == [] and ids(trips.FlightFilters(out_times=["morning"])) \
        == ids(trips.FlightFilters())
    assert trips.time_bucket(359) == "night" and trips.time_bucket(1080) == "evening"
    tabs, tags = trips.flight_tops(fl, trips.FlightFilters())
    assert tabs["cheapest"]["price"] == 389.0 and tabs["fastest"]["duration_min"] == 14 * 60
    assert "Cheapest" in tags["off_2"] and "Fastest" in tags["off_1"]
    tabs, tags = trips.flight_tops(fl, trips.FlightFilters(max_price=100))
    assert tabs == {"best": None, "cheapest": None, "fastest": None} and tags == {}
    st = trips.add_distances(trips.parse_liteapi(LITEAPI, _sq()), 51.507819, -0.126137)
    tabs, tags = trips.stay_tops(st, trips.StayFilters())
    assert tabs["price"]["price_night"] == 100.0 and tabs["rating"]["rating"] == 9.1
    assert tags["lp1"] == ["Best for your days", "Cheapest"] and "lp2" not in tags   # "Top rated" isn't a tag


def test_flight_and_stay_responses_carry_tabs_and_tags(client):
    h, _ = install(client)
    soon = date.today() + timedelta(days=30)
    d = client.post("/v1/trips/flights", headers=h, json={
        "origin": "TAS", "depart_date": soon.isoformat(), "return_date": (soon + timedelta(days=7)).isoformat(),
        "filters": {"stops": [0, 1], "out_times": ["morning", "afternoon"]}}).json()
    assert set(d["tabs"]) == {"best", "cheapest", "fastest"} and d["searched_at"]
    assert all(min(x["stops"], 2) in (0, 1) for x in d["results"])
    assert all(360 <= int(x["outbound"]["depart_at"][11:13]) * 60 + int(x["outbound"]["depart_at"][14:16]) < 1080
               for x in d["results"])
    assert sum("Cheapest" in x["tags"] for x in d["results"]) == (1 if d["results"] else 0)
    s = client.post("/v1/trips/stays", headers=h, json={
        "checkin": soon.isoformat(), "checkout": (soon + timedelta(days=3)).isoformat()}).json()
    assert set(s["tabs"]) == {"recommended", "price", "rating"} and s["results"][0]["tags"]


def test_trip_days_never_repeat_a_moment_and_shape_the_ends(client):
    h, uid = install(client)
    start = date.today() + timedelta(days=3)
    r = client.post("/v1/me/trips/days", headers=h, json={"start_date": start.isoformat(), "nights": 3,
                                                          "feelings": ["curious", "nonsense"]})
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["total_days"] == 4 and [x["index"] for x in d["days"]] == [0, 1, 2, 3]
    assert [x["date"] for x in d["days"]] == [(start + timedelta(days=i)).isoformat() for i in range(4)]
    seen = [st["moment_id"].split("#")[0] for x in d["days"] if x["plan"] for st in x["plan"]["stops"] if st["rateable"]]
    assert len(seen) == len(set(seen)) and set(seen) <= set(d["used"])
    assert all(x["title"] for x in d["days"])
    planned = [x for x in d["days"] if x["plan"]]
    assert planned and all(x["plan"]["date"] == x["date"] for x in planned)
    assert client.get("/v1/me/weights", headers=h).json()["n_observations"] == 0   # the trip's feelings: this trip only
    later = client.post("/v1/me/trips/days", headers=h, json={"start_date": start.isoformat(), "nights": 3,
                                                              "days": [2], "exclude": d["used"]}).json()
    again = [st["moment_id"] for x in later["days"] if x["plan"] for st in x["plan"]["stops"] if st["rateable"]]
    assert not set(again) & set(d["used"])
    assert client.post("/v1/me/trips/days", headers=h, json={"start_date": start.isoformat(), "nights": 3,
                                                             "days": [4]}).status_code == 422
    ended = client.post("/v1/me/trips/days", headers=h, json={
        "start_date": (date.today() - timedelta(days=3)).isoformat(), "nights": 2})
    assert ended.status_code == 422 and "ended" in ended.text
    # a long trip under way still plans its later days ("planned as you go"), and today's
    under_way = client.post("/v1/me/trips/days", headers=h, json={
        "start_date": (date.today() - timedelta(days=8)).isoformat(), "nights": 9, "days": [8, 9]})
    assert under_way.status_code == 201, under_way.text
    assert [x["date"] for x in under_way.json()["days"]] == [date.today().isoformat(),
                                                             (date.today() + timedelta(days=1)).isoformat()]


# ---- D122: the person's own day, and the journeys at each end of the trip ----------------------------------------

from brain import tripdays                       # noqa: E402
from brain.moments import Point                  # noqa: E402
from brain.travel import LondonEstimate          # noqa: E402

CFG = tripdays.load_arrivals(DATA_DIR / "arrivals.yaml")["london"]
STAY = Point(lat=51.5117, lon=-0.1240)           # Covent Garden


def _frame(i, total, **kw):
    args = dict(stay=STAY, stay_name="Sample hotel", stay_chosen=True, day_start="10:00", day_end="18:00", stops=4,
                arrive=None, leave=None, travel_light=False)
    args.update(kw)
    return tripdays.frame_day(i, total, CFG, LondonEstimate(), **args)


def test_on_the_way_is_an_ellipse_between_the_station_and_the_stay():
    paddington = CFG.airports["LHR"].hub.point
    assert tripdays.on_the_way(Point(lat=51.5154, lon=-0.1410), paddington, STAY)     # Oxford Circus: on the way
    assert not tripdays.on_the_way(Point(lat=51.5131, lon=-0.0820), paddington, STAY)  # the City: not on the way


def test_frames_follow_the_persons_hours_and_places_a_day():
    f = _frame(2, 5, day_start="09:00", day_end="20:00", stops=5)
    assert (f.kind, f.main.start_time, f.main.end_time, f.main.stops, f.legs) == ("full", "09:00", "20:00", 6, [])  # 5 + lunch
    assert _frame(2, 5, day_start="10:00", day_end="12:00", stops=5).main.stops == 1   # a short day holds fewer
    assert set(CFG.airports) == {"LHR", "LGW", "STN", "LTN", "LCY"} and "KGX" in CFG.stations


def test_arrival_day_starts_where_they_land():
    f = _frame(0, 4, arrive=tripdays.End("flight", "LHR", "09:40"))
    leg = f.legs[0]
    assert (leg.slot, leg.title, leg.depart) == ("arrive", "Heathrow → your stay", "10:40")   # an hour to get out
    assert leg.origin.maps == "Heathrow Airport" and leg.destination.lat == STAY.lat
    assert leg.how.startswith("Elizabeth line or Heathrow Express to Paddington (28 min)")
    assert f.before is None and f.main.start_time >= leg.arrive                # the plan starts at the stay
    # travelling light and early: Paddington, one place, then the stay
    f = _frame(0, 4, arrive=tripdays.End("flight", "LHR", "09:40"), travel_light=True)
    assert f.legs[0].title == "Heathrow → Paddington" and f.legs[0].arrive == "11:08"
    assert (f.before.start_name, f.before.start_time, f.before.stops) == ("Paddington", "11:10", 1)
    # light but landing after check-in time: the stay first
    assert _frame(0, 4, arrive=tripdays.End("flight", "LHR", "15:30"), travel_light=True).before is None
    late = _frame(0, 4, arrive=tripdays.End("flight", "LGW", "17:30"))
    assert late.main is None and late.title == "Arrive and settle in"
    car = _frame(0, 4, arrive=tripdays.End("car", None, "12:00"))
    assert car.legs[0].title == "Drive to your stay" and car.main.start_time == "12:20"
    train = _frame(0, 4, arrive=tripdays.End("train", "KGX", "10:00"))
    assert train.legs[0].origin.name == "King's Cross St Pancras" and train.legs[0].depart == "10:10"
    unknown = _frame(0, 4, arrive=tripdays.End("flight", None, "09:00"))          # the older app: no airport
    assert unknown.legs[0].title == "the airport → your stay" and unknown.legs[0].origin.maps is None


def test_last_day_ends_with_the_way_to_the_airport_or_station():
    f = _frame(3, 4, leave=tripdays.End("flight", "LGW", "18:00"))
    leg = f.leave_leg
    assert leg.title.startswith("Leave for Gatwick by") and leg.destination.maps == "Gatwick Airport"
    assert 16 * 60 - 5 < tripdays.mins(leg.arrive) <= 16 * 60                   # 2 hours before the flight
    assert tripdays.mins(f.main.end_time) == f.leave_at - CFG.back_for_bags_min
    early = _frame(3, 4, leave=tripdays.End("flight", "STN", "11:00"))
    assert early.main is None and early.title.startswith("Travel day")
    train = _frame(3, 4, leave=tripdays.End("train", "PAD", "17:00"))
    assert train.leave_leg.destination.name == "Paddington" and train.leave_leg.note.startswith("At the station 20 min")
    car = _frame(3, 4, leave=tripdays.End("car", None, "16:00"))
    assert car.leave_at == 16 * 60 and car.main.end_time == "15:15"          # 45 min to get back and pack the car
    one = _frame(0, 1, arrive=tripdays.End("train", "VIC", "09:00"), leave=tripdays.End("train", "VIC", "19:00"))
    assert one.kind == "one" and one.legs and one.leave_leg and one.main.stops >= 1


def test_trip_days_carry_legs_and_the_place_on_the_way(client):
    h, _ = install(client)
    start = date.today() + timedelta(days=5)
    body = {"start_date": start.isoformat(), "nights": 2, "stay": {"lat": STAY.lat, "lon": STAY.lon},
            "stay_name": "Sample hotel", "day_start": "09:30", "day_end": "19:30", "stops_per_day": 3,
            "travel_light": True, "arrive": {"mode": "flight", "place": "lhr", "time": "08:30"},
            "leave": {"mode": "train", "place": "KGX", "time": "19:00"}}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    days = r.json()["days"]
    first, middle, last = days
    assert first["legs"][0]["slot"] == "arrive" and first["legs"][0]["origin"]["maps"] == "Heathrow Airport"
    if first["before"]:                                    # one place on the way, then the stay to check in
        assert len(first["before"]["stops"]) == 1 and first["legs"][1]["slot"] == "to_stay"
        pin = first["before"]["stops"][0]["pin"]
        hub = CFG.airports["LHR"].hub.point
        assert tripdays.on_the_way(Point(**pin), hub, STAY)
    assert middle["legs"] == [] and middle["window"]["start"] == "09:30"
    assert middle["plan"] and len(middle["plan"]["stops"]) <= 3 + 1          # 3 places, plus lunch if it's one
    assert last["legs"][-1]["slot"] == "leave" and last["legs"][-1]["destination"]["name"] == "King's Cross St Pancras"
    plans = [d[k] for d in days for k in ("before", "plan") if d[k]]
    seen = [st["moment_id"].split("#")[0] for pl in plans for st in pl["stops"] if st["rateable"]]
    assert len(seen) == len(set(seen))                     # nothing twice, the place on the way included
    bad = {**body, "day_start": "12:00", "day_end": "12:30"}
    assert client.post("/v1/me/trips/days", headers=h, json=bad).status_code == 422
    old = client.post("/v1/me/trips/days", headers=h, json={"start_date": start.isoformat(), "nights": 1,
                                                            "arrive_time": "10:00", "leave_time": "20:00"}).json()
    assert old["days"][0]["legs"][0]["origin"]["name"] == "the airport"   # build 41 still works
