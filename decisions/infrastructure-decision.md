# Infrastructure before 6 December: the database, the server and what they cost (16 Nov 2026)

Abram's review of the audit, part 1 (12 Nov): "Prepare the recommended solution and exact cost. Do not purchase anything, change production settings or migrate the live database without my explicit approval."

**Nothing has been bought, changed or migrated.** This builds on the development branch's `database-before-6-dec.md` (m266), with today's prices and the performance study (`performance-study.md`).

## The recommendation, and its exact cost

**Database:** upgrade the existing Render Postgres in place to the smallest paid plan.
- The plan is `0.1c-256mb`: **$6 a month**, plus storage at **$0.30 per GB a month**.
- **When:** after the friends' round's final export, and before 6 Dec.
- **First:** a fresh sealed backup, then the plan change, then the checks below (the m266 process).

**Server:** move the Brain's web service off the free plan to **1 CPU (`1c-2g`, $25 a month)**.
- The 0.5 CPU plan (`0.5c-512mb`, $7 a month) costs less, but it gives worse plans: the planner stops on wall-clock time, so less CPU means less search (`performance-study.md`).
- The free plan's 0.1 CPU is worse still, and it is what the live Brain runs on today.
- **When:** before the round's first invite if it hasn't started. Otherwise after the round, so its plans aren't made on two different machines.
- **The cheaper path:** the planner change in `performance-study.md` (about 4 h) makes plans independent of CPU, and would make the $7 plan enough. Abram chooses between the two below.

| | Database | Server | Monthly total (USD, before VAT) |
|---|---|---|---|
| **Recommended now** | Render Postgres `0.1c-256mb`, 1 GB storage: $6 + $0.30 | Render `1c-2g`: $25 | **$31.30** |
| With the planner change (after it's built and measured) | the same | Render `0.5c-512mb`: $7 | **$13.30** |
| The minimum to keep the data (the server stays free) | the same | free (0.1 CPU, sleeps after 15 min) | **$6.30** |

- **Storage:** Render's page doesn't say whether any is included in the plan price, so the $0.30 for 1 GB is counted to be safe. The database is well under 1 GB today (m266).
- **The workspace:** stays on Hobby ($0). That gives 3 days of point-in-time recovery; Pro ($25 a month) would give 7 and isn't needed while the nightly sealed backups run.
- **Prices:** read 16 Nov 2026 from https://render.com/pricing.md (below). VAT is not included. The card is Abram's; Render may ask for one before any upgrade.

## Abram's ten points

### 1. The current provider and its expiry

- **The database:** Render Postgres, free plan.
  - Render: "Free Render Postgres databases expire 30 days after creation." After that comes "a grace period of 14 days to upgrade it to a paid compute plan", then "Render *deletes* the database (along with all of its data)".
  - It was created on 6 Nov (`brain/README.md`), so it **expires on 6 Dec** and is **deleted after 20 Dec** unless upgraded.
  - Free databases "don't support any form of backups". The only backups are ours: nightly at 02:23 UTC, sealed to Abram's key, kept 30 days (`ops.yml`).
- **The server:** Render's free web service.
  - It "spins down … after 15 minutes without receiving any inbound traffic", and waking "takes about one minute".
  - 0.1 CPU and 512 MB. 750 free instance hours a month per workspace.

### 2. The minimum viable paid database

**`0.1c-256mb`:** 0.1 CPU, 256 MB RAM, 100 connections, $6 a month plus $0.30 per GB.
- Adequate here because the database does little work. The planner runs in the web service, and each plan request makes a handful of small queries.
- The next plan up is `0.5c-1g` at $19, if connection or memory limits ever bite. Nothing measured says they will.

### 3. The minimum viable backend

The performance study (`performance-study.md`):
- **Memory:** about 170 MB per server process with the London catalogue, so 512 MB is enough.
- **CPU:** one day plan needs about 4.7 CPU-seconds to reach the quality measured with a full CPU.
- **Time:** the planner limits its search by **wall-clock** time. A request takes about the same time on any CPU (about 4.8–5 s for a day), but **gets worse plans on less CPU**. One own-time scenario lost 28% of its plan value at 0.5 CPU.

**So the minimum viable server, without a code change, is 1 CPU.**
- **With the planner change** (search effort fixed, not time), 0.5 CPU should give the same plans, about twice as slowly.
- **That is an estimate:** the check inside a 0.5 CPU quota is the change's first step.
- **At 0.1 CPU (today's free plan):**
  - own-time days lose up to 40%;
  - eight people at once wait about 60 s each, against the apps' 90 s limit.

### 4. Monthly costs: the options

| Option | Database | Server | Total a month | Backups | What it costs in work |
|---|---|---|---|---|---|
| **A. Render, recommended** | `0.1c-256mb` $6.30 | `1c-2g` $25 | **$31.30** | Render's 3 days of recovery, Render's 7-day logical backups, and ours | none: a plan change |
| A′. Render, after the planner change | $6.30 | `0.5c-512mb` $7 | **$13.30** | as A | the planner change (~4 h) |
| B. Neon for the database, Render server | Neon Free $0: 1 GB per project, 100 CU-hours a month, scale to zero after 5 min, **6-hour** history | `1c-2g` $25 (or $7 after the change) | **$25** ($7) | Neon's 6 hours, and ours | a move (~3 h), a new processor named in the privacy notice, and a 1 GB ceiling that stops writes |
| C. Hetzner, run ourselves | on the server | CX23, 2 vCPU, 4 GB: €5.99, plus backups 20% (€1.20) | **about €7.19** (12 Nov reading; UNVERIFIED today) | ours plus Hetzner's snapshots | Abram runs Postgres, TLS, updates, the firewall and monitoring; a new processor; **the apps' Brain address changes, so new app builds** |
| D. DigitalOcean | Managed PG 1 GiB $15.15 | App Platform $5 (512 MiB) | **about $20.15** (12 Nov reading) | daily backups, 7 days of recovery | a move, a new processor, new app builds |
| E. Keep everything free | a new free database every 30 days | free | $0 | none from Render | a monthly restore, with a deletion window each time; **not recommended** |

- **The cheapest reliable option is A′** ($13.30) once the planner change exists. **A** ($31.30) is the reliable one without code risk.
- **B is cheaper but weaker:** six hours of history, and a 1 GB ceiling.
- **C is cheapest in money and dearest in hours,** which CLAUDE.md says is the binding constraint.

### 5. Backup and restoration

- **Kept:**
  - **Ours, nightly:** a sealed backup (X25519 and AES-GCM, only Abram's key opens it), kept 30 days as a GitHub artifact.
  - **Render's, on a paid plan:** point-in-time recovery for the past 3 days (Hobby), and logical backups kept seven days "regardless of your workspace plan".
- **To restore ours (from this branch's tooling, SEC-10):**
  1. `python -m brain.backup verify <file> --key <Abram's key>`. It refuses an altered, cut-short or inconsistent file.
  2. `python -m brain.backup restore <file> --key <key> --database-url <the new database's External URL> --deletions <any newer backup>`. It keeps out everyone deleted since, from the newer backups' deletion records.
  3. Close outside access and point the services at the Internal URL (as on 6 Nov).
- **Production gap:**
  - The live Brain doesn't yet keep deletion records (SEC-10 is on the branch).
  - So a restore from today's backups can bring back someone who deleted after the backup was taken.
  - **Mitigation:** the backup that is restored is the one taken just before the change, minutes old.
  - The real fix arrives with the security release (`security-release-proposal.md`).
- **A restore drill**, monthly (about 20 minutes): `verify` the latest backup and restore it into a scratch database, never production.

### 6. Migration complexity

- **A, in place:** none. It's a plan change on the same database, with no new address and no copy.
- **B to D:** a copy.
  - A `pg_dump`/`pg_restore`, or our own backup's restore, plus the new connection string in Render.
  - About 2–3 h with checks.
  - A new data processor goes into the privacy notice: Abram's wording, and the ICO check (D108).
- **C or D for the server:** these also change the Brain's address. Both apps have `moments-brain.onrender.com` built in (`AppModel.swift`, `build.gradle.kts`), so moving the server means new app builds.
- **A custom domain** (for example `api.` on ODYS's own domain, once it exists) would remove that for good. It's worth adding in the next builds; a domain is a few pounds a year (Abram's money).

### 7. Compatibility

- **The Brain:**
  - It builds its own tables at start (`create_all`; no migration tool).
  - Our backups are row-by-row JSON, not a Postgres dump, so they restore into any Postgres version the Brain runs on.
  - CI now runs the whole suite on Postgres 18 (SEC-21), the version Render runs.
- **Neon:** supports 18.
- **DigitalOcean:** supports 15–18.
- **Fly's managed Postgres:** 16 and 17 only.
- **Supabase:** 18 not confirmed.

### 8. Does the app keep running during the change?

- **A:** Render says changing the plan means "brief downtime".
  - During it, plan requests fail with the apps' "can't reach" message.
  - **Ratings are kept on the phone and sent later** (both apps hold `pending_ratings`).
  - Onboarding answers sent in that minute would need a retry.
  - So do it at night, after the final export, with nobody mid-onboarding.
- **B to D:** the Brain has no read-only mode. A short maintenance window (about 30 minutes) at night, announced to testers, is the honest plan.

### 9. If a backup is corrupted

- `verify` refuses it, and so does `restore`, before writing anything.
  - AES-GCM fails on any changed byte, and on a cut-short file.
  - The content check refuses a backup whose rows don't hold together.
  - This is tested: `test_deletion_and_restore.py`, 19 tests.
- **Then:**
  1. the previous night's file (30 are kept);
  2. Render's own point-in-time recovery or logical backup (paid plans only);
  3. if all fail, the database as it is, untouched.
- **Prevention:**
  - The nightly job fails loudly if a backup can't be made (the ops alert).
  - The monthly drill proves a file can be restored before one is needed.

### 10. If the provider becomes unavailable

- **A short outage:**
  - The apps show their offline messages.
  - Ratings wait on the phone.
  - Trips' offline packs work without the server.
  - Nothing is lost.
- **A long one, or Render ending the service:**
  - Restore the latest sealed backup into another Postgres (Neon Free can be made in minutes) and point the Brain at it.
  - That keeps the data.
  - **The server address stays Render's until a custom domain exists** (point 6). Moving the server off Render means new app builds, about a day through TestFlight and the APK.
- **The rule that protects the data:** backups leave Render every night, sealed. They never depend on the provider that's down.

## Sources (read 16 Nov 2026 unless stated)

- **Render:**
  - **Pricing:** https://render.com/pricing.md
    - Postgres: "Less than 1 CPU … $6/month, 256 MB RAM … `0.1c-256mb`"; `0.5c-1g` $19; `1c-2g` $40; "Expandable storage ($0.30/GB)".
    - Web: free (0.1 CPU / 512 MB), `0.5c-512mb` $7, `1c-2g` $25.
    - Workspaces: Hobby "$0/month + compute", 3-day recovery; Pro "$25/month + compute", 7 days.
  - **Free plan rules:** https://render.com/docs/free.md (expiry, grace period, deletion, no backups, spin-down).
  - **Backups:** https://render.com/docs/postgresql-backups.md (recovery windows; logical backups kept seven days).
- **Neon:** https://neon.com/pricing.md, "Last updated: 2026-11-04".
  - Free: "permanent (not a trial)", 1 GB per project, 100 CU-hours, scale to zero after 5 min, 6-hour history.
  - Launch: $0.106 per CU-hour, $0.35 per GB-month.
- **Read 12 Nov, not re-read today:**
  - Hetzner (https://www.hetzner.com/cloud/cost-optimized; https://docs.hetzner.com/cloud/billing/faq/);
  - DigitalOcean (https://www.digitalocean.com/pricing/managed-databases; https://www.digitalocean.com/pricing/app-platform);
  - Fly (https://fly.io/docs/mpg/);
  - Supabase (https://supabase.com/pricing).
  - Their figures above are marked by date.
- **The performance figures:** `performance-study.md` (`brain/scripts/perf_study.py`, 16 Nov).
