# Places to stay, judged for this trip: like for like, the whole cost, and separate lenses (WS4, 7 Nov 2026; m209)

**Decision.** A stay is never given one blended score or a quality rating of ours. It is looked at through four separate questions, each with its own answer:
- **Cheapest overall:** the whole cost, meaning the total plus anything paid at the property, in one currency.
- **Closest to your days:** minutes from the stay to each planned day's first place and back from its last.
- **Most flexible:** free cancellation, as the provider shows it.
- **The trade-offs:** the stays no other beats on both cost and travel, each said in plain terms ("£200 more, and about 25 min less travel a day").

ODYS doesn't put a price on the person's time; they weigh it. Stars and guest scores stay the provider's, shown as theirs and used in no ranking.

LiteAPI live prices stay off (`stay_dates_live = False`), no historical prices are stored, and the price index is never called (m205).

## The audit (stay detail and "For your trip", 7 Nov)

| Question | Before | Now |
|---|---|---|
| Location against the actual days | Medians of the minutes to each day's first place and back from its last; the furthest day named | Unchanged, plus the first and last days below |
| **First and last days** | Treated like any other: day 1 counted "minutes there" from the stay, though the person comes from the airport or station | **Fixed.** The check-in day has no morning leg from the stay, and the check-out day no evening leg back. Each day has its own words ("Day 1: you arrive from your journey; 5 min back here at the end"). The typical day counts only legs that happen. Both apps show the Brain's words, and older builds fall back to the old line |
| **A day with no places yet** | Silently left out | **Said:** "Day 2 has no places yet, so it isn't counted." (`missing`) |
| Room, board, cancellation | Compared by room name, board and refundable tag; differences said | Unchanged. Names are matched exactly (case aside), because LiteAPI documents no room ID that stays stable across searches. A small naming difference reads as "a different room", which errs on the honest side |
| **Terms the provider doesn't give** | An unknown board or cancellation counted as the same terms | **Fixed:** "meals not given", "cancellation terms not given". Unknown is never "the same", so such a date can't be "lowest of these" |
| Taxes not included | Added to the whole cost | Unchanged, now limited to the same currency |
| **Property fees in another currency** | Added to a total in a different currency (a city tax in euros onto pounds) | **Fixed:** kept apart and said, e.g. "8.00 EUR paid at the property, not added in". A date with such a fee isn't "lowest of these", because its whole cost isn't like for like. Search results carry the same words (`Stay.pay_there_other`) |
| **A rate in another currency** | Compared as a number | **Fixed:** never compared |
| **Unknown currency** | Would print a bare number | "420 (currency not given)", never assumed to be pounds |
| Rounding | Whole cost to the penny; pence shown only under £100 | Unchanged |
| Missing route times | — | No planned day gives "Plan your days to see how far they are from here." Travel times are the straight-line estimate, or TfL's where known |
| Far from everything | Said in minutes | Unchanged, and the lenses add "about 40 min a day more travel than the closest" |
| Near the days but far from the centre | — | Distance to the centre plays no part. A stay in Whitechapel beats one at Charing Cross for days in the City (tested) |

## The lenses (`brain/src/brain/stayranking.py`)

| Lens | Answer | When there's none |
|---|---|---|
| Cheapest overall | The lowest whole cost among stays in the most common currency; others "aren't compared", and that's said | — |
| Closest to your days | The least typical-day travel (there and back) | "How far it is from your days: plan your days first." |
| Most flexible | The cheapest with free cancellation, as found | "None of these has free cancellation, as found." |
| Trade-offs | The Pareto set on (whole cost, travel a day), cheapest first, each against the cheapest: "£200 more, and about 25 min less travel a day." | — |

Each stay also gets its own lines:
- where it stands on cost, e.g. "Cheapest of these: £400 for 3 nights, including £20 paid at the property.";
- where it stands on travel;
- its cancellation terms.

**Why no single "best".** The rating model's cost weight spans about 20 times after the short onboarding (D127). So any pounds-per-minute figure would be the model's guess presented as the person's value. The trade-off is shown instead, and the person chooses.

## Tests (`brain/tests/test_accommodation.py`, 10)

The tests cover:
- the same hotel, room and terms;
- a different room, board or cancellation, each said;
- unknown terms never treated as the same;
- taxes and property fees not included, added in the same currency only;
- a city tax in another currency kept apart;
- a rate in another currency never compared;
- a missing currency said;
- a day without places said;
- far from all activities, said in minutes;
- near the activities but far from the centre, which wins on location;
- the four lenses, the Pareto set, other currencies left out, and no free cancellation said;
- no day planned means no location lens;
- the arrival and leaving days counting only their real legs.

The existing stay tests (`test_stay_prices.py`, `test_trips.py`) still pass.

## Not done, and why

- **The lenses aren't on a screen yet.** "Compare these stays" is a new screen in both apps (~4 h). It's worth building once live prices exist, since sample prices make every comparison a demo.
- **Room matching by ID.** Not until Nuitée or LiteAPI documents a stable room ID.
- **Several stays in one trip** (a different hotel per city): WS3.

**Hours:** Claude ~3 h (the audit, the fixes, the lenses, tests, both apps' wording). Abram: none needed now.
