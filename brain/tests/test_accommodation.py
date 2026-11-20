"""WS4 (m209): a stay judged for this trip: like for like across dates, the whole cost in one currency, and separate
lenses (cheapest, closest to your days, most flexible, the trade-offs) with no made-up quality score."""
from brain import stayprices, stayranking, trips
from brain.moments import Point
from brain.stayprices import DayEnds, StayTerms
from brain.travel import LondonEstimate

WANT = StayTerms("h1", "Sample hotel", 51.51, -0.12, 600.0, 3, room="Double room", board="Room only", refundable=True)
EST = LondonEstimate()


def _resp(*rates):
    return {"data": [{"hotelId": "h1", "roomTypes": [{"rates": list(rates)}]}]}


def _rate(name="Double room", amount=600, board="RO", board_name="Room only", tag="RFN", currency="GBP", fees=()):
    r = {"name": name, "boardType": board, "cancellationPolicies": {"refundableTag": tag} if tag else {},
         "retailRate": {"total": [{"amount": amount, "currency": currency}],
                        "taxesAndFees": [dict(included=inc, amount=a, description="Tax", **({"currency": c} if c else {}))
                                         for inc, a, c in fees]}}
    if board_name is not None:
        r["boardName"] = board_name
    return r


def test_same_hotel_same_room_same_terms():
    assert stayprices.match_rate(_resp(_rate()), WANT) == (600.0, 0.0, [])


def test_a_different_room_board_or_cancellation_is_said():
    assert stayprices.match_rate(_resp(_rate(name="Twin room")), WANT)[2] == ["a different room (Twin room)"]
    assert stayprices.match_rate(_resp(_rate(board="BB", board_name="Breakfast included")), WANT)[2] == \
        ["breakfast included"]
    assert stayprices.match_rate(_resp(_rate(tag="NRFN")), WANT)[2] == ["non-refundable"]


def test_terms_the_provider_doesnt_give_are_never_assumed_the_same():
    assert stayprices.match_rate(_resp(_rate(tag=None)), WANT)[2] == ["cancellation terms not given"]
    assert stayprices.match_rate(_resp(_rate(board="BI", board_name=None)), WANT)[2] == ["meals not given"]


def test_taxes_and_property_fees_not_included_are_added_in_the_same_currency_only():
    fees = [(True, 50, None), (False, 12.5, None), (False, 30, "GBP")]   # a tax inside the total; two to pay there
    assert stayprices.match_rate(_resp(_rate(fees=fees)), WANT) == (600.0, 42.5, [])
    city_tax = [(False, 12.5, None), (False, 8, "EUR")]                   # a city tax in euros, on a total in pounds
    total, there, differs = stayprices.match_rate(_resp(_rate(fees=city_tax)), WANT)
    assert (total, there) == (600.0, 12.5) and differs == ["8.00 EUR paid at the property, not added in"]
    rate = _rate(fees=city_tax)
    assert trips.rate_pay_there(rate) == 12.5 and trips.rate_fees_there(rate)[1] == [(8.0, "EUR")]


def test_a_price_in_another_currency_is_never_compared_and_a_missing_currency_is_said():
    assert stayprices.match_rate(_resp(_rate(currency="EUR")), WANT) == (None, 0.0, [])
    eur_and_gbp = _resp(_rate(amount=500, currency="EUR"), _rate(amount=650))
    assert stayprices.match_rate(eur_and_gbp, WANT)[0] == 650.0                 # the euro price never wins on number
    c = stayprices.cost_lines(StayTerms("x", "X", None, None, 420.0, 2, currency=""), sample=False)
    assert "(currency not given)" in c["line"] and "£" not in c["line"]
    assert stayprices.cost_lines(StayTerms("x", "X", None, None, 420.0, 2, currency="EUR"),
                                 sample=False)["line"].startswith("420 EUR for 2 nights")


def test_a_day_without_places_is_said_not_silently_left_out():
    p = Point(lat=51.51, lon=-0.12)
    fit = stayprices.trip_fit(p, [DayEnds(0, p, p), DayEnds(1, None, None), DayEnds(2, p, p)], EST)
    assert fit["missing"] == [1] and "Day 2 has no places yet, so it isn't counted." in fit["line"]
    none = stayprices.trip_fit(p, [DayEnds(0, None, None)], EST)
    assert none["days"] == [] and none["missing"] == [0]


def _option(sid, lat, lon, price, refundable=True, currency="GBP", days=None, pay_there=0.0):
    stay = StayTerms(sid, sid, lat, lon, price, 3, currency=currency, refundable=refundable, pay_there=pay_there)
    return stayranking.StayOption(stay, stayprices.trip_fit(Point(lat=lat, lon=lon), days or DAYS, EST))


# the person's days are in the City (around Bank); the centre of London is Charing Cross
CITY = Point(lat=51.5133, lon=-0.0890)
DAYS = [DayEnds(0, CITY, CITY), DayEnds(1, Point(lat=51.5155, lon=-0.0822), CITY)]


def test_far_from_every_place_is_said_in_minutes_and_near_the_days_beats_near_the_centre():
    near_days = _option("whitechapel", 51.5194, -0.0610, 520)       # east, far from the centre, near the City
    centre = _option("charing_cross", 51.5080, -0.1247, 520)          # the centre, further from these days
    far = _option("wembley", 51.5560, -0.2796, 380)                   # far from everything planned
    out = stayranking.lenses([near_days, centre, far])
    assert out["closest"] == "whitechapel"                            # distance to the centre plays no part
    assert out["cheapest"] == "wembley"
    far_line = out["lines"]["wembley"][1]
    assert far_line.startswith("About ") and "min a day more travel than the closest" in far_line
    assert far.travel_a_day > near_days.travel_a_day + 30


def test_the_lenses_are_separate_and_say_their_trade_offs_in_plain_terms():
    a = _option("a", 51.5194, -0.0610, 600, refundable=False)
    b = _option("b", 51.5080, -0.1247, 520, refundable=True)
    c = _option("c", 51.5560, -0.2796, 380, refundable=None, pay_there=20)
    d = _option("d", 51.5560, -0.2796, 700, refundable=True)            # dearer and no closer than c: beaten
    eur = _option("e", 51.5194, -0.0610, 100, currency="EUR")
    out = stayranking.lenses([a, b, c, d, eur])
    assert out["cheapest"] == "c" and out["lines"]["c"][0].startswith("Cheapest of these: £400 for 3 nights, "
                                                                      "including £20 paid at the property")
    assert out["flexible"] == "b" and out["closest"] == "a"
    assert [t["id"] for t in out["tradeoffs"]] == ["c", "b", "a"] and "d" not in [t["id"] for t in out["tradeoffs"]]
    assert out["tradeoffs"][2]["line"].startswith("£200 more, and about ")
    assert out["note"] == "1 stay priced in another currency isn't compared." and "e" not in out["lines"]
    assert out["lines"]["c"][2] == "Cancellation terms not given."
    none_free = stayranking.lenses([a])
    assert none_free["flexible"] is None and none_free["flexible_note"].startswith("None of these")


def test_no_day_planned_yet_means_no_location_lens_not_a_guess():
    p = _option("p", 51.5080, -0.1247, 500, days=[DayEnds(0, None, None)])
    out = stayranking.lenses([p])
    assert out["closest"] is None and out["lines"]["p"][1] == "How far it is from your days: plan your days first."


def test_the_arrival_and_leaving_days_count_only_the_legs_that_happen():
    stay, near, far = Point(lat=51.51, lon=-0.12), Point(lat=51.511, lon=-0.121), Point(lat=51.53, lon=-0.20)
    fit = stayprices.trip_fit(stay, [DayEnds(0, far, near, arrive=True), DayEnds(1, near, near),
                                     DayEnds(2, near, far, leave=True)], EST)
    day1, day2, day3 = fit["days"]
    assert day1["text"].startswith("Day 1: you arrive from your journey; ") and "min there" not in day1["text"]
    assert day3["text"].endswith("at the end you leave for your journey") and day2["text"].startswith("Day 2: ")
    # the far morning on day 1 (from the journey) and the far evening on day 3 (to the journey) never count
    assert fit["to_first"] == stayprices.trip_fit(stay, [DayEnds(1, near, near)], EST)["to_first"]
    assert fit["back"] == stayprices.trip_fit(stay, [DayEnds(1, near, near)], EST)["back"]
