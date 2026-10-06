"""A shareable PDF of the app's screens, for feedback from other people (D109).

Takes the screenshots CI makes (`.github/workflows/ios.yml`, artifact "screenshots") and lays them out three to a
page with a plain caption, after a cover page that says what the app is and asks four feedback questions.

    brain/.venv/bin/python design/make_screens_pdf.py <folder of PNGs> design/odys-screens.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

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
    ("tripwhen", "21", "Trips (Abram's ODYS Trips design)", "How long for?",
     "One day to two weeks, or any number of nights; the first day on a strip; the dates in words."),
    ("tripfrom", "22", "Trips (Abram's ODYS Trips design)", "Getting there",
     "The airport from the town or city you gave (never nationality), \"I don't need a flight\", and who's going."),
    ("tripfeel", "23", "Trips (Abram's ODYS Trips design)", "How should the trip feel?", "One or two feelings; they shape every day of this trip."),
    ("trip", "24", "Trips (Abram's ODYS Trips design)", "The trip",
     "A checklist in the order you'd do it, each with its status, then your days and a running total of real numbers only."),
    ("tripday", "25", "Trips (Abram's ODYS Trips design)", "A day of the trip",
     "Its stops, no moment twice in a trip, and \"Make this my day\" for Now, ratings and swaps."),
    ("flights", "26", "Trips (Abram's ODYS Trips design)", "Flights",
     "The search pinned at the top; Best, Cheapest and Fastest with their tops; one-tap chips. Sample prices until the keys are in."),
    ("flightfilters", "27", "Trips (Abram's ODYS Trips design)", "Flight filters",
     "Stops, leaving times, longest journey, price, a checked bag and airlines, with a live \"Show N flights\"."),
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

INK = colors.HexColor("#1c2230")
MUTED = colors.HexColor("#5b6475")
ACCENT = colors.HexColor("#b4532f")
RULE = colors.HexColor("#d9dce3")

COVER_LINES = [
    ("title", "ODYS: the test app, in its new design"),
    ("sub", f"{N_SCREENS} screens, in the order you'd see them"),
    ("gap", ""),
    ("body", "An iPhone app that plans a day out in London around how you want it to feel, not a list of famous sights."),
    ("body", "You answer a few quick questions and react to some places you know. It plans a day with a map, and you rate each stop after you've been. More questions, all optional, come after the first plan."),
    ("body", "These are screenshots from a test build with sample data. Nothing is live yet."),
    ("gap", ""),
    ("head", "Your feedback (about 10 minutes)"),
    ("body", "1.  Is there a screen that would make you stop or give up? Which one?"),
    ("body", "2.  Is anything confusing or unclear? Give the screen number."),
    ("body", "3.  Is there anything you'd change, add or remove?"),
    ("body", "4.  Would you want to try it for a real day out? Why, or why not?"),
    ("gap", ""),
    ("body", "Reply to Abram with the screen numbers. Short answers are best, and honest ones help most, including \"this is boring\"."),
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


def screens_pages(c: canvas.Canvas, w: float, h: float, shots: Path) -> None:
    per_page, margin, gap = 3, 16 * mm, 14 * mm
    caption_h = 22 * mm
    img_h = h - 2 * margin - caption_h
    def img_path(key: str) -> Path:   # PNG from CI, or a JPEG copy for a smaller file to share
        png = shots / f"{key}.png"
        return png if png.exists() else shots / f"{key}.jpg"

    present = [(s[1], s) for s in SCREENS if img_path(s[0]).exists()]
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
            c.drawImage(ImageReader(str(img_path(key))), x, y, img_w, img_h, preserveAspectRatio=True)
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
        c.drawRightString(w - margin, 8 * mm, f"ODYS · screens {span} of {N_SCREENS}")


def main(shots: str, out: str) -> None:
    w, h = landscape(A4)
    c = canvas.Canvas(out, pagesize=(w, h))
    c.setTitle("ODYS: the test app")
    c.setAuthor("Abram")
    cover(c, w, h)
    screens_pages(c, w, h, Path(shots))
    c.save()
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
