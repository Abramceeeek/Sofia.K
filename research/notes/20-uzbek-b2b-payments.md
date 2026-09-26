# Area 20 — Getting paid by Uzbek agencies from a UK company (D49)

**Decision (proposed):**
- **Yes. A UK company can invoice Uzbek agencies without any Stripe presence in Uzbekistan.** Stripe only needs *our* business to be in a supported country (the UK). The customer can be anywhere its card works.
- **Invoice in GBP at London prices** (£200–500 a month, workbook `B2B`). The agency's bank converts from UZS, so Stripe's 2% conversion fee does not apply.
- **Offer two ways to pay on each invoice:**
  1. **Card** through Stripe Invoicing. This works with an Uzbek-issued **international Visa or Mastercard**; the domestic Humo and Uzcard networks will not work. Cost ≈ 3.6% of the invoice.
  2. **SWIFT bank transfer** to the company's UK business account, because a UK Stripe account cannot receive SWIFT. Cost ≈ £2 a payment on Wise Business, plus any intermediary bank charges.
- **Get an HMRC certificate of residence before the first Uzbek invoice.** Without one, the agency must withhold **20%** Uzbek tax. With one, the UK–Uzbekistan treaty should cut this to 0% if the plans count as business profits, or at most 5% if they count as royalties. **Which applies is UNVERIFIED; take professional advice.**
- **No UK VAT** on these B2B sales: they are outside its scope.
- **No money moves until the money gates, incorporation, the ICO fee and insurance are done** (CLAUDE.md).

## What a £350 monthly invoice leaves us (workbook `B2B` → "Outbound agencies")

| Route | Fees | Net, with certificate | Net, no certificate (20% withheld) |
|---|---|---|---|
| Card, invoiced in GBP | 3.15% + 20p card + 0.4% Invoicing | **£337** | £270 |
| Card, invoiced in USD (Stripe converts) | above + 2% | £330 | £264 |
| SWIFT in GBP to Wise Business | £2.16 per payment | **£348** | £278 |

- **Card** is easiest for the agency. **SWIFT** keeps about £10 more a month per client.
- **"Net" is before intermediary bank charges** on SWIFT, which are UNVERIFIED.
- **Alternative:** a gross-up clause ("prices are net of any withholding tax") moves the 20% onto the agency. That is harder to sell.

## Findings

| Question | Answer | Source (accessed 2026-09-26) |
|---|---|---|
| Stripe fee on non-UK cards (UK account) | "3.15% + 20p for international cards + 2% if currency conversion is required" | stripe.com/gb/pricing (fetched) |
| Stripe Invoicing fee | Starter **0.4%** per paid invoice; Plus 0.5% | stripe.com/gb/invoicing/pricing (fetched) |
| Can Stripe receive SWIFT for a UK account? | **No.** "…can accept domestic and international wire transfers (SWIFT): The United States" | docs.stripe.com/payments/bank-transfers (fetched) |
| Can Stripe be used from Uzbekistan? | No. Uzbekistan is not on Stripe's list of supported business countries | stripe.com/global (fetched) |
| SWIFT receiving fee, Wise Business | GBP SWIFT **£2.16** per payment; USD wire **$6.11**; £50 one-off for account details | wise.com/gb/pricing/business/receive (fetched) |
| Do Uzbek cards work abroad and online? | **Yes**, for international cards. KDB Visa Classic UZS: usable "abroad or for online payments in any currency". Mastercard "is used for traveling abroad, online payments, and international services" | kdb.uz (fetched); kun.uz, 16 Apr 2026 (fetched) |
| Humo and Uzcard | Domestic networks only. Co-badged Visa or Mastercard versions work abroad | 8b.world, finera.com (search only) |
| Uzbek withholding tax on services | Domestic rate 20% on "Royalties, services (including management, consulting services), rents, other income". The treaty rate applies only with "a duly formalised tax certificate" of residence. UK treaty royalties rate: 5 | PwC Tax Summaries, Uzbekistan WHT, last reviewed 27 Aug 2026 (fetched) |
| UK–Uzbekistan treaty | Art 7: business profits are "taxable only in that State unless the enterprise carries on business in the other Contracting State through a permanent establishment". Art 12: royalties are taxed at no more than 5%. Royalties include payment for "the use of … any copyright of literary, artistic or scientific work" | gov.uk, 1993 DTC as amended by the 2018 Protocol (fetched) |
| UK certificate of residence | Companies apply online. A new company that has not yet filed a return gives its directors, shareholders and why it is UK resident. No future dates. "The relevant overseas authority decides if relief … can be granted" | gov.uk "Apply for a certificate of residence", updated 26 Aug 2026 (fetched) |
| UK VAT | B2B general-rule services are "supplied where the customer belongs". Such services are "outside the scope of UK VAT". Keep evidence that the customer is a business abroad | HMRC VAT Notice 741A (fetched) |
| Uzbek VAT | 12%. Foreign firms selling **e-services to Uzbek individuals** must register for Uzbek VAT | PwC Tax Summaries, Uzbekistan other taxes (fetched) |
| Uzbek currency rules | Individuals: current international transactions "without restrictions". Companies buy foreign currency through a bank application, and the purchased currency may be used only for the purpose stated | Azizov & Partners memo (fetched) |

## UNVERIFIED — check before the first Uzbek invoice

1. **Services or royalties?**
   - A plan made for a client looks like a service: 0% under Art 7 with the certificate.
   - A licence to reuse our moment library looks like a royalty: up to 5%.
   - Write the contract as a service, and have an adviser confirm.
2. **Can an Uzbek company pay a foreign service by corporate card?** The sources above cover personal cards. If an owner pays with a personal card, the tax and currency rules on their side are theirs, but we still invoice the company.
3. **What paperwork the agency's bank needs to send foreign currency.** It is probably a contract, an invoice and an acceptance act (a signed confirmation that the service was delivered). Ask in Test E.
4. **Whether the agency must self-account for Uzbek VAT** (a reverse charge) on a service bought from abroad. This adds 12% to its cost if it cannot reclaim it.
5. **Whether Stripe's risk checks decline Uzbek-issued cards.** Test this with the first real invoice once the gates clear.
6. **Intermediary bank charges on SWIFT**, and card limits for payments abroad.

**Never sell directly to Uzbek consumers** without first registering for Uzbek VAT (PwC above).

## Hours

- **Now:** reading this note takes ≈ 0.25 h. Test E now asks how the agency last paid a foreign supplier (`validation/discovery-interviews.md`), which adds no time.
- **At the first Uzbek client** (after the gates and incorporation), ≈ 2.5 h one-off:
  - Stripe Invoicing ≈ 0.5 h;
  - Wise Business account ≈ 0.5 h (£50);
  - HMRC certificate ≈ 0.5 h;
  - adviser call ≈ 1 h (fee UNVERIFIED).
