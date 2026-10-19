"""Settings from environment variables, with local-development defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class Settings:
    database_url: str
    data_dir: Path
    admin_token: str | None          # unset = admin endpoints disabled
    alert_webhook_url: str | None    # where safety alerts are posted (Abram, and the backup helper)
    planner_time_limit_s: float
    testflight_url: str | None = None   # D114: the public TestFlight link a share page offers; unset until external testing
    duffel_token: str | None = None     # D120: flight search; unset = sample flights, clearly labelled
    liteapi_key: str | None = None      # D120: places to stay; unset = sample stays, clearly labelled
    tfl_app_key: str | None = None      # Stage 1: TfL journey times; unset = the straight-line estimate
    met_office_key: str | None = None   # Stage 1: Met Office forecast; unset = no weather, as before
    backup_key: str | None = None       # Stage 1: the public key nightly backups are encrypted to (ops.py)


def driver_url(raw: str) -> str:
    """Render gives `postgresql://…` (older services `postgres://…`); SQLAlchemy needs the psycopg driver."""
    for prefix in ("postgres://", "postgresql://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix):]
    return raw


def _first(*names: str) -> str | None:
    """The first of these environment variables that is set: the keys may have been named a little differently in
    Render, and /v1/health says whether each was found (never its value)."""
    for n in names:
        if v := (os.environ.get(n) or "").strip():
            return v
    return None


def get_settings() -> Settings:
    return Settings(
        database_url=driver_url(os.environ.get("BRAIN_DATABASE_URL", "sqlite:///./brain.db")),
        data_dir=Path(os.environ.get("BRAIN_DATA_DIR", str(DATA_DIR))),
        admin_token=os.environ.get("BRAIN_ADMIN_TOKEN") or None,
        alert_webhook_url=os.environ.get("BRAIN_ALERT_WEBHOOK_URL") or None,
        planner_time_limit_s=float(os.environ.get("BRAIN_PLANNER_TIME_LIMIT_S", "1.0")),
        testflight_url=os.environ.get("BRAIN_TESTFLIGHT_URL") or None,
        duffel_token=os.environ.get("DUFFEL_ACCESS_TOKEN") or None,
        liteapi_key=os.environ.get("LITEAPI_KEY") or None,
        tfl_app_key=_first("TFL_APP_KEY", "TFL_API_KEY", "TFL_KEY", "TFL_PRIMARY_KEY"),
        met_office_key=_first("MET_OFFICE_API_KEY", "MET_OFFICE_KEY", "METOFFICE_API_KEY", "MET_API_KEY",
                              "MET_OFFICE_DATAHUB_KEY"),
        backup_key=_first("BRAIN_BACKUP_PUBLIC_KEY"),
    )
