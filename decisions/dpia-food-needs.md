# DPIA (DRAFT): food needs in ODYS (8 Nov 2026; m223)

**Status: draft for Abram. Not signed off. Nothing here is built for real users** (m215 decision 4). A solicitor or the DPIA review checks it before any build. **Not legal advice.**

**Its structure** follows UK GDPR Article 35(7) (legislation.gov.uk/eur/2016/679/article/35, read 8 Nov 2026). An assessment must contain at least:
- (a) "a systematic description of the envisaged processing operations and the purposes";
- (b) necessity and proportionality;
- (c) the risks to people's rights and freedoms;
- (d) the measures to address them.

The ICO's own DPIA pages refused automated reading in this session (403), so its template's step headings aren't quoted here. Compare this draft against the ICO template before sign-off.

## Why a DPIA

- **It's special category data.** Halal or kosher can reveal "religious or philosophical beliefs", and an allergy or a medical diet is "data concerning health" (Article 9(1), legislation.gov.uk/eur/2016/679/article/9, read 8 Nov).
- **Article 35(1)** requires a DPIA before processing "likely to result in a high risk", "in particular using new technologies". **35(3)(b)** requires one for "processing on a large scale" of special category data.
- ODYS isn't large-scale yet. But it would be **a new feature, built on a personal model, offered to strangers**, and the plan is to grow. So the DPIA comes **before** building, as product-direction.md and m208 already said.
- **Storing it only on the phone doesn't take it out of UK GDPR** (Abram, 7 Nov). ODYS designs the processing, decides what the app does with the data, and would be the controller of that design. Phone-only storage reduces the risk; it doesn't remove the duty.

## (a) The processing, systematically

| | |
|---|---|
| **Data** | The needs a person chooses from a fixed list: halal, kosher, vegetarian, vegan, and "places not centred on alcohol". For halal and kosher, also "certified places only" (yes/no). **No free text. No allergies stored** (see below). The consent record: text version and date. |
| **Whose** | ODYS users who choose to turn it on: adults (the consent screen asks "I'm 18 or over"). |
| **Purpose (one)** | To show, on the person's own food stops, whether each venue fits their needs and on what evidence. **Never:** matching with other people, advertising, ranking people, analytics, model training or research statistics. |
| **Where it lives (recommended)** | **On the phone only.** iPhone: a file with "complete" protection (readable only while the phone is unlocked) and excluded from backups (`isExcludedFromBackup`, set on each save; Apple calls this guidance, not a guarantee). Android: a file in app storage, encrypted with a key in the Android Keystore, already excluded from backup and transfer (`data_extraction_rules.xml`). |
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
- **Lawful basis (to decide; m208):**
  - **Article 9 condition:** explicit consent, "for one or more specified purposes" (Article 9(2)(a)). As amended in the UK, it must also be "based on Article 6(1)".
  - **Article 6 basis:** consent (proposed) or contract.
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

**Consultation (to do).** Ask a few people who would use halal or kosher filters how they'd want it worded and which certifiers they trust (the friends' round or after). Ask HMC before any automated use of its directory.

**Sign-off (to do).**
- Abram, as the decision-maker, records the outcome, any residual risk accepted, and the review date (on launch, then yearly).
- The privacy notice gets its own section (~0.5 h).
- If a high residual risk remained, the ICO would have to be consulted before processing (Article 36). On the measures above, none is expected to remain high.

## What's built and what isn't

- **Built (safe, no persistence):**
  - the evidence model and the purpose guard (`brain/src/brain/food.py`, m208);
  - the guard test above;
  - the Brain now drops `foods_avoided` (D19's free text, unasked since D123) instead of storing it;
  - both apps' profiles no longer carry the field.
- **Not built until sign-off:** the screen, the consent, the phone storage and the on-device filtering (both apps ~5 h, after decisions 1–4 in `decisions/food-preferences-and-privacy.md`).
- **For Abram, separately:** check whether any profile on the live Brain still holds a `foods_avoided` value from before 8 Oct (an admin export shows it). If so, delete it. Each profile save already replaces the stored profile, so it goes the next time that person saves.

**Hours:** Claude ~2 h. Abram: read and decide (~1 h), then sign off, or send it to a solicitor.
