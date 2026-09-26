# Area 2 — Place and experience preferences (moments)

**Decision:**
- **The unit is a moment (decision D9).** A moment is a place + how you approach it + when to be there + features, plus a shot card for the ~20 swipe and peak moments only (D14). Abram **hand-picks 50 moments** (D11), starting from 5 seed moments of his own. An LLM drafts the rest of each card and Abram corrects it.
- **Place coordinates and IDs** come from **Overture Places**, looked up per moment. There is no bulk pull.
- **Features:** 11 place attributes plus **4 moment features** (contrast/reveal, absorption, awe, social pull), each scored 0–2, plus cost in £. Feeling-per-pound is computed by the model, not tagged.
- **Swipe layer:** an ordinal regression on those features with a hierarchical prior (Area 3). The 15–20 swipe moments must be familiar, polarising and spread across features.
- **Google Places:** spot-checks only, because it can't be stored. RecBole and check-in datasets are skipped.
- **Cost: about 5 founder hours.** Schema 1, seed-moment session 1, LLM-drafted cards and review for 45 more 2 (shot cards for ~20 only, D14), swipe-set selection 1.

## The moment schema (v0)

```yaml
id: m_southken_nhm_reveal
title: "Out of the tunnel, into the Natural History Museum"
place:    {name: Natural History Museum, overture_id: ..., lat: ..., lon: ...}
approach:                     # how you arrive: part of the experience
  from: South Kensington station
  start_point: {lat: ..., lon: ...}   # where the planner must deliver you
  path: "<exit and walking route, as Abram describes it>"
  duration_min: <n>
  step_free: <true|false>
experience: {duration_min: [<min>, <max>], end_point: {lat: ..., lon: ...}}
best_time:
  time_of_day: ["<hh:mm-hh:mm>"]
  light: "<when the reveal looks best>"
  weather: [<dry|any>]
  crowd_window: "<when to avoid>"
  opening_hours: "<spot-checked, with date>"
features:                     # 0-2, founder-tagged (LLM draft)
  place:  {movement_views: 0, food: 0, green_nature: 0, history_culture: 2, iconic: 2,
           local_novel: 0, crowds: 1, walking_effort: 1, active: 0, outdoor_exposure: 1,
           photo_potential: 2}
  moment: {contrast_reveal: 2, absorption: 0, awe: 2, social_pull: 2}
cost_gbp: <n>                 # raw input; feeling-per-£ = predicted S / cost, computed
shot_card:
  stand_at: {lat: ..., lon: ..., note: "<exact spot>"}
  face: <compass bearing>
  frame: "<what to include>"
  when: "<time and light>"
  avoid: "<what spoils it>"
source: seed | founder | user
last_checked: <date>
```

All values above are placeholders. Feature scores are illustrative until Abram tags his seed moments. The previous "price level" attribute is replaced by raw `cost_gbp`.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | [Overture Maps Places](https://docs.overturemaps.org/guides/places/) + [`overturemaps` CLI](https://github.com/OvertureMaps/overturemaps-py) | Monthly releases; ~2,300 categories. CLI ★270, 2026-09-22, Py ≥3.10 | CDLA-Permissive-2.0 / Apache-2.0 / CC0; CLI MIT | Free place IDs and coordinates, with **no ODbL share-alike** |
| 2 | [Explorest](https://apps.apple.com/us/app/explorest-photo-locations/id1227446332) (product, see Area 7) | 4.4★ from 1K ratings; covers the UK | Commercial | The closest existing **shot card**: exact spot the photographer stood, directions, best time and light, field tips. We copy the format, not the content |
| 3 | [Komoot Highlights](https://support.komoot.com/hc/en-us/articles/10194639751450-Highlights) (product) | Mature | Commercial | Community-curated **segments with a direction**: Komoot routes you to the segment start "so you experience it as intended". A working precedent for approach-aware curation |
| 4 | OpenStreetMap | Live; London coverage good but uneven | **ODbL** (derived databases must be shared alike) | Opening hours, station exits and footpaths for approach paths. Keep it in a separate layer |
| 5 | Google Places API (New) | Production | May store only `place_id` | Place Details $5–25 per 1k by tier, with free monthly caps. Spot-checking 50 moments costs £0 |
| 6 | Place Pulse 2.0 / Quercia "happy maps" | Research | Research | In London, "beautiful/quiet/happy" walking routes were 26–30% better on those ratings for only 12% more length. Evidence that the *walk between* places can be scored |
| 7 | LLM attribute extraction (Boughanmi et al. 2025) | Research | — | Agrees closely with human coders. Drafts moment cards from reviews and descriptions |
| 8 | [RecBole](https://github.com/RUCAIBox/RecBole); Foursquare / Yelp datasets | Stale / old / educational only | MIT / research | **Skip for v0.** These datasets record visits, not enjoyment; Yelp has no UK |

## What the evidence says

- **Choose the swipe items for familiarity *and* disagreement.** Selecting only the most polarising items was unusable: people paged through hundreds before finding 10 they knew. Balancing log-popularity against entropy worked (Rashid et al. 2002). Adaptive follow-ups help further (Golbandi et al. 2011).
- **Hierarchical Bayes borrows strength for new users** (Zhang & Koren 2007). This links to Area 3.
- **POI research predicts check-ins, not enjoyment** (20 pitfalls, Bellogín et al. 2025). **Expected utility ≠ experienced utility** (Hofschen et al. 2023), so per-moment ratings after the experience must carry the model.
- **The moment features have mixed but real support** (details in Area 6):
  - *Contrast/reveal* maps onto Kaplan's **mystery** (the promise of more ahead). It was the only significant informational predictor of scene preference (Kaplan, Kaplan & Brown 1989), but a meta-analysis found its correlation with preference ranges from −0.45 to +0.95, with no stable direction (Stamps 2004).
  - In VR, **narrowing walls raised arousal and felt unpleasant**, while spacious designs felt pleasant (Presti et al. 2022). Compression is real; whether *release after compression* adds a bonus is **untested**, and our ratings can test it.
  - *Awe* (vastness + need for accommodation) and *absorption/flow* (challenge–skill balance) have validated scales.
  - *Social pull* has no academic measure I found. Measure it directly with a one-tap "Would you bring someone here?" after each moment. It doubles as a distribution signal.

## Gaps we'd have to fill ourselves

- **Approach geometry.** Station exits, entry points and approach paths are hand-entered per moment, and nothing off the shelf models them. The planner then needs asymmetric travel times (from the previous moment's end point to this moment's approach start). OR-Tools supports that natively (Area 4).
- **Per-moment ratings of transitions.** The rating prompt must fire at the *end of the approach* for reveal moments, not only on leaving.
- **Swipe cards for moments.** Each needs one photo or short clip. Familiarity is lower for moments than for places, so Londoners should be asked about London moments.

## Risks / unknowns

- **Too many features for the data.** 15 tagged features + cost against 50 moments and 10–20 swipes per person can't all be individual βs. Most stay population-level (Area 3).
- **Founder taste is baked into the seeds.** The 50 moments reflect one person, and Test A will show whether strangers share the reactions.
- **Moments go stale.** Light, construction and crowding change, so `last_checked` needs a refresh cadence.
- **ODbL** if OSM approach paths get mixed into the moment table.
- **Overture schema churn:** pin a release.

## Addendum (D29): benchmark the feature tagger before trusting it

- **The 50 v0 moments double as a gold set.** Abram tags them **blind** (before seeing any model draft). Jev (TypeSafe AI) and Claude then tag the same card text, and are scored on accuracy **and calibration**: does a tag's confidence predict whether it is right?
- **If one is calibrated,** auto-accept its high-confidence tags and route the rest to Abram. This matters again when the moment count grows past what one person can tag.
- **Cost:** +1.5 founder hours in the Phase 4 moment-DB step; cash under £10.
- **Full design:** [`research/benchmarks/moment-tagging-jev-vs-claude.md`](../benchmarks/moment-tagging-jev-vs-claude.md).
