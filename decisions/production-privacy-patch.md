# The live Brain's privacy gaps, and the smallest safe fixes (19 Nov 2026)

Abram's decisions of 19 Nov, §4 and §5: check the alert webhook now, separate urgent privacy fixes (Category A) from product changes (Category B), and present the smallest safe production fix separately for approval.

**Nothing has been deployed or merged into `main`.** The two patches below are files in `decisions/patches/`, made and tested against the frozen code `80a0da3`.

## What the live Brain (`80a0da3`) does today, read from its code

When someone sends a Help & safety message (`POST /v1/me/safety`, `brain/src/brain/api.py:801-812`, `notify.py`):

| Where it goes | What it holds | Promised by the live privacy notice? |
|---|---|---|
| The database | the message; the contact in its own table, deleted when resolved or after 30 days | yes |
| **The alert webhook, if `BRAIN_ALERT_WEBHOOK_URL` is set** | `Safety alert #N (user <first 8 characters of their id>): <the whole message> \| Reply to: <their phone or email>` | **No.** The notice names Render as the only host, and its "deleted … after 30 days at the latest" can't reach a copy held in a chat service |
| The server's log (Render keeps logs 7 days on the Hobby plan, read 16 Nov) | `SAFETY ALERT N from user <their full id>: <the whole message>` | in part: the notice says the message is logged and the contact never is. It doesn't say the person's id is logged with it |

**Plans keep what the notice says they don't (SEC-06).** Both are reproduced against `80a0da3` by the tests in Patch A2, which fail on the unpatched code:
- A day planned from "where you are" keeps that point, as lunch's map pin. The notice says it is "sent once, rounded to about 100 metres … and it isn't kept".
- A trip's day plans keep the stay's name, in "from …" and "Lunch near …". The notice says a stay is kept by "its location, never its name".

## For Abram to check now (without sharing the value)

1. **Render → the Brain's web service → Environment:** is `BRAIN_ALERT_WEBHOOK_URL` set? Don't paste it anywhere.
2. **If it is set, what was sent:** run `GET /v1/admin/safety`, or open the export's `safety_alerts`.
   - Any alert with `notified: true` was copied, message and contact, to that channel.
   - `notified: false` means the post didn't happen or failed.
3. **If anything was sent, about the channel:**
   - **Which service it is**, for example a Slack or Discord channel.
   - **Who can read it.** Only Abram, and the backup helper once they have signed Part A (D38/D73)?
   - **How long it keeps messages,** by the channel's own settings.
   - **Then:** delete the copied alerts from the channel once each is resolved in ODYS, and set the shortest retention it allows.
4. **If it isn't set:** the webhook gap is closed until someone sets it. The log line and the stored location (A2) remain.

## Category A: the smallest production fixes (each separate, each Abram's approval)

### A1: the alert says only that a message is waiting

| | |
|---|---|
| **File** | `brain/src/brain/notify.py`, plus a new test `brain/tests/test_alert_minimal.py` (3 tests) |
| **Endpoints** | `POST /v1/me/safety`, its side effects only: the reply to the person is unchanged |
| **The webhook now gets** | "ODYS Help & safety: message #N is waiting (received 19 Nov 14:05, London time). Read it and reply with GET /v1/admin/safety; it isn't copied here." No message, contact, person or location |
| **The log** | keeps the message, as the live notice says, but no longer the person's id |
| **User-visible impact** | none: the automatic reply, the in-app thread and the replies are unchanged |
| **Experimental impact** | none: no question, plan, rating or export field changes. Safety alerts aren't part of Test B |
| **Patch** | `decisions/patches/A1-alert-minimal.patch`, sha256 `46c4473f2b68062ce90b091dbb7ee49fb2f39b3d1149a19c632247615392dc84` |
| **Needed only if** | the webhook is set (step 1). If it isn't, A1 can wait for the next normal release |

### A2: plans stop keeping "where you are" and the stay's name

| | |
|---|---|
| **File** | `brain/src/brain/api.py`: a `kept_stops` helper, the stored copy in `POST /v1/me/plans` and `POST /v1/me/trips/days`; a new test `brain/tests/test_stored_location.py` (4 tests) |
| **Endpoints** | `POST /v1/me/plans` (only when the start is "where you are", the name both frozen apps send) and `POST /v1/me/trips/days` (only when the person named their stay) |
| **What changes** | the **stored** copy only: lunch-at-the-start loses its pin, and the stay's name reads "your stay". **The reply to the phone is the person's own copy, unchanged**: the patch makes both replies return it explicitly, because the frozen code built them from the stored row |
| **User-visible impact** | none when planning. **One corner:** a plan fetched again later from the server (`GET /v1/me/plans`) shows "your stay" and no pin for lunch at the start. The apps keep their plan on the phone, so this shows only after a reinstall |
| **Experimental impact** | none on Test B: the pair is planned from the Test B brief's start, never "where you are" or a stay, and no file under `brain/data/testb`, `testb.py`, the planner or scoring is touched. The export's plan rows lose those pins and names, which no analysis uses |
| **Patch** | `decisions/patches/A2-stored-location.patch`, sha256 `7e4f950b0fa11a06f5a939d53e39cc0ed1607d3e007ead8e7553f2ead63828d1` |
| **Not included** | cleaning the pins and names already stored: a destructive change on the live database, run only if Abram asks, after a fresh backup |

**Evidence (19 Nov, on a clean checkout of `80a0da3`):**
- The frozen suite has 202 tests.
- **With A1 and A2 applied, 209 pass**: the 202 plus the 7 new ones. Each patch also applies alone.
- **Without the patches, the new tests fail**: the stored rows hold the point and the stay's name, and the webhook text carries the message.

**How it would reach production (Abram's steps; this session can push only its own branch):**
1. Make a branch from `80a0da3`.
2. `git apply decisions/patches/A1-alert-minimal.patch` (and/or A2).
3. Check each file's sha256 first.
4. Review the diff.
5. Approve its merge into `main`.
6. Render deploys `main`. Then `/v1/health` reports the new commit, not `80a0da3`.

**The effect on the round's manifest:** the tag `friends-round-1` stays on `80a0da3`, the code the testers' experiment was frozen at. The manifest gets one line naming the privacy commit and saying it changes no question, plan or answer. The preflight's "live Brain reports `80a0da3`" check is then replaced by "reports `80a0da3` plus the approved privacy commit".

## Category B: everything else on the development branch stays out of production during the round

| Change | Files | What a tester would notice | Why it waits |
|---|---|---|---|
| m275: no match words; the factor line | `reasons.py`, `dayplan.py`, `explain.py`, `triplength.py`, `discovery.py`, `quality.py`, `group.py`, `api.py` | the line under each stop's price; trip-length wording | product wording, not participant protection |
| m276: plans keep their predictions | `api.py` | nothing | new stored field; evaluation only |
| SEC-01/02/03: limits and validation | `ops.py`, `schemas.py` | a refusal for oversized or impossible requests (the apps never send them) | changes behaviour; little risk in a private round |
| SEC-04: export robustness | `api.py` | nothing | only matters if a bad number arrives. **If the export fails during the round, this is the fix**, reviewed then |
| SEC-05: address header, check route | `ops.py`, `api.py` | nothing | needs the staging check first |
| SEC-07: API pages off | `api.py`, `config.py` | nothing | low risk; the admin token guards the routes anyway |
| SEC-08: backup route error | `api.py` | nothing | harmless; no rush |
| SEC-09 in full: the message out of the logs too, and the notice updated | `notify.py`, `privacy_app.html` | the privacy notice's text | the notice is what participants agreed to; A1 covers the urgent part |
| SEC-10: deletion records survive a restore | `db.py`, `backup.py`, `api.py` | nothing | **only matters if a restore happens.** The in-place upgrade involves none (`database-upgrade-runbook.md`) |
| SEC-19: 20 searches a day per install | `trips.py`, `api.py` | a refusal after 20 searches in a day | behaviour |
| The apps (SEC-13/15/16) | `app/`, `android/` | a new build | the round's builds are frozen |

## Hours

- **Claude:** 1.5 h for the patches, tests and this note (done).
- **Abram:**
  - 0.25 h for the checks above;
  - 0.5 h to review and decide on A1 and A2;
  - 0.25 h to deploy, if approved.
