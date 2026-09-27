# Seed moments, batch 1: 11 cards and the gaps for you to fill

**Received** 2026-09-26 (voice-transcribed). **Drafted** the same day as `brain/data/moments/*.yaml`.

**Where they stand**
- Nine can already be planned, using GUESS values where a gap is open.
- **All 11 are `status: draft`.** Real Test B plans use only checked cards (`status: ready`). `python -m brain.testb plans` skips drafts, unless `--include-drafts` is set for a dry run (D72).
- **Time:** checking them fits inside "check Claude's drafted cards" (2.5 h, Phase 3). About 8 minutes a card, so about 1.5 h for these 11.

**How to read a card**
- Your words are marked **FOUNDER**.
- Facts from a source (in `research/sources.csv`) are **CHECKED**.
- **GUESS** marks Claude's placeholders.
- The 15 tags are my first draft, per the Area 2 process: I draft, you correct.
- Notes for the new features wait in each file's header, "for later (after 9 Nov)" (D75).

## Gaps, card by card

| # | Card (file) | What to fill or decide | How long |
|---|---|---|---|
| 1 ✅ **ready (27 Sep)** | Into the whale hall (`m_nhm_whale_hall`) | **Which galleries you pass through, in order.** The hall with the blue whale model is the Mammals hall, on the ground floor of the North Wing (NHM, checked). On the museum map, "Human Evolution" is in the East Wing and "Images of Nature" is in the central building. Are those your "evolution and picture galleries"? | 5 min, or on your next visit |
| 2 ✅ **ready (27 Sep)** | Great Court → King's Library (`m_bm_great_court`) | **Room 1 accepted; confirm it on your next visit.** Room 4 confirmed as your Egypt room; times and scores kept. **Redrafted (D78):** Room 4 (Egyptian sculpture, west side) → across the Great Court → **Room 1, the Enlightenment Gallery** (the former King's Library, east side). It's 91 m long, with shelves of books, warm wood and gold (map and Wikipedia checked; the route is from search). The round Reading Room has been closed to the public since 2013. **Confirm Room 1 is the "library" you remember**, and that Room 4 is your Egypt room | 3 min |
| 3 ✅ **ready (27 Sep)** | River by day (`m_uber_boat_west_day`) | **Kept at £19.30; you check the charge the next time you tap in.** Nothing required. The trip runs 58–65 min, and weekday through boats run 10:00–17:05 (weekends 07:55–22:32), from the timetable. **Cost £19.30 assumes the trip is "All Zones"** (the zone map was UNVERIFIED): check the charge the next time you tap in. Fares change after 31 Oct | 2 min |
| 4 ✅ **ready (27 Sep)** | River at night (`m_uber_boat_west_night`) | **Westminster kept; no weekend-only Battersea version for v0. £11.40 kept until you check it.** I ended it at Westminster, not Battersea. It's the only pier the evening boats reach every day. Weekday evening boats stop at London Eye; weekend boats skip London Eye and run on to Battersea until the 22:32 departure. OK, or do you want a weekend-only Battersea version? The "after dark" window (18:30 on) is set for the Test B weeks, and a sunset rule comes later | 2 min |
| 5 ✅ **ready (27 Sep)** | Steak dinner at Meet Bros (`m_open_kitchen_steakhouse`) | **Meet Bros, Paddington; about £60 a head.** The open kitchen is UNVERIFIED, so the card now promises the room's buzz. **Which restaurant.**** "Meat Bros" is probably **Meet Bros**, 29–31 Craven Road, Paddington (via search); whether it has an open kitchen is UNVERIFIED. Or the Liverpool Street steakhouse: which one? Also your usual spend per person. Not plannable until filled | 5 min |
| 6 ✅ **ready (27 Sep)** | Canary Wharf towers (`m_canary_wharf_towers`) | **Up the Jubilee escalators, among the towers, ending at the Crossrail Place Roof Garden; weekdays only; reveal 2.** The window is 10:00–18:00 so the garden is open. Was: your route among the towers | 5 min |
| 7 | City towers (`m_city_towers_walk`) | Your streets from Bank to Liverpool Street. **Cards 6 and 7 share a variant group**, so a plan holds at most one, because they give the same feeling. OK? | 5 min |
| 8 | Covent Garden and Soho (`a_covent_garden_soho`) | Nothing required: it's an **area vibe** (centre, flexible 45–90 min, no set route). Favourite streets are optional | — |
| 9 | Outdoor dining near TCR (`a_tcr_outdoor_dining`) | **Which street(s)**, and your usual spend. Not plannable until the cost is filled | 3 min |
| 10 | A London park (`a_st_james_park`) | **"Any London park" needs specific parks.** I proposed **St James's Park**: the pelicans have lived on the lake since 1664 and are fed about 14:30 daily (Royal Parks). Want others (Regent's, Hyde, Greenwich)? The spring/summer rule waits until after 9 Nov | 3 min |
| 11 | Richmond Park (`m_richmond_park_view`) | **Which viewpoint.** I proposed **King Henry's Mound** in Pembroke Lodge Gardens, with a protected view to St Paul's (Royal Parks). Also the walk in from Richmond Gate (GUESS). The card warns people to keep 50 m from the deer | 3 min |

**For every card:** check my draft tags and the GUESS durations and windows, then set `status: ready`. Seed 1 (tube to museum, `m_southken_nhm_reveal`) still waits for your walk.

## Aspiration fields (D77): which cards feed which answer

From `python -m brain.testb fields` (updated 2026-09-27). A field is **flagged** until it has at least 2 cards marked `status: ready`.

| Field | Cards | Ready now |
|---|---|---|
| Finance & tech | Canary Wharf towers, City towers (one variant group); research drafts: Bank of England gold bar, Garden at 120, Horizon 22 (all listed by id) | 0 → flag until 2 are ready |
| Food | Meet Bros dinner (**ready**), outdoor dining near TCR; research drafts: Borough Market, Beigel Bake | 1 → flag until 1 more is ready |
| History & culture | Whale hall, British Museum (history tag 2) | **2 ✅ no flag** (27 Sep) |
| Nature | St James's Park, Richmond Park; research drafts: Garden at 120, Greenwich Park view, St Dunstan-in-the-East | 0 → flag until 2 are ready |
| ~~Art & design~~ | Dropped from the Test B question (D83); parked on `decisions/after-9-nov.md` | — |

- **Art & design is dropped for Test B (D83)** and parked on the after-9-Nov list.
- History & culture is clear (27 Sep). The other three fields clear the flag once you mark their cards ready (updated 27 Sep with the 12 research drafts, D90).

## What changed in the Brain to hold these (D72)

- **Entry types:** `kind: moment | area`.
  - An area vibe has a centre point and a flexible duration.
  - The planner allows **one area a day**, and never reports it as the day's peak.
- **Variants:** `variant_of` and `variant`. The day and night river trips, and the two tower walks, are each **at most one per plan**.
- **Direction:** a `direction` note, plus different start and end points (Greenwich → Battersea ends in Battersea's relaxed crowd).
- **Drafts stay out of real plans** (Test B generator and API). 52 tests pass.
