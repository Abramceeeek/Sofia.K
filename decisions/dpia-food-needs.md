# DPIA (DRAFT): food needs in ODYS (8 Nov 2026; m223; corrected 9 Nov, m232)

**Status: draft. Unsigned, and not for Claude to sign.** **A UK data-protection solicitor checks it before any user sees the feature** (Abram, m224); Abram signs after that. Food-need collection stays switched off and nothing is stored (tested). **Not legal advice.**

> **Corrected by Abram's decision 5 (m224).** m223 called every food need special category data. The classification below replaces that:
> - halal and kosher **potentially reveal religious belief**;
> - allergies are **health data** and are **not stored**;
> - vegetarian, vegan and alcohol-free venues are **assessed on context**.
>
> The same high security applies to all of them. The Article 6(1)(a) basis and the Article 9(2)(a) condition are now set out separately. The storage and server sections now match on-device filtering, as `food-preferences-and-privacy.md` now does too.

**Its structure** follows UK GDPR Article 35(7) (legislation.gov.uk/eur/2016/679/article/35, read 8 Nov 2026). An assessment must contain at least:
- (a) "a systematic description of the envisaged processing operations and the purposes";
- (b) necessity and proportionality;
- (c) the risks to people's rights and freedoms;
- (d) the measures to address them.

The ICO's own DPIA pages refused automated reading in this session (403), so its template's step headings aren't quoted here. Compare this draft against the ICO template before sign-off.

## What each food need is (m232; Abram's classification, m224)

Article 9(1) prohibits processing personal data **revealing** "religious or philosophical beliefs", and **"data concerning health"**, unless an Article 9(2) condition applies (legislation.gov.uk/eur/2016/679/article/9, read 8 and 9 Nov 2026).

| Class | Needs | What it is | How ODYS treats it |
|---|---|---|---|
| **1. Potentially revealing religious belief** | Halal; kosher; "certified places only" for either | Special category: it can reveal "religious or philosophical beliefs". The ICO treats an inference as special category data when you treat someone differently because of it (ICO guidance, read through search extracts on 7 Nov: `food-preferences-and-privacy.md`, section 1). ODYS would, by design: different food suggestions | Article 9(2)(a) explicit consent, with an Article 6(1)(a) basis (below) |
| **2. Data concerning health** | Allergies, intolerances, coeliac or other medical diets | Special category: "data concerning health" | **Not asked and not stored.** Instead, everyone gets the same line on every food stop: ask the venue about allergens. So ODYS never knows who has an allergy |
| **3. Preferences assessed on context** | Vegetarian; vegan; "places not centred on alcohol" | **May or may not reveal a belief.** For one person it's a taste or a health habit. For another it follows from religion (no alcohol; vegetarian for some faiths), or from a philosophical belief: ethical veganism has been held to be one in an employment tribunal (UNVERIFIED: not read in this session; for the solicitor). **ODYS can't tell which, and asking why would itself collect the belief** | Never asked why. Because the reason can't be known, the same consent standard and safeguards as class 1 apply (class 4) |
| **4. Safeguards applied more broadly** | All of classes 1 and 3 | An internal choice, not a legal classification | The same high security for every food need: phone only, the same consent screen, one purpose, no analytics, the purpose guard in code. So a mistake about which class a need is in costs nothing |

**For the solicitor:** whether one consent screen at the explicit standard is right for class 3 too, or whether class 3 should sit on Article 6(1)(a) alone. The proposal uses one screen, so the person never has to say why they choose a need.

## Why a DPIA

- **Class 1 is special category data**, and class 3 can be.
- **Article 35(1)** requires a DPIA before processing "likely to result in a high risk", "in particular using new technologies". **35(3)(b)** requires one for "processing on a large scale" of special category data.
- ODYS isn't large-scale yet. But it would be **a new feature, built on a personal model, offered to strangers**, and the plan is to grow. So the DPIA comes **before** building, as product-direction.md and m208 already said.
- **Storing it only on the phone doesn't take it out of UK GDPR** (Abram, 7 Nov). ODYS designs the processing, decides what the app does with the data, and would be the controller of that design. Phone-only storage reduces the risk; it doesn't remove the duty.

## (a) The processing, systematically

| | |
|---|---|
| **Data** | The needs a person chooses from a fixed list: halal, kosher (class 1); vegetarian, vegan, "places not centred on alcohol" (class 3). For halal and kosher, also "certified places only" (yes/no). **No free text, no reason, no allergies** (class 2 isn't collected). The consent record: the text version, the date, and the basis and condition it records (Article 6(1)(a) consent; Article 9(2)(a) explicit consent). |
| **Whose** | ODYS users who choose to turn it on: adults (the consent screen asks "I'm 18 or over"). |
| **Purpose (one)** | To show, on the person's own food stops, whether each venue fits their needs and on what evidence. **Never:** matching with other people, advertising, ranking people, analytics, model training or research statistics. |
| **Where it lives (recommended)** | **On the phone only.** iPhone: a file with "complete" protection (readable only while the phone is unlocked), excluded from backups (`isExcludedFromBackup`, set on each save; Apple calls this guidance, not a guarantee). Android: a file sealed with an Android Keystore key in `noBackupFilesDir`, as the install token now is (m227). **The backup exclusion is a deliberate exception to m226** (no blanket iPhone backup exclusion: trips stay in backups). Food needs are special category data, five taps to choose again, and a backup restored on another phone is exactly risk 1. After a restore, the app asks again; it never guesses. |
| **What the server sees (recommended)** | **Nothing about the need.** The Brain sends every food venue's evidence for every need (certified by whom, "the venue says", "a community map says", unknown), and **the phone** picks the lines to show and the order. So the need never leaves the phone, is never in a request or a log, and the server can't infer it. (The alternative, sending the need with each plan request and storing nothing, still processes special category data on the server and lands in request logs. Not recommended.) |
| **Retention** | Until the person switches it off, deletes their data, or deletes the app. |
| **Who can see it** | Only the person, on their phone. No ODYS staff, no helper, no processor. |
| **Sources of venue evidence** | A certifier's own public listing, checked by hand per venue with the date (HMC's outlet list first; its FAQ says it doesn't certify stunned meat, so certifiers' standards differ and ODYS names the certifier, never just "halal"); the venue's own words with the URL; community map tags, labelled as such (m208). |

## (b) Necessity and proportionality

- **Necessary for the purpose:** a person can't get food stops that fit their needs unless the app knows them. Fixed choices, not free text, keep it to what's needed.
- **Less intrusive options, considered:**
  1. Show every venue's evidence to everyone and let people read it. Nothing is stored. This is the **baseline**, and the "for everyone" allergy line is built this way.
  2. Phone-only needs, filtered on the phone (recommended).
  3. Server-side storage. **Rejected:** no benefit over 2 for one person's own suggestions.
- **Lawful basis, identified separately (m224; legislation.gov.uk, read 9 Nov 2026):**
  1. **Article 6 basis: consent, Article 6(1)(a).** Processing is lawful only if at least one Article 6(1) point applies. Point (a): "the data subject has given consent to the processing of his or her personal data for one or more specific purposes". The specific purpose here is the person's own food suggestions. This basis covers every food need (classes 1 and 3).
  2. **Article 9 condition: explicit consent, Article 9(2)(a).** It lifts the Article 9(1) prohibition when the person has given explicit consent for one or more specified purposes. **In the UK, Article 9(2) now opens "Paragraph 1 shall not apply if [the processing is based on Article 6(1) and] …"**, words inserted by the Data (Use and Access) Act 2025, in force 20 Aug 2025. So the Article 9 condition never stands alone: it needs basis 1 as well. This condition is needed for class 1, and for class 3 whenever the need reveals a belief.
  3. **Recorded apart:** the consent record names both, the Article 6(1)(a) consent and the Article 9(2)(a) explicit consent, with the text version and the date. A withdrawal ends both at once.
- **Consent is separate and explicit:**
  - its own screen, not bundled with the general consent;
  - one specified purpose;
  - "I agree: use my food needs" / "Not now";
  - versioned text, recorded on the phone with the date.
- **Withdrawal** must be "as easy to withdraw as to give" (Article 7(3), legislation.gov.uk/eur/2016/679/article/7). One switch in You deletes the needs from the phone at once. The person is told this before agreeing.
- **Allergies are never stored.** Instead, every food stop shows everyone the same line: always ask the venue about allergens. That avoids holding health data at all, and it's safer: a venue's allergen information changes, and ODYS can't check it.

## (c) Risks to people

| # | Risk | Likelihood (before measures) | Severity |
|---|---|---|---|
| 1 | Someone else sees the person's religion or health (shoulder, shared phone, a backup restored elsewhere) | possible | serious |
| 2 | The need reaches the server or logs and is breached, or is seen by staff | possible (if sent with requests) | serious |
| 3 | The need is reused for another purpose (matching, ads, statistics) | possible over time | serious |
| 4 | **Wrong evidence:** "certified" when a listing has lapsed, or the venue's words are wrong, and someone eats against their beliefs | likely without care | serious (to the person) |
| 5 | Certifiers' standards differ (stunning), and ODYS appears to judge which is "proper" | possible | moderate |
| 6 | Allergy harm from relying on ODYS | possible | **severe** |
| 7 | Consent isn't free (feels required), or is hard to withdraw | unlikely | moderate |
| 8 | A child uses it | unlikely | moderate |
| 9 | Inference from behaviour (e.g. always skipping some venues), even without the stated need | possible | moderate |
| 10 | **Misclassifying a need:** treating a class 3 choice as a plain preference when, for this person, it reveals their religion or a belief | possible | serious |

## (d) Measures, and what's left

| # | Measures | Residual |
|---|---|---|
| 1 | Phone-only. iPhone "complete" protection plus excluded from backup; Android Keystore-encrypted, no backup. Nothing about it on shared screens (no lock-screen or notification text) | low |
| 2 | **The need never leaves the phone** (on-device filtering). A test that no request or schema carries it. Already in place: `test_food_needs_are_never_stored_until_their_dpia` guards the profile and user tables, and the old free-text "foods you avoid" is now dropped, never stored | low |
| 3 | One purpose in code: `food.py`'s purpose guard refuses any other use (`PurposeError`, m208). No analytics events about it. A CLAUDE.md rule | low |
| 4 | Status lines say **who** said it and **when it was checked**. "Certified" needs the certifier's own listing with a date; it's flagged after 90 days (GUESS). "Strict" shows certified-and-current only (m208) | medium: listings can lapse between checks, so the line always says "checked on …" |
| 5 | Name the certifier; never rank certifiers. A later option lets the person choose which certifiers they accept | low |
| 6 | **No allergy storage**, and the allergen line for everyone on every food stop | low (the venue remains responsible) |
| 7 | Separate, optional screen. "Not now" is equal. Nothing else in the app changes if declined. Withdraw is one switch | low |
| 8 | ODYS is for adults: the consent screen requires "I'm 18 or over" (`FirstRunViews.swift`, both apps) | low |
| 9 | No behavioural inference about food: skips and ratings are never mapped to a diet or belief, and the model has no feature for it | low |
| 10 | Every food need gets class 1's safeguards and consent standard (class 4), and no one is asked why. So a wrong class changes nothing about how the need is protected | low |

**Consultation (to do).** Ask a few people who would use halal or kosher filters how they'd want it worded and which certifiers they trust (the friends' round or after). Ask HMC before any automated use of its directory.

**Review and sign-off (to do; nothing is signed).**
1. **A UK data-protection solicitor reviews this draft before any user** (Abram, m224). Questions for them:
   - the class 3 question above;
   - whether one screen can carry both the Article 6(1)(a) consent and the Article 9(2)(a) explicit consent;
   - the wording of the consent screen (`food-preferences-and-privacy.md`, section 5);
   - the ethical-veganism point (UNVERIFIED here).
2. Then Abram, as the decision-maker, records the outcome, any residual risk accepted, and the review date (on launch, then yearly).
3. The privacy notice gets its own section (~0.5 h).
4. If a high residual risk remained, the ICO would have to be consulted before processing (Article 36). On the measures above, none is expected to remain high.

## What's built and what isn't

- **Built (safe, no persistence):**
  - the evidence model and the purpose guard (`brain/src/brain/food.py`, m208);
  - the guard test above;
  - the Brain now drops `foods_avoided` (D19's free text, unasked since D123) instead of storing it;
  - both apps' profiles no longer carry the field.
- **Not built until sign-off:** the screen, the consent, the phone storage and the on-device filtering (both apps ~5 h, after decisions 1–4 in `decisions/food-preferences-and-privacy.md`).
- **The old free-text field:** a count-only audit and a deletion plan, built and tested (m233, `decisions/foods-avoided-audit.md`). **Don't use the admin export to check:** it would show the values. Note: build 91 and Android 21 still send the field with every profile save, so it can come back until the branch Brain is live.

**Hours:** Claude ~2 h. Abram: read and decide (~1 h), then sign off, or send it to a solicitor.
