"""m349 (Abram, 24 Nov: "Add regression tests for: incorrect final finish times; sunset activities scheduled after
sunset when sunset is essential to the experience; unsupported or misleading food prices; seasonal descriptions that
are inappropriate for the visit date; duplicated sentences and descriptions. Ensure the displayed plan, underlying
schedule and cost summary agree.")"""
import re
from datetime import date, timedelta

from test_api import client, install  # noqa: F401  (the client fixture)

from brain import dayplan, quality, sun
from brain.config import DATA_DIR
from brain.dayplan import parse_hhmm
from brain.moments import load_moments

CARDS = {m.id: m for m in load_moments(DATA_DIR / "moments")}


def _trip(client, **kw):
    h, _ = install(client)
    body = {"start_date": (date.today() + timedelta(days=5)).isoformat(), "nights": 2, "day_start": "10:00",
            "day_end": "20:00", "stops_per_day": 3, **kw}
    r = client.post("/v1/me/trips/days", headers=h, json=body)
    assert r.status_code == 201, r.text
    return [d for d in r.json()["days"] if d.get("plan")]


def test_the_plan_its_schedule_and_its_cost_summary_agree(client):
    for feel in ("relaxed", "full"):
        for d in _trip(client, day_feel=feel):
            pl, stops = d["plan"], d["plan"]["stops"]
            t = pl["totals"]
            assert t["finish"] == stops[-1]["depart"]                           # the finish is the last stop's end
            assert abs(t["cost_gbp"] - (sum(st["cost_gbp"] for st in stops) + t["transport_gbp"])) < 0.01
            prev = parse_hhmm(d["window"]["start"])
            for st in stops:                                                   # no stop before the journey to it
                assert parse_hhmm(st["arrive"]) >= prev + (st.get("travel_min") or 0) - 1, st["title"]
                assert parse_hhmm(st["depart"]) >= parse_hhmm(st["arrive"])
                prev = parse_hhmm(st["depart"])
            assert parse_hhmm(stops[-1]["depart"]) <= parse_hhmm(d["window"]["end"])
            if fa := pl.get("free_after"):                                     # the free time is the day's own
                assert fa["from"] == stops[-1]["depart"] and fa["until"] == d["window"]["end"]
                assert fa["min"] == parse_hhmm(fa["until"]) - parse_hhmm(fa["from"])


def _sentences(text: str) -> list[str]:
    return [x.strip().lower() for x in re.split(r"(?<=[.!?])\s+", text or "") if len(x.strip()) > 12]


def test_no_sentence_is_said_twice_in_a_day(client):
    """What the day view shows (the stop's words, why it's picked, its notes and price) and what the text view shows
    (its lines, the blind pair's format): no sentence twice in a stop, or on two stops of a day."""
    def shown(st):
        v = st.get("what") or ""
        day = _sentences(" ".join(map(str, v)) if isinstance(v, list) else str(v))
        for r in st.get("reasons") or []:
            day += _sentences(r.get("you") or "")
        for ln in st.get("notes") or []:
            day += _sentences(ln)
        text = [x for ln in st.get("lines") or [] for x in _sentences(ln)]
        return day, text
    for d in _trip(client, day_feel="balanced"):
        said: dict[str, str] = {}
        for st in d["plan"]["stops"]:
            day, text = shown(st)
            assert len(day) == len(set(day)), (st["title"], day)                   # within a stop, both views
            assert len(text) == len(set(text)), (st["title"], text)
            for x in set(day):
                assert x not in said, f"{x!r} on {st['title']} and {said[x]}"      # across the day
                said[x] = st["title"]


def test_no_two_ready_cards_share_their_words():
    """The cards' own text, which both views show: never the same description or way in on two cards (the test
    cards above share theirs, so the day check covers the Brain's own sentences)."""
    for field in ("what_happens", "why_it_works"):
        texts = [getattr(m.experience, field) for m in CARDS.values() if m.status == "ready" and getattr(m.experience, field)]
        assert len(texts) == len(set(texts)), field
    by_path: dict[str, set] = {}   # variants of one moment (a plan holds one of them) may share their way in
    for m in CARDS.values():
        if m.status == "ready" and m.approach and m.approach.path:
            by_path.setdefault(m.approach.path, set()).add(m.variant_of or m.id)
    assert {k: v for k, v in by_path.items() if len(v) > 1} == {}


def test_what_the_brain_says_about_a_stop_reaches_the_day_view(client):
    """m349: free time, a later start and estimates are on `notes`, which the apps show under the stop (the day view
    never showed `lines`), as well as on the text lines."""
    days = _trip(client, day_feel="relaxed")
    notes = [n for d in days for st in d["plan"]["stops"] for n in st.get("notes") or []]
    lines = [ln for d in days for st in d["plan"]["stops"] for ln in st.get("lines") or []]
    assert notes and all(n in lines for n in notes)


def test_a_meal_with_no_named_place_says_its_price_is_an_estimate():
    st = {"key": "lunch@m_x", "moment_id": "lunch@m_x", "cost_gbp": 6.0, "cost_kind": "food"}
    assert dayplan._cost_line(st) == "Food: about £6, ODYS's estimate"
    named = {"key": "m_padella_borough#lunch", "moment_id": "m_padella_borough", "cost_gbp": 15.0, "cost_kind": "food"}
    assert dayplan._cost_line(named) == "Food: about £15"                    # its menu's price, checked
    two = [dict(st, lines=[]), dict(st, key="dinner@m_y", moment_id="dinner@m_y", lines=[])]
    dayplan.say_estimates(two)
    assert two[0]["lines"] == [dayplan.ESTIMATE_MEAL] and two[1]["lines"] == []   # said once a day


def test_no_ready_card_promises_something_out_of_season():
    """A winter visitor isn't promised summer flowers: a card's words name a season-bound thing only with its season."""
    bad = {m.id: hits for m in CARDS.values() if m.status == "ready"
           if (hits := quality.unseasonal(" ".join([m.title, m.experience.what_happens or "",
                                                    m.experience.why_it_works or ""])))}
    assert bad == {}


def test_unseasonal_words_are_found_and_qualified_ones_allowed():
    assert quality.unseasonal("A rooftop garden full of summer flowers.") == ["summer flowers"]
    assert quality.unseasonal("Cherry blossom over the path.") == ["blossom"]
    assert quality.unseasonal("In spring, cherry blossom over the path.") == []
    assert quality.unseasonal("Planted beds and trees, with flowers in summer.") == []
    assert quality.unseasonal("A calm walk among the trees.") == []


def test_sunset_is_worked_out_for_the_date_and_the_place():
    d = date(2026, 12, 4)
    assert "15:45" <= sun.sunset(d) <= "16:00"                                # central London (tests/test_sun.py)
    seville = sun.sunset(d, 37.3891, -5.9845, "Europe/Madrid")
    assert seville and parse_hhmm(seville) - parse_hhmm(sun.sunset(d)) > 120   # later, by its own clock
    assert sun.sunset(date(2026, 6, 21)) != sun.sunset(d)


def test_a_place_called_at_sunset_is_planned_at_sunset_on_every_day_it_comes(client):
    for d in _trip(client, day_feel="full", nights=3):
        set_at = parse_hhmm(sun.sunset(date.fromisoformat(d["date"])))
        for st in d["plan"]["stops"]:
            m = CARDS.get(st["moment_id"])
            if m and "sunset" in m.title.lower() and m.best_time.best_around_sunset:
                lo, hi = m.best_time.best_around_sunset
                assert set_at + lo <= parse_hhmm(st["arrive"]) <= set_at + hi, (d["date"], st["title"], st["arrive"])
