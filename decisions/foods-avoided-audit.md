# The old free-text food field: a count-only audit and a deletion plan (9 Nov 2026; m233)

**Decision (Abram, m224): count it, delete any that exist, make sure a backup can't bring it back, and never export or share the contents.** The code is built and tested on the branch. **Nothing has been run against the live Brain:** this session has no access to it, and the release rules (no deploys during the round) apply. The count and the deletion are Abram's to run, below.

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
| **A backup opened on Abram's computer** (`backup.json`) | The README already says to delete it after reading | — |

## The audit (counts only)

**Now, on the live database** (main has no audit route). In the database's shell (`psql`), run:

```sql
SELECT count(*) AS profiles,
       count(*) FILTER (WHERE profile::jsonb ? 'foods_avoided') AS with_key,
       count(*) FILTER (WHERE coalesce(profile::jsonb ->> 'foods_avoided', '') <> '') AS non_empty
FROM users;
```

- It returns three numbers and never a value.
- **Tested on PostgreSQL 16.15** with synthetic rows: it gave 4, 2 and 1, the same as the audit route.
- **Don't look up the values to check:** the numbers are enough.

**After the branch Brain is deployed** (after the round): `GET /v1/admin/audit/foods-avoided`, with the admin token in an environment variable. It answers `{"profiles": n, "with_key": k, "non_empty": m}` and logs the same three numbers.

## The deletion (approved by Abram, m224, if any exist; destructive, so Abram runs it)

1. **If `with_key` is 0, stop.** There's nothing to delete. Re-run the count once after the branch is deployed.
2. **Otherwise delete it now, in one transaction:**
   ```sql
   BEGIN;
   UPDATE users SET profile = (profile::jsonb - 'foods_avoided')::json WHERE profile::jsonb ? 'foods_avoided';
   -- then the count above again: with_key must be 0
   COMMIT;
   ```
   The update removes only that key and keeps the rest of each profile. **Tested on PostgreSQL 16.15** on a copy with synthetic rows: 2 rows updated, then 0 with the key, every other key kept.

   After the deploy, the same deletion is `POST /v1/admin/audit/foods-avoided/delete` with `{"confirm": "delete"}`. It answers with the counts before and after, and refuses without the confirmation.
3. **Until the branch Brain is live, re-run the count weekly.** An old build can send the field again (the table above). If it comes back, delete it again. Once the branch Brain is deployed, a profile save can't store it.
4. **Backups.**
   - Backups made after the deletion don't hold it.
   - The older ones expire within 30 days.
   - To close that window sooner, Abram can delete the older artifacts in GitHub Actions. That's his choice: they are also the study's only off-Render copies.
   - **First make sure a clean replacement exists** (Abram, m234). After the deletion, let the next nightly backup run, or run it by hand from the ops workflow, and check that it succeeded. Open it with Abram's key and run the same count on it: `with_key` must be 0. Only then delete older artifacts, if at all.
   - **Any restore must use the branch's restore command,** which strips the field. A restore with main's command, or the 6 Dec database swap (README) done before the branch is live, is followed by the count, and by the deletion if needed.
5. **Never:** export, print, log, copy or quote a value, not even its length. The audit and the delete only ever report counts (tested).

## Checks

- `brain/tests/test_foods_avoided_audit.py`, 3 tests:
  - the audit is admin-only and gives counts. A synthetic value is in neither the response nor the logs, at any log level.
  - the delete is admin-only, refuses without `{"confirm": "delete"}`, keeps the rest of the profile, is safe to run twice, and never echoes the value.
  - a new backup has no value, and restoring an "older" backup that has one gives a profile without it.
- **On PostgreSQL 16.15** (a throwaway local server, synthetic rows only, deleted after): both routes and both SQL statements agree.
- The guard from m223 still holds: `test_food_needs_are_never_stored_until_their_dpia`.

**Hours:** Claude ~1.5 h. Abram: the count (~5 min), and the deletion if any exist (~5 min), then the weekly re-count until the deploy.
