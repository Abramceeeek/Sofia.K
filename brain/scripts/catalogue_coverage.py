"""m245: the destination data coverage dashboard (Abram, m244): London before and after the official-source checks,
and Paris. Writes benchmarks/coverage/destination_coverage.md. Run from brain/: `.venv/bin/python scripts/catalogue_coverage.py`

Each line counts experiences; nothing is estimated here. "Before" is the cards alone (catalogue.load_catalogue(
checked=False)); "after" adds data/catalogue/london_checked.yaml and london_locations.yaml.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from brain.catalogue import _SEASONAL, load_catalogue, load_checked, load_dev  # noqa: E402
from brain.config import DATA_DIR  # noqa: E402

TODAY = date(2026, 11, 11)
FRESH = (TODAY - timedelta(days=90)).isoformat()
OUTDOOR = {"nature", "views", "neighbourhood"}


def stats(xs, located: int | None, photos: dict | None) -> dict:
    n = len(xs)
    c = lambda f: sum(1 for x in xs if f(x))
    sf = lambda v: c(lambda x: x.accessibility.step_free.known and x.accessibility.step_free.value == v)
    out = {
        "experiences": n,
        "location matched to a named Wikidata item (≤400 m)": "not checked" if located is None else located,
        "area named by an official page": c(lambda x: x.geo.area.trust == "checked"),
        "area named only by the card's own title": c(lambda x: x.geo.area.trust == "claimed"),
        "no named area": c(lambda x: not x.geo.area.known),
        "hours as a weekly table": c(lambda x: x.hours.weekly is not None),
        "hours read from an official page in the last 90 days": c(lambda x: x.hours.trust == "checked" and (x.hours.source or "").startswith("https://") and (x.hours.checked or "") >= FRESH),
        "hours kept as text (seasonal, conflicting or general)": c(lambda x: x.hours.text and x.hours.weekly is None),
        "hours unknown": c(lambda x: not x.hours.text and not getattr(x.facet, "event_based", False)),
        "step-free: yes / partial / no (from a named source)": f"{sf('yes')} / {sf('partial')} / {sf('no')}",
        "step-free unknown": c(lambda x: not x.accessibility.step_free.known),
        "price checked on an official page": c(lambda x: x.price.trust == "checked" and (x.price.source or "").startswith("https://")),
        "price checked on the card (before this sprint)": c(lambda x: x.price.trust == "checked" and not (x.price.source or "").startswith("https://")),
        "price claimed or estimated": c(lambda x: x.price.trust in ("claimed", "estimated")),
        "price unknown": c(lambda x: not x.price.known),
        "dated notices (closures, seasons, events)": sum(len(x.notices) for x in xs),
        "outdoor experiences with seasonal information (dated notices, or hours that change with the season)":
            f"{c(lambda x: x.category in OUTDOOR and (x.notices or _SEASONAL.search((x.hours.text or '').lower())))} of {c(lambda x: x.category in OUTDOOR)}",
        "district (borough or arrondissement): printed by an official page / from the postcode":
            f"{c(lambda x: x.district.trust == 'checked')} / {c(lambda x: x.district.trust == 'estimated')}",
        "any fact checked in the last 90 days": c(lambda x: max((f or "") for f in (x.hours.checked, x.price.checked, x.accessibility.step_free.checked, x.geo.area.checked, x.provenance.checked)) >= FRESH),
    }
    if photos is not None:
        out.update(photos)
    return out


def main() -> int:
    before = load_catalogue(checked=False)
    after = load_catalogue()
    loc = yaml.safe_load((DATA_DIR / "catalogue" / "london_locations.yaml").read_text(encoding="utf-8"))["cards"]
    checks = yaml.safe_load((DATA_DIR / "photo_checks.yaml").read_text(encoding="utf-8"))["photos"]
    shows = lambda v: sum(1 for r in checks.values() if r["shows"] == v)
    ph_before = {"photos with a credit": 45, "photo pages re-read one by one": 6, "photo credits the page asks to change": "not checked"}
    ph_after = {"photos with a credit": 45, "photo pages re-read one by one": len(checks),
                "photo credits the page asks to change": f"{sum(1 for r in checks.values() if r['author'] == 'fixed')} (fixed)",
                "photo licence stated two ways on its page": sum(1 for r in checks.values() if r["licence"] == "conflict"),
                "photos showing the place / something related / 15+ years old": f"{shows('place')} / {shows('related')} / {shows('dated')}"}
    lb = stats(before, None, ph_before)
    la = stats(after, sum(1 for v in loc.values() if v["wikidata"]), ph_after)
    dest, px, raw = load_dev("paris")
    ready = [x for x in px if x.status == "ready"]
    pa = stats(ready, None, {"photos": "none (not added until each is checked)"})
    pa["location matched to a named Wikidata item (≤400 m)"] = f"{sum(1 for x in ready if (x.place_id or '').startswith('wikidata:'))} (+1 OpenStreetMap)"
    lines = ["# Destination data coverage (m245, 11 Nov 2026)", "",
             "Generated by `brain/scripts/catalogue_coverage.py`. Counts of experiences; nothing here is estimated.",
             "London \"before\" is the cards alone; \"after\" adds the facts read from official pages on 11 Nov 2026",
             f"(`data/catalogue/london_checked.yaml`) and the Wikidata location check. Paris counts its {len(ready)} ready",
             f"experiences (of {len(px)}; the rest are drafts, never recommended). Fresh = checked on or after {FRESH}.", "",
             "| Measure | London before | London after | Paris (ready) |", "|---|---|---|---|"]
    for k in la:
        lines.append(f"| {k} | {lb.get(k, '—')} | {la[k]} | {pa.get(k, '—')} |")
    ch = load_checked("london")
    lines += ["", f"**London pages that couldn't be read** ({len(ch['not_read'])}; nothing filled from elsewhere):", ""]
    lines += [f"- `{r['card']}`: {r['why']}" for r in ch["not_read"]]
    lines += ["", "**Where an official page differs from the card the planner uses** (for Abram; no plan changes yet):", ""]
    lines += [f"- `{i}`: {c['card_differs']}" for i, c in ch["cards"].items() if "card_differs" in c]
    lines += ["", "**Paris pages that couldn't be read:**", ""] + [f"- {r['what']}: {r['why']}" for r in raw["not_read"]]
    Path("benchmarks/coverage").mkdir(parents=True, exist_ok=True)
    Path("benchmarks/coverage/destination_coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
