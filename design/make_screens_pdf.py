"""A shareable PDF of the app's screens, for feedback from other people (D109).

Takes the screenshots CI makes (`.github/workflows/ios.yml`, artifact "screenshots") and lays them out three to a
page with a plain caption, after a cover page that says what the app is and asks four feedback questions.

    brain/.venv/bin/python design/make_screens_pdf.py <folder of PNGs> design/days-out-screens.pdf
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
# screens 1-14; a second picture of the same screen gets a letter (9a map, 9b list), so no label repeats.
# (key, number, group, name, caption). Captions are written for people outside the project.
SCREENS = [
    ("intro", "1a", "First run", "Welcome: the logo",
     "On first opening, the icon's ring draws itself, then settles above the title (about 1.3 s; a tap skips it)."),
    ("welcome", "1b", "First run", "Welcome", "Who runs this, and why."),
    ("example", "2a", "First run", "An example day",
     "What a plan looks like, before any question: how the day should feel, cost and the stops. Not planned for you."),
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
     "Restored, excited, connected, curious or peaceful: pick up to two, or none."),
    ("places", "6", "Onboarding, up to the first plan", "Places you've been",
     "6 London places, one at a time. A short line reacts to the last answer (\"Got it: …\"), only from what was answered."),
    ("categories", "6b", "Onboarding, up to the first plan", "Kinds of places (visitors)",
     "Visitors from abroad only, instead of 6: 8 kinds of places with a London example. \"Never tried\" asks if they'd like to."),
    ("thisorthat", "7", "Onboarding, up to the first plan", "This or that",
     "\"There are no wrong answers.\" Two made-up days: pick one, or \"No preference\". A pattern is named once it holds 3 times."),
    ("learned", "7b", "Onboarding, up to the first plan", "So far, I've learned…",
     "Abram's thank-you tile, then your own answers in plain words. No scores. Looks right, or Change something."),
    ("learnedchange", "7c", "Onboarding, up to the first plan", "So far: changing something",
     "Tap any line that isn't right. It's stored, and that answer stops counting."),
    ("planform", "8", "The plan and the day out", "Plan a day",
     "Next Saturday, 12:00–17:00, already filled in: one tap makes the plan. The day and times can change."),
    ("plan", "9a", "The plan and the day out", "Your day",
     "How the day should feel in one line, then cost, walking and finish, the day's shape, the map and the stops."),
    ("planlist", "9b", "The plan and the day out", "Your day, as a list",
     "The same plan without the map, with the travel between stops. \"Regenerate plan\" is further down."),
    ("reveal", "9c", "The plan and the day out", "Your day: the reveal, part-way",
     "Instead of a spinner: the feeling line, the summary, then the route draws and each stop appears (2.6 s, once)."),
    ("stop", "10", "The plan and the day out", "A stop",
     "The moment card: why we picked it for you, worth to you, the way in, the best light, a rain option, Swap."),
    ("rating", "11a", "The plan and the day out", "Rating",
     "After the visit: Flat, Fine, Good, Great or Unforgettable."),
    ("sharecard", "11b", "The plan and the day out", "Share card",
     "After rating a stop: the photo, your own rating and why it was picked, to send to a friend. No rewards."),
    ("improve", "12a", "Improve future plans (optional, after the first plan)", "Improve future plans",
     "\"Want us to learn you better? About 30 seconds.\" Optional, after the first plan."),
    ("improveq", "12b", "Improve future plans (optional, after the first plan)", "One question at a time",
     "Tap an answer and the next question comes. Skip any, stop any time."),
    ("safety", "13a", "Help, safety and your data", "Help & safety",
     "Emergency: call 999, kept separate from \"I feel unsafe / something's wrong\"."),
    ("safetysend", "13b", "Help, safety and your data", "Help & safety: telling a person",
     "An optional message to a person on the team, who replies within a few hours. 999 stays on screen."),
    ("settings", "14a", "Help, safety and your data", "Your data", "What's stored, where and for how long."),
    ("delete", "14b", "Help, safety and your data", "Delete my data", "Type DELETE to confirm. It can't be undone."),
]
N_SCREENS = len({s[1].rstrip("abcdefghij") for s in SCREENS})

INK = colors.HexColor("#1c2230")
MUTED = colors.HexColor("#5b6475")
ACCENT = colors.HexColor("#b4532f")
RULE = colors.HexColor("#d9dce3")

COVER_LINES = [
    ("title", "Days out: the test app, after the screen review"),
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
    c.drawString(x, 14 * mm, "Days out · test build · September 2026")


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
        c.drawRightString(w - margin, 8 * mm, f"Days out · screens {span} of {N_SCREENS}")


def main(shots: str, out: str) -> None:
    w, h = landscape(A4)
    c = canvas.Canvas(out, pagesize=(w, h))
    c.setTitle("Days out: the test app")
    c.setAuthor("Abram")
    cover(c, w, h)
    screens_pages(c, w, h, Path(shots))
    c.save()
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
