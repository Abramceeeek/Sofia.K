# Brain: the backend for v0 (D50, D51)

The Brain is the FastAPI backend. It holds the moment database, scores each moment for each person, and plans the day with OR-Tools. The SwiftUI app (the Face) calls it. The whole plan is in [`decisions/v0-ios-plan.md`](../decisions/v0-ios-plan.md).

**Status:** first draft, written 2026-09-26. The 28 tests pass on Python 3.12. Nothing is deployed.

## Run it

```bash
cd brain
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest -q                       # 28 tests
BRAIN_ADMIN_TOKEN=change-me .venv/bin/uvicorn brain.api:app --app-dir src --reload
# API docs: http://127.0.0.1:8000/docs
```

**Settings** (environment variables):

| Variable | What it is | Default |
|---|---|---|
| `BRAIN_DATABASE_URL` | Database | `sqlite:///./brain.db`; use Postgres in production |
| `BRAIN_ADMIN_TOKEN` | Enables the admin endpoints | unset, so admin is off |
| `BRAIN_ALERT_WEBHOOK_URL` | Where safety alerts are posted: a channel you and the backup helper both watch | unset |
| `BRAIN_PLANNER_TIME_LIMIT_S` | Planner search time | 1.0 |

## What's where

| File | What it does |
|---|---|
| `data/moments/*.yaml` | **The moment database source.** One file per moment, in the Area 2 schema. Seed moment 1 is here as a **draft**: its gaps are `null`, and the planner skips it until they're filled |
| `data/priors.yaml` | **b_population and the prior on δ_person**, with named features and labels. All GUESS except the conjoint priors (`validation/conjoint/README.md`). Replace them with the pooled refit from Phase 3 data |
| `data/onboarding.yaml` | Onboarding copy served to the app (from the Test A script) |
| `data/conjoint_design.csv` | A copy of `validation/conjoint/design.csv`. A test fails if the two differ |
| `src/brain/moments.py` | The moment schema, and `missing_for_planning()`, which lists what a moment still needs |
| `src/brain/features.py` | The named x: tags scaled to 0–1, cost per £10, **transfer thresholds** (free up to 15 min, then hinges at 15–30 and 30+), **heat × outdoors** (28°C), rain × outdoors, heat × walking; the mapping from the "this or that" rows onto the same features |
| `src/brain/personal.py` | **δ_person**: a Laplace update over the three likelihood blocks (conjoint logit, swipe ordered logit, rating ordered logit) with fixed hyperparameters (Area 3). Numpy only and stateless, so it can move to the phone later (Area 17) |
| `src/brain/scoring.py` | `S = x · (b_pop + δ)`; the named terms behind each stop's score (input for the explanation); named weights with P(β<0), and "unsure" unless P > 0.8 or < 0.2 |
| `src/brain/planner.py` | An orienteering problem with time windows in OR-Tools. Prizes are utility above the 2|3 rating threshold, transfers cost the person's own transfer weights, and there is a stop limit. The **peak–end toggle is off by default** (D15). Travel runs from one moment's end to the next moment's start, so it is asymmetric |
| `src/brain/travel.py` | A straight-line walking estimate (a placeholder), and a hook for precomputed OSRM/TfL matrices |
| `src/brain/api.py` | 22 endpoints (below) |

## The API

| For | Endpoints |
|---|---|
| The app | `POST /v1/installs` (no login: consent plus an optional tester code, returns a token) · `GET /v1/onboarding` · `POST /v1/me/swipes` · `/conjoint` · `/answers` · `PUT /v1/me/profile` · `GET /v1/me/weights` · `GET /v1/moments` · `POST /v1/me/plans` · `GET /v1/me/plans` · `POST /v1/me/plans/{id}/feedback` · `POST /v1/me/ratings` (refits δ) · `POST /v1/me/events` · `POST /v1/me/safety` · `DELETE /v1/me` |
| Abram | `POST /v1/admin/moments/reload` (reports drafts and what they're missing) · `POST /v1/admin/users/{id}/plans` (a curated plan for Test B, Wizard of Oz) · `GET /v1/admin/safety` and `POST /v1/admin/safety/{id}/reply` (tracks the "within a few hours" target, D46) · `GET /v1/admin/export` (the Phase 3 data, with no tokens) |

**Guardrails in the code:**
- **No audio** is ever stored.
- **No nationality, health or allergy fields** exist.
- **AI permission** is stored separately (`consent_ai`, App Review 5.1.2(i)).
- **Delete my data** removes every row for that install.
- **Safety alerts** are saved first and sent to a person, and the user is told to call 999 and that a person will reply within a few hours.

## Not built yet (founder hours in the plan)

| Item | Hours |
|---|---|
| **Travel matrices:** walking (OSRM or openrouteservice) and transit (TfL), precomputed (Area 4) | 2 |
| **Weather:** Met Office DataHub. Plans currently take conditions in the request | 1 |
| **LLM explanation** from each stop's `why` | 1 |
| **LLM extraction** of the open answer, only for people who gave AI permission, plus the gold-set check (Area 1) | 3 |
| **Pooled refit** from Phase 3 data into `priors.yaml`. The full hierarchical refit comes after v0 | 1 |
| **Hosting** on Render with Postgres, secrets, migrations (Alembic) and backups | 2 |
| **The 50 moments** and ~20 shot cards: your content (Area 2) | 5 |
