# The friends' round: one fixed version (m196, m197; moved to the new build, m315; and again, m320)

> **21 Nov (m320): the round moves again, to the release that adds the Seville preview.** Abram chose "Seville in the app, me only". The preview is read-only and opens only with the code `ODYS-SEVILLE`; without it, the app is the same as build 112.
> - **The round's fixed version is now the merge commit of the 21 Nov release, and the TestFlight build it uploads.** Read "the new `main` commit" and "the new build number" below as those.
> - **The rehearsal on build 112 has to be redone on the new build.** The tag goes on the new commit.
> - No friend has been invited yet, so nothing is lost.

> **20 Nov (m315): the round moves to the new `main`.** Abram chose to put everything on `main` (`decisions/release-to-main.md`). No friend had been invited, so nothing is lost.
> - **The round's fixed version is the release's merge commit**, not `80a0da3`. TestFlight gets the build the merge uploads; Android stays unpublished until Abram's release key exists.
> - **Everything below keeps its checks and order, with three changes:**
>   - read "`80a0da3`" as **the new `main` commit**;
>   - read "TestFlight 91" as **the new build number**;
>   - Android is option B only, once the release key exists.
> - **The tag goes on the new commit.** The commands below show where to put it.


**Decision.** The friends' round is a controlled run of Test B: every tester uses the same app and Brain, recorded below, and nothing reaches `main` until the round ends: no code, no notes. This sheet lives on the work branch. Friends are a first usability group; the results are read as direction, not proof (D127).

## Open before the first invite (one order; Abram, 20 Nov §4)

Every step below happens before the tag, and the tag before any invite. **The rehearsal runs on the final configuration** (database, server, privacy commit, Android build), so what friends get is what was rehearsed.

| # | Step | Who | Status (20 Nov) |
|---|---|---|---|
| 1 | **The database to Basic-256mb and the server to 1 CPU.** One evening, with the backup preflight first (`decisions/database-before-6-dec.md`, "The schedule") | Abram | **Waiting for his "go"** after the preflight passes |
| 2 | **The privacy hotfixes**, if approved: deployed by hand and checked (`decisions/production-privacy-patch.md`, "Release procedure") | Abram | **Waiting for his approval** of the set and the procedure |
| 3 | **Android:** option A (iPhone only) or B (a properly signed build of `80a0da3`). **Build 21 is ruled out:** it is signed with the public debug key (`decisions/android-signing-key-runbook.md`) | Abram | **His decision** |
| 4 | **The rehearsal on the real phones**, with the code `REHEARSAL`. All 19 ⛔ steps pass on every phone the round uses (`friends-round-rehearsal.md`) | Abram; Claude reads the read-out | **Waiting** for 1–3 |
| 5 | **The seven tag conditions** (the next section) | Claude checks; Abram confirms his rows | **Waiting** for 1–4 |
| 6 | **The tag** `friends-round-1` on `80a0da3` (commands below) | **Abram** (this session never pushes tags) | after 5 |
| 7 | Apple outside-activities check (D60, D94) | Abram | **Waiting** |
| 8 | TestFlight's external review of build 91 | Abram | **Waiting** (after 7) |
| 9 | Recruiting, with the code `FRIENDS`. Start date into the manifest | Abram | after all of the above |

**The tester code is a label, not a lock** (Abram, 20 Nov §3):
- The frozen app accepts any code and keeps it as the install's source.
- `FRIENDS` and `FAMILY` being readable in the public repository lets anyone label themselves a friend. It keeps nobody out, and a new unpublished code wouldn't either.
- Its only job is attribution: the read-out counts `--code FRIENDS --since <start date>`. An outsider using it shows up there as an extra install, and the invite list is the check on who was asked.

### The seven conditions before the tag (Abram, 20 Nov §4)

| # | His condition | The check, and what it must show | Who |
|---|---|---|---|
| 1 | His private-key backup restoration check | `python -m brain.backup preflight <file> --key <key> --export <export>` ends **`Result: ALL CHECKS PASS`**, before the upgrade (step 3 of the schedule) and again on a backup made after it (step 9) | Abram runs; Claude reads |
| 2 | A successful real-device rehearsal | `friends-round-rehearsal.md`: every ⛔ step ticked on each phone the round uses. **Option A:** the iPhone column. **Option B:** both, the Android column on the re-signed file itself. A simulator or screenshot doesn't count | Abram |
| 3 | The iPhone and Android build fingerprints | **iPhone:** App Store Connect → TestFlight shows build **91** as the external group's build, and the phone's TestFlight page shows 91. GitHub's side, iOS run #91 on `main` at `80a0da3`, was checked by Claude on 19 Nov. Apple re-signs TestFlight builds, so the build number and its run are the fingerprint.<br>**Android:** build 21's certificate is `a07dae0c…cfb9`, the public debug key, so it is not used. Under option B, record the file's SHA-256 (`Get-FileHash`) and its certificate (`apksigner verify --print-certs`). The certificate must be the release key's recorded fingerprint, never `a07dae0c…` | Abram; Claude checks the numbers |
| 4 | The manifest confirmed | The manifest below, updated by Claude from steps 1–3: the database and server plans, the privacy commit (if any) and the Android file (or "iPhone only"). Abram reads it once | Claude, then Abram |
| 5 | No unintended changes in the frozen builds | `git fetch origin`, then `git diff --stat 80a0da3 origin/main -- app android` prints **nothing**, and `git log --oneline 80a0da3..origin/main` shows only the approved privacy commits (or nothing). GitHub Actions shows no iOS run after #91 and no Android run after #21 on `main` | Claude (read-only), Abram confirms |
| 6 | The live Brain's version | `Invoke-RestMethod https://moments-brain.onrender.com/v1/health` shows `ok` True, `version` `80a0da3` (or the first 7 characters of the approved privacy merge) and `population_version` `0.2` | Claude |
| 7 | Database and server readiness | In Render, Abram confirms:<br>• the database is **Basic-256mb, 1 GB, autoscaling off, Available**;<br>• `moments-brain` is **1 CPU**, with Auto-Deploy **Off**;<br>• Blueprint Auto Sync is **No**.<br>And condition 1's post-upgrade preflight has passed | Abram |

**Checked 12 Nov 2026 (m252), for Abram's approval; no tag was created:**
- `main`, the live Brain, iOS run 91 (TestFlight upload succeeded) and Android run 21 (the `android-latest` release, `ODYS-android-21.apk`) are all on `80a0da3`.
- `friends-round-1` doesn't exist yet.
- Nightly backups are running.

**The tag's 8-point preflight, 12 Nov 2026 (m265; Abram approved the tag in m260), all passed:**
1. No `friends-round-1` on GitHub.
2. `main` is `80a0da3`.
3. The live Brain's `/v1/health` gives `"version": "80a0da3"`.
4. TestFlight 91 is iOS run #91 at `80a0da3`, and its upload succeeded.
5. Android 21 is run #21 at `80a0da3`; `android-latest` holds `ODYS-android-21.apk`.
6. The latest backup (ops run 43196164553, 12 Nov 09:58 UTC, 56,918 bytes) passed the workflow's sealed-format check. Only Abram's key can show it opens: `count-food` does that, printing only numbers (`decisions/foods-avoided-audit.md`, step 1).
7. No commits on `main` after `80a0da3`.
8. This session's annotated tag points exactly at `80a0da3d117a1898deeb5a8913fea9f5914cb390`.

**The push was refused:** the session's git proxy answers HTTP 403 to any push but the work branch. Claude stopped there, as the approval required, and created nothing at any other commit. Rechecked 13 Nov: points 1–3 and 8 unchanged. **Abram pushes it** with step 2 of "Before the first invite"; the check after it must name `80a0da3`.

### Fresh read-only preflight, 19 Nov 2026 (m295; Abram, 19 Nov: "Do not create or push the tag yourself")

Nothing was created, pushed or changed. **All agree with the manifest:**

| Check | Found on 19 Nov | Matches |
|---|---|---|
| `main` | `80a0da3d117a1898deeb5a8913fea9f5914cb390`, 0 commits after it | yes |
| The live Brain | `/v1/health`: `"ok":true`, `"version":"80a0da3"`, `"population_version":"0.2"` | yes |
| TestFlight build 91 | iOS run #91 (run 42303190373) on `main` at `80a0da3`, 6 Nov 22:14 UTC, success. TestFlight keeps a build for 90 days (Apple, TestFlight overview), so until about 4 Feb 2027. Claude can't see App Store Connect | yes |
| Android build 21 | Android run #21 (run 42303190295) on `main` at `80a0da3`, success. The `android-latest` release targets `80a0da3`: "ODYS for Android (build 21)", asset `ODYS-android-21.apk` (30,143,378 bytes) | yes |
| Remote tags | only `android-latest`; **no `friends-round-1`** | yes |
| Local tag (this session) | annotated, made 6 Nov 22:37 UTC, pointing at `80a0da3d117a…`. It can't be pushed from here | yes |
| Latest backup | ops run #119 (44506350232), 19 Nov 10:31 UTC; artifact `odys-brain-backup-44506350232`, 56,918 bytes, kept until 19 Dec. The run passed the workflow's sealed-format check | yes |
| Frozen configuration at `80a0da3` | tester codes FRIENDS and FAMILY (any other code, such as `REHEARSAL`, is accepted and kept as the source); consent `app-2026-10-02` in both apps; population model `0.2` | yes |

**Abram: push the tag (PowerShell, from your copy of the repo; about 2 minutes), only after the seven conditions above.** Use the full commit, never a branch name:

```powershell
git fetch origin
git ls-remote origin main
#   expected: 80a0da3d117a1898deeb5a8913fea9f5914cb390  refs/heads/main
#   (or, if the privacy hotfix was merged: its merge commit. The tag still goes on 80a0da3, the code the
#   experiment was frozen at; condition 5 shows the merge changed nothing under app/ or android/)
git ls-remote --tags origin friends-round-1
#   expected: nothing (no tag yet). If a line appears, stop and tell Claude.
git tag -a friends-round-1 <the new main commit, in full> -m "The friends' round: code <short commit>, TestFlight <build> (the manifest records the rest)"
#   m315: since the move to main (20 Nov), the round's commit is the release's merge commit, not 80a0da3.
#   Claude fills in the exact commit and build number in the manifest before this step.
#   if it says "already exists": git rev-parse "friends-round-1^{commit}" must print 80a0da3d117a…; anything else, stop
git show friends-round-1 --no-patch
#   expected: "tag friends-round-1", your name, the message, then "commit 80a0da3d117a1898deeb5a8913fea9f5914cb390"
git push origin refs/tags/friends-round-1
git ls-remote --tags origin friends-round-1
#   expected: two lines: "<tag object>  refs/tags/friends-round-1" and
#             "80a0da3d117a1898deeb5a8913fea9f5914cb390  refs/tags/friends-round-1^{}"
```

Then tell Claude, and Claude checks it from here (read-only).

## The experiment manifest

| What | Value | How to check it during the round |
|---|---|---|
| Code (git commit on `main`) | **`ca6fd69`** (`ca6fd69b3317738db55c76502f1b52e3dbf89de7`), the release merge of 20 Nov (m315). Was `80a0da3` | `git ls-remote origin main` still gives `ca6fd69…` |
| Git tag | `friends-round-1` on **`ca6fd69`** (after the rehearsal) | `git ls-remote --tags origin friends-round-1`. **Abram pushes it** (this session can't push tags): see "Before the first invite" |
| iPhone (TestFlight build) | **`112`** (iOS run #112, attempt 3, from `ca6fd69`, uploaded 20 Nov 14:08 UTC). Attempts 1 and 2 were refused by Apple until Abram accepted the updated agreements. Was 91 | TestFlight shows build 112 to testers; external testers only once Abram adds it to the external group |
| Android (APK) | **Not build 21:** it is signed with the public debug key (certificate `a07dae0c…cfb9`, checked 20 Nov). Option A: none (iPhone only). Option B: the re-signed release build of `80a0da3`, its SHA-256 and certificate recorded here | Under option B: `Get-FileHash` and `apksigner verify --print-certs` on the file friends get |
| Brain (server) | **`ca6fd69`, live since the release merge on 20 Nov** (~10:40 UTC; checked 16:39 UTC: `ok`, `version` `ca6fd69`). **Auto-Deploy turned out to be on** (Abram, 20 Nov: "I didn't deploy it, auto-deploy was on"), so Render deployed `main` on the merge, before the planned backup check. Nothing was lost: the new code only added the empty `deletions` table, and the nightly backups from before the merge are kept 30 days. **Abram turns Auto-Deploy off** (m316). **To be recorded:** that it's off, and the 1 CPU change | `GET https://moments-brain.onrender.com/v1/health` answers `"version": "ca6fd69"` | `GET https://moments-brain.onrender.com/v1/health` answers `"version": "80a0da3"` (checked 6 Nov 22:54) |
| Database | **To be recorded:** Basic-256mb, 1 GB, autoscaling off, from <date> (free until then) | Render → the database's Info page |
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
- **The free database expires on 6 Dec 2026** (Render's banner; deleted 14 days later). **It moves to a paid plan before the first invite** (step 1 above; `decisions/database-before-6-dec.md`, m306), so the round has no database deadline. The 19 Nov "final export by 29 Nov" is retired. Nothing is bought or moved without Abram.
- **The plan, the invite and the analysis:** `friends-round-plan.md` (m265).

## Before the first invite

**The order is the table at the top** ("Open before the first invite"). Kept here from 6 Nov, because it explains the Render settings condition 7 checks:

1. **Done (6 Nov):** Render follows `main`, and nothing can replace it (Abram, in the dashboard):
   1. Blueprints → the Blueprint → Settings → **Auto Sync: No**.
   2. `moments-brain` → Settings → the deploy **Branch** → `main`.
   3. On the same page → **Auto-Deploy: Off**.
   4. `moments-brain` → **Manual Deploy → Deploy latest commit**, and wait for "Deploy live".
   5. Claude checks `/v1/health` shows `"version": "80a0da3"`, and GitHub's deployment record shows `main` (dashboard labels alone don't count).
2. **The rehearsal's minimum** (the full 25 steps are `friends-round-rehearsal.md`):

   | Install | Gut choice and both scores | "Easier" | Why |
   |---|---|---|---|
   | iPhone, TestFlight 91 | Answer | Answer | Answer |
   | Android, option B's file (if used) | Answer | Skip | Skip |

   Then the export and the read-out with `--code REHEARSAL --no-overlap`. With both phones it should count 2 installs, both answered the pair, and "easier" answered by 1 of 2. With the iPhone only: 1 install. **These are installs by one person, not participants**; the read-out says a tester is an install.
3. **Clean up after the run:**
   - "Delete my data" on each phone.
   - On the same export, the read-out with `--code FRIENDS` should count 0 installs, so the round starts with no earlier answers. `REHEARSAL` installs never match `--code FRIENDS`.
   - Delete the export file: `Remove-Item validation\raw\export-rehearsal.json`. `validation/raw/` is git-ignored. Raw exports are never committed or shared, only the read-out's text. The admin token stays in Abram's PowerShell window, never in a chat.
4. **Recruiting** starts only after the tag, the Apple check and TestFlight's review. The tester code **FRIENDS** goes in every invite, and the start date goes in the manifest.
