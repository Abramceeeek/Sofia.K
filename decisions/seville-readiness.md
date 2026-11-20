# Seville: a read-only readiness check (20 Nov 2026; m310)

Abram's decision of 20 Nov, §10. His friend travels to Seville on 22 Nov. "Do not add unverified information or activate Seville just to meet the travel date. If Seville is not ready, state that clearly."

## The answer: Seville is not ready, and nothing was added or switched on

- ODYS has **no Seville destination, no Seville cards and no Seville data**. The app can't plan a day there, and can't open a trip to it: its trip list offers only London.
- Making it ready is days of checked work, not a switch (below).
- **For 22 Nov, the friend should not rely on ODYS in Seville.** What ODYS can honestly offer is nothing in Seville.
- The official sources the friend can use directly:
  - **Emergency: 112.** GOV.UK, "Telephone: 112 (ambulance, fire, police)" (gov.uk/foreign-travel-advice/spain/getting-help, read 20 Nov, "Still current at: 20 November 2026").
  - **Health:** "you need a Global Health Insurance Card (GHIC) or a European Health Insurance Card (EHIC)", and "A GHIC or EHIC is not an alternative to travel insurance" (gov.uk/foreign-travel-advice/spain/health, read 20 Nov).
  - **The British Embassy in Madrid:** "+34 917 146 300 or +44 207 008 5000" (GOV.UK safety-and-security page, read 20 Nov).

## What was checked

| Item (Abram's list) | Found | Ready? |
|---|---|---|
| **The destination registry** | `brain/data/airports.yaml` → `destinations:` holds one entry, `london`. `brain/data/destinations.yaml` holds `london` only. The development-only cities (`brain/data/dev/`) hold `paris`, never offered to anyone. **No Seville entry anywhere** | **No** |
| **Existing Seville cards** | none. The only mention of Seville in the repository is a sentence in `decisions/brain-global-readiness.md` about heat thresholds | **No** |
| **Official transport** | **TUSSAM** (city buses, tussam.es): **HTTP 403**, nothing read. **Metro de Sevilla** (metro-sevilla.es): the page loaded but **states no fare and no hours**: only a journey calculator and menu labels. Nothing is verified, so nothing would be recorded | **No** |
| **Official hours, prices, accessibility of places** | no cards, so nothing to check. Each card would need its own official page, as for London | **No** |
| **Spain emergency information** | **112** for ambulance, fire and police (GOV.UK, above). **The apps' emergency text is written for the UK:** "In an emergency, call 999 or 112. For urgent help that isn't life-threatening, call NHS 111" (`app/Sources/TripViews.swift:484`, `android/…/Trips.kt:453`), with Samaritans and NHS 111 in Help & safety. In Spain, 999 and NHS 111 are wrong advice | **No**: it needs a per-country emergency block before any non-UK destination |
| **Currency** | Spain uses the euro. The catalogue keeps each price in its own currency (`Money.currency`), and the Paris dev city is EUR. But the model's costs are in pounds (`cost_gbp`, 25 files) through a dated ECB conversion, and the apps show pounds for London | Partly: the plumbing exists (Paris), **unused** for any live city |
| **Time zone** | Seville is on `Europe/Madrid`: on 22 and 29 Nov, CET, UTC+1, one hour ahead of London (GMT, UTC+0), from Python's time-zone database. The destination record carries a time zone (`Destination.timezone`, Paris uses `Europe/Paris`). But **`Europe/London` is fixed** in `api.py` (the "today" and next-Saturday lines), `notify.py`, `ops.py`, `weather.py` and `evaluation.py`, and sunset times default to London (`sun.py`) | **No** for planning: a Seville day's "today", sunset and opening checks would be London's |
| **London-specific assumptions in the engine** | listed below | **No** |

### The engine's London assumptions (each would be wrong in Seville)

| Assumption | Where | Why it matters there |
|---|---|---|
| Travel times from TfL, and the London estimate | `tfl.py`, `travel.py` (`LondonEstimate`, used by `dayplan.py`, `destination.py`) | Seville's buses, metro and tram aren't TfL. Walking speed and transfer penalties were set for London |
| Weather from the Met Office | `weather.py` | a UK service. Seville needs another source, checked |
| Heat and cold thresholds (28°C / 8°C) and transfer pain from 15 minutes | `priors.yaml`, noted in `brain-global-readiness.md` | right for London, wrong for Seville's summer (`brain-global-readiness.md`, finding 4) |
| Bank holidays for England and Wales | `api.py`, `travelcalendar.py` | Spain's and Andalusia's holidays differ |
| Sunset at London's coordinates by default | `sun.py` (`LONDON = (51.5074, -0.1278)`) | On 22 Nov the Brain's own `sunset()` gives **16:04** in London and **18:10** in Seville (37.3891, −5.9845, `Europe/Madrid`). A Seville day planned with the default would put "the light" two hours early |
| Emergency and help text: 999, NHS 111, Samaritans | both apps, `offline.py` | wrong numbers outside the UK |
| The swipe places and the Test B brief | London places and Charing Cross | onboarding asks about London places; visitors get kinds of places (D116) |
| Prices in pounds, budgets in pounds | `cost_gbp` and the apps | euros need the dated conversion shown honestly |

## What "ready" would take (for after the round; not started)

- **The bar is the one London is held to** (`decisions/multi-city-travel-architecture.md`, and the readiness bar in `brain-global-readiness.md`): ready cards with official hours, prices and step-free status.
- **Before any card:**
  - a destination record (time zone `Europe/Madrid`, currency EUR, centre, language);
  - a travel model for Seville;
  - a weather source;
  - Andalusia's holidays;
  - per-country emergency text in both apps.
- **Hours (GUESS):**
  - Claude: about 12–16 h for the engine and both apps' per-country text, plus about 20 min a card;
  - Abram: about 1 h to review.

  It is a new-city decision under `after-9-nov.md` (#49: London, then UK cities, Europe and more), and waits for Checkpoint 3.

## Hours

Claude 0.75 h (20 Nov): the repository search, three official pages and this note.
