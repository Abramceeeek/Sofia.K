# Recruiting now: what's left, in order (D105)

*28 Sep. The week-of-12-Oct tasks are pulled forward to this week. Your hours are GUESSES. Anything marked **(my judgement)** is opinion. Facts come from `research/sources.csv`.*

## Blockers before the first Test A chat (≈ 2.5 h of yours)

| # | Blocker | Why it blocks | Your time |
|---|---|---|---|
| 1 | **ICO data protection fee: do the self-assessment** on ico.org.uk. If it says you must pay: tier 1 is £52 a year (£47 by direct debit) | Sole traders who use personal information must pay unless exempt (ICO), and the study collects names, numbers and voice notes. **It costs money, so it's your call.** `CLAUDE.md` lists the fee "before the first paid client"; the self-assessment says whether the study already needs it | 0.2 |
| 2 | **Send me your surname (or "Abram" only) and a contact email for the study** | The consent form and privacy notice still say [surname] and [email] | 0.1 |
| 3 | **Confirm the WhatsApp checklist** (§1) | The chats run there | 0.25 |
| 4 | **Study sign-up form** (§4A), or take sign-ups by message only | Post 1 needs somewhere to send people | 0.3 |
| 5 | **Paste the swipe results table** (§2) and lock the 16 | Test A §3 sends the 16. Changing them after the first chat breaks comparability | 0.1 |
| 6 | **Seed moment 1 walk and photo** (South Kensington), to finish the example shot card | Test A §6 sends it (`shot-card-example.md` still has [exit], [route], [spot]…) | 0.5 |
| 7 | **Copy and check the real brief and generic plan** (§6) | Test B plans follow 1–3 days after the chat | 0.25 |
| 8 | **Check the one list** (§3) | The first chat uses all of it | 0.5 |

**Not blocking recruitment:**
- the Test D landing page (a different week or different groups, §4B);
- the Apple policy and IP-clause check (it gates money and external TestFlight builds; research and unpaid tests can go ahead, `CLAUDE.md`);
- the Area 18 review.

## 1. WhatsApp Business: confirm each, and I'll mark the set-up done

- [ ] **The second number** is on your personal phone (never the work phone) and used only for the study.
- [ ] **Business profile:** name "Days out that fit you (research)"; description "A research study by Abram in London. Nothing is sold." (suggested wording)
- [ ] **Greeting message** (to new chats): *"Hi, thanks for getting in touch. This is Abram's number for the 'days out that fit you' study. I'll reply within a few hours. In an emergency, call 999."*
- [ ] **Away message** (outside the hours you set, e.g. your working hours): *"Thanks for your message. I reply within a few hours. In an emergency, call 999."* It never promises a faster reply (`CLAUDE.md` safety rule).
- [ ] **Quick replies** (the script's fixed wording, `interview-script.md`):
  - `/consent`: the consent form;
  - `/start`: §0;
  - `/best`: §1;
  - `/why`: §2;
  - `/swipe`: §3 intro;
  - `/tot`: §4 intro;
  - `/fields`: §5.7;
  - `/photo`: §6;
  - `/readback`: §7;
  - `/survey`: §8;
  - `/more`: "Is there anything else you'd like to add about that?";
  - `/health`: "Thanks — I don't need health details, so I'll leave that out.";
  - `/plans`: the Test B message;
  - `/rate`: the Test C rating prompt.
- [ ] **Labels:**
  - Consented
  - Test A done
  - Plans sent
  - Day done
  - Friends & family (D43)
  - Withdrawn
- [ ] **Chat backup:** turn backup off for this account, so voice notes you delete after transcribing don't live on in a backup.
- [ ] **Test it:** message the number from your personal WhatsApp, and check that the greeting arrives with the 999 line.

*WhatsApp lists greeting and away messages, quick replies and labels as Business app features (business.whatsapp.com, read 26 Sep).*

## 2. The 16 swipe places

**What to paste:** open `<URL>/results` with your admin token. I never see or handle the token. Paste the ranked table: place, people who have been, familiarity, divisiveness, score and the low-n flag, plus the number of people counted. That's all aggregate counts, no personal data. The page counts only people who answered at least 10 places, and flags places with fewer than 5 people who have been.

**The rule:**
- **No low-n flag in the top 16:** take them. The page also warns if a taste feature is covered by fewer than 2 places.
- **Some are flagged:** use the provisional 16 below.

**Provisional 16 = the current list** in `interview-script.md` §3. It's already in the results sheet and the Brain, and 7 of the 16 have cards.
- **More answers needed** (my judgement, firmed up once you paste): a place needs about 5 ÷ familiarity people. The least familiar items (Columbia Road, the Hampstead ponds) might be known to about 3 in 10, so that means **about 17 people who each answer 10+ places**.
- **Lock the 16 before the first chat,** even if provisional. Swapping items mid-test breaks comparability.

## 3. One list to check (≈ 30 min)

1. **Aspiration question (§5.7):** *"Which of these fields inspire you? Pick any, or none. (Optional. We only use it to add places tied to what inspires you.)"*
   - Options: Finance & tech / Food / History & culture / Nature / None of these.
   - **Ready moments per field:** Finance & tech 6, Food 7, History & culture 12, Nature 12 (all above the minimum of 2).
2. **Consent form:** fill [surname] and [email]. Check:
   - the 999 line and "a person replies within a few hours";
   - the AI disclosure;
   - voice notes deleted on transcription (30-day opt-in);
   - deletion within 14 days.
3. **Privacy notice:** fill [date], [surname] and [email]. Check that retention to 31 Mar 2027 is right, and the ICO line.
4. **§0 opening:** "I run this chat myself; AI helps me write up a summary afterwards".
5. **§1–§2:** the best hour, and why they travel (up to 2).
6. **§3:** the 16 places, once locked.
7. **§4:** the 10 this-or-that tasks, including the weather wording (D95).
8. **§5:** budget bands, company, morning or night, activity, where they grew up, "foods or drinks you avoid" (no allergy question), the fields question.
9. **§6:** the photo question and the shot card, once the walk is done.
10. **§7–§9:** read-back, survey, past behaviour.
11. **Test B:** "Go with your gut: which would you rather do, Plan 1 or Plan 2?". Enter the choice as A or B (Plan 1 = A).
12. **Test C:** the 1–5 rating after each stop, the share link, and the safety line.
13. **Results sheet:** copy it to `validation/raw/results.xlsx` (never committed).
14. **Post 1 and the friends-and-family message** (§5 below).

## 4. Sign-up form, landing page and analytics

### A. Study sign-up form (needed now, about 20 min)

1. **On tally.so** (free plan), create a form called "Days out that fit you: study sign-up".
2. **Add the fields:**
   - first name;
   - WhatsApp number;
   - "How do you know me?" (I don't / a friend of a friend / I know you);
   - a required tick box: "I'm 18 or over".
3. **Add a hidden field `src`.** Tally fills hidden fields from the link, e.g. `…?src=fb-hiking` (Tally help, read 26 Sep).
4. **Publish, and send me the link.** I'll put it in Post 1 with one `?src=` per group.
5. **Consent comes in the chat**, as now: send `/consent` before the first question and keep their "I agree".

### B. Test D landing page (a different week, about 40 min)

1. **Waitlist form (Tally):**
   - fields: email, and an optional "anything you'd want from it?";
   - hidden fields: `arm`, `choice`, `price`, `src`, `ref`;
   - a consent line linking to the privacy page.
2. **GoatCounter:** create a site (free for reasonable use, no cookies; read 26 Sep).
3. **Send me:**
   - the waitlist form link;
   - the GoatCounter code;
   - your contact email and surname.

   I'll fill in `index.html` and `privacy.html` and push them.
4. **Render:** New → Static Site → this repository and branch, publish directory `validation/test-d-landing`, no build command. Render lists static sites as free (read 26 Sep).
5. **Test both arms:** open the page twice in a private window, and check that the form receives `arm`, `choice`, `price`, `src` and `ref`.

## 5. Recruitment posts and where to put them

**Post 1 (Tests A–C)** is in `recruitment-posts.md`. It's unchanged except for the link. Put the Tally link at the end, one per group: `https://tally.so/r/<id>?src=<group>`.

**Where:** the channels from the weekend test:
- uni and city Facebook groups you're already in;
- UK travel subreddits (read each one's self-promotion rules first, and ask the mods where required);
- hiking and photography groups.

**How (my judgement):**
- 4–6 groups over 2–3 evenings;
- one post per group;
- reply to every comment;
- log each post (date, group, minutes, sign-ups) in the results sheet's Posts tab.

**The target:** 14 people, of whom 12 are strangers.

**Friends and family:** use the separate message in `recruitment-posts.md` and tag them `ff`. They never count towards the thresholds.

**Post 2 (Test D)** goes in a different week or to different groups, once the landing page is live.

## 6. The real brief and generic plan (before the first chat, about 15 min)

1. **Copy the brief:** `brain/data/testb/brief.example.yaml` → `validation/raw/testb/brief.yaml`.
   - It's Charing Cross, 12:00–17:00, a Saturday, 4 stops including lunch, £40.
   - Before each batch of plans, **set `sunset`** to the coming Saturday:

     | Saturday | Sunset |
     |---|---|
     | 3 Oct | 18:36 |
     | 10 Oct | 18:20 |
     | 17 Oct | 18:05 |
     | 24 Oct | 17:50 |
     | 31 Oct | 16:37 |
     | 7 Nov | 16:25 |

     Before 25 Oct the day ends before sunset, and the "Best: Sunset" lines drop out by themselves.
2. **Copy the generic plan:** `brain/data/testb/generic.example.yaml` → `validation/raw/testb/generic.yaml`, and check its times and prices.
   - The route: the National Gallery, lunch at Borough Market, Tate Modern and its Level 10 view, then the South Bank past the London Eye.
   - It works on a Saturday.
3. **Test B plans leave out the London Transport Museum** (booking plus £18.50; it stays in the app). **The Courtauld is in:** "Open daily, 10:00–18:00" on its official site.

## 7. The new schedule (proposed; confirm the checkpoint)

| When | What | Your hours |
|---|---|---|
| This week (to 4 Oct) | Blockers 1–8 (≈2.5); Post 1 goes out Thu–Sun (2.0) | ≈ 4.5 more (2.2 logged so far) |
| Week of 5 Oct | Test A chats (4.0), transcripts and read-backs (1.0), first Test B plans (1.5), Area 18 review (0.5) | ≈ 7.0 |
| Week of 12 Oct | The last chats; Test B plans (2.0); Test C follow-ups (1.0); a second recruitment round **only if** fewer than 12 strangers | ≈ 7.0, or more with the second round |
| Week of 19 Oct | The last Test B plans; **Test B reports (was ~2 Nov)**; Test C follow-ups; **swipe CSVs by Fri 23 Oct** | ≈ 5.0 |
| 26 Oct – 1 Nov | Test C follow-ups and data entry; Brain code review | ≈ 5.0 |
| **Week of 2 Nov** | **Checkpoint 3 (was the week of 9 Nov):** analysis and `results.md` | ≈ 2.5 |

**Why not earlier (my judgement):** each person's Test C runs up to 2 weeks after their plans. With the last plans around 19 Oct, the follow-ups end around 2 Nov.
