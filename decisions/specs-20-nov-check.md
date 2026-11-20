# The food field, price ages and availability, checked against Abram's specs (20 Nov 2026; m309)

Abram's decisions of 20 Nov, §5 to §7.
- **All of this is on the development branch only.** Nothing here reaches production or the frozen round.
- **The default ranking is unchanged:** availability feeds only the report view (`quality.kept_apart`), never a plan's order.

## §5 The food field (`python -m brain.foodfield`): all seven requirements hold

| His requirement | Where it holds | Checked |
|---|---|---|
| Abram runs it | a command he runs with the database's External URL (`foods-avoided-audit.md`, the operator procedure) | yes |
| Aggregate counts only | it prints `profiles N, with_key N, non_empty N`, never a value, length or user | tests (`-k food`: 20 pass) |
| Removes only the `foods_avoided` key | `food.RETIRED_PROFILE_KEYS = ("foods_avoided",)`; `scrub_profile` drops that key only; it writes only `users.profile` | code read |
| Commits only when the count reaches 0 | it counts again inside the transaction, then commits or rolls back | tests |
| Verifies the final count | it prints `after:` from a fresh read | tests |
| Deletion holds across a restore | **Backups:**<br>• made by the branch's code, they never hold the key (m233);<br>• the live code's nightly ones still do, but restoring any of them with the branch's `restore` drops it;<br>• `count-food --after-restore` checks the result.<br>**Render:** step 0 of the database schedule runs before the upgrade, so no Render recovery point ever holds it | code read, tests |
| Never a value, never a whole record, nothing to analytics, notifications or the Brain | it never deletes a user. **The frozen apps never send the field:**<br>• no screen sets `foodsAvoided` in either app;<br>• Android encodes no nulls (`explicitNulls = false`);<br>• iOS leaves out empty optionals.<br>The branch Brain never stores it, and keeps only an in-memory count if an old app sends it (m223, m252) | `git grep` on `80a0da3` |

**One residual, stated plainly.** The live Brain (`80a0da3`) still accepts `foods_avoided` in `PUT /v1/me/profile`. So a hand-made request could store it again after the clean. The apps never send it. Run `count` again before Stage 2; the branch's version, once deployed after the round, closes this.

**No new food-preference collection is built or enabled.**

## §6 Price ages and estimates: matched to the spec, two gaps closed

| His rule | Before today | Now |
|---|---|---|
| Events 90 days, food 180, other experiences 365 | the same numbers, marked GUESS | the same, marked "Abram, 20 Nov §6" (`priceestimate.MAX_AGE_DAYS`, `DEFAULT_MAX_AGE_DAYS`) |
| Undated prices are never recent verified prices | held for comparable prices (an undated peer never counts) | **also for budgets:** `confirmed_price()` needs a verified price that is dated and recent for its kind. An old or undated one counts as an estimate, at the supplier's own amount |
| The customer-visible allowance: the median of at least 3 comparable, recent, same-city, same-currency prices, labelled as an estimate | held | the label now starts "No verified price. Estimate: about …", and still ends "not this place's price" |
| The internal cost: the upper-quartile proxy plus a separate uncertainty penalty, never shown as a ticket price | held (`model_costs`, `figure="conservative"`; the penalty is `quality.RISK`) | unchanged |
| Strict budgets: estimates never confirmed; an unknown necessary cost means the budget can't be verified | held | unchanged, now with the stricter "confirmed" above |
| Keep the supplier's own price and currency | each price kept in its own currency; but **a budget added amounts across currencies** | **prices in more than one currency are never added up:** the status is "mixed currencies", with "can't be verified without a conversion". Each price is left as given |

**Tests:** 9 in `tests/test_priceestimate.py`, 2 of them new: an old or undated price is never confirmed spending, and two currencies are never added. **What it changes:** only `budget_breakdown`, which nothing serves yet; no plan or price shown in the frozen round.

## §7 Availability: the place, the session and the activity kept apart

**What was wrong.** On 19 Nov (m291), any dated notice beginning "No …" made a card "closed or unavailable". That was right for the evensong card, where the service is the point. But it would wrongly close a venue whose own visit doesn't depend on the service.

**What it does now** (`quality.availability_parts`; `availability()` returns its state):

| | Comes for a **session** (a service, show or match: `SESSION_TYPES`, or a card with sessions per event) | Comes for a **place** |
|---|---|---|
| "Closed …" notice, or weekly hours closed | closed or unavailable | closed or unavailable |
| "No … listed", "Cancelled" | **closed or unavailable**: ODYS doesn't promise a service that isn't listed. The place isn't marked shut | **unchanged**: shown beside it, and it doesn't close the place |
| "Sold out", "… unavailable" | closed or unavailable | closed or unavailable |
| Usual times only, no listing for that date | **might be open**: never promised, because only a dated listing confirms a session, and the catalogue holds none | — |
| Official weekly hours, read within 180 days, open that day | — (the card's hours are the session's times) | confirmed open |
| Anything else | might be open | might be open |

Each answer carries the parts separately:
- `place`, `session` and `activity`;
- the day's notices;
- `says`, the notice that decided it ("No Choral Evensong listed").

So a report can say "No Choral Evensong listed that day" without saying St Paul's is shut.

**Tests:** 14 in `tests/test_recommend_international.py`; the 19 Nov one is unchanged and still passes.
- New: evensong on Saturday 28 Nov is "closed or unavailable" with the session "not on", and on Friday 27 Nov it is "might be open", never confirmed.
- A gallery with a "No Choral Evensong listed" notice stays "confirmed open", with the notice shown.
- "Sold out" stops the activity.
- "Closes at 15:00" is information only.

**For approval after the round (not done):** the default ranking change. Today a card that is "closed or unavailable" for the day isn't removed by this code: the planner still uses its own day rules (the weekly hours and "Closed" notices, `practicality`). The proposal:
- a session card whose session is "not on" or "not usually on that day" is left out of that day's plans;
- a session card that only "might be open" is shown with "Check the listing for that day";
- place cards stay as now.

It is tested on the benchmark before Abram decides. **Effort:** about 1.5 h, after Test B.

## Hours

- **Claude, 20 Nov:** 1.5 h (the checks, the two fixes, the availability split, the tests, this page). Done.
- **Abram:** 0.25 h to read it.
