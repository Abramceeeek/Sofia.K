"""Nightly encrypted backups (roadmap Stage 1, step 5).

Why our own: Render's free database has no backups. A paid one keeps point-in-time recovery for the past 3 days on a
Hobby workspace (7 on Pro), and its downloadable exports are made by hand and kept 7 days
(render.com/docs/postgresql-backups, read 19 Oct 2026). The testers' answers are the evidence for Checkpoint 3, so a
copy is also kept away from Render.

- **What:** every row of the Brain's tables and of the swipe page's answers, as JSON. Not the cards or TfL's times,
  which are rebuilt at every start, and never the contacts left with a safety message (D118).
- **Sealed on the server:** compressed, then encrypted to Abram's public key (X25519, HKDF-SHA256 and AES-256-GCM,
  from the `cryptography` library) before it leaves the server. Only his private key, kept on his own computer,
  opens it. So the copy can sit in this public repository's workflow artifacts, which anyone may download.
- **Where:** a GitHub Actions job (`.github/workflows/ops.yml`) fetches it each night with `BRAIN_BACKUP_TOKEN`, a
  token that unlocks only this, and keeps it for 30 days.
- **Commands** (on Abram's computer, from `brain/`, after `pip install cryptography`):
  - `python -m brain.backup keygen`: makes the key pair, keeps the private key in a file, and prints the public key
    for Render and a fresh BRAIN_BACKUP_TOKEN for Render and GitHub Secrets;
  - `python -m brain.backup open odys-brain-20261020.odysbk --key odys-backup-private.key > backup.json`;
  - `python -m brain.backup restore backup.json --database-url postgresql://…`: into an empty database.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import os
import secrets
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import Date, DateTime, Integer, Table, func, inspect, select, text
from sqlalchemy.engine import Engine

from . import calibration, db

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
                out[t.name] = [{k: _plain(v) for k, v in r._mapping.items()} for r in c.execute(select(t))]
    return {"format": 1, "made_at": datetime.now(timezone.utc).isoformat(), "tables": out}


def _typed(t: Table, row: dict) -> dict:
    out = {}
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


def restore(engine: Engine, data: dict) -> dict[str, int]:
    """Into an empty database: the tables are made, then filled. Refuses a table that already has rows."""
    if data.get("format") != 1:
        raise BackupError("not a backup this version can read")
    db.Base.metadata.create_all(engine)
    calibration.Base.metadata.create_all(engine)
    counts = {}
    with engine.begin() as c:
        for t in tables():
            rows = data["tables"].get(t.name, [])
            if c.execute(select(func.count()).select_from(t)).scalar():
                raise BackupError(f"{t.name} already has rows: restore into an empty database")
            if rows:
                c.execute(t.insert(), [_typed(t, r) for r in rows])
            counts[t.name] = len(rows)
            pk = list(t.primary_key.columns)
            if engine.dialect.name == "postgresql" and rows and len(pk) == 1 and isinstance(pk[0].type, Integer):
                # the next new row's id follows on from the restored ones
                c.execute(text(f"SELECT setval(pg_get_serial_sequence('{t.name}', '{pk[0].name}'), "
                               f"(SELECT MAX({pk[0].name}) FROM {t.name}))"))
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
    r = sub.add_parser("restore", help="load a decrypted backup into an empty database")
    r.add_argument("file")
    r.add_argument("--database-url", required=True)
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
    from .config import driver_url
    engine = db.make_engine(driver_url(a.database_url))
    counts = restore(engine, json.loads(Path(a.file).read_text(encoding="utf-8")))
    print("Restored: " + ", ".join(f"{k} {n}" for k, n in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
