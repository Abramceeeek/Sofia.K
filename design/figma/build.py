"""Builds odys-figma.html: ODYS's screens rebuilt as plain HTML and CSS, so Figma can turn them into editable layers
(the Figma connector's html_to_figma, or the html.to.design plugin's .html upload).

Every screen comes in the night and the day light (D130), with the sky variants of the home, the notifications and
system prompts, the error and waiting states, and the foundations (colours, type, parts). The words and the example day
are the app's own (app/Sources/Demo), and the colours are Theme.swift's. Card photos are drawn as the app's fields of
colour, as in the CI screenshots; the real screens, photos included, are on the screenshot board.

Run: python3 design/figma/build.py   (writes design/figma/odys-figma.html)
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "app" / "Sources" / "Demo"
OUT = Path(__file__).resolve().parent / "odys-figma.html"

# ---- the colours (Theme.swift) ------------------------------------------------------------------------------------
NIGHT = dict(background="#111317", calm="#0B0C0E", surface="#1A1D23", deep="#15171C", surfaceHigh="#2A2E36",
             selected="#241F17", ink="#F4EBDD", inkSoft="#CFC6B8", inkTertiary="#B5AB9C", muted="#A89F92",
             line="#2C2F36", outline="rgba(244,235,221,0.12)", outlineStrong="rgba(244,235,221,0.18)",
             hairline="rgba(244,235,221,0.07)", accent="#FFC665", amberDeep="#E5A93C", amberLight="#FFE7B0",
             onAccent="#111317", danger="#D0363B", dangerInk="#FF8A8D", emergencyBg="#3A1416",
             emergencyBorder="#7A2A2E", emergencyTitle="#FFDCDC", emergencyText="#F6D2D2", track="#3A3E46",
             ring="#4A4E57", warnBg="#3A1F1C", warnInk="#F0A090", okBg="#1F3A2A", okInk="#9BE0B0",
             savedBg="#3A2F1C", accentSoft="rgba(255,198,101,0.22)", sky="#1A2030")
DAY = dict(background="#F4F1EA", calm="#F4F1EA", surface="#FFFDF8", deep="#ECE8DF", surfaceHigh="#E7E2D8",
           selected="#F5E8D2", ink="#1E2326", inkSoft="#3B4044", inkTertiary="#4C5156", muted="#5A5F64",
           line="#D6D0C4", outline="rgba(30,35,38,0.16)", outlineStrong="rgba(30,35,38,0.24)",
           hairline="rgba(30,35,38,0.09)", accent="#80521A", amberDeep="#6E4614", amberLight="#E8B76A",
           onAccent="#FFFDF8", danger="#B8262C", dangerInk="#B8262C", emergencyBg="#FBE4E2",
           emergencyBorder="#E7AEAD", emergencyTitle="#7A1518", emergencyText="#6A2023", track="#CFC8BB",
           ring="#A9A398", warnBg="#F8E1DC", warnInk="#8A2A1C", okBg="#DDEFE3", okInk="#1F5A35",
           savedBg="#F5E8D2", accentSoft="rgba(128,82,26,0.18)", sky="#DDEBE6")
SKIES = {"morning": "#E9DCE3", "day": "#DDEBE6", "golden": "#F4D6B3", "rain": "#D5DCE2", "night": "#1A2030"}

# The fields of colour standing in for photos (Odys.swift, Field)
FIELDS = {
    "Big views": "linear-gradient(180deg,#22304A 0%,#4A5C78 40%,#D49A5A 60%,#1A1C22 100%)",
    "Lunch": "radial-gradient(circle at 40% 20%,#C0663A 0%,#5E2618 60%,#17120F 100%)",
    "Awe": "radial-gradient(circle at 40% 20%,#E7B77A 0%,#9A6A3E 40%,#3B2A1E 75%,#15130F 100%)",
    "Calm": "radial-gradient(circle at 40% 20%,#86A870 0%,#3B5532 60%,#141A12 100%)",
    "Curious": "radial-gradient(circle at 40% 20%,#8A7A62 0%,#4A3F33 60%,#1B1814 100%)",
    None: "radial-gradient(circle at 40% 20%,#9A7A58 0%,#4A3A2A 60%,#15130F 100%)",
}

# ---- the example day (the app's demo data) ------------------------------------------------------------------------
PLAN = json.loads((DEMO / "demo_plan.json").read_text())
PLAN = PLAN.get("plan", PLAN)
STOPS = PLAN["stops"]
FEELS = ["Lunch", "Big views", "Calm", "Awe"]          # the word per stop, as the screens show it
LEARNED = [i["text"] for i in json.loads((DEMO / "demo_summary.json").read_text())["items"]]
TRIP_DAYS = json.loads((DEMO / "demo_trip_days.json").read_text())["days"]
# where the stops sit on the path (the plan's real positions, as drawn on the phone; 354 × 180)
PATH_PTS = [(44, 53), (139, 39), (123, 66), (309, 161)]


def esc(s):
    return html.escape(s, quote=False)


def feel_parts(line):
    head, _, rest = line.partition(": ")
    return head, (rest[:1].upper() + rest[1:]) if rest else ""


HEADLINE, SUBLINE = feel_parts(PLAN["feel_line"])

# ---- CSS ----------------------------------------------------------------------------------------------------------
# Rules written once with $tokens, then scoped to .N (night) and .D (day) with literal colours: no CSS variables, so
# any HTML-to-Figma converter reads them.
THEMED = """
& {color:$ink}
& .ink{color:$ink} & .soft{color:$inkSoft} & .ter{color:$inkTertiary} & .muted{color:$muted} & .acc{color:$accent}
& .eb{color:$amberDeep}
& .card{background:$surface}
& .deepcard{background:$deep}
& .outlined{border:1px solid $outline}
& .btn-p{background:$accent;color:$onAccent}
& .btn-s{border:1px solid $outlineStrong;color:$ink}
& .btn-d{background:$danger;color:#FFFFFF}
& .pill{border:1px solid $outlineStrong;color:$ink}
& .circ{border:1px solid $outlineStrong;color:$ink}
& .close{background:$surface;color:$accent;border:1px solid $outline}
& .chip{border:1.5px solid $outline;color:$ink}
& .chip.on{background:$accent;border-color:$accent;color:$onAccent}
& .tile{background:$surface;border:1px solid $outline}
& .tile.sel{background:$selected;border:1px solid $amberDeep}
& .opt{background:$surface;color:$ink}
& .opt.sel{background:$selected;border:1.5px solid $accent}
& .hair{background:$hairline}
& .seg{background:$surface} & .seg .on{background:$surfaceHigh;color:$ink} & .seg .off{color:$muted}
& .stat{background:$surface;color:$ink}
& .num{border:2px solid $accent;color:$accent} & .num.lit{background:$accent;color:$onAccent}
& .badge{background:$accent;color:$onAccent}
& .saved{background:$savedBg;color:$accent} & .booked{background:$okBg;color:$okInk}
& .emerg{background:$emergencyBg;border:1px solid $emergencyBorder}
& .emerg .t{color:$emergencyTitle} & .emerg .x{color:$emergencyText}
& .btn-e{border:1px solid $emergencyBorder;color:$emergencyTitle}
& .field{background:$background;border:1px solid $outline;color:$muted}
& .dot{background:$accent} & .ringdot{border:2px solid $ring} & .rail{background:$track}
& .track{background:$track} & .fill{background:$accent}
& .warn{background:$warnBg;color:$warnInk}
"""

BASE = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#E7E3DA;color:#1E2326;font-family:Inter,"SF Pro Text",-apple-system,system-ui,sans-serif;
  -webkit-font-smoothing:antialiased}
.board{padding:72px;display:flex;flex-direction:column;gap:112px;width:max-content}
.sec{display:flex;flex-direction:column;gap:28px}
.sec-h{display:flex;flex-direction:column;gap:8px;max-width:980px}
.sec-h h2{font-family:Newsreader,Georgia,serif;font-weight:400;font-size:44px;line-height:1.1;color:#1E2326}
.sec-h p{font-size:17px;line-height:1.5;color:#3B4044}
.row{display:flex;gap:56px;align-items:flex-start}
.shot{display:flex;flex-direction:column;gap:14px;width:402px;flex:none}
.shot>.label{font-size:15px;font-weight:600;color:#1E2326}
.shot>.note{font-size:13px;line-height:1.45;color:#4C5156;margin-top:-8px}
.phone{width:402px;min-height:874px;position:relative;display:flex;flex-direction:column;overflow:hidden;
  border-radius:0}
.sb{height:54px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:6px 32px 0 48px;
  position:relative}
.sb .time{font-size:17px;font-weight:600;letter-spacing:-0.2px}
.sb .island{position:absolute;left:138px;top:11px;width:126px;height:37px;border-radius:19px;background:#000000}
.sb .icons{display:flex;gap:6px;align-items:center}
.pad{padding:0 24px;display:flex;flex-direction:column}
.serif{font-family:Newsreader,Georgia,serif;font-weight:400}
.it{font-family:Newsreader,Georgia,serif;font-style:italic;font-weight:400}
.hero{font-size:44px;line-height:1.08;letter-spacing:-0.3px}
.display{font-size:40px;line-height:1.1;letter-spacing:-0.2px}
.h1{font-size:34px;line-height:1.12}
.t28{font-size:28px;line-height:1.15} .t24{font-size:24px;line-height:1.18} .t22{font-size:22px;line-height:1.2}
.t21{font-size:21px;line-height:1.22} .t19{font-size:19px;line-height:1.3}
.body{font-size:17px;line-height:1.38} .sub{font-size:15px;line-height:1.38} .foot{font-size:13px;line-height:1.38}
.semi{font-weight:600} .med{font-weight:500}
.eb{font-size:13px;font-weight:500;letter-spacing:1px;text-transform:uppercase}
.topbar{display:flex;align-items:center;gap:10px;min-height:44px}
.topbar .sp{flex:1}
.pill{height:36px;padding:0 14px;border-radius:18px;font-size:15px;display:flex;align-items:center}
.circ{width:36px;height:36px;border-radius:18px;display:flex;align-items:center;justify-content:center}
.close{height:40px;padding:0 18px;border-radius:20px;font-size:17px;display:flex;align-items:center}
.card{border-radius:18px;padding:16px;display:flex;flex-direction:column}
.r20{border-radius:20px}
.btn-p{height:56px;border-radius:28px;font-size:17px;font-weight:600;display:flex;align-items:center;
  justify-content:center;gap:8px;padding:0 20px}
.btn-s{height:52px;border-radius:26px;font-size:17px;display:flex;align-items:center;justify-content:center;
  gap:8px;padding:0 20px;flex:1}
.btn-d{height:52px;border-radius:26px;font-size:17px;font-weight:600;display:flex;align-items:center;
  justify-content:center;gap:10px}
.btn-e{height:52px;border-radius:26px;font-size:17px;display:flex;align-items:center;justify-content:center;gap:10px}
.quiet{font-size:15px;min-height:44px;display:flex;align-items:center}
.chip{height:48px;border-radius:24px;font-size:15px;font-weight:500;display:flex;align-items:center;
  justify-content:center;padding:0 16px;flex:1}
.chips{display:flex;gap:8px}
.tile{border-radius:22px;padding:20px 18px;display:flex;flex-direction:column;gap:10px;flex:1;min-height:208px}
.opt{height:58px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:22px}
.hair{height:1px}
.seg{display:flex;border-radius:14px;padding:3px}
.seg div{flex:1;height:44px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:17px}
.stat{height:36px;border-radius:18px;padding:0 12px;font-size:15px;display:flex;align-items:center}
.num{width:34px;height:34px;border-radius:17px;display:flex;align-items:center;justify-content:center;
  font-size:15px;font-weight:600;flex:none}
.thumb{border-radius:14px;flex:none;position:relative}
.badge{position:absolute;left:8px;top:8px;width:26px;height:26px;border-radius:13px;display:flex;
  align-items:center;justify-content:center;font-size:13px;font-weight:600}
.tag{height:28px;border-radius:14px;padding:0 12px;font-size:15px;display:flex;align-items:center}
.emerg{border-radius:20px;padding:18px;display:flex;flex-direction:column;gap:12px}
.field{border-radius:16px;padding:14px 16px;font-size:17px}
.gap4{gap:4px} .gap6{gap:6px} .gap8{gap:8px} .gap10{gap:10px} .gap12{gap:12px} .gap14{gap:14px}
.gap16{gap:16px} .gap18{gap:18px} .gap22{gap:22px} .gap28{gap:28px}
.flex{display:flex;flex-direction:column}
.hrow{display:flex;flex-direction:row;align-items:center} .top{align-items:flex-start} .between{justify-content:space-between}
.center{text-align:center;justify-content:center} .grow{flex:1;min-width:0}
.spacer{flex:1}
.homebar{height:34px;flex:none;display:flex;align-items:flex-end;justify-content:center;padding-bottom:8px}
.homebar div{width:139px;height:5px;border-radius:3px}
.sw{width:180px;flex:none;display:flex;flex-direction:column;gap:6px}
.sw .chip-c{height:72px;border-radius:14px;border:1px solid rgba(30,35,38,0.12)}
.sw b{font-size:14px;font-weight:600;color:#1E2326} .sw span{font-size:12px;color:#4C5156;line-height:1.35}
.panel{background:#FFFDF8;border-radius:24px;padding:32px;display:flex;flex-direction:column;gap:20px}
.panel.dark{background:#111317}
.ptitle{font-size:20px;font-weight:600}
.notes{display:grid;grid-template-columns:repeat(2,minmax(0,460px));gap:16px 40px}
.notes div{font-size:15px;line-height:1.5;color:#3B4044}
.notes b{color:#1E2326}
"""


def themed_css():
    out = []
    for cls, t in (("N", NIGHT), ("D", DAY)):
        css = THEMED.replace("& ", f".{cls} ").replace("&{", f".{cls}{{").replace("& {", f".{cls} {{")
        css = re.sub(r"\$([A-Za-z]+)", lambda m: t[m.group(1)], css)
        out.append(css)
    return "\n".join(out)


# ---- small parts --------------------------------------------------------------------------------------------------
def status_bar(t):
    ink = t["ink"]
    return f"""<div class="sb"><span class="time" style="color:{ink}">9:41</span><div class="island"></div>
<div class="icons"><svg width="18" height="12" viewBox="0 0 18 12"><rect x="0" y="8" width="3" height="4" rx="1" fill="{ink}"/>
<rect x="5" y="5.5" width="3" height="6.5" rx="1" fill="{ink}"/><rect x="10" y="3" width="3" height="9" rx="1" fill="{ink}"/>
<rect x="15" y="0" width="3" height="12" rx="1" fill="{ink}"/></svg>
<svg width="16" height="12" viewBox="0 0 16 12"><path d="M8 11.5 5.6 9a3.4 3.4 0 0 1 4.8 0zM3.5 7a6.4 6.4 0 0 1 9 0l-1.4 1.4a4.4 4.4 0 0 0-6.2 0zM1.3 4.8a9.6 9.6 0 0 1 13.4 0l-1.4 1.4a7.6 7.6 0 0 0-10.6 0z" fill="{ink}"/></svg>
<svg width="27" height="13" viewBox="0 0 27 13"><rect x="0.5" y="0.5" width="23" height="12" rx="3.5" fill="none" stroke="{ink}" stroke-opacity="0.4"/>
<rect x="2" y="2" width="20" height="9" rx="2" fill="{ink}"/><rect x="24.5" y="4" width="2" height="5" rx="1" fill="{ink}" fill-opacity="0.4"/></svg></div></div>"""


def home_bar(t):
    return f'<div class="homebar"><div style="background:{t["ink"]}"></div></div>'


def icon(name, color, size=20):
    p = {
        "menu": '<path d="M4 7h16M4 12h16M4 17h16" stroke="C" stroke-width="1.8" stroke-linecap="round"/>',
        "gear": '<circle cx="12" cy="12" r="3.2" fill="none" stroke="C" stroke-width="1.7"/><path d="M12 2.8v2.4M12 18.8v2.4M2.8 12h2.4M18.8 12h2.4M5.5 5.5l1.7 1.7M16.8 16.8l1.7 1.7M5.5 18.5l1.7-1.7M16.8 7.2l1.7-1.7" stroke="C" stroke-width="1.7" stroke-linecap="round"/>',
        "chev": '<path d="M9 5l7 7-7 7" fill="none" stroke="C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
        "back": '<path d="M15 5l-7 7 7 7" fill="none" stroke="C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
        "sun": '<circle cx="12" cy="12" r="4.2" fill="none" stroke="C" stroke-width="1.8"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" stroke="C" stroke-width="1.8" stroke-linecap="round"/>',
        "plane": '<path transform="rotate(90 12 12)" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" fill="C"/>',
        "walk": '<circle cx="13" cy="4" r="2" fill="C"/><path d="M10 21l2-7 3 3v5M8 12l2-5 4 1 2 4 3 1M10 7l-3 5" fill="none" stroke="C" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "train": '<rect x="5" y="3" width="14" height="14" rx="3" fill="none" stroke="C" stroke-width="1.8"/><path d="M5 11h14M8.5 21l2-4M15.5 21l-2-4" stroke="C" stroke-width="1.8" stroke-linecap="round"/><circle cx="9" cy="14" r="1" fill="C"/><circle cx="15" cy="14" r="1" fill="C"/>',
        "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15zM10 20.5a2 2 0 0 0 4 0" fill="none" stroke="C" stroke-width="1.8" stroke-linejoin="round"/>',
        "phone": '<path d="M6.6 3.5l3 3.5-1.8 2.3a12 12 0 0 0 6.9 6.9l2.3-1.8 3.5 3-1.6 3.1C11.3 20.3 3.7 12.7 3.5 5.1z" fill="C"/>',
        "kit": '<rect x="3" y="7" width="18" height="13" rx="2.5" fill="none" stroke="C" stroke-width="1.8"/><path d="M9 7V5h6v2M12 10.5v6M9 13.5h6" stroke="C" stroke-width="1.8" stroke-linecap="round"/>',
        "share": '<path d="M12 3v12M8 7l4-4 4 4M6 11v9h12v-9" fill="none" stroke="C" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "pin": '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z" fill="C"/><circle cx="12" cy="10" r="2.4" fill="#FFFFFF"/>',
        "play": '<circle cx="12" cy="12" r="9.5" fill="none" stroke="C" stroke-width="2"/><path d="M10 8l6 4-6 4z" fill="C"/>',
    }[name].replace('"C"', f'"{color}"')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">{p}</svg>'


def eyebrow(text):
    return f'<div class="eb">{esc(text)}</div>'


def topbar(t, eb, right="menu", help_=True, back=False):
    left = (f'<div class="hrow gap6 acc body">{icon("back", t["accent"], 22)}<span>Back</span></div>' if back
            else eyebrow(eb))
    parts = [left, '<div class="sp"></div>']
    if help_:
        parts.append('<div class="pill">Help</div>')
    if right == "menu":
        parts.append(f'<div class="circ">{icon("menu", t["ink"], 18)}</div>')
    elif right == "gear":
        parts.append(f'<div class="circ">{icon("gear", t["ink"], 18)}</div>')
    return f'<div class="topbar">{"".join(parts)}</div>'


def thumb(feel, w, h, num=None, radius=14):
    b = f'<div class="badge">{num}</div>' if num else ""
    return f'<div class="thumb" style="width:{w}px;height:{h}px;border-radius:{radius}px;background:{FIELDS.get(feel, FIELDS[None])}">{b}</div>'


def path_svg(t, current=None, w=354, h=180, pts=PATH_PTS, dim=1.0):
    """The day as a path (DayPath.swift): walked solid, the rest dotted, the current stop lit with a halo."""
    acc = t["accent"]
    sx, sy = w / 354, h / 180
    p = [(x * sx, y * sy) for x, y in pts]
    segs = []
    for j in range(len(p) - 1):
        a, b, c, d = p[max(j - 1, 0)], p[j], p[j + 1], p[min(j + 2, len(p) - 1)]
        c1 = (b[0] + (c[0] - a[0]) / 6, b[1] + (c[1] - a[1]) / 6)
        c2 = (c[0] - (d[0] - b[0]) / 6, c[1] - (d[1] - b[1]) / 6)
        walked = current is not None and j + 1 <= current
        dash = "" if walked else ' stroke-dasharray="2 7"'
        op = 1 if walked else 0.85
        segs.append(f'<path d="M{b[0]:.1f} {b[1]:.1f} C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {c[0]:.1f} {c[1]:.1f}" '
                    f'fill="none" stroke="{acc}" stroke-opacity="{op * dim:.2f}" stroke-width="2.5" stroke-linecap="round"{dash}/>')
    dots = []
    for i, (x, y) in enumerate(p):
        lit = current is not None and i <= current
        if current == i:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="21" fill="{acc}" fill-opacity="0.22"/>')
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{acc if lit else t["surface"]}" '
                    f'stroke="{acc}" stroke-width="2" fill-opacity="{dim if lit else 1}" stroke-opacity="{dim}"/>')
        dots.append(f'<text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" font-family="Inter,sans-serif" '
                    f'font-size="12" font-weight="600" fill="{t["onAccent"] if lit else acc}" fill-opacity="{dim}">{i + 1}</text>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(segs)}{"".join(dots)}</svg>'


def door_path(left, right, spring, bottom, closed=True):
    r = (right - left) / 2
    d = f"M{left} {bottom} L{left} {spring} A{r} {r} 0 0 1 {right} {spring} L{right} {bottom}"
    return d + (" Z" if closed else "")


def arch_logo(t, w=180, light=1.0, uid="a"):
    """The ODYS mark (ArchLogo): a doorway of light in a dark frame, the light spilling out in front."""
    h = w * 220 / 180
    top = 160 - light * (160 - 34)
    return f"""<svg width="{w:.0f}" height="{h:.0f}" viewBox="0 0 180 220">
<defs><radialGradient id="halo{uid}" cx="50%" cy="55%" r="50%"><stop offset="0" stop-color="{t['accent']}" stop-opacity="{0.22 * light:.2f}"/>
<stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
<linearGradient id="lt{uid}" x1="0" y1="34" x2="0" y2="160" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['amberLight']}"/>
<stop offset="0.5" stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['amberDeep']}"/></linearGradient>
<linearGradient id="pl{uid}" x1="0" y1="160" x2="0" y2="214" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['accent']}" stop-opacity="0.55"/>
<stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></linearGradient>
<clipPath id="lv{uid}"><rect x="0" y="{top:.1f}" width="180" height="{220 - top:.1f}"/></clipPath></defs>
<ellipse cx="90" cy="110" rx="90" ry="100" fill="url(#halo{uid})"/>
<path d="{door_path(34, 146, 70, 160, False)}" fill="none" stroke="{t['line']}" stroke-width="10"/>
<path d="{door_path(50, 130, 74, 160)}" fill="url(#lt{uid})" clip-path="url(#lv{uid})"/>
<path d="M50 160 L130 160 L176 214 L4 214 Z" fill="url(#pl{uid})" opacity="{light}"/>
<path d="M14 160 L166 160" stroke="{t['line']}" stroke-width="2"/></svg>"""


def rating_arch(t, level=0.0, uid="r"):
    """The rating's arch (RatingArch): dark inside, filling with light to the chosen word."""
    top = 120 - level * (120 - 24)
    return f"""<svg width="150" height="190" viewBox="0 0 120 152">
<defs><linearGradient id="rg{uid}" x1="0" y1="24" x2="0" y2="120" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['amberLight']}"/>
<stop offset="1" stop-color="{t['amberDeep']}"/></linearGradient><clipPath id="rc{uid}"><rect x="0" y="{top:.1f}" width="120" height="{152 - top:.1f}"/></clipPath></defs>
<path d="{door_path(30, 90, 54, 120)}" fill="{t['surface']}"/>
<path d="{door_path(30, 90, 54, 120)}" fill="url(#rg{uid})" clip-path="url(#rc{uid})"/>
<path d="{door_path(30, 90, 54, 120)}" fill="none" stroke="{t['line']}" stroke-width="3"/>
<path d="M30 121 L90 121 L116 150 L4 150 Z" fill="{t['accent']}" opacity="{level * 0.5:.2f}"/></svg>"""


def glyph(color, w=14):
    return (f'<svg width="{w}" height="{w * 18 / 14:.0f}" viewBox="0 0 14 18"><path d="{door_path(1, 13, 7, 18)}" '
            f'fill="{color}"/></svg>')


def breathing_arch(t, sky=None, sun=None):
    """The quiet arch on "Now" (BreathingArch): a glow, the small arch and, by day, the sun where it really is."""
    light = SKIES[sky] if sky and sky != "night" else t["accent"]
    glow = 0.8 if sky and sky != "night" else 0.14
    sun_svg = ""
    if sun is not None:
        import math
        a = math.pi * (1 - sun)
        x, y = 80 + 62 * math.cos(a), 80 + 19.2 - 62 * math.sin(a)
        sun_svg = (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{t["amberLight"]}" fill-opacity="0.5"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{t["accent"]}"/>')
    return f"""<svg width="160" height="160" viewBox="0 0 160 160"><defs><radialGradient id="bg{id(t)}{sky}{sun}" cx="50%" cy="50%" r="50%">
<stop offset="0" stop-color="{light}" stop-opacity="{glow}"/><stop offset="1" stop-color="{light}" stop-opacity="0"/></radialGradient></defs>
<circle cx="80" cy="80" r="78" fill="url(#bg{id(t)}{sky}{sun})"/>
<g transform="translate(60 54)"><path d="M1.4 51.4 L1.4 20 A18.6 18.6 0 0 1 38.6 20 L38.6 51.4 Z" fill="{t['accent']}" fill-opacity="0.72"/></g>{sun_svg}</svg>"""


def phone(t, inner, sky=None, base=None, label="", note="", height=None):
    """A 402 × 874 frame (iPhone 16 Pro in points). The sky fades into the page over its top 440 points."""
    base = base or t["background"]
    bg = f"background:linear-gradient(180deg,{SKIES[sky]} 0px,{base} 440px);background-color:{base}" if sky else f"background:{base}"
    cls = "D" if t is DAY else "N"
    h = f"min-height:{height}px;" if height else ""
    n = f'<div class="note">{esc(note)}</div>' if note else ""
    return (f'<div class="shot"><div class="label">{esc(label)}</div>{n}<div class="phone {cls}" style="{h}{bg}">'
            f'{status_bar(t)}{inner}<div class="spacer"></div>{home_bar(t)}</div></div>')


# ---- the screens --------------------------------------------------------------------------------------------------
def tiles(t):
    return f"""<div class="hrow top gap14">
<div class="tile sel">{icon("sun", t["accent"], 30)}<div class="serif t28 ink">A day out</div>
<div class="body soft">In London, around what you enjoy: your hours, your start, places that fit you.</div></div>
<div class="tile">{icon("plane", t["accent"], 30)}<div class="serif t28 ink">A trip</div>
<div class="body soft">A few days away: getting there, a place to stay, and days that fit you.</div></div></div>"""


def row_card(t, feel, title, sub, right=None):
    r = right or icon("chev", t["muted"], 20)
    return f"""<div class="card hrow gap16" style="padding:12px 16px 12px 12px">{thumb(feel, 56, 56)}
<div class="grow flex"><div class="serif t22 ink">{esc(title)}</div><div class="body muted">{esc(sub)}</div></div>{r}</div>"""


def home_before(t, sky):
    return f"""<div class="pad gap22" style="padding-top:22px">{topbar(t, "Good morning")}
<div class="serif display ink" style="margin-top:14px">Where to next?</div>{tiles(t)}
<div class="body soft" style="margin-top:8px">Coming up</div>
{row_card(t, "Big views", "Saturday 31 October", "4 stops · done by 17:00")}
<div class="body soft" style="margin-top:8px">Your trips</div>
{row_card(t, "Awe", "London", "8–13 Nov · 5 nights")}</div>"""


def stop_rows(t, current):
    rows = []
    for i, s in enumerate(STOPS):
        lit = i <= current
        title_cls = "muted" if i < current else "ink"
        rows.append(f"""<div class="hrow gap14" style="padding:12px 0"><div class="num{' lit' if lit else ''}">{i + 1}</div>
<div class="grow"><div class="body {title_cls}">{esc(s["title"])}</div><div class="sub muted">{s["arrive"]} · {FEELS[i]}</div></div></div>""")
        if i < len(STOPS) - 1:
            rows.append('<div class="hair" style="margin-left:48px"></div>')
    return "".join(rows)


def home_today(t, sky, current=1):
    return f"""<div class="pad gap16" style="padding-top:22px">{topbar(t, "Good morning")}
<div style="margin-top:22px">{eyebrow("Today · Sat 31 Oct")}</div><div class="serif h1 ink">{esc(HEADLINE)}</div>
<div class="card" style="padding:16px 16px 8px">{path_svg(t, current, 322, 180)}{stop_rows(t, current)}</div>
<div class="btn-p">Back to now</div><div class="quiet muted center">See the whole day</div>
<div class="serif h1 ink" style="margin-top:20px">And next?</div>{tiles(t)}</div>"""


def home_after(t, sky):
    words = ["Unforgettable", "Great", "Good"]
    cards = "".join(f"""<div class="card hrow gap14" style="padding:14px 16px 14px 14px">{thumb(FEELS[i + 1], 52, 52)}
<div class="grow"><div class="body ink">{esc(STOPS[i + 1]["title"])}</div><div class="sub muted">{STOPS[i + 1]["arrive"]}</div></div>
<div class="it t22 acc">{w}</div></div>""" for i, w in enumerate(words))
    return f"""<div class="pad gap14" style="padding-top:22px">{topbar(t, "Good evening")}
<div style="margin-top:22px">{eyebrow("Earlier today")}</div><div class="serif h1 ink">{esc(HEADLINE)}</div>
{cards}<div class="quiet muted center">See the day</div>
<div class="serif h1 ink" style="margin-top:20px">And next?</div>{tiles(t)}</div>"""


def stop_card(t, i, with_travel=True):
    s = STOPS[i]
    mode = "walk" if s.get("travel_mode") == "walk" else "train"
    travel = (f'<div class="hrow top gap10" style="padding:6px 4px">{icon(mode, t["muted"], 20)}'
              f'<div class="sub muted grow">{esc(s["travel_text"])}</div></div>') if with_travel else ""
    return f"""{travel}<div class="card hrow top gap16" style="padding:12px">{thumb(FEELS[i], 90, 110, i + 1)}
<div class="grow flex gap4" style="padding-top:6px"><div class="body muted">{s["arrive"]}–{s["depart"]} · {FEELS[i]}</div>
<div class="serif t24 ink">{esc(s["title"])}</div></div></div>"""


def reminder_ask(t):
    return f"""<div class="card outlined gap12" style="padding:18px"><div class="hrow top gap12">{icon("bell", t["accent"], 20)}
<div class="serif t21 ink">Remind me to rate each stop?</div></div>
<div class="sub muted">One reminder after each stop, set on this phone only. Your ratings are what make the next plan better.</div>
<div class="hrow gap10"><div class="btn-s">Yes, remind me</div><div class="btn-s">No thanks</div></div></div>"""


def plan_top(t):
    tot = PLAN["totals"]
    return f"""{topbar(t, PLAN["title"], right="gear")}
<div class="serif h1 ink" style="margin-top:18px">{esc(HEADLINE)}</div><div class="serif t21 soft">{esc(SUBLINE)}</div>
<div class="hrow gap8" style="flex-wrap:wrap"><div class="stat">£{tot["cost_gbp"]:.0f} per person</div>
<div class="stat">{tot["walk_km"]} km walking</div><div class="stat">Done by {tot["finish"]}</div></div>
<div class="sub muted">£{tot["spend_gbp"]:.0f} food and entry, £{tot["transport_gbp"]:.0f} Tube or bus. Start: Charing Cross station at 12:00 · 4 stops, including lunch.</div>
<div class="seg" style="margin-top:6px"><div class="on">List</div><div class="off">Map</div></div>"""


def plan(t, sky):
    stops = "".join(stop_card(t, i) for i in range(len(STOPS)))
    return f"""<div class="pad gap12" style="padding-top:22px;padding-bottom:12px">{plan_top(t)}
<div class="deepcard card" style="padding:12px 16px">{path_svg(t, None, 322, 180)}</div>{stops}
<div style="margin-top:8px">{reminder_ask(t)}</div><div class="btn-p" style="margin-top:8px">Start the day</div>
<div class="hrow gap10"><div class="btn-s">Plan again</div><div class="btn-s">Another day</div></div></div>"""


def plan_reveal(t, sky):
    return f"""<div class="pad gap12" style="padding-top:22px">{plan_top(t)}
<div class="deepcard card" style="padding:12px 16px">{path_svg(t, None, 322, 180, dim=0.35)}</div>{stop_card(t, 0)}
<div style="opacity:0.35">{stop_card(t, 1, False)}</div></div>"""


def way_in(t, s):
    steps = s.get("approach_steps") or []
    out = []
    for i, st in enumerate(steps):
        mark = '<div class="dot" style="width:22px;height:22px;border-radius:11px"></div>' if i == 0 else \
            '<div class="ringdot" style="width:16px;height:16px;border-radius:8px;margin:3px"></div>'
        rail = '<div class="rail" style="width:2px;flex:1;margin:4px 0 0 10px"></div>' if i < len(steps) - 1 else ""
        reveal = '<div class="eb acc" style="margin-top:2px">The reveal</div>' if i == len(steps) - 1 and s.get("reveal") else ""
        out.append(f"""<div class="hrow top gap14"><div style="display:flex;flex-direction:column;width:22px;align-self:stretch">{mark}{rail}</div>
<div class="grow" style="padding-bottom:16px"><div class="sub muted">{esc(st["label"])}</div><div class="body ink">{esc(st["text"])}</div>{reveal}</div></div>""")
    return f'<div class="card gap10 r20" style="padding:18px"><div class="eb muted" style="color:inherit"><span class="muted">The way in</span></div>{"".join(out)}</div>'


def now_bottom(t):
    return """<div class="hrow between"><div class="quiet muted">See the whole day</div><div class="quiet muted">Help</div></div>"""


def location_ask(t):
    return f"""<div class="card gap10"><div class="body semi ink">Use your location while you're out?</div>
<div class="sub soft">I'll show how far your next stop is, and ask how it felt once you've left. Your location stays on your phone.</div>
<div class="hrow gap10"><div class="btn-s">Yes, use it</div><div class="btn-s">No thanks</div></div></div>"""


def now_way(t, sky):
    s = STOPS[1]
    return f"""<div class="pad gap16" style="padding:40px 28px 0">{eyebrow("Next · around " + s["arrive"])}
<div class="serif hero ink">{esc(s["title"])}</div>{way_in(t, s)}
<div style="display:flex;justify-content:center">{path_svg(t, 1, 346, 120)}</div>
<div class="btn-s" style="flex:none">Directions</div><div class="btn-p">I'm here</div>
<div class="quiet muted">Didn't go? Skip this stop</div><div class="quiet acc">Plans changed? Re-plan the rest of today</div>
{location_ask(t)}{now_bottom(t)}</div>"""


def next_up(t, s):
    return f"""<div class="outlined" style="border-radius:18px;padding:16px 18px;display:flex;flex-direction:column;gap:4px">
<div class="sub muted">Next, around {s["arrive"]}</div><div class="body ink">{esc(s["title"])}</div>
<div class="sub ter">{esc(s["travel_text"])}</div></div>"""


def now_here(t, sky, glow=False):
    s = STOPS[1]
    return f"""<div class="pad gap16" style="padding:40px 28px 0">{eyebrow("Now")}
<div class="serif hero ink">{esc(s["title"])}</div><div class="it t21 ink">{esc(s["what"])}</div>
<div class="body soft">Enjoy it. I'll stay quiet until you need me.</div>
<div style="display:flex;justify-content:center;padding:12px 0">{breathing_arch(t, sky, 0.42 if sky != "night" else None)}</div>
{next_up(t, STOPS[2])}<div class="btn-p">I'm done here</div><div class="quiet muted">Didn't go? Skip this stop</div>
<div class="quiet acc">Plans changed? Re-plan the rest of today</div>{now_bottom(t)}</div>"""


def options(t, chosen=None):
    words = ["Disappointing", "Fine", "Good", "Great", "Unforgettable"]
    return "".join(f'<div class="opt serif{" sel" if i == chosen else ""}">{w}</div>' for i, w in enumerate(words))


def rating_top(t):
    s = STOPS[1]
    return f"""<div class="hrow" style="justify-content:flex-end;padding-top:6px"><div class="close">Close</div></div>
{eyebrow("Just finished")}<div class="serif ink" style="font-size:30px;line-height:1.15">How did {esc(s["title"])} feel?</div>"""


def rating(t, sky):
    return f"""<div class="pad gap14" style="padding-top:4px">{rating_top(t)}
<div style="display:flex;justify-content:center;padding:4px 0">{rating_arch(t, 0, "e" + sky)}</div>{options(t)}</div>"""


def rating_chosen(t, sky):
    return f"""<div class="pad gap14" style="padding-top:4px">{rating_top(t)}
<div style="display:flex;justify-content:center;padding:4px 0">{rating_arch(t, 0.8, "c" + sky)}</div>{options(t, 3)}
<div class="sub muted" style="margin-top:6px">Would you bring someone here? (optional)</div>
<div class="chips"><div class="chip on" style="height:44px">Yes</div><div class="chip" style="height:44px">No</div></div>
<div class="btn-p">Save</div></div>"""


def rating_saved(t, sky):
    return f"""<div class="pad gap14" style="padding-top:4px">{rating_top(t)}
<div style="display:flex;justify-content:center;padding:4px 0">{rating_arch(t, 0.8, "s" + sky)}</div>
<div class="it t19 soft center" style="text-align:center">Thank you. That helps the next day fit better.</div>
<div class="btn-p">On to the next stop</div><div class="btn-s" style="flex:none">{icon("share", t["ink"], 18)}Share this moment</div></div>"""


def rating_offline(t, sky):
    return f"""<div class="pad gap14" style="padding-top:4px">{rating_top(t)}
<div style="display:flex;justify-content:center;padding:4px 0">{rating_arch(t, 0.8, "o" + sky)}</div>
<div class="it t19 soft" style="text-align:center">Thank you. That helps the next day fit better.</div>
<div class="foot muted" style="text-align:center">Saved on your phone. It'll send the next time you open ODYS with signal.</div>
<div class="btn-p">On to the next stop</div></div>"""


def day_end(t, sky):
    return f"""<div class="pad gap16" style="padding:40px 28px 0">{eyebrow("That's the day")}
<div class="serif hero ink">Thanks for today.</div><div class="body soft">Every stop you rated makes the next day fit you better.</div>
<div class="flex gap22" style="display:flex;flex-direction:column;margin-top:8px">
<div class="flex gap10" style="display:flex;flex-direction:column"><div class="body ink">Was today worth what you spent on it?</div>
<div class="chips"><div class="chip">Not quite</div><div class="chip on">Yes</div><div class="chip">More than that</div></div></div>
<div class="flex gap10" style="display:flex;flex-direction:column"><div class="body ink">Would you do this day again?</div>
<div class="chips"><div class="chip">Yes</div><div class="chip">No</div></div></div></div>
<div style="display:flex;justify-content:center;padding:8px 0">{breathing_arch(t, sky)}</div>
<div class="btn-p">See the whole day</div><div class="hrow" style="justify-content:flex-end"><div class="quiet muted">Help</div></div></div>"""


def share_preview(t, sky):
    s = STOPS[1]
    card = f"""<div style="background:#F4EBDD;border-radius:26px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.45)">
<div style="height:236px;background:radial-gradient(circle at 40% 20%,#86A870 0%,#3B5532 60%,#141A12 100%);position:relative">
<div class="it" style="position:absolute;left:16px;top:16px;padding:6px 14px;border-radius:18px;background:rgba(17,19,23,0.55);color:#FFC665;font-size:17px">Rated: Unforgettable</div></div>
<div style="padding:20px 20px 18px;display:flex;flex-direction:column;gap:8px">
<div style="font-size:15px;color:#6B5E4C">A moment from my day</div>
<div class="serif" style="font-size:25px;line-height:1.15;color:#111317">{esc(s["title"])}</div>
<div class="it" style="font-size:17px;line-height:1.3;color:#3A3128">I loved Uber Boat on the Thames, and this has views too.</div>
<div class="hrow gap10" style="margin-top:14px">{glyph("#E5A93C", 11)}<span style="font-size:15px;color:#6B5E4C">Planned with ODYS</span></div>
<div style="font-size:10px;color:#6B5E4C">Photo: AndyScott, CC0, Wikimedia Commons (cropped)</div></div></div>"""
    return f"""<div class="pad gap18" style="padding-top:8px"><div class="hrow" style="justify-content:center;height:44px"><div class="serif t19 ink">Share this moment</div></div>{card}
<div class="hrow between"><div class="body ink">Include the line about why</div><div style="width:51px;height:31px;border-radius:16px;background:{t['accent']};position:relative"><div style="position:absolute;right:2px;top:2px;width:27px;height:27px;border-radius:14px;background:#FFFFFF"></div></div></div>
<div class="foot muted" style="text-align:center">Your rating and the line about why go with it, and nothing else about you.</div>
<div class="btn-p">Send to a friend</div><div class="btn-s" style="flex:none">Not now</div></div>"""


def trip(t, sky):
    days = []
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
    for i, d in enumerate(TRIP_DAYS):
        line = (d.get("plan") or {}).get("feel_line") or "Travel home: the way back to the stay, then on to the airport"
        state = '<div class="sub acc">Ready</div>' if i < 2 else '<div class="sub muted">Planned when you open it</div>'
        days.append(f"""<div class="hrow top gap16" style="padding:14px 0"><div style="width:44px;text-align:center"><div class="sub muted">{names[i]}</div>
<div class="t24 ink semi">{8 + i}</div></div><div class="grow"><div class="body ink">{esc(line)}</div>{state}</div></div>
<div class="hair"></div>""")
    return f"""<div class="pad gap16" style="padding-top:22px">{topbar(t, "", right=None, back=True)}
<div style="margin-top:14px">{eyebrow("8–13 Nov · 5 nights")}</div><div class="serif display ink" style="font-size:52px">London</div>
<div class="body soft">A curious, peaceful trip · 1 traveller</div>
<div class="card gap8 r20" style="padding:20px"><div class="hrow between"><div class="eb muted">1 · Getting there</div><div class="tag saved">Saved, not booked</div></div>
<div class="serif t24 ink">Sample Air · 20:55 → 00:22</div><div class="body soft">Skyscanner · £316</div></div>
<div class="quiet muted">Remove this flight from the trip</div>
<div class="card gap8 r20" style="padding:20px"><div class="hrow between"><div class="eb muted">2 · Where you'll stay</div><div class="tag booked">Booked</div></div>
<div class="serif t24 ink">Sample hotel U, Covent Garden</div><div class="body soft">Booking.com · £1,621 for 5 nights</div></div>
<div class="quiet muted">Remove this stay from the trip</div>
<div class="hrow between" style="margin-top:8px"><div class="eb muted">3 · Your days</div><div class="body muted">6 days</div></div>
<div class="hrow between top"><div class="body soft grow">09:30–19:00 · 3 places a day · travelling light</div><div class="body acc">Change</div></div>
<div>{"".join(days)}</div></div>"""


def you(t, sky):
    items = "".join(f'<div class="serif t19 ink" style="padding:12px 0">{esc(x)}</div><div class="hair"></div>' for x in LEARNED)
    return f"""<div class="pad gap18" style="padding-top:14px;padding-bottom:24px"><div class="hrow gap6 acc body" style="min-height:44px">{icon("back", t["accent"], 22)}<span>Back</span></div>
<div class="serif ink" style="font-size:36px">You</div>
<div class="emerg"><div class="t body semi">Emergency in the UK</div><div class="x body">If you or someone else is in danger, call 999 first.</div><div class="btn-d">Call 999</div></div>
<div class="card gap8 r20" style="padding:18px"><div class="hrow between"><div class="body semi ink">Talk to a person</div>{icon("chev", t["muted"], 18)}</div>
<div class="sub ter">Something wrong with a stop, a booking or how you feel? A real person replies here, usually within a few hours.</div></div>
<div><div class="eb muted" style="margin-bottom:6px"><span class="muted">What you've told us</span></div>{items}</div>
<div class="flex gap10" style="display:flex;flex-direction:column"><div class="eb"><span class="muted">The light</span></div>
<div class="seg"><div class="on semi" style="font-size:15px">Follow the sky</div><div class="off" style="font-size:15px">Always dark</div></div>
<div class="foot muted">By day the app is light, and it turns dark after sunset, following London's sky. Always dark keeps the night look.</div></div>
<div class="hrow between muted sub" style="min-height:44px"><span>Your data · what's stored and how to delete it</span>{icon("chev", t["muted"], 14)}</div></div>"""


def safety(t, sky):
    return f"""<div class="pad gap18" style="padding-top:4px;padding-bottom:24px"><div class="hrow" style="justify-content:flex-end;padding-top:6px"><div class="close">Close</div></div>
<div class="serif h1 ink">Help &amp; safety</div>
<div class="emerg"><div class="t body semi">Emergency</div><div class="x body">If you or someone else is in danger or hurt, call 999 now.</div>
<div class="btn-d">{icon("phone", "#FFFFFF", 20)}Call 999</div>
<div class="x sub">Urgent medical help that isn't an emergency: call NHS 111. You can ask for an interpreter.</div>
<div class="btn-e">{icon("kit", t["emergencyTitle"], 20)}Call 111</div>
<div class="x sub">Need to talk to someone, day or night? Samaritans answer free on <b>116 123</b>.</div></div>
<div class="card gap12 r20" style="padding:18px"><div class="body semi ink">I feel unsafe or something's wrong</div>
<div class="sub muted">This reaches a real person, not a bot. They'll reply here in Help &amp; safety, usually within a few hours. It isn't watched through the night: a message sent late is answered the next morning.</div>
<div class="field" style="height:120px">What's happening? (optional)</div><div class="field">Phone or email (optional)</div>
<div class="foot muted">Used only to reply to this message, and deleted once it's sorted (after 30 days at the latest).</div>
<div class="btn-s" style="flex:none">Send to a person</div></div>
<div class="flex gap6" style="display:flex;flex-direction:column"><div class="sub muted">Your messages</div>
<div class="card gap6"><div class="body ink">The lift at the Garden was closed.</div><div class="foot muted">No reply yet. A person replies, usually within a few hours (the next morning if it was sent late). In an emergency, call 999.</div></div></div></div>"""


def welcome(t, sky):
    return f"""<div class="pad gap16" style="padding:30px 28px 0;align-items:stretch">
<div style="display:flex;flex-direction:column;align-items:center;gap:22px">{arch_logo(t, 190, 1, "w" + sky)}
<div class="serif ink" style="font-size:22px;letter-spacing:7.5px;padding-left:7.5px">ODYS</div></div>
<div class="serif display ink" style="margin-top:22px;font-size:46px">Days out that fit you.</div>
<div class="body soft">Tell me how you want a day to feel. I'll plan real moments around it, including how you arrive.</div>
<div class="card hrow gap16 r20" style="padding:18px 18px 18px 16px;margin-top:10px"><div style="width:52px;height:52px;border-radius:26px;flex:none;background:radial-gradient(circle at 40% 35%,#6B5640 0%,#2A231C 100%);display:flex;align-items:center;justify-content:center" class="serif"><span style="color:#F4EBDD;font-size:22px">A</span></div>
<div class="grow flex gap8" style="display:flex;flex-direction:column"><div class="sub soft">This is a research test, run by one person: Abram, in London.</div><div class="sub acc">Watch his short hello</div></div></div>
<div class="btn-p" style="margin-top:28px">Show me an example day</div>
<div class="hrow between"><div class="quiet muted">Skip the example</div><div class="quiet muted">Got a tester code?</div></div></div>"""


def progress(t, step, of=14):
    return f"""<div class="hrow between"><div class="eb">Question {step} of {of}</div><div class="sub muted">Skip the rest</div></div>
<div class="track" style="height:5px;border-radius:3px"><div class="fill" style="height:5px;border-radius:3px;width:{step / of * 100:.0f}%"></div></div>"""


def places(t, sky):
    return f"""<div class="pad gap14" style="padding-top:14px"><div class="hrow gap4 acc sub" style="min-height:44px">‹ How you want to feel</div>
{progress(t, 3)}<div style="height:260px;border-radius:22px;background:linear-gradient(180deg,#9DB3C2 0%,#6E7A80 45%,#3A3330 100%);position:relative;margin-top:6px">
<div class="serif" style="position:absolute;left:22px;bottom:18px;font-size:40px;color:#F4EBDD">British Museum</div></div>
<div class="foot muted">“Great Court, British Museum” by Jim Osley, CC BY-SA 2.0, Wikimedia Commons (resized)</div>
<div class="body soft" style="margin-top:4px">Have you been? How did it feel?</div>
<div class="hrow gap10"><div class="opt grow" style="font-family:Inter,sans-serif;font-size:17px">Loved it</div><div class="opt sel grow" style="font-family:Inter,sans-serif;font-size:17px">It was fine</div></div>
<div class="hrow gap10"><div class="opt grow" style="font-family:Inter,sans-serif;font-size:17px">Didn't enjoy it</div><div class="opt grow" style="font-family:Inter,sans-serif;font-size:17px">Haven't been</div></div>
<div class="it t21 acc">Got it: big museums full of history.</div>
<div class="hrow between" style="margin-top:16px"><div class="quiet muted" style="opacity:0.6">Previous</div><div class="quiet muted">Not sure, skip</div></div></div>"""


def day_option(t, name, lines, chosen=False):
    rows = "".join(f'<div class="body ink">{esc(x)}</div>' for x in lines)
    btn = (f'<div class="chip on" style="flex:none;align-self:flex-start;padding:0 22px;height:48px">Chosen</div>' if chosen else
           f'<div class="chip" style="flex:none;align-self:flex-start;padding:0 22px;height:48px;border-color:{t["accent"]};color:{t["accent"]}">Choose this day</div>')
    return f"""<div class="card outlined gap10 r20" style="padding:20px 22px"><div class="hrow between"><div class="serif t28 ink">{name}</div>
<div class="sub muted">Made up</div></div>{rows}{btn}</div>"""


def this_or_that(t, sky):
    a = ["Up to 50 min between stops", "Mild and dry at the outdoor stops", "5 stops, packed", "Mostly quiet",
         "£60 per person", "About 8 km walking"]
    b = ["Up to 30 min between stops", "Rainy at the outdoor stops", "3 stops, relaxed", "Busy at 2 stops",
         "£60 per person", "About 3 km walking"]
    return f"""<div class="pad gap14" style="padding-top:14px"><div class="hrow gap4 acc sub" style="min-height:44px">‹ Places you've been</div>
{progress(t, 9)}<div class="serif display ink" style="margin-top:8px">Which day sounds more like you?</div>
<div class="body muted">There are no wrong answers.</div>{day_option(t, "Example day A", a)}
<div class="it t19 muted" style="text-align:center">or</div>{day_option(t, "Example day B", b, True)}</div>"""


def learned(t, sky):
    items = "".join(f'<div class="hrow top gap16"><div style="padding-top:10px">{glyph(t["accent"], 14)}</div>'
                    f'<div class="serif ink" style="font-size:25px;line-height:1.15">{esc(x)}</div></div>' for x in LEARNED)
    return f"""<div class="pad gap16" style="padding-top:14px"><div class="hrow gap4 acc sub" style="min-height:44px">‹ A great moment</div>
<div class="hrow top gap16"><div style="display:flex;flex-direction:column;align-items:center;gap:6px"><div class="card" style="width:58px;height:104px;align-items:center;padding:12px 0">{icon("play", t["accent"], 34)}</div>
<div class="foot muted" style="text-align:center">A note<br>from Abram</div></div>
<div class="grow flex gap8" style="display:flex;flex-direction:column;padding-top:6px"><div class="eb">So far, I've learned…</div>
<div class="sub muted">From your answers only. Nothing here is a score.</div></div></div>
<div class="flex gap14" style="display:flex;flex-direction:column">{items}</div>
<div class="btn-p" style="margin-top:12px">Looks right</div><div class="btn-s" style="flex:none">Change something</div></div>"""


# ---- system: notifications, permissions, errors --------------------------------------------------------------------
APP_ICON = (f'<div style="width:38px;height:38px;border-radius:9px;background:#111317;display:flex;align-items:center;'
            f'justify-content:center;flex:none">{glyph("#FFC665", 15)}</div>')


def lock_screen(t, sky):
    wall = ("linear-gradient(180deg,#1A2030 0%,#2A2440 45%,#3A2A2A 100%)" if sky == "night"
            else "linear-gradient(180deg,#9FB8C8 0%,#DDEBE6 50%,#E8D2B8 100%)")
    ink = "#FFFFFF" if sky == "night" else "#1E2326"
    note_bg = "rgba(40,40,46,0.72)" if sky == "night" else "rgba(255,255,255,0.72)"
    note_ink = "#FFFFFF" if sky == "night" else "#111317"
    sub = "rgba(255,255,255,0.7)" if sky == "night" else "rgba(17,19,23,0.62)"
    s = STOPS[1]
    return f"""<div class="shot"><div class="label">Rating reminder · lock screen · {sky}</div>
<div class="note">A local notification, 10 minutes after a stop's planned end, only if they said yes. Tapping it opens that stop.</div>
<div class="phone" style="background:{wall}"><div class="sb"><span class="time" style="color:{ink}">14:33</span><div class="island"></div><div></div></div>
<div style="display:flex;flex-direction:column;align-items:center;padding-top:28px;color:{ink}">
<div style="font-size:21px;font-weight:600">Saturday 31 October</div><div style="font-size:96px;font-weight:700;line-height:1;letter-spacing:-2px">14:33</div></div>
<div class="spacer"></div><div style="margin:0 12px 120px;padding:14px;border-radius:22px;background:{note_bg};display:flex;gap:12px">{APP_ICON}
<div class="grow"><div class="hrow between"><span style="font-size:15px;font-weight:600;color:{note_ink}">How was it?</span><span style="font-size:13px;color:{sub}">now</span></div>
<div style="font-size:15px;line-height:1.35;color:{note_ink}">{esc(s["title"])}. One tap to rate it.</div></div></div></div></div>"""


def banner_over_now(t, sky):
    s = STOPS[1]
    bg = "rgba(40,40,46,0.88)" if t is NIGHT else "rgba(255,255,255,0.9)"
    ink = "#FFFFFF" if t is NIGHT else "#111317"
    banner = f"""<div style="position:absolute;left:10px;right:10px;top:54px;padding:14px;border-radius:22px;background:{bg};display:flex;gap:12px;box-shadow:0 10px 30px rgba(0,0,0,0.25)">{APP_ICON}
<div class="grow"><div class="hrow between"><span style="font-size:15px;font-weight:600;color:{ink}">How was it?</span><span style="font-size:13px;color:{ink};opacity:0.6">now</span></div>
<div style="font-size:15px;line-height:1.35;color:{ink}">{esc(s["title"])}. One tap to rate it.</div></div></div>"""
    return now_here(t, sky) + banner


def ios_alert(t, title, text, buttons, under):
    """An iOS system alert over a dimmed screen (the system draws it; ODYS only sets the words in the middle)."""
    bg = "rgba(37,37,40,0.94)" if t is NIGHT else "rgba(242,242,247,0.96)"
    ink = "#FFFFFF" if t is NIGHT else "#000000"
    blue = "#0A84FF" if t is NIGHT else "#007AFF"
    sep = "rgba(255,255,255,0.16)" if t is NIGHT else "rgba(60,60,67,0.29)"
    stacked = len(buttons) > 2
    if stacked:
        btns = "".join(f'<div style="height:44px;border-top:1px solid {sep};display:flex;align-items:center;justify-content:center;font-size:17px;color:{blue}">{esc(b)}</div>' for b in buttons)
    else:
        btns = (f'<div style="display:flex;border-top:1px solid {sep}">' + "".join(
            f'<div style="flex:1;height:44px;display:flex;align-items:center;justify-content:center;font-size:17px;color:{blue};{"font-weight:600;" if i == len(buttons) - 1 else ""}{"border-left:1px solid " + sep if i else ""}">{esc(b)}</div>'
            for i, b in enumerate(buttons)) + "</div>")
    return f"""{under}<div style="position:absolute;inset:0;background:rgba(0,0,0,0.4)"></div>
<div style="position:absolute;left:64px;right:64px;top:300px;border-radius:14px;background:{bg};overflow:hidden">
<div style="padding:19px 16px 16px;display:flex;flex-direction:column;gap:4px;text-align:center"><div style="font-size:17px;font-weight:600;color:{ink}">{esc(title)}</div>
<div style="font-size:13px;line-height:1.35;color:{ink}">{esc(text)}</div></div>{btns}</div>"""


def notif_permission(t, sky):
    return ios_alert(t, "“ODYS” Would Like to Send You Notifications",
                     "Notifications may include alerts, sounds and icon badges. These can be configured in Settings.",
                     ["Don't Allow", "Allow"], plan_reveal(t, sky))


def location_permission(t, sky):
    return ios_alert(t, "Allow “ODYS” to use your location?",
                     "While you're out, ODYS shows how far your next stop is and notices when you've arrived and left, "
                     "so it can ask how it felt. Your location stays on your phone, unless you choose to start a plan "
                     "from where you are.", ["Allow Once", "Allow While Using App", "Don't Allow"], now_way(t, sky))


def error_alert(t, sky):
    return ios_alert(t, "Something went wrong", "You seem to be offline. Check your connection and try again.",
                     ["OK"], home_before(t, sky))


def waking(t, sky):
    bar = f"""<div style="position:absolute;left:16px;right:16px;top:58px;padding:12px 16px;border-radius:16px;background:{t['surfaceHigh']};display:flex;gap:10px;align-items:center;box-shadow:0 8px 24px rgba(0,0,0,0.2)">
<div style="width:16px;height:16px;border-radius:8px;border:2px solid {t['accent']};border-right-color:transparent"></div><div class="sub ink">Waking up the planner. This can take up to a minute.</div></div>"""
    return home_before(t, sky) + bar


def android_shade(t, sky):
    s = STOPS[1]
    dark = t is NIGHT
    bg = "#1B1B1F" if dark else "#F1EFF4"
    card = "#2B2930" if dark else "#FFFFFF"
    ink = "#E6E1E5" if dark else "#1C1B1F"
    sub = "#CAC4D0" if dark else "#49454F"
    return f"""<div class="shot"><div class="label">Rating reminder · Android notification shade · {sky}</div>
<div class="note">The same reminder on Android (channel "Rating reminders"). Drawn by the system: ODYS sets the words and the small arch icon.</div>
<div class="phone" style="background:{bg}"><div class="sb" style="padding:6px 24px 0"><span class="time" style="color:{ink};font-size:15px">14:33</span><div></div></div>
<div style="padding:8px 16px;display:flex;flex-direction:column;gap:10px"><div style="color:{ink};font-size:15px">Saturday 31 October</div>
<div style="background:{card};border-radius:24px;padding:16px;display:flex;gap:14px"><div style="width:36px;height:36px;border-radius:18px;background:#FFC665;display:flex;align-items:center;justify-content:center;flex:none">{glyph("#111317", 12)}</div>
<div class="grow"><div style="font-size:12px;color:{sub}">ODYS · now</div><div style="font-size:15px;font-weight:600;color:{ink};margin-top:2px">How was it?</div>
<div style="font-size:14px;line-height:1.4;color:{sub}">{esc(s["title"])}. One tap to rate it.</div></div></div></div></div></div>"""


# ---- foundations ----------------------------------------------------------------------------------------------------
def lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


ROLES = [("background", "The page"), ("calm", "“Now”: quieter while you're out"), ("surface", "Cards and tiles"),
         ("deep", "The path's box and the map"), ("surfaceHigh", "A chosen tab, a field"),
         ("selected", "A chosen tile: a little warmth"), ("ink", "Text"), ("inkSoft", "Second text"),
         ("inkTertiary", "Third text"), ("muted", "Labels, quiet buttons"), ("line", "The arch's frame"),
         ("accent", "The one light: actions, the path"), ("amberDeep", "Eyebrows, pressed"),
         ("amberLight", "Top of the arch's light"), ("onAccent", "Text on amber"),
         ("danger", "Only “Call 999”"), ("dangerInk", "Red as text"), ("emergencyBg", "The emergency card")]
TEXT_TOKENS = {"ink", "inkSoft", "inkTertiary", "muted", "accent", "amberDeep", "dangerInk"}


def swatches(t, name):
    cells = []
    for key, role in ROLES:
        c = t[key]
        r = f" · {ratio(c, t['background']):.1f}:1 on the page" if key in TEXT_TOKENS else ""
        cells.append(f'<div class="sw"><div class="chip-c" style="background:{c}"></div><b>{key}</b>'
                     f'<span>{c}{r}<br>{esc(role)}</span></div>')
    return (f'<div class="panel"><div class="ptitle">{name}</div>'
            f'<div style="display:grid;grid-template-columns:repeat(6,180px);gap:22px 20px">{"".join(cells)}</div></div>')


def skies_panel():
    cells = "".join(f'<div class="sw"><div class="chip-c" style="background:linear-gradient(180deg,{c},{NIGHT["background"] if k == "night" else DAY["background"]})"></div>'
                    f'<b>{k}</b><span>{c}</span></div>' for k, c in SKIES.items())
    rules = ("Night once the sun is 4° below the horizon (or “Always dark”). Rain when today's forecast gives 60% or "
             "more. Golden in the last 90 minutes before sunset. Morning until 2 hours after sunrise. Otherwise day. "
             "Worked out on the phone for London; the light changes only when a screen opens, never while you look.")
    return (f'<div class="panel"><div class="ptitle">The sky at the top of the main screens</div>'
            f'<div class="hrow gap22">{cells}</div><div style="font-size:15px;line-height:1.5;color:#3B4044;max-width:900px">{rules}</div></div>')


def type_panel():
    rows = [("Hero · Newsreader 44", "font-size:44px", "The Garden at 120", True),
            ("Display · Newsreader 40", "font-size:40px", "Where to next?", True),
            ("H1 · Newsreader 34", "font-size:34px", "A curious, peaceful day", True),
            ("Title · Newsreader 28", "font-size:28px", "A day out", True),
            ("Option · Newsreader 22", "font-size:22px", "Unforgettable", True),
            ("Reaction · Newsreader Italic 20, amber", "font-size:20px;font-style:italic;color:#80521A", "Got it: big museums full of history.", True),
            ("Body · system 17", "font-size:17px", "Tell me how you want a day to feel.", False),
            ("Subheadline · system 15", "font-size:15px", "Getting there: about 6 min on foot.", False),
            ("Eyebrow · system 13 medium, caps, +1 tracking", "font-size:13px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#6E4614", "Next · around 13:33", False)]
    out = "".join(f'<div class="hrow gap22" style="align-items:baseline"><div style="width:330px;font-size:13px;color:#4C5156;flex:none">{esc(a)}</div>'
                  f'<div style="{s};{"font-family:Newsreader,Georgia,serif;" if serif else ""}color:{"#1E2326" if "color" not in s else ""}">{esc(x)}</div></div>'
                  for a, s, x, serif in rows)
    return (f'<div class="panel"><div class="ptitle">Type</div>{out}<div style="font-size:14px;color:#4C5156;max-width:900px">'
            f'Newsreader for what matters (titles, answers, reactions); the system font for the rest (SF Pro on iPhone, '
            f'Roboto on Android; Inter in this file). Every size grows with the phone\'s text-size setting.</div></div>')


def parts_panel(t, name):
    cls = "D" if t is DAY else "N"
    pnl = "panel" + ("" if t is DAY else " dark")
    return f"""<div class="{pnl}"><div class="ptitle" style="color:{t['ink']}">{name}</div><div class="{cls}" style="display:flex;flex-direction:column;gap:22px;width:820px">
<div class="hrow gap16"><div class="btn-p" style="width:260px">Primary · Make my day</div><div class="btn-s" style="flex:none;width:260px">Secondary · Directions</div><div class="btn-d" style="width:220px">Call 999</div></div>
<div class="hrow gap16"><div class="quiet muted">Quiet · Skip the example</div><div class="pill">Help</div><div class="circ">{icon("menu", t["ink"], 18)}</div><div class="circ">{icon("gear", t["ink"], 18)}</div><div class="close">Close</div>{eyebrow("Eyebrow · Today")}</div>
<div class="chips" style="width:420px"><div class="chip on">Chip · on</div><div class="chip">Chip · off</div></div>
<div class="hrow gap16"><div class="opt serif" style="width:260px">Option</div><div class="opt serif sel" style="width:260px">Option · chosen</div><div class="stat">£21 per person</div><div class="tag saved">Saved, not booked</div><div class="tag booked">Booked</div></div>
<div class="hrow gap22 top"><div class="card" style="width:354px;padding:16px 16px 8px">{path_svg(t, 1, 322, 180)}</div>
<div style="display:flex;flex-direction:column;gap:12px;align-items:center">{arch_logo(t, 140, 1, "p" + cls)}<div class="foot muted">The mark</div></div>
<div style="display:flex;flex-direction:column;gap:4px;align-items:center">{rating_arch(t, 0.55, "p" + cls)}<div class="foot muted">Rating arch · Good</div></div>
<div style="display:flex;flex-direction:column;gap:4px;align-items:center">{breathing_arch(t, None if t is NIGHT else "day", 0.42 if t is DAY else None)}<div class="foot muted">Now · breathing arch</div></div></div>
<div style="width:402px">{row_card(t, "Big views", "Saturday 31 October", "4 stops · done by 17:00")}</div></div></div>"""


def motion_panel():
    notes = [
        ("Settle · 450 ms", "Content rises 10 pt as it fades in; lists stagger by 60 ms."),
        ("The arrival · 0.26 s, then 1.1 s", "Tapping “I'm here” (or the phone noticing): the way in gives way to what to notice, and a warm light opens out from the top once, like coming out of the station into the open."),
        ("Breathe · 6 s loop", "The glow behind the arch on “Now” slowly brightens and dims."),
        ("Rating · 0.7 s", "The arch fills with light up to the chosen word; on Save one small light rises into it (600 ms)."),
        ("Words · 70 ms a word", "Reactions come into focus from a blur, in amber italic."),
        ("Lift · 700 ms", "The share card tilts up into place."),
        ("Reduce Motion", "Every movement becomes a plain fade; nothing moves on its own."),
        ("Haptics", "One light tap on main actions and on arriving; nothing else."),
    ]
    out = "".join(f"<div><b>{esc(a)}</b><br>{esc(b)}</div>" for a, b in notes)
    return f'<div class="panel"><div class="ptitle">Motion (not in Figma, so written down)</div><div class="notes">{out}</div></div>'


# ---- the board ------------------------------------------------------------------------------------------------------
def section(title, text, rows):
    body = "".join(f'<div class="row">{r}</div>' for r in rows)
    return f'<div class="sec"><div class="sec-h"><h2>{esc(title)}</h2><p>{esc(text)}</p></div>{body}</div>'


def build():
    secs = []
    secs.append(f"""<div class="sec"><div class="sec-h"><h2>ODYS · the whole app, for review</h2>
<p>Every screen rebuilt as editable layers, in the night light and the day light. The colours follow London's real light on the phone (D130), so each screen exists in both. Built 25 Oct 2026 from the app's own words, colours and example day. Card photos are drawn as fields of colour; the real screens, photos included, are on the screenshot board.</p></div>
<div class="panel" style="max-width:1100px"><div class="notes">
<div><b>What's here</b><br>Foundations, the five skies, first run and onboarding, the plan, home before / on / after the day, “Now” on the way and arrived, rating, the end of the day, a trip, You, Help &amp; safety, notifications, permissions, errors and waiting.</div>
<div><b>Frames</b><br>402 × 874 points (iPhone 16 Pro). Long screens run to their full height. Android uses the same layout with the system's own bars.</div>
<div><b>Fonts</b><br>Newsreader (Google Fonts) and Inter. On the phone the system font is SF Pro (iPhone) or Roboto (Android).</div>
<div><b>Comment freely</b><br>Change anything. If a change from this file goes into the app, Abram needs a short signed note from you first (the contributor deed, Part A).</div></div></div></div>""")
    secs.append(section("Foundations", "Every colour has a night value and a day value; every text colour is 4.5:1 or better on every ground and sky (a test fails the build otherwise).",
                        [swatches(NIGHT, "Night colours"), swatches(DAY, "Day colours"), skies_panel(), type_panel(),
                         parts_panel(NIGHT, "Parts · night"), parts_panel(DAY, "Parts · day"), motion_panel()]))
    secs.append(section("The five skies", "The home on the day, under each sky. Only the top of the screen changes; the four day skies share the day colours.",
                        ["".join(phone(NIGHT if s == "night" else DAY, home_today(NIGHT if s == "night" else DAY, s), sky=s,
                                       base=(NIGHT if s == "night" else DAY)["background"], label=f"Home · today · {s}")
                                 for s in ["morning", "day", "golden", "rain", "night"])]))
    secs.append(section("First run and onboarding", "The welcome, a place they've been, a choice between two made-up days, and what the app has learned so far (their own answers only, never a score).",
                        [phone(NIGHT, welcome(NIGHT, "night"), label="Welcome · night") + phone(DAY, welcome(DAY, "day"), label="Welcome · day")
                         + phone(NIGHT, places(NIGHT, "night"), label="Places you've been · night") + phone(DAY, places(DAY, "day"), label="Places you've been · day"),
                         phone(NIGHT, this_or_that(NIGHT, "night"), label="This or that · night") + phone(DAY, this_or_that(DAY, "day"), label="This or that · day")
                         + phone(NIGHT, learned(NIGHT, "night"), label="So far, I've learned · night") + phone(DAY, learned(DAY, "day"), label="So far, I've learned · day")]))
    secs.append(section("The plan", "The day as a path over the list. The reveal draws the path, then the stops settle in one by one. The reminder question is asked once, under the first plan.",
                        [phone(NIGHT, plan_reveal(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Plan · revealing · night", note="Part-way through the reveal: the path is drawing and the first stop has settled.")
                         + phone(NIGHT, plan(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Plan · night")
                         + phone(DAY, plan(DAY, "day"), sky="day", base=DAY["background"], label="Plan · day")]))
    secs.append(section("Home: before, on and after the day", "No tabs. One home that follows the time: a day out and a trip as equals before, the day's path while it's on, the ratings after.",
                        [phone(NIGHT, home_before(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Home · before · night")
                         + phone(DAY, home_before(DAY, "day"), sky="day", base=DAY["background"], label="Home · before · day")
                         + phone(NIGHT, home_today(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Home · today · night")
                         + phone(DAY, home_today(DAY, "day"), sky="day", base=DAY["background"], label="Home · today · day"),
                         phone(NIGHT, home_after(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Home · after · night")
                         + phone(DAY, home_after(DAY, "golden"), sky="golden", base=DAY["background"], label="Home · after · golden hour")]))
    secs.append(section("On the day: “Now”", "Quiet on purpose. On the way: how you arrive is part of the moment. Arrived: what to notice, and the app goes quiet. By day the sun sits where the real sun is.",
                        [phone(NIGHT, now_way(NIGHT, "night"), sky="night", base=NIGHT["calm"], label="Now · on the way · night")
                         + phone(DAY, now_way(DAY, "day"), sky="day", base=DAY["calm"], label="Now · on the way · day")
                         + phone(NIGHT, now_here(NIGHT, "night"), sky="night", base=NIGHT["calm"], label="Now · arrived · night")
                         + phone(DAY, now_here(DAY, "day"), sky="day", base=DAY["calm"], label="Now · arrived · day"),
                         phone(NIGHT, now_here(NIGHT, "night"), sky="night", base=NIGHT["calm"], label="Now · the arrival moment · night",
                               note="The first second after “I'm here”: a warm light opens out from the top once (drawn here at its brightest).").replace(
                             '<div class="spacer"></div>', f'<div class="spacer"></div><div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 20%,rgba(255,231,176,0.6) 0%,rgba(255,231,176,0) 75%)"></div>', 1)
                         + phone(NIGHT, day_end(NIGHT, "night"), sky="night", base=NIGHT["calm"], label="End of the day · night")
                         + phone(DAY, day_end(DAY, "golden"), sky="golden", base=DAY["calm"], label="End of the day · golden hour")]))
    secs.append(section("Rating a stop", "One word on a 1–5 scale, after the visit. The arch fills with light to the word; Save sends it, so a mis-tap isn't sent. Sharing is offered, never pushed.",
                        [phone(NIGHT, rating(NIGHT, "night"), label="Rating · night") + phone(DAY, rating(DAY, "day"), label="Rating · day")
                         + phone(NIGHT, rating_chosen(NIGHT, "night"), label="Rating · chosen · night") + phone(DAY, rating_chosen(DAY, "day"), label="Rating · chosen · day"),
                         phone(NIGHT, rating_saved(NIGHT, "night"), label="Rating · saved · night") + phone(DAY, rating_saved(DAY, "day"), label="Rating · saved · day")
                         + phone(NIGHT, rating_offline(NIGHT, "night"), label="Rating · saved with no signal · night")
                         + phone(NIGHT, share_preview(NIGHT, "night"), label="Share this moment · night", note="The card is cream so it reads the same wherever it's sent. Their own rating and their own reason, never the model's guesses.")]))
    secs.append(section("A trip", "Getting there, where you'll stay and your days, in one place. Flights and stays are booked on the provider's own site.",
                        [phone(NIGHT, trip(NIGHT, "night"), label="Trip · night") + phone(DAY, trip(DAY, "day"), label="Trip · day")]))
    secs.append(section("You, and Help & safety", "Behind the menu: emergency first, then a real person, what the app has learned, the light, and your data.",
                        [phone(NIGHT, you(NIGHT, "night"), label="You · night") + phone(DAY, you(DAY, "day"), label="You · day")
                         + phone(NIGHT, safety(NIGHT, "night"), label="Help & safety · night") + phone(DAY, safety(DAY, "day"), label="Help & safety · day")]))
    secs.append(section("Notifications, permissions, errors and waiting", "Permissions are asked only when a feature needs them, after the app's own question. The system draws its alerts; ODYS sets only the words.",
                        [lock_screen(NIGHT, "night") + lock_screen(DAY, "day")
                         + phone(DAY, banner_over_now(DAY, "day"), sky="day", base=DAY["calm"], label="Rating reminder · banner while the app is open · day")
                         + android_shade(NIGHT, "night"),
                         phone(NIGHT, notif_permission(NIGHT, "night"), label="Notifications permission · after “Yes, remind me”")
                         + phone(DAY, location_permission(DAY, "day"), sky="day", base=DAY["calm"], label="Location permission · after “Yes, use it” on Now")
                         + phone(NIGHT, error_alert(NIGHT, "night"), sky="night", base=NIGHT["background"], label="Error · offline")
                         + phone(DAY, waking(DAY, "day"), sky="day", base=DAY["background"], label="Waiting · the planner waking up")]))
    page = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>ODYS for Figma</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap">
<style>{BASE}{themed_css()}</style></head><body><div class="board">{"".join(secs)}</div></body></html>"""
    OUT.write_text(page)
    print(f"wrote {OUT} ({len(page) / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
