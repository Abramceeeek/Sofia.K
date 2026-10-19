"""Stage 1: the Met Office forecast (weather.py) and TfL's journey times (tfl.py), with fake replies shaped like
the real ones (one keyless TfL call, 19 Oct; the Met Office's documented hourly fields)."""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from brain import db
from brain.dayplan import leg_text
from brain.moments import Moment, Point
from brain.tfl import DayView, Journey, TflTravel, TravelStore, key, next_weekday_1pm, parse, summarise
from brain.weather import DAILY_RAIN_SHARE, RETRY_AFTER_S, Forecast

from test_api import client, install  # noqa: F401  (the fixture)

LONDON = ZoneInfo("Europe/London")


# ---- the Met Office -------------------------------------------------------------------------------

def hourly(start: datetime, hours: int, temp=12.0, pop=30):
    t0 = start.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    return {"features": [{"properties": {"timeSeries": [
        {"time": (t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%MZ"), "screenTemperature": temp(i) if callable(temp)
         else temp, "probOfPrecipitation": pop(i) if callable(pop) else pop} for i in range(hours)]}}]}


def daily(days: list[date], temp=15.0, pop=60):
    return {"features": [{"properties": {"timeSeries": [
        {"time": f"{d.isoformat()}T00:00Z", "dayMaxScreenTemperature": temp, "dayProbabilityOfPrecipitation": pop}
        for d in days]}}]}


class FakeMet:
    def __init__(self, hourly=None, daily=None, fail=False):
        self.hourly, self.daily, self.fail, self.calls = hourly, daily, fail, []

    def __call__(self, url, headers, params):
        self.calls.append(url.rsplit("/", 1)[-1])
        assert headers["apikey"] == "met-key"
        if self.fail:
            raise ConnectionError("down")
        return self.hourly if url.endswith("hourly") else self.daily


def test_no_key_means_no_weather_as_before():
    f = Forecast(None)
    assert f.status == "off" and f.for_window(date.today(), "12:00", "17:00") is None and f.now() is None


def test_a_plans_hours_get_the_mean_temperature_and_chance_of_rain():
    now = datetime.now(timezone.utc)
    tomorrow = (now.astimezone(LONDON) + timedelta(days=1)).date()
    fake = FakeMet(hourly=hourly(now, 48, temp=lambda i: 10 + i % 4, pop=lambda i: 80 if i % 2 else 20))
    f = Forecast("met-key", fetch=fake)
    o = f.for_window(tomorrow, "12:00", "17:00")
    assert o.source == "hourly" and 10.5 <= o.temp_c <= 12.5 and 0.4 <= o.rain_prob <= 0.6
    assert o.line.startswith("Forecast: about ") and o.line.endswith("chance of rain (Met Office)")
    f.for_window(tomorrow, "13:00", "15:00")
    assert fake.calls == ["hourly"]          # kept for an hour: one call
    assert f.status == "met_office"


def test_further_ahead_the_daily_forecast_is_used_and_scaled():
    now = datetime.now(timezone.utc)
    day = (now.astimezone(LONDON) + timedelta(days=4)).date()
    fake = FakeMet(hourly=hourly(now, 48), daily=daily([day], temp=17.0, pop=60))
    o = Forecast("met-key", fetch=fake).for_window(day, "12:00", "17:00")
    assert o.source == "daily" and o.temp_c == 17.0 and abs(o.rain_prob - 0.6 * DAILY_RAIN_SHARE) < 1e-9


def test_a_failed_forecast_never_fails_a_plan_and_waits_before_trying_again():
    t = [1_000_000.0]
    fake = FakeMet(fail=True)
    f = Forecast("met-key", fetch=fake, clock=lambda: t[0])
    day = datetime.fromtimestamp(t[0], LONDON).date()
    assert f.for_window(day, "12:00", "17:00") is None and f.status == "met_office_error"
    n = len(fake.calls)
    f.for_window(day, "12:00", "17:00")
    assert len(fake.calls) == n              # not again within 10 minutes
    t[0] += RETRY_AFTER_S + 1
    f.for_window(day, "12:00", "17:00")
    assert len(fake.calls) > n


def test_the_weather_now_is_the_nearest_hour():
    now = datetime.now(timezone.utc)
    f = Forecast("met-key", fetch=FakeMet(hourly=hourly(now - timedelta(hours=2), 10, temp=7.0, pop=90)))
    o = f.now()
    assert o.temp_c == 7.0 and o.rain_prob == 0.9


def test_a_plan_and_a_rating_carry_the_forecast(client):
    now = datetime.now(timezone.utc)
    tomorrow = (now.astimezone(LONDON) + timedelta(days=1)).date()
    client.app.state.forecast = Forecast("met-key", fetch=FakeMet(hourly=hourly(now - timedelta(hours=1), 50,
                                                                                temp=6.0, pop=80)))
    h, _ = install(client)
    plan = client.post("/v1/me/plans", headers=h, json={
        "start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "12:00", "end_time": "17:00",
        "date": tomorrow.isoformat()}).json()
    assert plan["weather"]["line"] == "Forecast: about 6°C, 80% chance of rain (Met Office)"
    assert plan["intent"]["weather"]["rain_prob"] == 0.8
    # conditions from the app (the "it's raining" re-plan) win over the forecast
    own = client.post("/v1/me/plans", headers=h, json={
        "start": {"lat": 51.5081, "lon": -0.1281}, "start_time": "12:00", "end_time": "17:00",
        "date": tomorrow.isoformat(), "conditions": {"rain_prob": 0.1}}).json()
    assert "weather" not in own
    stop = next(st for st in plan["stops"] if st["rateable"])
    assert client.post("/v1/me/ratings", headers=h, json={"moment_id": stop["moment_id"], "rating": 4,
                                                          "plan_id": plan["id"]}).status_code == 201
    with client.app.state.Session() as s:
        r = s.query(db.Rating).one()
        assert r.temp_c == 6.0 and r.rain_prob == 0.8


def test_health_says_whether_the_keys_were_found(client):
    r = client.get("/v1/health").json()
    assert r["travel"] == "estimate" and r["weather"] == "off"


# ---- TfL ----------------------------------------------------------------------------------------

LEG = lambda mode, text, dur: {"mode": {"id": mode}, "duration": dur, "instruction": {"summary": text}}


def tfl_reply(minutes=21, walk_only=False):
    legs = [LEG("walking", "Walk to Westminster Station", 7), LEG("tube", "Jubilee line to London Bridge", 5),
            LEG("walking", "Walk to 5 BEDALE STREET, LONDON", 9)]
    if walk_only:
        legs = [LEG("walking", "Walk to 5 BEDALE STREET, LONDON", minutes)]
    return {"journeys": [{"duration": minutes + 3, "arrivalDateTime": "2026-10-21T13:26:00", "legs": legs},
                         {"duration": minutes, "arrivalDateTime": "2026-10-21T13:21:00", "legs": legs}]}


def test_the_journey_arriving_first_and_its_route_in_words():
    j = parse(tfl_reply(21))
    assert j == Journey(21.0, "transit", "walk to Westminster Station, then Jubilee line to London Bridge")
    assert parse(tfl_reply(30, walk_only=True)) == Journey(30.0, "walk", None)
    assert parse({"journeys": []}) is None
    assert summarise([LEG("bus", "24 bus to Pimlico", 12)]) == "24 bus to Pimlico"


def test_leg_text_names_the_real_lines():
    route = "walk to Westminster Station, then Jubilee line to London Bridge"
    assert leg_text(21, "transit", "the Garden", "Bank", "Borough Market", False, route) == \
        f"Getting there: about 21 min: {route}."
    assert leg_text(21, "transit", "Charing Cross", None, None, True, route).startswith(
        "Getting there: about 21 min from Charing Cross: walk to")
    assert "Tube or bus" in leg_text(21, "transit", "x", None, None, False)   # no route: as before


A, B = Point(lat=51.5008, lon=-0.1246), Point(lat=51.5055, lon=-0.0904)   # Westminster, Borough: beyond a walk
NEAR = Point(lat=51.5010, lon=-0.1240)


def test_the_table_is_used_where_it_has_the_pair_and_walks_stay_walks(tmp_path):
    calls = []
    tr = TflTravel("tfl-key", fetch=lambda url, params: (calls.append(params["app_key"]), tfl_reply(18))[1])
    est = tr.minutes(A, B)
    assert est > 18 and tr.mode(A, B) == "transit" and tr.route(A, B) is None   # not in the table yet: the estimate
    pairs = tr.pairs([(A, B), (A, B), (A, NEAR)])
    assert pairs == [(A, B)]                                   # once each, and never a short walk
    assert tr.fill(pairs, next_weekday_1pm(date(2026, 10, 19)), sleep=lambda s: None) == 1
    assert calls == ["tfl-key"] and tr.minutes(A, B) == 18 and tr.route(A, B).startswith("walk to Westminster")
    assert tr.status == "tfl"
    assert tr.fill(pairs, next_weekday_1pm(date(2026, 10, 19)), sleep=lambda s: None) == 0   # already known


def test_the_table_is_kept_across_restarts(tmp_path):
    Session = db.make_sessionmaker(db.make_engine(f"sqlite:///{tmp_path / 't.db'}"))
    tr = TflTravel("k", store=TravelStore(Session), fetch=lambda url, params: tfl_reply(18))
    tr.fill(tr.pairs([(A, B)]), next_weekday_1pm(date(2026, 10, 19)), sleep=lambda s: None)
    again = TflTravel("k", store=TravelStore(Session), fetch=lambda url, params: 1 / 0)
    assert again.minutes(A, B) == 18 and (key(A), key(B)) in again.table


def test_the_chosen_legs_are_checked_for_the_day_and_a_big_change_replans():
    replies = {"table": 18, "day": 40}
    tr = TflTravel("k", fetch=lambda url, params: tfl_reply(replies["day" if params["date"] == day.strftime(
        "%Y%m%d") else "table"]))
    day = date.today() + timedelta(days=3)
    tr.fill(tr.pairs([(A, B)]), next_weekday_1pm(date.today()), sleep=lambda s: None)
    view = tr.for_day(day, "12:00")
    assert view.minutes(A, B) == 18
    view.mode(A, B)                      # the plan chose this leg
    assert view.check() is True          # new for that day (40 min: works): plan again
    assert view.minutes(A, B) == 40 and tr.minutes(A, B) == 18   # only that day changes
    view2 = tr.for_day(day, "12:00")
    view2.mode(A, B)
    assert view2.check() is False        # already checked for that day: no new call, no change
    far = tr.for_day(date.today() + timedelta(days=60), "12:00")
    far.mode(A, B)
    assert far.check() is False          # too far ahead for TfL: the table stands


def test_a_plan_with_tfl_names_the_lines(client):
    tr = TflTravel("k", fetch=lambda url, params: tfl_reply(22))
    with client.app.state.Session() as s:   # the table, filled first as on the server (api.py, at start)
        cards = [Moment.model_validate(r.record) for r in s.query(db.MomentRow)]
    start = Point(lat=51.4967, lon=-0.1764)
    tr.fill(tr.pairs([(a.end(), b.start()) for a in cards for b in cards if a is not b]
                     + [(start, b.start()) for b in cards]), next_weekday_1pm(date.today()), sleep=lambda s: None)
    client.app.state.travel = tr
    h, _ = install(client)
    body = {"start": {"lat": 51.4967, "lon": -0.1764}, "start_time": "10:00", "end_time": "17:00", "stops": 4,
            "familiar": False, "date": (date.today() + timedelta(days=2)).isoformat()}
    plan = client.post("/v1/me/plans", headers=h, json=body).json()
    transit = [st for st in plan["stops"] if st["travel_mode"] == "transit"]
    assert transit, plan["stops"]
    assert all("Jubilee line to London Bridge" in st["travel_text"] for st in transit)
    assert client.get("/v1/health").json()["travel"].startswith("tfl")


def test_a_refused_key_stops_the_table_early_and_says_so():
    calls = []

    def refuse(url, params):
        calls.append(1)
        raise PermissionError("403")
    tr = TflTravel("wrong", fetch=refuse)
    far = [(Point(lat=51.50 + i / 100, lon=-0.20), Point(lat=51.50, lon=-0.05 - i / 100)) for i in range(40)]
    assert tr.fill(tr.pairs(far), next_weekday_1pm(date(2026, 10, 19)), sleep=lambda s: None) == 0
    assert len(calls) == 20 and tr.status == "tfl_error"


def test_pairs_tfl_finds_no_journey_for_keep_the_estimate_and_the_status_settles():
    replies = iter([tfl_reply(18), {"journeys": []}])
    tr = TflTravel("k", fetch=lambda url, params: next(replies))
    far = Point(lat=51.4613, lon=-0.3037)   # Richmond
    tr.fill(tr.pairs([(A, B), (A, far)]), next_weekday_1pm(date(2026, 10, 19)), sleep=lambda s: None)
    assert tr.status == "tfl 1/2" and tr.minutes(A, far) > 0
