# The friends' round: one fixed version (m196, m197)

**Decision.** The friends' round is a controlled run of Test B: every tester uses the same app and Brain, recorded below, and nothing reaches `main` until the round ends: no code, no notes. This sheet lives on the work branch. Friends are a first usability group; the results are read as direction, not proof (D127).

## Open before the first invite (kept here, apart from development; Abram, 7 Nov)

| Item | Who | Status |
|---|---|---|
| The live Brain runs `80a0da3`, and branch pushes can't redeploy it | Abram (Render), Claude (checks) | **Done** 6 Nov 22:54 UTC; checked again 7 Nov |
| Tag `friends-round-1` on `80a0da3` | Abram (this session can't push tags) | **Waiting** |
| Rehearsal on TestFlight 91 and Android 21 with the code `REHEARSAL`, then the read-out, then clean-up (steps 3-4 below) | Abram, Claude reads the read-out | **Waiting** |
| Apple outside-activities check (D60, D94) | Abram | **Waiting** |
| TestFlight's external review of build 91 | Abram | **Waiting** (after the Apple check) |
| Recruiting, with the code FRIENDS; start date into the manifest | Abram | After all of the above |

**Checked 12 Nov 2026 (m252), for Abram's approval; no tag was created:**
- `main`, the live Brain, iOS run 91 (TestFlight upload succeeded) and Android run 21 (the `android-latest` release, `ODYS-android-21.apk`) are all on `80a0da3`.
- `friends-round-1` doesn't exist yet.
- Nightly backups are running.

## The experiment manifest

| What | Value | How to check it during the round |
|---|---|---|
| Code (git commit on `main`) | `80a0da3` | `git ls-remote origin main` still gives `80a0da3…` |
| Git tag | `friends-round-1` on `80a0da3` | `git ls-remote --tags origin friends-round-1`. **Abram pushes it** (this session can't push tags): see "Before the first invite" |
| iPhone (TestFlight build) | `91` (iOS run #91, from `80a0da3`, uploaded 6 Nov) | TestFlight shows build 91 to testers |
| Android (APK) | `21` (Android run #21, from `80a0da3`, published 6 Nov 22:18 UTC) | The `android-latest` download: "ODYS for Android (build 21)", "from main (80a0da3)" |
| Brain (server) | `80a0da3`, live since 6 Nov 22:54 UTC (Render: branch `main`, Auto-Deploy off, Blueprint Auto Sync off) | `GET https://moments-brain.onrender.com/v1/health` answers `"version": "80a0da3"` (checked 6 Nov 22:54) |
| Population model | `0.2` | `/v1/health` `population_version` |
| Consent text | `app-2026-10-02` | The apps' consent version |
| Test B version | As of `80a0da3`: the blind Plan 1 / Plan 2 pair (personal vs the no-answers generic plan, order random and stored), the gut choice, "This plan fits me" 1–5 for each, "Which would be easier to actually do on the day?" (optional), why (optional), then the reveal | The iPhone screenshots of 95581c1 (run #89; no app change since) and Android build 21's screens |
| Read-out | `brain/scripts/testb_report.py` from the work branch, with `--code FRIENDS --since <start date>` (m197) | It prints how many installs it counted, of how many |
| Experiment date | Abram fills in: the day the first invite goes out | |
| Testers | The tester code **FRIENDS** (typed on the welcome screen; "friends" and " Friends " count too). The count comes from the export at the end | Their install IDs stay in `validation/raw/` on Abram's computer (never in git) |

## What keeps it fixed

Three systems, each tested on 6 Nov:

- **iPhone.** Only `main` reaches TestFlight. A push builds and uploads only on `main`. A run started by hand on the branch now builds for the simulator whatever its upload box says (m197; before, the box was ticked by default and would have uploaded a branch build). Tested on 6 Nov: branch run #92, with the box ticked and the signing secrets set, skipped the certificate, the signing and the upload.
- **Android.** Only `main` publishes the `android-latest` download (m196). Tested: the branch push 24556b6 (run #20) built, skipped "Publish", and the download stayed build 21.
- **Brain.** **Fixed on 6 Nov, 22:54 UTC** (Abram: Blueprint Auto Sync off, `moments-brain` on `main`, Auto-Deploy off, then a deploy): `/v1/health` answers `80a0da3`. Before that, `/v1/health` showed the branch's commits (774fa24, then 24556b6), and GitHub's deployment records show Render deploying `claude/vigilant-cannon-my82dj` for both services. They came from the Blueprint (`render.yaml`), which has no `branch` field, so they follow the Blueprint's branch. The only difference from `80a0da3` was one added endpoint the testers' apps never call. Tested after the fix: a branch push (5cc35cb, 22:55 UTC) started no deploy, and `/v1/health` stayed `80a0da3`. The fix is Abram's, in the Render dashboard (below). Render's docs (read 6 Nov 2026):
  - A service with no `branch` follows the Blueprint's branch: "Render uses the Blueprint's branch if the service uses the same repo as the Blueprint file" (render.com/docs/blueprint-spec).
  - A sync overwrites dashboard changes: "the next Blueprint sync overwrites them" (render.com/docs/infrastructure-as-code). It can be turned off: "set Auto Sync to No on your Blueprint's Settings page".
  - Auto-deploy can be turned off per service (On Commit, After CI Checks Pass, Off), and deploying a specific commit from the dashboard "disables automatic deploys for the service" (render.com/docs/deploys).
  - Pull request previews and preview environments are off unless turned on (render.com/docs/service-previews, /docs/preview-environments). Keep them off. The service's Deploy Hook URL (Settings) can deploy too: never share it.
- **The swipe page** (`london-places-swipe`, not part of the round) still deploys the branch (78e82a3 did, 6 Nov). It shares the database but only its own tables, so `brain/src/brain/calibration.py` doesn't change during the round.
- **During the round:** no commits to `main` (code or notes), no change to `render.yaml`, and no Manual Deploy, Blueprint sync or settings change on `moments-brain`. New work stays on the branch, and it only reaches testers after the round, through `main`.

## What it collects

1. The gut choice: which plan they'd rather do.
2. "This plan fits me" (1–5) for each plan: how personal it felt.
3. "Which would be easier to actually do on the day?" (Plan 1, Plan 2 or Same; optional): practicality.
4. Why (optional): their reasoning.

Also the stops' ratings, the end-of-day questions, and the Test A survey. `brain/scripts/testb_report.py` reads an export:
- It counts only this round's testers with `--code FRIENDS --since <start date>`. Without them it counts every install and says so by source: the database also holds the 15 installs restored on 6 Nov (Abram's own runs).
- It tells personal from generic by each plan's kind, never by its number.
- Every share is shown with how many answered and how many didn't.
- It lists everyone who chose the generic plan, with their scores and reasons, before any averages.

**Rehearsed on 6 Nov** (`brain/scripts/rehearse_testb.py`, on the frozen code at `80a0da3`, with a throwaway database): seven made-up installs, the export and the read-out. Every count matched the one worked out by hand. It found the mixing above, now handled by `--code` and `--since`.

## Keeping the data safe

- **Nightly sealed backup** (the `ops` workflow), kept 30 days on GitHub. Only Abram's private key opens it (m195).
- **The admin export once a week and at the end**, saved by Abram into `validation/raw/` on his computer (git-ignored). Then `python brain/scripts/testb_report.py <export.json> --code FRIENDS --since <start date>`.
- **The free database expires on 6 Dec 2026** (Render's banner; deleted 14 days later). The round ends, and its final export is saved, **by 29 Nov**. Otherwise, before then, the database moves to a paid plan or is swapped and restored as on 6 Nov (`brain/README.md`).

## Before the first invite

1. **Done (6 Nov):** Render follows `main`, and nothing can replace it (Abram, in the dashboard):
   1. Blueprints → the Blueprint → Settings → **Auto Sync: No**.
   2. `moments-brain` → Settings → the deploy **Branch** → `main`.
   3. On the same page → **Auto-Deploy: Off**.
   4. `moments-brain` → **Manual Deploy → Deploy latest commit**, and wait for "Deploy live".
   5. Claude checks `/v1/health` shows `"version": "80a0da3"`, and GitHub's deployment record shows `main` (dashboard labels alone don't count).
2. **The tag** (Abram, from his copy of the repo, in PowerShell):
   `git fetch origin` then `git tag -a friends-round-1 80a0da3 -m "The friends' round: main 80a0da3, TestFlight 91, Android 21"` then `git push origin friends-round-1`. Check: `git show friends-round-1 --no-patch` names commit `80a0da3`.
3. **An internal run on the real builds** (Abram, with the code `REHEARSAL`):

   | Install | Gut choice and both scores | "Easier" | Why |
   |---|---|---|---|
   | iPhone, TestFlight 91 | Answer | Answer | Answer |
   | Android, build 21 | Answer | Skip | Skip |

   Then the export and the read-out with `--code REHEARSAL --no-overlap`. It should count 2 installs, both answered the pair, and "easier" answered by 1 of 2 (1 didn't). **These are two installs by one person, not two participants**; the read-out says a tester is an install.
4. **Clean up after the run:**
   - "Delete my data" on both phones.
   - On the same export, the read-out with `--code FRIENDS` should count 0 installs, so the round starts with no earlier answers. If an earlier test used FRIENDS, `--since <start date>` leaves those out, and the read-out says how many it counted. `REHEARSAL` installs never match `--code FRIENDS`, so they're excluded either way.
   - Delete the export file: `Remove-Item validation\raw\export-rehearsal.json`. `validation/raw/` is git-ignored. Raw exports are never committed or shared, only the read-out's text. The admin token stays in Abram's PowerShell window, never in a chat.
5. The Apple outside-activities check, which gates external TestFlight (D60, D94). It's Abram's.
6. TestFlight's external review of build 91. Android testers use the `android-latest` link.
7. Recruiting starts only after 5 and 6. The tester code **FRIENDS** goes in every invite, and the start date goes in the manifest.
