# Food discovery and Seville: the 20 Nov sprint, and the friend's trip on 22 Nov

**Decision first.**
- **No in-app Seville pilot on 22 Nov.** TestFlight build 112 and the Android build can't show Seville. Both apps send `london` as every trip's destination. Help & safety and the offline card print 999, which is wrong in Spain.
- Seville itself stays **Development**: 5 kinds of place (6 needed), and no official transport data.
- **What can go ahead, if you approve:** you send the friend a reviewed list yourself, outside the app: `decisions/seville-preview-draft.md`. It says 112, says not to rely on it alone, and shows each place's state for each day from 22 to 28 Nov.
- **Food stays a category, not a new system.** Markets are told apart from restaurants. No dietary data was added.

Work on `claude/pensive-euler-fftd63` only. Nothing was deployed, merged into `main`, uploaded, published or changed in production. The live Brain is still `ca6fd69`, and TestFlight is still build 112.

**Hours:** about 7 h of Claude's work. Abram: about 20 min to review the preview sheet and decide (§16).

---

## 1. Food architecture: recommendation

Three options were considered:
- (a) food as an ordinary category;
- (b) food as a specialised type;
- (c) a separate food entity (venues, stalls, menus).

**Recommendation: keep what exists, which is (a) and (b) together. Don't build (c).**
- A food place is an `Experience` with `category: food_drink`.
- Its `type` is one of market, restaurant, cafe, bakery, street_food, food_street or bar.
- `FoodFacet` adds `service` (market / sit_down / counter / street), `cuisine`, `meals`, `price_range` and `reservations`.
- **A market and a dining business are different records:**
  - `type: market` with `service: market`, versus `type: restaurant` with `service: sit_down`.
  - A market's hours are the market's own. Stalls are not separate records, so the market's hours are never given to a stall.
  - Where the source says stall hours vary, that is a notice on the market ("Stall hours vary: 'algunos abren días y horas diferentes'", Mercado de Triana). Bars inside a market are named in the hours text with "keep their own hours, not stated".
- **No dietary field exists, and none was added.**
  - `FoodFacet` has no dietary, halal, vegetarian or allergen field. A test now fails the build if one appears (`test_no_dietary_claim_is_data`).
  - A venue's own dietary words are kept as a YAML comment only, never as data (Arte y Sabor).
  - Food preferences stay off. No persistence, no profile transmission and no analytics.

**Why not (c).** It would need its own hours, prices, evidence and planner rules, for a catalogue of 12 ready food places. Nothing in Test B or the friend's trip needs stall-level data.

## 2. Food changes in this sprint

- **The model is unchanged.**
- **One parser fix (m318), `catalogue.parse_hours`:**
  - Split hours like "Mon-Fri 09:00-15:00, 17:30-20:30" lost their morning session. The second range replaced the first.
  - Both sessions are now kept.
  - "…-00:00" now closes at midnight.
  - Hours that run past midnight are left as text only, never guessed.
- **What it changes today:** 0 London places and 0 Paris places. It matters for Spanish split hours, starting with the Mercado del Arenal.

## 3. London food coverage (6 ready cards)

Re-read on 20 Nov, official sites only:
- Borough Market and Beigel Bake: unchanged.
- St Martin-in-the-Fields: the site refused the read (403).
- The other three were not re-read.

**No London card was changed. The London catalogue is the round's data.**

| Card | Type / service | Hours | Price | Step-free | 20 Nov re-check |
|---|---|---|---|---|---|
| Borough Market | market / market | Weekly table, official, read 11 Nov | £15, ODYS estimate (entry is free) | yes (checked) | **Same hours.** The site also says "Opening times vary during the festive period and at Bank Holidays". **Its access text is mixed:** "single ground-floor level, so have no need for lifts or stairs", but also "some cobbles, with some areas harder to access" → proposal P2 |
| Beigel Bake | bakery / counter | "Open 24 hours, 7 days a week", official | £7.50, ODYS estimate | unknown | **Same hours.** Address "159 Brick Lane, London E1 6SB". Menu prices were seen only in a summarised page, so they stay estimates |
| Meet Bros Steakhouse | restaurant / sit_down | Weekly table, meetbros.co.uk, read 11 Nov | £60, ODYS estimate | unknown | Not re-read |
| West End outdoor dining | food_street / street | General text (Regent Street Online); no table, so never "confirmed open" | £45, ODYS estimate | unknown | Not re-read |
| Gerrard Street, Chinatown | restaurant / sit_down | "Restaurants' own hours"; source "the card (research)", 28 Sep | £20, ODYS estimate | partial | Not re-read |
| St Martin-in-the-Fields crypt | cafe / counter | "usually 11:00-17:00"; source "the card (research)", 28 Sep | £12, ODYS estimate | yes | **403 on 20 Nov** |

**Gaps across all six cards:**
- Every price is a planning estimate from September, not a printed price.
- There is no website field. The hours source is the closest thing.
- Indoor or outdoor is guessed from the card's tags.
- Two cards (Chinatown, St Martin) have no hours URL, so the Brain can never say "confirmed open" for them. That is correct.

**Candidates read, but not added:**
- **Camden Market** (camdenmarket.com/visit-us, 20 Nov): market 10:00-19:00, food halls 11:30-23:00, "individual times may vary". No prices and no access statement. Its banner dates print no year.
- **Maltby Street, Seven Dials Market, Mercato Metropolitano, Leadenhall:** not read. No official URL had been confirmed, and none was guessed.

## 4. Seville food: 6 ready, 3 drafts

All six ready places come from official pages read on 20 Nov 2026. Currency is EUR. The catalogue has no street-address field, so each location is the official address or name looked up in OpenStreetMap (Nominatim), with the OSM id kept.

| Place | Kind | District | Hours as printed (source) | Price | Step-free | Setting |
|---|---|---|---|---|---|---|
| Mercado de Triana | market | Triana | Mon-Sat 09:00-15:00 for the stalls. Some stalls differ, and bars and the cookery class keep their own hours (mercadosdesevilla.es/…/triana) | not printed | unknown | indoor |
| Mercado de Feria | market | Casco Antiguo | Mon-Sat 08:00-15:00 for the stalls; 3 named bars keep their own hours (…/feria) | not printed | unknown | indoor |
| Mercado de la Encarnación | market | Casco Antiguo | Mon-Sat 08:00-15:00 (…/encarnacion) | not printed | unknown | indoor |
| Mercado del Arenal | market | Casco Antiguo ("C. Pastor y Landero, 4") | Mon-Fri 09:00-15:00 and 17:30-20:30; Sat 09:00-15:00 (…/del-arenal) | not printed | unknown | indoor |
| Arte y Sabor | restaurant | Casco Antiguo ("Alameda de Hércules 85, 41002") | Every day 13:30-23:30 (arteysabor.es). Cuisine "Spanish, Moroccan and international fusion"; online reservations | not printed | unknown | mixed |
| Casa Robles | restaurant | Casco Antiguo | Mon-Sun 12:30-24:00 (casarobles.es). Bookings: a €20-a-head fee for a no-show or a cancellation under 8 h | not printed | unknown | indoor |

- **Drafts, never recommended:** El Rinconcillo, Espacio Eslava and Bodeguitas Antonio Romero. Their own sites print no opening hours. Antonio Romero's menu prices are recorded as `claimed` (a montadito €4.20).
- **All four municipal markets are closed on Sundays,** and the friend arrives on a Sunday. The Brain says so: "closed or unavailable".
- **Food prices:**
  - No ready food place prints a price, so each shows "not printed".
  - The Brain gives no typical-spend allowance in Seville, because too few comparable, dated food prices exist.
  - Nothing is converted to pounds without a dated rate.

## 5. Seville coverage

- **20 ready, all located from a named source:**
  - 11 culture: Alcázar, Cathedral, Bellas Artes, Pilatos, Dueñas, Lebrija, Baile Flamenco, CAAC, Archivo de Indias, Artes y Costumbres, Plaza de España;
  - 1 view: Setas;
  - 1 park: María Luisa;
  - 1 area: Triana;
  - 6 food (above).
- **Readiness (`readiness.checklist`):** **Development.**

| Check | Result |
|---|---|
| emergency, holidays (BOE 2026 and 2027), currency, time zone, 20 located experiences | pass |
| **variety** (essential) | partial: 5 kinds, 6 needed |
| **transport** (essential) | fail: missing |
| hours from an official page within 180 days | partial: 15 of 20. Four come from the city's June 2025 leaflet, and the CAAC page is not https |
| step-free from a named source | partial: 3 of 20 |
| school holidays | fail |
| photos | none yet |

- Seville's own local holidays are not included. The BOE lists only the national and Andalusian holidays.
- Seville is in `data/dev/seville.yaml`, which no route, trip or plan reads. A test checks that it never appears in `destinations.yaml` or `airports.yaml`.

## 6. Emergency number: Spain, verified

`data/emergency.yaml` now has `ES` (checked 20 Nov 2026):
- **112: ambulance, fire and police,** "free from landlines and mobiles". Source: administracion.gob.es, the numeros-urgencia page (updated 01-10-2026). It agrees with GOV.UK's Spain travel advice ("Telephone: 112").
- **The EU page** (digital-strategy.ec.europa.eu/en/policies/112, updated 5 Nov 2026): "available everywhere in the EU, free of charge".
- **Not listed:** the other Spanish numbers (061, 091, 092 and so on). They were not checked line by line.

What this changes:
- The Brain's offline pack for a Spanish trip now gives 112 and never 999 (tested).
- **The apps do not use it.** Both apps print 999:
  - iPhone: the automatic safety reply (`app/Sources/BrainClient.swift:148`) and the offline card (`app/Sources/Offline.swift:33`);
  - Android: the offline card (`android/app/src/main/java/com/odys/app/Offline.kt:66`) and the You screen, "Emergency? Call 999 first." (`Trips.kt:1523`).

## 7. Transport: unavailable, said so

- **No official journey planner was readable:**
  - TUSSAM (city buses): 403;
  - Metro de Sevilla: no fares or hours on the page read;
  - Consorcio de Transportes: DNS failure.
- The November 2024 map was not used as proof.
- **The Brain gives no journey times, and no real-time arrivals.** Nothing was invented.
- **The airport is the one exception,** from Aena, the airport operator:
  - **Bus:** EA bus €6 single or €8 return, card payment on board.
  - **Taxi:** fixed fares, €26 (Mon-Fri 07:00-21:00) or €29 at other times.

## 8. Weather: AEMET, assessed and not integrated

- **What AEMET's Seville page (sevilla-id41091) offers:**
  - a 7-day table and 48 hours by the hour;
  - rain probability, temperature, wind and UV;
  - re-use is allowed when AEMET is credited.
- **AEMET OpenData is free,** but it needs a key, and its terms were not readable (opendata.aemet.es returned no text).
- `weather.py` is the Met Office and covers the UK only. **No Seville forecast is shown anywhere.**
- **To integrate it:** about 3–4 h, once Abram has a key and has read the terms. It is not in this sprint.

## 9. Benchmark: 11 synthetic travellers, default ranking

`scripts/benchmark_seville.py` → `benchmarks/synthetic/profiles_seville.txt`.

**These are synthetic people, not evidence about anyone.** The default rule (doubts first) was used, unchanged.

- **Mean p(Good):** London 0.76, Seville 0.72.
- **The museum lover's taste transfers:** 100% culture in both cities.
- **Others' own kind in their Tuesday top 5:**
  - architecture: 100% London, 80% Seville;
  - active: 60%, 20%;
  - entertainment: 40%, 0%.
- **Finding: the food lover is shown no food, in either city.**
  - In Seville, their five best matches by the model are all food places (p(Good) 0.93–0.96; in London, Beigel Bake at 0.95 leads).
  - But the "doubts first" rule ranks every food place below fixed-price museums, because a meal's price is always an estimate or unknown.
  - With the experimental weighted rule (`doubt_cost 0.10`), one food place appears.
  - **This is not fixed.** The default ranking stays unchanged during Test B.
  - It affects only `quality.rank`. That is used by the development-only international discovery and the benchmarks, not by the live London planner.
  - Proposal P1 is below. A test records the finding.
- **The accessibility-focused traveller:** only 20% of their Seville top 5 is "good" on practicality, because step-free is unknown at most places. Unknown is never read as "no".
- **On Sunday 22 Nov:** the food lover's top 5 has two places the venue confirms are open (Baile Flamenco, Lebrija) and three marked "might be open".

## 10. Tests

New: `tests/test_seville.py`, 20 tests.

| Area | What is checked |
|---|---|
| Destination registration | Not in the registry; ids `xp:es:seville:*`; ES, EUR, Europe/Madrid |
| Time zone and date boundaries | 23:30 UTC on Sun 22 Nov is already Monday in Seville and still Sunday in London |
| Clock changes | +1 h on 22 Nov; +2 h after 01:00 UTC on 28 Mar 2027 |
| Sunset | Seville 18:10, against London's 16:04 on 22 Nov |
| Emergency number | ES = {112}, https sources, never 999 or 111; the offline pack gives 112 |
| Currency | EUR kept; no conversion to pounds without a dated rate; with the rate, €12 = £10.01 |
| Paid, free and unknown prices | Free = 0; unknown food prices stay unknown, with no allowance |
| Market and restaurant | Kind and service told apart; the stall-hours notice |
| Unknown hours | Drafts have none and are never ready |
| Expired check | Official hours read too long ago → "might be open", never "confirmed open" |
| Leaflet hours | Never "confirmed open" |
| Dated closure | The Cathedral is "closed or unavailable" on 8 Dec 2026 |
| Unverified access | Unknown step-free → "fair", never "no" |
| Unverified dietary claims | No dietary field; no dietary words in the data |
| Missing transport and weather | Recorded as missing or not integrated |
| Readiness | Development, even with Abram's review |
| Recommendation portability | The museum lover gets all culture, all practicable |
| Food finding | The food lover's best matches are food; the experimental rule surfaces one |
| Parser | Split sessions, midnight, past midnight; the old London case unchanged |

`tests/test_destination.py` was updated for the new ES entry.

**Results (20 Nov):**
- Before the update: 570 passed, 1 failed. The failure was the old test, which pinned the four countries.
- After it: **the full Brain suite passes, 571 of 571** (Python, SQLite, 165 s).

**Not run, and why:**
- **Postgres:** no database server here. CI runs it on push.
- **Android and the iOS simulator:** no app file changed, so no new build is needed.

## 11. Screenshots

None. No app screen changed, and neither app can show Seville.

## 12. What works in the existing builds (iPhone 112, Android)

- **London food:** works as before.
- **Seville: nothing.** No screen, plan, trip or search offers it, and the Brain's live registry is London only.
- **Nothing here reaches the friends' round:** it is on the branch, not deployed.

## 13. What needs a new app build (not started; needs approval)

| Change | Hours | Why it's needed |
|---|---|---|
| A destination choice in Trips, from the Brain's list, in both apps | 3–4 | Both apps hardcode `london` (`TripModels.swift:519`, `TripModels.kt:431`) |
| Emergency numbers from the trip's country | 2–3 | Help & safety and the offline card print 999. Spain needs 112 |
| A clear "Preview: not fully supported" label, with what's missing | 1–2 | So a Preview city can't pass for a supported one |
| CI for both apps, and the screenshot pages | 1 | As for every app change |

- **Then:** a TestFlight build from `main`, which the round has frozen. External testers also need Apple's beta review.
- **So none of it can reach a phone by Sunday** without breaking the freeze.

## 14. What needs a Brain deploy (not started; needs approval)

- Moving Seville from `data/dev/` into the registry, behind the readiness gate.
- **It can't rise above Development until:**
  - a sixth kind of place is added (for example a show or an activity, from official pages);
  - transport has official data, or is shown as "no journey times" and accepted as such by the gate.
- **Abram's review is then needed for Preview.** Supported needs more.
- **The ES emergency entry and the parser fix** ship with the next Brain deploy, whenever that is. Neither changes anything for London.

## 15. Unverified, or not read

- **Bus, metro and journey planner:** TUSSAM (403), Metro (no data), CTAS (DNS).
- **AEMET OpenData's key and terms.**
- **Four places' hours come from the city's June 2025 leaflet:** Archivo de Indias, Artes y Costumbres, Plaza de España, Triana. Their prices, where given, are `claimed`.
- **Prices not printed:** Bellas Artes, all 6 food places.
- **Step-free:** known for 3 of 20 (Bellas Artes, Baile Flamenco, Setas). Not checked for the rest.
- **Setas:** its two pages disagree on cancellation (24 h or 2 h). Kept as a notice.
- **Not read:** Hospital de los Venerables, Torre del Oro cruises and Lonja del Barranco (503 twice); the Junta's Bellas Artes page (503; the city's page was used instead).
- **Others:** Seville's local holidays, and Spanish school holidays.
- **Arte y Sabor's** vegetarian, vegan and intolerance wording is the venue's claim, not verified. It is kept as a comment only.

## 16. Can the friend safely take part on 22 Nov?

**In the app: no.**
- The builds can't show Seville.
- The safety screen would tell them to call 999.
- Making it work needs a new build from the frozen `main`, a Brain deploy and Apple's review.

**Outside the app: yes, if you approve it and send it yourself.**
- **The sheet:** `decisions/seville-preview-draft.md`, generated by `scripts/seville_preview.py` from the same data. It gives, for each place:
  - the hours as printed, with the source and the date read;
  - the price, or "not printed";
  - step-free, or "not known";
  - open / check / **shut** for each day from Sun 22 to Sat 28 Nov.
- **It starts with:**
  - **112;**
  - "Please don't rely on this alone";
  - the fact that the app's 999 does not apply in Spain;
  - the markets' Sunday closure.
- **The conditions:**
  - You read it before sending.
  - The friend uses the venues' own sites, a maps app and AEMET for hours, bookings, transport and weather.
  - Nothing is collected through ODYS. Their trip is **not** Test B evidence, and nothing goes into the Brain.
- **What's still missing:** a few lines about the friend's own trip, to put above the sheet.

---

## Status, kept apart

| | |
|---|---|
| **Implemented** | Seville development destination (20 ready, 3 drafts); ES emergency entry; the split-hours parser fix; `benchmark_seville.py`; `seville_preview.py` and its draft sheet |
| **Tested** | §10: 20 Seville tests and the updated destination test; the full Brain suite |
| **Verified from official pages (20 Nov)** | 112 (Spanish government and EU); 16 of 20 Seville places' hours (15 within the "official" rule, plus CAAC on http); the 4 markets and 2 restaurants; Aena airport bus and taxi; BOE holidays; Borough Market's and Beigel Bake's London hours |
| **Development only** | Seville and everything about it; the preview sheet (a draft, not sent) |
| **Awaiting Abram's approval** | Sending the preview sheet (§16).<br>**P1:** food's typical-spend estimate shouldn't count as a doubt in `quality.rank`, or adopt the weighted rule. After the round.<br>**P2:** Borough Market step-free "yes" → "partial", with the site's cobbles note. After the round.<br>The app changes (§13) and the Brain deploy (§14).<br>An AEMET key |
| **Not implemented** | In-app Seville; Seville transport and weather; Preview or Supported status; food preferences of any kind (halal, allergies, religious preference, dietary profiles or analytics); new London food cards |
