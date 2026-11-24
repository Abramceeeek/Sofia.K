"""m326 (the London gate, G4 and G5; Abram's acceptance tests, 24 Nov): kinds a person didn't enjoy, and a card's
minimum age, keep cards out of every plan."""
from brain import dayplan
from brain.config import DATA_DIR
from brain.moments import load_moments

READY = [m for m in load_moments(DATA_DIR / "moments") if m.status == "ready"]
TYPES = dayplan.load_swipe_types(DATA_DIR / "swipe_items.yaml")
KINDS = dayplan.load_card_kinds(DATA_DIR / "catalogue" / "london.yaml")
out_ids = lambda entries: {cid for _, ids in entries for cid in ids}


def test_a_place_they_didnt_enjoy_keeps_out_places_of_the_same_kind():
    # Jonas (the examples): didn't enjoy Sky Garden, a garden at the top of a tower
    gone = out_ids(dayplan.kept_out(READY, [(9, "didnt_enjoy")], TYPES, KINDS, "solo"))
    assert {"m_garden_at_120", "m_horizon_22"} <= gone
    assert "m_greenwich_wolfe_view" not in gone            # a hilltop view is another kind
    # …unless they loved or were fine with another place of that kind: then it's the place, not the kind
    assert "m_horizon_22" not in out_ids(dayplan.kept_out(
        READY, [(9, "didnt_enjoy"), (9, "fine")], TYPES, KINDS, "solo"))
    assert dayplan.kept_out(READY, [(9, "loved")], TYPES, KINDS, "solo") == []


def test_a_minimum_age_keeps_a_card_out_of_family_plans():
    assert "m_park_bike_loop_hyde" in out_ids(dayplan.kept_out(READY, [], TYPES, KINDS, "family"))
    assert "m_park_bike_loop_hyde" not in out_ids(dayplan.kept_out(READY, [], TYPES, KINDS, "friends"))
    bike = next(m for m in READY if m.id == "m_park_bike_loop_hyde")
    assert bike.rules == {"min_age": 14}


def test_every_swipe_place_has_a_kind_from_the_taxonomy():
    from brain.catalogue import TAXONOMY
    known = {t for ts in TAXONOMY.values() for t in ts}
    assert set(TYPES) == set(range(1, 17)) and all(TYPES[i] and set(TYPES[i]) <= known for i in TYPES)
