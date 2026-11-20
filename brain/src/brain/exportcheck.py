"""Abram, 19-20 Nov: an admin export checked on its own before the database moves. Counts and problems only, never a
value from a row. Used by `scripts/export_counts.py` and by `python -m brain.backup preflight`."""

from __future__ import annotations

PERSON_TABLES = ("swipes", "conjoint_choices", "answers", "plans", "ratings", "events", "safety_alerts",
                 "category_answers", "corrections", "day_feedback")


def counts(export: dict) -> dict[str, int]:
    """Rows per table (the export's lists; `cohorts` is a mapping, not a table)."""
    return {k: len(v) for k, v in sorted(export.items()) if isinstance(v, list)}


def problems(export: dict) -> list[str]:
    """Every row that names a person names one who exists, and every rating's plan exists (Abram, 20 Nov, 5)."""
    out = []
    users = {u.get("id") for u in export.get("users", [])}
    for table in PERSON_TABLES:
        orphans = sum(1 for row in export.get(table, []) if row.get("user_id") not in users)
        if orphans:
            out.append(f"{table}: {orphans} rows name a person who isn't in users")
    plans = {p.get("id") for p in export.get("plans", [])}
    lost = sum(1 for r in export.get("ratings", []) if r.get("plan_id") is not None and r["plan_id"] not in plans)
    if lost:
        out.append(f"ratings: {lost} rows name a plan that isn't in plans")
    if not export.get("users"):
        out.append("users: none (an empty export, or the wrong file)")
    return out
