# LiteAPI (Nuitée): written clarification before watching prices (draft, 7 Nov 2026)

**Why.** Watching a saved stay's price over time may fall outside what LiteAPI's terms allow, and ODYS doesn't book through LiteAPI (links out only, D120). Abram's decision (7 Nov): build the comparison screens with sample data; **switch on price watching with real data only after written confirmation.** Not legal advice; a solicitor reviews anything unclear before launch.

**What the terms say** (Nuitee Connect Terms of Service, https://www.liteapi.travel/terms, "Last Updated: 12 September 2025", read 7 Nov 2026; the operator is Nuitée Travel Limited, Dublin):
- Section 3: a licence "solely to deliver travel services to your end users, including: Browsing properties, Displaying rates and availability, Enabling bookings through your travel platform." "No other usage is permitted, including but not limited to: … Using Nuitee Connect data for competitive analysis, benchmarking, or derivative works, Storing, copying, or creating databases from Nuitee Connect data outside the permitted scope."
- Section 4: "property IDs, rates, and related materials are the exclusive intellectual property of Nuitée Travel Limited."
- Section 5 prohibits using the service "To scrape, harvest, or bulk-download inventory."
- The terms say nothing about look-to-book ratios or linking to other booking sites. The docs' pricing page (docs.liteapi.travel/reference/api-pricing-usage-costs, updated 23 Jul 2026) makes the free rates workflow subject to "a reasonable look-to-book ratio".
- Contact printed in the terms: **hello@nuitee.com** (also https://nuitee.com/contact).

## The email (Abram reviews the final wording, then sends it from his own address; 7 Nov)

> **Subject:** Questions about permitted use: price comparison and saved-stay price checks (ODYS)
>
> Hello,
>
> I'm building ODYS, a travel-planning app in testing in the UK. We use LiteAPI's rates search to show people places to stay for their trip. We don't take bookings or payments ourselves: people book on the provider's own site.
>
> Before we build two features, I'd like to check they're within your Terms of Service (12 September 2025, sections 3–5):
>
> 1. **Comparing nearby dates:** showing the same hotel's current rates for the same stay length on check-in dates up to 3 days either side of the person's dates (about 7 rate searches when they ask).
> 2. **Watching a saved stay:** when a person saves a hotel for their dates, checking its current rate for the same dates, guests and room terms at most once a day while they use the app, and showing the change since they last looked.
>
> Could you confirm in writing:
> 1. Whether we may check saved hotels' rates in this way without the booking being made through LiteAPI.
> 2. Whether a daily check per saved hotel is acceptable, and any limit you'd set.
> 3. Whether a person's own earlier observed prices may be kept on their device (not on our servers) to show the change.
> 4. Whether we may display price changes over time to that person.
> 5. What look-to-book ratio, or commercial agreement, applies to an app that refers people to book elsewhere; and whether we should be booking through LiteAPI instead.
>
> We also saw the beta price index (GET /prices/hotels and /prices/city). If we used it for context such as "places to stay in this city usually cost more on these dates", would that be permitted display? And what does it cost per request: the endpoint pages say $0.02, the pricing page $0.05?
>
> Thank you,
> Abram
> ODYS

## After the reply

Record the answer here (date, who replied, what they allowed) and in the decision log. Only then does price watching use real data. Until then it runs on clearly labelled sample prices.
