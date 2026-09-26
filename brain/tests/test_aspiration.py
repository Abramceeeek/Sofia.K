from brain.aspiration import load_aspiration
from brain.features import moment_features
from brain.moments import load_moments
from brain.personal import prior_only
from brain.scoring import named_weights, swipe_observation, update_person

from conftest import DATA

AMAP = load_aspiration(DATA / "aspiration.yaml")


def test_question_offers_the_fixed_list_and_none():
    assert [f.label for f in AMAP.fields.values()] == [
        "Finance & tech", "Food", "History & culture", "Nature", "Art & design", "None of these"]


def test_answers_parse_from_codes_or_labels_and_none_means_no_field():
    assert AMAP.parse("food, Nature")[0] == {"food", "nature"}
    assert AMAP.parse("History and culture; finance & tech")[0] == {"history_culture", "finance_tech"}
    assert AMAP.parse("None of these") == (frozenset(), [])
    assert AMAP.parse("") == (frozenset(), [])
    assert AMAP.parse("food, knitting") == (frozenset({"food"}), ["knitting"])


def test_fields_map_to_existing_tags_or_listed_moments():
    ms = {m.id: m for m in load_moments(DATA / "moments")}
    assert "food" in AMAP.fields_of(ms["m_open_kitchen_steakhouse"])            # food tag 2
    assert "nature" in AMAP.fields_of(ms["m_richmond_park_view"])               # green_nature 2
    assert "history_culture" in AMAP.fields_of(ms["m_nhm_whale_hall"])
    assert AMAP.fields_of(ms["m_canary_wharf_towers"]) == {"finance_tech"}       # listed by id
    assert "food" not in AMAP.fields_of(ms["a_covent_garden_soho"])             # food 1 is a side note


def test_coverage_flags_fields_with_fewer_than_two_ready_moments(test_moments):
    rows = {r["field"]: r for r in AMAP.coverage(load_moments(DATA / "moments"))}
    assert rows["art_design"]["ready"] == 0 and rows["art_design"]["drafts"] == 0 and rows["art_design"]["flag"]
    assert rows["finance_tech"]["drafts"] == 2
    # checked test moments count as ready
    ready = {r["field"]: r for r in AMAP.coverage(test_moments)}
    assert all(r["ready"] + r["drafts"] >= 0 for r in ready.values())


def test_a_match_raises_the_score_and_swipes_can_move_it(pop, test_moments):
    m = test_moments[0]
    x0 = pop.vector(moment_features(m))
    x1 = pop.vector(moment_features(m, aspiration_match=1.0))
    assert float((x1 - x0) @ pop.b_pop) == pop.spec("aspiration_match").mean
    # someone who picked the field but keeps not enjoying matching places: the weight goes down
    obs = [swipe_observation(pop, m, "didnt_enjoy", aspiration_match=1.0) for _ in range(8)]
    post = update_person(pop, obs)
    w = {n.name: n for n in named_weights(pop, post)}
    assert w["aspiration_match"].weight < pop.spec("aspiration_match").mean
    prior = {n.name: n for n in named_weights(pop, prior_only(pop.delta_prior_sd))}
    assert prior["aspiration_match"].weight == pop.spec("aspiration_match").mean


def test_fields_command_prints_a_flag_per_short_field(capsys):
    from brain import testb
    assert testb.main(["--data", str(DATA), "fields"]) == 0
    out = capsys.readouterr().out
    assert "Art & design" in out and "FLAG" in out
