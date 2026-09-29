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

# In the order a person sees them. Captions are written for people outside the project.
SCREENS = [
    ("welcome", "Welcome", "Who runs this, and why."),
    ("consent", "Before we start", "What's kept and why, before you begin."),
    ("besthour", "The best hour", "One open question. Type, or tap the keyboard mic to speak."),
    ("why", "Why you go out", "Pick up to two."),
    ("places", "Places you've been", "16 London places, one at a time, with four reactions."),
    ("thisorthat", "This or that", "Two made-up days: pick the one you'd rather have. There are 10 of these."),
    ("aboutyou", "A bit about you", "Every question is optional."),
    ("photos", "Photos", "Includes an example \"shot card\": where to stand for the best photo."),
    ("planform", "Plan a day", "Choose the day and the times."),
    ("plan", "Your day", "The plan: a map and the stops in order."),
    ("stop", "A stop", "How to get there, what happens, the cost and a rain option."),
    ("shotcard", "Shot card", "Where to stand, which way to face, what to frame and when."),
    ("rating", "Rating", "One tap after each stop: how did it feel?"),
    ("safety", "Help & safety", "One button reaches a person. In an emergency, call 999."),
    ("settings", "Your data", "What's stored, and deleting everything in one tap."),
]

INK = colors.HexColor("#1c2230")
MUTED = colors.HexColor("#5b6475")
ACCENT = colors.HexColor("#b4532f")
RULE = colors.HexColor("#d9dce3")

COVER_LINES = [
    ("title", "Days out: the first version of the app"),
    ("sub", "15 screens, in the order you'd see them"),
    ("gap", ""),
    ("body", "An iPhone app that plans a day out in London around how you want it to feel, not a list of famous sights."),
    ("body", "You answer a few questions and react to some places you know. It plans a day with a map, and you rate each stop."),
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

    present = [(i, s) for i, s in enumerate(SCREENS, 1) if img_path(s[0]).exists()]
    for start in range(0, len(present), per_page):
        c.showPage()
        group = present[start:start + per_page]
        img = ImageReader(str(img_path(group[0][1][0])))
        iw, ih = img.getSize()
        img_w = img_h * iw / ih
        total = per_page * img_w + (per_page - 1) * gap
        x0 = (w - total) / 2
        for k, (num, (key, name, what)) in enumerate(group):
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
            c.drawString(x + 7 * mm, y - 6 * mm, name)
            c.setFont("Helvetica", 9)
            c.setFillColor(MUTED)
            ty = y - 11 * mm
            for line in wrap(c, what, "Helvetica", 9, img_w):
                c.drawString(x, ty, line)
                ty -= 4.2 * mm
        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawRightString(w - margin, 8 * mm, f"Days out · screens {group[0][0]}–{group[-1][0]} of {len(SCREENS)}")


def main(shots: str, out: str) -> None:
    w, h = landscape(A4)
    c = canvas.Canvas(out, pagesize=(w, h))
    c.setTitle("Days out: the first version of the app")
    c.setAuthor("Abram")
    cover(c, w, h)
    screens_pages(c, w, h, Path(shots))
    c.save()
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
