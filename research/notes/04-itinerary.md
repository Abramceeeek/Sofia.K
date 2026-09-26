# Area 4 — Itinerary building

**Decision:**
- **Solver:** use **OR-Tools** routing as an orienteering problem with time windows. Each candidate place is an optional stop worth its predicted satisfaction (Areas 2 and 3), and opening hours are time windows.
- **Travel times:** precompute them for the 50 London places in v0 (cut from 100 on 2026-09-26). Walking comes from OSRM or openrouteservice, transit from the TfL Journey Planner, and the results are cached.
- **Weather:** Met Office DataHub free tier.
- **Peak and finish:** get "one peak and a good finish" by solving once for each candidate final stop (5–10 small solves) and keeping the best plan. It is a toggle (D8), and it is **off by default** (D15): the default objective is the sum of predicted moment satisfaction.
- **LLM:** it only writes the explanation from the solver's output. It never chooses stops.
- **Cost: about 11 founder hours for v0.** That breaks down as matrices 2, solver model 4, peak/finish toggle and weather rules 2, tests 2, explanation prompt 1.

## What exists (ranked)

| # | Name | Maturity | Licence | Why it matters |
|---|---|---|---|---|
| 1 | [Google OR-Tools](https://github.com/google/or-tools) 9.15 | ★14.1k, last commit 2026-09-17, wheels for Py 3.10–3.14 | Apache-2.0 | `AddDisjunction(penalty)` lets the solver drop a stop at the cost of its prize, which gives an orienteering problem. It has a built-in time-window dimension |
| 2 | [PyVRP](https://github.com/PyVRP/PyVRP) 0.14 | ★701, 2026-09-26, Py ≥3.11 | MIT | Supports prize-collecting / team-orienteering with time windows natively. Backup if OR-Tools modelling gets awkward |
| 3 | TfL Unified API (Journey Planner) | Production; free key gives 500 req/min | Modified OGL v2.0, attribution required | The only source covering Tube, bus, DLR **and river bus** timetables. It has no matrix endpoint, so we precompute |
| 4 | [OSRM](https://github.com/Project-OSRM/osrm-backend) | ★8.1k, 2026-09-13 | BSD-2 | Its foot profile and Table service give a walking matrix. Runs in Docker. No transit |
| 5 | openrouteservice (hosted) | Free: 2,500 req/day; a matrix request covers up to 3,500 routes | Service terms | A walking matrix without hosting anything: 50×50 fits in one request |
| 6 | Met Office Weather DataHub / Open-Meteo | Production | DataHub: free for 360 calls/day. Open-Meteo: free for **non-commercial use only**, $29/mo commercial | Hourly forecasts for heat and rain penalties. Caching a few London points each hour needs fewer than 100 calls a day |
| 7 | [Valhalla](https://github.com/valhalla/valhalla) / [OpenTripPlanner](https://github.com/opentripplanner/OpenTripPlanner) | ★6.3k MIT / ★2.7k LGPL-3.0, both active | — | Self-hosted multimodal routing. Needs a London GTFS feed, which TfL doesn't officially publish (unknown). Later, not v0 |
| 8 | [ITINERA](https://github.com/YihongT/ITINERA) (EMNLP 2024) | ★67, last commit 2025-05-22 (stale) | GPL-3.0 | Closest design to ours: an LLM picks candidate POIs from the request and a spatial optimiser orders them. Shanghai only, and GPL, so we copy the idea, not the code |

## What the evidence says

- **Planning a tourist day is a well-studied problem.** It is modelled as an orienteering problem with time windows. There are two surveys (Gavalas et al. 2014; Gunawan et al. 2016), and a 2022 review of 102 papers found this the most widely used model (Ruiz-Meza & Montoya-Torres). A version with public transport and time-varying travel times ran in real time for a whole city (Garcia et al. 2013, San Sebastián).
- **LLMs cannot plan under constraints on their own.**
  - The best agent (GPT-4-Turbo with ReAct) passed 0.6% of TravelPlanner tasks, and every other LLM passed none (Xie et al. 2024). o1-preview reached 10% even when given all the information up front.
  - Pairing the LLM with a formal solver reached 93.9% (Hao et al., NAACL 2025).
  - Adding generate-and-test critics gave a 4.6× lift (Gundawar et al. 2024), reaching 20% with GPT-4-Turbo and 65% with o1-preview (as reported by Hao et al.).
  - Having the LLM feed a planner gave 100% valid plans, where standalone LLMs produced invalid ones 86% of the time across 20 cities (TRIP-PAL 2024).
  - Personalised quality is still weak: fewer than 10% of LLM itineraries reach human level (TripTailor, ACL Findings 2025).
- **So the LLM handles language in and out, and the solver chooses and orders stops.** This also keeps explanations truthful ("we swapped the walk for the boat because the heat penalty dominated").
- **Peak–end in tourism is not settled.**
  - One field experiment found that an end-of-trip boat ride raised tour satisfaction (Park et al. 2018). I've only seen it cited, so it is **UNVERIFIED**.
  - A 2025 study tested the rule on tourists (Lin, JHTR), but search summaries disagree on its result, so it is also **UNVERIFIED**.
  - Area 6 will settle this. For v0, make peak/finish a switchable rule so our own per-stop and end-of-day ratings can test it: regress the day's rating on the mean, maximum and last stop rating.

## Gaps we'd have to fill ourselves

- **Time-varying utility** (heat × walking at 2 pm, fatigue late in the day). OR-Tools stop prizes are fixed per stop. Approximate by splitting the day into 2–3 slots with slot-specific scores, or re-score and re-solve. Solve time for up to 30 candidates is still to be measured.
- **Time-of-day transit.** Build one TfL matrix per slot. 50×49 = 2,450 journeys, which takes about 5 minutes per slot at 500 requests a minute.
- **Transfer-time thresholds** (15 min is fine, 50 min ruins the afternoon). Model these as a nonlinear penalty on each leg's travel time, with thresholds from Area 6.
- **Mid-day re-planning** when the weather turns: a trigger plus a re-solve from the user's current location. After v0.
- **Opening hours and visit durations** for each place: hand-tagged in the Area 2 place database.
- **Moments, not places (D9).** Each moment has an approach start point (for example a specific tube exit) and an end point. So the travel matrix runs from each moment's end point to the next moment's approach start, and it is asymmetric, which OR-Tools handles natively. A moment's time window uses its `best_time` (light, crowd window) as well as opening hours. The extra tagging is counted in Area 2; the solver itself needs no extra hours.

## Risks / unknowns

- **TfL caching terms.** TfL's terms on bulk caching of journey results haven't been read yet. Read them before running the precompute.
- **Open-Meteo licensing.** The free tier stops being compliant as soon as we charge anyone, so default to the Met Office DataHub.
- **The peak/finish rule could lower the average day.** It needs to be tested, not assumed.
- **Real journey times vary** (delays). Add slack to every transfer.
- **The LLM could misstate why the solver chose something.** Generate the explanation from a structured diff (what changed, and which weight drove it) and check the text against that diff.
