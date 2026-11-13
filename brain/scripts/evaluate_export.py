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

from brain.config import DATA_DIR  # noqa: E402
from brain.evaluation import DayOutcome, Outcome, evaluate, predictions_from_plans  # noqa: E402
from brain.population import load_population  # noqa: E402

MIN_FOR_PATTERNS = 30          # GUESS: fewer rated stops and the read-out says "exploratory only"


def read_out(export: dict) -> list[str]:
    pop = load_population(DATA_DIR / "priors.yaml")
    visitors = {u for u, c in (export.get("cohorts") or {}).items() if c == "visitor"}
    plans = [p for p in export.get("plans", []) if p.get("user_id") not in visitors]
    preds = predictions_from_plans(plans, pop.scales["rating"], pop.cutpoints["rating"][1])
    outs = [Outcome(r["plan_id"], r["moment_id"], r["rating"], r.get("would_bring"))
            for r in export.get("ratings", []) if r.get("plan_id") is not None and r.get("user_id") not in visitors]
    days = [DayOutcome(d["plan_id"], d.get("worth"), d.get("again"))
            for d in export.get("day_feedback", []) if d.get("user_id") not in visitors]
    r = evaluate(preds, outs, days, synthetic=False)
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
