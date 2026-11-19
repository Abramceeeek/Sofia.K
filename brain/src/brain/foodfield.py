"""m289 (Abram, m260 and 19 Nov): the old free-text food field (`foods_avoided`, D19), for an authorised operator.

    python -m brain.foodfield count  --database-url <External URL>
    python -m brain.foodfield delete --database-url <External URL> --confirm delete

It needs no `psql`: it runs from the same Python environment as `python -m brain.backup`.

What it can and can't do:
- It only ever prints counts: never a value, a length or a user.
- It reads and writes only `users.profile`. It never creates, alters or drops a table: no `create_all`, and the table
  is described here with just the two columns it touches, so it works on main's schema as on the branch's.
- `delete` removes only the `foods_avoided` key, in one transaction. It counts again inside that transaction and
  commits only if the count is 0; otherwise it rolls back and nothing changes.
- It never deletes a user record.
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine, select, update
from sqlalchemy.engine import Engine

from . import food
from .config import driver_url

_USERS = Table("users", MetaData(), Column("id", String(36), primary_key=True), Column("profile", JSON))


def _counts(conn) -> dict[str, int]:
    return food.audit_profiles(p if isinstance(p, dict) else None for (p,) in conn.execute(select(_USERS.c.profile)))


def count(engine: Engine) -> dict[str, int]:
    with engine.connect() as conn:
        return _counts(conn)


def delete(engine: Engine) -> dict:
    """Steps 4-6 of the procedure: the key only, one transaction, committed only when the count reaches 0."""
    with engine.connect() as conn:
        tx = conn.begin()
        before = _counts(conn)
        updated = 0
        for uid, profile in conn.execute(select(_USERS.c.id, _USERS.c.profile)).all():
            if isinstance(profile, dict) and any(k in profile for k in food.RETIRED_PROFILE_KEYS):
                conn.execute(update(_USERS).where(_USERS.c.id == uid).values(profile=food.scrub_profile(profile)))
                updated += 1
        inside = _counts(conn)
        committed = inside["with_key"] == 0
        tx.commit() if committed else tx.rollback()
    return {"before": before, "updated": updated, "after": count(engine), "committed": committed}


def _line(c: dict[str, int]) -> str:
    return f"profiles {c['profiles']}, with_key {c['with_key']}, non_empty {c['non_empty']}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m brain.foodfield", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("count", "delete"):
        p = sub.add_parser(name)
        p.add_argument("--database-url", required=True)
        if name == "delete":
            p.add_argument("--confirm", default="", help='type "delete" to remove the key')
    a = ap.parse_args(argv)
    engine = create_engine(driver_url(a.database_url))
    if a.cmd == "count":
        print(_line(count(engine)))
        return 0
    if a.confirm != "delete":
        print('Nothing changed: add --confirm delete to remove the foods_avoided key.', file=sys.stderr)
        return 1
    r = delete(engine)
    print(f"before: {_line(r['before'])}")
    print(f"updated {r['updated']} profiles (the foods_avoided key only)")
    print(f"after:  {_line(r['after'])}")
    print("COMMITTED" if r["committed"] else "ROLLED BACK: the count didn't reach 0, so nothing was changed")
    return 0 if r["committed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
