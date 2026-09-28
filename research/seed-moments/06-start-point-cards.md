# The real Test B start point, and nine cards near it (D104)

*28 Sep. Counts come from the Brain: ready cards open on a Saturday that fit a 12:00–17:00 day, using its walking estimate (4.5 km/h × 1.35) and rough Tube estimate. Station coordinates and lines come from TfL's StopPoint API (read 28 Sep). Anything marked **(my judgement)** is opinion.*

## Recommendation: Charing Cross (the Trafalgar Square exit) (my judgement)

| Start | Cards within a 25-min walk: before → after the new cards | Indoor, after | Within 30 min by Tube, after | Lines |
|---|---|---|---|---|
| **Charing Cross** | 7 → **16** | 9 | 24 | Bakerloo, Northern; Embankment (District, Circle) and Leicester Square (Piccadilly) are a few minutes' walk |
| Tottenham Court Road | 6 → 14 | 8 | 24 | Central, Elizabeth line, Northern |
| Waterloo | 5 → 12 | 6 | 22 | Bakerloo, Jubilee, Northern, Waterloo & City |
| London Bridge | 5 → 5 | 0 | 21 | Jubilee, Northern |

**Why Charing Cross:**
- **The most cards within walking distance,** before and after the new cards.
- **All three sunset river cards are close** (Waterloo Bridge, Villiers Street, Somerset House), so the 12:00–17:00 day can end on the river at sunset (D99).
- **It is busy at weekends.** The City cards near London Bridge and Bank are mostly weekday-only.
- **It's an easy meeting point** that everyone knows (Trafalgar Square).

**The trade-off:** London Bridge has the Jubilee line and Borough Market, but little else nearby that is open at weekends.

`brain/data/testb/brief.example.yaml` now starts at Charing Cross. **Confirm it or pick another start (about 5 min).**

## Nine new cards: one line each, flag any you disagree with

*All are verified from official sites (or search results limited to the official site) and marked ready (D91). Tags are my judgement. Eight are indoors, for rain.*

| # | Card | Line |
|---|---|---|
| 1 | `m_national_gallery` | **From Trafalgar Square into the National Gallery:** free, daily 10:00–18:00; wander the collection |
| 2 | `m_national_portrait_gallery` | **Centuries of British faces:** free, 10:30–18:00 (Fri–Sat to 21:00) |
| 3 | `m_st_martin_crypt_lunch` | **Lunch in the brick-vaulted crypt of St Martin-in-the-Fields:** tombstones in the floor, a daily menu; about £12 (GUESS); **only ever the lunch stop** |
| 4 | `m_soane_museum` | **Sir John Soane's house of curiosities:** free, Wed–Sun 10:00–17:00; kept as it was in 1837; 10 min queue allowed |
| 5 | `m_courtauld_gallery` | **The Courtauld: Van Gogh's bandaged ear and Manet's barmaid:** £12 at weekends (£10 weekdays); open days UNVERIFIED (assumed daily) |
| 6 | `m_rfh_foyers_rest` | **A rest in the Royal Festival Hall's free foyers:** Tue–Sun; the first "quiet and rest" card (a gap from the type-mix check) |
| 7 | `m_park_break_embankment` | **A park break in Victoria Embankment Gardens:** joins the park-break group; closes 16:30 after the clocks change |
| 8 | `m_chinatown_dim_sum` | **Dim sum lunch on Gerrard Street:** about £20 (GUESS), 10 min queue; **only ever the lunch stop** |
| 9 | `m_transport_museum` | **Climb aboard old buses and Tube trains at the London Transport Museum:** £18.50 (an annual pass), timed ticket booked ahead |

## Checked with the two made-up people (real day, from Charing Cross)

- **P02** (food, active): dim sum lunch, Victoria Embankment Gardens (rain swap: the Royal Festival Hall), the Garden at 120, then Beigel Bake.
- **P01** (calm, culture): unchanged. City gardens and the Greenwich hill still score higher for them than the new museums, because their dislike of crowds counts against the museums.
- **The overlap report:** they share 1 of 4 stops (the Garden at 120), with similarity −0.36 (dissimilar). No warning.
- **Both end within 30 min of the generic plan.**
