"""m318: a DRAFT Seville preview sheet for Abram to review, built only from data/dev/seville.yaml.

Not sent to anyone, not served by the Brain, not shown in either app. Abram decides whether to share it.
Every line comes from the catalogue as recorded on 20 Nov 2026; nothing is added here.

Run from brain/: `.venv/bin/python scripts/seville_preview.py` → ../decisions/seville-preview-draft.md
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from brain import quality  # noqa: E402
from brain.catalogue import load_dev  # noqa: E402
from brain.destination import load_emergency  # noqa: E402

TODAY = date(2026, 11, 20)
DAYS = [date(2026, 11, 22) + timedelta(days=i) for i in range(7)]          # Sun 22 to Sat 28 Nov
MARK = {"confirmed open": "open", "might be open": "check", "closed or unavailable": "**shut**"}
KINDS = {"culture": "Museums and monuments", "views": "Views", "nature": "Parks", "neighbourhood": "Areas to wander",
         "food_drink": "Markets and food"}


def price(x) -> str:
    if not x.price.known:
        return "price not printed"
    m = x.price.value
    if m.kind == "free":
        return "free" + ("" if x.price.trust == "checked" else " (as printed, not confirmed)")
    return f"€{m.amount:g}" + ("" if x.price.trust == "checked" else " (as printed, not confirmed)")


def access(x) -> str:
    sf = x.accessibility.step_free
    return {"yes": "step-free (the venue says)", "partial": "partly step-free"}.get(sf.value, "step-free not known") \
        if sf.known else "step-free not known"


def main() -> int:
    _, xs, raw = load_dev("seville")
    ready = [x for x in xs if x.status == "ready"]
    es = load_emergency()["ES"]
    out = ["# Seville preview — DRAFT for Abram's review (not sent)", "",
           "Generated from `brain/data/dev/seville.yaml` (read from official pages on 20 Nov 2026) by "
           "`brain/scripts/seville_preview.py`. ODYS does not support Seville: this is a list to look at, not a plan.",
           "",
           "**Please don't rely on this alone.** Check each place's own site on the day for hours, prices and "
           "bookings. ODYS has no Seville transport, weather or live information.", "",
           f"**Emergency in Spain: {es.lines[0].number}** (ambulance, fire and police; free). Source: "
           f"{es.lines[0].source}, checked {es.checked}. The ODYS app's Help & safety screen says 999, which is the "
           "UK number and does not apply in Spain.", "",
           "Seville's four municipal markets are closed on Sundays.", "",
           "Each day: **open** = the venue's own page, read on 20 Nov, lists that day; **check** = probably open, "
           "but the hours come from an older leaflet, a non-secure page or a seasonal timetable; **shut** = the "
           "venue's own hours leave that day out.", ""]
    head = "| Place | " + " | ".join(d.strftime("%a %d") for d in DAYS) + " | Hours as printed | Price | Access |"
    for cat, title in KINDS.items():
        rows = [x for x in ready if x.category == cat]
        if not rows:
            continue
        out += [f"## {title}", "", head, "|" + "---|" * (len(DAYS) + 4)]
        for x in rows:
            days = " | ".join(MARK[quality.availability(x, d, TODAY)] for d in DAYS)
            src = f"[source]({x.hours.source})" if (x.hours.source or "").startswith("http") else "leaflet"
            out.append(f"| **{x.name}** — {x.title} | {days} | {x.hours.text} ({src}, read {x.hours.checked}) | "
                       f"{price(x)} | {access(x)} |")
        def when(n) -> str:
            if not n.start:
                return "" if not n.end else f" (until {n.end})"
            return f" ({n.start})" if n.end == n.start else f" ({n.start} to {n.end or 'further notice'})"
        notes = [(x.name, n.what + when(n)) for x in rows for n in x.notices]
        if notes:
            out += [""] + [f"- {name}: {what}" for name, what in notes]
        out.append("")
    t = raw["transport"]["airport"]
    out += ["## From the airport (Aena, the airport operator)", "", f"- Bus: {t['bus']}", f"- Taxi: {t['taxi']}",
            f"- Source: {t['source']}", "",
            "## Not covered", "",
            "- City buses, metro and journey times: the operators' pages could not be read, so nothing is given.",
            "- Weather: ODYS has no Seville forecast. AEMET's page: " + raw["weather"]["page"],
            "- Restaurant prices, step-free access at most places, dietary information: not checked.",
            "- Seville's own local holidays: not included.", ""]
    path = HERE.parents[1] / "decisions" / "seville-preview-draft.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
