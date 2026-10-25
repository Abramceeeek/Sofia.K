# ODYS in Figma

**Decision (m189, 25 Oct):** the design goes to Figma as two files, so a friend can comment on it and change it. The editable file is rebuilt from the app's own words, colours and example day. It doesn't replace the app: the app stays the source of truth. Abram's time is ~0.5 h for either route below.

| File | What it is | In Figma |
|---|---|---|
| `odys-figma.html` (this folder) | 51 frames rebuilt as plain HTML and CSS: every main screen at night and by day, the five skies, the plan reveal, "Now" on the way and arrived, the arrival moment, rating (empty, chosen, saved, saved with no signal), share, a trip, You, Help & safety, the lock-screen, banner and Android reminders, the two permission prompts, the offline error, the waking banner, and the foundations (colours with contrast, skies, type, parts, motion notes) | **Editable layers**: text, colours, frames |
| `odys-screenshots.zip` (built, not in the repo) | The 133 real screens: 76 iPhone (the CI screenshots of build 84's code) and 57 Android, by journey, labelled | **Pictures**: to comment on, not to edit |

Rebuild after app changes: `python3 design/figma/build.py`; and `python3 design/figma/build_shots.py <iphone-shots> android/app/build/screens odys-screenshots.zip`. The iPhone shots come from the iOS workflow's screenshot run (`workflow_dispatch`, upload off).

## Done (25 Oct): "ODYS · design for review" in Abram's Figma drafts

Built through the Figma connector on Abram's free (Starter) account, in two pages:
- **Editable screens · night & day:** the 51 frames, the 8 foundation panels, the section headings and notes, laid out as on the board. Text is real text (Newsreader and Inter): each paragraph is one wrapping box with its weight, size, line height and letter spacing. Shapes are vectors with their fills.
- **Real screens · iPhone & Android:** the 133 screenshots at phone size, by journey, with headings.

**Sharing it (Figma help, help.figma.com/hc/en-us/articles/13838684089751, read 25 Oct 2026):** "On the Starter plan, you can only invite collaborators to drafts with `can view` access." Viewers can comment. For your friend to **edit**, either move the file out of Drafts into your team's project and share it from there, or upgrade. A Figma help mirror says a Starter team project holds up to three design files that can be shared with edit access (UNVERIFIED; forum reports from 2021 and 2024 disagree).

How it was built (the connector here has no `html_to_figma`, and its scripts can't fetch): `to_svg.js` turns each frame of `odys-figma.html` into an SVG. Figma's SVG import keeps text as text. `upload.py` posts the SVGs and screenshots to the connector's `upload_assets` URLs. `figma_fix.js`, run with `use_figma`, joins each paragraph's lines into one text box and restores what SVG can't carry: the weights, letter spacing, shadows and clean layer names. Known gaps: bold words inside a sentence come through regular, and a "/" in an uploaded file's name cuts the layer name short. Layer names with "·" arrived garbled and were repaired in Figma. Calls used: 7 uploads and 12 scripts, all write tools. Figma counts only read tools against the Starter limit.

## Route A: the Figma connector (what was used)

1. At <https://claude.ai/customize/connectors>, open **Figma** and finish signing in.
2. Start a **new** Claude Code session. Connectors are read when a session starts.
3. Ask Claude to put the files into Figma (see "Done" above for how).

What Figma says (developers.figma.com, read 25 Oct 2026):
- Writing to the canvas "is free during the beta period and will eventually become a usage-based paid feature".
- It needs "a Full seat to write outside your drafts". A free (Starter) account has no Full seat, so Claude writes into your drafts.
- Read tools are limited to "up to 20 per month" for View and Collab seats on every plan, including Starter. "Some tools are exempt, including tools that write to Figma files."

## Route B: no connector (the html.to.design plugin)

1. In Figma, open a new design file → **Plugins** → search **html.to.design** → run it.
2. Choose the file-upload option and upload `odys-figma.html`. Then do the same with `odys-screenshots.zip`, ideally on a second page.
3. If fonts are reported missing, let the plugin download them (Newsreader and Inter are Google fonts).

html.to.design says (html.to.design/docs/free-features, read 25 Oct 2026): "You can also upload your own `.html`, `.htm` or `.zip` files to instantly import them as editable Figma layers." **UNVERIFIED:** the free plan's import limit. The vendor's page doesn't state it, and other sites disagree (10, 12 or 20 a month). This needs 2 imports.

## Before using your friend's changes

Comments are just feedback. If your friend **changes the design** and you build those changes into the app, that's their work. **They sign Part A first** (`legal/contributor-deed-part-a.md`: IP assignment and confidentiality, D55, D73). D81 still holds: you design v0 yourself unless an outside designer is brought in.

## Sending the app too

- **Android:** the APK is public on the `android-latest` release (<https://github.com/abramceeeek/sofia.k/releases/tag/android-latest>, build 10, made from the D131 code). Your friend allows "install unknown apps" for their browser.
- **iPhone:** TestFlight's internal testers must be "App Store Connect users with access to your content" (developer.apple.com, read 25 Oct 2026; up to 100). Adding your friend means adding them as a user on your developer account. An external tester link needs the Apple check first (D60, `decisions/testflight-external.md`). Simplest: show build 84 on your own phone.
- Either way, have them type the tester code **FRIENDS** on the welcome screen, so their answers are tagged friends and family. They will see the privacy notice like any tester.
