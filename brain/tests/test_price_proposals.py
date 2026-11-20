"""m253: price discrepancies are proposals until Abram approves them: the cards the planner reads don't change."""
import yaml

from brain.config import DATA_DIR
from brain.moments import load_moments

CARDS = {m.id: m for m in load_moments(DATA_DIR / "moments")}
P = yaml.safe_load((DATA_DIR / "catalogue" / "london_price_proposals.yaml").read_text(encoding="utf-8"))["proposals"]


def test_cards_keep_their_prices_until_approved():
    for card, p in P.items():
        assert CARDS[card].cost_gbp == p["card"]["amount"], card       # change only after Abram's yes
        assert all(u.startswith("https://") for u in p["official"]["sources"]), card
        assert p["confidence"] in ("high", "medium", "low") and p["proposal"]


def test_every_unclear_price_is_held_not_guessed():                       # Abram, m260
    assert all(p["proposal"].startswith("Hold") for p in P.values())
