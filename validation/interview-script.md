# Host script — Tests A, B and C (WhatsApp Business, Wizard of Oz)

> **Status (D63):** **in use.** Tests A–C run by hand in a chat, with Checkpoint 3 in the week of 2 Nov (D106). The app reuses this wording later (`brain/data/onboarding.yaml`).

**Rules for the host (Abram):**
- **One question per message.** Wait for the answer. Never interrupt a voice note.
- **After each open answer, send:** "Is there anything else you'd like to add about that?"
- **Don't pitch, lead or praise answers** ("great!"). Neutral acknowledgements only: "Thanks", "Got it".
- **Follow-up probes:** use only the probes listed here. Note any improvisation in the results sheet.
- **Timestamps:** WhatsApp records them; completion time = first message → last survey answer.
- **Health and allergy details:** if someone volunteers them, reply "Thanks — I don't need health details, so I'll leave that out." Don't record them.

---

## 0. Start (after the consent form is signed)

> Hi [name], I'm Abram. Thanks for helping. I wanted to bring some of the best experiences I've had in London to other people, and to find out what makes a day out good *for you*.
>
> I'll ask a few questions, one at a time. You can answer by **voice note or typing**, whichever you like, and switch any time. There's no time limit. It usually takes 20–30 minutes and can be spread over the day.
>
> I run this chat myself; AI helps me write up a summary afterwards, which I'll show you to check.
>
> Voice or typing to start with?

Record the first mode (D4).

## 1. Best hour

> Tell me about the best hour of your last trip or day out. Where were you, what was happening, how did it feel?

**Probe, once each, only if they come up:**
- **crowds / queues** → "How much do crowds or queues affect a day for you?"
- **heat / weather** → "What does the weather do to a day out for you?"
- **food** → "What makes food on a day out worth it for you?"
- **the journey there** → "Was getting there part of it?"

## 2. Why they travel (tap up to 2; Area 15)

> Which of these is most often *why* you go out or travel? Pick up to two.
>
> 1 Switch off and rest · 2 Time with people I care about · 3 Discover something new · 4 Nature and being outdoors · 5 Culture and history · 6 Food

## 3. Places you've been (swipe; Area 2)

> I'll send 16 London places. For each, reply **1 Loved it · 2 It was fine · 3 Didn't enjoy it · 4 Haven't been**. Numbers are fine.

**Send one per message.** After the first "Loved it" and the first "Didn't enjoy it", ask once: "What made it that way?"

**Proposed items (Abram to confirm; chosen to split people):**
1. Big Ben and Parliament Square
2. Uber Boat on the Thames
3. Borough Market
4. British Museum
5. IFS Cloud Cable Car
6. Hyde Park
7. Camden Market
8. Tate Modern Turbine Hall
9. Sky Garden
10. Columbia Road Flower Market (Sunday)
11. The view from the top of Greenwich Park
12. Walking from South Kensington tube to the Natural History Museum
13. Primrose Hill at sunset
14. Brick Lane for food
15. Hampstead Heath ponds (swimming)
16. Regent's Canal walk from Little Venice

## 4. This or that (10 tasks; `conjoint/design.csv`)

> Now 10 quick ones. Two made-up day plans each time. Just reply **A or B**: which day would you rather have?

Send each task exactly as in `design.csv`, with plan A first, e.g.:

> **Task 1**
> **A:** longest transfer 15 min · cold but dry at the outdoor stops · 5 stops, packed · mostly quiet · £60 per person · about 3 km walking
> **B:** longest transfer 30 min · mild and dry at the outdoor stops · 3 stops, relaxed · busy at 2 stops · £60 per person · about 8 km walking

*If asked what the weather means (D95):* mild and dry ≈ 15°C, no rain; cold but dry ≈ 5°C, no rain; rainy = showers on and off.

No "why" questions here. Speed is the point.

## 5. A bit about you (all optional; ask for what's needed, not the sensitive category)

1. "Roughly what do you like to spend on a day out, per person?" (under £20 / £20–40 / £40–70 / more)
2. "Who do you usually go with?" (solo / friends / partner / family)
3. "Morning person or night person?"
4. "How active do you like a day to be?" (gentle / medium / full-on)
5. "What kind of place did you grow up in? Big city, town, coast or countryside?" *(Optional. Only used to guess what will feel new to you; Area 16.)*
6. "**Any foods or drinks you avoid?** *(Optional — only used to choose food stops, and you can skip it.)*" (D19; no allergy question)
7. "**Which of these fields inspire you? Pick any, or none.** *(Optional. We only use it to add places tied to what inspires you.)*"
   - Finance & tech / Food / History & culture / Nature / None of these (D77; art & design dropped for Test B, D83)
   - Send it as a list and let them reply with the names.
   - It asks about interests, never a job or employer.
   - Enter the answer in the results sheet → Participants → **column AG**, e.g. "food, nature". Enter "none" for none of these; leave it blank if they skip.

## 6. Photos (D16)

> How much do photos and sharing matter on your trips? 1 (not at all) – 5 (a lot)

Then send **the example shot card** (`shot-card-example.md`: Waterloo Bridge at sunset, where to stand, what to frame, when; text only, the same for everyone, D106):

> If a plan came with a card like this, would it make you more likely to go? 1 (no) – 5 (definitely)

## 7. Read-back (Area 1)

Within a few hours, send a short summary: what they love, avoid and care about, drafted from the transcript by an LLM and checked by Abram.

> Here's what I heard. Did I get that right? Anything to fix or add?

Their corrections count as data. **Completion = they reply to the read-back.**

## 8. Survey (1–5 and open)

1. "I felt understood." 1 (not at all) – 5 (completely)
2. "It felt like talking to a person, not filling in a form." 1–5
3. "Was anything intrusive or tedious?" (open)

## 9. Past behaviour (no pitching; kickoff interview script)

1. "Tell me about the last trip or day out you planned. How did you choose what to do?"
2. "What did you spend on it? Was it worth it?"
3. "What's a day out you'd happily repeat? Why?"

---

## Test B — two plans (send 1–3 days later)

**Trip intent first (Area 15; stored with the plan, D27):**
> For the plan: is this day more about recharging or exploring? Who might come? Anything you'd want in it for sure?

Then send the two plans, labelled **Plan 1 and Plan 2** from the results sheet (A → 1, B → 2; never say which is personalised). Numbers keep them apart from the A/B choices in Test A (D97):

> Here are two plans for the same kind of day. **Go with your gut: which would you rather do, Plan 1 or Plan 2?** No need to analyse them; a line on why is plenty.
> Then for each: "This plan fits me" 1–5.

*For you, not the participant (D100):* friends in the dry run wrote long, structured comparisons. Ask for a quick gut answer, and read a long, polished "why" with care: it may be AI-assisted. The choice still counts. Add "(possibly AI-assisted)" at the end of their "Why (open)" cell on the TestB tab, and don't quote those answers as evidence of what people felt. Enter the choice as A or B: Plan 1 = A, Plan 2 = B.

## Test C — the real day

After Test B, send the personalised plan. If they strongly preferred the other, let them choose and record which.

> Want to use it on a real day? If you do:
> - after each stop, send me one number, 1–5 (how it felt). Nothing else needed.
> - **Bringing someone?** Forward them this: "I'm trying a day plan made for me — you can get one too: [link?ref=P07]".

**After the shot-card stop** (send when they rate it):
> Got a shot you like? Share it if you want. If friends ask, this link lets them try it: [link?ref=P07]

**The day after:**
1. "Would you go again?" (yes / maybe / no)
2. "How did it feel overall?" (open)
3. "Did you invite anyone? How many?"
4. "Did you share a photo? Where?" (we never ask for the photo itself)

**Over the next 2 weeks:** don't prompt. Log any request for a second plan (date and wording).

## Close (only now)

> Thanks — that really helps. I'm building this properly if it works. If you'd like to follow along, here's the waitlist: [link?src=participant]
