"""Abram, 12 Nov (part 3B): does ODYS learn about a real person? Read-only, from an admin export; collects nothing new.

    .venv/bin/python scripts/learning_milestones.py ../validation/raw/export-<date>.json --code FRIENDS --since <start>

Each rated stop is judged by the prediction its plan was made with (kept with the stored plan since m276), grouped by
how much the person had told us by then: after onboarding, after the first rating, after 2 days out, after 5 days
out, after 20 ratings (evaluation.milestone). Beside it, the baseline: what the model says knowing nothing about them
(the population's weights alone, for the same card, conditions and interests). Learning shows as the personal
prediction beating the baseline by more at each later milestone (`gain` above 0, growing).

What it never does: impute a rating, use simulated people in place of real ones, or claim anything from a row with
fewer than 30 rated stops (it says "exploratory"). Visitors from abroad are left out (D116). The raw export stays in
validation/raw/ (git-ignored); only this read-out's text is shared. Plans made before m276 kept no prediction, so
their ratings are counted apart (evaluate_export.py checks them by the words they showed).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("testb_report", HERE / "testb_report.py")
tb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tb)

from brain.aspiration import NONE, load_aspiration  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.evaluation import (MIN_PER_MILESTONE, Outcome, PlanMade, learning_by_milestone, p_from_utility,  # noqa: E402
                              predictions_from_plans)
from brain.features import Conditions, moment_features  # noqa: E402
from brain.moments import load_moments  # noqa: E402
from brain.population import load_population  # noqa: E402


def baseline(plans: list[dict], users: dict[str, dict]) -> dict[tuple[int, str], float]:
    """The chance of Good from the population's weights alone (δ = 0), as dayplan computes `predicted`: the same card,
    the plan's own weather when it kept one, and the person's interests. A card no longer in the data has none."""
    pop = load_population(DATA_DIR / "priors.yaml")
    b0 = pop.b_person(np.zeros(len(pop.personal_names)))
    cards = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    asp = DATA_DIR / "aspiration.yaml"
    amap = load_aspiration(asp) if asp.exists() else None
    scale, cut = pop.scales["rating"], pop.cutpoints["rating"][1]
    out = {}
    for p in plans:
        w = (p.get("intent") or {}).get("weather") or {}
        cond = Conditions(w.get("temp_c"), w.get("rain_prob"))
        fields = frozenset(f for f in ((users.get(p.get("user_id")) or {}).get("profile") or {}).get("fields", [])
                           if f != NONE)
        for s in p.get("stops") or []:
            m = cards.get(str(s.get("moment_id", "")).split("#")[0])
            if m is None or s.get("predicted") is None:
                continue
            a = amap.match(m, fields) if amap else 0.0
            u = float(pop.vector(moment_features(m, cond, aspiration_match=a)) @ b0)
            out[(p["id"], s["moment_id"])] = p_from_utility(u, scale, cut)
    return out


def read_out(export: dict) -> list[str]:
    pop = load_population(DATA_DIR / "priors.yaml")
    visitors = {u for u, c in (export.get("cohorts") or {}).items() if c == "visitor"}
    plans = [p for p in export.get("plans", []) if p.get("user_id") not in visitors and p.get("kind") == "personal"]
    users = {u["id"]: u for u in export.get("users", [])}
    preds = predictions_from_plans(plans, pop.scales["rating"], pop.cutpoints["rating"][1])
    ratings = [r for r in export.get("ratings", []) if r.get("user_id") not in visitors]
    outs = [Outcome(r["plan_id"], r["moment_id"], r["rating"]) for r in ratings if r.get("plan_id") is not None]
    made = {p["id"]: PlanMade(p["user_id"], p["created_at"]) for p in plans if p.get("created_at")}
    rated_at: dict[str, list[str]] = {}
    for r in ratings:
        if r.get("created_at"):
            rated_at.setdefault(r["user_id"], []).append(r["created_at"])
    r = learning_by_milestone(preds, outs, made, rated_at, baseline(plans, users), synthetic=False)
    lines = [f"Learning by milestone ({r['label']}): each rated stop against the prediction its plan was made with, "
             "and against the population's weights alone (the baseline). Brier score: lower is better; gain = "
             "baseline minus personal, above 0 when the person's answers helped.",
             f"Rows with fewer than {MIN_PER_MILESTONE} rated stops are exploratory: read each one, not the averages."]
    for row in r["rows"]:
        if not row["n"]:
            lines.append(f"  {row['milestone']}: no rated stops yet.")
            continue
        tag = " (exploratory)" if row["exploratory"] else ""
        base = (f"; baseline {row['brier_baseline']}, gain {row['gain']:+.4f}" if "gain" in row else "; no baseline")
        lines.append(f"  {row['milestone']}{tag}: {row['n']} rated stops from {row['people']} people; observed Good "
                     f"{row['observed_good']:.0%}, mean predicted {row['mean_predicted']:.0%}; Brier {row['brier']}"
                     f"{base}; AUC {row['auc'] if row['auc'] is not None else 'n/a'}.")
    if r["rated_without_prediction"]:
        lines.append(f"Rated stops whose plan kept no prediction (made before m276): {r['rated_without_prediction']}. "
                     "They can't be placed here; evaluate_export.py checks them by the words they showed.")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", type=Path)
    ap.add_argument("--code")
    ap.add_argument("--since")
    a = ap.parse_args()
    export, said = tb.only(json.loads(a.export.read_text(encoding="utf-8")), a.code, a.since)
    print("\n".join(said + read_out(export)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
