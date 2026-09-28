# Decision log

Founder decisions that amend `KICKOFF_PROMPT.md`. Newest first. Where this log and the kickoff brief disagree, this log wins.

## 2026-09-28 — study contact details; the dates confirmed

| # | Decision | Replaces | Why |
|---|---|---|---|
| D106 | **Dates confirmed:** Test B reports around 23 Oct, and **Checkpoint 3 is in the week of 2 Nov** (was 9 Nov).<br>**Study contact:** "Abram" and abram@abdurakhmonbek.com, in every blank.<br>**The study's WhatsApp number** (+44 7771 477717) goes in the consent form, the privacy notice and the first message after sign-up, **never in the public recruitment posts**, which use the Tally sign-up link only.<br>**The example shot card is a ready card with a shot card, Waterloo Bridge at sunset,** instead of seed moment 1, so the South Kensington walk no longer blocks recruiting.<br>**Claude copies the real brief and generic plan** into `validation/raw/testb/`.<br>**Abram does the ICO self-assessment** and pays if required; he confirms the WhatsApp checklist today (quick replies and labels later) and pastes the swipe table next | D105's proposed dates; the seed-1 example card; blockers 2, 6 and 7 | Founder decisions |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m93 | **The WhatsApp number stays off the public `privacy.html` as well** as the posts: it says participants get the number when they sign up. It is in `privacy-notice.md`, which is sent in the chat | `test-d-landing/privacy.html`, `make_study_pdf.py` |
| m94 | **The consent form and privacy notice go as one PDF** (`study-info.pdf`) with the first message after sign-up. WhatsApp shows neither tables nor tick boxes, so consent is a reply: "I agree", or "I agree, and keep my voice notes" for the 30-day audio opt-in. `make_study_pdf.py` makes the PDF and the public page from the Markdown, and drops internal notes (now HTML comments) | `validation/` |
| m95 | **The AI line is accurate for a personal Claude account:** on Free, Pro and Max (including Claude Code) Anthropic is a separate controller, not our processor; it is a processor only on the API, Team or Enterprise (privacy.claude.com, 28 Sep). The notice says so, names Anthropic and the US, says model training is off, and says the chats are deleted with the rest of a person's data. **Staying on the personal account, or moving to a commercial plan, is Abram's call** (blocker 10 in `recruit-now.md`; my recommendation: stay for the study) | `privacy-notice.md`, `consent-form.md` |
| m96 | **The AI help is described as it is:** it helps write up the summary and run the planning program; the plans come from the Brain, not an AI chat. It gets answers under a code like P07, never names, numbers or audio | consent form, posts' reply template |
| m97 | **The Tally row is verified:** Tally is Belgian, stores form data in the EU and is our processor under its data processing agreement (tally.so/help, 28 Sep). The sign-up form gets a one-line privacy note at the top, and no fields beyond first name, number, "how do you know me?" and 18+ | `privacy-notice.md`, `recruit-now.md` §4A |
| m98 | **First message after sign-up:** sent within a day; one reminder after 3 days without an "I agree", then leave it. It carries the 999 line and "I reply within a few hours" | `recruitment-posts.md` |
| m99 | **The Waterloo shot card:** the middle of the bridge; west to Parliament and the London Eye, then east to St Paul's and the City; the 20 minutes either side of sunset ("around 4:30pm after the clocks go back"). Text only, the same for everyone. It is the only shot card so far, so only plans that include it get Test C's share prompt | the Waterloo card, `shot-card-example.md` |
| m100 | **A tracked copy of the real brief and generic plan** sits in `validation/testb-real/` (no participant data), because `validation/raw/` is git-ignored and each cloud session starts empty. The brief's `sunset` is 18:20 (Sat 10 Oct) for the first batch | `validation/testb-real/`, `validation/raw/testb/` |
| m101 | **The published screens page** now shows the new dates (D84) | https://claude.ai/artifact/CqRgaT1e328Qm4H2cX3W91 |

## 2026-09-28 — start point confirmed; recruiting pulled forward

| # | Decision | Replaces | Why |
|---|---|---|---|
| D105 | **The start point is Charing Cross (Trafalgar Square exit).**<br>**Cards:**<br>- the Courtauld is in once its open days are confirmed (done: "Open daily, 10:00–18:00", official site);<br>- the London Transport Museum is out of Test B (booking plus £18.50) but stays in the app.<br>**The week-of-12-Oct tasks are pulled forward to now:**<br>- the swipe 16;<br>- the aspiration question and materials check;<br>- the sign-up form, landing page and analytics;<br>- the recruitment posts;<br>- the real generic plan, before the first Test A chat.<br>**Proposed, for Abram to confirm:** Test B reports around 23 Oct (was ~2 Nov) and **Checkpoint 3 in the week of 2 Nov (was 9 Nov)** | D86's week-of-12-Oct schedule; D104's recommendation | Founder decisions. Blockers and the walkthrough: `validation/recruit-now.md` |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m87 | **`in_test_b: false`** keeps a card out of Test B plans; the run lists what it left out | `moments.py`, `testb.py`, the Transport Museum card |
| m88 | **Sunset-aware "Best" lines:**<br>- the brief can give `sunset`, and cards (and generic stops) can give `best_around_sunset` (minutes from sunset);<br>- 12 sunset or dusk cards now do;<br>- plans used before 25 Oct (sunset around 18:00) no longer say "Best: Sunset" at 16:30, because moving recruiting earlier puts some plan days before the clocks change;<br>- sunset times are from sunrise-sunset.org | `moments.py`, `testb.py`, 12 cards, the brief |
| m89 | **The example brief is a Saturday** (`weekday: sat`, "A Saturday out in London"), so weekday-only City cards stay out, and it carries the sunset time. The generic plan's last stop is worded to hold before and after 25 Oct | `brain/data/testb/*.example.yaml` |
| m90 | **Provisional swipe 16 = the current list** in `interview-script.md` §3, if the results still show low-n places; lock the 16 before the first chat | `validation/recruit-now.md` |
| m91 | **The ICO fee self-assessment is listed as a blocker before collecting data,** as the validation checklist already said. `CLAUDE.md`'s gate says "before the first paid client". Paying is Abram's decision | `validation/recruit-now.md` |
| m92 | **Actual hours:** 10 min for the start point and card flags, logged 28 Sep (D82) | `LOG.md` |

## 2026-09-28 — dry runs finished; overlap check; the start point

| # | Decision | Replaces | Why |
|---|---|---|---|
| D103 | **The familiar-favourite rule is off for the real Test B**, so the test measures prediction, not memory, and **on by default in the v0 app.** **The dry runs are finished;** no more rounds. The two earlier rounds are logged at about 30 min each | D100's proposal | Founder decisions |
| D104 | **Before recruiting:**<br>- a check of how much different people's personal plans overlap, warning if two dissimilar people share more than half their stops;<br>- 8–10 verified research cards near the real Test B start, including indoor options for rain;<br>- a start-point recommendation from card density and transport.<br>**Done:**<br>- the overlap report;<br>- nine cards near Charing Cross, eight of them indoors.<br>**Recommended start: Charing Cross (Trafalgar Square exit), for Abram to confirm.** It has 16 Saturday cards within a 25-min walk (London Bridge: 5), all three sunset river cards nearby, is busy at weekends, and has five Tube lines within a few minutes' walk | — | Founder request. Analysis and card list: `research/seed-moments/06-start-point-cards.md` |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m82 | **Overlap thresholds (GUESSES):**<br>- "dissimilar" means the cosine similarity of two people's δ, in prior-sd units, is below 0.3;<br>- a person whose δ is shorter than 0.5 prior-sds has "too little data" and is never flagged;<br>- flexible lunch slots don't count as shared;<br>- the report runs across every personal plan in the output folder, so it covers people planned on different days | `testb.py` (`overlap_report`) |
| m83 | **Meal cards** (`meal: lunch`: the crypt lunch, dim sum) are only ever the day's lunch stop and never a rain swap. P02 had two lunches in one plan before this. **A flexible lunch slot is also offered at the start point** | `testb.py`, `moments.py`, 2 cards |
| m84 | **The example brief starts at Charing Cross** (TfL coordinates), and the example generic plan's first leg starts there too | `brain/data/testb/*.example.yaml` |
| m85 | **Card details:**<br>- Courtauld open days are UNVERIFIED (assumed daily; the official hours snippet gives no days);<br>- St Martin-in-the-Fields uses its old postcode's centroid (WC2N 4JJ, closed in 2008);<br>- Victoria Embankment Gardens sits at Embankment station's coordinates;<br>- station names marked * are Claude's knowledge | 9 cards |
| m86 | **Actual hours:** 0.5 h each for the two earlier rounds (D97–D98, and round 1), logged 28 Sep on Abram's figure (D82) | `LOG.md` |

## 2026-09-28 — dry-run feedback round 2

| # | Decision | Replaces | Why |
|---|---|---|---|
| D102 | **Round 2 of the dry run (friends; fixes only, not test data):** 6 of 6 preferred the personal plan again, now against a generic plan several called "solid". One answer (person 1.3) seems to have read P02's description with P01's plans, so it is discounted: 5 of 5 valid.<br>**The fixes:**<br>1. Every plan has a meal stop around midday.<br>2. Rain swaps respect the person's weights.<br>3. Pace sets how long people stay, not just the number of stops.<br>4. Travel legs start with "walk to [station]", and the Serpentine → Natural History Museum walk is about 20 min.<br>5. The generic plan doesn't cross the river twice.<br>6. Titles name the place.<br>7. Busy food stops add queue time | D100's plan text | Founder decisions from the friends' feedback |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m74 | **How lunch works (GUESSES):**<br>- **Lunch counts as one of the brief's stops** (4 stops, including lunch), so a 5-hour day stays doable and both plans have the same number of stops.<br>- It starts 11:30–13:30 and lasts 45 min when flexible, at about £15 (`lunch_gbp` in the brief).<br>- A food card becomes the lunch only if the person is predicted to like it (+0.5 or more). Otherwise it's a flexible "Lunch near X" slot, scored as neutral, placed beside a place in the plan.<br>- A strong bonus makes the solver keep a lunch over an extra sight.<br>- The generic plan marks its lunch with `lunch: true`, and a warning fires if it has none | `testb.py`, `planner.py`, `generic.example.yaml` |
| m75 | **Rain swaps:** a swap must be predicted at least "fine" (the 2/3 rating threshold) and must not have, at full strength, a feature the person clearly dislikes (e.g. crowds) | `testb.py` |
| m76 | **Pace:**<br>- "relaxed" means a confident dislike of packed days; relaxed people get longer stays where the day has room (the top of each card's range, at least 45 min in a garden and 60 in a park), moving later stops back but never out of their windows or past the end rule;<br>- "packed" and "even" keep the usual stays;<br>- extra time goes into stays before it goes into gaps | `planner.py` (`extend_dwell`), `testb.py` |
| m77 | **Walking speed 4.5 km/h and a 1.35 detour factor** (was 4.8 and 1.3, both GUESSES), calibrated to friends' "about 20 min" from the Serpentine to the Natural History Museum. Every walking estimate gets about 12% longer | `travel.py` |
| m78 | **Leaving a stop by Tube or bus:**<br>- cards can name `end_station` (10 cards now do; station names are Claude's knowledge);<br>- otherwise the card's arrival station is used, or "the nearest station";<br>- the arrival line then names no station, because the travel line already does | 10 cards; `moments.py`, `testb.py` |
| m79 | **Titles:** "Place: title" when the title doesn't already name the place. Five cards have a hand-written `plan_title` where that read badly (outdoor dining, karting, the whale hall, both boats) | 5 cards; `moments.py` |
| m80 | **Queue time:** `queue_min` of 10 min (GUESS) on Beigel Bake and Borough Market, added to the time there and shown as "Allow about 10 min to queue." | 2 cards |
| m81 | **Actual hours:** 1.0 h for round 2 (sending, collecting, reading), logged 28 Sep (D82) | `LOG.md` |

## 2026-09-28 — dry-run feedback round 1; visitor mode parked

| # | Decision | Replaces | Why |
|---|---|---|---|
| D100 | **Round 1 of the dry run (6 friends, 3 per person; fixes only, not test data):** 6 of 6 preferred the personal plan and 6 of 6 spotted it, from how well the places fitted, never from the format. Read as "blindness held, personalisation visible". Caveats: the persona lines listed likes and dislikes openly, and the generic plan was a weak landmark checklist.<br>**The fixes:**<br>1. The generic plan becomes a strong "best of London" day (market, museum, view, walk), and Abram writes the real one to that standard.<br>2. A familiar-favourite rule is proposed (below).<br>3. Costs read "about £X for food and entry, plus about £Y transport".<br>4. Stop times are ranges.<br>5. "Best" lines show only when the time matches.<br>6. Travel legs are fixed (Greenwich uphill walk; no pier unless by boat; St James's → Palace gone).<br>7. Rain swaps for outdoor stops.<br>8. Wording: one start line, full sentences, no repeats, the London Eye is a walk-past.<br>9. A small buffer between stops.<br>10. The real Test B asks for a gut reaction and marks possibly AI-assisted answers | The D97 plan text and the landmark generic example | Founder decisions from the friends' feedback |
| D101 | **"Visitor mode" is parked on the after-9-Nov list (#18) and merged with #14 Stage 2:**<br>- flights by link-out;<br>- entry requirements as general information plus links to the GOV.UK checkers only, never personal immigration advice (regulated: Immigration and Asylum Act 1999, s.84);<br>- a driving-licence question with GOV.UK links;<br>- visitor onboarding with home-contrast novelty.<br>Linked to Test E: Uzbek agencies' clients are the target visitors. **No work before 9 Nov** | — | Founder request (D75) |

**Proposed, for your yes or no:**
- **The familiar-favourite rule (`--familiar`):** the personal plan holds exactly one place the person loved (if one fits the day's hours, the budget and the day of the week), and every other stop is a place they haven't marked as loved. The solver tries the three best-scoring loved places and keeps the best whole day.
- **Today it is off by default,** and the dry run uses it. Say yes and it becomes the default for the real Test B; say no and nothing changes.
- **The trade-off (my judgement):** a familiar place makes the plan feel personal and gives an easy anchor to the day. It also makes the personal plan easier to spot, and it tests "we remembered what you like" as well as "we predicted what you'll like".
- **It only works for loved places that have a card:** 7 of the 16 swipe places do today.

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m65 | **Places they didn't enjoy are never planned**, via each swipe place's `cards` list. This is always on, because it's what the friends' feedback on Big Ben implied | `brain/data/swipe_items.yaml`, `testb.py` |
| m66 | **Transport estimate:** £3.00 per Tube or bus leg (Zone 1 pay-as-you-go off-peak, TfL fare API, valid from 4 Jul 2026), capped at £8.90 (Zones 1–2 daily cap). Walking legs are free. It doesn't include getting to the start or home | `testb.py` |
| m67 | **"Best" lines need a `best_window` on the card;** with none, the line is never shown. Windows were set on 15 cards. Sunset windows are 16:00–17:00 for the Test B weeks (after 25 Oct). Compound lines were cut to their time-specific part, e.g. "At dusk, when the dome is lit". The spring and summer notes on the park cards stay in the card but aren't shown in Oct–Nov | 15 cards; `moments.py` |
| m68 | **Rain swaps:** indoor or covered moments (outdoor exposure ≤ 1, not dry-only), within 20 min and able to start within 30 min of the stop's time, inside the budget, and each used once. A loved place can be a swap, because it's a backup, not part of the planned day. If nothing is found and the plan has no indoor stop, the review says "add one by hand". The generic plan's swaps are written by hand (`rain_swap`) | `testb.py` |
| m69 | **Buffer:** 5 min after each walk and 10 min after each Tube or bus leg (GUESS). It changes arrival times only; the travel minutes shown stay the estimate | `planner.py` |
| m70 | **Card text fixes for full sentences and no repeats:**<br>- Garden at 120, Horizon 22, Canary Wharf and City towers (no double "lift" or "escalators" lines);<br>- British Museum and Natural History Museum now start from their stations (the routes inside are unchanged);<br>- Richmond, the steakhouse and Borough Market reworded;<br>- Greenwich hill starts at Cutty Sark DLR (TfL coordinates) with a 20-min approach;<br>- the boats start at Cutty Sark DLR | 12 cards |
| m71 | **`cost_kind` on cards** (food / entry / ticket / hire). The boats are "ticket" and the bike loop is "hire"; others follow the food tag | 3 cards; `moments.py` |
| m72 | **The review gains:** the familiar favourite, "Places they loved: in the plan or why not", "Places they didn't enjoy", and text checks (a line without a full stop; arrival and description sharing 5+ words in a row). A warning fires if the generic plan's first `from` isn't the brief's start | `testb.py` |
| m73 | **"Possibly AI-assisted" answers are marked in the TestB tab's "Why (open)" cell** (there is no notes column). The choice still counts | `validation/interview-script.md`, `test-plan.md` |

## 2026-09-28 — the real Test B day: 12:00–17:00

| # | Decision | Replaces | Why |
|---|---|---|---|
| D99 | **The real Test B brief runs 12:00–17:00**, so the day ends around sunset in late October and November, and the river, sunset and evening-light cards can appear. **"Plan 1 / Plan 2" is kept for the real Test B** (confirms m56). The dry run stays at 10:00–15:00, as shared | D97's 10:00–15:00 (now the dry run only) | Founder decision |

**Checked with the new window (28 Sep):**
- **The 30-minute end rule holds.** The two made-up people were run on a Saturday, a Sunday and a Wednesday from Charing Cross, against the example generic plan (ends 16:30). Personal plans ended at 16:00–16:57, so all six pairs were within 30 min.
- **Sunset (sunrise-sunset.org, central London):** 17:51 on 24 Oct; the clocks go back on 25 Oct; 16:47 on 26 Oct, 16:24 on 8 Nov. A 17:00 end is 15–35 min after sunset from 26 Oct, but about an hour before it on 24 Oct.
- **31 of the 35 ready cards fit the day.** They include both river routes, Alderman Stairs and Waterloo Bridge at sunset.
- **Four evening-only cards can't fit:** Soho and Chinatown after dark (from 17:30), evensong (17:00), the steak dinner (from 18:00) and the night boat (from 18:30).
- **Neither made-up person got a river or sunset card.** P01's plan ends on the Greenwich hill in the late-afternoon light, which scores higher, and Somerset House is the next strongest card left out. P02's weights don't favour views. Whether they appear depends on the person, which is the point.

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m62 | **The example generic plan is reordered for 12:00–17:00** so it ends on the South Bank at sunset: Trafalgar Square → St James's Park → Big Ben → the South Bank to the London Eye (12:10–16:30). A good generic day would use the sunset too, so the personal plan doesn't win on timing alone. Each stop has a `best` line, as the personal plan does. Abram still writes the real one (0.5 h, week of 19 Oct) | `brain/data/testb/generic.example.yaml` |
| m63 | **Sunset GUESSES on four cards are replaced by checked times** (Waterloo Bridge, Alderman Stairs, St Dunstan, the night boat). No window changed | 4 cards; `research/sources.csv` |
| m64 | **The review's "strong moments left out" lists only cards that fit the day's hours**, so an evening card no longer appears as "left out" of a 17:00 day | `brain/src/brain/testb.py`, `planner.py` (`fits_day`) |



| # | Decision | Replaces | Why |
|---|---|---|---|
| D97 | **Test B dry run:**<br>- **Both briefs run 10:00–15:00.**<br>- **The two plans in a pair end within 30 min of each other.**<br>- **The aspiration starting weight drops to +0.25** (was +0.5).<br>- **Plans are labelled "Plan 1" and "Plan 2"**, not A and B, and which one is personal is randomised per person.<br>- **The regenerated plans can go to a few friends. Their feedback is for catching problems only, not test data:** it is never entered in the results sheet | 10:00–18:00 briefs; the +0.5 prior (a GUESS); A/B labels | Founder decisions on m54's two questions. The personal plans finished hours before the generic one, which could give them away, and the aspiration prior topped every stop's reasons |
| D98 | **Friends' moments become cards where they fit.** Claude verifies the facts and marks complete cards ready (research rule, D91). No names are stored.<br>- **Ready:** the Greenwich Peninsula walk; Soho and Chinatown after dark (the evening version of card 8); two routes from the Strand to the river (Villiers Street; Somerset House); Tower Bridge at sunset from Alderman Stairs.<br>- **Notes added** to the Olympic Park break and card 11 (Richmond: time slows down; best in late spring).<br>- **Winter Wonderland stays a draft:** it runs 19 Nov – 3 Jan, after Test B.<br>- **Not cards:** the Tower of London dance event (one-off) and the Trocadero dance spot (closed).<br>- **Parked (D75):** stillness amid busyness (#16) and community hubs (#17).<br>- **Founder briefing:** friends described transitions, slow against fast, and evening lights unprompted; early qualitative support only | — | Founder request. Mapping: `research/seed-moments/05-friends-batch.md` |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m55 | **How the end rule works:** the personal plan is planned to finish by the generic end + 30 min, then its stops move later inside their windows until it ends no earlier than the generic end − 30 min. A constraint inside the solver was tried and dropped: it stopped the solver finding a first route, and it could be met by idling after the last stop. If the rule can't be met, the status says "fix by hand". Dry run: P01 ends 14:00 against 14:30; P02 14:36 against 14:30 | `brain/src/brain/planner.py` (`spread_to_end`), `testb.py` |
| m56 | **Numbering is an option (`--numbered`), mapping the sheet's A → 1 and B → 2,** so the balanced, seeded split stays. The README's command uses it, so real Test B plans are numbered too, and the script asks "Plan 1 or Plan 2", which keeps them apart from Test A's A/B choices. The generic plan now needs `depart` times, because they set the pair's end | `brain/README.md`, `validation/interview-script.md`, `generic.example.yaml` |
| m57 | **The dry run's generic plan is a copy of the example with its first leg from London Bridge, and a "best" line on each stop**, so both plans in a pair look alike | `validation/testb-dry-run/for-abram/generic.used.yaml` |
| m58 | **Plan text fixes:**<br>- after a walk from the previous stop, the arrival line drops the card's station ("From Monument or Tower Hill station" right after "20 min on foot from St Paul's" read as a contradiction);<br>- every arrival line ends with a full stop (the generic plan's did, which could give the personal plan away);<br>- "A late bagel on Brick Lane" is renamed "A salt beef bagel on Brick Lane";<br>- Borough Market's arrival line is reworded | `testb.py`, two cards |
| m59 | **Variant groups:** the two river routes share `to_the_river`; Soho by day (card 8) and Soho and Chinatown after dark share `soho_wander`. A plan holds one of each | 4 cards |
| m60 | **Alderman Stairs:** the card keeps you on the raised terrace beside the stairs, never on the tidal foreshore. Coordinates are the E1W 1UE postcode centroid, because OpenStreetMap was blocked from here | `m_alderman_stairs_sunset.yaml` |
| m61 | **The dry-run folder is split:** `share/` (the four plans and a one-line description of each made-up person) and `for-abram/` (reviews, the key, brief and generic). Give each friend one person's pair, because both people get the same generic plan | `validation/testb-dry-run/` |

## 2026-09-28 — government contract; Test B dry run prepared

| # | Decision | Replaces | Why |
|---|---|---|---|
| D96 | **The government contract is confirmed: it has no IP clause covering Abram's own projects.** **The conjoint keeps 10 tasks** | m50's assumption; m51 | Founder confirmation |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m53 | **Fixes to participant-facing plan text:**<br>- internal notes ("(GUESS)", "(CHECKED…)") are stripped;<br>- "from X" names the place you left: cards can carry `experience.end_name` (e.g. "Westminster Pier");<br>- the arrival line doesn't repeat "From …" | `brain/src/brain/testb.py`, `moments.py`, 8 cards |
| m54 | **The Test B dry run is prepared** from two made-up people (not participants), so Abram's hour is reading, not setting up. It raised two questions for him: plans that finish early, and the strength of the aspiration prior | `validation/testb-dry-run/` |

## 2026-09-28 — employment checks; the weather factor

| # | Decision | Replaces | Why |
|---|---|---|---|
| D94 | **Employment and Apple checks:**<br>- **Government job: done.** It is in Uzbekistan and doesn't conflict. The gate asked for written approval; it is recorded as done on Abram's confirmation.<br>- **Apple outside-activities policy:** Abram expects it to be fine and is double-checking.<br>- **Apple Developer auto-renew is off** (D74 done) | The pending gate items (D33, D38, D60) | Founder confirmation |
| D95 | **Conjoint:** "hot hour outside: yes / no" is replaced by **"weather at the outdoor stops: mild and dry / cold but dry / rainy"**; the other 5 factors stay.<br>**The design is regenerated:** Bayesian D-error 0.852 for 8 parameters. It is within 0.5% of a 20-start search, level-balanced, and every weather pair appears.<br>**The levels map onto the model:** cold × outdoors (`cold_outdoor`, new) and rain × outdoors (`rain_outdoor`, now personal). Mild and dry is the baseline.<br>**Updated:** Test A materials, the Brain's copy of the design, the screens scope and page | D30's heat factor | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m47 | **"Cold" is 8°C or below** in the model (GUESS). If a participant asks, the interviewer says mild ≈ 15°C, cold ≈ 5°C, rainy = showers on and off | `brain/src/brain/features.py`, `validation/interview-script.md`, `conjoint/README.md` |
| m48 | **Priors (GUESS):**<br>- `cold_outdoor` is new: mean −0.5, personal sd 0.75;<br>- `rain_outdoor` becomes personal: mean −1.0, sd 0.75, because the conjoint now identifies it;<br>- `hot_outdoor` keeps its prior and learns from stop ratings;<br>- design priors: cold −0.5, rain −1.0 | `brain/data/priors.yaml`, `make_design.py` |
| m49 | **The read-back marks weights that come mostly from the prior.** Rain's prior (−1.0, sd 0.75) already reads as a clear dislike, so any line whose sd has barely moved from the prior says "(mostly the population prior, not their answers)" | `brain/src/brain/testb.py` |
| m50 | **The government contract's IP clause is counted as done** with the job check. The Apple contract's IP clause goes with the Apple double-check. Say if you meant only the secondary-employment item | `CLAUDE.md` |
| m51 | **10 tasks are kept.** 12 tasks would lower the D-error by 19% for about 1 minute more per participant; that's offered, not applied | `validation/conjoint/README.md` |
| m52 | The published screens page shows the new weather attribute (D84) | https://claude.ai/artifact/CqRgaT1e328Qm4H2cX3W91 |

## 2026-09-27 — cards 9–11; park break; two more cards

| # | Decision | Replaces | Why |
|---|---|---|---|
| D93 | **Research cards: no flags. Karting stays at K1 Speed Canary Wharf.**<br>**Card 9** is eating outside around Oxford Circus and Regent Street, at places like OshPaz or Angus Steakhouse. What made it good: sitting outside, watching the street, good food.<br>**Card 10 is a flexible park break** that picks the park nearest the rest of the day's plan, from Abram's list: Kyoto Garden, Regent's, Hyde, Battersea and the Olympic Park.<br>**Card 11** runs from Richmond Gate to King Henry's Mound.<br>**Add King's Cross canal steps and Coal Drops Yard, and a park bike loop** | the draft cards 9–11 | Founder answers (D91) |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m44 | **How the park break works:**<br>- six park cards share one variant group, so a plan holds at most one;<br>- they carry identical tags ("all parks feel roughly the same"), so the route decides which one;<br>- they are `kind: moment`, so a park break can sit alongside an area vibe;<br>- the window is 10:00–16:00 (daylight in the Test B weeks).<br>St James's Park is Claude's addition to the list.<br>*Dry run:* with only parks to choose from, a Stratford start picks the Olympic Park; in a full day heading into the centre, it picks Regent's Park on the way | `brain/data/moments/m_park_break_*.yaml` |
| m45 | **Card 9 is renamed** `a_west_end_outdoor_dining`:<br>- OshPaz's restaurant is at 7 Regent Street, at the Piccadilly end, not by Oxford Circus (official site);<br>- Angus Steakhouse Oxford Circus has a heated terrace;<br>- the cost is £45, TheFork's average there | `a_west_end_outdoor_dining.yaml` |
| m46 | **The bike loop is in Hyde Park,** on the routes where the Royal Parks allow cycling (Serpentine Road, the Broad Walk). It uses a £3 Santander day pass. The 14+ age rule is from search results; TfL's own page refused our fetch | `m_park_bike_loop_hyde.yaml` |

## 2026-09-27 — how cards get checked from now on; type mix

| # | Decision | Replaces | Why |
|---|---|---|---|
| D91 | **The card rule from now on:**<br>(1) **Research-sourced cards:** Claude verifies the facts from official sources and marks each card ready once it is complete. Abram gets **one list** with a one-line summary each and flags any he disagrees with.<br>(2) **Abram's own cards (9–11):** Claude asks only what only he can know (route, feeling), in one batched message for all three, and fills everything else with its best checked guess | D72's "Abram checks each card"; the one-at-a-time walkthrough | Founder decision; it saves about 50 min of card checks |
| D92 | **Check that the ready cards cover a mix of experience types**, and say if one is missing for Test B. **Add the moment-engine notes** (a finder per type; new types: quiet and rest, social, learning by doing, music and nightlife, seasonal events) to `decisions/after-9-nov.md` (#15) | — | Founder request |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m40 | **Corrected the go-karting card.** TeamSport's Tower Bridge track closed in 2018; its replacement (Docklands) is in Charlton, a 30-min walk from the nearest stations. The card now uses **K1 Speed Canary Wharf** (central; official prices and hours) as `m_go_karting_canary_wharf` | `brain/data/moments/`, `03-candidates.md` |
| m41 | Official-source changes to the research cards:<br>- the Garden at 120's planting (wisteria, roses, hydrangeas; no fruit trees on the official page);<br>- Beigel Bake at £7.50 (the salt beef beigel);<br>- Horizon 22 needs a booked slot;<br>- the Bank of England Museum is closed Fri 2 Oct and from 15:00 Fri 27 Nov;<br>- evensong is "most days" | the cards |
| m42 | Cards 10–11 are filled with checked facts. St James's Park: gates 05:00–midnight. Richmond: Pembroke Lodge 09:00–17:30; the deer rut runs late Sept–early Nov, so keep at least 50 m away. Their windows now end in daylight for the Test B weeks | `a_st_james_park.yaml`, `m_richmond_park_view.yaml` |
| m43 | Two tests now follow the data (how many field cards are ready), not a fixed count | `brain/tests/test_aspiration.py` |

## 2026-09-27 — 12 research cards drafted; card 5

| # | Decision | Replaces | Why |
|---|---|---|---|
| D90 | **Draft 12 of the researched candidates as cards:** 1, 2, 4, 6, 7, 8, 9, 11, 12, 14, 16 and 19. They are drafts (`source: research`) until Abram checks them. **Card 5 is Meet Bros, Paddington, at about £60 a head**, and is ready | — | Founder decision; he invited changes to the list |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m34 | Card 5 is retitled "Steak dinner in a buzzing room at Meet Bros" and no longer promises chef-watching, because the open kitchen is unconfirmed. A Test B plan shouldn't promise what may not be there | `m_open_kitchen_steakhouse.yaml` |
| m35 | **Swapped 13 (Parliament Hill) for 9 (evensong at St Paul's).** *Abram left the choice to Claude (27 Sep): evensong stays.* It's dark by about 16:30 in the Test B weeks, and few cards work after dark. Evensong is free, adds awe and absorption, and pairs with the Millennium Bridge (7). Parliament Hill would have been a third skyline view, far from the other clusters; 11 and 14 already give skylines | `research/seed-moments/03-candidates.md` |
| m36 | **Built the day-of-week part of after-9-nov #7**, because weekday-only places (the Bank of England Museum, Horizon 22) would otherwise land in weekend plans. A card can list `best_time.days`, a Test B brief can set `weekday`, and the API uses the plan's date. Different hours on different days stay parked | `brain/src/brain/moments.py`, `testb.py`, `api.py` |
| m37 | Coordinates come from Wikipedia's geodata and postcodes.io postcode centroids, because OpenStreetMap's servers refused requests from here. Each card says which one it used | the 13 cards |
| m38 | The three finance & tech picks (1, 2, 14) are listed by id in `aspiration.yaml`. Food and nature picks map through their tags as before | `brain/data/aspiration.yaml` |
| m39 | Card 6's window moves from 08:00–19:00 to **10:00–18:00**, so the Crossrail Place Roof Garden at the end is open (its winter hours). The weekday rush hours before 10:00 are lost; the lunchtime and 17:00 crowds remain | `m_canary_wharf_towers.yaml` |

## 2026-09-27 — value in pounds; moment candidates; card 4

| # | Decision | Replaces | Why |
|---|---|---|---|
| D88 | **No raw S ÷ cost ratio. The app shows "worth about £V to you"**, where V = the non-cost part of S ÷ the person's cost weight (per £). Ranking is by V − price, which is the same as ranking by S, so the planner doesn't change. **The person's cost weight is constrained to stay negative:** it is fitted on a log scale. **CLAUDE.md is updated now**, not at Checkpoint 3 | CLAUDE.md's "feeling per pound = predicted S ÷ cost"; m29 | Founder decision |
| D89 | **A research pass for ~30 candidate London moments beyond the current cards**, from open sources read for ideas only (never scraped or copied), written in Claude's own words and ranked by fit with the Test B brief. Abram picks which to draft as cards | — | Founder request |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m31 | **The constraint is built now, because it protects the Test B plans:** a participant whose cost weight crossed zero would get plans that favour the dearest stops.<br>- In the model, β_cost = −0.25 · e^δ, with δ ~ N(0, 0.8²) (GUESS, matched to the old prior's negative range).<br>- Each step uses the full Hessian when it's negative definite, otherwise Gauss-Newton.<br>- The read-back says cost matters "more" or "less" to someone than to most people, never whether they like it.<br>- 62 tests pass | `brain/src/brain/personal.py`, `population.py`, `scoring.py` (`value_gbp`), `testb.py`, `data/priors.yaml` |
| m33 | The candidate list (`research/seed-moments/03-candidates.md`) has 34 moments in three tiers. Picking from it can stand in for most of blocker #2 (sending ~14 names, 1.0 h), at about 0.25 h. Cards drafted from it get `source: research`, with the link | `LOG.md` |
| m32 | **V isn't shown in the Test B plans.** Test B plans never say why a stop was chosen (they stay blind), so V waits for the v0 moment card | — |

## 2026-09-27 — trip cost layer parked; card 3

| # | Decision | Replaces | Why |
|---|---|---|---|
| D87 | **The trip cost layer goes on `decisions/after-9-nov.md` (#14)**, in three stages: (1) total cost per day plan and a feeling-per-pound ranking; (2) multi-city trips that always link out to the provider's checkout, with no in-app booking (because of the April 2027 package-travel change); (3) price-timing alerts. The API and price-prediction research comes first.<br>**No work before 9 Nov except a short note on whether Stage 1 fits v0.** The note is written (`decisions/trip-cost-stage-1.md`): a thin Stage 1 fits for about 1.5 h, and it's decided at Checkpoint 3 | — | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m29 | The Stage 1 note suggests showing a money-metric "worth about £V to you" in place of a raw S ÷ cost ratio, because the ratio depends on utility's arbitrary origin. **This amends CLAUDE.md's "feeling per pound = S ÷ cost" only if you agree at Checkpoint 3**, so it's listed there, not applied | `decisions/trip-cost-stage-1.md` |
| m30 | The note is read at Checkpoint 3 (about 10 min), inside the checkpoint's time | `LOG.md` |

## 2026-09-27 — Test E postponed until v0 exists

| # | Decision | Replaces | Why |
|---|---|---|---|
| D86 | **Test E is postponed until v0 exists.** It runs with a working demo after Test B, and before any B2B-specific build work. The B2B-vs-consumer decision note (D40) moves with it; the pass bar (D57) is kept.<br>**Until then, "businesses will pay" is an explicit, untested assumption. It is the main revenue risk:** the model's main money line (business clients, D37, `Path50k`) rests on it, and no business has been asked. The founder briefing says so (§6–7).<br>**The 6.25 h freed (recruiting 1.25, interviews 3.75, Uzbek script check 0.25, decision note 1.0) go to moment cards (2.25) and Test B (4.0).**<br>**The desk research stays as a light task after 9 Nov** (`decisions/after-9-nov.md` #13): companies selling itinerary or guest tools to hotels and agencies, and their prices; what hotels offer guests today; how many Uzbek agencies send clients to London | D36 (Test E first), D40's timing, D82's Test E recruiting slot, D84's Test E interviews | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m25 | **How the 6.25 h are split:**<br>- **1.25 h:** checking Claude's cards for the moments friends send. This takes Test E recruiting's place as #4 in the extra-hours list (26 Sep – 1 Oct).<br>- **Week of 28 Sep, 1.5 h:** a **Test B dry run** (1.0: read one generic and one personalised plan made from made-up answers, as a participant would get them) and moment cards (0.5).<br>- **Week of 12 Oct, 3.5 h:** the landing page and first recruitment posts (3.0) **start a week early**, and moment cards get +0.5.<br>- **Week of 19 Oct, 3.0 h:** the hours the move frees become a **Test B buffer**, for a second recruitment round if fewer than 12 strangers sign up. They're spent only if needed.<br>Phase 3 stays at ≈ 28.25 h | `LOG.md`, `validation/README.md` |
| m26 | The Area 20 review (Uzbek B2B payments, 0.25 h) moves with Test E, since nothing before it uses the note | `LOG.md` |
| m27 | The Test E guide, kit and published kit page are marked postponed. Before Test E runs, Claude adds a short demo section at the close of the call guide | `validation/`, https://claude.ai/artifact/LZQEYVFmjWUXXpVMLx7qu8 |
| m28 | A reminder is set to download both swipe CSVs before the free database expires (Wed 21 Oct; the database expires about 26 Oct). The final copy goes on your own device, or in `validation/raw/` (git-ignored), never in the repo | `LOG.md` |

## 2026-09-27 — swipe candidates

| # | Decision | Replaces | Why |
|---|---|---|---|
| D85 | **Swipe candidates:** out go Oxford Street shopping, and Piccadilly Circus and Leicester Square. In come **go-karting** and **Canary Wharf among the towers**. Still 30 places (`brain/data/calibration/places.yaml`; the two new entries have Claude's draft tags) | The 14 added candidates (D70c) | Founder decision at Render step 1 |

## 2026-09-27 — art & design, the week of 28 Sep, published pages

| # | Decision | Replaces | Why |
|---|---|---|---|
| D83 | **Art & design is dropped from the Test B question** and parked on `decisions/after-9-nov.md`. The question now offers finance & tech, food, history & culture, nature, none. The mapping, tests and the results-sheet note are updated (4,100 formulas recalculated, 0 errors, no cell changed) | D77's art & design option | Founder decision; it had no moments |
| D84 | **Week of 28 Sep:** the first 2 Test E interviews go there if contacts reply (otherwise the week of 5 Oct). **The Areas 5–7 review (3 h) is parked after 9 Nov.** The remaining ~5 h is kept as buffer.<br>**Keeping published pages in sync with decisions is a minor decision** under D69, so Claude does it without asking | The week of 28 Sep and 5 Oct plan (D80, D82) | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m22 | The aspiration question check drops from 0.5 to 0.25 h, since there's no art & design choice left | `LOG.md` |
| m23 | The published screens page is updated to D81 (who designs, 4 custom screens, native elsewhere, timing) | https://claude.ai/artifact/CqRgaT1e328Qm4H2cX3W91 |
| m24 | `decisions/v0-ios-plan.md` now points to `LOG.md` for the week-by-week schedule | `decisions/v0-ios-plan.md` |

## 2026-09-26 (evening, later) — Abram designs v0; extra hours on the blockers

| # | Decision | Replaces | Why |
|---|---|---|---|
| D81 | **Abram designs v0 himself in Claude Design, after Test B.** The external designer is optional.<br>Design covers **4 custom screens**: welcome, moment card, shot card, day plan. **Everything else uses native SwiftUI components.**<br>That is 7 h of Abram's design in place of the designer's 3 h, so the Face goes from 34 to 38 h and Phase 4 from 53 to 57 h (`design/v0-screens.md`).<br>**Part A no longer gates design work.** It applies only to the backup helper and any future contributor | D65 (the designer starts now), the designer brief in the week of 28 Sep | Founder decision |
| D82 | **Extra hours over the next few days (26 Sep – 1 Oct) go on the blockers, in this order:** card review, moment names, swipe page, Test E recruiting, Apple/IP checks (6.25 h, outside the weekly budget).<br>**Actual hours are logged in `LOG.md` as Abram reports them**; this is working rule 10 in `CLAUDE.md` | — | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m19 | Design hours are split as a GUESS of 1.5 h per custom screen plus 1 h for type, colour and hand-off. The welcome screen comes first (Build 1, week of 16 Nov), then the other three (weeks of 23–30 Nov) | `design/v0-screens.md`, `LOG.md` |
| m20 | Added a starting design direction for the four screens (field guide tone, one display face for titles, one route accent, one reveal animation), from the frontend-design skill. It's for Abram to change in Claude Design | `design/v0-screens.md` |
| m21 | The Apple membership check (0.25 h) goes in the same block as the Apple/IP checks | `LOG.md` |

**For Abram:**
1. **The build now fills the week of 28 Dec**, so Phase 5 starts about 4 Jan instead of late December. It's still January, and no checkpoint date moves.
2. **The week of 28 Sep has 6.5 h of room**, because the blockers moved into the extra hours. Suggestion: the Areas 5–7 review (3 h), and the first Test E interviews if contacts reply.
3. **Art & design (D77) is still open.**

## 2026-09-26 (status report) — Areas 1–3 review deferred

| # | Decision | Replaces | Why |
|---|---|---|---|
| D80 | **The Areas 1–3 review (5 h) is deferred to after 9 Nov** and goes on `decisions/after-9-nov.md`. This makes room for the card review and Test E | The week of 28 Sep (D17, D48) | Founder decision. Until then, Test B relies on the card review (tags) and the Brain code review in the week of 26 Oct (scoring) |
| — | **Art & design (D77) is still open.** The message had both options in brackets ("add Tate Modern Turbine Hall + one more / drop it") | — | Awaiting Abram's choice; needed before Test A (19 Oct) |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m18 | Using the room D80 frees for Test E:<br>- Test E recruiting (1.25 h) moves from the week of 5 Oct to 28 Sep;<br>- the first 2 interviews (1.5 h) move from the week of 12 Oct to 5 Oct.<br>Weeks now: 28 Sep 6.75 h, 5 Oct 6.75 h, 12 Oct 6.5 h | `LOG.md` |

## 2026-09-26 (late) — aspiration match for Test B, British Museum card, this week's actions

| # | Decision | Replaces | Why |
|---|---|---|---|
| D77 | **Aspiration match is in Test B**, limited to fields with moments.<br>**One optional Test A question (5.7)** with a fixed list: finance & tech, food, history & culture, nature, art & design, none of these.<br>Each field maps to **existing tags** where one fits: food ≥ 2, history & culture ≥ 2, green/nature ≥ 2. Finance & tech and art & design have no such tag, so their moments are **listed by id** (`brain/data/aspiration.yaml`).<br>Model feature `aspiration_match`: prior +0.5 (GUESS), personal δ sd 0.5. Swipes can move it.<br>The answer goes in the results sheet, Participants **column AG**.<br>**Any field with fewer than 2 ready moments is flagged** (`python -m brain.testb fields`, and a warning in `plans`) | On the after-9-Nov list (D75) | Founder decision; `decisions/new-moment-features.md` |
| D78 | **British Museum card redrafted as Room 4 (Egyptian sculpture) → Great Court → Room 1, the Enlightenment Gallery** (the former King's Library). Abram confirms at review | The Great Court alone (the Reading Room is closed) | Founder request; route checked (map, Wikipedia, search) |
| D79 | **This week Abram:** reviews the 11 cards, checks the Apple membership (auto-renew off), and signs Part A with the designer | — | Founder plan |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m14 | A field matches a tag only at level **2** (the defining trait). At ≥ 1, "history" would match almost every card | `brain/data/aspiration.yaml` |
| m15 | The answer goes in a new **column AG**, after the formula block. Inserting it earlier would break the existing formulas. The sheet was recalculated: 4,100 formulas, 0 errors | `validation/results-sheet.xlsx` |
| m16 | The aspiration weight stays **out of the generic read-back**, because its prior alone reads as "confident". The read-back quotes the person's own answer instead | `brain/src/brain/testb.py` |
| m17 | The question asks about **interests, never a job or employer**. It's optional, and "none" is an answer | `validation/interview-script.md` 5.7 |

**For Abram:**
1. **Art & design has no moments.** Before Test A (week of 19 Oct), add 2 art & design cards (e.g. the Tate Modern Turbine Hall, already on the swipe list) or drop the option from the question.
2. **The week of 28 Sep is now 10.5 h** with the card review. Suggestion: move 2 h of the Areas 1–3 review to the week of 5 Oct, making both weeks 8.5 h. It's a move over 1 h, so it's your call.

## 2026-09-26 (night) — seed moments batch 1, agreement split, Apple renewal, after-9-Nov rule

| # | Decision | Replaces | Why |
|---|---|---|---|
| D72 | **Seed moments batch 1 (11) are drafted as cards**, with gaps flagged (`research/seed-moments/02-batch-1.md`). Three new ideas go in now because the cards need them for Test B: **entry types** (moment vs area vibe; one area a day, never the peak), **variants** (day/night; at most one per plan) and **route direction**. **Draft cards never go into real plans**: Test B and the API use only `status: ready` | — | Founder request. The rest of the new features wait (D75); `decisions/new-moment-features.md` |
| D73 | **The contributors agreement is split.** (a) **Part A**, IP assignment, confidentiality and the personal-data clause, is **signed now, as a deed**. (b) **Part B**, the equity terms, gets a solicitor review before incorporation. **No fixed hours:** contributions are voluntary and flexible (`legal/contributor-deed-part-a.md`, `legal/contributor-equity-terms-part-b-draft.md`) | D70d's single agreement | Founder decision. It's a deed because Part A gives nothing in return (see its notes) |
| D74 | **Apple Developer membership:** Abram checks its status. **Renew only if Test B passes.** The GitHub secrets (0.75 h) need an active membership, so if it has lapsed they move after Test B. **Auto-renew must be off**: Apple charges the card on the expiry date when it's on (Apple help, 2026-09-26) | D70e's timing for the secrets | Founder decision (money) |
| D75 | **New rule:** any new idea that doesn't help Test B goes on `decisions/after-9-nov.md` instead of into the current plan. Added to `CLAUDE.md` as working rule 9 | — | Founder decision |
| D76 | **The swipe page's privacy note is approved.** Abram deploys on Render with **no payment method** and shares the link | For Abram item 1 (D69–D71) | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m9 | The night river card ends at **Westminster**, the only pier reached every evening (checked on the timetables). The day card runs to Battersea | `m_uber_boat_west_night.yaml` |
| m10 | The two tower walks (Canary Wharf, City) share a variant group: at most one per plan | the two cards |
| m11 | "Any London park" is drafted as **St James's Park** (pelicans, checked); Richmond's viewpoint as **King Henry's Mound** (checked). Both are for Abram to confirm | the two cards |
| m12 | Coordinates come from OpenStreetMap (Nominatim), one request a second. Two are approximate points near the stations (Canary Wharf, Bank) | cards; `research/sources.csv` |
| m13 | `--include-drafts` gives a dry run with draft cards; the output says "DRY RUN" | `brain/src/brain/testb.py` |

**For Abram (scope):** **aspiration match** is the one new weight that could help Test B. It needs one optional Test A question (≈ 0.5 h of your time). Yes, or on the after-9-Nov list? (`decisions/new-moment-features.md`)

## 2026-09-26 (evening) — standing rule, Test E kit, swipe page, agreement, iOS pipeline

| # | Decision | Replaces | Why |
|---|---|---|---|
| D69 | **Standing rule:** Claude makes minor decisions itself and logs them: wording, file layout, scheduling moves under 1 h, and tooling within the agreed stack. It stops only for decisions that **change scope, cost money, affect privacy or safety, or move a checkpoint**. Everything else is batched into one list at each checkpoint (below) | Asking about each minor choice | Founder decision; added to `CLAUDE.md` as working rule 8 |
| D70a | **WhatsApp Business second number is ready.** Abram shares it when needed | Set-up pending | Founder update |
| D70b | **Test E comes in two shareable forms:** a 30-min call guide, and a two-message version agencies answer in writing (English, Russian, Uzbek). **Hotel staff contacts are asked to introduce Abram to a manager or budget holder** (`validation/test-e-kit.md`, published with copy buttons) | The script only | Founder request. The description stays in message 2, so nothing is pitched before the questions |
| D70c | **An anonymous swipe page calibrates the 16 places:** ~30 candidates; Loved it / It was fine / Didn't enjoy it / Haven't been. There is no login and no personal questions, and no IP address is stored, only a random browser ID. **The 16 are picked by familiarity × divisiveness** (`brain/src/brain/calibration.py`) | Abram choosing the 16 by judgement (D30, D48) | Founder request. Onboarding needs places that split people (CLAUDE.md) |
| D70d | **Contributors agreement drafted:** role, IP assigned to the company (via Abram until it's incorporated), a **~10% equity placeholder with 4-year vesting and a 1-year cliff, granted once the company is incorporated** (`legal/contributors-agreement-draft.md`) | Agreement pending (D38) | Founder request. It must be signed before anyone else contributes work |
| D70e | **The GitHub Actions iOS pipeline starts now** (`.github/workflows/ios.yml`, a placeholder `app/`). Abram adds the secrets. **The app's feature code still waits until Test B reports** | D65's hold on the workflow | Founder request |
| D71 | **The Areas 8–12 review stays deferred to after Checkpoint 3** (approved). **Moment names arrive as they come**, not only in the week of 5 Oct; Claude drafts each card on arrival | Open questions 1 and 2 | Founder decision |

**Minor decisions made by Claude under D69 (for the checkpoint list):**

| # | What | Where |
|---|---|---|
| m1 | The swipe page runs as a small separate app on **Render's free tier** (a free web service plus free Postgres in Frankfurt, £0), deployed from `render.yaml`. The Artifact database can't take answers from anonymous public visitors (it is organisation-internal only) | `render.yaml`, `brain/README.md` |
| m2 | **30 candidates:** the draft 16, plus London Eye, Tower of London, Covent Garden, Buckingham Palace, Oxford Street, Piccadilly/Leicester Square, Kew, Richmond Park, Portobello Road, St Paul's, South Bank walk, Platform 9¾, Madame Tussauds and Westfield. All tags are DRAFT | `brain/data/calibration/places.yaml` |
| m3 | **Ranking rule:** only people with ≥ 10 answers count; places with < 5 visitors rank last; the results page warns when a taste tag appears in fewer than 2 of the 16 | `calibration.py` |
| m4 | **Page details:** the day is stored, not the time; one-tap deletion; no cookies, analytics or third-party fonts; `noindex`; the contact email is set at deploy | `data/calibration/index.html` |
| m5 | Test E message version: two messages. Claude's Russian and Uzbek translations, to be checked (0.25 h, already budgeted) | `validation/test-e-kit.md` |
| m6 | Agreement: IP goes to Abram, who holds it for the company until incorporation; one week's notice; the bad-leaver terms are left to the solicitor | `legal/contributors-agreement-draft.md` |
| m7 | **iOS pipeline:** XcodeGen (no committed project file); target "Face", display name "Planner" (placeholder); iOS 17+, iPhone only; the `macos-26` runner; team, bundle ID and profile read from the profile; a throwaway keychain password; simulator-only builds until the secrets exist; uploads only from `main` or a manual run | `app/`, `.github/workflows/ios.yml` |
| m8 | **Schedule moves:** swipe page deploy and share in the week of 28 Sep (0.75 h); pick the 16 in the week of 12 Oct (0.5 h, after two weeks of answers); "confirm the 16 places" shrinks to checking the candidates (1.0 → 0.5 h); secrets and the App Store Connect record move from the week of 9 Nov to the week of 26 Oct (0.75 h). **Net +0.75 h on the phase totals** (≈ 115.25 h in the window, 15.4 weeks), plus 0.25 h for this decision round | `LOG.md` |

**For Abram (money or privacy; not decided by Claude):**
1. **Privacy: read the swipe page's privacy note before sharing the link.** It is live only once you deploy it.
   - It keeps a random ID in the browser's local storage. Claude judges this to be "strictly necessary" under PECR (ICO guidance, 29 Apr 2026), because it only records the answers the visitor chose to give. This is Claude's judgement, not legal advice.
   - It deletes answers by 31 March 2027, the same date as the study data.
   - It says Render's own servers may keep technical logs, which our code can't switch off.
2. **Money: solicitor review of the agreement** before signing. The cost is UNVERIFIED.
3. **Money: the secrets need an active Apple Developer Program membership.** If you aren't enrolled yet, enrolling now pays the annual fee before Test B reports (it was planned for 9 Nov, and only if Test B passed). The simulator build runs without it.
4. **Legal gate:** the designer works now (D65), so the agreement must be signed before their work is used. If they've already started, sign now: clause 3 covers work already done.

## 2026-09-26 (after the founder briefing) — Test B first, WhatsApp, brain now

| # | Decision | Replaces | Why |
|---|---|---|---|
| D65 | **Build the Brain now, and use it to generate the Test B plans.** The designer starts now. **The iOS app code, including its GitHub Actions build, is held until Test B reports** | The app built in parallel (D63) | Test B is the premise; don't spend app hours before it |
| D66 | **Test A runs on WhatsApp Business with a separate number**, not Telegram. The materials are updated | Telegram for the hand-run tests | Founder decision |
| D67 | **The 1.3-week overrun is accepted** (≈ 114.5 h in the window) | Open question | Founder decision |
| D68 | **Test B runs first and as fast as possible after Test E.** Each person's Test A chat is followed by their two plans within 1–3 days, so Test B reports about the week of 2 Nov | Test B as a batch in the week of 26 Oct | The briefing's advice: Test B is the most informative test |

## 2026-09-26 (Phase 3 round 6) — iOS plan accepted, hand-run tests, build in the cloud

| # | Decision | Replaces | Why |
|---|---|---|---|
| D59 | **Accept the iOS v0 at 53.5 h with the proposed cuts** (`decisions/v0-ios-plan.md`): no AI support agent in v0 (a safety button instead), keyboard dictation, local notifications, no login, and "Directions" opens Apple Maps | Proposed (D54) | Founder decision |
| D60 | **Abram does the Apple outside-activities policy check and the IP/invention-clause check in both contracts this week**, before the first external TestFlight build | Proposed timing (D53) | Founder decision |
| D61 | **An individual developer account for TestFlight. Switch to a company account before the public App Store launch.** That means incorporation (online, "usually within 24 hours", £100), then a D-U-N-S number ("allow up to 5 business days"; email D&B after two weeks), then "up to 2 business days" for Apple to receive it (sources: gov.uk, Apple D-U-N-S page, 2026-09-26). **Start about 3 weeks before the planned App Store submission.** How to move the app to the company account is UNVERIFIED | Open question | Founder decision |
| D62 | **Voice in the app is keyboard dictation plus "Did you type or speak?"** No custom recorder | Open question | Founder decision |
| D63 | **Checkpoint 3 stays in the week of 9 Nov. Tests A–C run by hand**: Test A as a chat conversation, and the Test B/C plans sent as messages or PDFs. **The iOS app is built in parallel**, so the first external TestFlight build carries the lessons | Tests A–C through TestFlight (D50) | Keeps the evidence gate before most build hours |
| D64 | **iOS builds run on GitHub Actions** (Abram has shipped an iOS app this way; no personal Mac). A macOS runner builds, signs and uploads to TestFlight. Backend tests run on Linux. iOS builds trigger only on changes under the app folder. **Abram adds the signing certificate, provisioning profile and App Store Connect API key to GitHub Secrets.** No 30% buffer, but **+3 h for the slower build-and-check loop** without Xcode previews, so Phase 4 ≈ 56.5 h | "Built on a personal Mac" (D50, D51) | Founder decision |

## 2026-09-26 (Phase 3 round 5) — v0 becomes a native iOS app

| # | Decision | Replaces | Why |
|---|---|---|---|
| D50 | **v0 is a native iOS app (SwiftUI).** Testers get it through **TestFlight**, then the App Store once it passes. **The Telegram bot plan is replaced.** Phase 3 Tests A–C run through TestFlight; Tests D (web page) and E are unchanged. Plan, hours, proposed cuts and designer screens: `decisions/v0-ios-plan.md`, `design/v0-screens.md` | Telegram bot v0 (Areas 1, 8, 19); the "no code before Phase 3 passes" rule for Tests A–C | Founder decision |
| D51 | **Two parts.** The **Brain** is a FastAPI backend: moment database, scoring (hierarchical βs, with δ_person separate so it can move on-device later) and the OR-Tools planner. The **Face** is the SwiftUI app: self-serve onboarding (text first, voice optional), moment and shot cards, a day plan with map, one-tap ratings. **Building the Brain starts now, in parallel with Test E**, because it doesn't depend on test results. First draft in `brain/` (28 tests pass) | Phase 4 gated on Phase 3 for all build work | Founder decision |
| D52 | **Economics work is paused** unless a decision needs it. The workbook reviews (3 h) are deferred. The workbook's Telegram Stars base case is now stale; its Apple rows already cover an iOS app | — | Hours go to the build |
| D53 | **New gate before public App Store release:** check Apple's outside-activities policy for publishing under Abram's own developer account. Added to `CLAUDE.md`. *Proposed:* do the check before the first external TestFlight build too (open question) | — | Founder decision |
| D54 | **The 3 h overrun question is held** until Phase 4 is re-planned for iOS. The re-plan is now in `decisions/v0-ios-plan.md`: ≈ 106.5 h in the window, about 1.5 h over | LOG open question 1 | Founder decision |
| D55 | **Abram names the backup helper** for safety alerts. They sign the contributors agreement (D38) **before support goes live**. In the iOS plan that is the first external TestFlight build, when the Help & safety button goes live | Open question on who the helper is | Founder decision |
| D56 | **The Area 4 review moves to the week of 2 Nov** | Week of 28 Sep | Balances that week |
| D57 | **Test E pass bar confirmed:** ≥ 2 of 5 already spend money or staff time on this, **and** ≥ 2 of 5 give an introduction or agree to an unpaid pilot | Proposed read-out | Founder confirmed |
| D58 | **Uzbek payment route accepted** (Area 20): a GBP invoice from the UK company, paid by international card through Stripe or by SWIFT to the UK business account; an HMRC certificate of residence first; **one adviser call before the first Uzbek invoice** | Proposed route (D49) | Founder decision |

## 2026-09-26 (Phase 3 round 4) — Phase 4 trim, safety cover, gate confirmed, Uzbek focus

| # | Decision | Replaces | Why |
|---|---|---|---|
| D45 | **Content automation (≈5 h) moves to after v0.** Phase 4 keeps self-serve onboarding (3 h) and the AI support agent (6 h), so Phase 4 ≈ 47 h and the plan ≈ 108 h | Automation 3 in Phase 4 (D44) | Brings the plan back to about 14.4 weeks |
| D46 | **Safety alerts at the start: Abram handles them, with a response target of within a few hours. A named backup helper covers his working hours.** The helper signs the contributors agreement, including confidentiality, first (D38). The auto-reply gives 999 guidance and never promises a faster reply. Added to `CLAUDE.md` and Area 19 | "A human, promptly", same hour where possible (D44) | 7.5 h a week and a full-time job |
| D47 | **City-expansion thresholds confirmed:** ≥ 300 monthly active strangers, ≥ 30% asking for a second plan within 30 days, stranger K ≥ 0.3, all held for 3 consecutive months | Proposed thresholds (D42) | Founder confirmed |
| D48 | **The review of the conjoint attributes and swipe places moves to the week of 28 Sep** | Week of 21 Sep (D30) | That week was 2.5 h over |
| D49 | **Uzbekistan: focus on outbound agencies sending clients to London, at London prices.** Both Uzbek Test E interviews are with outbound agencies. Uzbek hotels and tour operators, and local PPP prices, are not pursued in year one. Payment route checked (Area 20): invoice from the UK company, paid by an Uzbek-issued international Visa or Mastercard through Stripe, or by SWIFT transfer to the UK business bank account. **No Stripe presence in Uzbekistan is needed** | Uzbek hotel or tour operator interview and local price scenarios (D36) | London prices are ~3× the local level, and the curation already exists |

## 2026-09-26 (Phase 3 round 3) — B2B first in Phase 3, team, automation, expansion

| # | Decision | Replaces | Why |
|---|---|---|---|
| D36 | **Test E runs first in Phase 3, all 5 interviews kept.** Two of the five are **Uzbek contacts**: travel agencies sending clients to London, and hotels or tour operators in Uzbekistan. Add local price scenarios | Test E in parallel (D34) | B2B is the likely primary line |
| D37 | **Year one: no paid group trips** (the unpaid weekend test stays). **Venues are a user benefit only**, not revenue. B2B account management is kept. **Path50k is rebuilt with B2B as the primary line** and the consumer app as the product engine, showing hours per £ for each line | Group-trip fee and venue commission lines (D34) | Hours: every £50k path was ~420–440 h a year over budget |
| D38 | **More gates.** IP/invention clauses checked in both employment contracts. Incorporation, the ICO fee and public liability + PI insurance before the first paid client or trip. **A written founders/contributors agreement** (roles, hours, equity or compensation, IP assignment to the company) before anyone contributes work | D33 gate list | Founder decision |
| D39 | **Guardrail: never hold trip money; Stripe Connect direct charges only.** Added to `CLAUDE.md` | Proposed in Area 18 | FCA commercial agent exclusion |
| D40 | **After Test E:** a short decision note, B2B-first vs consumer-first, with hours, revenue and interview evidence (`decisions/b2b-vs-consumer-first.md`) | — | Founder request |
| D41 | **Team capacity is one input: extra helper hours per week, default 0.** Helpers cost 1.5 h a week of founder coordination. The model shows which £50k paths become feasible, and the helper hours each path needs. The earlier "3 helpers" assumption is removed | — | Founder sets it |
| D42 | **City-expansion gate:** London must pass usage, return-rate and stranger-K thresholds before the next city. Curation hours per new city are estimated (`decisions/city-expansion-gate.md`) | — | Founder request |
| D43 | **Friends and family are a separate launch channel.** K and every Phase 3 threshold are measured on **strangers only** | Friends excluded from the study | Keeps the evidence clean while using the warm network |
| D44 | **Automation scenario, built in Phase 4:** (1) fully self-serve onboarding; (2) an AI support agent with escalation (technical and payment issues wait for Abram; safety issues and complaints always go to a human promptly; AI disclosed, with an option to reach a person); (3) content generated from moments and shot cards, auto-scheduled on our own channels, with community-group posting kept manual. Build hours are added to Phase 4 and the £50k paths are recomputed | — | Hours are the wall |

## 2026-09-26 (Phase 3 round 2) — Legal gates, prices, new revenue lines

| # | Decision | Replaces | Why |
|---|---|---|---|
| D30 | **Phase 3 Tests A–D at ≈ 17 h with 12 participants** accepted. Abram confirms the 6 conjoint attributes and 16 swipe places this week | 15 h budget | Checkpoint 2 open question |
| D31 | **Test D annual prices: about two months free in both arms.** Arm A £4.99/month or **£49.99/year**; arm B £9.99/month or **£99.99/year** | £59.99/year in both arms (D25) | £59.99 was no discount in arm A |
| D32 | **Jev vs Claude tagging benchmark runs after v0**, not in Phase 4 | Proposed +1.5 h in Phase 4 | Hours |
| D33 | **Legal gates:** right to run a business **cleared** (confirmed by Abram). Remaining before taking any money: (1) Apple's outside-activities policy check, with disclosure if required and work kept on personal time and devices; (2) written secondary-employment approval from the government agency employer. Revenue can start once both are done | `CLAUDE.md` gate list (employer permission, right to run a business, IP clauses) | Founder update |
| D34 | **Phase 3 additions:** (1) trip payments research: Package Travel Regulations, payment splitting without holding money, safety duties (Area 18); (2) a free-first scenario in the workbook; (3) new revenue lines modelled and tested: **venue partnerships** (group discounts + commission, off-peak) and **B2B** (hotels, tourism boards, employers buying moment plans) at £200–500/month per client; (4) **5 B2B discovery interviews** (Test E); (5) a £50k path scenario with B2B clients and K = 0.3 | — | Founder request |
| D35 | **Seed moment 1 received** ("From the tube to the museum"). It is the Test A example shot card; exit, route, best time and shot position are to be filled in on one walk | D13 (5 seed moments) | First seed |

## Checkpoint 2 approval — Phase 3 go, virality, pricing test, tools

| # | Decision | Replaces | Why |
|---|---|---|---|
| D23 | **Measure referral and virality in Phase 3:** invites sent per user, invitees who sign up, shares of shot-card photos, and a computed K-factor. Test C plans get a **"bring a friend"** option, and there is a **share prompt after shot-card moments**. The workbook gets a K-factor input and a scenario showing the K needed for £50k at the founder's hours | — | Checkpoint 2: acquisition, not cost, decides viability |
| D24 | **Payment method deferred.** Check Telegram's rules on linking out to an external checkout, and note the app-store fees for a future native app | Open question | Telegram's link-out rule was UNVERIFIED |
| D25 | **Test D prices:** £4.99 vs £9.99 a month (random arm), plus £59.99 a year in both arms. Payment is asked for after one free plan. **Waitlist only, no money taken** (D1 still holds) | "Two price points if traffic allows" | Checkpoint 2 upside scenario |
| D26 | **Meta ad test deferred** until the Test A and B results are in | Open question | Don't spend before the product is shown to work |
| D27 | **Accept +2 h in Phase 4** for the design hooks: keep δ_person separate from b_population, and store trip-intent answers with each plan (≈1 h each). Phase 4 ≈38 h | Phase 4 ≈36 h (D14) | Areas 15 and 17: design now, build later |
| D28 | **Evaluate God's Eye View** (Area 14) for pre-trip moment previews and shot-card view previews. Analysis (isovists) stays on OSM/Overture in Python. **No tracking or CCTV layers.** Post-v0 only | — | Founder request |
| D29 | **Benchmark Jev (TypeSafe AI) against Claude** on moment feature tagging (Areas 2 and 13): 50 moments hand-labelled by the founder; accuracy and calibration. If calibrated, auto-accept high-confidence tags and route low-confidence ones to the founder | — | Founder request |

## Checkpoint 1 approval — Phase 2 go, thresholds, food, sources, recruitment

| # | Decision | Replaces | Why |
|---|---|---|---|
| D18 | **Checkpoint 1 approved.** Keep the six proposed Phase 3 thresholds. **Report every Test A metric split by voice vs text** | Thresholds "proposed" | Area 1: voice break-off risk |
| D19 | **Food:** one optional question, "Any foods or drinks you avoid?", with a one-line consent note. **No allergy question in v0** | `CLAUDE.md` "food needs (halal, vegetarian, allergies)" | Area 12: allergies are health data; halal may reveal religion |
| D20 | **Re-verify pricing and cost sources now**, before the economics model. Re-verify the other search-only sources when each note is revised | Open question | Phase 2 depends on prices |
| D21 | **Separate recruitment posts** for Tests A–D and for the weekend test. Weekend-trip attendees are invited to do Test A afterwards | Open question | Keeps the weekend test clean while reusing its attendees |
| D22 | **After Phase 2, light-scan five new areas:** 13 moment mining from text + data rights; 14 spatial moment detection (isovists, scenicness, building data); 15 travel motivation + per-trip intent (β_trip = β_person + trip adjustment); 16 home-contrast novelty (home city only); 17 on-device personalisation (b_person = b_population + δ_person, federated learning, differential privacy). Design now, build after Phase 3 | — | Founder request |

## 2026-09-26 (third round) — Hours, peak–end, photos

| # | Decision | Replaces | Why |
|---|---|---|---|
| D14 | **Shot cards only for the ~20 swipe and peak moments.** Keep LLM-written explanations. **Accept a Phase 4 estimate of about 36 hours** | Shot cards for all 50 moments; 35-hour budget | Option (a) from LOG.md |
| D15 | **Peak–end end-of-day bonus is off by default.** The planner maximises the sum of predicted moment satisfaction, and our ratings will test whether the bonus should be switched on | D8 left the default open | Area 6: peak–end is weak for multi-part experiences (Kemp et al. 2008; Strijbosch et al. 2019) |
| D16 | **Photo pairs dropped from the model and from Test A.** Instead, Test A adds two 1–5 questions: "How much do photos and sharing matter on your trips?" and "Would a shot card make you more likely to visit this moment?" | Onboarding layer (a), camera taste | Area 5: 10 examples add only +0.006 ρ over a generic model |
| D17 | **Review schedule.** Abram reviews the 15 moment features in the week of 28 Sep. The Areas 5–7 review moves to the week of 5 Oct | LOG.md weekly plan | Keeps weekly hours near 7.5 |

## 2026-09-26 (second round) — Moments, Python, place database

| # | Decision | Replaces | Why |
|---|---|---|---|
| D9 | **The unit of the database is a moment, not a place.** A moment = place + route/approach + best time + features + shot card. The swipe layer, planner and per-stop ratings work on moments | "~100 hand-tagged places" (D5 kept the count at 50) | Founder example: the South Kensington tube exit to the Natural History Museum reveal is the experience, not the museum |
| D10 | **New moment features:** contrast/reveal, absorption/flow, awe, social pull. Cost stays a raw £ input, and feeling-per-pound is derived by the model | Area 2's 12-attribute list | Founder design change. Evidence in Area 6 (Kaplan's mystery, Csikszentmihalyi's flow, Keltner's awe) |
| D11 | **v0 moments are hand-picked by the founder**, with no Overture bulk pull and no second tagger | Area 2 "Overture pull" and "tag reliability" steps | Hours (Phase 4 was estimated at 37 of 35) |
| D12 | **Prototype pinned to Python 3.12** | — | PyMC 6 and Biogeme 3.3 require ≥3.12 |
| D13 | **Five seed moments** come from the founder's own experience this week | — | Real examples to calibrate the schema before tagging the rest |

## 2026-09-26 — Test design, audio, v0 scope

| # | Decision | Replaces | Why |
|---|---|---|---|
| D1 | **Test D:** waitlist and stated price only, **no money taken**. A priced "Reserve founding spot" button leads to the waitlist with an honest note. Test two price points if traffic allows | "Small refundable deposit" | `CLAUDE.md` legal gates: no charging before employer permission, right to run a business and IP clauses are cleared |
| D2 | **Test D pass threshold:** ≥20% of sign-ups pick the priced option | "Any paid deposits ≥3" | Follows from D1 |
| D3 | **Audio:** delete after transcription by default. Opt-in 30-day retention, used only for transcription-accuracy spot-checks | — | `CLAUDE.md` guardrail; Area 1 risk (ASR hallucination and accent bias need spot-checks) |
| D4 | **Test A:** answer mode (voice/text) is a recorded variable. Report the choice, completion and "felt understood" for each mode | — | Area 1: voice answers are 2× longer but break-off is 45% vs 13% (Gavras & Höhne 2020) and 51% vs 24% (Höhne et al. 2024) |
| D5 | **Phase 4 scope cut:** 50 places (not ~100) | "~100 hand-tagged places" | Hours: onboarding and planner alone were estimated at 22 of 35 |
| D6 | **Phase 4 scope cut:** no photo taste in v0 | "Photo taste: basic embedding similarity" | Same |
| D7 | **Phase 4 scope cut:** feedback is log-only. Weight updates run offline, not live | "Simple Bayesian update of the person's weights" | Same |
| D8 | **Peak–end** stays as a planner toggle, not a hard guarantee | "guaranteeing one peak and a good finish" | Area 4: the tourism evidence is mixed. Test it on our own ratings |

## Phase 3 thresholds (confirmed: D2, D18)

| Metric | Pass |
|---|---|
| Onboarding completion | ≥ 70% (reported overall and by mode) |
| "Felt understood" | median ≥ 4/5 (reported overall and by mode) |
| Prefer personalised plan (blind) | ≥ 7 of 10 |
| Used the plan on a real day | ≥ 40% |
| Asked for a second plan within 2 weeks | ≥ 30% |
| Landing page visit → sign-up | ≥ 10% |
| Sign-ups choosing the priced option | ≥ 20% (confirmed, D2) |

Descriptive Test A measures with no pass threshold (D16): "How much do photos and sharing matter on your trips?" (1–5), and "Would a shot card make you more likely to visit this moment?" (1–5).

Descriptive virality measures with no pass threshold (D23): invites sent per participant, invitee sign-ups, shot-card shares, and K. They are compared with the K the workbook says £50k would need (`Virality` tab).
