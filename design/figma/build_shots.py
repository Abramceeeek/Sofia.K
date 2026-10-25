"""Builds odys-screenshots.zip: every real screen of both apps (the CI iPhone screenshots and the Android Robolectric
screens), laid out by journey with a label on each, as one HTML page plus its images. The html.to.design plugin
imports a .zip as one Figma page; each screen becomes an image you can comment on (not edit: odys-figma.html is the
editable one).

Run: python3 design/figma/build_shots.py <iphone-shots-dir> <android-screens-dir> <out.zip>
"""
import html
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

IOS = [
    ("First run and onboarding", ["welcome", "welcome-day", "intro", "founder", "example", "examplecard", "consent",
                                  "based", "besthour", "why", "places", "categories", "thisorthat", "learned",
                                  "learnedchange", "improve", "improveq", "survey"]),
    ("Plan 1 / Plan 2 (Test B)", ["pairintent", "pair", "pair2", "pairreveal"]),
    ("The plan", ["planform", "reveal", "plan", "plan2", "plan-day", "planmap", "stop", "stop2", "daychange"]),
    ("On the day", ["now", "now-day", "nowarrived", "nowarrived-day", "nowend", "rating", "rating-day", "ratingdone",
                    "sharecard"]),
    ("Home", ["triphome", "triphome-day", "hometoday", "hometoday-day", "hometoday-golden", "homeafter",
              "homeafter-day"]),
    ("Trips, flights and stays", ["tripwhere", "tripwhen", "tripfrom", "tripdays", "tripfeel", "trip", "trip-day",
                                  "tripday", "tripdaylast", "flights", "flights-day", "flightfilters", "flight",
                                  "handoff", "handoffback", "stays", "staysmap", "stayfilters", "stay", "stay-day"]),
    ("You, Help & safety, your data", ["you", "you-day", "safety", "safety-day", "safetysend", "safetyreply",
                                       "settings", "settings-day", "delete"]),
]
NAMES = {
    "welcome": "Welcome", "intro": "Abram's hello", "founder": "Run by one person", "example": "An example day",
    "examplecard": "Example day: a stop", "consent": "Before we start", "based": "Where are you based?",
    "besthour": "A great moment", "why": "Why it asks", "places": "Places you've been",
    "categories": "Kinds of places (visitors)", "thisorthat": "This or that", "learned": "So far, I've learned",
    "learnedchange": "Change something", "improve": "Improve future plans", "improveq": "Improve: a question",
    "survey": "Short survey", "pairintent": "Your day (Test B)", "pair": "Plan 1 / Plan 2", "pair2": "Plan 2",
    "pairreveal": "The reveal", "planform": "Plan a day", "reveal": "Plan: revealing", "plan": "Plan",
    "plan2": "Plan: further down", "planmap": "Plan: map", "stop": "A stop's card", "stop2": "A stop's card: more",
    "daychange": "Change the day", "now": "Now: on the way", "nowarrived": "Now: arrived", "nowend": "End of a trip day",
    "rating": "Rating", "ratingdone": "Rating: saved", "sharecard": "Share this moment", "triphome": "Home: before",
    "hometoday": "Home: today", "homeafter": "Home: after", "tripwhere": "Trip: where", "tripwhen": "Trip: when",
    "tripfrom": "Trip: from", "tripdays": "Trip: your days", "tripfeel": "Trip: the feel", "trip": "Trip",
    "tripday": "A trip day", "tripdaylast": "The last trip day", "flights": "Flights", "flightfilters": "Flight filters",
    "flight": "A flight", "handoff": "Off to book", "handoffback": "Back from booking", "stays": "Stays",
    "staysmap": "Stays: map", "stayfilters": "Stay filters", "stay": "A stay", "you": "You", "safety": "Help & safety",
    "safetysend": "Help: sent", "safetyreply": "Help: a reply", "settings": "Your data", "delete": "Delete my data",
}

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{background:#E7E3DA;color:#1E2326;font-family:Inter,system-ui,sans-serif}
.board{padding:72px;display:flex;flex-direction:column;gap:96px;width:max-content}
h1{font-family:Newsreader,Georgia,serif;font-weight:400;font-size:56px}
h2{font-family:Newsreader,Georgia,serif;font-weight:400;font-size:40px}
.lead{font-size:17px;line-height:1.5;color:#3B4044;max-width:980px;margin-top:10px}
.sec{display:flex;flex-direction:column;gap:24px}
.grid{display:grid;grid-template-columns:repeat(10,402px);gap:48px 40px}
.shot{display:flex;flex-direction:column;gap:10px}
.shot b{font-size:15px;font-weight:600}
.shot img{width:402px;display:block;border-radius:0}
"""


def label(name):
    base, _, light = name.partition("-")
    words = NAMES.get(base, base)
    light = {"day": "day", "golden": "golden hour"}.get(light, "night") if light else "night"
    return f"{words} · {light}"


def jpeg(path, width):
    im = Image.open(path).convert("RGB")
    h = round(im.height * width / im.width)
    buf = io.BytesIO()
    im.resize((width, h), Image.LANCZOS).save(buf, "JPEG", quality=84, optimize=True)
    return buf.getvalue()


def main(ios_dir, android_dir, out):
    ios_dir, android_dir = Path(ios_dir), Path(android_dir)
    secs, files = [], {}
    listed = {n for _, names in IOS for n in names}
    missing = sorted(p.stem for p in ios_dir.glob("*.png") if p.stem not in listed)
    groups = IOS + ([("More", missing)] if missing else [])
    for title, names in groups:
        cells = []
        for n in names:
            src = ios_dir / f"{n}.png"
            if not src.exists():
                continue
            files[f"iphone/{n}.jpg"] = jpeg(src, 804)
            cells.append(f'<div class="shot"><b>{html.escape(label(n))}</b><img src="iphone/{n}.jpg" alt=""></div>')
        secs.append(f'<div class="sec"><h2>iPhone · {html.escape(title)}</h2><div class="grid">{"".join(cells)}</div></div>')
    cells = []
    for src in sorted(android_dir.glob("*.png")):
        files[f"android/{src.stem}.jpg"] = jpeg(src, 786)
        name = src.stem.split("-", 1)[1].replace("-", " ")
        cells.append(f'<div class="shot"><b>{html.escape(src.stem.split("-")[0] + " · " + name)}</b>'
                     f'<img src="android/{src.stem}.jpg" alt=""></div>')
    secs.append(f'<div class="sec"><h2>Android · every screen</h2><div class="grid">{"".join(cells)}</div></div>')
    n_ios = sum(1 for k in files if k.startswith("iphone/"))
    page = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>ODYS screenshots</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Newsreader:opsz@6..72&display=swap">
<style>{CSS}</style></head><body><div class="board"><div><h1>ODYS · every real screen</h1>
<p class="lead">{n_ios} iPhone screens (CI screenshots of TestFlight build 84's code, night unless marked) and {len(files) - n_ios} Android screens (drawn by CI from the same sample data). These are pictures to comment on; the editable versions are in the other file.</p></div>
{"".join(secs)}</div></body></html>"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", page)
        for k, v in files.items():
            z.writestr(k, v)
    print(f"wrote {out}: {n_ios} iPhone + {len(files) - n_ios} Android, {Path(out).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
