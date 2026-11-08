# Next sprint report: recommendation quality and global readiness (7–8 Nov 2026; m216–m223)

**Branch only:** `claude/vigilant-cannon-my82dj`.
- `main` is untouched at `80a0da3` (the friends' round build, TestFlight 91, Android 21).
- The live Brain answers `"version":"80a0da3"` (checked 8 Nov).
- Nothing was deployed, uploaded or published, and there were no paid API calls.
- LiteAPI live prices and `stay_dates_live` stay off.
- No Test B question changed.

The aim was Abram's: **an ODYS that makes better decisions, not just one with more screens.** No Home features were added.

## In one page

| # | Work (Abram's order) | Outcome | Decision |
|---|---|---|---|
| 1 | **Planner optimisation** | Two-stage planning built and benchmarked. 0 rule breaks in 1,056 plans, but **no clear gain at the app's 1 s** (2 better, 3 worse, within the noise floor). It helps under time pressure (0.2 s: +0.04 to +0.14). **Left off.** | m216 |
| 2 | **Budget and lunch** | Lunch stays inside the budget and steps down (café £15 → cheaper £6 → bring lunch), **never silently removed**. Fares now count. One total equals the plan's own total at every budget **from £5 to £100** (tested). An overrun is explained, with ways to change it. **Both apps.** | m217 |
| 3 | **Currency-aware comparison** | No more ranking 300 EUR below £389. With a dated ECB rate, prices are converted, the fare is kept and the estimate shown beside it. Without one, they're grouped by currency and nothing is the cheapest overall. Stays' "Cheapest" counts fees paid there. The apps no longer put £ on euros, and the trip total no longer adds euros to pounds. **Both apps. Rate fetching off until Abram decides.** | m218 |
| 4 | **Explanations from actual inputs** | Stops, stays and trip lengths carry factors taken from the algorithm's own numbers. A stay's factors **sum to the score its list is sorted by** (tested). Building it **caught a made-up line**, which is now fixed. API only. | m219 |
| 5 | **Universal onboarding preparation** | One switch (`places_mode`), off. With it on, a Londoner gets kinds of places and **stays in the Test B cohort**. A synthetic comparison of what each version lets the model learn. **Both apps.** | m220 |
| 6 | **Offline companion** | Storage audit with official sources, a design, and a tested proof of concept (the pack, freshness, sync, deletion). Two platform findings to fix after the round. | m221 |
| 7 | **School holidays** | +21 Welsh councils, Northern Ireland, France (3 zones) and the Netherlands (3 regions), all from official sources. A **coverage matrix kept as data and tested against the dates**. England: none checked, and said. | m222 |
| — | **Food (research only)** | A DPIA draft, unsigned, recommending that **the need never leaves the phone**. Found and fixed: the Brain still stored an old free-text "foods you avoid" field. Nothing for real users. | m223 |

## 1. Implemented (safe engineering, tested)

- **Budget and lunch** (`brain/src/brain/daybudget.py`, `api.personal_day`; both apps' `BudgetBlock`):
  - lunch figures are labelled estimates, never a venue or a live price;
  - `food_in_budget: false` leaves lunch out and shows it on its own line;
  - the blind pair is unchanged (no block, the usual £15 lunch).
  - **A second bug found while fixing the first:** from Greenwich, setting the fares aside squeezed lunch out, and the lunchless day won. Fixed, with a regression test.
- **Currencies** (`brain/src/brain/fx.py`, `trips.py`; both apps):
  - the ECB reference rates, crossed through the euro, rounded half-up, current for 5 days;
  - a failed fetch keeps the last good rates and never invents them;
  - Duffel prices in the account's billing currency, with exceptions (its docs), so a whole result set in USD is the likelier case. That's handled too.
  - A note says when fares include different bags. Bag prices aren't fetched: that would be an extra Duffel request per offer.
- **Explanations** (`brain/src/brain/explain.py`): each factor has kind, effect, text, value and source, plus what isn't known. **Never for the blind pair.**
- **Onboarding switch** (`onboarding.yaml` `places_mode`; `usesKinds` in both apps).
- **Food guard:** `foods_avoided` (D19, unasked since D123) is accepted from older builds and dropped, never stored. A test guards against any food, diet, belief or allergy field.
- **School holidays:** 30 areas in `school_holidays.yaml`, with `coverage.yaml` cross-checked against them.
- **Offline rules** (`brain/src/brain/offline.py`): the reference for both apps, tested on their demo trip.
- **Test fix:** a TfL test failed every Sunday ("3 days from today" was the table's own reference Wednesday). Test only, checked for all seven weekdays.

## 2. Research or design only (nothing built for users)

- **Two-stage planner:** built, off (`SEEDED_WITH_BLOCKS = False`). It can be switched on after a fresh benchmark on a busier server.
- **Offline companion:** the app screens (~6 h) wait for Abram's view of the design.
- **Food needs:** the DPIA draft, separate-consent wording, the phone-only design, certifier research. **No screen, storage or consent is built** (m215 decision 4).
- **Onboarding:** the synthetic comparison. It's model-level only, and **no conclusion is drawn about how people find the questions.**

## 3. Decisions for Abram

1. **ECB rates on?** (`fx_rates_live`, one line.) Recommended: on, with the live flight keys, after the round.
2. **Where explanations show in the apps.** Recommended: "Why this stop" on the stop card, after the round.
3. **Kinds of places for everyone:** flip `places_mode: kinds` after the round, and check the eight kinds' wording (~0.5 h).
4. **Offline:**
   - the 30-day deletion after a trip (GUESS);
   - build the iPhone backup exclusion (~0.5 h) and the Android token move (~2 h);
   - the "Offline" view on "Now" (~6 h).
5. **Food:** the DPIA. Read it, decide the Article 6 basis, then sign off or send it to a solicitor. Separately, check the live Brain for any old `foods_avoided` values and delete them.
6. **School holidays:** read the 7 blocked English councils by hand (~10 min each), or wait for real travellers' areas.
7. **The planner's next pass** (from m216 and the demo days):
   - shorten the strict first search when it can't succeed (p90 2 s on small catalogues);
   - look at long waits before a card's visiting window (a 2-hour gap in one demo day).

## 4. Unsafe, unverified or limited

- **UNVERIFIED** (pages refused automated reading or didn't say), so a person should check these:
  - whether Apple backs up Application Support;
  - whether Keychain items outlive the app;
  - the ICO's DPIA template headings;
  - whether the Halal Food Authority has a directory;
  - whether the Halal Authority Board exists as a certifier;
  - which académies are in each French zone;
  - which provinces are in each Dutch region;
  - all 7 English councils tried (403/404).
- **GUESS thresholds**, all constants in code and named in the docs:
  - lunch £6 and £15;
  - 5 days for a current rate;
  - 90 days for a card's facts;
  - 7 days for a stale plan;
  - 30 days to keep a trip offline;
  - the onboarding simulation's familiarity rates.
- **Rates are estimates** (the ECB: "for information purposes only"). The fare in its own currency is always what's paid.
- **The Ascension bridge (France)** is left out because the data's row is ambiguous.
- **The demo trip, benchmark and onboarding results are synthetic.** Nothing here is evidence about real people.

## 5. Regressions

- **None found.** Every suite passed at each commit (below).
- **Behaviour that intentionally changed:**
  - stays' "Cheapest" now includes fees paid at the property;
  - facet rows now carry a currency (one test updated);
  - `triplength` returns two more keys (`best`, `capped`);
  - plan responses gain `budget` and per-stop `explain`;
  - flight and stay responses gain `estimate` and `compare_notes`.
- All new keys are additions. The frozen builds ignore unknown keys (both apps decode leniently), and nothing was removed from a response.
- **`foods_avoided`** is still accepted (older builds may send it) but no longer stored. That's the intended change.

## Tests and builds

| | Start of sprint | End |
|---|---|---|
| Brain (pytest) | 281 passed | **335 passed** (+54: budget 25, currency 9, explanations 6, offline 4, school coverage 5, onboarding switch 2, food guard 1, two-stage 2) |
| Android (unit + screenshots, Robolectric) | 98 | **102 passed** (planbudget, flightscurrency, categories-everyone, money estimates) |
| iPhone (CI, simulator, no upload) | run #101 success | **#102 success** (m217; the `planbudget` screenshot checked: "Your budget £30", lunch £15, fares £6, £9 left). **#103** (m218 + m220) compiled; screenshots pending at writing. **#104** for the final head (m223's model change) to follow |

New screenshots:
- iPhone: `planbudget`, `flightscurrency`;
- Android: `09g-planbudget`, `26b-flightscurrency` ("367 EUR / ≈ £306 · ECB rate of 6 Nov 2026"), `06c-categories-everyone`.

## Commits (branch)

`6d076b7` m216 · `cde0259` m217 · `d75876c` TfL test fix · `edca2e7` m218 · `466c737` m219 · `6058712` m220 · `fc5d6c8` m221 · `b1cd91c` m222 · `12f1d23` m223

## Hours

| | Claude | Abram |
|---|---|---|
| This sprint | ~25 h (planner 3, budget 4, currencies 4, explanations 3, onboarding 3, offline 3, school holidays 2, food 2, report 1) | none during it. The decisions above: ~2–3 h, mostly the DPIA read and the onboarding wording |
