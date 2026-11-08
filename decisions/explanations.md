# Explanations from the algorithm's actual inputs (8 Nov 2026; m219)

**Decision: built in the Brain and its API, on the branch; not yet shown in the apps.**

Every recommendation now carries an `explain` block:
- a stop in a day;
- a place to stay, in "Best for your days";
- a stay judged against the trip;
- a trip length.

The block is a list of **factors**. Each factor is one input the recommendation was really computed from. It has five fields:

| Field | What it holds |
|---|---|
| `kind` | the type of input (see the list below) |
| `effect` | for, against or neutral, by a fixed rule on the value |
| `text` | a fixed template around that value |
| `value` | the number or label the algorithm used |
| `source` | where that value comes from |

The kinds are: preference, travel, hours, best_time, budget, rating, price, location, terms, calendar, coverage and pace.

Whatever the algorithm didn't know is listed in `unknown`, never guessed. No model writes these texts, and nothing is added after the decision to justify it (Abram's rule).

Where to show it in the apps (a "Why this stop" section on the stop card, the stay card, the trip length) is Abram's design call. The apps ignore the new key until then.

## How each one is built (`brain/src/brain/explain.py`)

| Recommendation | Factors, and the number each comes from |
|---|---|
| **A stop** (`explain.stop`, in `/v1/me/plans`; never in the blind pair) | **Match:** P(Good or better) from the rating model, the same number as "A strong / good match for you". **Score terms:** the score's own named terms x·β (`scoring.contributions`), each "counts for it" or "against it" (terms under 0.05 aren't said). **Travel:** the planner's travel minutes, mode and origin; for (≤15 min), neutral (≤30) or against (>30), the planner's own penalty lines. **Visiting window:** the card's window the planner fitted the visit into, plus the card's opening hours. **Best time:** whether the visit overlaps the card's best time, said either way. **Budget:** the stop's price against the day's budget block (m217). **Lunch slots:** the lunch estimate and the day's total, never a venue. |
| **A place to stay in "Best for your days"** (`explain.stay_rank`, in `/v1/trips/stays`) | The three parts of the ranking itself: 45% guests' rating, 35% the night's real cost (fees paid there included, m218), 20% distance from the centre. Each shows the stay's value, the range across these results, and the scaled part. `score` is their weighted sum, computed with the ranking's own functions, so it **is** the number the list is sorted by (tested). A missing rating or location is "counted as middling", and said. |
| **A stay against the trip** (`explain.stay_for_trip`, in `/v1/trips/stays/compare`) | **Minutes to each planned day and back** (`stayprices.trip_fit`): for if the worse of "there" and "back" on a typical day is within 15 min, neutral if within 30, against beyond. **The whole cost** (`cost_lines`). **Cancellation terms.** **Bank holidays** on the person's dates. **Days with no places yet**, listed as unknown. |
| **A trip length** (`explain.trip_length`, in `/v1/me/trips/length`) | **Matches:** the strong and good match counts. **The basis:** what the suggestion is built on, either the strong matches or, with too few, "your best N for now". **Pace:** the days those take at the person's places a day, keeping the day's shape. **Fit:** the trip's own days against them. **Unknown:** whether each day is feasible, which the day planner checks when it plans. |

## Synthetic demonstration (`test_api.install`'s test person, all ready cards, sample stays; 8 Nov)

**A day with a £25 budget, starting at Charing Cross**

**11:10, the National Gallery**
- A good match for you: the rating model gives a 63% chance you'd rate it Good or better.
- Crowds: counts against it, for you.
- 3 min on foot from Charing Cross station.
- You're there 11:10–12:22, inside the card's visiting window (10:00–18:00).
- Free. The day comes to £15 of your £25.

**13:27, lunch near the National Gallery**
- Right by The National Gallery: no travel.
- Lunch at a café, pub or food stall: about £15, an estimate. The day comes to £15 of your £25.

**15:30, Somerset House river terrace**
- A good match for you: … 66% chance …
- Rain outdoors: counts against it, for you.
- 13 min on foot from The National Gallery.
- You're there 15:30–15:56, inside the card's visiting window (15:30–20:30).
- Its best time is 16:00–20:30; this plan has you there 15:30–15:56.
- Free. …

**Places to stay, "Best for your days" (sample results)**

**Sample hotel K, Clerkenwell** (score 0.646 = 0.45×1.0 + 0.35×0.112 + 0.2×0.785)
- Guests rate it 9.8 out of 10 (these results: 7.6 to 9.8); 45% of the score.
- £389 a night (these results: £182 to £415); 35% of the score. *Against: the top-ranked stay is dear, and it says so.*
- 2.3 km from Charing Cross (these results: 0.6 to 8.7 km); 20% of the score.

**How long to stay (4 nights)**
- 0 strong matches for you in London (a 75% or better chance of Good), and 34 good ones, of 39 checked places.
- Fewer strong matches than your places a day, so it uses your best 12 for now (strong and good ones).
- At 4 places a day, keeping the day's shape (at most two history stops a day, one wander), those 12 take 3 exploring days.
- Your trip has 4 exploring days: 1 more than they need.
- Not known: whether each day is feasible (travel, opening days); the day planner checks that when it plans them.

## Found while building it

1. **The first trip-length wording was wrong.** It said "the strong matches take 3 exploring days" with 0 strong matches. The suggestion falls back to the best few days' worth of good matches, so `triplength.suggest` now returns what it was built on (`best`, `capped`), and the text says that. This is exactly the made-up justification the rule forbids, and a test now covers it.
2. **"Its times" was ambiguous.** The planner's window is the card's visiting window (Somerset House: 15:30–20:30, chosen for the light). It isn't the opening hours (08:00–23:00), so the factor now names it that way, with the hours beside it.
3. **A long gap in the demo day.** Lunch starts at 13:27 and the next stop at 15:30, when Somerset House's window opens. This is the planner's existing wait allowance, not caused by this work. It's noted for the next planner pass, alongside m216's finding.

## Checks

`brain/tests/test_explain.py` (6 tests):
- every stop factor carries the planner's own number (match %, score terms, travel minutes, the window), with the effect rules at 15 and 30 min, and unknown visiting windows said, never assumed;
- a stop against a budget, and a weak match;
- **a stay's explanation sums to the exact score the list is sorted by**, with fees counted and missing values said;
- a stay against the trip, and a trip length, including the case with no strong matches;
- a lunch slot is an estimate, not a venue;
- through the API: places in a plan explain themselves, the match words agree with the stop's, the score terms are the stop's own `why`, the budget text matches the day's total, the blind pair has no explanation, and the stays' explained scores come out in the list's own order.

**Hours:** Claude ~3 h. Abram: decide where (or whether) the apps show it. Recommended: a "Why this stop" section on the stop card, after the friends' round.
