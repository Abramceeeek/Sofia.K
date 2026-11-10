"""m243: every card photo stays correctly credited and openly licensed as the catalogue grows (Abram, m234). Checked
in both apps, against the credits file, the design page and the catalogue. No network: the licences were read from
Wikimedia Commons when each photo was chosen (design/photo-credits.md), and a sample is re-read by hand (m243)."""
import json
import re

from brain.catalogue import PHOTO_LICENCES, load_catalogue
from brain.config import DATA_DIR

ROOT = DATA_DIR.parents[1]
IOS = ROOT / "app" / "Sources" / "Photos"
ANDROID = ROOT / "android" / "app" / "src" / "main" / "assets" / "photos"
CREDITS = json.loads((IOS / "photo-credits.json").read_text(encoding="utf-8"))
OPEN = re.compile(r"^(CC0|PD|Public domain|CC BY(-SA)? \d\.\d( [a-z]{2})?)$")   # never NC or ND


def test_both_apps_carry_the_same_photos_and_the_same_credits():
    assert (IOS / "photo-credits.json").read_bytes() == (ANDROID / "photo-credits.json").read_bytes()
    jpgs = lambda d: {p.name for p in d.glob("*.jpg")}
    assert jpgs(IOS) == jpgs(ANDROID) == {v["file"] for v in CREDITS.values()}   # no photo without a credit, or the reverse


def test_every_credit_has_title_author_licence_and_source_and_the_licence_is_open():
    for card, v in CREDITS.items():
        assert v["title"] and v["author"], card
        assert OPEN.match(v["licence"]), (card, v["licence"])
        assert not re.search(r"\bNC\b|\bND\b|NonCommercial|NoDerivatives", v["licence"]), card
        assert v["source"].startswith("https://commons.wikimedia.org/wiki/File:"), card
        lic = v["licence"]
        if lic.startswith("CC BY"):
            assert v["licenceURL"].startswith("https://creativecommons.org/licenses/by"), card
            assert ("-sa/" in v["licenceURL"]) == ("SA" in lic), card                   # the URL matches the name
        assert v["file"] == f"{card}.jpg"


def test_credits_match_the_design_page_and_point_at_ready_cards():
    page = (ROOT / "design" / "photo-credits.md").read_text(encoding="utf-8")
    ready = {i for x in load_catalogue() for i in x.legacy_ids}
    for card, v in CREDITS.items():
        assert f"`{card}`" in page and v["author"] in page, card                     # Abram's review page says it too
        assert card in ready, card                                                    # no photo for a retired card
    assert all(any(p.licence.startswith(x) for x in PHOTO_LICENCES) for e in load_catalogue() for p in e.photos)


def test_the_apps_show_the_credit_the_licence_asks_for():
    swift = (ROOT / "app" / "Sources" / "CardPhotos.swift").read_text(encoding="utf-8")
    assert "by \\(author), \\(licence), Wikimedia Commons (resized)" in swift              # title, author, licence, change
    kotlin = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "android" / "app" / "src" / "main").rglob("*.kt"))
    assert "Wikimedia Commons (resized)" in kotlin
