# Destination quality and international validation: report (12 Nov 2026; m244–m251)

Abram's decisions and five workstreams (m244), built on the branch `claude/vigilant-cannon-my82dj`. The aim was to prove that ODYS's intelligence transfers beyond London, not just that its architecture can store international data. **The short answer:**
- **Partly.** The model, the catalogue and the quality checks work in Paris without London assumptions, once one bug was fixed: euro prices were scored as free.
- **Data is the limit, not code.** London itself only reaches "preview" by the new bar: step-free access is known for 17 of 49 places.
- **Paris stays in development:** 19 places are ready, one short of 20, and there are no official transport facts yet.

## 1. Repository and branch state (checked 11–12 Nov)

- **`main`** is unchanged at `80a0da3`.
- **The live Brain** answers `"version":"80a0da3"` (11 Nov).
- **The tag `friends-round-1` doesn't exist on GitHub yet**, so the friends' round hasn't started. Its manifest's "before the first invite" steps are still Abram's.
- **The branch** was clean at `850ef29` before this sprint. It now has 5 sprint commits; the 5th holds this report and the documents.
- **Nothing differs from the earlier reports.** Every item Abram listed exists on the branch as reported:

| Item | Where |
|---|---|
| Catalogue | `catalogue.py`, m235 |
| Universal onboarding | `categories_global.yaml`, m229, not served: `places_mode` stays `named` |
| Offline Now | `Offline.swift` and `.kt`, m228 and m236 |
| Explanations | `explain.py`, m230 and m241 |
| Android token | Keystore, m227 |
| Multi-city | `itinerary.py`, m237 |
| Currency | `fx.py`, m238 |
| Group | `group.py`, m240 |
| Food DPIA | `dpia-food-needs.md`, unsigned |
| School holidays | `coverage.yaml`, m225 |

- **None of this is in the friends' round builds** (TestFlight 91, Android 21). They come from `main`.

**The release rules held:**
- no `main` commit, no deploy, no TestFlight upload (iOS run `upload: false`), no APK published;
- no paid API, no LiteAPI live prices, no ECB fetching, no food collection;
- no onboarding change and no new database table;
- no live data touched.

## 2. Already done in earlier sprints (not rebuilt)

The catalogue model, destination profiles, multi-city prototype, display currency, discovery, group prototype, explanations, food-interest study and the first photo test (m234–m243, `global-destination-intelligence-report.md`). This sprint extended them; nothing was rebuilt.

**Catalogue architecture: "global does not mean identical"** (Abram's section 2). The common core plus one facet per kind holds. This sprint added each kind's own attributes, every one a fact that defaults to unknown (`catalogue.py`):

| Kind | Its own attributes |
|---|---|
| **Restaurant** | Cuisine, meals, menu price range, whether reservations are taken. **No dietary field:** a venue's halal or vegetarian claim can only enter through `food.py`'s evidence model, after the DPIA and the solicitor (tested) |
| **Museum** | Booking rule, dated exhibitions; admission is the core price; duration the core duration; access the core |
| **Outdoor** | Weather dependence, terrain, closing at dusk, seasonal notices |
| **Entertainment** | A new facet. Sessions listed per event, ticketing, age limit. No invented opening hours |
| **Activity** | Age limit (K1 Speed: "14 and older") |
| **Every kind** | **Dated notices** (closures, works, seasons, events); step-free as yes, partial or no with the source's own words; a district (borough or arrondissement) |

It added no new layers, and no kind is forced into another's shape.

## 3. London catalogue coverage, before and after (`brain/benchmarks/coverage/destination_coverage.md`)

Every London place's official site was read on 11 Nov; each fact keeps its URL (`data/catalogue/london_checked.yaml`).

| Measure (of 49) | Before | After |
|---|---|---|
| Location matched to a named Wikidata item within 400 m | not checked | **47** (two walks have no single item; Burlington Arcade and the Soane matched a neighbouring building) |
| Area named by an official page / only by the card's title / none | 0 / 28 / 21 | **12** / 19 / 18 |
| Hours read on an official page in the last 90 days | 0 | **28** |
| Hours as a weekly table | 25 | **24** |
| Step-free yes / partial / no, from a named source | 4 / 0 / 0 | **9 / 8 / 0** |
| Price checked on an official page | 0 | 8 (33 more were checked on the card in Sept–Oct) |
| Dated notices | 0 | **14** |
| Outdoor places with seasonal information | 11 of 22 | **14** of 22 |
| Photo pages re-read one by one | 6 | **45** |

- **Hours as a table went down, from 25 to 24, on purpose:** Greenwich Park's gates change with the season, so it's text, not a table. This is Abram's rule: "25 reliable … rather than 49 … incorrect".
- **Some hours now use only the page's plain weekly wording**, so the parser isn't fooled by "usually" or by festive dates (the National Gallery, the Courtauld, the Soane). The festive dates became dated notices. A test checks that the parsed times are in the page's own text.

## 4. Outstanding data-quality problems

- **13 London pages couldn't be read** (403, an empty page, a PDF, collapsed text). Nothing was filled from elsewhere:
  - the British Museum;
  - the National Portrait Gallery;
  - Liberty;
  - St Martin-in-the-Fields;
  - the Southbank Centre;
  - King's Cross;
  - Canary Wharf;
  - Westminster Council (Victoria Embankment Gardens);
  - Horizon 22's access answer;
  - St Paul's Evensong schedule;
  - Battersea Park;
  - St Dunstan-in-the-East;
  - the Millennium Bridge.

  These need a person to read them, ~15 min each.
- **Step-free access is still unknown for 32 of 49.** No page said, and nothing was guessed.
- **Where an official page differs from the card the planner uses** (no plan was changed; for Abram):
  - **The Courtauld:** the card plans £12; the page now lists £14 and £16, without saying which includes a donation.
  - **Uber Boat Greenwich to Battersea Power Station:** the page doesn't say which fare zone covers it, so the card's £22.90 is unconfirmed.
- **Old Spitalfields Market:** the official site's two pages disagree on weekday closing (18:00 or 20:00). The hours are kept as text and say so.
- **Current notices that change a visit:**
  - the Somerset House courtyard is an ice rink until 10 Jan;
  - the QEOP fountains are closed until 31 Mar;
  - the Richmond Park deer cull;
  - the Bank of England Museum closes early on 27 Nov;
  - the National Gallery's east wing closes early on 17 Nov.

## 5. Paris prototype (`brain/data/dev/paris.yaml`; development only)

- **23 records, 19 ready, 4 drafts.** A draft is never recommended, because something essential couldn't be read:
  - the Palais Garnier's hours;
  - the Jardin du Luxembourg's hours (503);
  - the Petite Ceinture (no hours published);
  - the Batobus (every stop listed "closed", undated).
- **Kinds of experience:**
  - culture and history (8);
  - parks and views (3 ready);
  - food (3);
  - shopping (2);
  - entertainment (2);
  - a canal walk;
  - unusual places: the Catacombs, the sewers museum, the Chasse et Nature museum and the Coulée verte.
- **Five candidates couldn't be read and aren't included:** the Orangerie, the Arts Forains, La Grande Épicerie, and the Marais and Île Saint-Louis walks, which needed the tourist office's site.
- **Every fact has its source:**
  - locations from Wikidata, or OpenStreetMap for Chartier;
  - arrondissements as printed (8), or from the printed postcode (11, marked estimated);
  - hours, prices and access from each official page, read 11 Nov;
  - public holidays for 2026–27 from service-public.gouv.fr;
  - school zone C (already checked, m225);
  - emergency numbers for France (m236).
- **Nationality pricing:**
  - **The Sainte-Chapelle and the Palais Garnier charge more outside the EEA.** ODYS records the range, budgets with the higher price, and **never asks nationality**.
- **No photos:** none is added until each is checked (Abram).
- **No London assumptions in the data model** (tested): FR, EUR, Europe/Paris; prices never in pounds; Paris isn't in the registry, so no route or trip can offer it.
- **Coverage (of 19 ready):**
  - hours read on an official page: 17 (the other 2 are event-based: sessions per concert or film);
  - step-free known: 12 (7 yes, 4 partial, 1 no: the Catacombs' 131 steps);
  - prices known: 14.

## 6. Recommendation benchmark (`brain/benchmarks/synthetic/profiles.txt`)

**Set-up:**
- 11 synthetic travellers, as Abram listed them;
- each is a set of model weights plus at most one stated rule (a budget, step-free access). **Nothing is inferred about anyone.**
- Top 5 on a Tuesday and a Saturday, in London (49) and Paris (19).

**What it found:**
1. **A bug: euro prices were scored as free.** The scorer dropped any price not in pounds, so the €31 Catacombs looked free to every traveller. **Fixed** (`discovery.cost_gbp`): a rate converts it, and without one the price is unknown, never zero (tested).
2. **Relevance transfers where the model has the feature:**

| Traveller | Their own kind in London's top 5 | In Paris's top 5 |
|---|---|---|
| Museum lover | 100% | 80% |
| Architecture lover | 100% | 80% |

   Travellers the model can't represent don't transfer: the shopping lover gets 0% in London and 20% in Paris, because the model has no shopping taste (m229). The report says so rather than pretending.
3. **The quality ranking puts any doubt before relevance**, so complete data can beat a better match. A nature lover's Paris top 5 led with the Galerie Vivienne (an arcade), because the parks' hours change with the season and so count as a doubt. **A weighted rule** (each doubt costs 0.10 of the chance of "Good") was tested against today's rule:

| Rule | City | Chance of "Good" | Own kind | Practicality good | Money good | Trust good |
|---|---|---|---|---|---|---|
| Doubts first (today) | London | 0.76 | 46% | 96% | 100% | 100% |
| Doubts first (today) | Paris | 0.70 | 37% | 62% | 100% | 100% |
| 0.10 a doubt | London | 0.80 | 51% | 75% | 98% | 100% |
| 0.10 a doubt | Paris | 0.76 | 46% | 45% | 95% | 93% |

   **The default is unchanged; Abram decides** (section 14). Under either rule, a place a source says is poor on any perspective still ranks last.
4. **Accessibility:** a stated step-free need is now a rule. A place a source says isn't step-free never appears (0 in both cities), and unknown access is said, never read as "no".
5. **Sensitivity to missing information:**
   - **Price:** imputing an unknown price at the city's median changes 2–3 of Paris's top 5, and none of London's, where every price is known. So the 5 unknown Paris prices matter, and the money check says "unknown".
   - **Access:** hiding all step-free facts changes 2 of London's top 5 for the accessibility traveller.
6. **Popularity is not an input to these rankings.**

**Not measured:** real people's ratings. The model's weights are its own prior. Shopping, entertainment, architecture and family have no feature of their own (proxies are listed), and **no child-suitability data is held or inferred**.

## 7. Photos: attribution and licensing (`brain/data/photo_checks.yaml`, `design/photo-credits.md`)

All 45 Commons pages were re-read one by one, a few a turn (the API refused this container with 429; nothing was retried in a loop). The Creative Commons legal code was read for each licence used.

| Finding | Count | What was done |
|---|---|---|
| Credit matches the page | 44 | — |
| The page asks for a different credit | 1 | **Fixed in both apps:** "David Iliff" (the page: "Photo by DAVID ILIFF"), not "Diliff" |
| The page states its licence two ways | 1 | Richmond's deer: CC BY 4.0 in the text, CC BY-SA 4.0 in its data. Flagged; treat as BY-SA until resolved |
| Shows the place / something related / 15+ years old | 26 / 4 / 15 | Listed for Abram's own photos to replace first (Burlington Arcade is from 1987; Canary Wharf from 2008) |
| Commercial use and modification | all 45 permit both (CC0, CC BY, CC BY-SA; no NC or ND) | — |

**Legal questions this raises, for a solicitor** (a passing test doesn't prove legal use; Abram):
1. **The share card omits the title and the licence link.** CC BY and BY-SA 2.0, 2.5 and 3.0 ask for the title "if supplied", and every version asks for the licence's URI.
2. **The share card crops the photo and lays text over it.** If that is an adaptation, CC BY-SA requires the share card itself to be under BY-SA. 33 of the 45 photos are BY-SA (9 CC BY, 3 CC0).
3. **Two Acabashi photos** (Old Spitalfields, the Uber Boat) say social-media use is excluded unless the platform enforces CC terms. That conflicts with the share card's purpose.

**Recommended, not built:** until the solicitor answers, the share card uses only CC0 or CC BY photos (12 of 45; the rest share without a photo), adds the title, and puts the licence link in the share text. Both apps, ~2 h.

## 8. Group travel: fairness findings (`brain/benchmarks/synthetic/group_scenarios.txt`)

**Set-up:** Abram's nine cases, 60 synthetic groups each, Nash against least misery and the plain average, London's 49 experiences.
- **No hard rule broke under any method:** no rejected place, no place a source says has steps when someone needs step-free, and no day over the smallest budget left unsaid.
- **Results:**

| Case | Nash | Least misery | Average |
|---|---|---|---|
| Groups of 2 | least happy 0.70, everyone a favourite 90% | 0.72, 77% | 0.66, 93% |
| Groups of 10 | least happy 0.34, everyone a favourite 45% | 0.42, 20% | 0.25, 27% |
| One demanding member: share of stops from their own top 20%, against each other member's | **49% against 43%** | 44% against 41% | **77% against 39%** |
| Similar tastes | all three about the same (0.76) | | |
| One member with nothing that suits them | satisfaction ~0.01, and **the plan says so** | | |

- **Reading:** least misery always gives the least happy member most, but leaves the most groups without a favourite for everyone. The average lets one member take the trip. **Nash stays the balance**, as Abram decided (m244). For groups larger than 6, no method satisfies everyone in a 6-stop plan.
- **New rules:**
  - **A step-free need:** a place a source says has steps is out, and unknown access is flagged (or excluded, if the group asks).
  - **A member there for only some days** leads one of them and is judged on those days.
  - **No group accounts** were added.

## 9. School holidays

**Inspected first, nothing repeated:**
- **Already covered:**
  - Wales (all 22 councils);
  - Edinburgh;
  - Northern Ireland;
  - in England, Westminster, Birmingham and Leeds;
  - France zones A–C, which covers Paris (zone C);
  - the Netherlands.
- **Still outstanding:**
  - **Camden, Manchester, Kent and Hampshire:** bot protection, tried 9 Nov, not retried. Getting past a bot check isn't reading the page as offered.
  - **The other 31 Scottish councils, and every other English council.**
  - **Belgium** (Brussels, in the multi-city prototype only).
- **No calendar is extrapolated to another council.**

## 10. External providers still unverified

**This sprint:**
- RATP and Île-de-France Mobilités (403), so Paris has no official transport facts;
- the Paris tourist office (403);
- the Musée de l'Orangerie and La Grande Épicerie (403);
- the Musée des Arts Forains (503);
- the Jardin du Luxembourg hours page (503);
- the 13 London pages in section 4.

**From earlier sprints, still open:**
- LiteAPI pricing (404);
- Booking.com Demand API terms;
- GetYourGuide;
- Amadeus self-service closure (reported only);
- TfL's open-data page;
- Nager.Date;
- the Mobility Database and OpenTripPlanner licences;
- Masthoff's group papers.

**New external use this sprint:**
- **Wikidata's query service** (CC0, free; for locations);
- **one OpenStreetMap Nominatim lookup** (ODbL; for one address);
- **Babel**, run once in a scratch folder to read CLDR formats.

None of these is a runtime dependency, and none costs money.

## 11. Tests run, and their results (12 Nov)

| Suite | Result |
|---|---|
| Brain (`pytest`) | **418 passed**, 0 failed (one library deprecation warning). It was 396 at the last report |
| Android (`testDebugUnitTest`) | **119 tests, 0 failures, 0 errors** (the photo credits changed) |
| iPhone (CI run #109, `upload: false`, commit `04bf623`) | **Passed**: the app builds with the corrected credits file (one author name), and every screen was drawn. Signing, archive and upload were skipped, as always off `main` |

**New tests:**
- `test_paris_dev.py` (5);
- `test_readiness.py` (4);
- `test_recommend_international.py` (4);
- 3 group, 1 food, 2 photo and 3 catalogue tests.

## 12. Regressions and unresolved failures

- **A test failed from 12 Nov, unrelated to this sprint:** the currency test's fixed ECB rates aged past the five-day limit. The test now passes the day the rates were read; the rule is unchanged. Fixed in `a56fceb`.
- **No regressions in London planning:** the planner still reads the cards, which are unchanged. Only the catalogue and discovery read the new facts.
- **Unresolved:**
  - Paris is one ready place short of 20;
  - the 13 London pages couldn't be read;
  - Richmond's photo licence conflict;
  - the share-card legal questions.

## 13. Files changed, and commits

5 commits on the branch (`a56fceb`, `63edf83`, `fd390e9`, `04bf623`, and the one holding this report).

| Area | Files |
|---|---|
| Brain code | `catalogue.py` (facets, notices, the checked layer, the Paris loader), `readiness.py` (new), `quality.py` (access rule, notices, sessions, the weighted option), `discovery.py` (currency), `group.py`, `api.py` (the food notice), `trips.py` (a day for pricing) |
| Brain data | `catalogue/london_checked.yaml`, `catalogue/london_locations.yaml`, `dev/paris.yaml`, `photo_checks.yaml`, `formats.yaml` (all new) |
| Scripts and benchmarks | `verify_locations.py`, `catalogue_coverage.py`, `benchmark_profiles.py`, `compare_group_scenarios.py` (new); `benchmarks/coverage/destination_coverage.md`, `synthetic/profiles.txt`, `synthetic/group_scenarios.txt` |
| Tests | `test_catalogue.py`, `test_photo_credits.py`, `test_group.py`, `test_food.py`, `test_currency.py`; `test_paris_dev.py`, `test_readiness.py`, `test_recommend_international.py` (new) |
| Apps | `photo-credits.json` in both apps (one author) |
| Documents | this report, `destination-readiness.md` (new), `decision-log.md` (m244–m251), `design/photo-credits.md`, `foods-avoided-audit.md` |

## 14. Decisions for Abram

| # | Decision | Recommendation | Hours |
|---|---|---|---|
| 1 | **The ranking rule:** doubts first (today), or the match less a cost per doubt | **0.10 a doubt.** In both cities it raises the chance of "Good" and the traveller's own kind; doubts stay visible as reasons | Claude ~1 h, with the planner benchmark |
| 2 | **The readiness thresholds** (20 ready, 6 kinds, 80% fresh hours, 50% access known, 60% areas) | Accept, or change any one: each is one constant | a decision |
| 3 | **London's two card corrections** (the Courtauld price; the Uber Boat fare) | Re-read the Courtauld's ticket labels and the boat's zones, then correct the cards | Claude ~0.5 h, or Abram ~15 min |
| 4 | **The 13 London pages and 5 Paris places** that refuse automated reading | Read by hand, or leave the facts unknown | ~15 min each |
| 5 | **The share card's licences**: the three questions for the solicitor (section 7) | Until then, the share card shows only CC0 and CC BY photos, with the title and the licence link | Claude ~2 h, both apps |
| 6 | **Replace the oldest photos first** (15 are 15+ years old) | With Abram's own, when he has them | Abram |
| 7 | **Paris's next step** | Read the 3 drafts' hours; then decide whether Paris goes to preview | Claude ~2 h |
| 8 | **Group plans with a step-free need:** flag unknown access (default) or exclude it | Flag, and let the group choose strict | a decision |
| 9 | **Unchanged:** the `foods_avoided` count (old builds still send the field; the branch Brain now logs that it happened, never the value); the DPIA with the solicitor; the four councils; the friends' round's first steps (the tag, the rehearsal) | — | as before |

**Hours (Claude, approximate):**

| Workstream | Hours |
|---|---|
| Validation and decisions | ~1 |
| London facts and locations | ~4 |
| Catalogue facets | ~1.5 |
| Paris | ~4 |
| Photos | ~1.5 |
| Coverage dashboard | ~1 |
| Readiness | ~1 |
| Benchmark and its fixes | ~2.5 |
| Groups | ~1.5 |
| Food notice | ~0.3 |
| Report | ~1 |
| **Total** | **about 19 h** |
