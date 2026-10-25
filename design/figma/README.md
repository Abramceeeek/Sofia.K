# ODYS in Figma

**Decision (m189, 25 Oct):** the design goes to Figma as two files, so a friend can comment on it and change it. The editable file is rebuilt from the app's own words, colours and example day. It doesn't replace the app: the app stays the source of truth. Abram's time is ~0.5 h for either route below.

| File | What it is | In Figma |
|---|---|---|
| `odys-figma.html` (this folder) | 51 frames rebuilt as plain HTML and CSS: every main screen at night and by day, the five skies, the plan reveal, "Now" on the way and arrived, the arrival moment, rating (empty, chosen, saved, saved with no signal), share, a trip, You, Help & safety, the lock-screen, banner and Android reminders, the two permission prompts, the offline error, the waking banner, and the foundations (colours with contrast, skies, type, parts, motion notes) | **Editable layers**: text, colours, frames |
| `odys-screenshots.zip` (built, not in the repo) | The 133 real screens: 76 iPhone (the CI screenshots of build 84's code) and 57 Android, by journey, labelled | **Pictures**: to comment on, not to edit |

Rebuild after app changes: `python3 design/figma/build.py`; and `python3 design/figma/build_shots.py <iphone-shots> android/app/build/screens odys-screenshots.zip`. The iPhone shots come from the iOS workflow's screenshot run (`workflow_dispatch`, upload off).

## Route A: the Figma connector (recommended; free while Figma's beta lasts)

1. At <https://claude.ai/customize/connectors>, open **Figma** and finish signing in. It's installed on the account, but the sign-in wasn't finished (25 Oct).
2. Start a **new** Claude Code session. Connectors are read when a session starts.
3. Ask: "Put `design/figma/odys-figma.html` and the screenshots into Figma." Claude creates a file in your drafts and converts the HTML into layers.
4. In Figma: **Share** → invite your friend by email, as **can edit** or **can view** (viewers can still comment).

What Figma says (developers.figma.com, read 25 Oct 2026):
- Writing to the canvas "is free during the beta period and will eventually become a usage-based paid feature".
- It needs "a Full seat to write outside your drafts". A free (Starter) account has no Full seat, so Claude writes into your drafts.
- `html_to_figma` "converts an HTML document into design layers"; the HTML "must be self-contained, with CSS and images included". This file is.
- Read tools are limited to "up to 20 per month" for View and Collab seats on every plan, including Starter. "Some tools are exempt, including tools that write to Figma files."
- **UNVERIFIED:** whether a Starter account can run every write tool in its drafts. If one is refused, use route B.

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
