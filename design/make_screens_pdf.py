"""A shareable PDF of the app's screens, for feedback from other people (D109) and, since 19 Oct, from other AI
models: every iPhone screen, then every Android screen, with the same numbers and captions.

Takes the screenshots CI makes (`.github/workflows/ios.yml`, artifact "screenshots"; `.github/workflows/android.yml`,
artifact "ODYS-android-screens-N") and lays them out three to a page with a plain caption, after a cover page for
the reviewer (what the app is, who it's for, and what to look at) and a page listing the flows.

    brain/.venv/bin/python design/make_screens_pdf.py <iOS PNG folder> [<Android PNG folder>] design/odys-screens.pdf
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# In the order a person sees them. Numbers match design/v0-screens.md and the review page (D110, D112): Build 1 is
# screens 1-14; a second picture of the same screen gets a letter (9a top, 9b the stops), so no label repeats.
# (key, number, group, name, caption). Captions are written for people outside the project.
SCREENS = [
    ("intro", "1a", "First run", "Welcome: the arch lighting up",
     "On first opening, light rises in the arch and spills out in front (about a second; a tap skips it)."),
    ("welcome", "1b", "First run", "Welcome", "ODYS: days out that fit you, and who runs this test."),
    ("example", "2a", "First run", "An example day",
     "What a plan looks like, before any question: one stop as a picture, then the day. Not planned for you."),
    ("examplecard", "2b", "First run", "An example day: one full card",
     "Further down the same screen: one stop's full card, so the special parts show before any question."),
    ("founder", "2c", "First run", "A hello from Abram",
     "A 20–30 s video, bundled in the app, with captions. Skip, or Continue when it ends. (Placeholder until it's recorded.)"),
    ("consent", "3", "First run", "Before we start",
     "A short summary, the two required choices in a box, and the details folded away."),
    ("based", "3b", "Onboarding, up to the first plan", "Where you're based",
     "London, elsewhere in the UK, or visiting from abroad, and a town or city if they like. Never nationality."),
    ("besthour", "4", "Onboarding, up to the first plan", "A great moment",
     "Abram asks it in a small video tile (placeholder until recorded). \"Tell it instead\" to speak, or type, or skip."),
    ("why", "5", "Onboarding, up to the first plan", "How you want to feel",
     "Restored, excited, connected, curious or peaceful: pick one or two. \"None of these\" is a quiet link."),
    ("places", "6", "Onboarding, up to the first plan", "Places you've been",
     "6 London places, one at a time, with a photo. A short line reacts to the answer (\"Got it: …\"), only from what was answered."),
    ("categories", "6b", "Onboarding, up to the first plan", "Kinds of places (visitors)",
     "Visitors from abroad only, instead of 6: 8 kinds of places with a London example. \"Never tried\" asks if they'd like to."),
    ("thisorthat", "7", "Onboarding, up to the first plan", "This or that",
     "\"There are no wrong answers.\" Two made-up days with all six details: pick one, or \"No preference\"."),
    ("learned", "7b", "Onboarding, up to the first plan", "So far, I've learned…",
     "Your own answers in plain words, no scores, with a small note from Abram. Looks right, or Change something."),
    ("learnedchange", "7c", "Onboarding, up to the first plan", "So far: changing something",
     "\"Not right\" on any line (Undo to take it back). It's stored, and that answer stops counting."),
    ("planform", "8", "The plan and the day out", "Plan a day",
     "Next Saturday, 12:00–17:00, already filled in, or Today / Tomorrow. One tap makes the plan."),
    ("plan", "9a", "The plan and the day out", "Your day",
     "How the day should feel, the numbers, and \"How the day moves\": a word for each stop, higher where we think you'll enjoy it more."),
    ("plan2", "9b", "The plan and the day out", "Your day: the stops",
     "Further down: each stop with its photo, time, reason and worth to you, then \"Start the day\"."),
    ("reveal", "9c", "The plan and the day out", "Your day: the reveal, part-way",
     "Instead of a spinner: the headline settles, the curve draws and each stop appears (2.6 s, once)."),
    ("planmap", "9d", "The plan and the day out", "Your day, on the map",
     "The same plan on a real map, with numbered pins."),
    ("stop", "10", "The plan and the day out", "A stop",
     "The photo full-bleed, with the time, the kind of moment and the title; why we picked it and its worth to you."),
    ("stop2", "10a", "The plan and the day out", "A stop: the way in",
     "Further down: the way in as a path you can tap along, \"The reveal\" where the arrival is the moment, then the details."),
    ("now", "10b", "The plan and the day out", "Now (new)",
     "While you're out: the stop you're at, \"I'll stay quiet until you need me\", what's next, and \"I'm done here\"."),
    ("nowend", "10c", "The plan and the day out", "Now: the day done (new)",
     "On a trip, after the last stop: \"Preview tomorrow: Day 3\", which opens tomorrow's page to look at tonight and change if plans have changed."),
    ("rating", "11", "The plan and the day out", "Rating",
     "After the visit: Flat, Fine, Good, Great or Unforgettable. The arch fills with light to the word."),
    ("ratingdone", "11a", "The plan and the day out", "Rating: thank you",
     "After saving: a thank-you, \"Share this moment\" and \"On to the next stop\"."),
    ("sharecard", "11b", "The plan and the day out", "Share card",
     "Your own rating and your own words, the photo, \"Planned with ODYS\". Never what we estimated it's worth. No rewards."),
    ("improve", "12a", "Improve future plans (optional, after the first plan)", "Improve future plans",
     "\"Make your next day even better?\" Offered once a stop is rated; before that, a quiet link."),
    ("improveq", "12b", "Improve future plans (optional, after the first plan)", "One question at a time",
     "Tap an answer and the next question comes. Skip any, stop any time."),
    ("safety", "13a", "Help, safety and your data", "Help & safety",
     "Emergency: call 999, kept separate from \"I feel unsafe or something's wrong\", which reaches a person."),
    ("safetysend", "13b", "Help, safety and your data", "Help & safety: just sent",
     "The automatic answer: 999 first, then who replies (Abram, or whoever covers) and that it's within a few hours."),
    ("safetyreply", "13c", "Help, safety and your data", "Help & safety: a reply",
     "The reply shows here, under your message, and Help gets a dot. Replies come within a few hours."),
    ("settings", "14a", "Help, safety and your data", "Your data", "What's stored, where and for how long; rating reminders on or off."),
    ("delete", "14b", "Help, safety and your data", "Delete my data", "Type DELETE to confirm. It can't be undone."),
    ("survey", "15", "Build 2: Tests A and B inside the app", "Three quick questions",
     "After \"So far\": I felt understood, it felt like talking to a person, typed or spoke, anything intrusive. All optional."),
    ("pairintent", "16", "Build 2: Tests A and B inside the app", "Before your plans",
     "Recharge or explore, who might come, anything for sure. Stored with both plans; it changes neither."),
    ("pair", "17a", "Build 2: Tests A and B inside the app", "Plan 1 or Plan 2?",
     "Two plans for the same Saturday in the same text format: no photos, map or reasons, so nothing gives one away."),
    ("pair2", "17b", "Build 2: Tests A and B inside the app", "Plan 1 or Plan 2: choosing",
     "After reading both: which you'd rather do (a gut choice), \"This plan fits me\" for each, and why."),
    ("pairreveal", "18", "Build 2: Tests A and B inside the app", "Which was yours",
     "Which plan was made from your answers. The one you chose becomes your day, rated stop by stop."),
    ("triphome", "19", "Trips (Abram's ODYS Trips design)", "Where to next?",
     "Plan a trip, your day and your trips; three tabs: Trip, Book and You."),
    ("tripwhere", "20", "Trips (Abram's ODYS Trips design)", "Where are you going?", "London is ready; UK cities come next, then Europe."),
    ("tripwhen", "21", "Trips (Abram's ODYS Trips design)", "When are you going? (new)",
     "A calendar, as in the booking apps: the first tap is the first day, a later tap the last day, the same day twice a day out. Up to 30 nights."),
    ("tripfrom", "22", "Trips (Abram's ODYS Trips design)", "Getting there",
     "Flying, by train, by car or already in London (D122); the airport from the town or city you gave (never nationality), and who's going."),
    ("tripdays", "22a", "Trips (Abram's ODYS Trips design)", "Your days",
     "D122: out from and back by, places a day (lunch on top), and travelling light on day 1."),
    ("tripfeel", "23", "Trips (Abram's ODYS Trips design)", "How should the trip feel?", "One or two feelings; they shape every day of this trip."),
    ("trip", "24", "Trips (Abram's ODYS Trips design)", "The trip",
     "A checklist in the order you'd do it, each with its status, then your days and a running total of real numbers only."),
    ("tripday", "25", "Trips (Abram's ODYS Trips design)", "The first day",
     "D122: from the airport (\"Heathrow → Paddington\", with Directions), one place on the way when travelling light, the stay, then the day. No moment twice in a trip."),
    ("tripdaylast", "25a", "Trips (Abram's ODYS Trips design)", "The last day",
     "D122: the day, back to the stay for the bags, then \"Leave for Heathrow by 17:20\" with Directions in Apple Maps."),
    ("daychange", "25b", "Trips (Abram's ODYS Trips design)", "Change this day (new)",
     "\"Made other plans?\" The hours they're free and their places, then the day planned again around them; the other days stay as they are."),
    ("flights", "26", "Trips (Abram's ODYS Trips design)", "Flights",
     "The search pinned at the top; Best, Cheapest and Fastest with their tops; one-tap chips. Sample prices until the keys are in."),
    ("flightfilters", "27", "Trips (Abram's ODYS Trips design)", "Flight filters",
     "Stops, leaving times each way, longest journey, price, a checked bag and airlines, with a live \"Show N flights\"."),
    ("flight", "28", "Trips (Abram's ODYS Trips design)", "A flight: where to book",
     "Both legs, the bags, the price found here and where to book. ODYS earns nothing from these links."),
    ("handoff", "28a", "Trips (Abram's ODYS Trips design)", "Going to a booking site", "Where you're going, the price found and when, and that you pay them directly."),
    ("handoffback", "28b", "Trips (Abram's ODYS Trips design)", "Back from the booking site", "Did you book it? Yes adds it to the trip; Not yet keeps it saved."),
    ("stays", "29", "Trips (Abram's ODYS Trips design)", "Places to stay",
     "Hotels, flats and hostels: For your days, Cheapest, Top rated; distance from where your days start."),
    ("staysmap", "30", "Trips (Abram's ODYS Trips design)", "Places to stay, on the map", "A real map with each place's price per night."),
    ("stayfilters", "31", "Trips (Abram's ODYS Trips design)", "Stay filters",
     "Most per night, type of place, guest rating, free cancellation and breakfast, with a live count."),
    ("stay", "32", "Trips (Abram's ODYS Trips design)", "A place to stay", "The rating, the distance, the room and rate, the price found, and where to book."),
    ("you", "33", "Trips (Abram's ODYS Trips design)", "You", "999 first, then a person; what the app has learned in plain words; your data."),
]
N_SCREENS = len({s[1].rstrip("abcdefghij") for s in SCREENS})

# Android's captures (android/app/src/test/.../ScreensTest.kt) are named "<number>-<name>". Most are the same screen
# as an iPhone one, so they share its number and caption; these are the Android-only ones and the renamed ones.
ANDROID_SAME = {"tripcreate": "tripwhere", "changeday": "daychange"}
ANDROID_ONLY = {
    "mustinclude": ("8b", "The plan and the day out", "Must include a place",
                    "From Plan a day: pick one ready place the plan must keep (the iPhone has the same sheet)."),
    "sharepreview": ("11c", "The plan and the day out", "Share: the preview",
                     "The card as it will be sent, before Android's own share sheet opens."),
    "airports": ("22b", "Trips (Abram's ODYS Trips design)", "Flying from: pick an airport",
                 "Type a town, city or airport code; the list is airports and city codes, never countries."),
}
ANDROID_NOTE = ("Android differences: maps are OpenStreetMap tiles (the iPhone uses Apple Maps), directions open "
                "Google Maps, and Material system controls replace iOS ones. The words and order are the same.")


def android_screens(folder: Path) -> list[tuple]:
    """(key, number, group, name, caption) for each Android capture, in file order, captions from the iPhone list."""
    by_key = {s[0]: s for s in SCREENS}
    out = []
    for f in sorted(folder.glob("*.png")):
        stem = f.stem.split("-", 1)[1] if "-" in f.stem else f.stem
        if stem in ANDROID_ONLY:
            num, group, name, what = ANDROID_ONLY[stem]
        else:
            _, num, group, name, what = by_key[ANDROID_SAME.get(stem, stem)]
        out.append((f.stem, num, group, name, what))
    return out

INK = colors.HexColor("#1c2230")
MUTED = colors.HexColor("#5b6475")
ACCENT = colors.HexColor("#b4532f")
RULE = colors.HexColor("#d9dce3")

COVER_LINES = [
    ("title", "ODYS: every screen, iPhone and Android"),
    ("sub", "A design, UI and UX review pack for AI models and people (19 October 2026)"),
    ("gap", ""),
    ("head", "What ODYS is"),
    ("body", "A test app that plans a day out in London around how a person wants to feel (restored, excited, connected, curious, peaceful), not around famous sights. The unit is a 'moment': a specific experience at a place and time, often including how you arrive. People answer a few questions and react to places they know; the app plans a day with real Tube times and the forecast, and they rate each stop 1-5 after they've been. Trips add flights and places to stay, found in the app and booked on the provider's own site."),
    ("body", "Who it's for now: friends, then strangers in London, testing whether a personal plan beats a generic one. One founder, about 7.5 hours a week. Design language: dark always, amber light, the Newsreader serif, an arch motif, quiet motion."),
    ("body", "These are screenshots from test builds with sample data (CI, 19 Oct). The iPhone pages come first (58 pictures), then Android (46). The same number means the same screen on both."),
    ("gap", ""),
    ("head", "What we'd like from you"),
    ("body", "1. Flow: where would a first-time user hesitate or give up? There are 14 questions before the first plan."),
    ("body", "2. Clarity: anything confusing, ambiguous or too long? Quote the words."),
    ("body", "3. Visual design: hierarchy, typography, spacing, contrast on the dark theme, consistency between screens and platforms."),
    ("body", "4. Accessibility: legibility, tap targets, large text, colour contrast, motion."),
    ("body", "5. Trust: do safety, privacy and 'we earn nothing from these links' come across? Anything that feels pushy or creepy?"),
    ("body", "6. Platform fit: does each app feel native (iOS Human Interface Guidelines, Android Material)?"),
    ("body", "7. Your top 10 changes, as a table: Screen number | Problem | Why it matters | Suggested fix | Severity (high, medium, low)."),
]


def wrap(c: canvas.Canvas, text: str, font: str, size: float, width: float) -> list[str]:
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def cover(c: canvas.Canvas, w: float, h: float) -> None:
    x, y, width = 28 * mm, h - 36 * mm, w - 56 * mm
    styles = {"title": ("Helvetica-Bold", 24, INK, 11), "sub": ("Helvetica", 13, MUTED, 7),
              "head": ("Helvetica-Bold", 13, ACCENT, 7), "body": ("Helvetica", 12, INK, 5.2)}
    for kind, text in COVER_LINES:
        if kind == "gap":
            y -= 5 * mm
            continue
        font, size, colour, lead = styles[kind]
        c.setFont(font, size)
        c.setFillColor(colour)
        for line in wrap(c, text, font, size, width):
            c.drawString(x, y, line)
            y -= lead * mm
    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawString(x, 14 * mm, "ODYS · test build · October 2026")


def small(path: Path) -> ImageReader:
    """The screenshot as a JPEG about 1,000 px tall: sharp at this size on the page, and a file small enough to
    upload to an AI model or send by email."""
    im = Image.open(path).convert("RGB")
    if im.height > 1000:
        im = im.resize((round(im.width * 1000 / im.height), 1000), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True)
    buf.seek(0)
    return ImageReader(buf)


def flows_page(c: canvas.Canvas, w: float, h: float, screens: list[tuple]) -> None:
    c.showPage()
    x, y = 28 * mm, h - 30 * mm
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(INK)
    c.drawString(x, y, "The flows, and the screens in each")
    y -= 12 * mm
    groups: dict[str, list[str]] = {}
    for _, num, group, name, _ in screens:
        groups.setdefault(group, []).append(f"{num} {name}")
    col_w = (w - 56 * mm) / 2
    col, top = 0, y
    for group, items in groups.items():
        text = ", ".join(items)
        need = 6 * mm + 4.4 * mm * len(wrap(c, text, "Helvetica", 9.5, col_w))
        if y - need < 16 * mm and col == 0:
            col, y = 1, top
        cx = x + col * (col_w + 10 * mm)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(ACCENT)
        c.drawString(cx, y, group)
        y -= 5.5 * mm
        c.setFont("Helvetica", 9.5)
        c.setFillColor(INK)
        for line in wrap(c, text, "Helvetica", 9.5, col_w):
            c.drawString(cx, y, line)
            y -= 4.4 * mm
        y -= 3 * mm


def divider(c: canvas.Canvas, w: float, h: float, title: str, sub: str) -> None:
    c.showPage()
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(INK)
    c.drawString(28 * mm, h / 2 + 6 * mm, title)
    c.setFont("Helvetica", 12)
    c.setFillColor(MUTED)
    for i, line in enumerate(wrap(c, sub, "Helvetica", 12, w - 56 * mm)):
        c.drawString(28 * mm, h / 2 - 6 * mm - i * 6 * mm, line)


def screens_pages(c: canvas.Canvas, w: float, h: float, shots: Path, screens: list[tuple] | None = None,
                  platform: str = "iPhone") -> None:
    per_page, margin, gap = 3, 16 * mm, 14 * mm
    caption_h = 22 * mm
    img_h = h - 2 * margin - caption_h
    def img_path(key: str) -> Path:   # PNG from CI, or a JPEG copy for a smaller file to share
        png = shots / f"{key}.png"
        return png if png.exists() else shots / f"{key}.jpg"

    present = [(s[1], s) for s in (screens or SCREENS) if img_path(s[0]).exists()]
    for start in range(0, len(present), per_page):
        c.showPage()
        group = present[start:start + per_page]
        img = ImageReader(str(img_path(group[0][1][0])))
        iw, ih = img.getSize()
        img_w = img_h * iw / ih
        total = per_page * img_w + (per_page - 1) * gap
        x0 = (w - total) / 2
        for k, (num, (key, _, _, name, what)) in enumerate(group):
            x = x0 + k * (img_w + gap)
            y = margin + caption_h
            c.drawImage(small(img_path(key)), x, y, img_w, img_h, preserveAspectRatio=True)
            c.setStrokeColor(RULE)
            c.setLineWidth(0.6)
            c.roundRect(x, y, img_w, img_h, 4 * mm, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(ACCENT)
            c.drawString(x, y - 6 * mm, f"{num}")
            c.setFillColor(INK)
            c.drawString(x + 3 * mm + c.stringWidth(num, "Helvetica-Bold", 11), y - 6 * mm, name)
            c.setFont("Helvetica", 9)
            c.setFillColor(MUTED)
            ty = y - 11 * mm
            for line in wrap(c, what, "Helvetica", 9, img_w):
                c.drawString(x, ty, line)
                ty -= 4.2 * mm
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        first, last = group[0][0], group[-1][0]
        span = first if first == last else f"{first}–{last}"
        c.drawRightString(w - margin, 8 * mm, f"ODYS · {platform} · screens {span}")


def main(args: list[str]) -> None:
    ios, out = Path(args[0]), args[-1]
    android = Path(args[1]) if len(args) == 3 else None
    w, h = landscape(A4)
    c = canvas.Canvas(out, pagesize=(w, h))
    c.setTitle("ODYS: every screen, iPhone and Android")
    c.setAuthor("Abram")
    cover(c, w, h)
    flows_page(c, w, h, SCREENS)
    divider(c, w, h, "iPhone", f"{len(SCREENS)} pictures of {N_SCREENS} screens, in the order a person sees them. "
                               "Sample data from a test build.")
    screens_pages(c, w, h, ios, SCREENS, "iPhone")
    if android:
        shots = android_screens(android)
        divider(c, w, h, "Android", f"{len(shots)} pictures. {ANDROID_NOTE}")
        screens_pages(c, w, h, android, shots, "Android")
    c.save()
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
