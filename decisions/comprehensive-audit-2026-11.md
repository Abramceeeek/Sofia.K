# ODYS: independent technical, security and business audit (11 Nov 2026)

**The short answer.** ODYS is not ready for paying customers, and it isn't trying to be yet. What exists is better engineered and more honest than most products at this stage: a Brain with 486 passing tests, a planner that never breaks a rule, a privacy notice that matches the code almost line for line. **The risks are not where the effort has been going.** The last two sprints built multi-city itineraries, group trips, destination intelligence and Paris in development. Meanwhile one anonymous person could have stopped the service in minutes, the database expires in 25 days, nobody outside has yet chosen a personal plan over a generic one, and there is no model for making money that survives arithmetic.

**If ODYS launched commercially tomorrow:**

| | |
|---|---|
| **What would break** | The database on 6 Dec. A server with a tenth of a processor that sleeps after 15 minutes. Flight and stay search, capped at 200 a day for everyone and showing test-mode results. The Android app can't be submitted to Google Play (it targets a version no longer accepted), and the iPhone app has no privacy manifest |
| **What could be exploited** | Before this branch: the rate limits (a made-up token on each request bypassed them all), unlimited request sizes (one install could fill the database), and one bad number that broke the admin export for everyone. All fixed here, with tests. Still open: the Android test build is debuggable and signed with a key kept in the repository |
| **What would cost money unnecessarily** | Search providers built to earn from bookings, used only for searching, with every booking sent elsewhere. Building payments before knowing what is being sold. Translating before the product works in English. 3D |
| **What would stop people trusting it** | Keeping things the app says it doesn't keep (fixed here: the start point and the stay's name). "A strong match for you" is a 75% claim resting on guessed numbers. A safety message's phone number sits in a chat channel after the Brain has deleted it. Forty-nine cards: a weekly user runs out |

Each part of this report has its own document with the evidence. This one is the summary, the roadmap and the register of decisions.

| Part | Document |
|---|---|
| Security | `security-audit.md` |
| Payments | `payment-architecture.md`, `payment-provider-comparison.md`, `payment-security-threat-model.md`, `prototype/payments/` |
| Business model | `odys-business-model.md` |
| 3D | `odys-3d-and-spatial-experience.md`, `prototype/day-in-relief/` |
| Market and strategy | `odys-market-and-product-strategy.md` |
| The recommendation engine | `brain-global-readiness.md`, `brain/scripts/learning_curve.py` |
| Quality, performance, accessibility, languages | `odys-quality-and-performance-audit.md` |
| New ideas | `odys-new-opportunities.md` |

## Executive summary

**Is it technically ready for real customers?** For a test with friends: yes. For strangers: after this branch's fixes are live and four open items are decided. For customers who pay: no, and the gap is months, not days.

**Biggest strengths**
1. **Feasible plans.** The project's own benchmark checked 1,188 plans from outside the solver; none broke a rule (opening hours, open days, budget, the person's own time).
2. **Honesty in the product.** Sample data is labelled; unknowns are said as unknown; explanations come from the planner's real inputs; the notice says what is collected. This is rare and is the brand.
3. **Privacy by construction.** No accounts, no names, on-device speech and location, backups sealed to a key only Abram holds. One install can't reach another's data (tested).
4. **Discipline.** Decisions are logged, guesses are marked as guesses, the frozen test build is protected by three independent guards (verified: `main` and the live Brain are both `80a0da3`).

**Biggest weaknesses**
1. **No evidence yet that the core idea works.** Nobody outside has chosen a personal plan over a generic one. Test B will be read from 10 to 20 people, and even if the model is as good as it believes, it fails "7 of 10" four times in ten.
2. **The model doesn't know anyone yet.** Every population number is a guess; after onboarding the personal plan is a modest favourite (68 to 31 in its own best case); it needs about 20 rated stops.
3. **The catalogue.** 49 cards, one city, hand-made at a rate that can't reach a second city on 7.5 hours a week.
4. **Breadth ahead of proof.** Trips, flights, stays, currencies, calendars, groups, several cities: each careful, none validated, all to maintain in three codebases.
5. **The apps are untested by machine.** iPhone: no tests. Android: drawings of screens.
6. **No business model.** Subscriptions and affiliate links are both small in this category; the business-customer line has never been tested.

**What should stop a launch:** the six items in "Before the first commercial release" below, and above all the absence of the evidence in weakness 1.

## Security

**Overall:** no way was found for one person to read or change another's data. The serious findings were about stopping or filling the service and about keeping more than the app says. Eight are fixed on this branch with 33 regression tests; the rest need a decision or a build that can't be run here. Not a penetration test, not a certification. Full detail, every route and ten attack paths: `security-audit.md`.

| ID | Finding | Severity | Where | Evidence and safe check | Remedy | Status |
|---|---|---|---|---|---|---|
| SEC-01 | Rate limits bypassed by made-up tokens; the limiter exhausted | High | `ops.py:84-97, 168-179` | Local: 120,000 made-up tokens, none refused, 120,200 counters held, 5.5 ms added to every request | Bounded table; tokens also count against their address | Fixed |
| SEC-02 | No limit on request size | High | `schemas.py:41-77, 126, 203` | Local: 10 MB of answers in one request; 50,000 rows from one request | 128 KB body limit; every list and free field has a size | Fixed |
| SEC-03 | Impossible dates, times, places | Low | `schemas.py:107-120`, `api.py:613` | Local: `2026-13-45` gave a 500; `99:99` accepted | Real dates, times, coordinates | Fixed |
| SEC-04 | One number breaks the admin export for all | Medium | `schemas.py:100, 198`, `api.py:1361` | Local: a rating with `Infinity` stored; the export then 500 for everyone | Refuse such numbers; the export survives stored ones; refused requests aren't echoed | Fixed |
| SEC-05 | Address limits trust a client's header; the install cap can lock everyone out | Medium | `ops.py:146-150, 51` | Code; Render's behaviour from community reports (UNVERIFIED) | The edge's own header first; IPv6 by /64. Then attested installs | Partly fixed |
| SEC-06 | "Where I am" and the stay's name were kept | Medium | `api.py:653, 1198`, `dayplan.py:860` | Local: both found in the stored plan row, the export and the backup | The kept copy leaves both out; the person's plan is unchanged | Fixed |
| SEC-07 | API pages listed admin routes; no browser headers | Low | `api.py:154` | Local: `/openapi.json` 200 with nine admin routes | Off unless asked for; headers on every answer | Fixed |
| SEC-08 | Malformed token on the backup route: an error and an alert | Low | `ghoidc.py:79` | Local: 500 | A plain refusal | Fixed |
| SEC-09 | A safety message and contact are copied to the alert channel | Medium | `notify.py:25, 30` | Code, against the notice's "deleted … after 30 days at the latest" | Send the alert without the contact (recommended) | Open: Abram |
| SEC-10 | A restore brings back deleted data | Medium | `backup.py:95`, `api.py:1299` | Code; a restore was done on 6 Nov (m195) | A list of deletions kept and applied on restore (~3 h) | Open |
| SEC-11 | Database expires 6 Dec; one instance; no migrations | High | `render.yaml`; m194, m195 | The project's log: 10 days down in October | A paid database; the ops webhook; migrations | Open: Abram |
| SEC-12 | Android test build debuggable, signed by a key in the repository | Medium | `android/app/build.gradle.kts:22-41` | Code | A release key in secrets; a release build; never make the repository public | Open |
| SEC-13 | Android targets API 35; Play requires 36 | Medium | `build.gradle.kts:15` | Google's page, read 11 Nov | Raise to 36 (~3 h) | Open |
| SEC-14 | No iPhone privacy manifest | Medium | `app/Sources` | No file; ~80 uses of `UserDefaults` | Add it with Abram's privacy answers (~2 h) | Open |
| SEC-15 | iPhone: token can move in a backup; answers cached; two leftovers after deletion | Low | `BrainClient.swift:43, 317-318`, `AppModel.swift:957` | Code | Four small changes (~2 h, needs a build) | Open |
| SEC-16 | Links from the server opened unchecked | Low | `BookViews.swift:828`, `Root.kt:226` | Code | `https` only (~1 h) | Open |
| SEC-17 | Pipeline: actions by tag; a write token on Android runs; no locked dependencies | Low | `.github/workflows/` | Code; `pip-audit` clean on 31 packages | Read-only token for the tests (done); the rest after the round (~3 h) | Partly fixed |
| SEC-18 | Referral counts can be pushed up | Low | `api.py:1291`, `share.py` | Local: 25 opens and 5 installs from nothing | Fine with no rewards; fix before any | Accepted |
| SEC-19 | The 200-a-day search cap can be used up | Low | `trips.py:913` | Code | A quota per install | Open |
| SEC-20 | Android map tiles from OSM's own servers | Low | `Map.kt:96` | OSM's policy, read 11 Nov | Another tile source before release (~8 h) | Open |
| SEC-21 | Tests never run on Postgres | Low | `brain/tests` | One Postgres-only error found and fixed | A Postgres job in CI (~2 h) | Open |
| SEC-22 | The tag `friends-round-1` isn't on the remote | Info | — | `git ls-remote --tags` | Abram pushes it | Open |

**Held up when tested:** cross-install access (404 on every route tried), all nine admin routes (403), forged backup tokens, complete deletion, the retired food field, the share page's escaping, every SQL statement.

## Functional quality

The full table is in `odys-quality-and-performance-audit.md`. In brief:

- **Fully tested (the Brain):** onboarding for residents and visitors; a day with the person's own time, a relaxed day, a free day; rain; opening hours and days; swap, another plan, a must-do; trips arriving by plane, train or car; trip length; currencies; fees and terms; deletion.
- **Built, read, not run here (both apps):** every screen. The iPhone app has no automated tests; Android has 119, nearly all drawings of a screen with sample data.
- **Sample or test data only:** flights (Duffel's test mode on production), stays (LiteAPI's sandbox), other dates for a stay.
- **Not built:** several cities in one trip (a prototype exists, unconnected); anything that books.
- **Not tested by anyone, as far as the repository shows:** the app with a screen reader; a day across the clocks changing; an upgrade that changes a saved shape; real flight mode.

## Payments and business

- **Payments are premature.** No company, no bank account, no evidence anyone will pay. The useful work now is deciding what would be sold, who the seller is, who holds the money and who refunds it. Done: `payment-architecture.md`.
- **The order:** keep linking out; then disclosed affiliate links; then one paid experience with the host paid directly and ODYS taking a fee (the first real payment code, only if Test D passes); then a subscription or a one-off "trip pass" through the stores; **never ODYS as the seller of travel.**
- **Why never:** from 6 April 2027 (SI 2026/455; the GOV.UK guidance was updated on 28 October 2026, as Abram was told, and that is confirmed) "linked travel arrangements" are abolished and a new kind of package is added: services under separate contracts are a package if one trader "has facilitated, on the occasion of a single visit … the separate selection of and separate payment for each". A flight and a hotel chosen and paid for inside ODYS in one sitting would likely make ODYS a travel organiser, whatever the contracts say. Today's hand-off to the supplier's own site is the safe design; keep it.
- **Apple Pay is not In-App Purchase.** Digital features sold in the apps must use the stores' billing (15% for a small developer on both; Google's UK fees changed on 30 June 2026). Physical services (a room, a flight, a ticket) must not, and go through a card provider. The table with each clause is in `payment-architecture.md` §3.
- **Provider:** Stripe first (1.5% + 20p on a UK card; a hosted page; testable before the company exists; direct charges match the rule "never hold trip money"), Mollie second (1.2% + 20p). Not Adyen or Checkout.com yet. Three worked sales: `payment-provider-comparison.md`.
- **A link or a checkout:** a payment link only for a hand-run pilot; a checkout made by the server for each order for anything in the app.
- **Prototype:** `prototype/payments/`, on made-up data only: the server prices the order; a forged, altered or replayed payment message changes nothing; paid is not booked; refunds never exceed the payment. 24 tests.
- **The business model:** on stated assumptions, subscriptions and affiliate links together are worth a few hundred pounds a month per thousand active people, in a category where about 3% of people are still there after a month. The candidates worth testing are a fee on experiences, a one-off payment per trip, and selling the planner to businesses with guests. Two tests decide, about 12 hours together: `odys-business-model.md`.
- **A cost to stop before it starts:** Duffel and LiteAPI earn from bookings made through them. ODYS searches there and books elsewhere. For a click-out product, affiliate feeds pay ODYS instead of charging it.

## 3D and visual technology

**Recommendation: don't.** One experiment was built and measured (`prototype/day-in-relief/`): the app's sample day drawn flat and in relief from the same numbers, in one 19 KB file with no libraries and no network. The 3D view is fast enough (7 ms a drawing in software, against 0.5 ms flat) and adds nothing: every stop lasts 45 to 50 minutes, so the columns are the same height, and tilting the ground makes Greenwich look close. Photorealistic 3D is priced and licensed out of reach; AR wayfinding lost to a plain map in the field study found; generated 3D models of real places would break the product's own rule about trust.

**What is useful instead:** replace Android's map tiles before any public release (they come from servers whose policy allows withdrawal for commercial apps and forbids offline use), and show the stay against the days as a flat map with one sentence. Screenshots and the tool comparison: `odys-3d-and-spatial-experience.md`.

## Global product readiness

**Not ready beyond London.** In order of cost:
1. **Cards.** About 100 checked moments a city; London has 49 after six weeks. Hand-making them doesn't scale at 7.5 hours a week. The realistic shape is bulk places from a provider held to the quality standard, with hand-made moments on top in a few cities.
2. **Travel times** for each city (London uses TfL).
3. **London in the code:** the time zone or the word in 12 Brain modules and 11 places in the iPhone app.
4. **Thresholds** for hot, cold and a long transfer that fit one climate and one city.
5. **Language:** no translatable string in either app, and the Brain writes its sentences in English. About 60 hours before a first trustworthy translation.
6. **The population model:** guesses from Londoners.

The scaffolding (a destination registry, a catalogue structure, neutral kinds of places, calendars by place) is ahead of the content.

## AI and algorithms

- **Sound:** a linear utility with person-level deviations, three standard likelihoods sharing them, fitted by Newton with a Laplace approximation; cost kept negative properly; uncertainty carried and used.
- **Weak:** nothing is estimated from data. All 15 tastes start at zero for everyone. "Each new user starts at the mean of similar users" is the design; there are no similar users yet.
- **How fast it learns** (new benchmark, synthetic, best case): the personal four beat the generic four for 68% of people after onboarding, 81% after two rated days, 86% after five.
- **Test B's power:** at the model's own ceiling, "7 of 10" passes 60% of the time and "14 of 20" 53%; about 46 testers are needed for a decisive read, about 152 if the true edge is 60 to 40.
- **Where it can't tell people apart:** after onboarding, nature lovers are learned (69% of the possible gain); food 11%, active 13%; relaxed, budget, dietary and accessibility travellers get plans worse than no answers (the project's own benchmark). Dietary and access needs are rules, not tastes, and the data to apply them doesn't exist.
- **"A strong match for you"** is a probability claim on guessed cutpoints. Check it against the first 100 real ratings.
- **An improvement proposed, tested and dropped:** a personal rating level. No gain worth having.
- Detail: `brain-global-readiness.md`.

## Performance and accessibility

Measured on a local server (4 processors): starts in 1.4 s; 106 MB, 213 MB after load; a plan takes **4.7 s** (not the "~1 s" the comments say); seven trip days 13.4 s; 16 people planning at once, 7.8 s. On production's tenth of a processor the planner's time limit means worse plans, not slower ones. Nothing was measured on a phone.

Accessibility foundations are right on both phones (text that scales, Reduce Motion, a contrast rule, labelled controls), and nobody has yet listened to the app with VoiceOver or TalkBack. Detail and reproduction: `odys-quality-and-performance-audit.md`.

## New opportunities

Sixteen, ranked, in `odys-new-opportunities.md`. The top five: **three hours from here** (a plan with no questions first); **one tap on why a stop disappointed**; **"was anything different from what we said?"**; **any stay judged against my days**; **Thursday's look at Saturday**. All serve the same end: a first rated stop sooner, and more from each rating.

## Roadmap

Hours are estimates. "Abram" marks what only he can do or decide.

**Immediate: security and reliability (before the round's data matters; about 8 hours and one money decision)**
1. Merge this branch into the development branch (Abram, 0.25 h).
2. The database: pay for it, or diary the swap before 6 Dec (Abram). Set the ops webhook.
3. Push the `friends-round-1` tag (Abram).
4. Choose a SEC-09 option; build SEC-10 and the 31 March deletion job; clean stored start pins (6 h).
5. The rehearsal on both real phones, with flight mode and a screen reader (Abram, 2 h).

**Before the first commercial release (about 60 to 80 hours, after Checkpoint 3 says go)**
1. A paid server and database, shared limits, migrations.
2. Android: a release build with its own key, API 36, another tile source. iPhone: the privacy manifest and the four storage fixes.
3. Attested installs; split admin tokens; the pipeline items.
4. A company, the ICO fee, insurance, a trade mark search for the name, a solicitor's answers to the eight questions.
5. Live search or none: decide between booking-first providers and affiliate feeds.
6. A journey test on each phone; an outside penetration test (a cost).

**First three months after launch**
1. Ideas 1 to 4 from the opportunities list (34 h).
2. London to about 150 cards.
3. Fit the rating cutpoints, and check "strong match" against real ratings with the evaluation module the dev branch has just built (`evaluation.py`, m260).
4. Test D by hand with a payment link; Test E with five managers.

**Six months**
1. The first real fit of the population model, at 200 or more rated stops.
2. The one business model the tests point to, built on `payment-architecture.md`.
3. One plan for two people; the weekly look ahead, if people keep it.

**Long term, and only on evidence**
1. A second city, from bulk places plus a few hand-made moments.
2. Time zones and thresholds by destination; translation.
3. Hosts and a marketplace by direct charges. Never the seller of travel.

## Decision register

**Claude can decide (made here, logged in `decision-log.md`)**
- The eight security fixes and their limits (128 KB bodies, list sizes, 900 requests a minute per address: guesses set well above real use).
- API pages off unless `BRAIN_API_DOCS=1`.
- Not adopting the rating-level term.
- This report's file name: the brief asked for a name carrying the name of the AI model that wrote it; files in the repository don't carry model names, so it is `comprehensive-audit-2026-11.md`.

**Abram**
- Merge this branch. The database and server (money). The SEC-09 option. Cleaning stored pins. The Android release key, and how Android testers get the app. The privacy manifest's answers. Whether flights search stays. Days out or trips as the main product, at Checkpoint 3. How many testers Test B needs. Whether to run Test D and Test E before any more building.

**A solicitor**
- The eight questions in `payment-architecture.md` §9: packages before and after 6 April 2027; affiliate links; agency for hosts; the search providers' terms; subscription law; paid-ranking wording; the trade mark; Online Safety Act duties.

**A payment provider**
- Whether a fee on a hosted experience is "travel reservation services"; reserves and first payouts; Connect fees and who carries disputes; whether fees are returned on refunds.

**Data partners**
- LiteAPI's answer on watching prices and look-to-book (unanswered). Duffel's terms for search without booking. An affiliate feed's terms. Whether a UK halal certifier licenses its list. A routing source for a second city.

**Real people**
- Does anyone prefer the personal plan (Test B)? Do they plan a second day unprompted? Will anyone pay for a day (Test D)? Will a business with guests pay (Test E)? Is "strong match" right three times in four? Can someone use it with VoiceOver?

## Technical appendix

**Checked before starting.** `main` is `80a0da3`; the live Brain's `/v1/health` reported `80a0da3`, Duffel in test mode and LiteAPI's sandbox (11 Nov, 03:24 UTC, one read-only request). The development branch was at `f8c01eb` and moved to `850ef29` during the audit (another session's sprint, m234 to m243); this branch was restarted from that tip. By 12 Nov it had moved again, to `0a677fd` (m244 to m260: Paris in development, readiness levels, an evaluation framework); that was merged into this branch, the reports were brought up to date with it, and every test was run again. The tag `friends-round-1` is not on the remote. The brief's "TestFlight 91, Android 21" could not be checked from here.

**Files read in full:** the Brain's `api.py`, `ops.py`, `schemas.py`, `db.py`, `config.py`, `ghoidc.py`, `backup.py`, `notify.py`, `share.py`, `calibration.py`, `personal.py`, `scoring.py`, `features.py`, `priors.yaml`; all four workflows; `render.yaml`; the privacy notice; the friends' round manifest; the engine evaluation. **In part:** the rest of the Brain (provider calls, the planner's entry points, food, benchmarks); the iPhone app's client, model, location, speech and project file; the Android app's manifest, build file, storage, client and map; the decision log's recent entries. **Not read:** most view code in both apps (about 20,000 lines), the research notes, the validation scripts.

**Files changed (30, all on the audit branch; nothing on `main`, in `render.yaml`, the swipe page or either app):** `brain/src/brain/` `api.py`, `ops.py`, `schemas.py`, `config.py`, `ghoidc.py`; `brain/README.md`; `brain/tests/test_hardening.py`, `test_learning_curve.py`; `brain/scripts/learning_curve.py` and its output; `.github/workflows/brain-tests.yml`; `prototype/payments/` (3 files); `prototype/day-in-relief/` (7 files); ten documents under `decisions/` and the bill of materials.

**Tests.** The Brain: 486, all passing, after merging the development branch's latest sprint (m244 to m260, at `0a677fd`) into this branch on 12 Nov. Of these, 36 come from the audit (33 for the security fixes, 3 for the benchmark). 348 passed on the development branch as first checked (`f8c01eb`), before any change. The payment prototype: 24, all passing (not run by CI). CI on the pull request: green on the commits checked. Neither app was built or run.

**Local measurements and scripts** (kept outside the repository, in the session's scratch folder, and described here so they can be rewritten): `validate_security.py` (each weakness tried against a throwaway server); `perf.py` (timings against a real server process); `prototype/day-in-relief/measure.js` (in the repository).

**Tools.** Python 3.12.3; pytest 9.2.0; pip-audit 2.10.1 (no known vulnerabilities in the 31 packages `requirements-app.txt` installs); bandit 1.9.4 (no high findings; four mediums read and dismissed); cyclonedx-bom 8.0.1 (`decisions/audit/brain-app-sbom.cdx.json`); Node 22.23.4 with Playwright 1.63.0 and headless Chromium.

**Dependencies examined.** The Brain's 11 pinned packages and the 20 they bring; the Android build file's 21 libraries (16 in the app, 5 for its tests) and 4 plugins (versions listed in `build.gradle.kts`; not scanned for vulnerabilities: no tool here); the iPhone app has no third-party packages.

**Sources.** Listed in each document, with what was read directly and what came through a search summary. Two research passes by assistants were cut short by a usage limit; what they had saved was used, the load-bearing facts were re-read directly (the package-travel amendment and its guidance date, Stripe's and Mollie's prices, Paddle's and Adyen's terms, the OSM tile policy, Apple's guideline clauses, Google's payment policy, fees and target API level, Companies House fees), and everything else is marked.

**Limits.** One reviewer, one long session, interrupted several times. A code review and local tests, not a penetration test. No phone, no Mac, no Android SDK. No access to the Render, GitHub, Apple, Google, Duffel or LiteAPI accounts. No real user data was read; every benchmark is synthetic. The legal and tax points are from statutes and official guidance read on the day and are not advice.

**Prototypes and screenshots.** `prototype/payments/` (run with `python -m pytest prototype/payments`); `prototype/day-in-relief/index.html` with `screens/flat.png`, `screens/relief.png` and `measurements.json`.

**Commits** (on `claude/pensive-euler-fftd63`, from `850ef29`): `f496b20` the security fixes; `85001c2` addresses, the benchmark, the bill of materials; `7f7a6ff` the payment prototype; `dbe8d89` the 3D proof of concept; `2263a9e` the security report; `d0a2657` payments and the business model; `d722243` 3D; `e6c426e` market and strategy; `a5e0abb` the engine; `4090106` the merge of the development branch; and the commit that adds this report, the quality audit, the opportunities list and the log entries (m261 to m265, after-9-Nov #98 and #99). Pull request: https://github.com/Abramceeeek/Sofia.K/pull/1 (a draft, into the development branch, never `main`).
