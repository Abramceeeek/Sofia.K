# Stay prices: nearby dates and watched stays (plan, 7 Nov 2026)

**Decision (Abram, 7 Nov; m201).** Two things, branch only until the friends' round ends:
1. **Nearby dates:** the same stay at the same length, starting up to 3 days earlier or later, each price like for like, with the person's own dates marked. Observed prices only, never "it will be cheaper".
2. **Watch a stay:** a saved stay's last price seen, its price now, the change, when it was checked, and up to 3 alternatives on the same terms nearby. It's checked when the app opens (at most once a day per stay); push notifications come later.

## Like for like (the rule every comparison follows)

The same hotel, length of stay, guests and rooms, room, board (meals) and cancellation terms. The price is LiteAPI's total "what the end user will pay", **plus any tax or fee marked as not included** (payable at the property), shown separately. When a date or a check can't find the same room on the same terms, it shows the closest one and says what differs ("breakfast not included", "non-refundable"). It never puts a different room's price next to the original as if it were the same.

## What LiteAPI documents (docs.liteapi.travel, read 7 Nov 2026)

| Fact | Source |
|---|---|
| `POST /v3.0/hotels/rates` takes `hotelIds` (array; no maximum stated), and one `checkin`/`checkout` per call. `occupancies` is one object per room (`adults`, `children` ages). `currency` and `guestNationality` are required (we send the fixed market `GB`, never the person's nationality). | /reference/post_hotels-rates |
| `retailRate.total.amount`: "The total cost amount due to book this room. This is what the end user will pay." `taxesAndFees[]` items carry `included`: whether the tax is in the total (not included: "paid separately at check-in"). | /reference/post_hotels-rates, /reference/post_rates-prebook |
| A rate's room: `roomTypeId`, `name`; meals: `boardType`/`boardName`; cancellation: `cancellationPolicies.refundableTag` = `RFN` or `NRFN`. **No field is documented as stable across searches or dates**, so matching uses the room name, board and refundability, and says when it isn't exact. | /reference/post_hotels-rates |
| `/hotels/min-rates`: the cheapest rate per hotel for one date range. A multi-date "batch" endpoint exists but is enterprise-only. So nearby dates cost 7 searches. | /reference/post_hotels-min-rates, /reference/hotelsratesbatch |
| Rate searches are free under a "reasonable look-to-book ratio" (pricing page, updated 23 Jul 2026). Rate limits: **two pages disagree** (sandbox 5 a second, production 250; or 500 a second for everyone). We design for 5 a second. | /reference/api-pricing-usage-costs, /reference/rate-limiting, /docs/performance-reliability-rate-limiting |
| No rule found on caching or showing rates later; an `offerId` can go stale ("please refetch rates"). | /reference/post_rates-prebook |

**Open before live prices (UNVERIFIED until read):** LiteAPI's Terms of Service on look-to-book and on keeping or showing observed prices. ODYS never books through LiteAPI (links out only, D120), so checks stay few: cached 15 minutes, at most once a day per watched stay, within the per-person and daily caps already in `trips.py`.

## How it's built

- **The Brain** answers two questions and stores nothing about the person's trip: "this stay on nearby dates" and "this watched stay now". Without a key, both answer with clearly labelled sample prices, so the screens and tests work.
- **The phone** keeps each watch with its trip: the stay, its dates, guests, room, board, cancellation terms, and the prices seen with when.
- **Environments (Abram, 7 Nov):** the frozen production Brain keeps its sandbox key until the round ends. Live prices are tried on a **separate staging Brain on Render** that deploys the branch, with its own key in its own settings (never in a chat or Git). Claude checks it by calling its endpoints. (Not this cloud session's environment: it's the Default one, shared by all of Abram's repositories.) Until then, the Brain is built against LiteAPI's documented responses, with tests, and sample prices.
- **School holidays** (product direction, step 3): term dates are set by each local authority, so this needs a checked source per area first. Researched next, built after the two parts above.

## Hours (GUESS)

The Brain ~3 h; both apps ~4 h; the Terms of Service and school-holiday sources ~1 h. Abram: the staging Brain in Render with the key (~15 min, steps given when the Brain part is ready).
