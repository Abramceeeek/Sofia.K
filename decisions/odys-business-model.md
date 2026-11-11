# The business model (independent review, 11 Nov 2026)

**Decision.** ODYS does not yet have a way to make money that survives arithmetic, and it should not pick one now. On today's evidence the two models people reach for first, **a consumer subscription and affiliate links, are both small**: travel is the cheapest subscription category there is, people travel a few times a year, and referral commissions are pennies until the audience is very large. The models with a chance for a founder with 7.5 hours a week are narrower: **a fee on experiences ODYS genuinely sends people to**, **a one-off payment per trip rather than a subscription**, and **selling the planner to businesses** (still the project's own untested assumption, D86). Two cheap tests decide between them and cost about 12 hours together: Test D with a payment link, and five conversations for Test E.

What is fact and what is my reasoning is marked. Market figures come from the research in `odys-market-and-product-strategy.md`; several are from secondary sources and say so.

## The numbers that frame everything

| Fact | Source | What it means |
|---|---|---|
| UK adults took an average of 3.8 holidays a year, UK breaks included; 59% went abroad | ABTA Holiday Habits 2025-26 (n = 2,001), read directly | A holiday planner is opened a few times a year. A subscription has to be justified in those weeks |
| The median yearly price of a travel subscription app is US$20, "lowest of any category" | RevenueCat, State of Subscription Apps 2026 (web page) | The ceiling on a consumer subscription is low before any commission |
| Travel apps keep about 3% to 4% of users after 30 days | Business of Apps, Adjust (secondary) | Most people who install will be gone before their first rated day |
| Experience marketplaces take 20% to 30% from the supplier | GetYourGuide's supplier page (20-30%); Viator ~25% (third party) | The money in experiences is in being the place the booking happens, not in pointing at it |
| Affiliates of those marketplaces earn about 7% to 8%, with a 30-day window | Awin and others (third party; Awin shows 4% for Viator US) | Pointing at it earns roughly a quarter of what the marketplace takes |
| The stores take 15% of in-app digital sales from small developers | Apple, Google (read directly) | Net of it, a £20 subscription is £17 |
| The model needs about five rated days before it knows a person well | This audit's benchmark, synthetic and best case (`brain-global-readiness.md`) | The thing a subscriber would be paying for arrives late |

## Eight ways to make money, compared

Revenue is per 1,000 people using the app in a month, on stated assumptions. **Every assumption is a GUESS** unless a source is given; the point is the order of magnitude.

| Model | Revenue per 1,000 monthly users (illustration) | Build | Getting customers | Rules it brings | Margin | Depends on | Risk to trust | Time to first £ |
|---|---|---|---|---|---|---|---|---|
| 1. Free app, affiliate links | **About £100 to £400 a month.** Experiences: 10% click, 30% of those book £40, 8% = £96. Stays: 2% book a £300 stay through the link, about 5% = £300 | Low (8 h) | As hard as any consumer app | Disclosure of paid links | ~100% | Each programme's approval and terms | **High if links ever change the ranking** | Weeks after incorporation |
| 2. Subscription | **About £60 a month.** 3% pay £30 a year, less the stores' 15% | Medium (25-30 h) | Hard, and retention is the problem | Store billing; subscription and cancellation law | 85% | Apple, Google | Low | Months; needs retention first |
| 3. Booking commission (ODYS books) | Higher per booking, but see the next column | High | — | **Makes ODYS a travel seller: packages, ATOL, refunds, chargebacks** (`payment-architecture.md` §5) | Thin | Suppliers, a payment provider | Medium | Not recommended |
| 4. A fee on experiences sold through ODYS | **About £150 to £300 a month.** 5% buy one £20-£40 experience; ODYS keeps 15% | Medium (30-45 h) | The same, plus finding hosts | Payments through a provider; host terms; Online Safety Act if they message | High on the fee | Hosts turning up | Medium: ODYS's name is on the day | Months |
| 5. Paid planning as a one-off | **About £100 a month.** 2% buy a £5.99 "trip pass" when they have a trip, less 15% | Low to medium (15 h) | The same | Store billing | 85% | Apple, Google | Low | Months |
| 6. Supplier partnerships | Unknown. A venue pays for guaranteed, well-matched visitors | Low in code, high in hours | Selling to venues one by one | Disclosure | High | A few partners | High unless labelled | Slow |
| 7. Sponsored places | Small until the audience is large | Low | — | Must be labelled; CMA and ASA rules | High | Advertisers | **Highest** | Not for years |
| 8. The planner for businesses | **The project's own figure: £350 a client a month** (a GUESS, D40). 12 clients is £50,000 a year | Medium to high per client | Five to ten sales conversations per client (GUESS) | Contracts, data-processing terms | High | A few clients | Low | Unknown: Test E hasn't run |

Reading it:
- **Models 1, 2 and 5 together are worth a few hundred pounds a month per 1,000 active people.** To pay one modest salary that way needs tens of thousands of people who keep coming back, in a category where 97% leave within a month.
- **Model 4 is the only consumer one where ODYS's own work (matching a person to a day) is the thing being paid for.** It is also the one with the most hours in it.
- **Model 8 is the only one where a dozen customers would be enough.** It rests entirely on an assumption nobody has tested.

## Where people would really pay (my reasoning)

1. **For the day itself.** People already pay for a boat, a ticket, a tasting. If ODYS is why they went, a share of that is earned. This is model 4, and Test D is its test.
2. **Once per trip, not every month.** A trip is an event. "£5.99 to plan this trip properly" (longer trips, re-planning on the day, the offline pack, stays judged against the plan) matches how often people travel better than £30 a year does. Apple and Google both allow a one-off purchase of a feature.
3. **For a group.** The person organising eight friends has a real problem and pays to solve it. Not built; the group prototype (m240) is the start.
4. **As a business with guests.** A hotel, an aparthotel or a serviced-apartment firm that could send each guest "your stay, planned around you" has a reason to pay monthly. This is model 8.

Where they won't: for recommendations alone. Google, Wanderlog's free tier and every chatbot give those away.

## Three models to choose between later

| | Low-complexity start | Sustainable growth | Long-term platform |
|---|---|---|---|
| **What it is** | The free app, with disclosed affiliate links on the bookings people already click out to | One city done well: days out people pay for (a fee on experiences), and a paid trip pass for visitors | The planner and the moment catalogue offered to travel businesses, with the consumer app as the showcase and the source of ratings |
| **Money** | Affiliate only | Experience fees, trip passes; a subscription only if weekly use appears | Business contracts; experience fees; data partnerships |
| **Needs** | A company; programme approvals; a disclosure line; links that carry the affiliate id | Test D passing; a provider account; 5 to 10 hosts or venues; about 100 cards so a weekly user doesn't run out | Test E passing; a second city built from the destination registry (m207, m235); an API |
| **Hours to build** | ~8 | ~60 to 80, plus hours every week with hosts | 150+, and it stops being a one-person job |
| **What could it earn** | Pocket money. Its value is learning what people click | Hundreds a month per 1,000 active people | The only route to a salary on the evidence so far |
| **Main risk** | None, if the ranking is never touched | Hours: hosts and customers both need looking after | Selling to businesses is a different job from building an app |

They are stages more than alternatives: the first costs almost nothing and teaches what the second needs.

## Keeping money out of the recommendations

The product's claim is that a plan is for the person. One paid placement that isn't labelled ends that claim. Rules, in order of importance:

1. **Score first, then attach links.** The planner never sees which places earn money. Commission lives in a separate table that the planner's code does not import.
2. **A test enforces it**: the same person and day give the same plan with every commission set to zero and to its real value (~1 h when the first commission exists).
3. **Anything paid for is labelled "Sponsored" and sits outside the personal plan**, never as a stop in it.
4. **Every outbound link that earns says so** next to the link, in plain words ("We may earn a commission if you book through this link. It never changes what we recommend.").
5. **Measure it:** each month, how often would the plan have differed without the commercial rule? The answer should be never, and the number should be published.

The quality standard already in the code (`brain/src/brain/quality.py`, m234) judges a recommendation on relevance, practicality, cost and trust. Money made by ODYS is deliberately not one of the four, and should stay out.

## Two things that would cost money unnecessarily

- **Search providers built for booking, used only for searching.** Flights come from Duffel and stays from LiteAPI, and both businesses make their money when a booking is made through them. Duffel charges for searches beyond a set ratio to bookings (the Brain's own note, `trips.py`: "$0.005 a search beyond 1,500 per order … with no orders every search counts"), and LiteAPI's terms refer to a look-to-book ratio (`liteapi-clarification.md`, question 4, unanswered). ODYS sends every booking elsewhere, so it is, by design, the customer these providers least want. **For a click-out model the natural suppliers are the ones built for click-out**: affiliate feeds (Skyscanner through Travelpayouts, Booking.com's affiliate programme), which pay ODYS instead of charging it. Decide this before putting live keys in (~10 h to switch flights, similar for stays; Abram's decision because it changes scope).
- **A paid macOS build for every app change.** Already limited to `main` (m188). Keep it that way.

## What to do

| When | What | Hours |
|---|---|---|
| After Test B | **Test D by hand:** one real day out with a price, a payment link, ten people. Does anyone pay? | 4 |
| After Test B | **Test E:** five conversations with a hotel or serviced-apartment manager, with the working app | 8 |
| At incorporation | Apply to two affiliate programmes (one for experiences, one for stays); add the disclosure line | 8 |
| Before live provider keys | Decide: booking-first providers, or affiliate feeds | 2 to decide |
| Only then | Build the one model the tests point to | See `payment-architecture.md` §10 |

## Sources

All in `odys-market-and-product-strategy.md`, with which were read directly and which are third-party. The illustrations in the table are mine.
