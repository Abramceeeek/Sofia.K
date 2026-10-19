# Brain: the backend for v0 (D50, D51)

The Brain is the FastAPI backend. It holds the moment database, scores each moment for each person, and plans the day with OR-Tools. The SwiftUI app (the Face) calls it. The whole plan is in [`decisions/v0-ios-plan.md`](../decisions/v0-ios-plan.md).

**Status (28 Sep):** 92 tests pass on Python 3.12. Only the swipe page is deployed (Render free tier, 27 Sep). It writes the Test B plans (D65). **The app build has started (D107):** the app's `POST /v1/me/plans` now uses the same planning engine as Test B (`src/brain/dayplan.py`), with the familiar favourite on by default (D103), and the app's swipes use the 16 locked places.

## Run it

```bash
cd brain
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest -q                       # 92 tests
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
| `data/moments/*.yaml` | **The moment database source.** One file per moment, in the Area 2 schema. Seed moment 1 and **seed batch 1 (11 cards, D72)** are here as **drafts**. **Only `status: ready` cards go into real plans**; `testb plans --include-drafts` is a dry run. `kind: area` marks an area vibe (one a day, never the peak), and `variant_of` groups variants (at most one per plan) |
| `data/aspiration.yaml`, `src/brain/aspiration.py` | **Aspiration match (D77):** the Test A fields mapped onto moments (existing tags ≥ 2, or listed ids). `python -m brain.testb fields` flags fields with fewer than 2 ready moments |
| `data/priors.yaml` | **b_population and the prior on δ_person**, with named features and labels. All GUESS except the conjoint priors (`validation/conjoint/README.md`). Replace them with the pooled refit from Phase 3 data |
| `data/onboarding.yaml` | Onboarding copy served to the app (from the Test A script) |
| `data/swipe_items.yaml` | **The 16 swipe places, locked 28 Sep (D107)**, used by Test A and the app. Tags are Claude's draft. Keyed by the Swipes tab's "Item #"; `cards` links each place to its moment cards |
| `data/testb/*.example.yaml` | Examples of the Test B brief, the generic plan and trip intent. Copy them to `validation/raw/testb/` (never committed) and edit |
| `data/conjoint_design.csv` | A copy of `validation/conjoint/design.csv`. A test fails if the two differ |
| `src/brain/moments.py` | The moment schema, and `missing_for_planning()`, which lists what a moment still needs |
| `src/brain/features.py` | The named x: tags scaled to 0–1, cost per £10, **transfer thresholds** (free up to 15 min, then hinges at 15–30 and 30+), **heat × outdoors** (28°C), **cold × outdoors** (8°C or below, D95), rain × outdoors, heat × walking; the mapping from the "this or that" rows onto the same features |
| `src/brain/personal.py` | **δ_person**: a Laplace update over the three likelihood blocks (conjoint logit, swipe ordered logit, rating ordered logit) with fixed hyperparameters (Area 3). Numpy only and stateless, so it can move to the phone later (Area 17) |
| `src/brain/scoring.py` | `S = x · (b_pop + δ)`; the named terms behind each stop's score (input for the explanation); named weights with P(β<0), and "unsure" unless P > 0.8 or < 0.2 |
| `src/brain/planner.py` | An orienteering problem with time windows in OR-Tools. Prizes are utility above the 2|3 rating threshold, transfers cost the person's own transfer weights, and there is a stop limit. The **peak–end toggle is off by default** (D15). Travel runs from one moment's end to the next moment's start, so it is asymmetric |
| `src/brain/travel.py` | A straight-line walking estimate; `LondonEstimate` (walk up to 20 min, otherwise a rough Tube/bus time; every parameter is a GUESS) |
| `src/brain/tfl.py` | **Stage 1: TfL's journey times.** A table of every card-to-card leg beyond a walk (and from Charing Cross), filled in the background at start and refreshed every 14 days; the chosen Tube and bus legs are checked again for the plan's own date. Stops name the lines ("Jubilee line to London Bridge"). Without a key, the estimate, as before |
| `src/brain/weather.py` | **Stage 1: the Met Office forecast** for central London, cached (an hour, or three for the daily one). Fills a plan's temperature and chance of rain when the app sends none, and is saved with ratings. Not used for the Test B pair, which stays as designed |
| `src/brain/ops.py` | **Stage 1:** the request log (route pattern, status, time; never an address, token or answer), error alerts to a person (rate-limited), and rate limits per phone and overall |
| `src/brain/backup.py` | **Stage 1: the nightly backup**, sealed to Abram's public key on the server; commands to make the keys, open a backup and restore it |
| `src/brain/dayplan.py` | **The day planner** shared by Test B and the app (D107): lunch, buffers, pace, the familiar favourite, disliked places, rain swaps, sunset-aware "Best" lines and the participant-facing wording |
| `src/brain/sun.py` | Sunset for a date (NOAA equations), so the app's plans get sunset lines offline; checked against sunrise-sunset.org |
| `src/brain/testb.py` | **Test B:** reads the results sheet, fits each person's weights from their swipes and choices, plans their day with `dayplan`, and writes both blind plans (WhatsApp text and PDF) plus a review sheet for you |
| `src/brain/api.py` | 22 endpoints (below) |
| `src/brain/calibration.py`, `data/calibration/` | **The anonymous swipe page** (D70): a separate small app with its ~30 candidate places, the page, the results page and the ranking. Deployed by `../render.yaml` |

## Test B plans (D65, D68)

**Once per test,** copy the three example files to `validation/raw/testb/` and edit them:
- `brief.yaml`: the shared start, times, number of stops and budget. An optional `weekday: sat` (mon..sun) leaves out cards closed that day (`best_time.days`, e.g. weekday-only museums);
- `generic.yaml`: your strong "best of London" plan (D100), with the same number of stops, and for each stop `approach`, `what`, `arrive` and `depart` (the last `depart` sets the pair's end time, D97). Optional per stop: `best` with a `best_window` (shown only then), `cost_kind` (food / entry / ticket / hire) and a `rain_swap` for outdoor stops. The first stop's `from` should match the brief's start;
- `intent.yaml` (optional): each person's must-do and mode.

**After each person's Test A chat**, fill in their rows on the Swipes and Choices tabs of `validation/raw/results.xlsx`, then:

```bash
cd brain
.venv/bin/python -m brain.testb weights --results ../validation/raw/results.xlsx --ids P07     # read-back lines
.venv/bin/python -m brain.testb plans --results ../validation/raw/results.xlsx --ids P07 \
    --brief ../validation/raw/testb/brief.yaml --generic ../validation/raw/testb/generic.yaml \
    --intent ../validation/raw/testb/intent.yaml --out ../validation/raw/testb/out --numbered
# no --familiar for the real Test B (D103)
```

**For each person it writes:**
- `P07_plan_1.txt` and `P07_plan_2.txt` with `--numbered` (D97), or `_A`/`_B` without it: WhatsApp-ready, labelled by the TestB tab (A → 1, B → 2);
- the matching PDFs;
- `P07_review.md`: for you only. It covers why each stop was chosen, strong moments left out, legs to check, and the read-back lines.

**How the plans are kept fair:**
- **The sent plans never give reasons**, which keeps the test blind.
- **The planner fills exactly the brief's number of stops** within the budget, and includes the must-do stop if it fits.
- **The plan text follows the dry-run fixes (D100):**
  - each stop shows arrive–leave;
  - costs read "about £X for food and entry, plus about £Y transport" (£3 a Tube or bus leg, capped at £8.90);
  - "Best: …" appears only when the stop's time matches the card's `best_window`;
  - outdoor stops get an "If it rains: …" swap;
  - there are 5 min of slack after each walk and 10 after each Tube or bus leg.
- **Places they didn't enjoy are never planned (D100).** Swipe places link to their cards in `data/swipe_items.yaml` (`cards`).
- **Round-2 fixes (D102):**
  - one of the brief's stops is lunch when the day spans midday: a food card the person likes, or a flexible "Lunch near X" slot (`lunch_gbp`, default £15);
  - rain swaps respect the person's weights;
  - a relaxed person gets longer stays where the day has room;
  - Tube or bus legs read "walk to [station], then take the Tube or bus to [station]";
  - titles name the place, and busy food stops add queue time.
  - Card fields: `end_station`, `queue_min`, `plan_title`.
  - Generic fields: `lunch: true`, `queue_min`.
- **`--familiar` (D100): off for the real Test B (D103)**, so it measures prediction rather than memory; **on by default in the v0 app.** With it, the personal plan holds exactly one place the person loved, if one fits the day. Either way, the review says for each loved place why it is in the plan or not.
- **Overlap across participants (D104):** each run saves `<ID>_personal.json` (stop ids and a normalised weight vector, no answers) and writes `overlap.md`: shared stops for every pair, stops in more than half the plans, and a warning when two dissimilar people share more than half their stops. `python -m brain.testb overlap --out DIR` re-runs it.
- **Test B exclusions and sunset (D105):** cards with `in_test_b: false` are left out of Test B (the run lists them); the brief's `sunset` ("hh:mm", for the Saturday the plans are for) sets the sunset-based "Best" lines through each card's `best_around_sunset`.
- **Meal cards (D104):** a card with `meal: lunch` is only ever the day's lunch stop; a flexible lunch slot is also offered at the start point.
- **Both plans in a pair end within 30 min of each other (D97).** The personal plan is first planned to finish by the generic end + 30 min; then its stops move later inside their opening windows until it ends no earlier than the generic end − 30 min. If that can't be done, the status says "fix by hand", and the review shows both end times.
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
5. After the final download, suspend or delete the service and database in Render.

**Live since 2026-09-27** (deployed by Abram from branch `claude/vigilant-cannon-my82dj`; Frankfurt; no card). **Final download by Fri 23 Oct**: the database expires about 26 Oct.

The free service sleeps after 15 minutes without visits. The first visitor after that waits about a minute.

**Keep it at £0:** don't add a payment method to Render. Without one, going over the free monthly bandwidth or build minutes suspends the service or its builds instead of billing you (render.com/docs/free, fetched 2026-09-26).

Run it locally: `CALIBRATION_ADMIN_TOKEN=change-me .venv/bin/uvicorn brain.calibration:app --app-dir src --reload`, then open http://127.0.0.1:8000.

## The API

| For | Endpoints |
|---|---|
| The app | `POST /v1/installs` (no login: consent plus an optional tester code, returns a token) · `GET /v1/onboarding` · `POST /v1/me/swipes` · `/conjoint` · `/answers` · `PUT /v1/me/profile` · `GET /v1/me/weights` · `GET /v1/moments` · `POST /v1/me/plans` · `GET /v1/me/plans` · `POST /v1/me/plans/{id}/feedback` · `POST /v1/me/ratings` (refits δ) · `POST /v1/me/events` · `POST /v1/me/safety` · `DELETE /v1/me` |
| Abram | `POST /v1/admin/moments/reload` (reports drafts and what they're missing) · `POST /v1/admin/users/{id}/plans` (a curated plan for Test B, Wizard of Oz) · `GET /v1/admin/safety` and `POST /v1/admin/safety/{id}/reply` (a reply the person sees in the app, D118; tracks the "within a few hours" target, D46) · `GET /v1/admin/export` (the Phase 3 data, with no tokens) · `GET /v1/admin/backup` (Stage 1: the sealed backup; the backup token or the admin token) |

**Answering a Help & safety message (D118).** The alert reaches you through the webhook (with the phone or email, if the person left one), and `GET /v1/admin/safety` lists those still waiting. Reply by phone or email if there's a contact, and always in the app too, so the person sees it under Help & safety. Run these in Terminal, with the admin token in an environment variable (never paste it anywhere else):

```bash
export B=https://moments-brain.onrender.com
export T=...   # the BRAIN_ADMIN_TOKEN value from Render → Environment
curl -s -H "Authorization: Bearer $T" $B/v1/admin/safety                       # waiting for a first reply
curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
     -d '{"replied_by": "abram", "text": "Hi, it'"'"'s Abram. Are you somewhere safe?"}' $B/v1/admin/safety/12/reply
curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
     -d '{"replied_by": "abram", "resolved": true}' $B/v1/admin/safety/12/reply  # sorted: deletes their contact
curl -s -H "Authorization: Bearer $T" "$B/v1/admin/safety?all=true"             # every message, with replies
```

A contact is deleted when you mark the message resolved, and at the latest after 30 days. The first reply is timed against the "within a few hours" target (D46).

## Stage 1 keys, alerts and backups

**Keys in Render** (Dashboard → moments-brain → Environment). Never in Git or a chat. `GET /v1/health` says whether each was found, never the value:

| What | Variable (other spellings also read) | `/v1/health` shows |
|---|---|---|
| TfL journey times | `TFL_APP_KEY` (`TFL_API_KEY`, `TFL_KEY`, `TFL_PRIMARY_KEY`) | `"travel": "tfl"` (or `"tfl 2070/2077"`: TfL found no journey for a few pairs, which keep the estimate); `"tfl_filling 120/2077"` while the table fills (10 to 15 minutes after the first deploy, at 200 calls a minute; later deploys only refresh what's over 14 days old); `"tfl_error"` = found, but TfL refused the first 20 calls; `"estimate"` = not found |
| Met Office forecast | `MET_OFFICE_API_KEY` (`MET_OFFICE_KEY`, `METOFFICE_API_KEY`, `MET_API_KEY`, `MET_OFFICE_DATAHUB_KEY`) | `"weather": "met_office"`; `"met_office_error"` = found, but the last call failed; `"off"` = not found |
| Error alerts (optional) | `BRAIN_OPS_WEBHOOK_URL` | — (unset: errors go to `BRAIN_ALERT_WEBHOOK_URL`, marked "not a safety alert") |
| Nightly backup | `BRAIN_BACKUP_PUBLIC_KEY`, `BRAIN_BACKUP_TOKEN` | — |

**Uptime and backups** run in GitHub Actions (`.github/workflows/ops.yml`): an hourly `GET /v1/health`, and at 02:23 UTC the sealed backup, kept as a workflow artifact for 30 days. If the Brain doesn't answer, the run fails and GitHub emails whoever added the workflow; with the `BRAIN_OPS_WEBHOOK_URL` GitHub secret, a message also goes there. Run either now from GitHub → Actions → ops → Run workflow.

**Setting up the backup (Abram, ~15 min, once):**

```bash
cd brain && pip install cryptography
python -m brain.backup keygen            # writes odys-backup-private.key; prints a public key and a token
```

1. Put the private key in your password manager as well. Without it no backup can be opened; never put it in Git, a chat or Render.
2. In Render, add `BRAIN_BACKUP_PUBLIC_KEY` (the public key) and `BRAIN_BACKUP_TOKEN` (the token).
3. In GitHub → Settings → Secrets and variables → Actions, add `BRAIN_BACKUP_TOKEN` (the same token).
4. Run the ops workflow with "backup" once: the run should keep a file named `odys-brain-YYYYMMDD.odysbk`.

**Opening and restoring one:** download the artifact from the run, then `python -m brain.backup open odys-brain-20261020.odysbk --key odys-backup-private.key > backup.json`. To restore into a new, empty database: `python -m brain.backup restore backup.json --database-url postgresql://…`. The cards and TfL's times rebuild themselves at start. Contacts left with a safety message are never in a backup (D118).

**Rate limits** (GUESSES, in `ops.py`): 10 new installs an hour from one address and 300 from everyone; 30 plans per phone in 10 minutes; 10 trip plans per phone in 10 minutes; 180 other requests per phone a minute; 60 a minute from an address without a token. Provider searches: 40 per phone an hour (as before), and 400 a day from everyone. Above a limit the app says "That's a lot in a short time. Please wait a minute, then try again." The request log shows each 429 with its kind of limit, so the limits can be checked in the friends' round.

**Guardrails in the code:**
- **No audio** is ever stored.
- **No nationality, health or allergy fields** exist.
- **AI permission** is stored separately (`consent_ai`, App Review 5.1.2(i)).
- **Delete my data** removes every row for that install.
- **Safety alerts** are saved first and sent to a person, and the user is told to call 999 and that a person will reply within a few hours.

## Not built yet (founder hours in the plan)

| Item | Hours |
|---|---|
| **Walking matrix** (OSRM or openrouteservice), for walks along streets rather than straight lines (Area 4). TfL's transit times are in (Stage 1, `tfl.py`); the Test B pair still uses the estimate, so check its Tube/bus legs by hand | 2 |
| **LLM explanation** from each stop's `why` | 1 |
| **LLM extraction** of the open answer, only for people who gave AI permission, plus the gold-set check (Area 1) | 3 |
| **Pooled refit** from Phase 3 data into `priors.yaml`. The full hierarchical refit comes after v0 | 1 |
| **Migrations** (Alembic). Hosting, secrets and backups are in (Stage 1) | 2 |
| **The 50 moments** and ~20 shot cards: your content (Area 2). **About 25 are needed before Test B** (≈ 3.5 h, pulled into Phase 3, D65) | 5 |
