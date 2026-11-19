# The old free-text food field: a count-only audit and a deletion plan (9 Nov 2026; m233, m266)

**Decision (Abram, m224, confirmed m260): count it, delete any that exist, make sure a backup can't bring it back, and never export or share the contents.**
- The code is built and tested on the branch.
- **Nothing has been run against the live Brain.** This session has no access to the database. Abram, m260: "Do not attempt to access the production database using an admin token or another workaround."
- **An authorised operator (Abram) runs the seven steps below**, about 30 minutes, with the exact commands and what each should print.
- No new food preference persistence is authorised (m260).

## What it is

- **The field:** `foods_avoided`, D19's optional "Any foods or drinks you avoid?", kept as free text in a person's profile (`users.profile`, a JSON column).
- **When it was asked:** until D123 (8 Oct) stopped asking it.
- **Why it matters:** free text can name a religion ("no pork, halal") or health ("peanuts"). That's special category data, without the consent the DPIA now requires (`dpia-food-needs.md`).

## Where a value could still be

| Place | Today (main, `80a0da3`) | On the branch (m223, m233) |
|---|---|---|
| **The live database**, `users.profile` | Stored, if a profile save sends it | Every profile save drops it (m223). The audit and the delete find and remove what's left |
| **A phone on build 91 or Android 21** | Both apps' `Profile` still has `foodsAvoided`. A phone that answered before 8 Oct still holds it and **sends it with every profile save**, and main stores it again | Both apps' profiles no longer carry it (m223) |
| **Nightly backups** (GitHub artifacts, sealed to Abram's key, **kept 30 days**, `ops.yml`) | They hold whatever the database holds | **New backups never carry it**, and **restoring an older one strips it** (`backup._scrubbed`, both ways) |
| **The database itself was restored from a backup on 6 Nov** (README) | So any value from before 8 Oct came back with it | — |
| **Render's point-in-time recovery** (paid plans only, 3 days on Hobby: `database-before-6-dec.md`) | None on the free plan | Recovering to a moment before the deletion would bring it back |
| **A backup opened on Abram's computer** (`backup.json`) | The README already says to delete it after reading | `count-food` counts without opening it onto disk (m266) |

## The operator procedure (Abram's seven steps, m260; exact commands and outputs, m271, 19 Nov)

**Who:** an authorised operator, Abram, on his own computer. Claude never runs it: "Do not attempt to obtain additional database permissions or use an admin token."

**Time:** about 30 minutes.

**When:** **before the database upgrade** (`database-before-6-dec.md`). The free database has no point-in-time recovery, so a delete made before the upgrade can never be brought back by a recovery afterwards.

**What you need:**
- your copy of the repo;
- the Python 3.12 environment you used for the 6 Nov restore;
- your backup private key;
- the database's External URL (Render → `london-places-swipe-db` → Connect → External).

**No `psql` is needed:** `python -m brain.foodfield` does the database steps and only ever prints counts.

**Tested on 19 Nov** on PostgreSQL 16.15, with main's own `users` table and synthetic rows only (then deleted):
- the SQL count and the command agreed: 4, 2, 1;
- the delete removed only the key, kept every other profile field and every record, and created no table;
- the count after was 0.

### Before you start (PowerShell)

```powershell
cd <your copy of the repo>
git fetch origin claude/vigilant-cannon-my82dj
git switch claude/vigilant-cannon-my82dj   # the branch's tools, run on your computer; nothing is deployed
cd brain
$env:PYTHONPATH = "src"
$env:ODYS_DB = Read-Host "Paste the External URL"   # Read-Host keeps the password out of your command history
```

Under the database's **Networking** in Render, allow your own IP address for this session. You'll remove it at the end.

**Never** run a query that selects `profile`, and never use `python -m brain.backup open` for this. Every command below prints numbers only.

### 1. Verify a clean replacement backup

1. GitHub → Actions → `ops` → Run workflow → job `backup`. **Expected:** the run turns green and keeps an artifact named `odys-brain-backup-<run id>` (about 57 KB on 19 Nov).
2. Download it, unzip it, and run:

```powershell
python -m brain.backup count-food <path to odys-brain-YYYYMMDD.odysbk> --key <path to your private key> --after-restore
python -m brain.backup counts     <path to odys-brain-YYYYMMDD.odysbk> --key <path to your private key>
```

**Expected:**

```text
profiles N, with_key K, non_empty M
after a restore (in memory, nothing written): profiles N, with_key 0, non_empty 0
made_at 2026-11-..T..
answers …            # then one line per table: its name and its number of rows
```

- The first line shows the backup opens with your key. N is the number of installs (15 were restored on 6 Nov, plus any since).
- The second line shows the branch's restore removes the field. That is step 6's check, done on a real backup.
- Keep the `counts` lines: they are the "before" for the database upgrade.
- **This backup is the safety net for everything else.** It still holds the field if the database does, so it isn't "clean" for the field yet. Step 7 makes the clean one.

### 2. Run the aggregate count-only query

```powershell
python -m brain.foodfield count --database-url $env:ODYS_DB
```

**Expected:** one line, `profiles N, with_key K, non_empty M`. N should equal step 1's N, unless someone installed in between.

<details><summary>The same count in <code>psql</code>, if you prefer it</summary>

```sql
SELECT count(*) AS profiles,
       count(*) FILTER (WHERE profile::jsonb ? 'foods_avoided') AS with_key,
       count(*) FILTER (WHERE coalesce(profile::jsonb ->> 'foods_avoided', '') <> '') AS non_empty
FROM users;
```

</details>

### 3. Report only the number of affected records

- Send Claude the one line from step 2. Nothing else: no value, no length, no user.
- **If `with_key` is 0, skip to step 7.**

### 4 and 5. Remove only the `foods_avoided` key, in a controlled transaction

```powershell
python -m brain.foodfield delete --database-url $env:ODYS_DB --confirm delete
```

**Expected:**

```text
before: profiles N, with_key K, non_empty M
updated K profiles (the foods_avoided key only)
after:  profiles N, with_key 0, non_empty 0
COMMITTED
```

- It runs in **one transaction**. It counts again inside it, and commits only if `with_key` is 0. No user record is deleted.
- **If it prints `ROLLED BACK`** (exit code 2), nothing was changed. Send Claude the lines and stop there.
- **Without `--confirm delete`** it changes nothing.

<details><summary>The same in <code>psql</code></summary>

```sql
BEGIN;
UPDATE users SET profile = (profile::jsonb - 'foods_avoided')::json WHERE profile::jsonb ? 'foods_avoided';
-- psql answers "UPDATE K"
SELECT count(*) FILTER (WHERE profile::jsonb ? 'foods_avoided') AS with_key FROM users;
-- 0: COMMIT;   anything else: ROLLBACK; and tell Claude the numbers
```

</details>

### 6. Verify that the count becomes zero

```powershell
python -m brain.foodfield count --database-url $env:ODYS_DB
```

**Expected:** `profiles N, with_key 0, non_empty 0`. Send Claude this line, and step 4's `updated K`.

### 7. Check that old backups and restores can't bring it back

1. Run `ops` → `backup` again. Then:

```powershell
python -m brain.backup count-food <the new .odysbk> --key <key> --after-restore
```

2. **Expected:** both lines show `with_key 0`. **This is the clean replacement backup.**

| Route back | What stops it | Your check |
|---|---|---|
| **Older backup artifacts** (before the delete) | They expire within 30 days | Delete them only after the clean one exists, if at all. They are the study's only off-Render copies (m234) |
| **A restore** | The branch's `restore` removes the field (tested; step 1's second line shows it on a real backup). **Main's doesn't** | Restore only with the branch's command. After any restore: steps 2–6 again |
| **Render's point-in-time recovery** (only after a paid upgrade) | Doing this procedure **before** the upgrade means no recovery point holds the field | If the order changes: after any recovery, steps 2–6 again |
| **Phones on build 91 or Android 21** | Main stores the field again when an old phone saves a profile | **Step 2 once a week** until the branch Brain is live; steps 4–6 if it's back |
| **`backup.json` on your computer** | Not needed any more | Delete any you opened before |

### At the end

```powershell
Remove-Item Env:ODYS_DB
```

Then remove your IP address from the database's Networking in Render. The downloaded `.odysbk` files are sealed to your key: keep them somewhere private, or delete them.

**Never:** export, print, log, copy or quote a value, not even its length. Every command here reports counts only, and the tests check that a value never reaches the screen.

## Two separate checks (Abram, m260)

| | **The evidence: the database and backup counts** | **The monitoring: the old-app counter** |
|---|---|---|
| What | Step 2's query, and `count-food` on a backup | `old_app_saves_dropped_since_start` in `GET /v1/admin/audit/foods-avoided` (m257) |
| Where | The live database today (main); any backup | **Only on the branch Brain**, so not before it's deployed |
| What it shows | How many stored profiles hold the field now | How many profile saves from old apps carried the field since the server last started |
| Its limit | A point in time: an old app can send it again later (step 7) | **It resets on every restart** (the free server sleeps after 15 minutes). A 0 means "none since the restart", **never** "the database is clean" |
| Used for | Saying the field is gone | Spotting old apps still sending it, so step 2 is re-run |

**The counter is never cited as evidence that the database holds no values.** Only step 2's count (and `count-food` for a backup) is.

## After the branch Brain is deployed (after the round)

- `GET /v1/admin/audit/foods-avoided` (the admin token in an environment variable) gives the same three numbers, and the counter.
- `POST /v1/admin/audit/foods-avoided/delete` with `{"confirm": "delete"}` does steps 4–6 in one call and answers with the counts before and after. It refuses without the confirmation.
- A profile save can't store the field any more, so the weekly count can stop after one zero.

## Checks

`brain/tests/test_foods_avoided_audit.py`, 7 tests:
- the audit is admin-only and gives counts. A synthetic value is in neither the response nor the logs, at any log level;
- the delete is admin-only, refuses without `{"confirm": "delete"}`, keeps the rest of the profile, is safe to run twice, and never echoes the value;
- a new backup has no value, and restoring an "older" backup that has one gives a profile without it;
- **`count-food` (m266)** counts a sealed backup made on main (a dict profile, a JSON-text profile, an empty one), refuses without the key, shows only the three numbers, and writes nothing to disk;
- **`foodfield` (m271)** counts, refuses to delete without `--confirm delete`, removes only the key, keeps every record and the rest of each profile, and prints no value;
- **`foodfield` rolls back** when the count doesn't reach 0, leaving the database as it was (m271);
- **`count-food --after-restore` and `counts` (m271, m272)** restore a backup made on main in memory, show `with_key 0` after the restore, print table counts only, and write nothing to disk.

Also:
- **On PostgreSQL 16.15** (a throwaway local server, synthetic rows only, deleted after): both routes and both SQL statements agree (9 Nov). **On 19 Nov**, with main's own `users` table: `foodfield` and the SQL count agreed (4, 2, 1); the delete committed, removed only the key, created no table, and the count after was 0.
- The guard from m223 still holds: `test_food_needs_are_never_stored_until_their_dpia`.

**Hours:**
- **Claude:** ~1.5 h (m233), plus 0.5 h for this procedure and `count-food` (m266), plus ~1 h for `foodfield`, the restore check and the exact commands (m271).
- **Abram:** ~30 min for the seven steps; then step 2 weekly (~5 min) until the branch Brain is live.
