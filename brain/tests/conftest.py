"""Shared fixtures. The test moments are made up for testing: they are not real curated moments."""

from pathlib import Path

import pytest

from brain.moments import Moment
from brain.population import load_population

DATA = Path(__file__).resolve().parents[1] / "data"

ALL_TAGS = dict(movement_views=0, food=0, green_nature=0, history_culture=0, iconic=0, local_novel=0,
                crowds=0, walking_effort=0, active=0, outdoor_exposure=0, photo_potential=0)


def make_moment(mid: str, lat: float, lon: float, *, tags=None, mtags=None, cost=0.0,
                window="09:00-20:00", minutes=30, swipe=False) -> Moment:
    place = dict(ALL_TAGS, **(tags or {}))
    moment = {**dict(contrast_reveal=0, absorption=0, awe=0, social_pull=0), **(mtags or {})}
    return Moment.model_validate({
        "id": mid, "title": f"Test moment {mid}", "status": "ready", "swipe": swipe,
        "place": {"name": f"Test place {mid}", "lat": lat, "lon": lon},
        "approach": {"from": "test", "start_point": {"lat": lat, "lon": lon}, "duration_min": 5},
        "experience": {"duration_min": minutes - 5, "end_point": {"lat": lat + 0.0005, "lon": lon}},
        "best_time": {"time_of_day": [window] if isinstance(window, str) else window},
        "features": {"place": place, "moment": moment},
        "cost_gbp": cost, "source": "test",
    })


@pytest.fixture
def pop():
    return load_population(DATA / "priors.yaml")


@pytest.fixture
def test_moments():
    # A loose cluster around central London, ~0.5-2 km apart.
    return [
        make_moment("t_view", 51.5055, -0.0754, tags=dict(movement_views=2, outdoor_exposure=2, photo_potential=2),
                    mtags=dict(awe=2), swipe=True),
        make_moment("t_market", 51.5055, -0.0910, tags=dict(food=2, crowds=2, local_novel=1), cost=15, swipe=True),
        make_moment("t_museum", 51.4967, -0.1764, tags=dict(history_culture=2, iconic=2, crowds=1),
                    mtags=dict(contrast_reveal=2), window="10:00-17:30", minutes=90, swipe=True),
        make_moment("t_park", 51.5073, -0.1657, tags=dict(green_nature=2, outdoor_exposure=2, walking_effort=1), swipe=True),
        make_moment("t_boat", 51.5079, -0.1224, tags=dict(movement_views=2, outdoor_exposure=1), cost=10,
                    mtags=dict(absorption=1)),
        make_moment("t_pricey", 51.5134, -0.1300, tags=dict(iconic=1, crowds=2), cost=80),
    ]
