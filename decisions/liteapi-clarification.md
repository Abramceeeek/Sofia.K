# LiteAPI (Nuitée): written clarification before watching prices (draft, 7 Nov 2026)

**Why.** Watching a saved stay's price over time may fall outside what LiteAPI's terms allow, and ODYS doesn't book through LiteAPI (links out only, D120). Abram's decision (7 Nov): build the comparison screens with sample data; **switch on price watching with real data only after written confirmation.** Not legal advice; a solicitor reviews anything unclear before launch.

**What the terms say** (Nuitee Connect Terms of Service, https://www.liteapi.travel/terms, "Last Updated: 12 September 2025", read 7 Nov 2026; the operator is Nuitée Travel Limited, Dublin):
- Section 3: a licence "solely to deliver travel services to your end users, including: Browsing properties, Displaying rates and availability, Enabling bookings through your travel platform." "No other usage is permitted, including but not limited to: … Using Nuitee Connect data for competitive analysis, benchmarking, or derivative works, Storing, copying, or creating databases from Nuitee Connect data outside the permitted scope."
- Section 4: "property IDs, rates, and related materials are the exclusive intellectual property of Nuitée Travel Limited."
- Section 5 prohibits using the service "To scrape, harvest, or bulk-download inventory."
- The terms say nothing about look-to-book ratios or linking to other booking sites. The docs' pricing page (docs.liteapi.travel/reference/api-pricing-usage-costs, updated 23 Jul 2026) makes the free rates workflow subject to "a reasonable look-to-book ratio".
- Contact printed in the terms: **hello@nuitee.com** (also https://nuitee.com/contact).

## The email (Abram's final wording, 7 Nov; m205)

**Abram sends it himself**, from his own address, to **hello@nuitee.com** (the contact printed in the Terms; LiteAPI's developer support is a second route if there's no answer). Claude never sends it. Changes from the first draft, at Abram's review: it says ODYS is *evaluating* the integration with live prices not enabled; nearby dates keep the length of stay, guests and room terms; saved-stay checks happen only when the person opens ODYS, at most once in 24 hours, not as background monitoring; and it asks for explicit written permission, ideally naming the clause or an addendum.

**Price index cost:** Abram re-read the pages on 7 Nov and found **$0.05 per request** on the pricing page and on both endpoint pages (my reading earlier that day had $0.02 on the endpoint pages, so they may have been updated). The email asks Nuitée to confirm $0.05, rather than saying the pages disagree. The index stays off whatever the answer, until Abram decides to spend money on it.

> **Subject:** Questions about permitted use: price comparison and saved-stay price checks (ODYS)
>
> Hello Nuitée team,
>
> I'm developing ODYS, a travel-planning application currently being tested in the UK. We're evaluating LiteAPI's hotel-rate search to help travellers compare accommodation against their actual itineraries. Our intended model is to display accommodation options in ODYS and direct users to the relevant provider's website to complete their booking. We don't intend to take payments or make hotel bookings through LiteAPI. Before enabling live rates, I'd like written clarification on whether the following features are permitted under your Terms of Service dated 12 September 2025, particularly Sections 3–5.
>
> **1. Comparing nearby dates:** When someone selects a hotel, we'd like to show its available rates for check-in dates up to three days before and after their selected dates. We would preserve the length of stay and compare the same guests, room conditions, board and cancellation terms wherever an exact match is available. This would be an on-demand comparison initiated by the user, rather than a bulk inventory collection exercise. Is this permitted as part of displaying travel options to end users? Are there any restrictions on the number or frequency of these searches?
>
> **2. Watching a saved stay:** We'd like users to save accommodation they're considering. When they open ODYS, the application could check the current rate for that saved stay, at most once per 24 hours, using the same dates and occupancy. The user would then see whether the price has increased, decreased or remained unchanged since their previous observation. Would this type of user-initiated price monitoring be permitted if the user ultimately completes their booking through the accommodation provider or another external booking partner? Are there any limits on the number of saved properties or frequency of checks?
>
> **3. Retaining previous price observations:** Our intention is to keep a user's own previous price observations locally on their device, rather than building a central database of LiteAPI prices on our servers. This would allow the user to see how the price of their saved accommodation has changed over time. Would this be permitted? Are there any retention, caching or deletion requirements we should follow?
>
> **4. Look-to-book requirements and external bookings:** Your API pricing documentation refers to a reasonable look-to-book ratio for the core booking workflow. Since our intended model directs users to external booking providers rather than completing bookings through LiteAPI, could you clarify:
> * What look-to-book ratio would apply to ODYS?
> * Would our intended referral model be acceptable?
> * Would a different commercial agreement be required?
> * Would you recommend that bookings instead be completed through LiteAPI?
>
> **5. Price index endpoints:** We've also reviewed the beta price index endpoints: GET /v3.0/prices/hotels and GET /v3.0/prices/city. We are interested in potentially using these for contextual information, such as showing users how accommodation prices vary across different dates in a destination. Would this type of end-user display be permitted under your terms? The current API pricing documentation and endpoint pages show $0.05 per request. Could you confirm that this is the applicable price for both endpoints and whether any account-specific commercial conditions apply?
>
> Finally, could you confirm whether the proposed uses above are permitted under our existing agreement, and whether any written amendment or additional commercial agreement would be necessary? We want to make sure ODYS uses LiteAPI data in full compliance with your requirements before enabling these features for users.
>
> Thank you for your help.
>
> Kind regards,
> Abram
> ODYS

## Until the reply, and after it

- **Until then:** live nearby-date prices stay off (`Settings.stay_dates_live = False`), watched stays use labelled sample prices, the price index is never called, and nothing in production depends on LiteAPI.
- **The answer may change the business model, not only the feature.** If Nuitée wants bookings made through LiteAPI (question 4), that's a choice between referrals and in-app booking, with its own legal and money questions (taking payments, a merchant of record, commission). That's Abram's decision, not a code change.
- **Record the reply here** (date, who replied, the exact wording on each question, any clause or addendum named) and in the decision log; keep the email itself on Abram's computer, not in git, if it has anything personal or commercial in it. Only a sufficiently clear yes, in writing, switches anything on.
