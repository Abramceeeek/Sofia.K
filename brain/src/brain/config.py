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


def get_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("BRAIN_DATABASE_URL", "sqlite:///./brain.db"),
        data_dir=Path(os.environ.get("BRAIN_DATA_DIR", str(DATA_DIR))),
        admin_token=os.environ.get("BRAIN_ADMIN_TOKEN") or None,
        alert_webhook_url=os.environ.get("BRAIN_ALERT_WEBHOOK_URL") or None,
        planner_time_limit_s=float(os.environ.get("BRAIN_PLANNER_TIME_LIMIT_S", "1.0")),
    )
