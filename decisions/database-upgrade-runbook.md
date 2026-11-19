# The database upgrade: a runbook for Abram's final confirmation (19 Nov 2026)

Abram's decision of 19 Nov, §1: approved in principle. **Nothing is bought or changed until Abram has seen the exact configuration and the backup evidence, and given his final confirmation (step 5).** The steps follow his order: export, verify, restore test, configuration, upgrade, read/write check, keep a copy.

**The deadline:** the live database (`london-places-swipe-db`, created 6 Nov) expires on **6 Dec 2026**. Render then allows 14 days to upgrade, and after that "deletes the database (along with all of its data)" (render.com/docs/free.md, read 16 and 19 Nov). **The target is to finish by 3 Dec**, leaving three days' margin.

## The exact configuration (for his confirmation)

| | Today | After |
|---|---|---|
| Database | `london-places-swipe-db`, Render Postgres, plan `free`, Frankfurt | **the same database**, plan **`0.1c-256mb`** (0.1 CPU, 256 MB RAM, 100 connections) |
| Price | $0 | **$6 a month + $0.30 per GB a month** (render.com/pricing.md, 16 Nov); 1 GB = $6.30, before VAT |
| Backups | ours only (nightly, sealed, 30 days) | ours, plus Render's: point-in-time recovery for **3 days** (Hobby workspace) and logical backups kept **7 days** (render.com/docs/postgresql-backups.md) |
| Postgres version, region, name | 18, Frankfurt, unchanged | unchanged: a plan change, not a new database |
| Brain server (`moments-brain`) | plan `free`, 0.1 CPU | **`1c-2g`, $25 a month**, for the round (Abram, 19 Nov §2) |
| Monthly total | $0 | **about $31.30 before VAT** |

**Two things Render's pages don't say (read 19 Nov), so the plan doesn't rely on them:**
- **Whether a plan change keeps the data.** The plan change page says only that the database "will be unavailable temporarily during the change … for a few minutes" (render.com/docs/postgresql-creating-connecting.md). Hence step 3, a proven restore, before step 6.
- **Whether its connection address changes.** Step 7 checks that the Brain still connects.

**`render.yaml` says `plan: free` for both, and Render's Blueprint sync "overwrites" dashboard changes that conflict with it** (render.com/docs/infrastructure-as-code.md, 19 Nov).
- **When a sync runs:** on a push to `main` that changes `render.yaml`, or a manual sync.
- **During the round nothing touches `render.yaml`,** so nothing reverts.
- **Two safeguards, for Abram to choose:**
  - (a) turn **Auto Sync off** on the Blueprint's settings page, before the upgrade;
  - and/or (b) make the first post-round change to `render.yaml` set `plan: 0.1c-256mb` (database) and `plan: 1c-2g` (Brain), the plan IDs in render.com/docs/blueprint-spec.md.
- Claude prepares (b) on the development branch when Abram says.

## Who does what

**Abram** does every step that touches Render, money or the live database. **Claude** prepares, reads the outputs and checks.

| # | Step | Who | When | Done when |
|---|---|---|---|---|
| 1 | **Final export.** `GET /v1/admin/export` with the admin token, saved as `validation/raw/export-2026-11-29.json` (git-ignored, never committed) | Abram | 29 Nov, after the round's last tester | the file exists |
| 2a | **Check the export on its own.** `python brain/scripts/export_counts.py validation/raw/export-2026-11-29.json` | Abram (Claude reads the counts) | 29 Nov | it prints each table's count and "Holds together." |
| 2b | **A fresh sealed backup.** GitHub → Actions → `ops` → Run workflow → `backup`; download the artifact | Abram | right after 2a | the job is green and the file is on his computer |
| 2c | **Check the backup.** `python -m brain.backup verify <file> --key <his private key>` | Abram | right after 2b | "Whole and consistent.", and **its counts equal step 2a's** (two separate paths out of the same database) |
| 3 | **Prove the backup restores.** Into a scratch database on his own computer, never Render: `python -m brain.backup restore <file> --key <key> --database-url <scratch URL>` (a local Postgres, or `sqlite:///restore-test.db`); then compare the "Restored:" counts with 2a | Abram (Claude writes the exact commands for his machine) | 29–30 Nov | **"Restored:" counts equal 2a's** |
| 4 | **Keep recoverable copies of the original data.** The sealed backup from 2b, plus the export from step 1, each in **two places he controls** (his computer, and an encrypted drive or password-manager attachment). The GitHub artifact also lasts 30 days | Abram | 30 Nov | two copies of each |
| 5 | **His final confirmation**, after reading this table's evidence: the counts from 2a, 2c and 3, and the configuration above | **Abram** | by 1 Dec | he says "go" |
| 6 | **The upgrade.** Render → `london-places-swipe-db` → change plan to `0.1c-256mb`; confirm the price Render shows. Then `moments-brain` → plan `1c-2g`, **only if the round hasn't started**: the server should be the same for every tester | Abram | 1–3 Dec, at night, nobody mid-onboarding | Render shows "Available" |
| 7 | **Read and write check.**<br>• `GET /v1/health` gives `ok` and `version` `80a0da3` (or the approved privacy commit).<br>• A new export's counts equal 2a's.<br>• One write: an install with the code `REHEARSAL`, a plan and a rating, then "Delete my data", so nothing is left.<br>• The ops workflow's next uptime and backup runs are green | Abram, Claude reads the outputs | right after 6 | all four hold |
| 8 | **If anything fails:** see the next section | both | — | — |

**For the swipe page:** it shares the database, so steps 6–7 also cover it. Open `london-places-swipe….onrender.com` once after step 6.

## If something goes wrong

| What | Do |
|---|---|
| Step 2c or 3 fails | Don't upgrade yet. Take another backup (2b) and try again. If it fails twice, Claude investigates before anything else changes |
| The database comes back after step 6 but the counts differ | Render's point-in-time recovery to just before the change (now available on the paid plan) |
| The data is missing after step 6 | A new paid database (`0.1c-256mb`), then step 3's restore into it from the 2b backup, outside access blocked, and the services pointed at its Internal URL. This is the 6 Nov procedure (`brain/README.md`). **Anyone who deleted their data after 2b would come back with it:** the live Brain doesn't keep deletion records yet (SEC-10), and its logs show that a "Delete my data" happened (`DELETE /v1/me`), not who did it. **So run 2b to 6 within the same hour, at night, after the round's last tester.** If the log shows a deletion after 2b, don't restore that backup: take a fresh one first, if the database is still readable |
| It's 5 Dec and not done | Upgrade anyway, after 2b alone: an unverified backup is better than none, and a paid plan in time keeps the data |

## Hours

- **Abram:** about 1.5 h over 29 Nov – 3 Dec.
- **Claude:** about 1 h to read the counts and check step 7. `export_counts.py` and this note are done.
