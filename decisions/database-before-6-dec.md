# The database before 6 December (12 Nov 2026; m266): a decision for Abram

**The problem:** the live Brain's free Render Postgres database (created 6 Nov, `brain/README.md`) **expires on 6 Dec 2026**.
- Render's docs, read 12 Nov: "Free Render Postgres databases expire 30 days after creation". Then "a grace period of 14 days to upgrade it to a paid compute plan", after which "Render **deletes** the database (along with all of its data)" (https://render.com/docs/free).
- Free databases also "don't support any form of backups".
- **The friends' round's data lives in it.** Nothing is bought or moved without Abram's approval.

## Recommendation: upgrade the existing database in place to Render's smallest paid Postgres plan, after the round's final export

| | |
|---|---|
| **Provider** | Render, where the Brain already runs. No new data processor, so the privacy notice is unchanged, and there's no migration to get wrong |
| **Plan** | The smallest paid Postgres compute plan, `0.1c-256mb` (legacy name `basic-256mb`): 0.1 CPU, 256 MB RAM, 100 connections (https://render.com/docs/compute-plans, read 12 Nov) |
| **Monthly cost** | **About $6 a month plus storage at $0.30 per GB, as recorded on 9 Oct** (`roadmap.md`). **UNVERIFIED today:** Render's pricing page loads its figures in the browser, so the fetch couldn't read them. **Abram checks the price on https://render.com/pricing before upgrading.** With 1 GB, about $6.30 a month |
| **Backups** | (1) Render's point-in-time recovery for paid databases: "Past 3 days" on the Hobby workspace plan, 7 on Pro (https://render.com/docs/postgresql-backups, read 12 Nov). (2) **Our own nightly sealed backups continue unchanged** (`ops.yml`, kept 30 days, only Abram's key opens them) |
| **When** | **After the round's final export (29 Nov) and before 6 Dec**, because changing the plan means "brief downtime" (https://render.com/docs/compute-plans). If Abram wants the round to run past 29 Nov, upgrade **before** it starts instead, and accept a minute's downtime before any invite |
| **The web service** | Not needed for the expiry. The free service sleeps after 15 minutes (a short wait, which the rehearsal checks). Upgrading it (about $7 a month as recorded on 9 Oct, UNVERIFIED today) is separate, and optional |

## The process (Abram, about 20 minutes; Claude checks after)

1. **A fresh sealed backup first.** GitHub → Actions → `ops` → Run workflow → `backup`. Check the job succeeded and kept `odys-brain-backup-…`. No page read on 12 Nov says an upgrade keeps the data, so this backup is the safety net.
2. Render → the database (`london-places-swipe-db`) → **Upgrade** (or Change plan) → the smallest paid Postgres plan. Confirm the price shown.
3. Wait for "Available". Then Claude checks `/v1/health` and that a planning request works. The export's counts must match the last export.
4. **If anything is wrong: the recovery plan below.**

## The recovery plan

- **The data is there but something's off:** Render's point-in-time recovery to before the change (paid plans; 3 days on Hobby).
- **The data is missing:** create a new database. Then run `python -m brain.backup restore <sealed file> --key <Abram's private key> --database-url <External URL>` from the backup in step 1. Block outside access under Networking, and point both services' `…_DATABASE_URL` at the new Internal URL (as done on 6 Nov, `brain/README.md`).
- **After either:** the count-only food audit (`foods-avoided-audit.md`). A restored backup could hold old rows (backups from `main` don't strip that field).

## The alternatives (read 12 Nov 2026)

| Option | Cost | Backups | Why not first |
|---|---|---|---|
| **The free swap again** (delete, new free database, restore) | £0 | None from Render ("don't support any form of backups"); ours only | It expires again 30 days later (about 5 Jan); a monthly chore and a monthly risk |
| **Neon** (https://neon.com/pricing) | Free plan "permanent (not a trial)", 1 GB per project, not paused for inactivity. Launch: pay as you go, $0.106 per CU-hour, $0.35 per GB-month; its "intermittent load" example is $15 a month | A 6-hour history window on Free | A new processor (privacy notice), a migration, and its region not checked |
| **Supabase** (https://supabase.com/pricing) | Free: 500 MB, "paused after 1 week of inactivity". Pro "from $25/month" | Pro: "daily backups stored for 7 days" | Pausing on Free; Pro costs more; a migration |
| **Hetzner Cloud** (compared 9 Oct, `roadmap.md`) | from €5.99 (Abram's screenshot, 9 Oct) | Ours to run | Abram would run the server, database, backups and security updates |

## Required founder action

1. **Decide:** upgrade in place (recommended), or one of the alternatives.
2. **Check the price** on Render's pricing page; add a card if Render asks.
3. **When:** after the final export (by 29 Nov), or before the round if it should run longer.
4. **Run steps 1–2.** Claude checks step 3.

**Payments to anyone else stay off** (Abram, m260: "Do not start payment integration yet").
