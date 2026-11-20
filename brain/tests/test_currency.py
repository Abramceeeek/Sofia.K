"""m218: flights and stays in different currencies are never ranked against each other as raw numbers. With a current
ECB rate they're converted (the original fare kept, the estimate shown beside it, with its source and date); without
one they're grouped by currency and nothing is the cheapest overall."""
from datetime import date, datetime, timedelta, timezone

from brain import fx, trips

from test_api import client, install  # noqa: F401  (the client fixture)

# The ECB daily file's structure (eurofxref-daily.xml, read 7 Nov 2026), with its USD and GBP rates for 6 Nov 2026.
ECB_XML = """<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
  <gesmes:subject>Reference rates</gesmes:subject>
  <gesmes:Sender><gesmes:name>European Central Bank</gesmes:name></gesmes:Sender>
  <Cube>
    <Cube time='2026-11-06'>
      <Cube currency='USD' rate='1.1165'/>
      <Cube currency='GBP' rate='0.83415'/>
    </Cube>
  </Cube>
</gesmes:Envelope>"""
FETCHED = datetime(2026, 11, 7, 9, 0, tzinfo=timezone.utc)
TODAY = date(2026, 11, 7)


def _rates(as_of=date(2026, 11, 6)):
    r = fx.parse_ecb(ECB_XML, FETCHED)
    return fx.Rates(r.per_eur, as_of, FETCHED)


def _leg(dep="2026-11-20T08:35", minutes=420, stops=0):
    return trips.Leg("TAS", "LHR", dep, "2026-11-20T15:35", minutes, stops, [], ["XX"], ["XX1"])


def _flight(fid, price, currency, minutes=420, airline="Sample Air", bags=1):
    return trips.Flight(fid, airline, "SA", price, currency, _leg(minutes=minutes), None, bags, None, None)


def _stay(sid, total, currency, nights=7, pay_there=0.0, rating=8.0):
    return trips.Stay(sid, f"Stay {sid}", "hotel", 4, rating, 100, "London", 51.51, -0.12, None, total, currency, nights,
                      "Double room", "Room only", False, None, distance_km=1.0, pay_there=pay_there)


def test_the_ecb_file_is_read_and_crossed_through_the_euro():
    r = fx.parse_ecb(ECB_XML, FETCHED)
    assert r.as_of == date(2026, 11, 6) and r.per_eur == {"EUR": 1.0, "USD": 1.1165, "GBP": 0.83415}
    assert r.convert(100, "EUR") == 83.42                         # 100 × 0.83415
    assert r.convert(100, "USD") == round(100 * 0.83415 / 1.1165, 2) == 74.71
    assert r.convert(100, "GBP") == 100.0 and r.convert(100, "UZS") is None   # the som isn't an ECB currency
    assert r.line() == "ECB rate of 6 Nov 2026"
    assert r.fresh(TODAY) and r.fresh(date(2026, 11, 11)) and not r.fresh(date(2026, 11, 12))
    for bad in ("<a/>", "<Cube><Cube time='2026-11-06'/></Cube>"):
        try:
            fx.parse_ecb(bad, FETCHED)
            raise AssertionError("parsed a file with no rates")
        except ValueError:
            pass


def test_the_rate_source_keeps_the_last_good_rates_and_never_makes_them_up():
    now, calls, answer = [FETCHED], [], [RuntimeError("down")]

    def fetch(url):
        calls.append(url)
        if isinstance(answer[0], Exception):
            raise answer[0]
        return answer[0]

    src = fx.EcbRates(fetch_text=fetch, clock=lambda: now[0], refresh_s=3600)
    assert src.get() is None and calls == [fx.ECB_DAILY]           # nothing yet: nothing converted
    answer[0] = ECB_XML
    assert src.get() is None and len(calls) == 1                   # asked again only after refresh_s
    now[0] += timedelta(hours=1)
    assert src.get().as_of == date(2026, 11, 6) and len(calls) == 2
    answer[0] = RuntimeError("down again")
    now[0] += timedelta(hours=2)
    assert src.get().as_of == date(2026, 11, 6)                    # a failed fetch keeps the last good rates
    now[0] = FETCHED + timedelta(days=6)
    assert src.get() is None                                       # too old to use: never converted on stale rates


def test_one_currency_compares_as_before():
    fl = [_flight("a", 389.0, "GBP", 665), _flight("b", 512.4, "GBP", 430)]
    px = trips.flight_pricing(fl, _rates(), today=TODAY)
    assert px.mode == "one" and px.note("flights") is None and px.estimate(389.0, "GBP") is None
    assert [x.id for x in trips.filter_flights(fl, trips.FlightFilters(sort="cheapest"), px)] == ["a", "b"]
    tabs, tags = trips.flight_tops(fl, trips.FlightFilters(), px)
    assert "Cheapest" in tags["a"] and tabs["cheapest"] == {"price": 389.0, "currency": "GBP", "duration_min": 665}
    # all in euros: ranked as they are, every figure says EUR, never a pound sign it doesn't have
    eur = [_flight("e1", 300.0, "EUR"), _flight("e2", 250.0, "EUR")]
    px = trips.flight_pricing(eur, None)
    assert [x.id for x in trips.filter_flights(eur, trips.FlightFilters(sort="cheapest"), px)] == ["e2", "e1"]
    facets = trips.flight_facets(eur, px)
    assert facets["currency"] == "EUR" and facets["price"] == [250.0, 300.0] and not facets["estimated"]
    assert facets["airlines"][0]["currency"] == "EUR" and px.note("flights") is None   # no rate: nothing to estimate
    # with a current rate, the pounds are shown beside the euros, never instead of them
    px = trips.flight_pricing(eur, _rates(), today=TODAY)
    est = px.estimate(250.0, "EUR")
    assert est == {"amount": 208.54, "currency": "GBP", "rate": 0.83415, "source": fx.ECB_SOURCE, "as_of": "2026-11-06",
                   "line": "ECB rate of 6 Nov 2026"}
    assert px.note("flights") == ("These flights are priced in EUR. The pounds beside each are converted at the ECB "
                                  "rate of 6 Nov 2026: an estimate. You pay the price in EUR.")


def test_several_currencies_without_a_rate_are_grouped_and_nothing_is_cheapest_overall():
    """300 EUR isn't cheaper than £389 because 300 < 389: without a rate, they're not ranked against each other."""
    fl = [_flight("g1", 389.0, "GBP"), _flight("g2", 420.0, "GBP"), _flight("e1", 300.0, "EUR", airline="Euro Air"),
          _flight("u1", 450.0, "USD", airline="Dollar Air")]
    px = trips.flight_pricing(fl, None)
    assert px.mode == "grouped" and px.currencies == ("GBP", "EUR", "USD")   # pounds first, then by count, then code
    cheapest = [x.id for x in trips.filter_flights(fl, trips.FlightFilters(sort="cheapest"), px)]
    assert cheapest == ["g1", "g2", "e1", "u1"]                              # within each currency, never across
    best = [x.id for x in trips.filter_flights(fl, trips.FlightFilters(), px)]
    assert best[:2] == ["g1", "g2"] and set(best[2:]) == {"e1", "u1"}
    tabs, tags = trips.flight_tops(fl, trips.FlightFilters(), px)
    labels = [t for ts in tags.values() for t in ts]
    assert "Cheapest" not in labels
    assert {"Cheapest in GBP", "Cheapest in EUR", "Cheapest in USD"} <= set(labels) and "Cheapest in GBP" in tags["g1"]
    # a price limit in pounds can't be checked against a fare in euros: like any unknown, it doesn't pass
    assert [x.id for x in trips.filter_flights(fl, trips.FlightFilters(max_price=400), px)] == ["g1"]
    facets = trips.flight_facets(fl, px)
    assert facets["currency"] == "GBP" and facets["price"] == [389.0, 420.0]   # the slider is in pounds only
    rows = {a["name"]: (a["min_price"], a["currency"]) for a in facets["airlines"]}
    assert rows == {"Sample Air": (389.0, "GBP"), "Euro Air": (300.0, "EUR"), "Dollar Air": (450.0, "USD")}
    assert facets["stops"] == [{"stops": 0, "min_price": 389.0, "currency": "GBP"}]   # never a minimum across currencies
    assert px.note("flights") == ("These flights are priced in GBP, EUR and USD, and there's no current exchange rate "
                                  "here, so they're grouped by currency and not ranked against each other.")
    assert all(px.estimate(x.price, x.currency) is None for x in fl)


def test_several_currencies_with_a_current_rate_are_converted_and_the_fare_is_kept():
    fl = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR", airline="Euro Air"),
          _flight("u1", 450.0, "USD", airline="Dollar Air")]
    px = trips.flight_pricing(fl, _rates(), today=TODAY)
    assert px.mode == "converted"
    # 400 EUR ≈ £333.66 and 450 USD ≈ £336.20: both cheaper than £389
    assert [x.id for x in trips.filter_flights(fl, trips.FlightFilters(sort="cheapest"), px)] == ["e1", "u1", "g1"]
    tabs, tags = trips.flight_tops(fl, trips.FlightFilters(), px)
    assert "Cheapest" in tags["e1"] and tabs["cheapest"] == {"price": 400.0, "currency": "EUR", "duration_min": 420}
    assert [x.id for x in trips.filter_flights(fl, trips.FlightFilters(max_price=335), px)] == ["e1"]
    facets = trips.flight_facets(fl, px)
    assert facets["currency"] == "GBP" and facets["estimated"] and facets["price"] == [333.66, 389.0]
    assert px.estimate(400.0, "EUR")["amount"] == 333.66 and px.estimate(389.0, "GBP") is None
    out = trips.flight_out(fl[1])
    assert (out["price"], out["currency"]) == (400.0, "EUR")       # the fare itself is never rewritten
    assert px.note("flights").startswith("These flights are priced in GBP, EUR and USD. To compare them, other "
                                         "currencies are converted to pounds at the ECB rate of 6 Nov 2026")


def test_a_currency_the_ecb_doesnt_publish_or_a_stale_rate_means_grouped():
    fl = [_flight("g1", 389.0, "GBP"), _flight("z1", 4_500_000.0, "UZS", airline="Som Air")]
    px = trips.flight_pricing(fl, _rates(), today=TODAY)
    assert px.mode == "grouped" and "no current exchange rate for UZS here" in px.note("flights")
    fl = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR")]
    assert trips.flight_pricing(fl, _rates(as_of=date(2026, 10, 20)), today=TODAY).mode == "grouped"   # too old: not used


def test_stays_sort_by_what_a_night_really_costs():
    """£100 a night plus £20 a night paid at the property is dearer than £110 with nothing to pay there."""
    st = [_stay("a", 700.0, "GBP", pay_there=140.0), _stay("b", 770.0, "GBP")]
    assert [s.id for s in trips.filter_stays(st, trips.StayFilters(sort="price"))] == ["b", "a"]
    tabs, tags = trips.stay_tops(st, trips.StayFilters())
    assert tags["b"][-1] == "Cheapest" and tabs["price"] == {"price_night": 110.0, "currency": "GBP", "rating": 8.0,
                                                              "distance_km": 1.0}
    mixed = [_stay("g", 770.0, "GBP"), _stay("e", 700.0, "EUR")]
    px = trips.stay_pricing(mixed, None)
    assert px.mode == "grouped" and [s.id for s in trips.filter_stays(mixed, trips.StayFilters(sort="price"), px)] \
        == ["g", "e"]
    _, tags = trips.stay_tops(mixed, trips.StayFilters(), px)
    assert "Cheapest" not in [t for ts in tags.values() for t in ts] and "Cheapest in EUR" in tags["e"]
    assert trips.stay_facets(mixed, px)["price_night"] == [110.0, 110.0]   # the slider in pounds only
    px = trips.stay_pricing(mixed, _rates(), today=TODAY)                              # 700 EUR ≈ £583.91, a night £83.42 (100 × 0.83415)
    assert [s.id for s in trips.filter_stays(mixed, trips.StayFilters(sort="price"), px)] == ["e", "g"]
    est = trips.stay_estimate(px, mixed[1])
    assert (est["amount"], est["total"], est["currency"]) == (83.42, 583.91, "GBP")   # 583.905, halves up


def test_the_bag_note_says_when_fares_include_different_bags():
    ff = trips.FlightFilters()
    same = [_flight("a", 1, "GBP", bags=1), _flight("b", 2, "GBP", bags=2)]
    assert trips.bags_note(same, ff) is None
    mixed = [_flight("a", 1, "GBP", bags=1), _flight("b", 2, "GBP", bags=0)]
    assert trips.bags_note(mixed, ff).startswith("Some of these fares include a checked bag and some don't. A bag costs")
    assert trips.bags_note(mixed, trips.FlightFilters(checked_bag=True)) is None
    unknown = [_flight("a", 1, "GBP", bags=0), _flight("b", 2, "GBP", bags=None)]
    assert trips.bags_note(unknown, ff).startswith("Some of these fares have no checked bag, and for others it isn't")


def test_the_trip_endpoints_say_how_prices_compare(client):
    """Through the API: sample results (all pounds) as before; then a mixed set, without and with a rate."""
    h, _ = install(client)
    soon = (date.today() + timedelta(days=30)).isoformat()
    body = {"origin": "TAS", "depart_date": soon, "filters": {"sort": "cheapest"}}
    d = client.post("/v1/trips/flights", headers=h, json=body).json()
    assert d["facets"]["currency"] == "GBP" and all(x["estimate"] is None for x in d["results"])
    assert not any("currency" in n or "priced in" in n for n in d["compare_notes"])
    ts = client.app.state.trips
    mixed = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR", airline="Euro Air")]
    real, client.app.state.trips.flights = ts.flights, (lambda q, who: mixed)
    try:
        d = client.post("/v1/trips/flights", headers=h, json=body).json()
        assert [x["id"] for x in d["results"]] == ["g1", "e1"] and "Cheapest in EUR" in d["results"][1]["tags"]
        assert any("grouped by currency" in n for n in d["compare_notes"])

        class Fixed:
            def get(self):
                return fx.Rates(_rates().per_eur, date.today() - timedelta(days=1), FETCHED)
        client.app.state.rates = Fixed()
        d = client.post("/v1/trips/flights", headers=h, json=body).json()
        e1 = d["results"][0]
        assert (e1["id"], e1["price"], e1["currency"], e1["estimate"]["amount"]) == ("e1", 400.0, "EUR", 333.66)
        assert d["results"][1]["estimate"] is None and d["facets"]["estimated"] is True
    finally:
        client.app.state.trips.flights, client.app.state.rates = real, None


def test_a_traveller_can_plan_in_their_own_currency_and_the_fare_is_kept():
    """m238 (WS5): a person who plans in US dollars sees estimates in dollars, crossed through the euro at the ECB
    rate; the provider's price and currency never change."""
    fl = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR", airline="Euro Air")]
    px = trips.flight_pricing(fl, _rates(), display="USD", today=TODAY)
    assert px.mode == "converted" and px.unit == "USD" and px.currencies == ("EUR", "GBP")   # no USD fares: by count
    # 400 EUR × 1.1165 = 446.60 USD; £389 ÷ 0.83415 × 1.1165 = 520.67 USD
    assert px.estimate(400.0, "EUR") == {"amount": 446.6, "currency": "USD", "rate": 1.1165,
                                         "source": fx.ECB_SOURCE, "as_of": "2026-11-06", "line": "ECB rate of 6 Nov 2026"}
    assert px.estimate(389.0, "GBP")["amount"] == 520.67
    assert [x.id for x in trips.filter_flights(fl, trips.FlightFilters(sort="cheapest"), px)] == ["e1", "g1"]
    assert "converted to US dollars at the ECB rate of 6 Nov 2026" in px.note("flights")
    assert (trips.flight_out(fl[1])["price"], trips.flight_out(fl[1])["currency"]) == (400.0, "EUR")
    one = trips.flight_pricing([_flight("e1", 400.0, "EUR")], _rates(), display="EUR")
    assert one.mode == "one" and one.estimate(400.0, "EUR") is None and one.note("flights") is None


def test_a_display_currency_without_a_current_rate_falls_back_to_grouping():
    fl = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR")]
    unknown = trips.flight_pricing(fl, _rates(), display="UZS")          # not an ECB currency
    assert unknown.mode == "grouped" and unknown.estimate(400.0, "EUR") is None
    stale = trips.flight_pricing(fl, _rates(as_of=date(2026, 10, 20)), display="USD", today=TODAY)
    assert stale.mode == "grouped" and stale.rates is None              # over five days old: never used
    assert fx.display_options(None) == ["GBP"]                           # without rates, pounds only
    assert fx.display_options(_rates()) == ["GBP", "EUR", "USD"]


def test_the_endpoints_take_the_display_currency(client):
    h, _ = install(client)
    soon = (date.today() + timedelta(days=30)).isoformat()
    ts = client.app.state.trips
    mixed = [_flight("g1", 389.0, "GBP"), _flight("e1", 400.0, "EUR", airline="Euro Air")]
    real, ts.flights = ts.flights, (lambda q, who: mixed)

    class Fixed:
        def get(self):
            return fx.Rates(_rates().per_eur, date.today() - timedelta(days=1), FETCHED)
    client.app.state.rates = Fixed()
    try:
        body = {"origin": "TAS", "depart_date": soon, "display_currency": "USD"}
        d = client.post("/v1/trips/flights", headers=h, json=body).json()
        est = {x["id"]: x["estimate"] for x in d["results"]}
        assert est["e1"]["currency"] == "USD" and est["g1"]["currency"] == "USD" and d["facets"]["currency"] == "USD"
        assert client.post("/v1/trips/flights", headers=h, json={**body, "display_currency": "usd"}).status_code == 422
    finally:
        ts.flights, client.app.state.rates = real, None
