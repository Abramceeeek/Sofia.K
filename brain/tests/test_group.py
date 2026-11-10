"""m240 (WS6): a shared trip for three synthetic people on London's checked experiences. The hard rules (rejections,
the smallest budget, each first must-see) always hold, highlights take turns, and one person's louder tastes don't
take the trip under the Nash rule as they do under a plain average."""
import numpy as np

from brain import group
from brain.catalogue import load_catalogue
from brain.config import DATA_DIR
from brain.discovery import Scorer
from brain.population import load_population

POP = load_population(DATA_DIR / "priors.yaml")
CANDS = list(load_catalogue())
X = {x.legacy_ids[0]: x for x in CANDS}


def scorer(scale=1.0, **w):
    d = np.zeros(len(POP.delta_prior_sd))
    for k, v in w.items():
        d[POP.names.index(k)] = v * scale
    return Scorer(POP, d)


def members(intense=1.0, **extra):
    return [group.Member("Member A", scorer(intense, movement_views=2.0, awe=2.0), **extra.get("A", {})),
            group.Member("Member B", scorer(history_culture=2.0, absorption=1.5), **extra.get("B", {})),
            group.Member("Member C", scorer(food=2.5, local_novel=1.0), **extra.get("C", {}))]


def test_rejections_budgets_and_must_sees_always_hold():
    ms = members(A={"budget_per_day": 20.0, "rejects": (X["m_horizon_22"].id,)},
                 B={"musts": (X["m_courtauld_gallery"].id, X["m_soane_museum"].id)},
                 C={"budget_per_day": 40.0, "musts": (X["m_borough_market_graze"].id,)})
    p = group.plan(ms, CANDS, days=2, per_day=3)
    ids = [x.id for x in p.stops]
    assert X["m_horizon_22"].id not in ids                              # one person's no is a no
    assert X["m_courtauld_gallery"].id in ids and X["m_borough_market_graze"].id in ids   # each first must-see
    assert all(sum(x.price.value.amount for x in day) <= 20.0 for day in p.days)        # the smallest budget, daily
    assert any("rejected" in n for n in p.notes) and len(ids) == len(set(ids)) == 6
    # a must-see the smallest budget can't take is left for the group to decide, and said: never forced in
    tight = members(A={"budget_per_day": 5.0}, B={"musts": (X["m_courtauld_gallery"].id,)})
    q = group.plan(tight, CANDS, days=2, per_day=3)
    assert X["m_courtauld_gallery"].id not in [x.id for x in q.stops]
    assert any("Member B's must-see" in n and "smallest budget" in n for n in q.notes)
    assert all(sum(x.price.value.amount for x in day) <= 5.0 for day in q.days)


def test_highlights_take_turns_and_members_are_never_named():
    p = group.plan(members(), CANDS, days=3, per_day=2)
    assert [h.split("'s pick")[0] for h in p.highlights] == ["Day 1 leads with Member A", "Day 2 leads with Member B",
                                                             "Day 3 leads with Member C"]
    assert set(p.satisfaction) == {"Member A", "Member B", "Member C"}


def test_one_louder_member_doesnt_take_the_trip_under_nash():
    k = max(1, round(group.DELTA * len(CANDS)))
    loud = members(intense=3.0)
    top_a = {x.id for x in sorted(CANDS, key=lambda x: -loud[0].scorer.p_good(x))[:k]}
    avg = group.plan(loud, CANDS, days=2, per_day=3, method="average")
    nash = group.plan(loud, CANDS, days=2, per_day=3, method="nash")
    share = lambda p: len({x.id for x in p.stops} & top_a) / len(p.stops)
    assert share(avg) > share(nash)                                     # the average follows the loudest
    assert nash.fairness()["min"] >= avg.fairness()["min"] and nash.fairness()["gap"] <= avg.fairness()["gap"]
    assert all(nash.proportional.values())                              # everyone gets one of their own favourites


def test_least_misery_is_kept_for_comparison_and_can_leave_everyone_lukewarm():
    lm = group.plan(members(), CANDS, days=2, per_day=3, method="least_misery")
    nash = group.plan(members(), CANDS, days=2, per_day=3, method="nash")
    assert lm.fairness()["gap"] <= nash.fairness()["gap"] + 1e-9
    assert lm.method == "least_misery" and len(lm.stops) == 6
