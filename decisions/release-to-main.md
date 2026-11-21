# Moving everything to `main`: the release and its steps (20 Nov 2026; m315)

**Abram's decision (20 Nov):** "Yes, move all to main", and Android publishing **off** until his own release key exists.
- **The friends' round moves to the new build.** It is no longer frozen at `80a0da3` and TestFlight 91. No friend had been invited, so no round data is lost.
- It gets a new manifest, a new rehearsal and a tag on the new `main` commit.

## What goes in

The development branch (`claude/vigilant-cannon-my82dj`, with PR #2 merged) plus three release fixes, through the release PR from `claude/pensive-euler-fftd63`.

**From the development branch** (84 commits), among them:
- m275: no match words; the factor line under each stop's price;
- SEC-01/02/03 (size limits), SEC-04/05/07/08/09/10/19;
- the iPhone and Android fixes (SEC-13/15/16);
- Paris as a development-only city, never offered.

**This release adds:**
- **The alert says exactly "Safety message #N is waiting"** (Abram, 20 Nov §2). The development branch had a longer text.
- **A failed database write never logs its values** (`hide_parameters`; found on 20 Nov at `80a0da3`).
- **The nightly storage warning (A4):** the backup route reports the database size, and the `ops` job fails at 50% of 1 GB. The public log prints only "under 50%".
- **Android: no APK is handed out** (`android.yml`): no run artifact and no `android-latest` download. The build still runs, with its tests and every screen drawn.

**What already matched** the 20 Nov hotfixes:
- A2 (stored plans keep neither "where you are" nor the stay's name: SEC-06);
- A3's log line (SEC-09);
- the privacy notice updated to match, "Last updated: 12 November 2026", consent version `app-2026-10-02` unchanged.

**Not changed:** `render.yaml` (still `plan: free` everywhere, with Blueprint Auto Sync off), the swipe page's code, and the consent version.

## What happens when it merges

| | Automatically | By hand (Abram) |
|---|---|---|
| **iPhone** | `ios.yml` builds, signs and uploads a **new TestFlight build** (a push to `main` that changes `app/`), numbered with the run number | install it from TestFlight on his phone. **External testers get it only after he adds it to the external group** (Apple reviews it again) |
| **Android** | builds and tests; **publishes nothing** | `android-latest` still offers build 21 (the public debug key): **delete that release** (GitHub → Releases → `android-latest` → Delete), so nobody installs it |
| **The Brain** | **nothing**: Auto-Deploy is off on `moments-brain` (since 6 Nov) | deploys it (step 3 below). **Until then the new app talks to the old server**, and its new parts won't work |
| **The database** | nothing | the backup and preflight first. The new Brain adds one table (`deletions`) on start; no existing table or column changes |
| **Nightly `ops`** | runs from `main`, now with the storage check | — |

## The order (Abram; about 1.5 h in one evening, after the merge)

1. **Merge the release PR** into `main` ("Create a merge commit"), once CI is green. Claude merges it only on his word.
2. **The database schedule, steps 0–7** (`database-before-6-dec.md`): the food field, a fresh backup, the export, `python -m brain.backup preflight`, his "go", then the upgrade to Basic-256mb.
   - **The backup and preflight come before the deploy**, because the deploy adds a table to the live database.
3. **Deploy the Brain:** Render → `moments-brain` → Manual Deploy → "Deploy latest commit". Wait for "Deploy live".
4. **The server to 1 CPU** for the round (approved 19 Nov), if not already done in step 2's evening.
5. **Checks** (Claude reads them):

   | Check | Expected |
   |---|---|
   | `https://moments-brain.onrender.com/v1/health` | `"ok": true`, and `"version"` the first 7 characters of the new `main` commit |
   | The SEC-05 address check (`security-release-proposal.md`, "SEC-05: confirm what Render passes") from his phone | it shows his own network, not Render's |
   | One Help & safety message from his phone | the webhook, if set, shows only "Safety message #N is waiting" |
   | Actions → `ops` → Run workflow → `backup` | green, with "The database is under 50% of its 1024 MB." |
   | The new TestFlight build on his iPhone | it opens, signs in, and makes a plan |
6. **The round on the new build:**
   - Claude writes the new manifest (commit, TestFlight number, database, server);
   - Abram runs the 25-step rehearsal on it;
   - Abram tags `friends-round-1` **on the new commit** (`validation/friends-round.md`);
   - then Apple's check, the external TestFlight review, and the invites.

## Rollback

| If | Do |
|---|---|
| The new Brain misbehaves after step 3 | Render → `moments-brain` → Deploys → the `80a0da3` deploy → Rollback. The old code ignores the added `deletions` table. Testers stay on TestFlight 91 until it's fixed |
| The release itself is wrong | `git revert -m 1 <merge commit>` on `main`, then Manual Deploy. A revert that changes `app/` uploads another TestFlight build |
| The database after step 2 | the rollback in `database-before-6-dec.md` |

## Hours

- **Claude:** 1.5 h (the merge, the three fixes, the tests, this page).
- **Abram:** about 1.5 h for steps 1–5, then the rehearsal (about 45 min).
