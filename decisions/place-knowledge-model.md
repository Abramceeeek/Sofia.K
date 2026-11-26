# The place knowledge model: a proposal (26 Nov 2026, batch 8 work package E)

Abram (m363): "a proper place knowledge model, not six more tags". This is a proposal for him to challenge before anything is built. **No place data is changed by it.** The two worked examples below use only facts the cards and the checked layer already hold, each with its source as it stands today.

## Decision first

- **A place is not one thing.**
  - A place has one or more **experiences**: what a visitor actually does there.
  - Each experience has **appeals**: which kind of person might enjoy it, and why.
  - Each experience also has **cautions** (who might not) and **practicalities**.
- **Every attribute carries its evidence**: a value, a source type, a source, the date checked, and a confidence.
  - Missing is "unknown", never a negative.
  - A crowd-sourced label is never a verified fact.
- **Today's 15 tags are kept as a view derived from the richer record**, so the person model, the planner and every test keep working while the record grows.
- **New dimensions enter the person model only when the places carry them.** That means at least 80% of ready London places filled or explicitly unknown, so no traveller is asked a question that has no use yet.
- **Two findings make this urgent:**
  1. **Tate Modern is tagged history 2** (`m_tate_modern.yaml`). There is no art dimension, so an art lover's taste has nowhere to go, and the gallery recommends itself to history lovers.
  2. **Whether a card's fact is checked or a guess lives only in YAML comments** ("`# CHECKED`", "`# GUESS`"). No code can read it. Only 35 of 74 cards have facts in the machine-readable checked layer.

## 1. The record

```
Place  (one location; facts about the whole place)
  id, name, location, area, official_url
  facts: opening hours, dated closures, access, contact      ← each an Evidence
  experiences: [Experience, …]

Experience  (what a visitor does there: one place can hold several)
  id, title, what_you_do (plain text), activity: look | walk | eat | ride | learn | play | shop | rest | swim | climb
  dimensions: {dimension: Evidence(level 0–2, …)}           ← §2
  atmosphere: [Evidence(word)] from a fixed vocabulary        ← §2
  appeals: [Appeal]        who might enjoy it, and why
  cautions: [Caution]      who might not, and why (from attributes, never stereotypes)
  practicalities: duration, price (adult, child, concession), effort, age, booking, best times, seasons, weather
  derived_tags: the 15 tags of today, computed from the above (back-compatibility)

Evidence
  value
  source_type: official | odys_research | inferred | crowd_label | unknown
  source: URL or file, and the quote where there is one
  checked: date
  confidence: high | medium | low        (official and fresh → high; inferred → low; crowd_label → low)

Appeal
  for: an interest or atmosphere word (food, history, art, photography, quiet, families…)
  why: one sentence, built only from the experience's own evidence
  strength: defining | partial
  evidence: [Evidence references]
```

**Source types, strongest first:**
1. **official:** the place's own page, with the quote and the date.
2. **odys_research:** ODYS read official or reliable sources and wrote it down (D91: Claude verifies and marks ready; Abram flags disagreements).
3. **inferred:** a judgement from descriptions, such as "absorbing" or "romantic". Always labelled. **Never used for a hard rule, and never supports more than a "partial" appeal on its own.**
4. **crowd_label:** an Overture or OpenStreetMap label (a cuisine, "halal"). A candidate only, never verified. OSM data is ODbL, so it is kept as a separately credited layer.
5. **unknown.**

## 2. The dimensions (Abram's list), with how each is represented and sourced

| Dimension | Representation | Best source | Feeds the model as |
|---|---|---|---|
| Activities and experiences | `activity` and `what_you_do` for each experience | official, odys_research | the experience list itself |
| History and culture | level 0–2, plus kind (museum, historic site, living culture) | official | `history_culture` (today's tag) |
| **Art and creativity** (new) | level 0–2, plus kind (gallery, street art, design, performance) | official | a new feature, `art` |
| Nature and scenery | level 0–2 for green space; views | official, odys_research | `green_nature`, `movement_views` |
| **Architecture** (new) | level 0–2 | official, odys_research | a new feature, or part of `awe` (to test) |
| Food and cuisine | meal kind (substantial, tasting, snack, coffee: m360), cuisines, price band, dietary labels | official for menus; crowd_label for cuisine candidates | `food`, plus meal kind for G15 |
| **Shopping** (new) | level 0–2, plus kind (market, boutique, department store, arcade) | official | a new feature, `shopping` |
| **Nightlife** (new) | level 0–2, plus evening hours | official | a new feature, by time of day |
| Social experiences | good for groups, a place to bring people | odys_research | `social_pull` |
| **Atmosphere** (new) | words from a fixed list: peaceful, lively, grand, intimate, unusual, romantic, family-friendly; each can be tied to a time window | odys_research, inferred | new features, one per word, only once places carry them |
| Crowds and noise | level for each time window (weekday morning, weekend afternoon…) | official ("quieter times" pages); otherwise inferred, low confidence | `crowds`, by time |
| Physical effort | walking distance, stairs, hills, standing time | official access pages | `walking_effort`, `active` |
| Accessibility | step-free (yes, no, partly), seating, toilets | official only | a hard rule for a stated need (never inferred) |
| Age suitability | minimum age; children only; suitable for children | official for rules; inferred for "suitable" | hard rules; family appeal |
| Visit duration | minimum, typical and maximum minutes | official suggestion, odys_research | the planner's duration |
| Price and value | adult, child, concession, free; date checked | official | `cost_per_10gbp`. "Value" is never stored; it's personal (worth to them, computed) |
| Seasonal suitability | dated closures, seasonal events, weather dependence | official | the opening rules, the rain rule |
| Practical restrictions | booking, timed entry, bag rules | official | the "book ahead" line, and quality's practicality perspective |

**Who might dislike it** is never a stereotype. Cautions come from the experience's own attributes. For example: "busy on Saturdays" (official), "standing room only" (official), "a steep climb" (official). The engine then matches them to a traveller's own leanings, as it does today for crowds ("You picked quieter days, and this place is busy").

## 3. Two worked examples, from today's data only

**Borough Market** (`m_borough_market_graze`, plus the checked layer). One place, one experience, several appeals:

| | Value | Evidence today |
|---|---|---|
| What you do | "You taste your way round the stalls, pick a few things, and eat standing up among the traders." | odys_research (the card) |
| Opening hours | Mon closed; Tue–Fri 10:00–17:00; Sat 09:00–17:00; Sun 10:00–16:00 | **official**, boroughmarket.org.uk/visit-us |
| Step-free | "laid out on a single ground-floor level … some cobbles" | **official**, the same page |
| Appeal: food | defining: food is the experience itself | odys_research (food tag 2; the card's text) |
| Appeal: photography | defining | **inferred** (photo_potential 2, set by hand; no source): stays partial until a source supports it |
| Appeal: places to bring people | defining | inferred (social_pull 2) |
| Appeal: history | **partial** | inferred (history 1). The card states no historical fact, so no history claim can be made until one is sourced |
| Caution: crowds | "Saturdays are the busiest; late weekday mornings are calmer" | the card marks it **GUESS**: low confidence until official |
| Meal kind | tasting (m360: a market) | the catalogue kind |
| Price | about £15 a person | the card marks it **GUESS** |
| Duration | 45–75 min | **GUESS** |

**Tate Modern** (`m_tate_modern`):

| | Value | Evidence today |
|---|---|---|
| What you do | "walk down into the vast Turbine Hall, then up through free galleries of modern art" | Turbine Hall entrance and free collection **official** (tate.org.uk, read 24 Nov); the rest odys_research |
| Hours | Sun–Thu 10:00–18:00, Fri–Sat 10:00–21:00 | **official** |
| Price | free collection | **official** |
| Appeal: art | **defining**, though today's record has nowhere to say it | official ("galleries of modern art") |
| Appeal: history and culture | the tag says 2; under this model it would be culture, not history | inferred |
| Step-free | "four lifts … a step-free route isn't stated" | official; recorded as **unknown**, not "no" |

So with this model, Borough Market becomes a strong match for a food lover (defining food, from the card's text). It stays a possible poor match for a quiet traveller (crowds, a low-confidence caution until official). And it makes **no** history claim until a historical fact is sourced. That is the demonstration Abram asked for, at the level of the data.

## 4. Overture and OpenStreetMap: assess before integrating

1. **Measure quality first (about 3 h).**
   - Draw 50 London food and drink places from the pull (`decisions/plan-london-then-cities.md`).
   - Check each against its own website: does it exist, and is its category right?
   - Proposed acceptance: at least 90% exist and are correctly categorised.
2. **If it passes,** Overture becomes a **candidate layer.**
   - Places can be suggested ("an option nearby, not checked") but never planned.
   - A place is planned only once a card with official hours exists.
3. **Matching** existing cards to Overture by name and distance (`overture_id` already exists on a card's place) gives each card a second, independent location and website.
4. **Labels** (cuisine, "halal") stay `crowd_label`. They're never shown as verified, and never used for a dietary rule (D19, D123: food needs wait for consent, a DPIA and a checked source).

## 5. Migration, and the hours (GUESSES)

| Step | What | Claude's hours |
|---|---|---|
| 1 | The schema in code (`catalogue.py` gains Experience, Appeal, Caution and Evidence), with today's tags derived from it. Nothing changes for the planner | 6 |
| 2 | Move the YAML comments' CHECKED and GUESS into evidence fields for the 74 ready cards, mechanically, then by hand where the comments are unclear | 5 |
| 3 | New dimensions (art, architecture, shopping, nightlife, atmosphere) for the 74 places, from official sources, with Abram's one-line flag list (D91) | 12 |
| 4 | The engine reads appeals and cautions, with evidence on both sides, in shadow mode first (`match.py`) | 4 |
| 5 | The Overture quality sample (§4) | 3 |
| 6 | New person-model features, once the places carry them, with priors and a bench comparison | 4 |

**Total:** about 34 h of Claude's time over two or three batches. Abram's part: about 1 h to challenge the vocabulary and the source rules, and his one-line flags on the research cards.

## 6. Questions for Abram

1. **The atmosphere vocabulary:** peaceful, lively, grand, intimate, unusual, romantic, family-friendly. Add or remove words?
2. **May "inferred" support a partial appeal, as proposed?** The alternative is that only official or researched facts appear in a reason.
3. **Should step 3 (new dimensions for the 74 places) come before or after the Overture sample?** The proposal is before: understand 74 well before adding thousands.
