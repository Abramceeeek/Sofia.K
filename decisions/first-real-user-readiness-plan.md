# ODYS: First Real-User Readiness Checkpoint, and the plan to reach it (16 Nov 2026)

Abram's review of the audit, parts 10–12 (12 Nov). This is the plan, the checkpoint's acceptance criteria and the decisions that are his. **All work below is on the audit branch `claude/pensive-euler-fftd63`** (draft pull request into the development branch, never `main`).

**Nothing is deployed, bought or migrated, and the frozen friends' round is untouched.** Passing automated tests is not readiness: every criterion below that matters is about real phones, real people or real money decisions.

## 1. Where things stand (16 Nov)

| | Production (what testers get) | Development (the audit branch, merged with the development branch's m261–m269) |
|---|---|---|
| **Code** | `main` at `80a0da3`, frozen for the round (m198) | 165+ commits beyond it; m270–m277 from the audit and Abram's review |
| **Apps** | TestFlight 91, Android 21 | Android builds on API 36 (CI green); iPhone compiled only when the workflow is started by hand |
| **Brain server** | Render free plan: 0.1 CPU, sleeps after 15 min | the same code would run anywhere; sizing in `infrastructure-decision.md` |
| **Database** | Render free Postgres, **expires 6 Dec, deleted after 20 Dec**; no Render backups; our nightly sealed backups | the same database; nothing changed |
| **Tests** | as of the round's build | 526 Brain tests on SQLite, a Postgres 18 job in CI, 122 Android tests (100 of them screen renders) |
| **Friends' round** | ready to run; **the tag `friends-round-1` is not pushed** (the session's proxy refused it, m265) | Stage 1 and Stage 2 plans: `validation/friends-round-stages.md` |
| **Sample results** | flights and stays show labelled samples: a banner note, "· test prices", "A test price, not a real offer" (checked on 12 Nov in both apps). Live keys aren't set, so nothing claims live availability | unchanged; Abram's Part 10 question is answered: **labelled, not presented as live** |

## 2. Critical security issues (`security-release-proposal.md`)

- **Present in production today:**
  - SEC-06: the start point and stay name are kept, against the app's own words.
  - SEC-09: the safety message and contact are copied to the alert channel, *if* a webhook is set.
  - SEC-01 and SEC-02: limits can be bypassed, and there is no size cap.
  - SEC-04: one bad number breaks the export.
  - SEC-10: a restore brings back deleted people.
  - SEC-11: the database expiry.
- **Proposed during the round, if Abram approves:**
  - a privacy-only patch (SEC-04, SEC-06, SEC-08, SEC-09) cut from `80a0da3`, which changes nothing a tester sees;
  - Abram checks today whether the alert webhook is set.
- **Before strangers:** the rest of the Brain fixes, as a normal release.
- **Before any public release:**
  - SEC-12 (the Android key) and SEC-14 (the iPhone privacy manifest), both needing Abram;
  - SEC-13 (API 36, built);
  - SEC-20 (map tiles).

## 3. The database and the server, with costs (`infrastructure-decision.md`)

- **The database:** upgrade in place to `0.1c-256mb`, $6 + $0.30 a month, after the round's final export and before 6 Dec.
- **The server:** 1 CPU, $25 a month, keeps today's plan quality. After the planner change, 0.5 CPU at $7 is enough. Checked on 18 Nov: the same plans, stop for stop, in a 0.5 CPU quota.
- **Total:**
  - **$31.30 a month now**;
  - **$13.30 a month after the planner change**;
  - $6.30 a month if only the data is kept.
- Prices were read from Render's pages on 16 Nov, before VAT.

## 4. Backend performance (`performance-study.md`)

- **Feasibility holds:** 0 broken rules and 0 failures at any CPU level.
- **Quality does not hold.** The planner stops on wall-clock time, so less CPU means less search:
  - on today's 0.1 CPU, own-time days lose up to 40% of their value;
  - eight people at once wait about 60 s each.
- **The fix:**
  - a fixed amount of search, with time only as a cap, and a status when the cap is hit;
  - a better seed for own-time days;
  - about 7 h, after the round.

## 5. Mobile testing gaps (`mobile-validation-plan.md`)

- **The iPhone has no automated tests.** Android's are mostly drawings of screens.
- **Proposed:**
  - a contract test (2 h);
  - Android journeys against a fake Brain (5 h);
  - iPhone unit tests (4 h);
  - a 25-step real-device checklist, on top of the rehearsal's 25.
- **No external build without the "blocks release" rows passed on both phones.**

## 6. The friends' experiment

- **Stage 1:** a usability pilot that makes no statistical claims, read from what build 91 already collects. There is an optional 10-minute debrief, and an issue log with severities.
- **Stage 2:** pre-registered:
  - **H1:** the gut choice, exact binomial;
  - **H2:** "fits me", paired, tested only if H1 passes;
  - **The size:** 76 completers if the true share is 65%, 169 if it is 60%;
  - **Installs:** about 110 at a 70% completion rate.
  - H2's size comes from Stage 1's spread.
- **The round's own preparation:**
  - `friends-round-plan.md`;
  - `friends-round-rehearsal.md`;
  - push the tag;
  - the final export by 29 Nov.

## 7. Recommendation calibration (`recommendation-honesty-and-learning.md`)

- **Built (m275):** no chance or match word on screen. "Recommended because of your lean towards views and awe" names factors from the person's own answers.
- **Kept internally and checked on real ratings:** the 75% and 50% bands, with words on screen again only if Abram decides after that check.
- **Built (m276):** stored plans now keep each stop's prediction, server-side only. They never did, so the previous evaluation would have found nothing to measure.

## 8. Real-user validation

`learning_milestones.py` judges each rated stop against its own plan's prediction, by milestone, against the population's weights alone:
- after onboarding;
- after the first rating;
- after 2 days out;
- after 5 days out;
- after 20 ratings.

It runs on real exports only, and a row is exploratory under 30 rated stops. The friends' round's plans (build 91) kept no predictions, so they are checked by the words they showed.

## 9. Payment and business experiments (`commercial-experiments.md`)

- **Test D:**
  - 6–8 interviews on past spending;
  - then a non-binding offer at a random £4.99–£9.99 (a day) or £14.99–£24.99 (a trip), to people who used a plan;
  - the signal is who takes a small next step, not who says yes.
- **Test E:**
  - five accommodation managers;
  - a demo;
  - a five-step ladder, where only a price and a start date in writing count as evidence of payment.
- **No money, card or payment page anywhere.**
- The six questions Abram set before money (what is sold, the seller, the provider, refunds, travel-sector duties, app-store rules) have working answers. Two of them need a solicitor.

## 10. Global data-provider research (`map-tiles-and-place-data.md`)

- **Layer 1:** Overture Places (free, storable, no share-alike), Wikidata for official links, and OSM in its own table for hours and access hints.
- **Layer 2:** the existing verified catalogue (built).
- **Layer 3:** moments.
- **Ruled out for storage:** Google, Tripadvisor and Yelp.
- **The real cost is verification hours**, not data: roughly 60 h per 100 experiences by hand (a GUESS until measured).
- **Proposed:** a 4 h, read-only one-borough match trial, for London and the Paris benchmark.
- **Map tiles:** OpenFreeMap with MapLibre now ($0), our own PMTiles as the fallback, Stadia $20 a month if a vendor is wanted.

## 11. The release-readiness backlog (Abram's part 10, with status)

| Item | Decision | Status (16 Nov) | Blocks |
|---|---|---|---|
| Database expiry, 6 Dec | urgent; paid options | **recommendation and exact cost ready**; Abram approves | everything after 6 Dec |
| Production server capacity | benchmark and cost | **measured**; 1 CPU, or 0.5 CPU after the planner fix | strangers (plan quality) |
| Android API 36 | verify, approve | **built**, CI green; checked against Google's page (11 Nov) | Play submission |
| Android signing key | secure migration plan | **plan ready**; Abram makes the key | Android strangers |
| iPhone privacy manifest | prepare; founder input | **inventory ready**; Abram's answers needed | App Store; external TestFlight to strangers |
| iPhone backup and deletion | correct and test | **built** (Keychain this-device-only, cache off, full clear); compiled only by hand; A3 tests proposed | next iPhone build |
| External URL validation | approved | **built**, both apps, with tests | next builds |
| CI/CD least privilege | safe improvements | **built**: actions pinned; write only in the publish job on `main` | — |
| Postgres testing in CI | approved | **built**: a Postgres 18 job; it found one real bug, now fixed | — |
| Android map tiles | replace before public release | **researched**; OpenFreeMap + MapLibre recommended (~6 h) | public release |
| Search quota | one install can't exhaust it | **built**: 20 a day per install, on top of the hourly and overall caps | live provider keys |
| Referral manipulation | fix before rewards | accepted until rewards; nothing pays per referral | any reward |
| Deleted-data restoration | implement | **built**: deletion records, `restore --deletions`, `verify`, 19 tests | any restore (so the database move) |
| Admin and safety alerts | minimise personal data | **built**: the alert says only "message #N is waiting" | the privacy patch |
| Test-mode search results | label, or keep unavailable | **checked: labelled in production** (banner, "test prices", "A test price, not a real offer") | — |

## 12. The First Real-User Readiness Checkpoint: acceptance criteria

**Each line is pass or fail, with the evidence named.** Any failed line means the checkpoint fails, whatever the tests say.

### 1. Security and infrastructure are reliable enough

- [ ] **The database:**
  - it is on a paid plan;
  - `/v1/health` answers;
  - the export's row counts match the last free-plan export.
- [ ] **Backups:**
  - the last 7 nightly sealed backups exist;
  - the latest passes `verify`;
  - **a restore drill into a scratch database succeeded within the last 30 days**.
- [ ] **Every High and Medium security finding** is either live (`/v1/health` `version` is the release containing it) or accepted by Abram in the decision log, with its reason.
- [ ] **The SEC-05 header check** has run on a staging service, and its result is recorded.
- [ ] **The live server keeps plan quality.** The four day scenarios in `perf_study.py` give the same plan value on the production plan size (simulated by its CPU quota) as on 1 CPU, and eight simultaneous day plans each finish within 30 s.
- [ ] **No personal data in alerts or logs:**
  - the tests pass;
  - one real Help & safety test message arrives in the alert channel as "message #N is waiting" only.

### 2. Both apps work on real devices

- [ ] **The rehearsal's 25 steps and R1–R25** (`mobile-validation-plan.md`) are recorded for the build under test, on one iPhone (newest iOS) and one Android 16 phone. **Every "blocks release" row passes.**
- [ ] **No crash** in those runs.
- [ ] A1 (the contract test) and A2 (Android journeys) run in CI and pass. A3 (iPhone unit tests) has passed at least once on that build's commit.
- [ ] The build's Android signing follows the SEC-12 plan, or Abram has accepted the debug key for that round, in writing in the log.

### 3. The frozen friends' experiment is ready, and runs without interference

- [ ] The tag `friends-round-1` points at `80a0da3` on GitHub.
- [ ] `/v1/health` `version` is `80a0da3` on every check during the round (the ops workflow's uptime check, every 6 h).
- [ ] **No commit to `main` between the round's start and its final export** (`git log`), unless Abram approved the privacy patch, in which case its diff touches none of Test B's files.
- [ ] The rehearsal passed on both phones before the first invite. The manifest records the start date and the final export's date.
- [ ] The final export is saved in `validation/raw/` **before** the database plan change.

### 4. The recommendations are evaluated against real experiences

- [ ] **The Stage 1 read-out exists:**
  - the issue log, with severities;
  - the pair's counts and quotes;
  - every rated stop listed with its plan's words and the rating;
  - `evaluate_export.py`'s output.
  - It says "exploratory" wherever n is under 30, and makes no claim of preference or calibration.
- [ ] **Every blocker and major from the issue log** is fixed or explicitly deferred by Abram.
- [ ] **The next build shows no chance or match word** (m275, checked as R2 on both phones). It keeps predictions with stored plans (m276, a test).
- [ ] **Stage 2's pre-registration is frozen:** this branch's `friends-round-stages.md` is committed with its sizes filled in from Stage 1, before Stage 2's first invite.

### 5. We know what customers value, and which model to test

- [ ] At least 6 Test D interviews are done, with notes kept without names.
- [ ] The non-binding offer has been shown to at least 8 people who used a plan, with the next-step rate reported.
- [ ] Five Test E conversations are done, with each manager's furthest step on the ladder recorded.
- [ ] **A one-page decision:** which business model to test first, the evidence for it, and what would change the decision. Abram signs it off in the log.

## 13. The proposed order

| When | What | Who | Hours |
|---|---|---|---|
| **This week** | check the alert webhook in Render; push the tag; decide the server size before the round (or leave it); start the round | Abram | 1 |
| This week | review the audit branch's full diff and merge it into the development branch (§14) | Abram | 1 |
| During the round | if approved, the privacy patch from `80a0da3` | Claude, then Abram | 3 + 0.5 |
| By 29 Nov | the final export; then the database upgrade (m266's steps), and the checks | Abram, then Claude | 0.5 + 0.5 |
| Early December | the security release to the live Brain, with the planner fix and the server size | Claude (Abram approves the deploy) | 7 + 1 |
| Early December | the Stage 1 read-out; fix its blockers and majors | Claude | 3 + per issue |
| December | the next app builds: m275, SEC-13, SEC-15, SEC-16, the map tiles, SEC-12 (after Abram's key), SEC-14 (after his answers); A1–A3 | Claude | 6 + 3 + 2 + 11 |
| December | the real-device pass on both phones | Abram | 3 |
| December, in parallel | Test D interviews and Test E conversations | Abram (Claude prepares) | 9 + 3 |
| **Then** | the checkpoint review; if it passes, Stage 2 with strangers | both | — |

**Total, about 7.5 h a week:**
- **Claude:** about 45 h of build and analysis.
- **Abram:** about 20 h of his own over December, mostly conversations and phones.
- **The checkpoint lands in early January,** if the round ends on 29 Nov and nothing major is found.

## 14. Before the audit branch is merged into the development branch

Abram asked for its complete diff to be reviewed first, confirming two things: it doesn't alter the frozen experiment, and it doesn't introduce unrelated changes. The review is in the pull request's description. It covers:
- the files changed;
- that no file `main` runs was changed on `main`;
- that Test B's own files are unchanged: `brain/data/testb/`, `testb.py`, and the blind-pair code paths (the pair still shows nothing personal, with tests);
- every non-security change, each with the founder decision behind it.

## 15. Decisions for Abram

**Money:**
1. **The database:** upgrade in place to Render's `0.1c-256mb` ($6 + $0.30 a month), after the final export, before 6 Dec.
2. **The server:**
   - 1 CPU ($25 a month) now;
   - or stay free until the planner fix, then 0.5 CPU ($7 a month);
   - and **when**: before the round starts, or after it ends.
3. Later: a domain for the Brain's address, so it can move without new app builds (a few pounds a year); and Google Play or Firebase for Android testers.

**Production and the round:**
4. Push `friends-round-1` (the session's proxy can't).
5. The privacy patch during the round: yes or no. If yes, approve the merge into `main` when it's ready. Also decide whether to clean the start points already stored (SEC-06): destructive, on the live database.
6. Look in Render at `BRAIN_ALERT_WEBHOOK_URL` today.
7. The SEC-05 staging check (a separate free service, deleted afterwards).

**Privacy and the apps:**
8. **SEC-14:** the App Store privacy answers for each item in the inventory. The manifest is written from them.
9. **SEC-12:** make the release key on his own computer, put it in GitHub Secrets, and choose how Android testers get the app.
10. **m276:** whether the privacy notice says plans keep "how well each stop was expected to suit you".
11. **The post-experience tap** (`post-experience-feedback-proposal.md`): build after the round, and confirm the notice line.
12. **The map tiles provider:** OpenFreeMap now, with our own tiles later. This also changes the privacy notice's map line.

**Evidence and validation:**
13. **Stage 2's design point:** 65% (76 completers) or another. And δ = 0.5 points for "fits me".
14. The Stage 1 debrief calls: whether they fall within the round's consent.
15. **Test D's prices,** and Test E's quote figure (£350 a month, the project's GUESS).
16. The one-borough data trial (4 h, read-only, £0).
17. Merge this branch into the development branch, after reading §14's review.

**Not decided, by design:**
- the payment provider (after the business bank account);
- a marketplace (needs legal advice and commercial evidence);
- more cities;
- 3D (closed).
