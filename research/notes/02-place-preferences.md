# Area 2 — Place and experience preferences

**Decision:**
- **Place data:** take London candidates and IDs from **Overture Places**, which is permissively licensed and has no share-alike obligation.
- **Tagging:** hand-tag the **50 v0 places** (decision D5) on a fixed set of 12 experiential attributes. An LLM drafts the tags and Abram corrects them.
- **Swipe layer:** treat it as an **ordinal regression on those attributes** with a hierarchical prior (Area 3), not as collaborative filtering. Pick the 15–20 swipe places to be well known, polarising and spread across attributes.
- **Google Places:** spot-checks only, because its terms forbid storing anything except the place ID.
- **Skipped for v0:** RecBole and check-in datasets. They model visits, not enjoyment.
- **Cost: about 6 founder hours.** Overture pull 1, schema 1, LLM-drafted tags plus review for 50 places 3, swipe-set selection script 1.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | [Overture Maps Places](https://docs.overturemaps.org/guides/places/) + [`overturemaps` CLI](https://github.com/OvertureMaps/overturemaps-py) | Monthly releases; ~2,300-category taxonomy; existence `confidence` score. CLI ★270, 2026-09-22, Py ≥3.10 | Places: CDLA-Permissive-2.0 / Apache-2.0 / CC0 by source. CLI: MIT | Free, commercially usable POI base with **no ODbL share-alike** (it contains no OSM data). Download by bounding box to GeoParquet |
| 2 | [Foursquare OS Places](https://docs.foursquare.com/data-products/docs/fsq-places-open-source) | 100M+ POIs, 1,000+ categories, monthly | Apache-2.0 | Second free source (already one of Overture's inputs); richer category tree |
| 3 | OpenStreetMap | Live; London coverage good but uneven | **ODbL**: a derived database must also be shared under ODbL | Best for `opening_hours`, parks and footpaths. Keep OSM-derived fields out of our own place table, or accept ODbL for that layer |
| 4 | Google Places API (New) | Production; freshest data; atmosphere fields such as `outdoorSeating`, `liveMusic`, `goodForGroups`, `reviewSummary` | Commercial; **may not store content except `place_id`** | Place Details costs $5/1k (Essentials, 10k free a month), $17/1k (Pro, 5k free), $20/1k (Enterprise, 1k free) and $25/1k (Enterprise + Atmosphere). Spot-checking 50 places costs £0. It can't be the source of our database |
| 5 | Place Pulse 2.0 / Quercia "happy maps" | Research datasets | Research | Perceptual attributes that transfer across cities: 56 cities, 1.17M pairwise votes on safe, lively, beautiful and similar qualities. In London, "beautiful/quiet/happy" walking routes were only 12% longer (about 2.5 minutes) |
| 6 | LLM attribute extraction from reviews (Boughanmi et al. 2025) | Research | — | Agrees closely with human coders, at about 2 seconds per review against 6 minutes. Use it to draft our tags |
| 7 | [RecBole](https://github.com/RUCAIBox/RecBole) | ★4.6k, 94 models, last commit 2025-02-24 (**stale**), Py 3.7+ / PyTorch | MIT | Only for offline benchmarking if we ever have many users. Overkill for 50 places |
| 8 | Test datasets: Foursquare global check-ins, Yelp Open Dataset | Old / restricted | Research / **educational use only** | Foursquare: 33.3M check-ins, 267k users, 415 cities, 2012–13. Yelp: 150k businesses in 11 US/Canada metros, **no UK**. Both record visits, not enjoyment |

## What the evidence says

- **Which places you ask about matters as much as how many.** In a live test with 300+ users, choosing items people are likely to have experienced cut effort, while pure "most polarising" selection was unusable: users paged through hundreds of items before finding 10 they knew. Balancing log-popularity against entropy worked well (Rashid et al. 2002). Adaptive interviews that choose the next item from earlier answers add more (Golbandi et al. 2011; survey in Elahi et al. 2016). **So our swipe places should be well known and split people**, as `CLAUDE.md` already suggests.
- **Hierarchical Bayes is the standard fix for users with little feedback.** It borrows strength from other users (Zhang & Koren 2007), which is exactly the "start at the mean of similar users" plan in Area 3.
- **Most POI-recommendation research predicts check-ins, not enjoyment.** A 2025 review lists 20 pitfalls (Bellogín et al., RecSys 2025):
  - there is no public POI dataset from after COVID;
  - check-in data is dominated by locals;
  - it is extremely sparse (0.003–0.005% density vs 0.5–1.5% for MovieLens/Netflix) and missing not at random;
  - accuracy metrics don't measure satisfaction.
- **Liking a place before a visit is not the same as enjoying it after.** Expected utility (before the visit) and experienced utility (after) produce different preference patterns (Hofschen, Massimo & Ricci 2023). **So the post-visit ratings should carry the model over time.**
- **"How a place feels" can be measured and compared across cities.** Place Pulse did it with crowd-sourced pairwise image votes. Quercia et al. (2014) did it for London walking legs, where pleasant routes were 26–30% more beautiful, quiet or happy for only 12% more distance. That is a candidate *walking-leg* attribute for Area 4.

## Gaps we'd have to fill ourselves

- **An experiential tag set.** No open dataset records how London places *feel*. Proposed 12 attributes, each scored 0–2, mirroring the S equation: movement/views, food, green/nature, history/culture, iconic, local/novel, crowds, walking effort, active vs passive, indoor/outdoor (weather exposure), price level, photo potential. Abram to confirm the list.
- **Tag reliability (~1 h).** A second person tags 10 of the places and we compute κ against Abram's tags.
- **Swipe-set selection.** Choose 15–20 of the 50 places that are familiar, spread across attributes with low collinearity (a D-optimal subset of the attribute matrix), and polarising in Test A reactions.
- **Opening hours and visit durations.** Enter by hand, spot-checked against OSM or Google.

## Risks / unknowns

- **ODbL contamination.** Mixing OSM-derived fields into our place table would make the whole table ODbL. Keep OSM data in a separate layer.
- **Founder bias in tags.** One person's view of "crowded" or "photogenic" is a guess. The second tagger and per-stop ratings are the correction.
- **Familiarity differs between Londoners and visitors.** v0 only asks about London, the "city they know".
- **Overture schema churn.** The `categories` field was removed in the September 2026 release in favour of `taxonomy`. Pin a release.
- **Unconfirmed attribute list.** The 12-attribute list above is my proposal, not tested. Test A reactions will show which attributes actually split people.
