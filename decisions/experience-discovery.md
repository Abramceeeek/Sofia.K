# Discovering places when you don't know where to go, and the quality standard in code (10 Nov 2026; m239)

**Decision: a prototype in the Brain, not in the apps yet.**
- **Discovery answers a question with at most three moments or places, never a feed.** Each says why, from the inputs that chose it, and carries the four-perspective quality check.
- **The ODYS quality standard (Abram, m234) is now code** (`brain/src/brain/quality.py`). Every suggestion is judged on personal relevance, practicality, financial suitability and trustworthiness. **Anything poor on one of them ranks after everything that isn't,** however strong a match it is.

`brain/src/brain/discovery.py`, `brain/src/brain/quality.py`, `brain/tests/test_discovery.py` (9 tests), on London's checked catalogue and the synthetic Testville.

## The quality standard (`quality.py`)

| Perspective | Good | Fair | Poor |
|---|---|---|---|
| **Personal relevance** | the rating model's chance of "Good" or better ≥ 50% ("A strong match" at 75%) | under 50%: "Worth a try" | — (unknown before any answers) |
| **Practicality** | open that day, fits the time with the journey | over 45 min to get there; hours vary or aren't known | closed that day; doesn't fit the time |
| **Financial suitability** | free, or a checked price within what's left | an estimated price; unknown; another currency than the budget's | over what's left to spend |
| **Trustworthiness** | checked at a named source in the last 180 days, with hours and price known | checked 180–365 days ago, or hours or price unknown | over a year since checked; never checked; test data |

- **Ranking:** nothing poor sorts above anything without a poor perspective. Then fewer doubts (fair or unknown) come first, then the strongest match.
- **Thresholds are GUESSES,** stated in the module, until real ratings say otherwise.
- **Tested:** the Soane Museum at 95% fit, but closed on Mondays, ranks below the National Gallery at 55% on a Monday. Go-karting is poor on money with £20 left. A card checked over a year ago, or test data, is poor on trust.

## The six kinds of discovery

| Abram asked for | `discovery.py` | Grounded in | Example (synthetic tastes, London) |
|---|---|---|---|
| **Destination recommendations** | `destinations` | Each ready destination's best moments for this person over the days asked: the mean chance of "Good" or better, and how many are strong matches | Among two synthetic splits of London (views, culture), a views lover gets the views city first and a culture lover the museum city. **Not-ready places are named with what they lack,** never suggested: Testville's moments are test data |
| **Experience categories** | inside each answer | The catalogue's categories (m235) | "Its best for you: 4 views, 2 nature" |
| **Neighbourhood discovery** | `neighbourhoods` | Areas the cards' own records name, with at least two moments, by mean fit | Views lover: City of London (best: Horizon 22), Hyde Park, Canary Wharf |
| **Hidden local experiences** | `hidden_local` | The card's local tag at its highest, **and** in at most 5% of simulated plans (`popularity.yaml`), **and** still a good match | "Lift a real gold bar at the Bank of England Museum": "Local, and in none of the simulated plans other people got" |
| **Seasonal activities** | `seasonal` | **Only dated season notes that name their moments.** Never guessed from the weather or the month | London: nothing, because no checked notes yet (said). Testville in April: the river path at blossom time, with the note's source. Its trust is poor (test data), so it isn't recommendable |
| **Food discovery** | `food` | The food category or the food tag, ranked by the person's own food interest | Food lover: Brick Lane bagel, Borough Market, a steak dinner. **No diet or belief words, ever** (tested); dietary needs stay with `food.py`, behind consent and the DPIA |
| **Time and budget** | `fits` | The experience's duration, the journey, its price, and that day's hours | 90 minutes, nothing to spend, a Monday: three free, open, short moments for each taste |

**Why it isn't a feed.**
1. At most three answers (`LIMIT`).
2. Each answer is a moment (or a place), never "top 10 attractions".
3. Each gives at most three reasons, from the actual inputs: the score's own taste terms by name, as in "Why this stop?" (m230), the season note and its source, the time and money it fits. No percentages, except "in only n% of the simulated plans" for hidden moments, which is a count, not a score.
4. A place ODYS can't vouch for isn't offered, and the answer says so.

## Found while building it

- **London's neighbourhoods are thin.** Only 3 areas have two or more moments whose records name them, because only 28 of 49 cards name an area. **Placing cards in their nearest area was tried and dropped:** it put St Paul's into "Borough", across the river. Areas must come from sources.
- **No season notes are checked for London,** so seasonal discovery is empty there by design.
- **Popularity comes from simulated plans** (D113), not real ones. "Hidden" means rarely planned by the model for other people. That's the honest claim, and the wording says so.

## Next (GUESS hours; after the friends' round)

| Step | Hours |
|---|---|
| Name an area on every card, from its official address (for neighbourhood discovery) | Claude ~1.5 h; Abram's check 0.25 h |
| London season notes from official sources (Royal Parks, the venues), each naming its moments | Claude ~1.5 h |
| An "I don't know where to go" screen (after-9-Nov #83), both apps: three answers, reasons and the quality line | ~8 h, both apps |
| Popularity from real plans once there are enough people (not before Test B ends) | Claude ~1 h |

**Hours this step:** Claude ~3 h.
