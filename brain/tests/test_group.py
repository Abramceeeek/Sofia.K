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


# ---- m250: Abram's further cases (m244): access, limited time, nothing that suits someone --------------------------

def _london():
    from brain.catalogue import load_catalogue
    return [x for x in load_catalogue() if x.status == "ready"]


def test_a_step_free_need_removes_places_a_source_says_have_steps_and_flags_unknowns():
    import numpy as np
    from brain.config import DATA_DIR
    from brain.discovery import Scorer
    from brain.group import Member, plan
    from brain.population import load_population
    pop = load_population(DATA_DIR / "priors.yaml")
    xs = _london()
    rng = np.random.default_rng(7)
    ms = [Member(f"Member {c}", Scorer(pop, rng.normal(0, pop.delta_prior_sd)), needs_step_free=(c == "A")) for c in "ABC"]
    gp = plan(ms, xs, 2, 3)
    assert not [x for x in gp.stops if x.accessibility.step_free.known and x.accessibility.step_free.value == "no"]
    unknown = [x for x in gp.stops if not x.accessibility.step_free.known]
    assert not unknown or any("isn't known" in n for n in gp.notes)       # said, never read as "no"
    strict = plan(ms, xs, 2, 3, unknown_access="exclude")
    assert all(x.accessibility.step_free.known for x in strict.stops)


def test_someone_there_one_day_leads_that_day_and_is_judged_on_it():
    import numpy as np
    from brain.config import DATA_DIR
    from brain.discovery import Scorer
    from brain.group import Member, plan
    from brain.population import load_population
    pop = load_population(DATA_DIR / "priors.yaml")
    rng = np.random.default_rng(11)
    ms = [Member("Member A", Scorer(pop, rng.normal(0, pop.delta_prior_sd)), days_present=(2,))] + [
        Member(f"Member {c}", Scorer(pop, rng.normal(0, pop.delta_prior_sd))) for c in "BC"]
    gp = plan(ms, _london(), 3, 3)
    assert gp.highlights[1].startswith("Day 2 leads with Member A's pick")
    a = ms[0].scorer
    assert abs(gp.satisfaction["Member A"] - sum(a.p_good(x) for x in gp.days[1]) / len(gp.days[1])) < 1e-9


def test_when_nothing_suits_a_member_it_is_said():
    import numpy as np
    from brain.config import DATA_DIR
    from brain.discovery import Scorer
    from brain.group import Member, plan
    from brain.population import load_population
    pop = load_population(DATA_DIR / "priors.yaml")
    sd = np.asarray(pop.delta_prior_sd, dtype=float)
    d = -3 * sd
    d[[i for i, k in enumerate(pop.names[:len(sd)]) if k.startswith("cost")]] = 0
    ms = [Member("Member A", Scorer(pop, d)), Member("Member B", Scorer(pop, None))]
    gp = plan(ms, _london(), 1, 3)
    assert any("Nothing here is a strong match for Member A" in n for n in gp.notes)


# ---- m256: Abram's regression cases (m252) -------------------------------------------------------------------------

def _members(n, per=None, seed=5):
    import numpy as np
    from brain.config import DATA_DIR
    from brain.discovery import Scorer
    from brain.group import Member
    from brain.population import load_population
    pop = load_population(DATA_DIR / "priors.yaml")
    rng = np.random.default_rng(seed)
    return [Member(f"Member {'ABCDEFGHIJ'[i]}", Scorer(pop, rng.normal(0, pop.delta_prior_sd)), **(per or {}).get(i, {}))
            for i in range(n)]


def test_arriving_late_or_leaving_early_counts_only_the_days_there():
    from brain.group import plan
    ms = _members(3, {0: dict(days_present=(2, 3)), 1: dict(days_present=(1,))})
    gp = plan(ms, _london(), 3, 2)
    a, b = ms[0].scorer, ms[1].scorer
    days23 = gp.days[1] + gp.days[2]
    assert abs(gp.satisfaction["Member A"] - sum(a.p_good(x) for x in days23) / len(days23)) < 1e-9
    assert abs(gp.satisfaction["Member B"] - sum(b.p_good(x) for x in gp.days[0]) / len(gp.days[0])) < 1e-9
    assert gp.highlights[0].startswith("Day 1 leads with Member B")       # B is only there on day 1


def test_joining_part_of_a_day_counts_only_those_stops():
    from brain.group import plan
    ms = _members(2, {0: dict(joins_first={1: 1})})
    gp = plan(ms, _london(), 1, 3)
    assert abs(gp.satisfaction["Member A"] - ms[0].scorer.p_good(gp.days[0][0])) < 1e-9


def test_different_daily_budgets_keep_every_day_within_the_smallest():
    from brain.group import plan
    ms = _members(3, {0: dict(budget_per_day=15.0), 1: dict(budget_per_day=60.0)})
    gp = plan(ms, _london(), 2, 3)
    for i, d in enumerate(gp.days, 1):
        cost = sum(x.price.value.amount for x in d)
        assert cost <= 15.0 + 1e-9 or any(n.startswith(f"Day {i} costs") for n in gp.notes)


def test_different_access_needs_strict_excludes_unverified_and_says_why():
    from brain.group import plan
    xs = _london()
    loose = plan(_members(3, {0: dict(needs_step_free=True)}), xs, 2, 3)
    strict = plan(_members(3, {0: dict(needs_step_free=True), 1: dict(needs_step_free=True, strict_access=True)}), xs, 2, 3)
    assert all(x.accessibility.step_free.known and x.accessibility.step_free.value != "no" for x in strict.stops)
    assert any("no source confirms they're step-free" in n for n in strict.notes)  # why, by name
    assert not [x for x in loose.stops if x.accessibility.step_free.known and x.accessibility.step_free.value == "no"]


def test_a_large_group_is_told_the_trade_off_and_the_alternatives():
    from brain.group import plan
    gp = plan(_members(10, seed=3), _london(), 2, 3)
    if not all(gp.proportional.values()):
        note = next(n for n in gp.notes if "none of their favourite places" in n)
        assert "add a day" in note and "split up" in note
