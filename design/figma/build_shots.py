"""Builds odys-screenshots.zip: every real screen of both apps (the CI iPhone screenshots and the Android Robolectric
screens), laid out by journey with the iPhone and Android versions of each screen side by side, as one HTML page plus
its images. The html.to.design plugin imports a .zip as one Figma page; each screen becomes an image you can comment
on (not edit: odys-figma.html is the editable one). design/figma/to_pdf.js prints the same page as a PDF.

Run: python3 design/figma/build_shots.py <iphone-shots-dir> <android-screens-dir> <out.zip> ["what was built"]
"""
import html
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

# Each screen by its iPhone name (ios.yml's lists; "-day" and "-golden" are the daylight versions)
GROUPS = [
    ("First run and onboarding", ["intro", "welcome", "welcome-day", "founder", "example", "examplecard", "consent",
                                  "based", "besthour", "why", "places", "categories", "thisorthat", "learned",
                                  "learnedchange"]),
    ("Plan 1 / Plan 2 (Test B) and the survey", ["survey", "pairintent", "pair", "pair2", "pairreveal"]),
    ("Planning a day", ["planform", "mustinclude", "waking", "error", "reveal", "plan", "plan-day", "plan2", "planend",
                        "planmap", "stop", "stop2", "swap"]),
    ("On the day", ["now", "now-day", "nowahead", "nowlocation", "replan", "nowarrived", "nowarrived-day", "nowend", "rating",
                    "rating-day", "ratingpicked", "ratingdone", "sharecard", "shareimage", "improve", "improveq"]),
    ("Home", ["triphome", "triphome-day", "hometoday", "hometoday-day", "hometoday-golden", "homeafter",
              "homeafter-day"]),
    ("Trips", ["tripwhere", "tripwhen", "tripfrom", "airports", "tripdays", "tripfeel", "trip", "trip-day", "tripday",
               "tripdaylast", "daychange"]),
    ("Flights and stays", ["flights", "flights-day", "flightfilters", "flight", "handoff", "handoffback", "stays",
                           "staysmap", "stayfilters", "stay", "stay-day"]),
    ("You, Help & safety, your data", ["you", "you-day", "safety", "safety-day", "safetysend", "safetyreply",
                                       "settings", "settings-day", "delete"]),
]
NAMES = {
    "intro": "Opening: the arch lights up", "welcome": "Welcome", "founder": "Abram's hello video",
    "example": "An example day", "examplecard": "Example day: further down", "consent": "Before we start",
    "based": "Where are you based?", "besthour": "A great moment", "why": "Why do you go out?",
    "places": "Places you've been", "categories": "Kinds of places (visitors)", "thisorthat": "This or that",
    "learned": "So far, I've learned", "learnedchange": "So far: change something", "survey": "A few quick questions",
    "pairintent": "Before the two plans", "pair": "Plan 1 / Plan 2", "pair2": "Plan 1 / Plan 2: the questions",
    "pairreveal": "Which plan was which", "planform": "Plan a day", "mustinclude": "Must include a place",
    "waking": "Waking up the planner", "error": "Something went wrong", "reveal": "The plan appearing",
    "plan": "Your day", "plan2": "Your day: the stops", "planend": "Your day: the end, the reminder ask",
    "planmap": "Your day: map", "stop": "A stop's card", "stop2": "A stop's card: further down",
    "swap": "Swap this stop?", "now": "Now: on the way", "nowlocation": "Now: the location ask",
    "replan": "Re-plan the rest of today?", "nowahead": "Now: a look ahead (a later day)", "nowarrived": "Now: arrived", "nowend": "End of the day",
    "rating": "Rate the stop", "ratingpicked": "Rate: a word chosen", "ratingdone": "Rate: saved",
    "sharecard": "Share this moment", "shareimage": "The picture that's shared", "improve": "Improve future plans",
    "improveq": "Improve: a question", "triphome": "Home: before the day", "hometoday": "Home: on the day",
    "homeafter": "Home: after the day", "tripwhere": "New trip: where", "tripwhen": "New trip: when",
    "tripfrom": "New trip: from", "airports": "New trip: find a town or airport", "tripdays": "New trip: your days",
    "tripfeel": "New trip: the feel", "trip": "A trip", "tripday": "A trip day", "tripdaylast": "The last day: home",
    "daychange": "Change this day", "flights": "Flights", "flightfilters": "Flight filters", "flight": "A flight",
    "handoff": "Off to book", "handoffback": "Back from booking: did you book it?", "stays": "Stays",
    "staysmap": "Stays: map", "stayfilters": "Stay filters", "stay": "A stay", "you": "You (from the menu)",
    "safety": "Help & safety", "safetysend": "Help & safety: just sent", "safetyreply": "Help & safety: a reply",
    "settings": "Your data", "delete": "Delete my data",
}
# A screen one app has and the other doesn't, and why
ONLY = {
    "founder": ("iPhone", "Shows only once Abram's hello clip is recorded and bundled (D117); this is the placeholder."),
    "shareimage": ("Android", "The picture itself, as friends receive it. On the iPhone it's the card in "
                              "\"Share this moment\"."),
}
# Android screen files (ScreensTest) whose names differ from the iPhone's
ANDROID_ALIASES = {"home-day": "triphome-day", "tripcreate": "tripwhere", "changeday": "daychange",
                   "sharepreview": "sharecard", "sharecard": "shareimage", "now-arrived": "nowarrived-day"}
SKIP_ANDROID = {"arch-sun"}   # a drawing test of one part, not a screen

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{background:#E7E3DA;color:#1E2326;font-family:Inter,system-ui,sans-serif}
.board{padding:72px;display:flex;flex-direction:column;gap:96px;width:max-content}
h1{font-family:Newsreader,Georgia,serif;font-weight:400;font-size:56px}
h2{font-family:Newsreader,Georgia,serif;font-weight:400;font-size:40px}
.lead{font-size:17px;line-height:1.5;color:#3B4044;max-width:1100px;margin-top:10px}
.sec{display:flex;flex-direction:column;gap:24px}
.grid{display:grid;grid-template-columns:repeat(3,828px);gap:56px 48px}
.shot{display:flex;flex-direction:column;gap:10px;width:828px}
.shot b{font-size:17px;font-weight:600}
.shot .light{font-weight:400;color:#5B6064}
.pair{display:grid;grid-template-columns:402px 402px;gap:24px;align-items:start}
.phone{display:flex;flex-direction:column;gap:6px}
.phone i{font-style:normal;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#5B6064}
.phone img{width:402px;display:block}
.none{width:402px;height:871px;border:1.5px dashed #A7A196;display:flex;align-items:center;justify-content:center;
  padding:40px;text-align:center;font-size:16px;line-height:1.5;color:#5B6064}
"""


def label(name):
    base, _, light = name.partition("-")
    words = NAMES.get(base, base)
    light = {"day": "day", "golden": "golden hour"}.get(light, "night") if light else "night"
    return words, light


def jpeg(path, width):
    im = Image.open(path).convert("RGB")
    h = round(im.height * width / im.width)
    buf = io.BytesIO()
    im.resize((width, h), Image.LANCZOS).save(buf, "JPEG", quality=84, optimize=True)
    return buf.getvalue()


def android_files(android_dir):
    found = {}
    for src in sorted(android_dir.glob("*.png")):
        key = src.stem.split("-", 1)[1]
        if key in SKIP_ANDROID:
            continue
        found[ANDROID_ALIASES.get(key, key)] = src
    return found


def phone(platform, path, files, name, note):
    if path is None:
        return f'<div class="phone"><i>{platform}</i><div class="none">{html.escape(note)}</div></div>'
    key = f"{platform.lower()}/{name}.jpg"
    files[key] = jpeg(path, 804)
    return f'<div class="phone"><i>{platform}</i><img src="{key}" alt=""></div>'


def main(ios_dir, android_dir, out, built=""):
    ios_dir, android_dir = Path(ios_dir), Path(android_dir)
    ios = {p.stem: p for p in ios_dir.glob("*.png")}
    android = android_files(android_dir)
    listed = {n for _, names in GROUPS for n in names}
    extra = sorted((set(ios) | set(android)) - listed)
    groups = GROUPS + ([("More", extra)] if extra else [])
    secs, files, both = [], {}, 0
    for title, names in groups:
        cells = []
        for n in names:
            i, a = ios.get(n), android.get(n)
            if i is None and a is None:
                continue
            both += i is not None and a is not None
            only = ONLY.get(n.partition("-")[0])
            missing = only[1] if only else "Not drawn for this phone yet."
            words, light = label(n)
            cells.append(f'<div class="shot"><b>{html.escape(words)} <span class="light">· {light}</span></b>'
                         f'<div class="pair">{phone("iPhone", i, files, n, missing)}'
                         f'{phone("Android", a, files, n, missing)}</div></div>')
        if cells:
            secs.append(f'<div class="sec"><h2>{html.escape(title)}</h2><div class="grid">{"".join(cells)}</div></div>')
    n_ios = sum(1 for k in files if k.startswith("iphone/"))
    n_and = len(files) - n_ios
    page = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>ODYS screenshots</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Newsreader:opsz@6..72&display=swap">
<style>{CSS}</style></head><body><div class="board"><div><h1>ODYS · every screen a person sees</h1>
<p class="lead">{n_ios} iPhone screens and {n_and} Android screens, side by side ({both} on both). {html.escape(built)}
Drawn from the apps' own code with the same sample data, no server. Night unless marked; the colours follow London's
real light, so the daylight versions are shown for the main screens.</p></div>
{"".join(secs)}</div></body></html>"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", page)
        for k, v in files.items():
            z.writestr(k, v)
    print(f"wrote {out}: {n_ios} iPhone + {n_and} Android ({both} pairs), {Path(out).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(*sys.argv[1:5])
