"""m229: the globally neutral kinds of places (data/categories_global.yaml), proposed for after the friends' round.
Nothing serves it: the Brain still serves data/categories.yaml, and places_mode stays "named"."""
import json
from pathlib import Path

import yaml

from brain.categories import category_from, load_categories
from brain.config import DATA_DIR
from brain.moments import load_moments
from brain.population import load_population

G = yaml.safe_load((DATA_DIR / "categories_global.yaml").read_text(encoding="utf-8"))
SERVED = load_categories(DATA_DIR / "categories.yaml")
POP = load_population(DATA_DIR / "priors.yaml")
READY = {m.id for m in load_moments(DATA_DIR / "moments") if m.status == "ready"}
PHOTOS = json.load(open(DATA_DIR.parent.parent / "app/Sources/Photos/photo-credits.json"))


def test_it_keeps_eight_kinds_under_the_same_keys():
    assert len(G["items"]) == 8 and list(G["items"]) == list(SERVED.items)   # stored answers keep their meaning


def test_abrams_wordings():
    assert G["want_prompt"] == "Would you like to try this kind of experience?"
    titles = {k: it["title"] for k, it in G["items"].items()}
    assert titles["river"] == "Water experiences and boat trips"
    assert titles["street_food"] == "Local food and food markets"
    assert titles["hands_on"] == "Hands-on activities and adventures"


def test_nothing_names_london_and_the_photo_says_where_it_is_from():
    texts = [G["prompt"], G["note"], G["want_prompt"]]
    texts += [it[f] for it in G["items"].values() for f in ("title", "line", "phrase")]
    assert not [t for t in texts if "london" in t.lower()]
    assert "{city}" in G["example_note"] and "{title}" in G["example_note"]


def test_every_kind_has_a_ready_example_with_a_photo_and_real_tags():
    for key, it in {**G["items"], **G["candidates"]}.items():
        c = category_from(key, it)
        assert set(c.moment.features.place) | set(c.moment.features.moment) <= set(POP.names), key
        assert c.phrase == c.phrase.lower(), key
        if key == "live":
            assert c.example is None          # no ready card is a show, a gig or a match: said, not faked
        else:
            assert c.example in READY and c.example in PHOTOS, key


def test_the_proposal_is_not_served():
    src = Path(__file__).resolve().parents[1] / "src" / "brain"
    assert not [p.name for p in src.glob("*.py") if "categories_global" in p.read_text(encoding="utf-8")]
    assert SERVED.want_prompt == "Would you like to try it in London?"          # the round's wording, unchanged
    assert yaml.safe_load((DATA_DIR / "onboarding.yaml").read_text())["places_mode"] == "named"
