"""Nightly encrypted backups (roadmap Stage 1, step 5).

Why our own: Render's free database has no backups. A paid one keeps point-in-time recovery for the past 3 days on a
Hobby workspace (7 on Pro), and its downloadable exports are made by hand and kept 7 days
(render.com/docs/postgresql-backups, read 19 Oct 2026). The testers' answers are the evidence for Checkpoint 3, so a
copy is also kept away from Render.

- **What:** every row of the Brain's tables and of the swipe page's answers, as JSON. Not the cards or TfL's times,
  which are rebuilt at every start, and never the contacts left with a safety message (D118).
- **Sealed on the server:** compressed, then encrypted to Abram's public key (X25519, HKDF-SHA256 and AES-256-GCM,
  from the `cryptography` library) before it leaves the server. Only his private key, kept on his own computer,
  opens it. So the copy can sit in GitHub (this private repository's workflow artifacts) without GitHub, or anyone
  who can see the repository, being able to read it.
- **Where:** a GitHub Actions job (`.github/workflows/ops.yml`) fetches it each night with `BRAIN_BACKUP_TOKEN`, a
  token that unlocks only this, and keeps it for 30 days.
- **Commands** (on Abram's computer, from `brain/`, after `pip install cryptography`):
  - `python -m brain.backup keygen`: makes the key pair, keeps the private key in a file, and prints the public key
    for Render and a fresh BRAIN_BACKUP_TOKEN for Render and GitHub Secrets;
  - `python -m brain.backup open odys-brain-20261020.odysbk --key odys-backup-private.key > backup.json`;
  - `python -m brain.backup restore backup.json --database-url postgresql://…`: into an empty database.
  - `python -m brain.backup verify odys-brain-20261020.odysbk --key …`: opens a backup and checks it is whole and
    consistent, without writing anything.
- **Deletions survive a restore (SEC-10, Abram, 12 Nov 2026).** "Delete my data" keeps one row: a one-way code made
  from the install's id (`deleted_key`), never the id or anything the person said. Every backup carries these rows,
  and a restore removes those installs again before anything is written. When restoring an OLDER backup, pass the
  NEWEST backup too (`--deletions newest.odysbk`): its list then applies as well, so nothing deleted in between
  comes back. Only deletions made after the newest backup can't be known; they are lost with everything else from
  those hours.
- **A damaged or incomplete backup is refused** before anything is written: it must open (the seal fails on any
  changed byte), read as JSON, be this format, and hang together (no rating, plan or reply that points at a person or
  message the backup doesn't hold). A table the backup doesn't have at all (one added since it was made) is noted and
  left empty.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import os
import secrets
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import Date, DateTime, Integer, Table, func, inspect, select, text
from sqlalchemy.engine import Engine

from . import calibration, db, food

DELETED_PREFIX = "odys-deleted-install:"


def deleted_key(user_id: str) -> str:
    """SEC-10: the one-way code kept when an install is deleted. The ids are random (uuid4), so the code can't be
    turned back into one; it can only be matched against an id that a backup still holds."""
    return hashlib.sha256((DELETED_PREFIX + user_id).encode()).hexdigest()

MAGIC = b"ODYSBK1\n"
INFO = b"odys-backup-v1"
# The cards and TfL's times are rebuilt at start. The phone numbers and emails left with a safety message are never
# copied: they are deleted once sorted (D118), and a copy would outlive that.
SKIP = {"moments", "travel_times", "safety_contacts"}


class BackupError(Exception):
    pass


# ---- what is kept ---------------------------------------------------------------------------------------------

def tables() -> list[Table]:
    """Parents before children, so a restore can insert them in this order."""
    return [t for t in db.Base.metadata.sorted_tables if t.name not in SKIP] + \
        list(calibration.Base.metadata.sorted_tables)


def _plain(v):
    return v.isoformat() if isinstance(v, (datetime, date)) else v


def dump(engine: Engine) -> dict:
    have = set(inspect(engine).get_table_names())
    out: dict[str, list[dict]] = {}
    with engine.connect() as c:
        for t in tables():
            if t.name in have:
                out[t.name] = [_scrubbed(t.name, {k: _plain(v) for k, v in r._mapping.items()})
                               for r in c.execute(select(t))]
    return {"format": 1, "made_at": datetime.now(timezone.utc).isoformat(), "tables": out}


def _scrubbed(table: str, row: dict) -> dict:
    """m233: the retired free-text food field never goes into a backup, and never comes back out of an older one."""
    if table == "users" and isinstance(row.get("profile"), dict):
        return {**row, "profile": food.scrub_profile(row["profile"])}
    return row


def _typed(t: Table, row: dict) -> dict:
    out = {}
    if t.name == "deletions" and row.get("deleted_at") is None:
        row = {**row, "deleted_at": datetime.now(timezone.utc).isoformat()}
    for k, v in row.items():
        col = t.c.get(k)
        if col is None:
            continue   # a column dropped since the backup was made
        if v is not None and isinstance(col.type, DateTime):
            v = datetime.fromisoformat(v)
        elif v is not None and isinstance(col.type, Date):
            v = date.fromisoformat(v)
        out[k] = v
    return out


# ---- checking a backup before it is used (SEC-10) ------------------------------------------------------------------

# Rows that point at another table's rows: (table, column) -> (parent table, its key). A nullable pointer may be empty.
POINTERS = {("swipes", "user_id"): ("users", "id"), ("conjoint_choices", "user_id"): ("users", "id"),
            ("answers", "user_id"): ("users", "id"), ("plans", "user_id"): ("users", "id"),
            ("ratings", "user_id"): ("users", "id"), ("ratings", "plan_id"): ("plans", "id"),
            ("events", "user_id"): ("users", "id"), ("day_feedback", "user_id"): ("users", "id"),
            ("day_feedback", "plan_id"): ("plans", "id"), ("safety_alerts", "user_id"): ("users", "id"),
            ("safety_replies", "alert_id"): ("safety_alerts", "id"), ("category_answers", "user_id"): ("users", "id"),
            ("corrections", "user_id"): ("users", "id"), ("referrals", "user_id"): ("users", "id")}


def check(data) -> tuple[list[str], list[str]]:
    """(problems that stop a restore, notes that don't). Reads only; writes nothing."""
    if not isinstance(data, dict) or data.get("format") != 1:
        return ["not a backup this version can read"], []
    t = data.get("tables")
    if not isinstance(t, dict):
        return ["the backup has no tables"], []
    problems, notes = [], []
    for name, rows in t.items():
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            problems.append(f"{name}: not a list of rows")
    if problems:
        return problems, notes
    absent = [x.name for x in tables() if x.name not in t]
    if absent:
        notes.append("not in this backup (made before they existed, or cut short): " + ", ".join(absent))
    if "users" not in t and any(child == "users" or parent == "users" for (child, _), (parent, _) in POINTERS.items()
                                if child in t and t[child]):
        problems.append("rows that belong to people, but no users table: the backup is incomplete")
    for (child, col), (parent, key) in POINTERS.items():
        if child not in t or not t[child]:
            continue
        have = {r.get(key) for r in t.get(parent, [])}
        orphans = sum(1 for r in t[child] if r.get(col) is not None and r.get(col) not in have)
        if orphans:
            problems.append(f"{child}: {orphans} row(s) point at {parent} rows the backup doesn't hold")
    return problems, notes


def deletions_in(data: dict) -> list[dict]:
    """The deletion records a backup holds: to pass on when restoring an older one."""
    return [r for r in (data.get("tables", {}).get("deletions") or []) if isinstance(r, dict) and r.get("user_hash")]


def restore(engine: Engine, data: dict, extra_deletions: list[dict] = ()) -> dict[str, int]:
    """Into an empty database: checked first, then the tables are made and filled, all in one transaction (a failure
    leaves nothing behind). Refuses a table that already has rows. SEC-10: any install whose deletion is recorded,
    in this backup or in `extra_deletions` (from a newer one), is left out, with everything that belonged to it; the
    deletion records themselves are all kept, so a later restore does the same."""
    problems, _ = check(data)
    if problems:
        raise BackupError("this backup can't be restored: " + "; ".join(problems[:5]))
    deleted = {r["user_hash"]: r for r in [*deletions_in(data), *extra_deletions] if r.get("user_hash")}
    gone = {u["id"] for u in data["tables"].get("users", []) if deleted_key(u["id"]) in deleted}
    gone_alerts = {a["id"] for a in data["tables"].get("safety_alerts", []) if a.get("user_id") in gone}

    def kept(table: str, row: dict) -> bool:
        if table == "users":
            return row["id"] not in gone
        if table in ("safety_replies", "safety_contacts"):
            return row.get("alert_id") not in gone_alerts
        return row.get("user_id") not in gone

    db.Base.metadata.create_all(engine)
    calibration.Base.metadata.create_all(engine)
    counts = {}
    with engine.begin() as c:
        for t in tables():
            if t.name == "deletions":
                rows = [{"user_hash": h, "deleted_at": r.get("deleted_at")} for h, r in deleted.items()]
            else:
                rows = [r for r in data["tables"].get(t.name, []) if kept(t.name, r)]
            if c.execute(select(func.count()).select_from(t)).scalar():
                raise BackupError(f"{t.name} already has rows: restore into an empty database")
            if rows:
                c.execute(t.insert(), [_typed(t, _scrubbed(t.name, r)) for r in rows])
            counts[t.name] = len(rows)
            pk = list(t.primary_key.columns)
            if engine.dialect.name == "postgresql" and rows and len(pk) == 1 and isinstance(pk[0].type, Integer):
                # the next new row's id follows on from the restored ones
                c.execute(text(f"SELECT setval(pg_get_serial_sequence('{t.name}', '{pk[0].name}'), "
                               f"(SELECT MAX({pk[0].name}) FROM {t.name}))"))
    counts["removed_again"] = len(gone)
    return counts


# ---- sealing ---------------------------------------------------------------------------------------------------

def _crypto():
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    except ImportError as e:   # pragma: no cover - the server and the tests have it
        raise BackupError("the cryptography library isn't installed: pip install cryptography") from e
    return hashes, serialization, X25519PrivateKey, X25519PublicKey, AESGCM, HKDF


def _raw(key) -> bytes:
    _, serialization, *_ = _crypto()
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def _derive(shared: bytes, eph: bytes, recipient: bytes) -> bytes:
    hashes, *_, HKDF = _crypto()
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=eph + recipient, info=INFO).derive(shared)


def keygen() -> tuple[str, str]:
    """(public key for Render, private key for Abram's own computer), each as base64 text."""
    _, serialization, X25519PrivateKey, *_ = _crypto()
    k = X25519PrivateKey.generate()
    private = k.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                              serialization.NoEncryption())
    return base64.b64encode(_raw(k.public_key())).decode(), base64.b64encode(private).decode()


def seal(data: bytes, public_key_b64: str) -> bytes:
    _, _, X25519PrivateKey, X25519PublicKey, AESGCM, _ = _crypto()
    try:
        recipient = base64.b64decode(public_key_b64.strip(), validate=True)
        pub = X25519PublicKey.from_public_bytes(recipient)
    except Exception as e:  # noqa: BLE001
        raise BackupError("BRAIN_BACKUP_PUBLIC_KEY isn't a key made by `python -m brain.backup keygen`") from e
    eph = X25519PrivateKey.generate()
    eph_raw = _raw(eph.public_key())
    nonce = os.urandom(12)
    box = AESGCM(_derive(eph.exchange(pub), eph_raw, recipient)).encrypt(nonce, gzip.compress(data), MAGIC)
    return MAGIC + eph_raw + nonce + box


def unseal(blob: bytes, private_key_b64: str) -> bytes:
    _, _, X25519PrivateKey, X25519PublicKey, AESGCM, _ = _crypto()
    if not blob.startswith(MAGIC):
        raise BackupError("not an ODYS backup")
    eph_raw, nonce, box = blob[8:40], blob[40:52], blob[52:]
    k = X25519PrivateKey.from_private_bytes(base64.b64decode(private_key_b64.strip()))
    try:
        key = _derive(k.exchange(X25519PublicKey.from_public_bytes(eph_raw)), eph_raw, _raw(k.public_key()))
        return gzip.decompress(AESGCM(key).decrypt(nonce, box, MAGIC))
    except Exception as e:  # noqa: BLE001
        raise BackupError("this key doesn't open this backup (or the file is damaged)") from e


def sealed_backup(engine: Engine, public_key_b64: str) -> tuple[bytes, dict[str, int]]:
    data = dump(engine)
    counts = {k: len(v) for k, v in data["tables"].items()}
    return seal(json.dumps(data, separators=(",", ":")).encode(), public_key_b64), counts


# ---- Abram's commands ------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m brain.backup", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("keygen", help="make the key pair")
    g.add_argument("--out", default="odys-backup-private.key", help="where the private key is written")
    o = sub.add_parser("open", help="decrypt a backup to JSON on standard output")
    o.add_argument("file")
    o.add_argument("--key", default="odys-backup-private.key")
    r = sub.add_parser("restore", help="load a backup into an empty database: the sealed file with --key, or opened JSON")
    r.add_argument("file")
    r.add_argument("--key", help="the private key, to restore a sealed backup straight from GitHub")
    r.add_argument("--database-url", required=True)
    r.add_argument("--deletions", action="append", default=[],
                   help="a NEWER backup (sealed, with --key, or opened JSON) whose deletions must also apply; "
                        "always pass the newest one when restoring an older backup (SEC-10)")
    v = sub.add_parser("verify", help="open a backup and check it is whole and consistent; writes nothing")
    v.add_argument("file")
    v.add_argument("--key", help="the private key, for a sealed backup")
    a = ap.parse_args(argv)
    if a.cmd == "keygen":
        out = Path(a.out)
        if out.exists():
            print(f"{out} already exists: keep it, or move it away first.", file=sys.stderr)
            return 1
        public, private = keygen()
        out.write_text(private + "\n", encoding="utf-8")
        out.chmod(0o600)
        print(f"Private key written to {out}. Keep it on this computer and in your password manager; never in Git,"
              f" a chat or Render. Without it the backups can't be opened.\n")
        print("Put this in Render as BRAIN_BACKUP_PUBLIC_KEY (it's safe to share):\n" + public + "\n")
        print("And this, a fresh random token, in BOTH Render and GitHub Secrets as BRAIN_BACKUP_TOKEN (it unlocks "
              "only the sealed backup):\n" + secrets.token_urlsafe(32))
        return 0
    if a.cmd == "open":
        sys.stdout.write(unseal(Path(a.file).read_bytes(), Path(a.key).read_text(encoding="utf-8")).decode())
        return 0
    try:
        data = _load(a.file, a.key)
        if a.cmd == "verify":
            problems, notes = check(data)
            counts = {k: len(v) for k, v in data["tables"].items() if isinstance(v, list)}
            print(f"Made at {data.get('made_at', '?')}: " + ", ".join(f"{k} {n}" for k, n in counts.items()))
            for n in notes:
                print("Note: " + n)
            for pr in problems:
                print("PROBLEM: " + pr, file=sys.stderr)
            print("Whole and consistent." if not problems else "Don't restore this one: use the one before it.")
            return 1 if problems else 0
        extra = [r for f in a.deletions for r in deletions_in(_load(f, a.key))]
        if not a.deletions:
            print("Reminder: if this isn't the newest backup, stop and pass the newest with --deletions, so nothing "
                  "deleted since comes back (SEC-10).", file=sys.stderr)
        from .config import driver_url
        counts = restore(db.make_engine(driver_url(a.database_url)), data, extra)
    except BackupError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("Restored: " + ", ".join(f"{k} {n}" for k, n in counts.items()))
    return 0


def _load(file: str, key: str | None) -> dict:
    """A backup as data: sealed (opened in memory with the key, so the answers are never written out in the clear) or
    already opened JSON. Damage of any kind is a BackupError, never a half-read backup."""
    raw = Path(file).read_bytes()
    if raw.startswith(MAGIC):
        if not key:
            raise BackupError("This backup is sealed: add --key and the path to your private key.")
        raw = unseal(raw, Path(key).read_text(encoding="utf-8"))
    try:
        return json.loads(raw.decode("utf-8-sig"))   # -sig: JSON saved by Windows PowerShell
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BackupError("this file isn't a whole backup: it doesn't read as JSON (cut short or damaged)") from e


if __name__ == "__main__":
    raise SystemExit(main())
