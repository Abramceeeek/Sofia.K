# When can ODYS say it supports a destination? (12 Nov 2026; m248)

**Decision (proposed): three levels, earned by measured data, never by the number of cards.** Abram, m244: "A destination should not become fully supported simply because a few places have been entered into the database."

`brain/src/brain/readiness.py`, `brain/tests/test_readiness.py` (4 tests), `brain/data/formats.yaml`.

| Level | What it means | How it's reached |
|---|---|---|
| **Development** | Data is being gathered. Nothing is offered to anyone | The default |
| **Preview** | Testers could try it, labelled as a preview | Every **essential** item passes |
| **Supported** | Offered to everyone | Every item passes, **and** Abram has reviewed the coverage |

## The checklist

| Item | Essential? | Passes when (thresholds are GUESSES, for Abram) |
|---|---|---|
| Emergency numbers | yes | The country's official numbers are in `emergency.yaml`, each with its source and the date it was checked |
| Public holidays | yes | They come from the government's own page and cover the trip's year |
| Currency | yes | The ECB publishes a rate for it (`fx.py`) |
| Time zone | yes | It's a valid IANA zone (clock changes, opening times) |
| Experiences | yes | At least **20 ready**, at least 20 of them with an independently sourced location (Wikidata or OpenStreetMap) |
| Variety | yes | At least **6 of the 9 kinds**, so it's not only museums and landmarks |
| Getting around | yes | An official journey planner. Estimates labelled as estimates count as partial |
| Date and number formats | no | The locale's formats are recorded from Unicode CLDR |
| School holidays | no | From official sources where they change crowds, or "not relevant" |
| Opening hours | no | **80%** have hours (or event sessions) read on an official page in the last 180 days |
| Step-free access | no | **50%** known from a named source. Unknown never counts as "no" |
| Areas | no | **60%** have a neighbourhood or district named by a source |
| Seasons | no | Every outdoor experience has seasonal information |
| Photos | no | Every photo's licence and credit checked one by one |

## Today

| | London | Paris |
|---|---|---|
| **Level** | **Preview** | **Development** |
| Essential items | all pass | experiences 19 of 20 (partial); getting around: estimates only (partial) |
| Quality items short | hours 28 of 49 fresh; step-free 17 of 49; school holidays one London borough (Westminster); seasons 14 of 22 outdoor | step-free 12 of 19; areas named 2 of 19 (arrondissements 19 of 19, 11 from the postcode) |

So **London is not "supported" by this bar today**, even though it's live for testers. That's the honest reading: its essentials are in place, but too much of what a careful traveller needs (step-free access, fresh hours) is still unknown.

## Paris: what it needs next

1. One more ready experience: the drafts need their hours read (the Palais Garnier, the Jardin du Luxembourg, the Petite Ceinture), or the Batobus closure notice explained.
2. Getting around: Île-de-France Mobilités and RATP refused automated reading (403). The options are a person reading them, or a GTFS feed (licence UNVERIFIED, `destination-intelligence.md`).
3. Step-free access for 7 places, and neighbourhood names from a source the tourist office would have given (403).

**Hours this step:** Claude ~1 h.
