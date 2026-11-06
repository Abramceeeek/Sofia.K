# The friends' round: one fixed version (m196)

**Decision.** The friends' round is a controlled run of Test B: every tester uses the same app and Brain, recorded below, and nothing that changes them reaches `main` until the round ends. Friends are a first usability group; the results are read as direction, not proof (D127).

## The fixed version (filled in when the builds are up)

| What | Value | How to check it during the round |
|---|---|---|
| Code (git commit on `main`) | `PENDING` | `git log -1 origin/main -- app android brain .github` shows no newer commit |
| iPhone (TestFlight build) | `PENDING` | TestFlight shows this build number to testers |
| Android (APK) | `PENDING` | The `android-latest` download's title, "ODYS for Android (build N)" |
| Brain (server) | `PENDING` | `GET /v1/health` answers `"version": "<7 characters of the commit>"` |
| Population model | `0.2` | `/v1/health` `population_version` |
| Start date | Abram fills in: the day the first invite goes out | |
| Testers | The count, from the admin export at the end | Their install IDs stay in `validation/raw/` (never in git) |

**What keeps it fixed:**
- **No pushes to `main` that change the app, Android, the Brain or the workflows.** Only notes like this one may change, and they deploy nothing.
- **New work stays on `claude/vigilant-cannon-my82dj`.** Branch builds never reach testers: the iPhone workflow only uploads from `main`, Android publishes its download only from `main` (since m196), and Render deploys only `main`.

## What it collects

1. The gut choice: which plan they'd rather do.
2. "This plan fits me" (1–5) for each plan: how personal it felt.
3. "Which would be easier to actually do on the day?" (Plan 1, Plan 2 or Same; optional): practicality.
4. Why (optional): their reasoning.

Also the stops' ratings, the end-of-day questions, and the Test A survey. `brain/scripts/testb_report.py` reads an export:
- It tells personal from generic by each plan's kind, never by its number.
- Every share is shown with how many answered and how many didn't.
- It lists everyone who chose the generic plan, with their scores and reasons, before any averages.

## Keeping the data safe

- **Nightly sealed backup** (the `ops` workflow), kept 30 days on GitHub. Only Abram's private key opens it (m195).
- **The admin export once a week and at the end**, saved by Abram into `validation/raw/` on his computer (git-ignored). Then `python brain/scripts/testb_report.py <export.json>`.
- **The free database expires on 6 Dec 2026** (Render's banner; deleted 14 days later). The round ends, and its final export is saved, **by 29 Nov**, or before then the database moves to a paid plan or is swapped and restored as on 6 Nov (`brain/README.md`).

## Before the first invite

- The Apple outside-activities check, which gates external TestFlight (D60, D94). It's Abram's.
- TestFlight's external review of the fixed build. Android testers use the `android-latest` link.
- The tester code **FRIENDS** on the welcome screen, so every tester is tagged as a friend.
