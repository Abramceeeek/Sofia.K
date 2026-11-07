# Food needs, halal included: privacy, evidence and the flow (WS2, 7 Nov 2026; m208)

**Decision (proposed; the lawful basis, the DPIA and the privacy notice are Abram's).**

How ODYS treats the data:
- **All food needs are special category data:** halal, kosher, vegetarian, vegan and allergies alike.
- **The lawful basis is explicit consent**, separate and specific, and withdrawn with one switch.
- **Use is limited to the person's own food suggestions.** Never matching people, advertising, analytics or anyone else.

How the data is held:
- **Kept on the phone only.** It is sent with each suggestions request and never stored on the server, as with location (D123).
- **Allergies are never stored.** Every food stop tells everyone to ask the venue, because UK law makes the venue give allergen information dish by dish.

What a venue can be called:
- **"Certified" only with a named certifier's own listing and the date it was checked.**
- Otherwise it says what the evidence is: "the venue says", "a community map says", or "not known".
- **Nothing is ever inferred** from a cuisine, a name, an owner, a neighbourhood or a photo.

**Built now:** the model and its rules (`brain/src/brain/food.py`) and 7 tests on synthetic venues. Nothing is stored, sent, asked or used in a plan. The app screens are specified below for review, not built.

Not legal advice: a solicitor or the DPIA review checks the reading below before launch.

## 1. Why it's special category data

| Need | Why | Source |
|---|---|---|
| Halal, kosher | Can reveal religious belief. The ICO says an inference is special category data if the processing aims to make it, *or if you treat someone differently because of it*, however confident you are. ODYS treats people differently by design: different food suggestions. | ICO, "What is special category data?" ([page](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-is-special-category-data/); read through ICO-domain search extracts on 7 Nov, because the page refused automated reading) |
| Allergies | Data concerning health, which the ICO reads broadly, including when it's only implied | Same page |
| Vegetarian, vegan | Not religion or health in itself. Ethical veganism has been held to be a protected philosophical belief in an employment tribunal (UNVERIFIED: not read in this session). Treated as special category to be safe: it costs nothing more, since the same consent covers all needs | — |

CLAUDE.md already points the same way. D19 asked no allergy question, because allergies are health data and halal may reveal religion. D123 stopped asking about food because no plan used it.

## 2. What the law asks, and ODYS's answer

| Requirement | What the ICO says (via search extracts, 7 Nov; [conditions](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/special-category-data/what-are-the-conditions-for-processing/), [valid consent](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/what-is-valid-consent/), [DPIA examples](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/examples-of-processing-likely-to-result-in-high-risk/)) | ODYS |
|---|---|---|
| **Article 6 basis** | One is needed as well as an Article 9 condition | **Consent, Art 6(1)(a)** (proposed). It matches Article 9 and the feature is optional. Abram decides |
| **Article 9 condition** | Explicit consent, Art 9(2)(a). No DPA 2018 Schedule 1 condition and no appropriate policy document are required for it (the ICO's table: "none required") | Explicit consent |
| **Explicit** | Confirmed "in a clear statement", which names the kind of special category data; kept apart from other consents. Where the data is needed for the service, you must show consent is still freely given | Its own screen, naming the data (below). Never bundled with the app's privacy consent. ODYS works fully without it |
| **Withdrawal** | Withdrawing should be easy, "one-step", with no detriment | One switch, "Use my food needs", in You. Off deletes them on the phone. The rest of the app is unchanged |
| **Purpose limitation** | One or more specified purposes | One purpose: the person's own food suggestions. Enforced in code: `FoodNeeds.use()` raises for any other purpose, and there's a test for matching, advertising, analytics and group trips |
| **Minimisation** | Only what the purpose needs | Only the chosen needs, and "strict" where it applies. No free text, no "why", no allergy list (section 5) |
| **Retention and deletion** | Not longer than needed | **On the phone only.** Sent with each suggestions request and used for that answer only; never written to the database, the logs or a backup. Deleted when withdrawn, with "Delete my data", or with the app |
| **Export** | Rights of access | Shown in "Your data" on the phone, where they are kept |
| **Analytics** | — | **None.** No event carries a food need, not even a count: a "halal filter used" count would itself be special category data about groups of people |
| **Third parties** | — | Never sent to venues, booking partners, LiteAPI, Duffel or anyone else |
| **DPIA** | Mandatory for large-scale special category processing (Art 35(3)(b)). The ICO's high-risk list includes decisions on access to a service that involve special category data | **A DPIA before building it** (product-direction.md already says so), even while the scale is small, and signed off by Abram. Its draft is the next step (~2 h) |
| **Privacy notice** | — | A new section: what is kept (on the phone), the purpose, the basis, withdrawal |

## 3. Where checked halal evidence comes from (read 7 Nov)

| Source | What it is | What we found | How ODYS can use it |
|---|---|---|---|
| **Halal Monitoring Committee (HMC)** | "an independent, not for profit, registered charity which monitors, inspects and certifies Halal products" (charity no. 1147462) | A public list of "HMC certified butchers, caterers, takeaways and dessert shops" at [halalhmc.org/outlets](https://halalhmc.org/outlets/), and a search by name at [halalhmc.org/outlets-by-name](https://halalhmc.org/outlets-by-name/) ([homepage](https://halalhmc.org/)). How often outlets are audited isn't stated on the homepage | `certified`, with "Halal Monitoring Committee", the outlet's listing URL and the date we saw it. Checked by hand per venue first. Any automated use of their directory needs HMC's permission |
| **Halal Food Authority (HFA)** | Calls itself the "UK's Leading Halal Certification Body" ([halalfoodauthority.com](https://halalfoodauthority.com/)) | Only the page title could be read. **No public directory found** (UNVERIFIED either way). A third-party guide points to a business search: unconfirmed | Only if a listing can be checked at the source |
| **Other certifiers** | Others exist in the UK | Not researched in this session | Later, one by one |
| **The venue's own words** | Its website or menu | — | `whole_menu` or `some_dishes`, quoted with the URL: "The venue says its whole menu is halal." Never "certified" |
| **Community map tags** | OSM `diet:halal=yes/only/no` | Mapper-added, unchecked (WS1) | "A community map says some dishes are halal." Never "certified" |
| **Our own visit** | Abram or a checker, on a date | — | `our_visit`, with the date |

**Certifiers' standards differ.** For example, secondary sources say certifiers disagree about stunning (UNVERIFIED). ODYS doesn't rank or judge them. It names the certifier, and a later option could let a person choose which certifiers they accept.

Kosher (London Beth Din, KLBD and others), vegetarian and vegan sources: not researched yet (UNVERIFIED).

## 4. The verification model (`brain/src/brain/food.py`)

| Status | Meaning | Required | What the person reads |
|---|---|---|---|
| `certified` | A certifier lists the venue | `evidence = certifier_directory`, the certifier's name, the listing URL, the date we saw it | "Certified halal by Halal Monitoring Committee (their listing, checked 20 Oct 2026)." Older than 90 days (GUESS): "Listed by … when last checked on 1 Mar 2026: check it's current." |
| `whole_menu` | The source says everything served meets the need | Evidence and URL | "The venue says its whole menu is halal." With strict halal: "… Not certified." |
| `some_dishes` | The source says some dishes do | Evidence and URL; dishes if named | "The venue says some dishes are vegetarian: halloumi wrap, falafel plate." |
| `not_suitable` | The source says it doesn't | Evidence and URL | "Not halal, according to the venue." It is then left out of that person's suggestions |
| `unknown` | Nothing with a source | — | "Not known whether it's halal: check with the venue." |

**Strict** (halal or kosher, the person's choice) means certified and current only. **Flexible** puts the evidence in order: certified, then "the venue says" or "a community map says", then unknown. Nothing is ever ranked by a guess.

**Never inferred, by construction.**
- `VenueFood` has no field for a cuisine, an owner, a neighbourhood, a photo or a name, so a guess can't be stored.
- The tests check two cases. A venue called "Halal Example Kitchen" with no evidence is unknown. An OSM restaurant tagged `cuisine=turkish` and nothing else is unknown for halal.

**Allergies.** The Food Standards Agency's guidance names 14 allergens. Businesses "must supply allergen information for every item that contains any of the 14 allergens", including "meals served in a restaurant" ([GOV.UK, updated 17 Jul 2026](https://www.gov.uk/government/publications/allergen-guidance-for-food-businesses/allergen-guidance-for-food-businesses); applies to England, Northern Ireland and Wales). So ODYS never says a venue or a dish is safe. Every food stop, for everyone, says: "For allergies, ask the venue before ordering: they must tell you which of the 14 allergens are in each dish. ODYS can't confirm what's safe for you." That helps people with allergies **without ODYS knowing who they are**.

## 5. The flow (a spec for review; both apps; not built)

1. **Where it's offered:** in You → "Food needs (optional)", and once on a day with lunch: "Want food suggestions that fit your needs?" (Not now / Choose). It's offered only when the destination has food evidence to show; with nothing checked, it isn't offered at all.
2. **What it does, and consent** (its own screen, apart from everything else):
   - "ODYS can suggest places to eat that fit food needs you choose. Some of these, like halal or kosher, can say something about your beliefs, so we ask first."
   - "**What we keep:** the needs you pick, on this phone only. **What for:** your own food suggestions, nothing else: never to match you with people, for ads, or for our statistics. **Change your mind:** one switch in You deletes them."
   - Button: "I agree: use my food needs". Secondary: "Not now". The consent text has its own version, recorded on the phone with the date.
3. **Choose:** chips for Halal, Kosher, Vegetarian, Vegan, and "Places not centred on alcohol". Halal and kosher each have "Certified places only" (off by default). No free text, and **no allergy question** (step 4 covers allergies for everyone).
4. **On a food stop:** one line per need, worded as in section 4, with the source as a link ("their listing", "the venue's menu"). For everyone, the allergy line.
5. **Withdraw:** You → "Use my food needs" off. "Your food needs are deleted from this phone." No other change to the app.
6. **Accessibility and parity:** chips at least 44 pt (iPhone) and 48 dp (Android); each status line read in full by VoiceOver and TalkBack. The same wording on both phones.

## 6. Decisions for Abram

1. The Article 6 basis: consent (proposed), or contract.
2. Phone-only storage (proposed): no server copy, no analytics.
3. Allergies never stored, with the line for everyone (proposed).
4. Sign off the DPIA (Claude drafts it, ~2 h) and the privacy-notice section (~0.5 h).
5. The first evidence: HMC's public directory checked by hand for the cards' food stops. Ask HMC before any automated use.
6. Whether "Places not centred on alcohol" belongs here (it's a preference about venues, not a belief), or in the day's feel.

## 7. Hours

- **This step:** Claude ~3 h (research, the model, tests, this page).
- **Next:** the DPIA draft ~2 h; the screens in both apps ~5 h; per-venue HMC checks ~10 min a venue (Abram or a checker).
- **Built only after** decisions 1–4.
