# The database before 6 December: the plan for Abram's final confirmation (19 Nov 2026; m266, m288)

**Status:**
- Abram provisionally approved upgrading the existing Render database in place (19 Nov).
- **Nothing is bought, and the production database isn't touched, until his final confirmation.**
- Payments to anyone else stay off.

**The deadline** (Render, https://render.com/docs/free, read 19 Nov):
- The free database `london-places-swipe-db` was created on 6 Nov. Free databases "expire 30 days after creation", so this one **expires on 6 Dec**.
- "An expired Free database is inaccessible unless you upgrade it to a paid compute plan."
- After "a grace period of 14 days" (about 20 Dec), "Render deletes the database (along with all of its data)".
- **Plan the upgrade for 2 Dec at the latest** (Abram: "Do not leave the upgrade until 5 December").

## The recommendation

Upgrade `london-places-swipe-db` in place, from Free to **Basic-256mb**, in the Hobby workspace. **About $6.30 a month** (£4.79), or $7.56 (£5.75) if Render adds UK VAT.
- The pricing page calls the plan "Basic-256mb". Render's docs and the audit call it `0.1c-256mb`. It's the same plan: 0.1 CPU, 256 MB RAM, $6 a month.

**When:** before the first friends' invite (option B below), or after the final export is checked, by 2 Dec at the latest.

**This page is the database only**, because that's the 6 Dec deadline.
- **The server is a separate decision:** the audit's `infrastructure-decision.md` (m278, prices read 16 Nov). It recommends 1 CPU ($25) for the planner, or 0.5 CPU ($7) once the planner fix exists.
- Both pages agree on the database: in place, $6 plus $0.30 per GB, the same steps.
- Today's prices (19 Nov) match the audit's of 16 Nov.

## 1. Current official Render pricing (render.com/pricing, read 19 Nov 2026 from the page's own data)

| Item | Price | Notes |
|---|---|---|
| Postgres **Free** (today) | $0 | "30-day limit"; 0.1 CPU, 256 MB RAM, 100 connections |
| Postgres **Basic-256mb** (recommended) | **$6/month** | 0.1 CPU, 256 MB RAM, 100 connections: the same size as today |
| Postgres Basic-1gb (the next size) | $19/month | 0.5 CPU, 1 GB RAM; not needed |
| Postgres storage | **$0.30 per GB** | "Expandable storage ($0.30/GB)". The page doesn't repeat "per month" on this row; disks beside it say "per GB per month" |
| Workspace **Hobby** (ours) | **$0/month + compute** | Its listed features include "Database PITR" (a 3-day window) and chat support |
| Workspace Pro | $25/month | 7-day recovery window; not needed |
| Web service `0.5c-512mb` / `1c-2g` (separate) | $7 / $25 a month | The server decision is `infrastructure-decision.md` (m278). Not needed for the deadline |
| Billing | prorated | "billing is prorated to the second" (Render's FAQ on the same page) |

The 12 Nov fetch couldn't read these prices, because the page builds them in the browser. Today they were read from the page's own data: the Postgres table row "Basic | Basic-256mb | $6/month | 0.1 | 256 MB | 100 connections".

## 2. The exact configuration

| | Now | After the upgrade |
|---|---|---|
| Name | `london-places-swipe-db` (both services use it) | the same, with the same URLs |
| Region | Frankfurt (`render.yaml`; EU data location) | the same |
| Compute | Free: 0.1 CPU, 256 MB RAM, 100 connections | **Basic-256mb**: the same |
| Storage | 1 GB, fixed (free databases) | **1 GB.** Paid storage is "1 GB or any multiple of 5 GB" and can only grow. **Check the storage line before saving:** the docs don't say what an upgraded free database gets |
| Storage autoscaling | — | **On** (recommended): at 90% full it grows by 50%, rounded up to 5 GB (+$1.20 a month, only if it happens). A full database stops taking answers |
| PostgreSQL version | **Abram reads it** on the database's Info page (Claude can't see the dashboard) | unchanged |
| Access from the internet | none (`ipAllowList: []`) | unchanged |
| Render's backups | **none** ("don't support any form of backups") | point-in-time recovery for 3 days, plus logical exports kept 7 days |
| Our backups | nightly, sealed to Abram's key, kept 30 days (`ops.yml`) | unchanged |

**`render.yaml` still says `plan: free`.** That's harmless while Blueprint Auto Sync is off (since 6 Nov). **Don't run a Blueprint sync** until `render.yaml` on `main` says `basic-256mb`, which happens after the round, since nothing changes on `main` during it.

## 3. Monthly storage allowance

- **1 GB.** There's no free allowance: each GB set is paid for.
- **Our data is far smaller.** The nightly sealed backup of every table is 57 KB compressed (19 Nov). PostgreSQL's own overhead comes on top of that; the dashboard shows the total used.

## 4. Expected storage charges

| Storage | Per month |
|---|---|
| 1 GB (expected) | **$0.30** |
| 5 GB (only if autoscaling ever triggers) | $1.50 |

## 5. Backup and restoration

| What | Covers | Limit |
|---|---|---|
| **Render point-in-time recovery** | Any moment in the past 3 days (Hobby) | **Only from the upgrade on.** The free database has no backups, so nothing from before the upgrade can be recovered this way. A recovery "spins up a new database instance", which is billed while it exists |
| **Render logical backups** | A downloadable dump, made on demand in the dashboard | Kept 7 days; paid databases only |
| **Our sealed backups** (`ops.yml`) | Every table, nightly, plus on demand | 30 days; only Abram's key opens them. Restoring one with the branch's `restore` command was proven on 6 Nov, and it removes the old food field |

**Before the upgrade, ours are the only copies.** That's why the procedure starts with a fresh one and checks it.

## 6. The procedure (Abram; about 40 minutes; Claude checks the result)

0. **The old food field first** (`foods-avoided-audit.md`, ~30 minutes). Done before the upgrade, no Render recovery point can ever hold the field.
1. **A fresh sealed backup.** Actions → `ops` → Run workflow → `backup`. Download it and run (PowerShell, from `brain/` on the work branch, with `$env:PYTHONPATH = "src"`):
   ```powershell
   python -m brain.backup counts <odys-brain-YYYYMMDD.odysbk> --key <your private key>
   ```
   **Expected:** `made_at …`, then one line per table with its number of rows. **Keep these lines: they are the "before".**
2. **The export, checked independently.** Download the admin export as usual (the admin token stays in your PowerShell window). Then:
   ```powershell
   python scripts\export_counts.py ..\validation\raw\export-<date>.json
   ```
   **Expected:** the same tables with the same counts as step 1. A difference of a few rows is fine only if someone used the app between the two. **If any table is short, stop and tell Claude.**
3. **The upgrade.** Render → `london-places-swipe-db` → Plan → Compute → Edit → **Basic-256mb**.
   - Check that it shows $6/month and storage 1 GB.
   - Turn Storage Autoscaling on.
   - Save, and add a card if asked (Render checks it with a $1 charge it refunds).
4. **Wait for "Available"** (a few minutes).
5. **Checks:**
   - **Claude:** `/v1/health` answers `"ok":true` and `"version":"80a0da3"`.
   - **Abram:** a new sealed backup (`ops` → `backup`), then `counts` on it. **Every table must match step 1.**
   - **Abram:** in the database's dashboard, trigger one logical backup (Render's docs: "Trigger a backup"), as an extra copy kept 7 days.
6. **Record it** in `validation/friends-round.md` ("the database moved to Basic-256mb on …"). This isn't a deploy: the Brain's code and settings don't change.

## 7. Downtime

- Render: "Your database will be unavailable temporarily during the change… Otherwise, it's unavailable for a few minutes." There's no high availability on this plan (https://render.com/docs/postgresql-creating-connecting, read 19 Nov).
- **During those minutes** the apps can't save. They show their usual connection message, and a stop rating waits on the phone (build 91's offline behaviour).
- **When:** an evening when no tester is mid-onboarding, and not while `ops` is running. The nightly backup is scheduled for 02:23 UTC but has run between about 07:00 and 10:30 UTC lately. Before the round (option B), nobody is affected at all.

## 8. If the upgrade fails

| What happens | What to do |
|---|---|
| **The change stalls or errors** | The free database and its data stay as they were until 6 Dec, with the grace period to about 20 Dec. Contact Render support (chat is included on Hobby). Try again the next day |
| **It finishes, but rows are missing** (step 5's counts differ) | **Render's recovery can't help:** it only reaches back to the upgrade. Restore from step 1's backup:<br>(a) create a new Basic-256mb database in Frankfurt;<br>(b) run `python -m brain.backup restore <step 1's file> --key <key> --database-url <its External URL>`;<br>(c) block outside access under its Networking;<br>(d) point both services' `…_DATABASE_URL` at its Internal URL;<br>(e) Claude checks `/v1/health` still answers `80a0da3`;<br>(f) `counts` on a new backup matches step 1.<br>Changing the environment variable redeploys `moments-brain` on `main`, which is still `80a0da3`. So the version doesn't change, but it's the one exception to "no settings change" during the round, so record it. The extra database is billed only while both exist (prorated) |
| **The app misbehaves after it** | Same as above if the data is wrong. If the data is right, it isn't the database: send Claude the time and the screen |

## 9. The exact total cost

| | Per month | Per month in £ (ECB, 19 Nov: $1 = £0.7604) |
|---|---|---|
| Basic-256mb | $6.00 | £4.56 |
| Storage, 1 GB | $0.30 | £0.23 |
| Hobby workspace | $0.00 | £0.00 |
| **Total before tax** | **$6.30** | **£4.79** |
| **If Render adds UK VAT at 20%** (GOV.UK standard rate) | **$7.56** | **£5.75** |

- **VAT is UNVERIFIED.** Render's terms say only "You will pay any applicable taxes, if any" (https://render.com/terms, read 19 Nov). No Render page found says whether UK VAT is added to an individual's invoice. Abram sees it on the first invoice. Budget for $7.56.
- Abram's card issuer may add a foreign-transaction fee on dollar charges. Not known here.
- **December to February:** about $19 (£14), or $23 (£17) with VAT. Prorated for a part month.
- **Not included:** the server (`infrastructure-decision.md`: $25 a month at 1 CPU, or $7 at 0.5 CPU after the planner fix; with it, the audit's totals are $31.30 or $13.30) and the Pro workspace ($25/month).

## Compared with the alternatives (researched 12 Nov; prices as read then)

| Option | Monthly cost | Migration | Backups | Privacy notice | Main risk |
|---|---|---|---|---|---|
| **Render Basic-256mb, upgraded in place** (recommended) | **$6.30** (+VAT?) | None | 3-day recovery + exports + ours | Unchanged | A few minutes' downtime |
| The free swap again (delete, new free, restore) | £0 | A restore every month | Ours only | Unchanged | It expires again about 5 Jan: a monthly chore and a monthly risk |
| Neon (https://neon.com/pricing) | Free plan "permanent", 1 GB; Launch about $15 typical | Export, restore, two URL changes | 6-hour history (Free) | **A new processor to add** | A migration during or near the round; region not checked |
| Supabase (https://supabase.com/pricing) | Free pauses after a week idle; Pro from $25 | As Neon | Pro: daily, 7 days | A new processor | Pausing; cost |
| Hetzner Cloud (`roadmap.md`, 9 Oct) | from €5.99 | A server to build | Ours to run | A new processor | Abram runs the server, updates and security |

## The decision on timing (Abram)

**The round hasn't started yet** (19 Nov). The tag, the rehearsal, Apple's check and TestFlight's review are still ahead.

- **Option A (the plan as written):** the round's final export on 29 Nov, checked, then the upgrade by 2 Dec. If invites go out around 22 Nov, **the round gets about a week**.
- **Option B (recommended):** upgrade **before the first invite**, after the food steps and a checked export of today's data (Abram's 15 test installs).
  - The round then has **no database deadline**, nobody is affected by the downtime, and nothing moves while friends' answers are in the database.
  - "Completed and independently checked before migration" still holds: steps 1–2 are exactly that, on the data that exists then.
  - The round's own final export simply comes at its end.

## Required founder action

1. **Choose the timing:** A or B (B recommended).
2. **Confirm the purchase:** Basic-256mb at $6/month plus 1 GB at $0.30, in the Hobby workspace (about $6.30, or $7.56 with VAT).
3. **Read the PostgreSQL version and storage used** from the dashboard, and send them to Claude.
4. **Run the steps:** the food steps, then steps 1–5, by 2 Dec at the latest. Claude checks step 5.
