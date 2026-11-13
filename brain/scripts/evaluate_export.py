"""m264 (Abram, m260): compare ODYS's predictions with what people reported, from an admin export. Read-only; collects
nothing new; separate from the Test B read-out (testb_report.py), which stays the round's own analysis.

    .venv/bin/python scripts/evaluate_export.py ../validation/raw/export-<date>.json --code FRIENDS --since <start>

It pairs each 1-5 rating with the prediction stored with that stop of that plan (`predicted`, the model's utility),
then reports calibration, discrimination and the match words (evaluation.py), the day-level "again" and "worth", and
how many planned stops were rated. Visitors from abroad are left out, as in Test B (D116). The raw export stays in
validation/raw/ (git-ignored) and is never committed; only this read-out's text is shared.

With a handful of testers this is exploratory: it says what to look at, not what is true. The read-out says so.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
spec = importlib.util.spec_from_file_location("testb_report", HERE / "testb_report.py")
tb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tb)

from datetime import date  # noqa: E402

from brain.catalogue import load_catalogue  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402
from brain.evaluation import DayOutcome, Outcome, evaluate, predictions_from_plans  # noqa: E402
from brain.population import load_population  # noqa: E402
from brain.quality import uncertainties  # noqa: E402

MIN_FOR_PATTERNS = 30          # GUESS: fewer rated stops and the read-out says "exploratory only"
MATERIAL = 0.05                # GUESS: a risk this size or more is an open question (an unnamed area, 0.01, isn't)


def open_questions(plans: list[dict]) -> dict[tuple[int, str], tuple[str, ...]]:
    """m268: each planned stop's material open questions (hours, price, season, age…) for its plan's own day, from the
    catalogue as it is now (facts checked since the plan count as known). Build 91's plans store the old moment ids,
    which each catalogue entry keeps as legacy ids."""
    by_id = {i: x for x in load_catalogue() for i in (x.id, *x.legacy_ids)}
    out = {}
    for p in plans:
        when = p.get("date") or (p.get("created_at") or "")[:10]
        if not when:
            continue
        day = date.fromisoformat(when)
        for s in p.get("stops") or []:
            x = by_id.get(s.get("moment_id"))
            if x is not None:
                out[(p["id"], s["moment_id"])] = tuple(sorted(
                    {r.field for r in uncertainties(x, today=day, day=day) if r.p >= MATERIAL}))
    return out


def read_out(export: dict) -> list[str]:
    pop = load_population(DATA_DIR / "priors.yaml")
    visitors = {u for u, c in (export.get("cohorts") or {}).items() if c == "visitor"}
    plans = [p for p in export.get("plans", []) if p.get("user_id") not in visitors]
    preds = predictions_from_plans(plans, pop.scales["rating"], pop.cutpoints["rating"][1])
    outs = [Outcome(r["plan_id"], r["moment_id"], r["rating"], r.get("would_bring"))
            for r in export.get("ratings", []) if r.get("plan_id") is not None and r.get("user_id") not in visitors]
    days = [DayOutcome(d["plan_id"], d.get("worth"), d.get("again"))
            for d in export.get("day_feedback", []) if d.get("user_id") not in visitors]
    r = evaluate(preds, outs, days, synthetic=False, open_questions=open_questions(plans))
    lines = [f"Predictions against what people reported ({r['label']}).",
             f"Planned stops with a prediction: {r['planned_stops']}; rated: {r['rated']}"
             + (f" ({r['rated_share']:.0%})" if r["rated_share"] is not None else "") + "."]
    if r["rated"] < MIN_FOR_PATTERNS:
        lines.append(f"Exploratory only: {r['rated']} rated stops is too few for conclusions (fewer than "
                     f"{MIN_FOR_PATTERNS}). Read each one, not the averages.")
    if "brier" in r:
        lines += [f"Observed Good or better: {r['observed_good']:.0%}; mean prediction: {r['mean_predicted']:.0%}.",
                  f"Brier score {r['brier']} against {r['base_rate_brier']} for always predicting the average "
                  "(lower is better).",
                  f"Discrimination (AUC): {r['auc'] if r['auc'] is not None else 'needs both Good and not-Good ratings'}."]
        lines += [f"  predicted {b['band']}: {b['n']} stops, observed Good {b['observed']:.0%}" for b in r["calibration"]]
        lines += [f"  \"{w}\": {v['n']} stops, observed Good {v['observed_good']:.0%}" for w, v in r["match_words"].items()]
        if r.get("would_bring") is not None:
            lines.append(f"Would bring someone: {r['would_bring']:.0%}.")
        oq = r.get("open_questions")
        if oq:
            pct = lambda g: "-" if g["observed_good"] is None else f"{g['observed_good']:.0%}"
            lines.append("Stops whose facts had a material open question on their day (the catalogue as it is now; "
                         "build 91 didn't rank by them): "
                         f"{oq['some']['n']} rated, observed Good {pct(oq['some'])}; with none: {oq['none']['n']}, "
                         f"{pct(oq['none'])}" + (f"; not in the catalogue: {oq['not_in_catalogue']}" if
                                                 oq["not_in_catalogue"] else "") + ".")
            lines += [f"  open {f}: {g['n']} stops, observed Good {pct(g)}" for f, g in oq["by_fact"].items()]
    if r.get("day_again") is not None:
        lines.append(f"Would do the day again: {r['day_again']:.0%}; worth what they spent: {r.get('day_worth')}.")
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
