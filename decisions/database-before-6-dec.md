# The database before 6 December: one schedule, for Abram's final approval (20 Nov 2026; m266, m288, m306)

**Status:**
- Abram approved the upgrade in principle: Basic-256mb, $6 a month plus $0.30 per GB (19 and 20 Nov).
- **Nothing is bought, and the production database isn't touched, until his final approval at step 6 below.**
- This page replaces the 29 Nov / 1 Dec / 3 Dec dates in `database-upgrade-runbook.md`, which now points here.

**The deadline** (Render, https://render.com/docs/free, read 19 Nov):
- The free database `london-places-swipe-db` was created on 6 Nov. Free databases "expire 30 days after creation", so this one **expires on 6 Dec**.
- "An expired Free database is inaccessible unless you upgrade it to a paid compute plan."
- After "a grace period of 14 days" (about 20 Dec), "Render deletes the database (along with all of its data)".
- **A paid database doesn't expire.** That's the end of this kind of deadline.

## The schedule (Option B: before the first invite, as Abram prefers)

One evening, in this order. **The target is the evening before the rehearsal, and 2 Dec at the latest.**
- The rehearsal then runs on the final database and server.
- The invites go out only after the rehearsal passes (`validation/friends-round.md`).

| # | Step | Who | Done when |
|---|---|---|---|
| 0 | **The old food field** (`foods-avoided-audit.md`, approved 20 Nov §5). Done first, so no backup or Render recovery point made later can hold it | Abram | `python -m brain.foodfield count` shows `with_key 0` |
| 1 | **A fresh sealed backup.** GitHub → Actions → `ops` → Run workflow → `backup`. Download the artifact | Abram | the job is green and the `.odysbk` file is on his computer |
| 2 | **The admin export**, as usual (`GET /v1/admin/export`), saved as `validation/raw/export-<date>.json` (git-ignored). Straight after step 1, so the two can be compared | Abram | the file exists |
| 3 | **The preflight**: all seven of Abram's conditions in one read-only command (below) | Abram | it ends `ALL CHECKS PASS` |
| 4 | **Keep copies.** The `.odysbk` file and the export, each in two places he controls (his computer, and an encrypted drive or password-manager attachment). The GitHub artifact also lasts 30 days | Abram | two copies of each |
| 5 | **Send Claude the preflight's output.** It holds only counts, digests and the sha256, never a value | Abram → Claude | Claude confirms it reads as a pass |
| 6 | **Abram's final approval**: "go", for the purchase and this configuration | **Abram** | he says go |
| 7 | **The upgrade** (configuration below), at night, with nobody mid-onboarding. Before the round, nobody is affected | Abram | Render shows "Available" |
| 8 | **The server to 1 CPU** (approved 19 Nov §2, $25 a month): `moments-brain` → Settings → Instance Type → 1 CPU / 2 GB. It redeploys the same commit | Abram | `/v1/health` shows the same `version` as before |
| 9 | **The read and write check** (below) | Abram, Claude reads the outputs | all of it holds |
| 10 | **Record it** in `validation/friends-round.md`: "the database moved to Basic-256mb, 1 GB, on …; the server to 1 CPU on …" | Claude, from Abram's outputs | the line is there |

**Steps 1 to 7 within the same hour.** The live Brain doesn't keep deletion records (SEC-10 is Category B), so a restore from step 1's file would bring back anything deleted after it. Before the round nobody else deletes, but keep the hour anyway.

**If it's 5 Dec and the preflight still hasn't passed:** upgrade anyway, after step 1 alone. An unchecked backup is better than none, and a paid plan in time keeps the data.

### Step 3: the preflight (one command, read-only)

From `brain/` on the development branch, in PowerShell with `$env:PYTHONPATH = "src"`:

```powershell
python -m brain.backup preflight <odys-brain-YYYYMMDD.odysbk> --key <your private key file> --export ..\validation\raw\export-<date>.json
```

It never connects to Render and never prints a value. Each of Abram's seven conditions maps to a line:

| His condition (20 Nov §1) | The line |
|---|---|
| 1. Decrypt it with his private key | `1. Opened with your key: PASS` |
| 2. Structurally valid | `2. Structure: PASS` (every table and column the Brain expects) |
| 3. An isolated test restoration | `3. Restored in an isolated database: PASS`: restored into an in-memory database on his computer, dumped again, then the counts and an id digest compared for every table |
| 4. Per-table row counts against the separate admin export | `4. Export against backup (N tables in both): PASS`, with each table's two counts. The id digests must match too, so equal counts with different rows still fail. Tables only in the backup, such as the swipe page's, are listed |
| 5. Every exported record belongs to an existing user | `5. Every exported row belongs to an existing person: PASS` (`brain/src/brain/exportcheck.py`) |
| 6. Record the backup checksum and the restoration result | the line `backup <name>: <bytes> bytes, sha256 <hex>`, and `6. Record (keep these lines; they hold no personal data):` with each table's count and digest. **Abram keeps this output with the file** |
| 7. A rollback procedure | "Rollback", below |

- **It ends with one of two lines:**
  - `Result: ALL CHECKS PASS: this is the evidence for your go.`;
  - or `Result: NOT READY: don't upgrade yet…`, with the failing check above it.
- **Abram's point about file sizes is built in:** nothing in it compares sizes. A backup counts only if its contents, digests and counts agree.
- **Tested** (`brain/tests/test_deletion_and_restore.py`):
  - a pass;
  - an export that disagrees with the backup by one rating ("FAIL: ratings: backup 2, export 1");
  - a wrong key;
  - a missing export.

  None of their output contains an answer, a contact or a message.

### Step 7: the configuration to check on the screen before saving

| | Now | After |
|---|---|---|
| Database | `london-places-swipe-db`, Free, Frankfurt | **the same database**, **Basic-256mb** (`0.1c-256mb`): 0.1 CPU, 256 MB RAM, 100 connections, $6 a month |
| **Storage** | 1 GB | **1 GB.** Read this line before saving. Render's Blueprint spec says a *new* `0.1c-256mb` database defaults to **15 GB** ($4.50 a month). Its docs don't say what an upgraded free one gets. If the screen shows 15, set 1 |
| **Storage autoscaling** | — | **Off** (changed from 19 Nov's "on"; reasons under "Storage") |
| Region, name, URLs, version | Frankfurt; both services use it | unchanged: a plan change, not a new database |
| Access from the internet | none (`ipAllowList: []`) | unchanged |
| Render's backups | none | point-in-time recovery for 3 days (Hobby), and logical backups kept 7 days |

Save, and add a card if asked (Render checks it with a $1 charge it refunds). Render says: "Your database will be unavailable temporarily during the change… Otherwise, it's unavailable for a few minutes" (https://render.com/docs/postgresql-creating-connecting, read 19 Nov).

### Step 9: the read and write check

| Check | Who | Expected |
|---|---|---|
| `GET https://moments-brain.onrender.com/v1/health` | Claude | `"ok":true`, and `"version"` unchanged by the upgrade (`80a0da3` until the new release is deployed, then its commit: `release-to-main.md`) |
| A new sealed backup (`ops` → `backup`), then `python -m brain.backup preflight <new file> --key <key> --export <step 2's file>` | Abram | **PASS** on 1–3 and 5. Step 4's counts and digests equal step 3's |
| One write | Abram | An install with the code `REHEARSAL`, a plan and a rating, then "Delete my data", so nothing is left |
| The swipe page | Abram | `london-places-swipe….onrender.com` opens: it shares the database |
| One logical backup in Render (the database → Recovery → "Trigger a backup") | Abram | an extra copy, kept 7 days |
| The next nightly `ops` runs | Claude | both jobs green |

## Storage: the size now, the growth, and the warning (Abram, 20 Nov §1)

### How big the database is

| | Bytes | Source |
|---|---|---|
| **Every table's rows, compressed** (the 19 Nov sealed backup) | 56,918 | the ops artifact |
| **The same schema with the 51 moment cards and no testers**, measured on PostgreSQL 16 on 20 Nov | 8,641,559 (8.2 MB) | `pg_database_size`. About 7.5 MB of it is PostgreSQL's own empty-database overhead |
| **The live database's actual size** | **Abram reads it** | Render → `london-places-swipe-db` → Metrics → disk usage ("View a variety of metrics for your database (disk usage, active connections, etc.)", render.com/docs/postgresql-creating-connecting.md, read 20 Nov). Claude can't see the dashboard |

**Estimate until Abram reads it:** about 9 MB, under 1% of 1 GB. The live database holds only test installs, and its compressed rows are 57 KB.

### How fast it grows

**Measured on 20 Nov:** the real Brain on PostgreSQL, with 20 simulated testers each doing a whole round:
- 6 swipes, 5 choices, the profile, a 400-character answer and 21 app events;
- the Test B pair, two day plans and a four-night trip (5 day plans);
- 6 ratings.

That's a heavy tester. **Each added about 79 KB** (8.98 MB after the first, 10.48 MB after 20). The script is `brain/scripts/storage_growth.py`.

| Who | Added | Total | Share of 1 GB |
|---|---|---|---|
| The friends' round (~20) | ~1.6 MB | ~11 MB | ~1% |
| Stage 2 (~110 installs) | ~8.7 MB | ~20 MB | ~2% |
| 1,000 testers | ~79 MB | ~90 MB | ~9% |
| **The warning level, 50%** | — | 512 MB | at about 6,000 such testers |

**Ordinary use can't fill 1 GB this winter.** Autoscaling would trigger at 90% (about 11,000 such testers).

### The one way it could fill fast: deliberate misuse

This was found while measuring, and it is in the audit (SEC-02):
- In the live code (`80a0da3`), a request's size isn't capped, and an app event's details (`props`) have no size limit.
- Anyone can make an install. The repository is public, so the API is easy to read.
- One install at the existing rate limit (180 requests a minute) could add roughly a gigabyte an hour.
- This is worked out from the code. **It was not tried against production**, which Abram has ruled out. Whether Render's proxy caps request sizes is **UNVERIFIED**.
- **The exposure exists today on the free plan too.** The upgrade doesn't create it.

SEC-01/02 on the development branch fix it (requests over 128 KB refused, an event's details at most 2,000 bytes). They are Category B, waiting for after the round. **Abram's call:** keep them there, or ask for them as a fifth hotfix before the invites (about 1 h to prepare and prove, as for A1–A4).

### Autoscaling: off, and why (changed from 19 Nov)

Render's rules (render.com/docs/postgresql-creating-connecting.md, read 20 Nov):
- "Whenever your database is 90% full, Render automatically increases its storage by 50%, rounded up to the nearest multiple of 5 GB" (1 GB becomes 5 GB).
- "It is not possible to reduce a database's storage."
- "After you increase a database's storage, you can't increase it again for 6 hours."
- With autoscaling off: "If your database exceeds its storage limit, it becomes unhealthy … Render automatically suspends the database to prevent data loss".
- **No email is mentioned for an autoscale.**

| | Autoscaling on | **Autoscaling off (recommended)** |
|---|---|---|
| Ordinary growth this winter | never triggers | never fills |
| A deliberate fill | storage grows by itself, permanently: +$1.20 a month for 5 GB, then more steps, at most one every 6 hours, **with no warning** | the database is suspended, **without data loss**. The round stops taking answers until Abram raises the storage in the dashboard (one click, the same price as an autoscale step) and the junk is removed |
| Spend without Abram's click | possible | **never** |

**The trade:**
- Off means that no storage is ever bought without Abram, which is what he asked.
- The cost of off is an outage in an unlikely abuse case, not lost data.
- If he would rather never have that outage, on is defensible: the first step is $1.20 a month. But then the warning below is his only notice, and it may come after the spend.

### The warning before any storage spend

Render has **no storage alert for Postgres**. Its notifications cover a service's persistent disk ("A service's persistent disk usage exceeds 80%"), not a database (render.com/docs/notifications.md, read 20 Nov). So:

| When | Warning | Lead time |
|---|---|---|
| **Now, until A4 is deployed** | Abram reads Metrics → disk usage at the upgrade, then once a week during the round (1 minute) | weeks, at ordinary growth |
| **With hotfix A4** (`production-privacy-patch.md`; prepared and tested, waiting for approval) | Each night the backup route reports the database's size, and the `ops` job **fails at 50%** of `LIMIT_MB` (1024). GitHub then emails Abram, and the ops webhook, if set, gets a message. The public log prints only "under 50%", never the size | at ordinary growth, years; a day at most otherwise |
| **Neither** | can't stop a fast deliberate fill: only SEC-01/02 can | — |

**If the storage is ever raised in Render, change `LIMIT_MB` in `ops.yml` to match** (the hotfix's comment says so).

## The Blueprint: how the paid plan stays paid

**The facts:**
- `render.yaml` on `main` (`80a0da3`) says `plan: free` for the database and both web services.
- It has no `diskSizeGB`, no `storageAutoscalingEnabled` and no auto-deploy line.

Render's Blueprint spec (render.com/docs/blueprint-spec.md, read 20 Nov):
- "Render retains the current compute plan for an existing database" when `plan` is **omitted**. It says the same for an existing service.
- `storageAutoscalingEnabled`, if omitted: "Render retains the current value for an existing database".
- `diskSizeGB`: "You can increase disk size, but you can't _decrease_ it."
- **Not stated** on that page: what a sync does when `plan` *differs* from the dashboard. The infrastructure-as-code page (read 19 Nov) says a sync "overwrites" conflicting dashboard changes. **So treat a sync with `plan: free` as able to undo the upgrade.** Whether Render would actually move a paid database back to free isn't stated; this plan doesn't rely on it either way.

**When `render.yaml` is applied:**
- only by a Blueprint sync: Auto Sync, on a push to `main` that changes it, or a Manual Sync;
- **never by an ordinary deploy.** A code deploy uses "the service's current configuration" (render.com/docs/rollbacks.md and deploys.md, read 20 Nov).
  - A push to `main` deploys code only where Auto-Deploy is on. For `moments-brain` it is off (since 6 Nov), so Abram deploys by hand.
  - Either way, a deploy never changes the plan.

**The guarantee, four parts:**
1. **Auto Sync stays off.** It has been off since 6 Nov, by the other session's record. **Abram confirms it before step 7:** Render → Blueprints → the Blueprint → Settings → Auto Sync shows "No".
2. **Never click Manual Sync while `main`'s `render.yaml` says `plan: free`.**

   The check, before any sync (PowerShell):
   ```powershell
   git fetch origin
   git show origin/main:render.yaml | Select-String "plan:"
   ```
   If any line says `free`, don't sync.
3. **After the round, the first `render.yaml` change makes the paid plan the written one.** It is prepared on the development branch only once the round's freeze on `render.yaml` ends (m196), and merged by Abram:
   - the database: `plan: 0.1c-256mb`, `diskSizeGB: 1`, `storageAutoscalingEnabled: false`;
   - `moments-brain`: `plan: 1c-2g`;
   - the swipe page: `plan: free`, as now.
   From then on, a sync re-applies exactly what was bought.
4. **An ordinary repository update** (a code push to `main`, a hotfix, a rollback) never touches the plan: see "When `render.yaml` is applied".

## Rollback, if the upgrade goes wrong

| What happens | What to do |
|---|---|
| **The change stalls or errors** | The free database and its data stay as they were until 6 Dec, with the grace period to about 20 Dec. Contact Render support (chat is included on Hobby). Try again the next day |
| **It finishes, but step 9's preflight differs from step 3's** | **Render's recovery can't help:** it reaches back only to the upgrade. Restore from step 1's file, which step 3 proved:<br>(a) create a new Basic-256mb database in Frankfurt, 1 GB, autoscaling off;<br>(b) `python -m brain.backup restore <step 1's file> --key <key> --database-url <its External URL>`;<br>(c) block outside access under its Networking;<br>(d) point both services' `…_DATABASE_URL` at its Internal URL;<br>(e) Claude checks `/v1/health` still answers the same version;<br>(f) the preflight on a new backup matches step 3.<br>Changing the variable redeploys `moments-brain` on `main`, so the version doesn't change; record it. The extra database is billed only while both exist (prorated) |
| **The server change (step 8) misbehaves** | `moments-brain` → Instance Type → back to Free. That redeploys the same commit, and needs no data step |
| **The app misbehaves after it** | If the data is wrong, as above. If the data is right, it isn't the database: send Claude the time and the screen |

## The cost

| | Per month | In £ (ECB, 19 Nov: $1 = £0.7604) |
|---|---|---|
| Basic-256mb | $6.00 | £4.56 |
| Storage, 1 GB | $0.30 | £0.23 |
| **Database total** | **$6.30** | **£4.79** |
| With UK VAT at 20%, if Render adds it (**UNVERIFIED**: Render's terms say only "You will pay any applicable taxes, if any") | $7.56 | £5.75 |
| The server at 1 CPU, for the round (approved 19 Nov) | $25.00 | £19.01 |
| **With the server** | **$31.30** ($37.56 with VAT) | **£23.80** (£28.56) |

- Billing is "prorated to the second" (render.com/pricing).
- Abram's card issuer may add a foreign-transaction fee on dollar charges. Not known here.
- **The first invoice settles the VAT question.**

## What the 19 Nov version said that no longer holds

- **"Option A, the round's final export on 29 Nov, then the upgrade by 2 Dec":** retired. The upgrade comes first, so the round has no database deadline.
- **"Autoscaling on":** replaced by off, with the warning.
- **The steps "counts", "export_counts" and "verify" one by one:** replaced by the single `preflight`, which does all of them and the isolated restore.

## Hours

- **Abram:** about 1.25 h for steps 0–9, in one evening.
- **Claude:** 0.25 h to read step 5's and step 9's outputs.
- **Done:** the preflight, the growth measurement and this page (1.5 h, 20 Nov).
