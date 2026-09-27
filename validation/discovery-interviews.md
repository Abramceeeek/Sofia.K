# Test E — B2B discovery interviews (5) and optional venue conversations (D34, D36)

**Postponed until v0 exists (D86).** It runs with a working demo after Test B, and before any B2B-specific build work. Its results feed the decision note `decisions/b2b-vs-consumer-first.md` (D40). The questions stay as they are; Claude adds a short demo section at the close before it runs. *(Was: runs first in Phase 3, D36.)*

**Goal:** learn whether hotels and tourism bodies already spend money or time helping guests and visitors find good things to do, who owns that budget, and what "better" would be worth. We are **not pitching and not selling** (no money can be taken until the money gates clear, CLAUDE.md).

**Founder hours:** ≈ 5.25
- recruiting ≈ 1.25 h;
- 5 × (15 min prep + 30 min call + 15 min notes) ≈ 3.75 h;
- checking a translated script for the Uzbek interviews, if you run them in Uzbek or Russian ≈ 0.25 h (Claude translates).
- **Optional venue conversations:** 3 × 40 min ≈ 2.0 h.

## Who (5 interviews)

| # | Type | Role to ask for |
|---|---|---|
| 1 | Independent or boutique hotel, London | Guest experience or front-of-house manager, head concierge |
| 2 | Serviced apartments or aparthotel operator, London | Guest services lead |
| 3 | Tourism body: a London borough visitor service, Business Improvement District, or destination organisation | Visitor experience or marketing lead |
| 4 | **Uzbekistan: travel agency sending clients to London** (D36, D49) | Owner or London product manager |
| 5 | **Uzbekistan: a second outbound agency**, or a tour operator selling London trips (D49) | Owner or London product manager |

**Both Uzbek interviews test one offer (D49):** London moment plans for the agency's clients, **at London prices** (£200–500 a month).
- Uzbek hotels and tour operators working inside Uzbekistan are **not pursued in year one**. They would need Uzbek cities curated first, at ~33% of UK prices (`decisions/city-expansion-gate.md`).
- How they would pay us is set out in `research/notes/20-uzbek-b2b-payments.md`: a GBP invoice paid by international card or SWIFT, with no Stripe presence in Uzbekistan needed.

Employers (staff wellbeing, team offsites) are the third B2B segment. They are not in these 5, so add 2 later if hotels and tourism look weak.

**Rules before outreach (CLAUDE.md gates):**
- Do it on personal time and personal devices, and **never use employer contacts or information**.
- Before approaching public bodies such as tourism boards or councils, check that your employer's secondary-employment rules don't treat that as a conflict.

**Recruiting:** warm introductions are fine here (they don't bias B2B answers the way friends bias consumer tests), plus LinkedIn. Message:

> Hi [name], I'm researching how hotels [or visitor services] help guests find things to do in London, as part of a small independent project. Could I ask you about how you handle it today, 25–30 minutes, no sales pitch? Happy to share what I learn across the conversations. — Abram

*For hotel staff contacts, add (D70):*
> If you're not the person who decides on guest services or the budget for them, could you introduce me to the manager or budget holder? A two-line email or WhatsApp intro is perfect.

**Shareable versions (D70):** `test-e-kit.md` has this script as a one-page call guide, a short message version that agencies can answer in writing (English, Russian, Uzbek), and the intro line. A published copy with copy buttons: https://claude.ai/artifact/LZQEYVFmjWUXXpVMLx7qu8.

Log each contact in `results-sheet.xlsx` → `Posts` (For = "B2B"), with minutes spent.

## Interview script (past behaviour only; no pitching until the close)

**Context (3 min)**
1. "What's your role, and roughly how many guests or visitors do you deal with in a week?"

**Last time (10 min)**
2. "Tell me about the last time a guest asked you what to do or where to go. What did they ask? What did you give them?"
3. "What happened afterwards? Did you hear how it went?"
4. "When did a recommendation last go wrong, or a guest come back disappointed? What happened?"

**What they use and spend today (8 min)**
5. "What do you use now: your own knowledge, printed guides, an app, partners, a concierge service? Who keeps it up to date?"
6. "Have you paid for anything like that in the last year: guides, concierge software, local partnerships, content? What did it cost, and who signed it off?"
7. "Do local venues or tour companies pay you, or give your guests discounts? How does that work?"

**How they judge it (5 min)**
8. "How do you know whether a recommendation was good? Do reviews, repeat stays or complaints show it?"
9. *Tourism bodies:* "What do you measure for visitors (spend, dwell time, spreading people beyond the hotspots)? What did you last commission for visitor experience, and how did the budget decision work?"

**Uzbek outbound-agency variant** (replace questions 2–9; ask in the language the contact prefers)
- "Tell me about the last client you sent to London. What did they do on their free days? How did they choose?"
- "What did they complain about or wish they'd known?"
- "Do you sell tours, guides or day plans in London? What do you pay for them, and what do you charge?"
- "What do you pay each month for tools or services such as booking systems, guides or marketing? Who approves it?"
- **Payment (past behaviour, Area 20):**
  - "How did you last pay a supplier in London or elsewhere abroad: card or bank transfer? A company card or a personal one? In which currency?"
  - "What did your bank or accountant need for that payment: a contract, an invoice, an acceptance act, anything else?"
  - "Has your accountant ever withheld tax on a payment to a foreign company?"
- **Record** card vs transfer, company vs personal card, currency, and the paperwork. They feed the UNVERIFIED items in Area 20.

**Close (only now, 3 min)**
10. Describe it in two sentences: "a planner that learns what makes each person feel good on a day out and plans around it (moments, not landmarks), with a personal plan for each guest."
11. "Who else should I talk to about this?"
12. "Would you be open to trying it with a few guests later, unpaid, when it exists?" **Record the exact answer.**

## What to record (results sheet → `Discovery`)

- Organisation type, role, date, and guests or visitors per week.
- Current solution, and **current spend (£ a month; 0 if none)**.
- **Budget owner named?** (Y/N)
- The strongest pain quote, verbatim.
- **Commitment:** none / introduction to the budget owner / agreed to an unpaid pilot.

**Read-out (confirmed, D57):** the B2B line is worth building toward if **≥ 2 of 5** already spend money or staff time on this, **and ≥ 2 of 5** give a commitment (an introduction or a pilot). Polite interest ("sounds great!") does not count.

## Optional: 3 venue conversations (venue partnerships)

**Who:** venues in Test C plans with quiet periods, such as a climbing wall, boat hire, a small gallery café, or a go-kart track.

**Questions:**
1. "When are you quiet? What did you try last time to fill those slots?"
2. "Do you do group or off-peak discounts now? Who books them, and how do they find you?"
3. "Do you pay any booking platforms or agents? What percentage?" (Online travel agents take 20–30%: Viator 20%, GetYourGuide 20–30%, search.)
4. **Close:** "Would you offer a group of 4–6 from a plan a discount on a quiet afternoon?"

**Record:** quiet slots, current discounts, current commission paid, and yes/no to a trial discount. This feeds the `Venues` tab (bookings per venue, commission, discount).
