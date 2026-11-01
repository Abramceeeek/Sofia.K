# ODYS in Figma

**Decision (m189, 25 Oct):** the design goes to Figma as two files, so a friend can comment on it and change it. The editable file is rebuilt from the app's own words, colours and example day. It doesn't replace the app: the app stays the source of truth. Abram's time is ~0.5 h for either route below.

| File | What it is | In Figma |
|---|---|---|
| `odys-figma.html` (this folder) | 51 frames rebuilt as plain HTML and CSS: every main screen at night and by day, the five skies, the plan reveal, "Now" on the way and arrived, the arrival moment, rating (empty, chosen, saved, saved with no signal), share, a trip, You, Help & safety, the lock-screen, banner and Android reminders, the two permission prompts, the offline error, the waking banner, and the foundations (colours with contrast, skies, type, parts, motion notes) | **Editable layers**: text, colours, frames |
| `odys-screenshots.zip` (built, not in the repo) | The 133 real screens: 76 iPhone (the CI screenshots of build 84's code) and 57 Android, by journey, labelled | **Pictures**: to comment on, not to edit |

Rebuild after app changes: `python3 design/figma/build.py`; and `python3 design/figma/build_shots.py <iphone-shots> android/app/build/screens odys-screenshots.zip`. The iPhone shots come from the iOS workflow's screenshot run (`workflow_dispatch`, upload off).

**As PDFs** (27 Oct, for sharing with ChatGPT or people): `to_pdf.js` prints either board as pages. Each section starts a page with its title, phones are never split, and text stays text. Run `NODE_PATH=$(npm root -g) node design/figma/to_pdf.js design/figma/odys-figma.html "ODYS design board.pdf" 4` for the board (16 pages). For the real screens, run it on the unzipped screenshot board's `index.html` with `4 2` (23 pages: four phones a row, two rows a page).

## Update (1 Nov): half done, stopped by Figma's call limit

The Starter plan allows 3 pages, so the 25 Oct versions stay on the same two pages, moved 7000 px right under "Older version · 25 Oct" (on the same page, any comments stay with them).
- **Editable screens: done.** The board as of 1 Nov (m190, m191): the pinned "Start the day", knife and fork on lunch, the 999-only red card, the one-line emergency row on You. Same build as 25 Oct (`to_svg.js`, `upload.py`, `figma_fix.js`, then the bold labels in Read me and Motion). Checked with screenshots.
- **Real screens: not finished.** 76 of the 172 pictures (86 iPhone, 86 Android, from `odys-screens.zip`) are uploaded and sit loose on the page as squashed 400 × 300 frames named `iphone-<screen>` or `android-<screen>`. Then Figma refused all calls: "You've reached the Figma MCP tool call limit on the Starter plan." **The docs say write tools are exempt, but in practice `use_figma` and `upload_assets` counted**: about 20 calls this month, then a stop. The page (developers.figma.com/docs/figma-mcp-server/rate-limits-access, read 1 Nov 2026) gives Starter "up to 20 per month" and doesn't say when it resets.
- **To finish (about 3 calls, once the limit allows):** upload the other 96 (two `upload_assets` calls of 60 and 36, then `upload.py` with the manifest `shots_layout.py` writes; it posts 8 at a time, because an image can take ~25 s and the links expire after 10 minutes), then run the script from `python3 design/figma/shots_layout.py <unzipped odys-screens.zip> layout.js manifest.json` in `use_figma`. It finds the pictures by name, drops any duplicates, and lays each screen out as iPhone and Android side by side, by journey. Anything still missing shows as a dashed "Picture not uploaded yet." box.
- **Or by hand, no connector:** delete the loose `iphone-…` and `android-…` frames, then import `odys-screens.zip` with the html.to.design plugin (Route B below).

## Done (25 Oct): "ODYS · design for review" in Abram's Figma drafts

Built through the Figma connector on Abram's free (Starter) account, in two pages:
- **Editable screens · night & day:** the 51 frames, the 8 foundation panels, the section headings and notes, laid out as on the board. Text is real text (Newsreader and Inter): each paragraph is one wrapping box with its weight, size, line height and letter spacing. Shapes are vectors with their fills.
- **Real screens · iPhone & Android:** the 133 screenshots at phone size, by journey, with headings.

**Sharing it (Figma help, help.figma.com/hc/en-us/articles/13838684089751, read 25 Oct 2026):** "On the Starter plan, you can only invite collaborators to drafts with `can view` access." Viewers can comment. For your friend to **edit**, either move the file out of Drafts into your team's project and share it from there, or upgrade. A Figma help mirror says a Starter team project holds up to three design files that can be shared with edit access (UNVERIFIED; forum reports from 2021 and 2024 disagree).

How it was built (the connector here has no `html_to_figma`, and its scripts can't fetch): `to_svg.js` turns each frame of `odys-figma.html` into an SVG. Figma's SVG import keeps text as text. `upload.py` posts the SVGs and screenshots to the connector's `upload_assets` URLs. `figma_fix.js`, run with `use_figma`, joins each paragraph's lines into one text box and restores what SVG can't carry: the weights, letter spacing, shadows and clean layer names. Known gaps: bold words inside a sentence come through regular, and a "/" in an uploaded file's name cuts the layer name short. Layer names with "·" arrived garbled and were repaired in Figma. Calls used: 7 uploads and 12 scripts, all write tools. (We believed then that Figma counts only read tools against the Starter limit; on 1 Nov the write calls counted too. See above.)

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
