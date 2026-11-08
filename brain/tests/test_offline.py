"""m221: the offline companion's reference rules, on the apps' own demo trip (app/Sources/Demo/demo_trip_days.json).
The itinerary comes first, then the stay, the journey and emergency help. Each item says how fresh it is and what to
do when it isn't. Missing data is said, never filled in. A trip's copy is deleted 30 days after it ends. Synthetic
data only."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from brain import offline

DEMO = json.loads((Path(__file__).resolve().parents[2] / "app/Sources/Demo/demo_trip_days.json").read_text())
NOW = datetime(2026, 11, 8, 9, 0, tzinfo=timezone.utc)


def _trip(**kw):
    start = DEMO["days"][0]["date"]
    nights = len(DEMO["days"]) - 1
    stay = {"kind": "stay", "title": "Sample hotel U, Covent Garden", "provider": "Booking.com", "price": 840.0,
            "booked": True, "point": {"lat": 51.51, "lon": -0.12}, "forStart": start}
    flight = {"kind": "flight", "title": "Sample Air · 20:55 → 00:22", "provider": "Skyscanner", "price": 367.0,
              "currency": "EUR", "booked": True, "arriveTime": "00:22", "leaveTime": "10:00", "arrivePlace": "LHR",
              "leavePlace": "LHR", "forStart": start}
    return {"start": start, "nights": nights, "city": "London", "days": DEMO["days"], "stay": stay, "flight": flight,
            "needStay": True, "needFlight": True, **kw}


def test_the_pack_puts_the_itinerary_first_and_says_how_fresh_each_part_is():
    trip = _trip()
    today = date.fromisoformat(trip["start"])
    pack = offline.build_pack(trip, today, NOW)
    assert [s["name"] for s in pack["sections"]] == ["itinerary", "stay", "travel", "emergency"]
    days = pack["sections"][0]["items"]
    assert len(days) == len(DEMO["days"]) and all(d["source"] == "your plan" or d["lines"] for d in days)
    planned = next(d for d in days if d["source"] == "your plan")
    assert planned["lines"] and planned["saved"]                 # the stops, and when the plan was made
    stay, flight = pack["sections"][1]["items"][0], pack["sections"][2]["items"][0]
    assert stay["lines"][1] == "£840, as found on Booking.com" and stay["status"] == "current"
    assert flight["lines"][1] == "367 EUR, as found on Skyscanner"   # m218: its own currency, never a £ sign
    assert flight["action"] == "Times can change: check with the airline on the day."
    assert "Lands 00:22 (LHR)" in flight["lines"]
    help_ = [i["lines"][0] for i in pack["sections"][3]["items"]]
    assert help_[0] == "If you or someone else is in danger or hurt, call 999." and "116 123" in help_[2]
    assert pack["within_budget"] and pack["photos"].startswith("not kept offline")


def test_stale_unbooked_and_missing_are_said_never_filled_in():
    trip = _trip()
    first = date.fromisoformat(trip["start"])
    # a day planned more than a week before it: "check"
    old = json.loads(json.dumps(trip))
    for d in old["days"]:
        if d.get("plan"):
            d["plan"]["created_at"] = (first - timedelta(days=20)).isoformat() + "T09:00:00Z"
    days = offline.build_pack(old, first - timedelta(days=1), NOW)["sections"][0]["items"]
    stale = [d for d in days if d["status"] == "check"]
    assert stale and stale[0]["action"].startswith("Planned on")
    # a stay not marked booked, and one with no address saved
    st = offline.build_pack(_trip(stay={**trip["stay"], "booked": False, "point": None}), first, NOW)
    stay = st["sections"][1]["items"][0]
    assert stay["status"] == "check" and stay["action"] == "Not marked as booked: check with Booking.com."
    assert stay["missing"] == ["the address (open the booking site when you have signal)"]
    # chosen for other dates, and a flight with no times
    other = offline.build_pack(_trip(flight={**trip["flight"], "forStart": "2026-01-01", "arriveTime": None}), first, NOW)
    fl = other["sections"][2]["items"][0]
    assert fl["status"] == "check" and fl["action"].startswith("Chosen for other dates (2026-01-01)")
    assert "when the flight lands" in fl["missing"]
    # nothing chosen yet: said
    none = offline.build_pack(_trip(stay=None), first, NOW)["sections"][1]["items"][0]
    assert none["missing"] == ["no stay chosen"]
    # a sample price is never presented as a booking
    s = offline.build_pack(_trip(stay={**trip["stay"], "sample": True}), first, NOW)["sections"][1]["items"][0]
    assert s["status"] == "check" and s["action"].startswith("A sample price")


def test_after_the_trip_it_expires_then_is_deleted():
    trip = _trip()
    end = offline.trip_end(trip)
    after = offline.build_pack(trip, end + timedelta(days=1), NOW)
    assert after["sections"][1]["items"][0]["status"] == "expired"
    assert all(d["status"] == "past" for d in after["sections"][0]["items"])
    gone = offline.build_pack(trip, end + timedelta(days=offline.KEEP_AFTER_TRIP_DAYS + 1), NOW)
    assert gone["deleted"] and gone["sections"] == [] and gone["line"].startswith("This trip ended more than 30 days")


def test_ratings_made_offline_are_never_lost_and_the_later_one_wins():
    server = [{"plan_id": 1, "moment_id": "a", "rating": 3, "at": "2026-11-08T10:00:00Z"},
              {"plan_id": 1, "moment_id": "b", "rating": 5, "at": "2026-11-08T12:00:00Z"}]
    phone = [{"plan_id": 1, "moment_id": "a", "rating": 4, "at": "2026-11-08T11:00:00Z"},   # later: wins
             {"plan_id": 1, "moment_id": "b", "rating": 2, "at": "2026-11-08T09:00:00Z"},   # older: loses
             {"plan_id": 1, "moment_id": "c", "rating": 5, "at": "2026-11-08T13:00:00Z"}]   # only on the phone: kept
    got = {r["moment_id"]: r["rating"] for r in offline.merge_ratings(phone, server)}
    assert got == {"a": 4, "b": 5, "c": 5}
    p, s = {"created_at": "2026-11-08T08:00:00Z"}, {"created_at": "2026-11-08T12:00:00Z"}
    assert offline.which_plan(p, s, unsent_for_phone_plan=0) == "server"
    assert offline.which_plan(p, s, unsent_for_phone_plan=2) == "phone"   # its ratings go first
    assert offline.which_plan(None, s, 0) == "server" and offline.which_plan(p, None, 0) == "phone"
