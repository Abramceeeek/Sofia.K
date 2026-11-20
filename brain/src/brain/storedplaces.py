"""m308 (Abram, 20 Nov): plans stored before the A2 hotfix, for an authorised operator.

    python -m brain.storedplaces count --database-url <External URL>
    python -m brain.storedplaces clean --database-url <External URL> --confirm clean

Before A2, a stored plan could keep two things the privacy notice says aren't kept (SEC-06):
- a day planned from "where you are": that point, as the map pin of lunch near the start;
- a trip's day plans: the stay's name, in "Lunch near …" and "… from <stay>".

What it can and can't do (the same rules as `brain.foodfield`):
- It only ever prints counts: never a place, a name, a point or a user.
- It reads and writes only `plans.stops`, and reads `plans.intent` to tell trip days apart. It never creates, alters
  or drops a table, so it works on main's schema as on the branch's.
- `clean` changes only those two things, in one transaction: the pin becomes empty and the stay's name reads
  "your stay", as A2 stores them now. It counts again inside the transaction and commits only if both counts are 0;
  otherwise it rolls back and nothing changes. It never deletes a plan or a person.
- A restore from a backup made before the clean brings the old copies back: run `count` after any restore, and
  `clean` again if it isn't 0.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from sqlalchemy import JSON, Column, Integer, MetaData, Table, create_engine, select, update
from sqlalchemy.engine import Engine

from .config import DATA_DIR, driver_url

HERE = "where you are"            # the start's name both frozen apps send for "Start from where I am"
SHOWN_AS = "your stay"            # what A2 stores instead of a stay's name
_PLANS = Table("plans", MetaData(), Column("id", Integer, primary_key=True), Column("intent", JSON),
               Column("stops", JSON))
_FROM = re.compile(r" from (.+?)(?: to |\.$)")


def public_names(data_dir: Path = DATA_DIR) -> set[str]:
    """Start names that are public places, not a person's stay: each destination's centre (airports.yaml)."""
    names = {SHOWN_AS}
    for x in (yaml.safe_load((data_dir / "airports.yaml").read_text()) or {}).get("destinations", []) or []:
        name = ((x or {}).get("centre") or {}).get("name")
        if name:
            names.add(str(name))
    return names


def _start_stop(stops: list) -> dict | None:
    return next((st for st in stops if isinstance(st, dict) and str(st.get("moment_id", "")).endswith("@start")),
                None)


def here_pin(stops) -> bool:
    """A day from "where you are" whose lunch near the start still carries the point."""
    st = _start_stop(stops or [])
    return bool(st and st.get("pin") and str(st.get("title", "")).strip().lower() == f"lunch near {HERE}")


def stay_name(intent, stops, public: set[str]) -> str | None:
    """The stay's name a trip day kept, read from where the frozen code wrote it; None if it kept none."""
    if not (isinstance(intent, dict) and intent.get("trip")):
        return None
    found = []
    st = _start_stop(stops or [])
    if st and str(st.get("title", "")).startswith("Lunch near "):
        found.append(str(st["title"])[len("Lunch near "):].strip())
    first = (stops or [None])[0]
    if isinstance(first, dict) and (m := _FROM.search(str(first.get("travel_text", "")))):
        found.append(m.group(1).strip())
    for name in found:
        if len(name) >= 3 and name not in public:   # as A2: too short to tell apart, or a public centre
            return name
    return None


def _replace(v, name: str):
    if isinstance(v, str):
        return v.replace(name, SHOWN_AS)
    if isinstance(v, list):
        return [_replace(x, name) for x in v]
    if isinstance(v, dict):
        return {k: _replace(x, name) for k, x in v.items()}
    return v


def cleaned(intent, stops, public: set[str]):
    """The stops as A2 would have stored them. Only the two things above change."""
    out = stops
    if here_pin(out):
        out = [dict(st, pin=None) if st is _start_stop(out) else st for st in out]
    if name := stay_name(intent, out, public):
        out = _replace(out, name)
    return out


def _counts(conn, public: set[str]) -> dict[str, int]:
    c = {"plans": 0, "here_pins": 0, "stay_names": 0}
    for intent, stops in conn.execute(select(_PLANS.c.intent, _PLANS.c.stops)):
        c["plans"] += 1
        c["here_pins"] += here_pin(stops if isinstance(stops, list) else [])
        c["stay_names"] += stay_name(intent, stops if isinstance(stops, list) else [], public) is not None
    return c


def count(engine: Engine, public: set[str] | None = None) -> dict[str, int]:
    with engine.connect() as conn:
        return _counts(conn, public or public_names())


def clean(engine: Engine, public: set[str] | None = None) -> dict:
    public = public or public_names()
    with engine.connect() as conn:
        tx = conn.begin()
        before = _counts(conn, public)
        updated = 0
        for pid, intent, stops in conn.execute(select(_PLANS.c.id, _PLANS.c.intent, _PLANS.c.stops)).all():
            if not isinstance(stops, list):
                continue
            new = cleaned(intent, stops, public)
            if new != stops:
                conn.execute(update(_PLANS).where(_PLANS.c.id == pid).values(stops=new))
                updated += 1
        inside = _counts(conn, public)
        committed = inside["here_pins"] == 0 and inside["stay_names"] == 0
        tx.commit() if committed else tx.rollback()
    return {"before": before, "updated": updated, "after": count(engine, public), "committed": committed}


def _line(c: dict[str, int]) -> str:
    return f"plans {c['plans']}, here_pins {c['here_pins']}, stay_names {c['stay_names']}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m brain.storedplaces", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("count", "clean"):
        p = sub.add_parser(name)
        p.add_argument("--database-url", required=True)
        if name == "clean":
            p.add_argument("--confirm", default="", help='type "clean" to change the stored plans')
    a = ap.parse_args(argv)
    engine = create_engine(driver_url(a.database_url), hide_parameters=True)
    if a.cmd == "count":
        print(_line(count(engine)))
        return 0
    if a.confirm != "clean":
        print("Nothing changed: add --confirm clean to change the stored plans.", file=sys.stderr)
        return 1
    r = clean(engine)
    print(f"before: {_line(r['before'])}")
    print(f"updated {r['updated']} plans (the start pin and the stay's name only)")
    print(f"after:  {_line(r['after'])}")
    print("COMMITTED" if r["committed"] else "ROLLED BACK: a count didn't reach 0, so nothing was changed")
    return 0 if r["committed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
