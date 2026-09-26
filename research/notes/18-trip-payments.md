# Area 18 — Trip payments, package travel and group-trip safety (Phase 3 addition)

**Decision:**
- **Paid group trips are day trips only** (under 24 hours, no overnight stay). Those are outside the Package Travel Regulations.
- **Overnight trips:** the app sells nothing travel-related. Attendees book their own accommodation and transport, until a solicitor confirms the package position. The rules tighten on **6 April 2027**.
- **Never hold trip money.** Use **Stripe Connect with direct charges**: each attendee pays the host's or venue's own Stripe account, and our fee arrives as an application fee. Funds never sit in our balance.
- **The weekend test stays payment-free for us:** hosts collect as they do today.
- **Safety before the first paid trip:** a written trip policy, a host checklist and risk note, verified hosts, in-app reporting, and public liability insurance.
- **Cost after v0, once the gates clear:** payments ~8–10 h; safety kit ~4 h; solicitor review of overnight trips (£, UNVERIFIED).

## Package Travel Regulations 2018 (read on legislation.gov.uk, 2026-09-26)

- **Scope (reg 3(2)(a)):** the Regulations **do not apply** to "packages … covering a period of less than 24 hours, unless overnight accommodation is included". A day trip is outside them however it is sold.
- **Also excluded (reg 3(2)(b)):** packages offered "occasionally on a not-for-profit basis for a limited group of travellers". That fits the founder's weekend test, but not anything we charge a fee on.
- **A package** is at least two *different* types of travel service (carriage of passengers, accommodation, car hire, other tourist services) for the same trip, combined by one trader or sold at an inclusive price (reg 2(5)). The text read shows a "significant proportion of the value / essential feature" test for tourist services in reg 2(4), which covers linked travel arrangements. The package equivalent (reg 2(6)) was not read: **UNVERIFIED**.
- **If we sold a package:** we would carry organiser duties: liability for performance, insolvency protection and information requirements. That is out of scope for us.
- **From 6 April 2027** (Amendment Regulations 2026, S.I. 2026/455, read):
  - linked travel arrangements are abolished;
  - "package" is widened: separately selected and separately paid travel services become a package "if a single trader has facilitated, on the occasion of a single visit to … the trader's point of sale, the separate selection of and separate payment for each". An app that lets a group pick and pay for a coach *and* a hostel in one session could become the organiser.
  - The 24-hour exclusion stays; only the linked-arrangement words are removed.

## Payments without holding money

- **FCA commercial agent exclusion** (FCA page, updated 17 Feb 2023, read; PSRs 2017 Sch 1 Pt 2 para 2(b), read):
  - The exclusion only covers an agent acting for the payer **or** the payee, "but not both".
  - A business "is likely to be acting for both … if payments are transferred into an account that it controls or manages before being sent to the payee". That would need FCA authorisation or registration.
  - → Collecting everyone's share into our account and paying the host or venue is the pattern to avoid.
- **Stripe Connect direct charges** (Stripe docs, read):
  - "the payment appears as a charge on the connected account, not your platform's account", and "your account balance increases with application fees".
  - Refunds and chargebacks come out of the connected account.
  - *Destination charges* land in the platform balance first, so avoid them.
- **Stripe Connect UK pricing** (read):
  - If Stripe bills connected accounts directly, there are no platform fees.
  - If the platform sets pricing, it pays £2 per monthly active account plus 0.25% + 10p per payout.
  - Card processing (1.5% + 20p, Area econ) is paid by the connected account under direct charges.
- **Host onboarding:** hosts go through Stripe's identity checks before they can take payments. That doubles as a trust signal, but adds friction for casual hosts.
- **Telegram:** physical goods and services may use any payment provider (Developer Terms s.6.1). Only digital goods need Stars.
- **Cancellations:** the 14-day cancellation right does not apply to "services related to leisure activities, if the contract provides for a specific date" (Consumer Contracts Regulations 2013 reg 28(1)(h), read). A clear refund policy (e.g. full refund up to 48 h before) is ours to set.

## Extra duties for paid group trips

| Duty | What applies | Source |
|---|---|---|
| Reasonable care and skill | Every service contract implies that the trader performs the service "with reasonable care and skill" | Consumer Rights Act 2015 s.49 (read) |
| Health and safety | The self-employed duty to others applies only to undertakings "of a prescribed description". Whether trip organising is prescribed is **UNVERIFIED** (likely not). Employers owe the s.3(1) duty. The common-law duty of care applies either way | HSWA 1974 s.3 (read) |
| Adventure activities | A licence is needed only to provide caving, climbing, remote trekking (moorland or above 600 m) or watersports on non-placid water **to under-18s for payment**. Adults-only is exempt, but use licensed or insured providers for these activities | HSE AALA pages (search) |
| Insurance | Employers' liability is compulsory once you employ someone (£5m minimum). Public liability is not on that list, but get it before paid trips (cost UNVERIFIED) | GOV.UK (read) |
| Online safety | Illegal-content risk assessment within 3 months of launch; reporting and blocking | Online Safety Act (Area 12) |
| Equality | No age filters on day trips (the holiday exception needs >24 h or an overnight stay) | Area 11 |

**Trip safety kit (≈4 h):**
- a public meeting point;
- host ID via Stripe onboarding;
- an attendee list shared with the host only;
- an emergency contact on file;
- a risk note per trip (heat, water, terrain, night);
- a weather-cancellation rule;
- in-app report and block;
- no meet-ups in private homes.

## Phase 3 implications

- **Payments stay off** (legal gates, CLAUDE.md).
- **Weekend test and Test C:** ask attendees how they split costs today and what went wrong. Log it in the results sheet notes.
- **The free-first scenario** in the workbook assumes the group-trip fee only starts after the gates clear.

## Risks / unknowns

- **Package status of weekend trips** where the app suggests accommodation but doesn't sell it: a solicitor's question, especially after April 2027.
- **Direct charges make the host the merchant**, so refunds and chargebacks are theirs. That may deter casual hosts. A venue as merchant is simpler.
- **The prescribed-undertakings list under HSWA s.3(2)** was not read here: UNVERIFIED.
