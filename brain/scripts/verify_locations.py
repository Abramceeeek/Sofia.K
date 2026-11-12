"""m245: check each London card's coordinates against Wikidata (CC0): is there an item whose English label matches
the card's place name within 400 m? Writes data/catalogue/london_locations.yaml (the card, the item, the distance).
A card with no match is listed as unconfirmed, never moved. One query per card, a second apart (Wikidata's limits).

Run from brain/: `.venv/bin/python scripts/verify_locations.py`
"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from brain.catalogue import load_catalogue  # noqa: E402

STOP = {"the", "and", "of", "a", "an", "at", "by", "on", "in", "to", "london", "park", "museum", "gallery", "s", "st",
        "street", "road", "market", "garden", "gardens", "church", "bridge"}


def words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", t.lower().replace("'", "")) if w not in STOP and len(w) > 1}


def around(lat: float, lon: float) -> list[dict]:
    q = f"""SELECT ?item ?label ?dist WHERE {{ SERVICE wikibase:around {{ ?item wdt:P625 ?loc.
      bd:serviceParam wikibase:center "Point({lon} {lat})"^^geo:wktLiteral. bd:serviceParam wikibase:radius "0.4".
      bd:serviceParam wikibase:distance ?dist. }} ?item rdfs:label ?label. FILTER(LANG(?label) = "en") }}
      ORDER BY ?dist LIMIT 300"""
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": "ODYS-research/1.0 (research script)"})
    return json.load(urllib.request.urlopen(req, timeout=90))["results"]["bindings"]


def main() -> int:
    out = {}
    for x in load_catalogue():
        name = words(x.name) | words(x.title)
        best = None
        for b in around(x.geo.lat, x.geo.lon):
            lw = words(b["label"]["value"])
            if lw and lw <= name:                  # every significant word of the item's label is in the card's
                best = (b["item"]["value"].rsplit("/", 1)[1], b["label"]["value"], round(float(b["dist"]["value"]) * 1000))
                break
        out[x.legacy_ids[0]] = ({"wikidata": best[0], "label": best[1], "metres": best[2]} if best
                                else {"wikidata": None, "note": "no item with a matching name within 400 m"})
        time.sleep(1.0)
    head = ("# m245: London card coordinates against Wikidata (CC0), checked 2026-11-11 by scripts/verify_locations.py.\n"
            "# A match: an item whose English label's words all appear in the card's place name or title, within 400 m.\n"
            "# Unmatched cards keep their coordinates and are listed as unconfirmed; nothing is moved.\n")
    Path("data/catalogue/london_locations.yaml").write_text(head + yaml.safe_dump({"checked": "2026-11-11", "cards": out},
                                                            sort_keys=True, allow_unicode=True), encoding="utf-8")
    print(sum(1 for v in out.values() if v["wikidata"]), "of", len(out), "matched")
    for k, v in out.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
