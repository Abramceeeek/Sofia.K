# New opportunities (independent review, 11 Nov 2026)

**Decision.** Sixteen ideas, ranked by what they'd do for a person against what they'd cost to build. The top five all do the same job from different sides: **get someone to a first rated stop sooner, and make each rating worth more.** That is what the audit's benchmark says the product lives on (`brain-global-readiness.md`). None should be built before Checkpoint 3; by the project's own rule (D75) this list belongs on `after-9-nov.md`, which now points here. Ideas that need data ODYS doesn't have are marked and ranked low however good they sound.

Hours are estimates for the Brain and both apps together. "Others" is from the competitor research in `odys-market-and-product-strategy.md`; nothing was installed, so "doesn't" means "wasn't found to".

## Ranked

| # | Idea | Value | Hours | Needs from outside | Build it? |
|---|---|---|---|---|---|
| 1 | Three hours from here | High | 10 | Nothing | **First** |
| 2 | One tap on why a stop disappointed | High | 6 | Nothing | **Yes** |
| 3 | "Was anything different from what we said?" | High | 6 | Nothing | **Yes** |
| 4 | Any stay, judged against my days | High | 12 | The phone's own address lookup | **Yes** |
| 5 | Thursday's look at Saturday | High if it lands | 8 | Nothing | Yes, as an experiment |
| 6 | One plan for two people | High | 20 | Nothing | After 1 to 4 |
| 7 | The wet-weather day, ready before you leave | Medium | 6 | Nothing | Yes |
| 8 | Leave-by warnings on the day | Medium | 8 | Nothing | Yes |
| 9 | Step-free by evidence | Medium, high for some | 8 | Card data over time | Yes |
| 10 | One stop at a time | Medium | 6 | Nothing | A small experiment |
| 11 | The day, kept | Medium | 12 | Nothing | Later |
| 12 | A guest's day from the hotel's door | Unknown; decides the business | 20 | One willing hotel | **For Test E** |
| 13 | This week only | High for locals | 6, then 3 a week | Hours every week | Only if weekly use shows |
| 14 | Lunch as a real choice | Medium | 10 plus cards | Food cards | With more cards |
| 15 | Family rules | High for families | 15 plus data | Data that doesn't exist | Not yet |
| 16 | This weekend: A or B? | Medium | 10 | A second city | Not yet |

## The ideas

### 1. Three hours from here

- **Problem:** the app asks 14 questions before it shows anything, and most people who install a travel app are gone within a month. Someone standing in town with a free afternoon has no way in.
- **Idea:** one screen: where I am, how long I have. A short plan at once, from the general weights. The questions come afterwards, a couple at a time, and each rated stop does more than any of them.
- **Why others don't:** Google and the chatbots will suggest places nearby; none returns a timed, feasible route inside opening hours and then learns from how it went.
- **Value:** the shortest path to a first rating, which is the unit everything depends on. Also the product for residents.
- **Complexity:** low. The planner already plans from the population's weights (the example day does exactly this).
- **Depends on:** nothing new. Location is already asked for at this moment.
- **Money:** none directly; it feeds everything else.
- **Risks:** the first plan is generic, so it must say so; it changes the consent order (consent before the first plan still, one screen).
- **Priority:** first.

### 2. One tap on why a stop disappointed

- **Problem:** a rating of 2 says the stop was poor, not why. The model then guesses which taste to blame.
- **Idea:** after a 1 or 2, one row of taps: too crowded, too far, not my kind of place, the weather, not as described. The first three sharpen one weight each; the last flags the card.
- **Why others don't:** reviews elsewhere are written for other people. Nobody uses your reason to change your next plan.
- **Value:** each low rating teaches several times as much, and people feel heard.
- **Complexity:** low: one more observation type, or simply more weight on the named feature.
- **Depends on:** nothing.
- **Money:** none.
- **Risks:** asking after a bad experience can grate; keep it to one optional tap. Test on the benchmark before trusting the weighting.
- **Priority:** yes.

### 3. "Was anything different from what we said?"

- **Problem:** cards carry a "checked" date and go stale. A closed café or a new price is the fastest way to lose trust, and one founder can't re-check every card.
- **Idea:** on arrival, one quiet question with three taps: all as described, hours or price differ, closed. A flag puts the card in a queue for re-checking and marks it "being checked" for others.
- **Why others don't:** Google does, at its scale, for places. Nobody does it for moments (the approach, the best half hour).
- **Value:** the checked catalogue is ODYS's real asset; this is how it stays checked as it grows.
- **Complexity:** low.
- **Depends on:** people answering; Abram or a helper acting on flags (~15 minutes each).
- **Money:** none.
- **Risks:** false flags; needs two before a card changes status.
- **Priority:** yes.

### 4. Any stay, judged against my days

- **Problem:** booking sites say how far a hotel is from "the centre". Nobody says how far it is from *your* mornings.
- **Idea:** paste a stay's address or pick it on a map; ODYS says the minutes to each day's first stop and back at night, and which day it suits least. No hotel search needed.
- **Why others don't:** they sell rooms, not days; they don't have your days.
- **Value:** a real decision made easier, and the one piece of the trips product nobody else has. It already exists in the Brain (`stayprices.trip_fit`), tied to search results.
- **Complexity:** low to medium: an address-to-point lookup on the phone (both platforms provide one, free) and one screen.
- **Depends on:** nothing paid. It removes the dependence on a hotel search provider.
- **Money:** an affiliate link out to that stay, disclosed.
- **Risks:** travel times outside London are estimates; say so.
- **Priority:** yes. It also lets in-app hotel search be dropped.

### 5. Thursday's look at Saturday

- **Problem:** people open a planner when they already have a plan to make. A habit needs a reason to look.
- **Idea:** for people who ask for it: on Thursday evening, one notification with a day for Saturday that fits the forecast and what they've rated. One tap keeps it; ignoring it costs nothing.
- **Why others don't:** event apps push tickets; nobody offers a whole personal day.
- **Value:** the looking-forward is part of the pleasure (the research the project already cites: Nawijn and others). It is the cheapest test of whether a weekly habit exists.
- **Complexity:** low: local notifications and the forecast exist.
- **Depends on:** enough cards that Saturdays differ.
- **Money:** none; it is the retention test.
- **Risks:** notifications annoy; strictly opt-in, weekly at most, easy to stop.
- **Priority:** yes, as a measured experiment (how many keep the plan; how many go).

### 6. One plan for two people

- **Problem:** most days out are with someone, and "what shall we do?" is a negotiation.
- **Idea:** two people, each with their own answers on their own phone, share a code. One day that is fair to both, and says where it leans to whom.
- **Why others don't:** shared itineraries exist (Wanderlog); a plan computed from two people's tastes wasn't found.
- **Value:** a frequent, real problem, and every use brings a second person in.
- **Complexity:** medium. The fairness method is prototyped (m240); pairing two installs is new.
- **Depends on:** nothing outside.
- **Money:** a natural paid feature for groups later.
- **Risks:** privacy: share the plan and its reasons, never one person's answers with the other. A consent screen of its own.
- **Priority:** after the first four.

### 7. The wet-weather day, ready before you leave

- **Problem:** rain arrives when the signal doesn't.
- **Idea:** every plan with outdoor stops carries its indoor alternative, worked out in advance and saved with the offline day. One tap: "It's raining".
- **Why others don't:** they re-plan online, generically.
- **Value:** the day survives the weather, with no connection needed.
- **Complexity:** low. Cards already name a rain swap.
- **Depends on:** nothing.
- **Money:** none.
- **Risks:** the alternative also has opening hours; plan it properly, not as a list.
- **Priority:** yes.

### 8. Leave-by warnings on the day

- **Problem:** lingering at stop two quietly makes stop four impossible.
- **Idea:** "Now" shows the latest time to leave for the next stop to still work (last entry, or the best half hour of light), and offers to drop or reorder when it can't.
- **Why others don't:** maps warn about closing times while navigating to one place, not across a day.
- **Value:** fewer days that fall apart; it is what a good companion would say.
- **Complexity:** low to medium: the hours and windows are on the cards.
- **Depends on:** nothing.
- **Money:** none.
- **Risks:** nagging. One quiet line, never a notification, in keeping with "calm technology".
- **Priority:** yes.

### 9. Step-free by evidence

- **Problem:** for someone who needs step-free access, "probably fine" is useless. Today step-free access is known for 17 of London's 49 cards (m245), and was unknown for 82% of the places the planner benchmark chose (m206).
- **Idea:** every stop shows one of three words for its access: checked, claimed, unknown. A switch plans with "checked" only, and says how few places that leaves. Idea 3 fills the gaps over time.
- **Why others don't:** they show a wheelchair icon from the venue's own claim.
- **Value:** honest, and for some people the difference between using the app and not.
- **Complexity:** low: the quality standard already has the three states.
- **Depends on:** checking cards, a few a week.
- **Money:** none.
- **Risks:** a small catalogue becomes tiny under the filter. Say so plainly rather than hide it.
- **Priority:** yes.

### 10. One stop at a time

- **Problem:** a full itinerary can feel like a schedule to keep.
- **Idea:** an option: the day is planned, and each stop is revealed only as you leave the last. The approach and the reveal are the product's own idea of a moment.
- **Why others don't:** nobody was found to.
- **Value:** delight, for the people who want it. Distinctive, and nearly free.
- **Complexity:** low: the screens exist.
- **Depends on:** nothing.
- **Money:** none.
- **Risks:** some people hate not knowing; opt-in, with "show me the whole day" always one tap away, and costs and travel time said up front.
- **Priority:** a small experiment.

### 11. The day, kept

- **Problem:** nothing remains of a good day except the camera roll.
- **Idea:** a private page per day: the stops, your ratings, your best hour in your own words, and photos you pick, all kept on the phone.
- **Why others don't:** Polarsteps does it for journeys and is the travel app people keep; nobody ties it to what you rated.
- **Value:** a reason to open the app after the day, and to rate.
- **Complexity:** medium.
- **Depends on:** nothing; photos never leave the phone.
- **Money:** a printed book later, perhaps.
- **Risks:** scope creep into a photo app.
- **Priority:** later.

### 12. A guest's day from the hotel's door

- **Problem:** the business line ("businesses will pay") has never been tested, and there is nothing to show a hotel.
- **Idea:** a hotel gets a link or a code for its guests. A guest answers six questions on a web page, with no app to install, and gets a day that starts and ends at that hotel.
- **Why others don't:** concierge software lists the same ten sights for everyone.
- **Value:** unknown, which is the point: it is the demo Test E needs.
- **Complexity:** medium: the Brain can do it today; a small web page is new.
- **Depends on:** one hotel or serviced-apartment manager willing to try it.
- **Money:** this *is* the money test: a monthly fee per property.
- **Risks:** a web version to maintain; keep it to one page.
- **Priority:** build only for Test E, and only the least that lets five managers react.

### 13. This week only

- **Problem:** a resident sees the same 49 cards.
- **Idea:** five to ten dated moments a week (a market, an exhibition's last days, a late opening), each from an official source, each with an end date.
- **Why others don't:** they do: Time Out, Fever, DICE. ODYS's difference would be choosing among them for the person and fitting them into a day.
- **Value:** the reason to open the app weekly.
- **Complexity:** low to build; the cost is three hours of editing every week, for ever.
- **Depends on:** those hours, or a licensed events feed (a cost).
- **Money:** ticket affiliate links.
- **Risks:** it competes with products that do only this, with staff.
- **Priority:** only once idea 5 shows people come back.

### 14. Lunch as a real choice

- **Problem:** lunch is often "near X", a gap in the day, not a recommendation.
- **Idea:** three checked places to eat along the route, with a price and a reason, one tap to choose.
- **Why others don't:** maps list hundreds.
- **Value:** food is a third of a good day; today the model learns almost nothing about it.
- **Complexity:** medium; the need is cards.
- **Depends on:** 30 or more food cards.
- **Money:** none soon.
- **Risks:** stale restaurant facts, the fastest-changing kind.
- **Priority:** with the next batch of cards.

### 15. Family rules

- **Problem:** a day with a four-year-old is a different problem, not a different taste.
- **Idea:** ages, then rules: the longest walk, a toilet within reach, buggy access, child prices.
- **Why others don't:** some list "family-friendly"; none plans by rules.
- **Value:** high for families.
- **Complexity:** medium in code; the planner takes hard rules already.
- **Depends on:** data that doesn't exist for most places.
- **Money:** families pay for certainty.
- **Risks:** a promise the data can't keep. Children's ages are personal data about children: a privacy review first.
- **Priority:** not yet.

### 16. This weekend: A or B?

- **Problem:** choosing between two places to go is a guess.
- **Idea:** two destinations compared for *you*: how many strong matches each has, what the days would cost, the weather that weekend.
- **Why others don't:** they compare flight prices.
- **Value:** real, for the "I don't know where to go" person.
- **Complexity:** low once two cities exist.
- **Depends on:** a second city.
- **Money:** affiliate links.
- **Risks:** none beyond the data.
- **Priority:** not yet.

## Deliberately not on the list

- **A chat assistant.** Everyone has one, and it would be judged against the best in the world.
- **Price forecasts.** Already ruled out by the project, rightly.
- **3D or AR anything** (`odys-3d-and-spatial-experience.md`).
- **In-app booking** (`payment-architecture.md` §5).
- **A social feed of other people's days.** Moderation duties, cold start, and it works against a plan being yours.
