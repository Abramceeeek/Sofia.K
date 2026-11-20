"""WS6 (m212): the whole trip's cost: every line says what it is, an incomplete total is never "the total", and no
currency is converted without a dated rate. The amounts below are SAMPLES except where a source is named."""
import pytest

from brain.tripbudget import Line, Rate, against, levers, summarise

# Two people, three nights in London, from Edinburgh by train, with a £900 budget
TRIP = [
    Line("trains", "Train to London and back", 180.0, "GBP", "quote", source="sample fare, labelled"),
    Line("accommodation", "3 nights, booked", 420.0, "GBP", "confirmed", source="the booking"),
    Line("local_transport", "Tube and bus, at most the Zones 1-2 daily cap", 4 * 8.90, "GBP", "estimate", "person",
         source="TfL daily cap £8.90 (read 27 Sep 2026)"),
    Line("food", "Lunches (£15 each)", 4 * 15.0, "GBP", "estimate", "person", source="ODYS's planning GUESS (D102)"),
    Line("food", "Dinners", None, None, "unknown"),
    Line("attractions", "Paid places in the day plans", 58.0, "GBP", "quote", "person", source="the cards' prices"),
    Line("experiences", "A boat trip", 24.0, "GBP", "optional", "person", source="sample"),
]


def test_an_incomplete_total_is_never_the_total():
    s = summarise(TRIP, people=2)
    assert s.known == 907.2 and not s.complete
    assert s.headline() == "At least £907 so far for 2 people (£454 each): not everything is priced yet."
    lines = s.lines()
    assert "Not priced yet: Dinners." in lines
    assert "Optional, not included: up to £48 if you add them." in lines
    assert lines[-1] == "Of which confirmed £420, quote £296, estimate £191."


def test_against_the_budget_with_what_can_move():
    s = summarise(TRIP, people=2)
    assert against(s, 900) == "£7 over your £900, before what isn't priced yet."
    lv = levers(TRIP, 2, s, 900)
    assert [x.split(":")[0] for x in lv] == ["Train to London and back", "Lunches (£15 each)",
                                             "Paid places in the day plans",
                                             "Tube and bus, at most the Zones 1-2 daily cap"]
    assert "3 nights, booked" not in " ".join(lv)                     # booked costs don't move
    assert levers(TRIP, 2, s, 1000) == [] and against(s, 1000).startswith("£93 under")


def test_per_person_and_group_lines_add_up_right():
    one = summarise([Line("accommodation", "Room", 300.0, "GBP", "confirmed"),
                     Line("food", "Food", 20.0, "GBP", "estimate", "person"),
                     Line("local_transport", "Transport", 10.0, "GBP", "estimate", "person"),
                     Line("trains", "Train", 50.0, "GBP", "quote", "person")], people=3)
    assert one.known == 300 + 3 * 80 and one.complete
    assert one.headline() == "About £540 for 3 people (£180 each), everything priced."


def test_another_currency_is_kept_apart_unless_a_dated_rate_is_given():
    eur = TRIP + [Line("attractions", "A museum in Paris", 22.0, "EUR", "quote", "person")]
    s = summarise(eur, people=2)
    assert s.known == 907.2 and s.not_converted == {"EUR": 44.0}
    assert "Plus 44 EUR, not converted (no exchange rate set)." in s.lines()
    r = summarise(eur, people=2, rates={"EUR": Rate(0.85, "a rate source", "2026-11-07")})
    assert r.known == round(907.2 + 44 * 0.85, 2) and r.not_converted == {}
    assert r.converted == ["A museum in Paris, EUR at 0.85 (a rate source, 2026-11-07)"]


def test_what_any_trip_needs_is_named_when_missing():
    s = summarise([Line("attractions", "A ticket", 30.0, "GBP", "quote")], people=1)
    assert s.missing == ["where you'll stay", "getting around", "food", "getting there and back"]
    assert s.headline() == "At least £30 so far: not everything is priced yet."


def test_a_line_must_say_what_it_is():
    with pytest.raises(ValueError):
        Line("food", "Dinners", 40.0, "GBP", "unknown")
    with pytest.raises(ValueError):
        Line("food", "Dinners", None, None, "estimate")
    with pytest.raises(ValueError):
        Line("food", "Dinners", 40.0, None, "estimate")
