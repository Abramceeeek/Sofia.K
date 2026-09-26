# Area 7 — Existing products

**Decision:** No product I found **curates moments or transitions for city leisure**, or learns a person's *experienced* enjoyment from post-moment ratings.
- **Closest precedents:** Komoot (direction-aware route segments, outdoors), Explorest (photo spots with approach, best time and shot tips) and VoiceMap (GPS-timed audio along a route). Copy their formats and **don't compete on AI itinerary chat**, which Google, Mindtrip and Expedia/Layla give away free or cheap.
- **Positioning:** "moments that fit how you feel, learned from your ratings", plus stranger trips (the weekend test).
- **Cost: 0 build hours.** This informs positioning and the Test D landing page.

## What exists (ranked by threat or relevance)

| # | Product | Maturity | Model | Why it matters |
|---|---|---|---|---|
| 1 | Google Gemini / Maps trip planning | Mass market | Free | Itineraries built from Maps, Flights, Hotels and the user's Gmail/Photos, with real-time pivots. It can add "vibe" prompts cheaply. **The biggest threat** |
| 2 | Mindtrip | Scaled startup | Free; commission via partners such as Priceline and Viator | Chat to an itinerary, in-chat booking (flights since May 2026), group co-editing and voting |
| 3 | Layla (acquired by **Expedia**, reported 31 Jul 2026) | Owned by an incumbent | Free core; ~$49/yr paid tier (third-party figure) | Live prices and booking. Now an Expedia funnel |
| 4 | Wanderlog | Mature | Pro $39.99/yr (third-party figure) | Collaborative map planning; Pro adds AI suggestions and route optimisation. The benchmark for "plan with friends" |
| 5 | WeRoad (+ WeMeet) | Raised $58M (May 2026) | Trip price; human coordinators | **Strangers travelling together works at scale**: age-matched coordinators, a WhatsApp group a month before, 30–40% unstructured time. WeMeet ran local meetups (50k+ attendees, 35 cities) |
| 6 | Flash Pack | Mature | Trip price, instalments | Solo travellers aged 30–49 / 50–65, groups of at most 16 (average 12). 90% travel solo, and 80%+ stay in touch afterwards |
| 7 | Timeleft | 3M+ users (search figure) | ~$16 per dinner or ~$26/month (third-party figures) | Paid meetings of 6 strangers, matched by quiz, in cities across roughly 50 countries (sources differ on the count). Evidence that people pay to meet strangers |
| 8 | **Moment-adjacent:** Komoot Highlights, Explorest, VoiceMap | Mature / niche | Komoot not checked; Explorest in-app purchase; VoiceMap £4–12 per tour | See the moments question below |

## What the evidence says

**Feature map** ("not seen" means not in anything I read, not proven absent):

| | Plans from | Unit | Learns how it *felt*? | Strangers | Money |
|---|---|---|---|---|---|
| Gemini/Maps, Mindtrip, Layla | chat + history | places → itinerary | not seen | no (Mindtrip: friends) | free / commission / subscription |
| Wanderlog | manual + AI | places on a map | not seen | friends | subscription |
| WeRoad, Flash Pack | catalogue | whole trip | not seen | **yes**, human-run | trip price |
| Timeleft | quiz | one dinner | not seen | **yes** | ticket / subscription |
| Komoot | community | **directional segment** | ratings of highlights | no | — |
| Explorest | influencers | **spot + approach + light** | no | no | in-app purchase |
| VoiceMap | authors | **GPS-timed story along a route** | no | no | per tour |
| **This app** | voice onboarding + choices + swipes | **moment** (approach + time + shot card) | **yes**: per-moment ratings update the βs | weekend test, then matching | Phase 2 |

- **Does anyone curate moments or transitions? Partly, in three niches:**
  - **Komoot's segment highlights** are direction-dependent, and it routes you to the start of a segment "so you experience it as intended". That is transition-aware curation, but for hiking and cycling.
  - **Explorest** gives the exact spot the photographer stood, directions, best times and light, and field tips. That is the shot card, but for photographers (4.4★ from 1K ratings; includes the UK).
  - **VoiceMap** plays audio automatically at the right spot along a walk (100+ London tours, £4–12 each). That is a sequenced experience, but authored stories, not personal fit.
  - **"Moments: Curated Travel"** (App Store) sounds identical but isn't: it curates spots and hotels (Bali, Sharm el-Sheikh) and has too few ratings to show.
- **There is demand for mood-first planning.** 25% of travellers want to start a search from a mood rather than a destination (ALL Accor / Globetrender 2026; Dynata survey of 4,300 travellers in 9 countries including the UK). The supply I found is research or concept work (Mood2Trip, 2026 paper; the Narae concept), not a scaled product.
- **The AI-itinerary layer is commoditised.** It is free (Google, Mindtrip), under $50 a year (Layla, Wanderlog), or bundled into an OTA (Expedia bought Layla). None I read models personal enjoyment with named weights.

## Gaps we'd have to fill ourselves

- **A London moment database** (Area 2). Nobody has one with approach, timing and feeling tags.
- **A per-moment rating loop** feeding personal βs. This is the one asset competitors can't copy by prompting.
- **Stranger trips that run without a paid human coordinator.** WeRoad and Flash Pack rely on staff, which is a trust-and-safety and cost question for Phase 2.

## Risks / unknowns

- **Google or Expedia add "moments" or "vibes" as a feature.** The defence is the rating data and the community, not the idea.
- **The moat is only data.** Until per-moment ratings exist in volume, we have no advantage.
- **Search coverage is limited.** App stores are large and small apps may be missed. Prices marked "third-party" need checking on each vendor's own page in Phase 2.
