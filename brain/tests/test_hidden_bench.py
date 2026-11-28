"""The hidden-preference bench stays independent of the engine (Abram, m364: "don't let the benchmark become circular
again"): its generator imports nothing from the Brain and reads none of ODYS's own judgements of places."""
import ast
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
DATA = Path(__file__).resolve().parents[1] / "data"


def test_the_hidden_truth_imports_nothing_from_the_brain():
    tree = ast.parse((SCRIPTS / "hidden_truth.py").read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add((node.module or "").split(".")[0])
    assert "brain" not in mods
    assert mods <= {"__future__", "hashlib", "re", "dataclasses", "pathlib", "numpy", "yaml"}


def test_the_hidden_truth_reads_no_tags_records_or_aspiration_map():
    """Every string the code uses (docstrings aside): no ODYS judgement file, and no card key but id, title, status
    and cost."""
    tree = ast.parse((SCRIPTS / "hidden_truth.py").read_text())
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body
            and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
               and id(n) not in docs}
    for banned in ("features", "place", "moment", "aspiration.yaml", "priors.yaml", "popularity.yaml", "places",
                   "tags"):
        assert banned not in strings, banned
    assert {"id", "title", "status", "cost_gbp", "ready", "moments", "catalogue", "london.yaml"} <= strings


def test_hidden_travellers_are_repeatable_and_differ():
    sys.path.insert(0, str(SCRIPTS))
    import hidden_truth as truth
    places, items, shown = truth.load_world(DATA)
    a1, a2 = truth.make_traveller("art", 0, places), truth.make_traveller("art", 0, places)
    assert a1.taste == a2.taste and a1.eps == a2.eps
    assert truth.observe(a1, places, items, shown) == truth.observe(a2, places, items, shown)
    b = truth.make_traveller("food", 0, places)
    assert a1.taste != b.taste
    assert truth.similarity(a1, a1) > 0.99 > truth.similarity(a1, b)
    # tastes the person model has no feature for are part of the truth
    assert {"art", "science", "shopping", "nightlife", "architecture"} <= set(a1.taste)
