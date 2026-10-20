# A more natural feel: what four AI models said, what checked out, and the joint pick (20 Oct 2026)

The answers are kept in `design/reviews/2026-10-20-ai-natural-feel.md` (Answers 1–4, then four short answers written as a person using the app). The prompt is `design/research-prompts/01-natural-feel.md`. Abram asked the models and Claude to pick together ("other ai models will help you to pick"), so this page ends in a pick (D130). The build and the dates that follow from it are his to approve (D128).

## Decision first

**Built (D131, 20 Oct), in both apps:** Daylight with "Always dark", settling motion, the day as a path and the arrival moment, with the shape Abram picked (A, with D's path). Still to do: the 5-person test below, and the outdoor check on Abram's iPhone.

**The idea behind the pick:** the nature is in the day out. The app shouldn't decorate itself with leaves. It should feel as if it belongs to the day you're having, then get out of the way (Answer 2, and Claude agrees).

**Build these five, in this order:**

| # | What | Votes | Effort (Claude, GUESS) |
|---|---|---|---|
| 1 | **Daylight.** The colours follow London's real light (ideas 1 and 3): dawn, a pale day, golden hour and rain-grey by day, and today's dark ODYS look at night. An **"Always dark"** setting keeps the look we have now (idea 4 survives only as this setting). The amber arch becomes the sun: its light follows the sky. | Top pick in 4 of 4 answers; all 4 short answers | ~6 h, both apps |
| 2 | **Settling motion** (idea 9). One rule in both apps: things ease to rest, with no bounce or snap. With Reduce Motion on, they fade instead. | Top five in 4 of 4 | ~1 h (mostly there: `Motion.settle`) |
| 3 | **One thing at a time** (idea 13). Each screen has one main thing to do. The whole day stays one tap away, so nothing is hidden. | Top five in 4 of 4 | Part of the shape work (D129) |
| 4 | **The day as a path, with the list under it** (idea 5). The day is drawn as a path through the stops' real positions, numbered, with the stops and times listed straight under it. On "Now", the path shows where you are. | Top five in 3 of 4; the short answers liked mock-up D's path | ~3 h |
| 5 | **The arrival moment** (missing from our list; all four answers raised it). On the way, "Now" shows the card's way in. Once the phone sees you're there, or you tap "I'm here", the screen brightens once, like coming out of the station into the open, and shows what to notice. It's a fade with Reduce Motion on. | 4 of 4 named it as missing | ~2.5 h (the cards already have the way-in steps) |

Done alongside: **softer shapes** (idea 8) means keeping the corners we already have consistent everywhere. **Haptics** (idea 10) means the standard light tap when you choose something or finish a stop, with no raindrop or heartbeat.

**Not now** (after 9 Nov, #80): seasons (2), textures (7), a place soundscape (11), growth rings or constellations (14), nature in every plan (15) and best-light photos (16). Hand-drawn lines (6) means keeping the one drawn line we already have. A separate "gently alive" element (12) is folded into the arch-sun, so the app has one living thing, not two. **Rejected:** editing one photo to fake the light or the weather, and raindrop or heartbeat haptics.

**Hours:** Claude ~12.5 h for items 1, 2, 4 and 5 in both apps; item 3 comes with the shape (about 6–8 h more if Abram picks mock-up A). **Abram: ~15 min to read this, ~1.5 h for the mock-up test below, ~0.5 h to check the screenshots.**

## How the votes fell

| Idea | A1 | A2 | A3 | A4 | Joint |
|---|---|---|---|---|---|
| 1 Sky follows the day | Keep, #1 | Keep, #1 | Keep, #1 | Keep, #1 | **Build** |
| 3 Night stays dark | Inside 1 | Inside 1 | Inside 1 | Keep | **Build, as 1's night** |
| 4 Dark always | Drop | Drop as default; keep as a setting | Drop or fallback | Drop | **A setting only** |
| 9 Settling motion | #2 | #3 | #2 (with 12) | #4 | **Build** |
| 13 One thing at a time | #3 | #4 | #3 (with 5) | #3 | **Build** |
| 5 Day as a path | #5 | #2 | #3 | Change: keep the list | **Build, with the list** |
| 8 Softer shapes | Keep | Keep, with restraint | #5 | #2 | Small, with the rest |
| 12 Gently alive | Keep | Change: one effect | #2 | #5 | Folded into the arch-sun |
| 7 Light textures | #4 | Change | Change | Drop | Not now |
| 15 Nature in every day | Soft default | #5 | Soft default | Drop | Not now: a planner change |
| 14 Growth, not points | Keep, abstract | Change: quiet history | #4 | Keep | Not now (the memories list stays) |
| 16 Best-light photos | Keep | Change | #5 | Change: filters | Not now |
| 6 Hand-drawn lines | Keep | Change | Keep | Drop | Keep the line we have |
| 10 Nature haptics | Change | Drop | Change | Change | Standard haptics only |
| 11 Place soundscape | Change, off | Change, off | Keep, opt-in | Drop | Not now |
| 2 Seasons | Change | Change | Keep, light | Drop | Not now: daylight already brings them |

**Missing from our list** (each named by at least two answers): the arrival moment (4 of 4); control over the atmosphere, meaning "Always dark", Reduce Motion and sound off (3 of 4); readability in bright sun (2 of 4); a sky that still works offline (A1); weather changing during the day (A2: "Re-plan the rest of today" already covers it, D124).

## Where Claude disagrees with the models

1. **Solid surfaces, not frosted glass** (A4). See-through panels over a moving sky change their contrast as the sky changes, and some people turn on Reduce Transparency. Text always sits on solid surfaces (A2 says the same).
2. **Don't fake the light on a photo** (A4: "dynamic lighting filters on one base photo"). It would show a place as it isn't. Photos stay real and credited (`design/photo-credits.md`).
3. **The research is mixed, so no promises.** Three answers suggest nature on screens restores attention. The checked evidence below says it often doesn't. The one large smartphone experiment (n = 433) found nature backgrounds made no difference to attention or stress. ODYS aims to *feel* natural and calm, and never claims the app itself restores anyone. The parks and the river are what restore people, and those are what the planner puts in the day.
4. **London's winter sun breaks fixed sun-angle bands.** A4's "midday bright above 25°" never happens in November. On 14 Nov the sun peaks at about 20° and sets at about 16:15. On 21 Dec it peaks at about 15° (Claude's calculation from the standard solar formula). So the bands are set by time to sunset, not by fixed angles. That makes the shift easy to see on a winter day out: a 12:00–17:00 day is in golden light from about 14:30 and ends in the dark.
5. **A1's palette fails its own test.** White on its "noon" blue is 3.34:1, not the "≥ 4.6:1" it claims, and below the 4.5:1 minimum. Its sun-angle bands put sunset at 45–70°, which is wrong. **A2's palette passes.** Checked here: text 13.2–15.3:1, accent 6.3–8.1:1. Its night value is 14.8:1, not the 16.2:1 it claims, but that still passes. The day palette starts from A2's.
6. **Today's amber can't be used by day.** `#FFC665` on a pale surface is 1.5:1. By day the accent becomes a deep amber (A2 suggests `#80521A`, 6.4:1), and the bright amber comes back at night.

## How Daylight works (for the build)

- **Four states and a rain overlay:** night (today's colours), dawn/dusk, day, golden hour. Rain lowers the colour and shifts it toward grey-blue. It never adds a new background.
- **Which state:** worked out on the phone from the date and London's position, so it needs no network and works offline. Weather comes from the Met Office forecast the plan already carries. Without a forecast, the light follows the sun only.
- **Text:** two sets of colours, dark ink by day and the current warm ink by night, always on solid cards. Every pair is checked at 4.5:1 or better, in a test that fails the build if one drops below.
- **When it changes:** when a screen opens, or between steps of the day. Never while someone is reading.
- **The arch:** its light takes the sky's colour. On "Now", the sun sits where the real sun is in the day.
- **Control:** You → Appearance: "Follow the sky" (default) or "Always dark". Reduce Motion: cross-fades only.
- **The share card stays cream**, so it reads the same wherever it's sent (as now).

## Test it with people before trusting it (5 people, ~1.5 h of Abram's time)

The models agreed on comparing the current dark look with the new one, with the same few questions after each (A2's set, shortened). 5 people is enough to catch problems, not to prove anything.

1. **This week, before or alongside the build:** Abram shows 5 people the clickable mock-up on their own phones: the dark look, then Daylight, in a random order (10–15 min each). After each, they rate 1–7: "feels connected to the real day outside", "feels calm, not demanding", "I can tell what to do next", "I'd trust this plan". Then three open questions: "three words for how it feels", "did anything distract you or feel fake?" and "which would you use on a real day out?".
2. **Keep going if** at least 4 of the 5 would use Daylight on a real day out, and nobody found any text hard to read. If not, Claude changes the palette before building on it.
3. **Then on Abram's iPhone:** check "Now" outdoors in bright sun, and with Reduce Motion and the largest text size.

## Sources checked (20 Oct 2026)

| Claim in the answers | Checked | Verdict |
|---|---|---|
| Yan 2026 (Auburn thesis): nature backgrounds in a phone UI, n = 433 | [Fetched](https://etd.auburn.edu/handle/10415/10566) | **Correct.** Neither nature backgrounds nor see-through text boxes changed attention or stress |
| "2026" Korean plant-shop app study | [Fetched](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002908988) | **Real, but 2022** (Guo & Kim, n = 174, survey only). Nature images, colours and materials had positive emotional effects |
| Basu, Duvall & Kaplan 2019: soft fascination, n = 398 | [Search](https://deepblue.lib.umich.edu/items/329e6c84-9aba-491f-b542-c508b87de815) | Correct (abstract). About everyday activities, not screens |
| Huang et al. 2024 (ACM TAP): gamified VR nature is less relaxing | Link refused; not found by search | **UNVERIFIED** |
| Van der Jagt et al. 2017 (PLOS ONE): salient scenes interfere with restoration | [Fetched](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0169997) | Correct |
| Kaplan 1995; Berto 2005 (photos restore attention) | [Search](https://forrt.org/flora-replication-atlas/doi/10.1016/j.jenvp.2005.07.001/) | Citations correct. **A 2020 replication of Berto failed** (FORRT replication atlas) |
| Hicks et al. 2020: nature images didn't restore sustained attention | [Search](https://uwspace.uwaterloo.ca/handle/10012/16120) | Correct (from the thesis version: a Bayesian null, replicated) |
| Tay, Chen & Majeed 2023: nature videos didn't restore attention | [Search](https://ink.library.smu.edu.sg/soss_research/3773) | Correct (pre-registered; support for no effect) |
| Luo, Wang & Chen 2021: a nature-sound app, n = 71, 4 weeks | [Fetched](https://www.frontiersin.org/articles/10.3389/fpsyg.2021.699908/full) | Correct, with caveats: the groups differed at the start and the control group did nothing |
| Stevenson et al. 2018 review (after Ohly et al. 2016) | [Search](https://research.regionh.dk/en/publications/attention-restoration-theory-ii-a-systematic-review-to-clarify-at/) | Correct: small to moderate gains in working memory and flexibility. **Real places beat virtual ones** |
| Rendell et al. 2022 (BIT): nature imagery raises trust and aesthetics, n = 408 | [Search](https://ideas.repec.org/a/taf/tbitxx/v41y2022i13p2762-2778.html) | Correct; water and plants mattered most |
| Riaz, Gregor & Lin 2018 (I&M): emotional website imagery raises recall | [Search](https://researchportalplus.anu.edu.au/en/publications/biophilia-and-biophobia-in-website-design-improving-internet-info/) | Correct (abstract) |
| Sakdavong et al. 2026 (Frontiers): a nature video on a phone | [Fetched](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1942295/full) | Correct: **no clear effect on a phone** (n = 27 in that group; no control group) |
| Chan, Qiu & Yong 2025 (Ecopsychology): city wallpapers lower connectedness with nature | [Search](https://www.sutd.edu.sg/stories-listing/new-journal-paper-by-sarah-chan-urban-themed-mobile-phone-wallpapers-reduce-connectedness-with-nature-compared-with-nature-themed-wallpapers-evidence-from-two-field-studies/) | Correct (two 2-week field studies) |
| A4: Ulrich 1991 and Berman 2008 show screens lower **salivary cortisol** within 30–120 s | [Ulrich](https://psych.utah.edu/_resources/documents/psych4130/Ulrich%20et%20al_1991.pdf), [Berman](https://deepblue.lib.umich.edu/handle/2027.42/150702) | **Wrong.** Ulrich measured heart rate, muscle tension and skin conductance, not cortisol, and a 2026 replication only partly confirmed it. Berman's photo experiment measured attention, not stress |
| A4: Aristizabal 2021 shows digital organic cues help | [Search](https://mayoclinic.elsevierpure.com/en/publications/biophilic-office-design-exploring-the-impact-of-a-multisensory-ap) | **Misused:** a real office study (n = 37), not a screen study |
| A4: Shakhshir & Sheta 2024 | Not found | **UNVERIFIED** (probably invented) |
| Forest: a tree grows, withers if you leave, becomes a forest | [Fetched](https://apps.apple.com/gb/app/forest-focus-for-productivity/id866450515) | Correct |
| Calm: scenes with sound; silent scenes; volume | [Search](https://support.calm.com/hc/en-us/articles/115002582948-How-to-Stop-Background-Scene-Sounds-in-the-Calm-App) | Correct. **Sound plays by default** while the app is open, a reason to keep ours off |
| AllTrails: planned route green, walked route blue | [Search](https://support.alltrails.com/hc/en-us/articles/37228358315668-Using-the-Navigate-feature) | Correct |
| Endel: sound adapts to time, weather, heart rate, place | [Fetched](https://endel.io/) | Correct |
| Pikmin Bloom: flowers left behind as you walk | [Fan wiki](https://pikminwiki.com/Flower_Planting) | Correct (fan source) |
| Oak, Headspace, Apple Weather, Oura details | Oak's link was dead; the others weren't checked | **UNVERIFIED** |
| WCAG: 4.5:1 for normal text, 3:1 for large | [Fetched](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Correct |
