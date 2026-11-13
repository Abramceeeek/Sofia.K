# The old free-text food field: a count-only audit and a deletion plan (9 Nov 2026; m233, m266)

**Decision (Abram, m224, confirmed m260): count it, delete any that exist, make sure a backup can't bring it back, and never export or share the contents.**
- The code is built and tested on the branch.
- **Nothing has been run against the live Brain.** This session has no access to the database. Abram, m260: "Do not attempt to access the production database using an admin token or another workaround."
- **An authorised operator (Abram) runs the seven steps below**, about 30 minutes.
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

## The operator procedure (Abram's seven steps, m260)

**Before you start:**
- Use a terminal on your own computer, with this branch checked out (`claude/vigilant-cannon-my82dj`) and its Python 3.12 environment. This only runs the branch's backup tool locally; nothing is deployed.
- **Connect to the database with `psql`**, using its External URL (Render → `london-places-swipe-db` → Connect). If outside access is blocked under the database's Networking, allow your own IP address for this session only, and remove it at the end.
- **Never run a query that selects `profile`** or the field itself. Every command below returns only numbers.

### 1. Verify a clean replacement backup

- GitHub → Actions → `ops` → Run workflow → `backup`. Check the job succeeded and kept `odys-brain-backup-<run id>`.
- Download it and check that it opens, on your computer:
  ```text
  python -m brain.backup count-food <the downloaded file> --key <your private key>
  ```
  It prints one line, such as `profiles 23, with_key 1, non_empty 1`, and nothing else. It opens the backup in memory and writes nothing to disk (tested).
- **This backup is the safety net for everything else in the database.** It still holds the field if the database does, so it isn't yet "clean" for the field. Step 7 makes the clean one.

### 2. Run the aggregate count-only query

In `psql`:

```sql
SELECT count(*) AS profiles,
       count(*) FILTER (WHERE profile::jsonb ? 'foods_avoided') AS with_key,
       count(*) FILTER (WHERE coalesce(profile::jsonb ->> 'foods_avoided', '') <> '') AS non_empty
FROM users;
```

It returns three numbers and never a value (tested on PostgreSQL 16.15 with synthetic rows: 4, 2 and 1).

### 3. Report only the number of affected records

- Send Claude the three numbers: `profiles`, `with_key`, `non_empty`. Nothing else: no value, no length, no user.
- **If `with_key` is 0, skip to step 7.**

### 4. If any values remain, remove only the `foods_avoided` JSON key

### 5. Use a controlled transaction

Steps 4 and 5 are one block in `psql`:

```sql
BEGIN;
UPDATE users SET profile = (profile::jsonb - 'foods_avoided')::json WHERE profile::jsonb ? 'foods_avoided';
-- psql answers "UPDATE n": n must equal step 2's with_key
SELECT count(*) FILTER (WHERE profile::jsonb ? 'foods_avoided') AS with_key FROM users;
-- 0: type COMMIT;   anything else: type ROLLBACK; and tell Claude the numbers
```

- The update removes only that key; the rest of each profile stays (tested on PostgreSQL 16.15: 2 rows updated, then 0 with the key, every other key kept).
- Nothing is saved until `COMMIT`. `ROLLBACK` leaves the database as it was.

### 6. Verify that the count becomes zero

- After `COMMIT`, run step 2's query again: `with_key` and `non_empty` must both be 0.
- Report the `UPDATE n` figure and the new three numbers to Claude.

### 7. Check that old backups and restores can't bring it back

| Route back | What stops it | Abram's check |
|---|---|---|
| **The next backup** | Taken after step 6, it reflects the cleaned database | Run `ops` → `backup` again, then `count-food` on it: `with_key 0`. **This is the clean replacement backup** |
| **Older backup artifacts** (before the delete) | They expire within 30 days | Delete them only after the clean one exists, if at all: they are the study's only off-Render copies (m234) |
| **A restore** | The branch's `restore` strips the field (tested). **Main's doesn't** | Restore only with the branch's command. After any restore, steps 2–6 again |
| **Render's point-in-time recovery** (after a paid upgrade) | A recovery to before step 6 brings it back | After any recovery, steps 2–6 again. The window closes 3 days after the delete (Hobby) |
| **Phones on build 91 or Android 21** | Main stores the field again on a profile save | **Step 2 once a week** until the branch Brain is live; steps 4–6 if it's back |
| **`backup.json` on your computer** | Not needed with `count-food` | Delete any you opened before |

**Finally:** remove your IP address from the database's Networking if you added it.

**Never:** export, print, log, copy or quote a value, not even its length. The SQL, `count-food`, the audit route and the delete route only ever report counts (tested).

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

`brain/tests/test_foods_avoided_audit.py`, 4 tests:
- the audit is admin-only and gives counts. A synthetic value is in neither the response nor the logs, at any log level;
- the delete is admin-only, refuses without `{"confirm": "delete"}`, keeps the rest of the profile, is safe to run twice, and never echoes the value;
- a new backup has no value, and restoring an "older" backup that has one gives a profile without it;
- **`count-food` (m266)** counts a sealed backup made on main (a dict profile, a JSON-text profile, an empty one), refuses without the key, shows only the three numbers, and writes nothing to disk.

Also:
- **On PostgreSQL 16.15** (a throwaway local server, synthetic rows only, deleted after): both routes and both SQL statements agree.
- The guard from m223 still holds: `test_food_needs_are_never_stored_until_their_dpia`.

**Hours:**
- **Claude:** ~1.5 h (m233), plus 0.5 h for this procedure and `count-food` (m266).
- **Abram:** ~30 min for the seven steps; then step 2 weekly (~5 min) until the branch Brain is live.
