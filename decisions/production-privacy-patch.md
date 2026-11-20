# Production hotfixes for the live Brain (`80a0da3`): A1 to A4 (19–20 Nov 2026)

Abram's decisions of 19 Nov (§4, §5) and 20 Nov (§1, §2): prepare the smallest production fixes as isolated hotfixes. Each one must apply on its own to `80a0da3`, pass the frozen suite, have a reviewed diff and a rollback, and leave Test B as it is.

**Status: prepared and tested; nothing is deployed and nothing is on `main`.** Two things wait for Abram's explicit approval:
- the final patch set (all four, or which of them);
- the release procedure below.

## The four hotfixes

| | A1: the alert | A3: the logs | A2: stored plans | A4: storage warning |
|---|---|---|---|---|
| **Live today** | The webhook, if set, gets `Safety alert #N (user <first 8 of their id>): <the whole message> \| Reply to: <their phone or email>` | **(1)** The log line: `SAFETY ALERT N from user <full id>: <the whole message>`, whether or not a webhook is set.<br>**(2)** A failed database write logs the values it was writing. Shown on 20 Nov, with the frozen code on Postgres: a too-long consent version gave a 500, and its log line held the new person's id and token hash | A day from "where you are" keeps that point (lunch's map pin). A trip's days keep the stay's name ("Lunch near …", "… from …") | No warning before the database fills. Render has no storage alert for Postgres (below) |
| **After** | `Safety message #N is waiting`, and nothing else | **(1)** `SAFETY ALERT N received`.<br>**(2)** The engine runs with `hide_parameters=True`, so an error never shows a row | The stored copy has no pin for lunch at "where you are", and "your stay" for the stay's name. **The person's reply is their own full copy, as before** | The nightly job fails, so GitHub emails Abram, at 50% of the database's storage |
| **Files** | `notify.py` | `notify.py` (one line), `db.py` (one line) | `api.py` | `backup.py`, `api.py` (the backup route), `.github/workflows/ops.yml` |
| **Tests added** | 5 (`test_alert_minimal.py`) | 3 (`test_log_minimal.py`) | 4 (`test_stored_location.py`) | 3 (`test_storage_warning.py`) |
| **What a tester notices** | nothing | nothing | Only after a reinstall: a plan fetched again from the server shows "your stay" and no lunch pin at "where you are" | nothing |
| **Patch, sha256** | `A1-alert-minimal.patch`<br>`fefcf301…6b83a8` | `A3-log-minimal.patch`<br>`921d22d3…723fd1` | `A2-stored-location.patch`<br>`ebccefe2…7b130` | `A4-storage-warning.patch`<br>`84fe24d5…c5460` |
| **Commit in the bundle** | `99f6ad8` | `ac88946` | `add36ef` | `fa82016` |

The full sha256s are in "Release procedure", step 2.

**Changes since 19 Nov:**
- A1 now changes only the webhook, with the exact text Abram asked for. Its log change moved to A3, so each fix stands alone.
- A3 is new: the log line, and the failed-write values found on 20 Nov.
- A2 is unchanged in behaviour: only its comments now say "processed … not retained".
- A4 is new: the storage warning (`database-before-6-dec.md`, "Storage").

**What A3 does to the privacy notice.** The live notice says a Help & safety message "is also written to the logs, in case it can't reach a person any other way". After A3 that sentence says more than happens. That errs on the side of disclosure: it never hides a use. The message is committed to the database before the log line is written, so the database is where Abram reads it. The sentence is corrected in the next normal release (SEC-09 in full, Category B), not mid-round, because the notice is what participants agreed to.

## Processing versus retention

The wording to use from now on, in the docs and any notice:

| Information | Sent by the app to the Brain? | Used during the request | Retained after the request (after A2) |
|---|---|---|---|
| "Start from where I am" | **Yes**, once, rounded on the phone to about 100 m | to plan the day; the person's reply includes it (lunch's pin) | **No**: not in the stored plan. The request log never records a body (frozen `ops.py`) |
| The stay's name, in a trip | **Yes**, with the trip's request | to write "from …" and "Lunch near …" in the person's reply | **No**: stored as "your stay" |
| The stay's location | **Yes** | to plan from it | **Yes**, as the notice says ("its location, never its name") |
| A Help & safety message and contact | **Yes** | stored, and a person is told one is waiting | the message, as the notice says; the contact until resolved, 30 days at most. **Not** in the webhook (A1) or the log (A3) |

Never write "never sent" or "never transmitted" for the first two: the app sends them. Say "used to plan your day, and not kept after it".

## Evidence (20 Nov, on a clean checkout of `80a0da3`)

| Run | Result |
|---|---|
| `80a0da3` as it is | 202 passed |
| A1 alone / A2 alone / A3 alone / A4 alone | 207 / 206 / 205 / 205 passed: the 202 plus each patch's own |
| All four, in the order A1 A2 A3 A4, and in the reverse order | 217 passed both times |
| Each patch's new tests on the unpatched code | **fail** (2, 3, 3 and 2 of them), as they should: they test what the patch changes |
| The Test B pair for 10 fixed people, which stops each plan has, by kind (personal or generic) | `53cf41f5fde94582` on `80a0da3` and `53cf41f5fde94582` with all four: **identical**. Two runs on `80a0da3` also matched, so the pair is deterministic |

**What the patches don't touch:**
- no file under `brain/data/`, `testb.py`, the planner, scoring or `schemas.py`;
- no database model: no table or column is added or changed;
- nothing under `app/` or `android/`, so the iPhone and Android build workflows don't run (they trigger only on those folders).

**Re-run all of it:** `bash decisions/patches/check.sh` from the repository root, in a Python 3.12 environment with `brain/requirements-app.txt` and pytest. It uses a throwaway worktree, never `main`, a remote or a database. The Test B fingerprint is `decisions/patches/testb_same.py`.

## Release procedure (for Abram's approval; nothing here has been run on `main` or Render)

Commands for PowerShell, from Abram's clone. **The bundle carries the four commits byte-for-byte**, so Windows line endings can't alter them. The `.gitattributes` in `decisions/patches/` keeps the `.patch` files exact too.

1. **Get the reviewed commits.**
   ```powershell
   git fetch origin
   git switch claude/pensive-euler-fftd63
   git pull --ff-only
   git bundle verify decisions/patches/privacy-hotfix-80a0da3.bundle
   git fetch decisions/patches/privacy-hotfix-80a0da3.bundle privacy-hotfix:privacy-hotfix
   git log --oneline 80a0da3..privacy-hotfix
   ```
   **Expected:** `verify` ends "The bundle requires this ref: 80a0da3d117a…", and the log shows exactly:
   ```text
   fa82016 A4: a nightly warning at half the database's storage
   add36ef A2: "where you are" and the stay's name are processed to plan, not retained
   ac88946 A3: the log never holds a safety message, who sent it, or a failed write's values
   99f6ad8 A1: the safety alert says only "Safety message #N is waiting"
   ```
2. **Review the diff.**
   ```powershell
   git diff --stat 80a0da3 privacy-hotfix
   git diff 80a0da3 privacy-hotfix
   Get-FileHash decisions\patches\*.patch -Algorithm SHA256
   ```
   **Expected:** 9 files (5 changed, 4 new tests), about 87 lines added and 12 removed outside the tests. The hashes:
   ```text
   A1-alert-minimal.patch    FEFCF301A8B9A0C7CE61A637DC0C5E02323417F4AB6412D4BC7D1E02CD6B83A8
   A2-stored-location.patch  EBCCEFE23CFD75D454D63BB95C3FA676C2492621DB9EAB599936D1634F5B7130
   A3-log-minimal.patch      921D22D3DF412FD0B3CE4FAE5115C18FD75C6D05E25E4C580210A66C19723FD1
   A4-storage-warning.patch  84FE24D5C62646E5B0CC33BF07E5689E9F4F9E2B388588375651354BDEFC5460
   ```
3. **Choose the set.**
   - **All four:** use `privacy-hotfix` as it is.
   - **Fewer:** each applies alone, so start from `80a0da3` and pick:
     ```powershell
     git switch -c privacy-hotfix-subset 80a0da3
     git cherry-pick 99f6ad8 ac88946
     ```
     This example takes A1 and A3. The cherry-picked commits get new ids: review `git diff 80a0da3 privacy-hotfix-subset` again.
4. **Push it and open a pull request into `main`** (Abram; this session can push only its own branch):
   ```powershell
   git push origin privacy-hotfix
   ```
   - The PR's checks should show only the backend tests, with no iPhone or Android build.
   - Review the PR's "Files changed" against step 2.
5. **Merge, then deploy by hand.**
   - Merge with "Create a merge commit". This keeps the reviewed commit ids.
   - **A merge doesn't deploy.** `moments-brain` has had Auto-Deploy **Off** since 6 Nov (`validation/friends-round.md`, "What keeps it fixed"), so the round's code can't change by accident. Leave it Off.
   - Then: Render → `moments-brain` → Manual Deploy → "Deploy latest commit", and wait for "Deploy live".
   - Render's docs: deploying a specific commit from the dashboard "disables automatic deploys for the service" (render.com/docs/deploys, read 6 Nov). It's already off, so nothing else changes.
6. **Check it worked.**
   - **The Brain:** `https://moments-brain.onrender.com/v1/health` shows `"ok": true`, and `version` is the first 7 characters of the merge commit. Also run `git diff privacy-hotfix origin/main` (after a `git fetch`): it should print nothing.
   - **A1 and A3:** send one Help & safety message from Abram's own phone (code `REHEARSAL`).
     - The webhook, if set, shows only `Safety message #N is waiting`.
     - Render → moments-brain → Logs shows `SAFETY ALERT N received`.
     - Then resolve it.
   - **A2:** plan a day from "Start from where I am". The app shows lunch's pin as before. `python -m brain.storedplaces count` doesn't go up.
   - **A4:** GitHub → Actions → ops → Run workflow → `backup`. The step "Check the database's size" prints "The database is under 50% of its 1024 MB."
7. **Record it.** The manifest (`validation/friends-round.md`) gets one line: the privacy commit, "changes no question, plan or answer". **The tag `friends-round-1` stays on `80a0da3`.** The preflight's check 2 becomes "the live Brain reports the approved privacy commit".

**When to do it:** before the first invite, so every tester is under the same code. A Render deploy on the free plan restarts the server. It changes no data, and Test B is unaffected (Evidence).

## Rollback

| When | **Roll back if, after step 5:**<br>• `/v1/health` isn't ok;<br>• any 500 appears in the log for `/v1/me/plans`, `/v1/me/trips/days`, `/v1/me/testb/pair`, `/v1/me/safety` or `/v1/admin/backup`;<br>• the app can't make a plan or a pair |
|---|---|
| **Fastest** | Render → moments-brain → Deploys → the deploy of `80a0da3` → Rollback → "Rollback to this deploy". Render re-runs that deploy's build, so it takes about a minute, and `/v1/health` shows `80a0da3` again.<br>**What Render's docs say about it** (render.com/docs/rollbacks.md, read 20 Nov):<br>• "Triggering a rollback in the Render Dashboard automatically disables autodeploys for the service": already off here, so no change;<br>• the rollback uses that deploy's environment variables, and "When you next trigger a _standard_ deploy, Render uses the service's current configuration"; the compute plan is not reverted;<br>• a rollback works only while that deploy's build is kept ("a fixed number of recent build artifacts … based on your workspace plan"; how many isn't stated).<br>**Then revert `main`** (the next row), so `main` again matches what runs and the manifest; a later manual deploy would otherwise bring the hotfix back |
| **In git** | `git switch main` · `git pull` · `git revert -m 1 <merge commit>` · `git push origin main`, then Manual Deploy → "Deploy latest commit". `main` now has the same files as `80a0da3`, and `/v1/health` shows the revert's commit. **Check:** `git diff 80a0da3 origin/main` prints nothing. It also works when the old build is no longer kept |
| **Effect on data** | None needs undoing. No patch changes the schema. Plans stored meanwhile keep "your stay" and no "where you are" pin (more private, harmless). After a rollback, new plans keep the pin and name again. A4's step sees no header and warns instead of failing |

## Historical data: does anything need a separate controlled deletion?

| Where | What is there now | Needs a deletion step? | How |
|---|---|---|---|
| **Database: plans** | Plans made before A2 from "where you are" (a pin), or for a trip with a named stay (its name). **No invite has gone out yet**, so these can only be Abram's own and the rehearsal's plans | **Yes, if the count isn't 0** | `python -m brain.storedplaces count --database-url <External URL>` prints only counts (`plans N, here_pins N, stay_names N`). If either isn't 0, follow the steps below |
| **The nightly sealed backups** (GitHub, 30 days) | copies of those rows | No separate step | They age out within 30 days of the clean, as the notice says for anything deleted. Keep them until a post-clean backup has passed `python -m brain.backup preflight` |
| **Render's own backups** (after the upgrade: 3 days point-in-time, 7 days logical; `database-before-6-dec.md`) | from the upgrade on | No | age out within 7 days |
| **Render's logs** (7 days on Hobby, read 16 Nov) | safety messages with the person's full id; any failed write's values | No: they age out 7 days after A3 is deployed | Whether Render can delete single log lines: **UNVERIFIED** (not found in its docs) |
| **The alert channel** | if `BRAIN_ALERT_WEBHOOK_URL` was ever set: each alert's message and contact | **Yes**, by Abram | delete the copied alerts in the channel, and set its shortest retention (19 Nov, "For Abram to check now", step 3) |

**The clean, if the count isn't 0** (the same shape as `brain.foodfield`, approved on 20 Nov §5):
1. Make a fresh backup (ops → Run workflow → `backup`), and check it with `python -m brain.backup preflight`.
2. Run `count`, and note the two numbers.
3. Run `python -m brain.storedplaces clean --database-url <External URL> --confirm clean`. It runs as one transaction. It changes only the pin and the name, and commits only if both counts reach 0 (otherwise "ROLLED BACK", nothing changed).
4. Run `count` again: it should show `here_pins 0, stay_names 0`.
5. **After any restore** from a backup older than the clean, run `count` again, and `clean` if it isn't 0.

It never deletes a plan or a person, and never prints a place, name, point or user. Tested on 20 Nov:
- on rows the frozen code itself stored (a day from "where you are", a day from a station, a two-night trip);
- result: "where you are" lost its pin, the station kept its pin, and the stay's name was gone from the file;
- 4 unit tests (`brain/tests/test_storedplaces.py`).

## Category B: everything else on the development branch stays out of production during the round

| Change | Files | What a tester would notice | Why it waits |
|---|---|---|---|
| m275: no match words; the factor line | `reasons.py`, `dayplan.py`, `explain.py`, `triplength.py`, `discovery.py`, `quality.py`, `group.py`, `api.py` | the line under each stop's price; trip-length wording | product wording, not participant protection |
| m276: plans keep their predictions | `api.py` | nothing | new stored field; evaluation only |
| SEC-01/02/03: limits and validation | `ops.py`, `schemas.py` | a refusal for oversized or impossible requests (the apps never send them) | changes behaviour. **Re-raised by the storage question:** without them, a deliberate fill of the database is possible (`database-before-6-dec.md`, "Storage") |
| SEC-04: export robustness | `api.py` | nothing | only matters if a bad number arrives. **If the export fails during the round, this is the fix**, reviewed then |
| SEC-05: address header, check route | `ops.py`, `api.py` | nothing | needs the staging check first |
| SEC-07: API pages off | `api.py`, `config.py` | nothing | low risk; the admin token guards the routes anyway |
| SEC-08: backup route error | `api.py` | nothing | harmless; no rush |
| SEC-09 in full: the notice updated to match A1 and A3 | `privacy_app.html` | the privacy notice's text | the notice is what participants agreed to |
| SEC-10: deletion records survive a restore | `db.py`, `backup.py`, `api.py` | nothing | **only matters if a restore happens.** The in-place upgrade involves none |
| SEC-19: 20 searches a day per install | `trips.py`, `api.py` | a refusal after 20 searches in a day | behaviour |
| The apps (SEC-13/15/16) | `app/`, `android/` | a new build | the round's builds are frozen |

## Hours

**Claude:** 1.5 h (19 Nov) and 2.5 h (20 Nov: A1 reworked, A3, A4, the bundle, the evidence, `storedplaces`, this note). All done.

**Abram:**

| Step | Hours |
|---|---|
| Decide the set | 0.25 |
| Review the diff (steps 1–2) | 0.5 |
| Push, merge and check (steps 4–6) | 0.5 |
| `storedplaces count`, and the clean if needed | 0.25 |
