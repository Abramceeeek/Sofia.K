# Market and product strategy (independent review, 11 Nov 2026)

**Decision.** As "one app for all of travel", ODYS is not defensible: Google, Booking.com and Airbnb are each bundling the same services with a thousand times the reach, and every chatbot now writes an itinerary for free. The part of ODYS nobody else was found to have is narrower: **it learns one person's taste from how their own days actually went, and it holds hand-checked "moments" rather than a list of places.** That is unproven, not disproven. It only compounds if people use it often, which a holiday twice a year can't supply. So the wedge worth betting on is **days out in your own city, most weeks**, with trips as the occasional extension, the reverse of the direction set on 6 Nov ("Trips are the main product"). I'd settle that question with evidence at Checkpoint 3 before building further on either side.

**How to read this.** "VERIFIED" means a page read in this session (11 Nov 2026) said it; where it came through a search summary or a third party, it says so. "HYPOTHESIS" is my reasoning. Company figures are their own claims. Nothing here was tested by installing a competitor.

## What the evidence says

1. **VERIFIED: the big players ship the feature.** Google added conversational trip planning to Maps and Search in 2026 (third-party reports; rollout countries disputed). Booking.com has had an AI trip planner since 2023 and is building a "connected trip" of hotels, flights and attractions. Expedia launched its assistant in 2024. Airbnb began listing Viator's tours in August 2026 (Skift).
2. **VERIFIED: people travel rarely.** UK adults: 3.8 holidays a year on average, UK breaks included; 59% went abroad (ABTA Holiday Habits 2025-26, n = 2,001, read directly).
3. **VERIFIED (secondary): travel apps don't keep people.** About 18% return the next day and about 3% after 30 days (Business of Apps; Adjust gave 4% in 2022).
4. **VERIFIED: travel is the cheapest subscription category.** Median yearly price US$20, "lowest of any category" (RevenueCat 2026, web page).
5. **VERIFIED: trust in AI planning is thin, and demand is real.** 8% used AI for holiday inspiration, double the year before; 43% are "confident to some degree" letting AI plan a holiday and 15% extremely confident letting it book (ABTA, read directly). Vendor surveys report about one in six AI users being sent somewhere that doesn't exist (Greetwell, US, via secondary coverage).
6. **VERIFIED: content alone has not protected anyone.** Culture Trip raised US$155m and was sold in parts in 2024 (Skift). Utrip, a personalised trip planner, raised about US$4m and closed in 2019 (GeekWire). Triposo closed in 2023.
7. **NOT FOUND: any evidence that personalised recommendation beats a popularity list in tourism with the amount of data a new app has**, or that answers to onboarding questions predict what people enjoy. The academic work found is thin and mostly on old check-in data. This is exactly what Test B and the first ratings are for.
8. **A correction worth making:** the idea that travel planners are a "tarpit" is often credited to Y Combinator. The talk the term comes from uses weekend plans with friends as its example, not travel planning (transcript read). The warning is fair; the attribution isn't.

## The questions, answered straight

**Why open ODYS instead of Google Maps?** Today, mostly you wouldn't. Google knows where you've been and now plans in conversation. The reason would be a plan that is visibly *yours* in a way Google's isn't, backed by having asked how each stop felt. For someone who never rates a stop, ODYS has no advantage. *Hypothesis.*

**Instead of Wanderlog?** Different jobs. Wanderlog (about US$40 a year for Pro, third-party figure) holds the plan you researched. ODYS claims to do the research. That only wins if its picks beat your own, which is what Test B measures.

**Why book through ODYS?** There is no good reason, and that's fine. People compare across many sites before booking (Expedia's own 2023 study: dozens of pages over 45 days). ODYS hands off, and should. The legal analysis says the same (`payment-architecture.md` §5).

**What makes its recommendations trustworthy?** Three things that are real in the code today: every card's facts were checked against an official source and carry the date; every recommendation says why, from the planner's actual inputs (m219); and the planner can't place a stop outside its opening hours. That is a genuine edge over a chatbot. It is also 49 cards, in one city.

**Why come back after one holiday?** For a holiday, you wouldn't, and the retention figures above say so. You'd come back for next Saturday. That is the argument for the wedge.

**What can it do that a chatbot can't?** Be specific:
- *Facts and routing:* chatbots with live tools are closing this gap fast. A 2024 test found 90% of itineraries had an error (an old model, commissioned by an agency). Don't build a strategy on them staying bad.
- *A fitted model of one person, updated from their own ratings:* a chatbot has memory, not a model. This is ODYS's real technical difference, and by this audit's benchmark it needs about 20 rated stops to become good (`brain-global-readiness.md`).
- *A day that provably fits:* opening hours, travel times, the budget and the person's own commitments as hard rules, checked by a solver. A chatbot asserts feasibility; ODYS computes it.
- *Moments:* the approach, the light, the half hour to be there. Hand-made, so it is the hardest part for anyone to copy and the hardest for ODYS to scale.

**Is there a network effect?** Not really. One person's ratings improve their own plans. They improve other people's only by sharpening the starting point for newcomers, which needs hundreds of raters per city before it shows. The advantage is a switching cost (my history is here), not a network.

**What becomes an advantage over time?** In order of how real it is today: (1) rating histories, per person; (2) the catalogue of checked moments, per city; (3) a population model fitted to real ratings, which today is entirely guesses (`brain/data/priors.yaml` says so itself). None exists at a scale that matters yet.

**Is combining existing services enough?** No. It is what Booking.com, Airbnb and Google are each doing, with existing customers. An aggregator with no inventory, no audience and no price advantage has nothing to bundle with.

## The three ways in

| Journey | What exists today | Friction and gaps | What I'd do |
|---|---|---|---|
| **A. "I don't know where to go"** | Nothing. One destination (London); discovery "without a feed" is a prototype in the Brain (m239) with no data behind it | The product can't answer the question it is asked. Answering it for the world needs data ODYS doesn't have and shouldn't hand-make | Don't build it. This is the journey where Google and the chatbots are strongest and ODYS has no asset |
| **B. "I know where I'm going"** | Trips: length, days planned around arrival and departure, own time, flights and stays to compare, the stay judged against the days. Sample or test data for flights and stays | Only works if "where" is London. 14 questions before a first plan. The flight and stay search is the least distinctive and most expensive part to keep | Keep days and trip length. **Cut flights search and keep stays only as "judge this stay against my days"**, fed by a link or a paste, which is the one piece no booking site does |
| **C. "I'm already here"** | The "Now" screen, re-planning the rest of the day, arrival, ratings, the offline view | Needs the trip planned beforehand. No way in for someone standing in a city with a free afternoon | **The best entry point there is.** "I have three hours from here": one screen, no onboarding first, questions asked afterwards. It is also the days-out product for residents |

## The wedge, and what would change my mind

*Hypothesis, with the reasoning.*

- A model that learns from ratings needs ratings. Twenty rated stops is five days out. At two holidays a year that is years; at two Saturdays a month it is ten weeks.
- The catalogue is the binding constraint either way. A weekly user in London needs a few hundred cards to keep finding new days that suit them; 49 cards is 16 days at three places a day with no repeats, and fewer for any one person's taste. A second city for visitors needs its own hundred.
- So depth in one city, for people who live there, builds both assets (ratings and catalogue) fastest. A trip to London for a visitor then uses the same catalogue.

What it is not: a claim that locals will pay, or that they'll come back weekly. Fever and DICE built that habit with tickets and events, and AllTrails with a map you need on the hill, not with personalisation. **The test is simple and already half-built: of the people who plan one day, how many plan a second within a month without being asked** (the app already logs `plan_another_day`). If that number is near zero among friends and strangers, neither wedge works and the idea needs rethinking, not more features.

What would change my mind towards trips: a hotel or serviced-apartment firm saying in Test E that it would pay for guests' days planned around their stay. Then the customer is the business, frequency stops mattering, and trips are right.

## Competitors at a glance

Cells are VERIFIED (V) from a source in this session or ASSUMED (A) from general knowledge; nothing was installed.

| Product | Learns your taste from your own ratings | Moment-level, checked content | A day that provably fits | Offline | Books | Price |
|---|---|---|---|---|---|---|
| Google Maps / Gemini | No, as far as could be found (A) | No (A) | Routing yes; pace unknown (A) | Yes (A) | Links to hotels and flights (A) | Free |
| Wanderlog | No (A) | No (A) | Route optimising in Pro (V, third party) | In Pro (V, third party) | Links (A) | Pro about US$40 a year (V, third party) |
| Booking.com | No (A) | No (A) | Unknown | Unknown | Yes (V) | Free |
| Expedia | No (A) | No (A) | Unknown | Unknown | Yes (V) | Free |
| Tripadvisor / Viator | No (A) | Operator listings (A) | No (A) | Unknown | Yes (V) | Free |
| Mindtrip, Layla | Chat memory at most (A) | No (A) | Unknown | Unknown | Starting to (claims, unverified) | Layla US$49 a year (V, third party) |
| TripIt | No (A) | No (A) | No (A) | In Pro (A) | No | About US$49 a year (V, third party) |
| Polarsteps | No (A) | No (A) | No (A) | Yes (A) | No | €29.99 a year (V) |
| ChatGPT, Gemini, Perplexity | Chat memory only (A) | No | Asserted, not computed; error-prone in a dated test (V) | No (A) | Increasingly (A) | Free or paid |
| **ODYS** | **Yes, by design; needs ~20 rated stops** (this audit) | **Yes: 49 cards, one city** | **Yes** | Today's plan (built) | No, by choice | Free |

**Muslim-friendly travel:** the specialist sites (HalalBooking, a commission-based booking site claiming US$89m of sales in 2025; HalalTrip; Have Halal Will Travel) sell or publish, they don't plan a day. The gap ODYS could fill is practical (which of today's stops have food I can eat), and it rests on certification data nobody was found to license: the Halal Monitoring Committee's site showed no public dataset (UNVERIFIED: ask them directly). ODYS's own rule stands: a food need is a filter the person sets, never a guess about who they are (`food-preferences-and-privacy.md`).

## What I'd stop, keep and start

| | | Why |
|---|---|---|
| **Stop** | Widening the surface before Checkpoint 3: multi-city itineraries, destination intelligence, group trips, display currencies, discovery (m234 to m243, the last sprint) | All built ahead of any evidence that one person prefers one personal day. The hours are the scarce thing |
| **Stop** | In-app flight search | The least distinctive feature, on a provider whose terms assume bookings ODYS won't make |
| **Keep** | The checked cards, the planner's hard rules, the explanations, ratings, the offline day | These are the trustworthy core |
| **Start** | A no-questions "three hours from here" entry | Shortest path to a first rated stop, which is the unit everything depends on |
| **Start** | Measuring the second plan | The one number that says whether there is a product |
| **Start** | More cards in London, to about 150 | Without them neither a weekly local nor the model's learning is possible |

## Sources (read 11 Nov 2026)

Read directly: ABTA Holiday Habits 2025-26 (https://www.abta.com/sites/default/files/media/document/uploads/Holiday%20Habits_2025_26_FINAL.pdf); RevenueCat State of Subscription Apps 2026 (https://www.revenuecat.com/state-of-subscription-apps/); the Y Combinator talk transcript (https://sozai.app/transcript/get-evaluate-startup-ideas-startup-school/).

Through search summaries or third parties (treat as indicative): Google's 2026 planning features (eweek.com, engine.com, blog.google); Booking.com (the-decoder.com, skift.com, hospitality.today); Expedia (travelmarketreport.com); Airbnb and Viator (skift.com, 11 Aug 2026; phocuswire.com); retention (businessofapps.com, adjust.com); Wanderlog, TripIt, Layla, Polarsteps prices (review sites, support.polarsteps.com); marketplace commissions (getyourguide.supply, arival.travel, trekksoft.com); affiliate rates (ui.awin.com, flexoffers.com, travelpayouts.com); AI errors (travolution.com on the 2024 test; stacker.com on Greetwell); Culture Trip (skift.com, 29 Feb 2024); Utrip (geekwire.com; skift.com, paywalled); Triposo (wikipedia.org); HalalBooking (salaamgateway.com); the Global Muslim Travel Index (mastercard.com press release, June 2025); academic (link.springer.com/article/10.1007/s40558-021-00214-5; arxiv.org/abs/2507.13725).

Not found or not confirmed: user numbers for Wanderlog, Polarsteps, Mindtrip; RevenueCat's download-to-paid and retention for travel (in a PDF not obtained); Booking.com's, Expedia's and Trainline's affiliate terms from their own pages; a current-model test of chatbot itineraries; whether UK halal certifiers license their lists.
