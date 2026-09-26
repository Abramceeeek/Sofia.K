# Brain: the backend for v0 (D50, D51)

The Brain is the FastAPI backend. It holds the moment database, scores each moment for each person, and plans the day with OR-Tools. The SwiftUI app (the Face) calls it. The whole plan is in [`decisions/v0-ios-plan.md`](../decisions/v0-ios-plan.md).

**Status:** first draft, written 2026-09-26. The 49 tests pass on Python 3.12. Nothing is deployed. **It now also writes the Test B plans (D65), and holds the anonymous swipe page for choosing the 16 onboarding places (D70).** The app itself waits until Test B reports.

## Run it

```bash
cd brain
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest -q                       # 49 tests
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
| `data/swipe_items.yaml` | **The 16 Test A swipe items with DRAFT tags** (Claude's first draft; you confirm the places and the tags). Keyed by the Swipes tab's "Item #" |
| `data/testb/*.example.yaml` | Examples of the Test B brief, the generic plan and trip intent. Copy them to `validation/raw/testb/` (never committed) and edit |
| `data/conjoint_design.csv` | A copy of `validation/conjoint/design.csv`. A test fails if the two differ |
| `src/brain/moments.py` | The moment schema, and `missing_for_planning()`, which lists what a moment still needs |
| `src/brain/features.py` | The named x: tags scaled to 0–1, cost per £10, **transfer thresholds** (free up to 15 min, then hinges at 15–30 and 30+), **heat × outdoors** (28°C), rain × outdoors, heat × walking; the mapping from the "this or that" rows onto the same features |
| `src/brain/personal.py` | **δ_person**: a Laplace update over the three likelihood blocks (conjoint logit, swipe ordered logit, rating ordered logit) with fixed hyperparameters (Area 3). Numpy only and stateless, so it can move to the phone later (Area 17) |
| `src/brain/scoring.py` | `S = x · (b_pop + δ)`; the named terms behind each stop's score (input for the explanation); named weights with P(β<0), and "unsure" unless P > 0.8 or < 0.2 |
| `src/brain/planner.py` | An orienteering problem with time windows in OR-Tools. Prizes are utility above the 2|3 rating threshold, transfers cost the person's own transfer weights, and there is a stop limit. The **peak–end toggle is off by default** (D15). Travel runs from one moment's end to the next moment's start, so it is asymmetric |
| `src/brain/travel.py` | A straight-line walking estimate; `LondonEstimate` (walk up to 20 min, otherwise a rough Tube/bus time; every parameter is a GUESS); a hook for precomputed OSRM/TfL matrices |
| `src/brain/testb.py` | **Test B:** reads the results sheet, fits each person's weights from their swipes and choices, plans their day, and writes both blind plans (WhatsApp text and PDF) plus a review sheet for you |
| `src/brain/api.py` | 22 endpoints (below) |
| `src/brain/calibration.py`, `data/calibration/` | **The anonymous swipe page** (D70): a separate small app with its ~30 candidate places, the page, the results page and the ranking. Deployed by `../render.yaml` |

## Test B plans (D65, D68)

**Once per test,** copy the three example files to `validation/raw/testb/` and edit them:
- `brief.yaml`: the shared start, times, number of stops and budget;
- `generic.yaml`: your "top sights" plan, with the same number of stops, and `approach` and `what` for each stop;
- `intent.yaml` (optional): each person's must-do and mode.

**After each person's Test A chat**, fill in their rows on the Swipes and Choices tabs of `validation/raw/results.xlsx`, then:

```bash
cd brain
.venv/bin/python -m brain.testb weights --results ../validation/raw/results.xlsx --ids P07     # read-back lines
.venv/bin/python -m brain.testb plans --results ../validation/raw/results.xlsx --ids P07 \
    --brief ../validation/raw/testb/brief.yaml --generic ../validation/raw/testb/generic.yaml \
    --intent ../validation/raw/testb/intent.yaml --out ../validation/raw/testb/out
```

**For each person it writes:**
- `P07_plan_A.txt` and `P07_plan_B.txt`: WhatsApp-ready, labelled by the TestB tab;
- the matching PDFs;
- `P07_review.md`: for you only. It covers why each stop was chosen, strong moments left out, legs to check, and the read-back lines.

**How the plans are kept fair:**
- **The sent plans never give reasons**, which keeps the test blind.
- **The planner fills exactly the brief's number of stops** within the budget, and includes the must-do stop if it fits.
- It refuses to run until there are enough complete moments in `data/moments/`.

## Swipe calibration page (D70)

An anonymous, mobile-first page where strangers swipe ~30 candidate London places (Loved it / It was fine / Didn't enjoy it / Haven't been). The results pick the 16 most familiar-and-divisive places for the Test A swipe step and v0 onboarding.

**Privacy.** No login and no questions about the person. The browser makes a random ID (`crypto.randomUUID`) and keeps it in local storage. The server stores that ID, the answer and the **day only**. It never reads the client address, and uvicorn runs with `--no-access-log`. There are no cookies, analytics or third-party fonts. Each person can delete their answers from the end screen, and the page states the retention (by 31 March 2027, the same as the study data). Render's own edge logs are outside our code, and the page says so.

**How the 16 are picked.** Only people who answered at least 10 places count.
- **Familiarity** is the share who have been.
- **Divisiveness** is the variance of the reaction among those who have been (loved +1, fine 0, didn't enjoy −1). It runs from 0 to 1.
- **Score** is familiarity × divisiveness.
- A place with fewer than 5 visitors is ranked last.
- The results page also warns when a taste tag appears in fewer than 2 of the 16, and names the best place outside the set that has it. Whether to swap it in is your call.

**Deploy (about 0.5 h, £0).** The Artifact database can't take answers from anonymous public visitors (it is limited to signed-in members of your organisation), so the page runs on Render's free tier.
1. On render.com, sign in with GitHub, then choose **New → Blueprint** and pick this repo. Render reads `render.yaml`, which sets up a free web service and a free Postgres database in Frankfurt.
2. When asked for `CALIBRATION_CONTACT`, enter the email for questions. It shows in the privacy note.
3. Open the service URL (`https://london-places-swipe….onrender.com`), do the swipe yourself once, then share the link.
4. For results, open `<URL>/results` and paste `CALIBRATION_ADMIN_TOKEN` (the service's Environment tab). Download **all answers (CSV)** into `validation/raw/` (never committed) **before day 30**. The free database expires 30 days after it is created.
5. After picking the 16, suspend or delete the service and database in Render.

The free service sleeps after 15 minutes without visits. The first visitor after that waits about a minute.

**Keep it at £0:** don't add a payment method to Render. Without one, going over the free monthly bandwidth or build minutes suspends the service or its builds instead of billing you (render.com/docs/free, fetched 2026-09-26).

Run it locally: `CALIBRATION_ADMIN_TOKEN=change-me .venv/bin/uvicorn brain.calibration:app --app-dir src --reload`, then open http://127.0.0.1:8000.

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
| **Travel matrices:** walking (OSRM or openrouteservice) and transit (TfL), precomputed (Area 4). Until then, check every Tube/bus leg in a Test B plan by hand | 2 |
| **Weather:** Met Office DataHub. Plans currently take conditions in the request | 1 |
| **LLM explanation** from each stop's `why` | 1 |
| **LLM extraction** of the open answer, only for people who gave AI permission, plus the gold-set check (Area 1) | 3 |
| **Pooled refit** from Phase 3 data into `priors.yaml`. The full hierarchical refit comes after v0 | 1 |
| **Hosting** on Render with Postgres, secrets, migrations (Alembic) and backups | 2 |
| **The 50 moments** and ~20 shot cards: your content (Area 2). **About 25 are needed before Test B** (≈ 3.5 h, pulled into Phase 3, D65) | 5 |
