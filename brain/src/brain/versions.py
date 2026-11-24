"""m327 (Abram, 24 Nov: "Save the exact commit and build identifier used by the friends. Otherwise, feedback from
different versions could become mixed"): every plan row records the Brain commit that made it and the app build that
asked for it, so ratings and Test B answers can be read per version.

- The Brain's commit is Render's `RENDER_GIT_COMMIT` (first 7 characters), as `/v1/health` reports it.
- The app's build comes from the `X-ODYS-Build` header both apps send ("ios-114", "android-22"). Anything else is
  ignored, so the header can't carry free text into the database. Neither is personal data.
"""
from __future__ import annotations

import os
import re
from contextvars import ContextVar

from sqlalchemy import event

APP_BUILD: ContextVar[str | None] = ContextVar("app_build", default=None)
HEADER = "x-odys-build"
_OK = re.compile(r"^(ios|android)-\d{1,7}$")


def brain_version() -> str | None:
    return (os.environ.get("RENDER_GIT_COMMIT") or "")[:7] or None


def app_build(value: str | None) -> str | None:
    """The header's value if it's a build identifier, else None."""
    v = (value or "").strip().lower()
    return v if _OK.match(v) else None


def stamp(intent: dict | None) -> dict:
    return {**(intent or {}), "versions": {"brain": brain_version(), "app": APP_BUILD.get()}}


_installed = False


def install_plan_stamp(plan_cls) -> None:
    """Stamp each new plan row once, whichever route creates it."""
    global _installed
    if _installed:
        return

    @event.listens_for(plan_cls, "before_insert")
    def _stamp(mapper, connection, target):   # noqa: ARG001 - SQLAlchemy's signature
        target.intent = stamp(target.intent)

    _installed = True
