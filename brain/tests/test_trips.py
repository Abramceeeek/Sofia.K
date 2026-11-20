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
    assert facets["stops"] == [{"stops": 0, "min_price": 512.4, "currency": "GBP"},   # m218: each says its currency
                               {"stops": 1, "min_price": 389.0, "currency": "GBP"}]
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


def test_sample_flights_keep_each_airports_clock():
    """19 Oct review: Tashkent 20:00 + 6h 50m showed 02:50 in London. Each end is on its own clock now, and the
    duration is real time, across the clock change on Sunday 25 Oct too."""
    from datetime import datetime, timezone
    q = trips.FlightQuery(origin="TAS", destination="LHR", depart=date(2026, 10, 21), ret=date(2026, 10, 27))
    for f in trips.sample_flights(q, AIRPORTS):
        for leg, (src, dst) in ((f.outbound, ("Asia/Tashkent", "Europe/London")),
                                (f.inbound, ("Europe/London", "Asia/Tashkent"))):
            from zoneinfo import ZoneInfo
            dep = datetime.fromisoformat(leg.depart_at).replace(tzinfo=ZoneInfo(src))
            arr = datetime.fromisoformat(leg.arrive_at).replace(tzinfo=ZoneInfo(dst))
            assert (arr.astimezone(timezone.utc) - dep.astimezone(timezone.utc)).total_seconds() == leg.duration_min * 60
    every = {a.code for a in AIRPORTS}
    assert all(a.country in trips._COUNTRY_TZ for a in AIRPORTS), "an airport's country has no time zone"
    assert next(a for a in AIRPORTS if a.code == "OSL").country == "NO"      # not YAML's false
    assert trips.airport_zone("LAX", AIRPORTS).key == "America/Los_Angeles" and "LAX" in every


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
    # 9 Oct: the flight home has its own leaving times
    back = client.post("/v1/trips/flights", headers=h, json={
        "origin": "TAS", "depart_date": soon.isoformat(), "return_date": (soon + timedelta(days=7)).isoformat(),
        "filters": {"in_times": ["evening"]}}).json()["results"]
    assert back and all(x["inbound"]["depart_at"][11:13] >= "18" for x in back)
    assert client.post("/v1/trips/flights", headers=h, json={
        "origin": "TAS", "depart_date": soon.isoformat(), "filters": {"in_times": ["late"]}}).status_code == 422
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


def test_one_day_changed_to_the_hours_the_person_is_free(client):
    """Abram's comment (8 Oct, m177): "I'm meeting someone tomorrow." The app plans just that day again at the hours
    they're free, without the trip's other days' places; the day may keep its own."""
    h, _ = install(client)
    start = date.today() + timedelta(days=4)
    body = {"start_date": start.isoformat(), "nights": 2, "day_start": "10:00", "day_end": "18:00", "stops_per_day": 3}
    d = client.post("/v1/me/trips/days", headers=h, json=body).json()
    middle = d["days"][1]
    own = {st["moment_id"].split("#")[0] for st in middle["plan"]["stops"] if st["rateable"]}
    others = [m for m in d["used"] if m not in own]
    r = client.post("/v1/me/trips/days", headers=h, json={**body, "days": [1], "exclude": others,
                                                          "day_start": "15:00", "day_end": "21:00", "stops_per_day": 2})
    assert r.status_code == 201, r.text
    day = r.json()["days"]
    assert [x["index"] for x in day] == [1] and day[0]["window"]["start"] == "15:00"
    stops = day[0]["plan"]["stops"]
    assert stops[0]["arrive"] >= "15:00" and stops[-1]["depart"] <= "21:00"
    places = [st["moment_id"].split("#")[0] for st in stops if st["rateable"]]
    assert len(places) <= 2 and not set(places) & set(others)
    assert set(others) <= set(r.json()["used"])          # the other days' places stay taken


def test_a_day_trip_starts_at_the_station_with_no_check_in_or_bags(client):
    """Journey round 2: one day by train, no stay. The day starts when the train is in, from the station, and ends on
    the way back to it: no "to your stay", no check-in and no bags (they cost about 65 min of a 6-hour day)."""
    h, _ = install(client)
    start = date.today() + timedelta(days=6)
    body = {"start_date": start.isoformat(), "nights": 0, "day_start": "09:00", "day_end": "20:00", "stops_per_day": 3,
            "arrive": {"mode": "train", "place": "EUS", "time": "10:15"},
            "leave": {"mode": "train", "place": "EUS", "time": "19:30"}}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    day = r.json()["days"][0]
    assert day["kind"] == "one" and [l["slot"] for l in day["legs"]] == ["arrive", "leave"]
    assert day["legs"][0]["title"] == "Arrive at Euston" and day["legs"][1]["origin"] is None
    assert day["window"]["start"] == "10:25"                       # the train's 10:15, plus 10 min to get out
    assert day["plan"]["stops"][-1]["depart"] <= day["legs"][1]["depart"]
    # with a stay, the same arrival goes to the stay first, as before
    stay = {**body, "nights": 1, "stay": {"lat": STAY.lat, "lon": STAY.lon}, "stay_name": "Sample hotel"}
    first = client.post("/v1/me/trips/days", headers=h, json=stay).json()["days"][0]
    assert first["legs"][0]["title"].endswith("→ your stay")


def test_a_day_with_only_lunch_left_is_a_free_day(client):
    """Journey round 2: a long trip runs out of places that suit the person; a day with lunch alone was shown as
    planned ("Ready"). It's a free day now, and says so."""
    h, _ = install(client)
    ids = [m["id"] for m in client.get("/v1/moments?plannable_only=true", headers=h).json()]
    start = date.today() + timedelta(days=8)
    r = client.post("/v1/me/trips/days", headers=h, json={"start_date": start.isoformat(), "nights": 3, "days": [2],
                                                          "exclude": ids, "day_start": "10:00", "day_end": "18:00"})
    assert r.status_code == 201, r.text
    day = r.json()["days"][0]
    assert day["plan"] is None and day["title"].startswith("A free day")


def test_journeys_past_midnight_say_so():
    """Journey round 2: a 22:45 landing reached London after midnight but showed "23:59"; a 01:30 flight home said
    "leave by 00:00". Times now say "next day" or "the night before", with a note when trains may not run."""
    late = _frame(0, 3, arrive=tripdays.End("flight", "LHR", "22:45"))
    leg = late.legs[0]
    assert "(next day)" in (leg.arrive or "") and tripdays.NIGHT_NOTE in (leg.note or "")
    assert late.main is None and late.title == "Arrive and settle in"
    early = _frame(2, 3, leave=tripdays.End("flight", "LHR", "01:30"))
    assert "(the night before)" in early.leave_leg.title and early.main is None
    dawn = _frame(2, 3, leave=tripdays.End("flight", "LHR", "06:00"))   # at the airport by 04:00: no trains yet
    assert tripdays.NIGHT_NOTE in dawn.leave_leg.note
    day = _frame(2, 3, leave=tripdays.End("flight", "LHR", "18:00"))
    assert "next day" not in day.leave_leg.title and tripdays.NIGHT_NOTE not in (day.leave_leg.note or "")


def test_trip_length_comes_from_the_persons_matches_and_names_what_each_length_leaves_out(client):
    """m196: "How long should I stay?" from the person's own good matches, at their places a day."""
    h, _ = install(client)
    r = client.post("/v1/me/trips/length", headers=h, json={"nights": 9, "stops_per_day": 3})
    assert r.status_code == 200, r.text
    d = r.json()
    need, yours = d["suggested_days"], d["your_days"]
    assert 1 <= need <= 14 and yours == 9 and d["places_per_day"] == 3
    assert d["checked"] > 0 and "London" in d["why"] and d["headline"] == f"Around {need} day{'s' if need != 1 else ''}"
    assert "not a limit" in d["note"] and "3 places a day" in d["note"]
    lengths = [o["days"] for o in d["options"]]
    assert lengths == sorted(lengths) and need in lengths and yours in lengths
    by_days = {o["days"]: o for o in d["options"]}
    assert by_days[need]["suggested"] and by_days[need]["covers"] == by_days[need]["of"]
    assert by_days[yours]["yours"]
    for o in d["options"]:
        assert o["line"] and o["covers"] + len(o["leaves_out"]) == o["of"]
        assert not o["adds"] or o["days"] > need                 # extra good matches only come with more days
        if o["days"] < need:   # a shorter trip says what it leaves out, by name
            assert o["label"] == "Highlights" and "leave out" in o["line"] and o["leaves_out"]
    if yours > need:
        assert d["spare_days"] == yours - need and {"slower", "free"} <= {e["kind"] for e in d["extra"]}
    else:
        assert d["short"]
    # a short day holds fewer places: the person's hours cap their places a day
    short_day = client.post("/v1/me/trips/length", headers=h,
                            json={"nights": 2, "stops_per_day": 6, "day_start": "10:00", "day_end": "12:30"}).json()
    assert short_day["places_per_day"] == 2
    assert client.post("/v1/me/trips/length", headers=h,
                       json={"day_start": "10:00", "day_end": "10:30"}).status_code == 422


def test_days_for_keeps_the_days_shape():
    from types import SimpleNamespace

    from brain import triplength
    card = lambda hist=0, kind="moment": SimpleNamespace(tag=lambda n: hist if n == "history_culture" else 0, kind=kind)
    assert triplength.days_for([], 3) == 0
    assert triplength.days_for([card() for _ in range(7)], 3) == 3                 # 7 places at 3 a day
    assert triplength.days_for([card(2) for _ in range(6)], 4) == 3                # at most 2 history a day
    assert triplength.days_for([card(kind="area") for _ in range(3)], 4) == 3      # at most 1 wander a day
    six = [card() for _ in range(6)]
    assert triplength._covered(six, 1, 4) == 4 and triplength._covered(six, 2, 4) == 6


def test_trip_length_names_each_place_once_on_the_page():
    from types import SimpleNamespace

    from brain import triplength
    cards = [SimpleNamespace(id=f"m{i}", title=f"Place {i}: a line") for i in range(8)]
    seen: set[str] = set()
    first = triplength._names(cards, 2, seen)
    second = triplength._names(cards, 2, seen)
    assert first == "Place 0, Place 1 and 6 more"
    assert second == "Place 2, Place 3 and 6 more"     # the next ones, and the count still covers all eight
    assert triplength._names(cards[:2], 2, seen) == "Place 0, Place 1"   # nothing new left: the named ones again


def test_the_persons_own_time_is_planned_around(client):
    """m200 (product direction, step 2): "I have plans 13:00-14:00" and free time are stops of their own, at their
    times, never rated and never one of the day's places; a relaxed day has one place fewer; a free day has no plan."""
    h, _ = install(client)
    start = date.today() + timedelta(days=4)
    body = {"start_date": start.isoformat(), "nights": 3, "day_start": "10:00", "day_end": "18:00", "stops_per_day": 3,
            "personal": [{"day": 1, "mine": [{"kind": "plans", "start": "13:00", "end": "14:00"},
                                             {"kind": "free", "start": "07:00", "end": "08:00"}]},   # before the day
                         {"day": 2, "relaxed": True}, {"day": 3, "free_day": True}]}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    days = {d["index"]: d for d in r.json()["days"]}
    one = days[1]
    assert [(b["kind"], b["planned"]) for b in one["mine"]] == [("plans", True), ("free", False)]
    mine = [st for st in one["plan"]["stops"] if st["mine"]]
    assert len(mine) == 1 and (mine[0]["arrive"], mine[0]["depart"]) == ("13:00", "14:00")
    assert mine[0]["title"] == "Your plans" and not mine[0]["rateable"] and mine[0]["feel_word"] == "Your time"
    assert mine[0]["cost_text"] == "" and mine[0]["what"].startswith("Where isn't decided yet")   # m201: the default
    assert mine[0]["pin"] is None
    places = [st for st in one["plan"]["stops"] if st["rateable"] and not st["lunch"]]   # a food card can be lunch
    # m201, m202: plans not decided yet keep the cautious allowance either side: 45 min (GUESS)
    assert "45 min before and 45 min after" in mine[0]["what"]
    assert 1 <= len(places) <= 3 and all(st["depart"] <= "12:15" or st["arrive"] >= "14:45" for st in places)
    assert "your own plans" in one["title"].lower()
    assert not any(m.startswith("mine") for m in r.json()["used"])         # never kept as a place of the trip
    assert days[2]["relaxed"] and sum(st["rateable"] for st in days[2]["plan"]["stops"]) <= 2
    assert days[3]["free_day"] and days[3]["plan"] is None and days[3]["title"] == "A day that's yours"
    home = client.post("/v1/me/trips/days", headers=h, json={**body, "days": [3], "leave": {
        "mode": "train", "place": "KGX", "time": "17:00"}}).json()["days"][0]
    assert home["free_day"] and home["plan"] is None and [x["slot"] for x in home["legs"]] == ["leave"]   # still home
    bad = {**body, "personal": [{"day": 1, "mine": [{"kind": "plans", "start": "1pm", "end": "14:00"}]}]}
    assert client.post("/v1/me/trips/days", headers=h, json=bad).status_code == 422
    three = [{"kind": "free", "start": f"1{k}:00", "end": f"1{k}:30"} for k in range(3)]
    assert client.post("/v1/me/trips/days", headers=h,
                       json={**body, "personal": [{"day": 1, "mine": three}]}).status_code == 422


def test_a_block_is_pinned_to_its_time_and_isnt_a_place():
    """m200: the planner keeps the person's own time at its times, near a place, without counting it as a stop."""
    from brain.moments import Point
    from brain.planner import Candidate, LegWeights, plan_day
    from brain.travel import LondonEstimate
    p = lambda lat, lon: Point(lat=lat, lon=lon)
    places = [Candidate(f"m{k}", p(51.50 + k / 200, -0.12), p(51.50 + k / 200, -0.12), 45, ((600, 1080),), 1.0)
              for k in range(4)]
    slot = lambda mid, at: Candidate(mid, at, at, 60, ((780, 840),), 0.0, mine="mine0")
    cands = places + [slot(f"mine0@{c.moment_id}", c.end) for c in places] + [slot("mine0@start", p(51.5, -0.12))]
    plan = plan_day(cands, p(51.5, -0.12), 600, 1080, LondonEstimate(), LegWeights(0.0, 0.0), max_stops=2)
    ids = [s.moment_id for s in plan.stops]
    mine = [s for s in plan.stops if s.moment_id.startswith("mine0@")]
    assert len(mine) == 1 and (mine[0].arrive_min, mine[0].depart_min) == (780, 840)
    assert len([i for i in ids if not i.startswith("mine")]) == 2          # still two places
    assert plan.peak_moment_id and not plan.peak_moment_id.startswith("mine")


def test_swap_and_regenerate_keep_the_persons_own_time(client):
    """m200: once a trip day is "my day", swapping a stop or planning again goes through /v1/me/plans; the person's
    own time comes too, so it's never lost."""
    h, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "your stay", "start_time": "10:00",
            "end_time": "18:00", "stops": 4, "familiar": False,
            "mine": [{"kind": "plans", "start": "15:00", "end": "16:00"}]}
    first = client.post("/v1/me/plans", headers=h, json=body)
    assert first.status_code == 201, first.text
    stops = first.json()["stops"]
    own = [st for st in stops if st["mine"]]
    assert [(st["arrive"], st["depart"], st["mine"]) for st in own] == [("15:00", "16:00", "plans")]
    out = next(st for st in stops if st["rateable"])
    keep = [st["key"] for st in stops if st is not out]
    again = client.post("/v1/me/plans", headers=h, json={**body, "keep": keep, "exclude": [out["moment_id"]]})
    assert again.status_code == 201, again.text
    new = again.json()["stops"]
    assert [(st["arrive"], st["depart"]) for st in new if st["mine"]] == [("15:00", "16:00")]
    assert out["moment_id"] not in {st["moment_id"] for st in new}


def test_where_the_plans_are_and_whether_they_include_a_meal(client):
    """m201 (Abram, 7 Nov): plans near the day's places sit beside one, with no time added; plans somewhere else get
    time to get there and back and no pin; plans the person eats during take the place of the lunch stop."""
    h, _ = install(client)
    base = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "your stay", "start_time": "10:00",
            "end_time": "18:00", "stops": 4, "familiar": False}
    plan = lambda **b: client.post("/v1/me/plans", headers=h, json={**base, "mine": [
        {"kind": "plans", "start": "12:30", "end": "14:00", **b}]}).json()["stops"]
    near = plan(location="near")
    block = next(st for st in near if st["mine"])
    assert block["what"].startswith("Your own time, ") and block["pin"] is not None
    away = plan(location="elsewhere")
    i = next(k for k, st in enumerate(away) if st["mine"])
    assert (away[i]["arrive"], away[i]["depart"]) == ("12:30", "14:00") and away[i]["pin"] is None
    assert away[i]["what"].startswith("Somewhere else: we've left 30 min before and 30 min after")
    if i + 1 < len(away):
        assert away[i + 1]["travel_text"].startswith("Getting there: from your plans") and away[i + 1]["arrive"] >= "14:30"
    assert any(st["lunch"] for st in near)                                   # no meal said: lunch stays
    eaten = plan(location="near", meal=True)
    assert not any(st["lunch"] for st in eaten) and "no lunch stop" in next(st for st in eaten if st["mine"])["what"]


def test_plans_that_leave_no_room_for_lunch_say_so(client):
    """m202: midday plans not decided yet keep 45 min either side; when that leaves no room for lunch, the plans say so
    rather than lunch disappearing silently, and no extra place takes lunch's slot."""
    h, _ = install(client)
    body = {"start": {"lat": 51.5081, "lon": -0.1281}, "start_name": "your stay", "start_time": "10:00",
            "end_time": "18:00", "stops": 4, "familiar": False,
            "mine": [{"kind": "plans", "start": "12:00", "end": "14:00"}]}
    stops = client.post("/v1/me/plans", headers=h, json=body).json()["stops"]
    assert not any(st["lunch"] for st in stops)
    assert "no room for a lunch stop" in next(st for st in stops if st["mine"])["what"]
    assert len([st for st in stops if st["rateable"]]) <= 3                  # never a 4th place instead of lunch
