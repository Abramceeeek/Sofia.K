"""Anonymous swipe page for choosing the 16 onboarding places (D70).

A small app of its own, deployed separately from the Brain (`render.yaml`). Strangers swipe about
30 candidate London places: Loved it / It was fine / Didn't enjoy it / Haven't been.

Privacy, by design:
- no login, no names, no questions about the person;
- the only identifier is a random ID the browser makes (`crypto.randomUUID`) and keeps in local
  storage, so one person's answers stay together and they can delete them;
- the app never reads the client's address, stores only the day (not the time) of each answer,
  and runs with uvicorn's access log off (`--no-access-log`), so no IP address reaches our logs.
  The host's own edge logs are outside this code (see the page's privacy note).

Results rank places by familiarity × divisiveness:
- familiarity f = share of answers that are not "Haven't been";
- divisiveness v = variance of the reaction among people who have been (Loved = +1,
  Fine = 0, Didn't enjoy = -1): 0 when everyone agrees, 1 when half love it and half don't;
- score = f × v, the spread one swipe on this place adds for a random person. It rewards
  places most people know and disagree about, which are the ones that tell people apart.

Run locally:  uvicorn brain.calibration:app --reload   (then open http://127.0.0.1:8000)
"""

from __future__ import annotations

import csv
import hmac
import html
import io
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import Date, Integer, String, UniqueConstraint, create_engine, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "calibration"

ANSWERS = ("loved", "fine", "didnt", "not_been")
REACTION = {"loved": 1, "fine": 0, "didnt": -1}
TAGS = ("movement_views", "food", "green_nature", "history_culture", "iconic", "local_novel", "crowds",
        "walking_effort", "active", "outdoor_exposure", "photo_potential",
        "contrast_reveal", "absorption", "awe", "social_pull")
MAX_ROWS = 100_000          # the free database is 1 GB; this cap keeps a flood of fake IDs harmless
MAX_BATCH = 60

HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Robots-Tag": "noindex, nofollow",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                                "connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; "
                                "frame-ancestors 'none'"),
}


# ---- settings -----------------------------------------------------------------------------------

def database_url(raw: str) -> str:
    """Render gives `postgresql://…` (older services `postgres://…`); SQLAlchemy needs the driver."""
    for prefix in ("postgres://", "postgresql://"):
        if raw.startswith(prefix):
            return "postgresql+psycopg://" + raw[len(prefix):]
    return raw


@dataclass(frozen=True)
class CalibrationSettings:
    database_url: str
    data_dir: Path
    admin_token: str | None     # unset = results and export are switched off
    contact: str = ""           # shown in the page's privacy note, e.g. an email address


def get_settings() -> CalibrationSettings:
    return CalibrationSettings(
        database_url=database_url(os.environ.get("CALIBRATION_DATABASE_URL", "sqlite:///./calibration.db")),
        data_dir=Path(os.environ.get("CALIBRATION_DATA_DIR", str(DATA_DIR))),
        admin_token=os.environ.get("CALIBRATION_ADMIN_TOKEN") or None,
        contact=os.environ.get("CALIBRATION_CONTACT", ""),
    )


# ---- storage ------------------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class CalibrationAnswer(Base):
    __tablename__ = "calibration_answers"
    __table_args__ = (UniqueConstraint("browser_id", "place_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    browser_id: Mapped[str] = mapped_column(String(36), index=True)   # random UUID made by the browser
    place_id: Mapped[str] = mapped_column(String(40))
    answer: Mapped[str] = mapped_column(String(10))
    day: Mapped[date] = mapped_column(Date)                           # day only, never the time


# ---- places -------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Place:
    id: str
    name: str
    area: str
    icon: str
    line: str
    tags: dict[str, int]
    swipe_item: int | None = None


def load_places(path: Path) -> list[Place]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    places = []
    for p in doc["places"]:
        tags = {**p.get("place", {}), **p.get("moment", {})}
        places.append(Place(id=p["id"], name=p["name"], area=p.get("area", ""), icon=p.get("icon", ""),
                            line=p.get("line", ""), tags={t: int(tags.get(t, 0)) for t in TAGS},
                            swipe_item=p.get("swipe_item")))
    ids = [p.id for p in places]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate place ids in " + str(path))
    return places


# ---- ranking ------------------------------------------------------------------------------------

@dataclass
class PlaceResult:
    place_id: str
    name: str
    answers: int
    loved: int
    fine: int
    didnt: int
    not_been: int
    familiarity: float
    mean: float | None
    divisiveness: float | None
    score: float
    low_n: bool
    recommended: bool = False
    rank: int = 0


def rank_places(rows: list[tuple[str, str, str]], places: list[Place], *, n_pick: int = 16,
                min_answers: int = 10, min_visitors: int = 5) -> dict:
    """Rank candidates from (browser_id, place_id, answer) rows.

    Only browsers with at least `min_answers` answers count, so drive-by visitors don't skew the
    shares. Places with fewer than `min_visitors` people who have been are flagged `low_n` and ranked
    after the rest, because a variance from two or three people is noise.
    """
    known = {p.id for p in places}
    per_browser: dict[str, dict[str, str]] = defaultdict(dict)
    for browser, place, answer in rows:
        if place in known and answer in ANSWERS:
            per_browser[browser][place] = answer
    included = {b: a for b, a in per_browser.items() if len(a) >= min_answers}
    straight = sum(1 for a in included.values() if len(set(a.values())) == 1)

    counts: dict[str, Counter] = {p.id: Counter() for p in places}
    for answers in included.values():
        for place, answer in answers.items():
            counts[place][answer] += 1

    results = []
    for p in places:
        c = counts[p.id]
        n = sum(c.values())
        been = c["loved"] + c["fine"] + c["didnt"]
        f = been / n if n else 0.0
        if been:
            mean = (c["loved"] - c["didnt"]) / been
            var = (c["loved"] + c["didnt"]) / been - mean ** 2
        else:
            mean = var = None
        results.append(PlaceResult(p.id, p.name, n, c["loved"], c["fine"], c["didnt"], c["not_been"],
                                   round(f, 3), None if mean is None else round(mean, 3),
                                   None if var is None else round(var, 3),
                                   round(f * (var or 0.0), 3), been < min_visitors))
    results.sort(key=lambda r: (not r.low_n, r.score, r.familiarity), reverse=True)
    for i, r in enumerate(results, start=1):
        r.rank = i
        r.recommended = i <= n_pick and not r.low_n

    return {
        "browsers_total": len(per_browser),
        "browsers_included": len(included),
        "straight_liners": straight,
        "rules": {"min_answers_per_browser": min_answers, "min_visitors_per_place": min_visitors, "n_pick": n_pick},
        "n_recommended": sum(r.recommended for r in results),
        "places": [r.__dict__ for r in results],
        "coverage": coverage(results, places),
    }


def coverage(results: list[PlaceResult], places: list[Place], min_items: int = 2) -> list[dict]:
    """Warn when the recommended set has fewer than `min_items` places carrying a taste tag.

    A tag that barely varies across the swiped places can't be learned from swipes. The fix offered
    is the best-ranked place outside the set that has the tag; swapping it in is Abram's call.
    """
    by_id = {p.id: p for p in places}
    picked = [r.place_id for r in results if r.recommended]
    rest = [r.place_id for r in results if not r.recommended and not r.low_n]
    warnings = []
    if not picked:
        return warnings
    for tag in TAGS:
        have = sum(1 for pid in picked if by_id[pid].tags[tag] >= 1)
        if have < min_items:
            alt = next((pid for pid in rest if by_id[pid].tags[tag] >= 1), None)
            warnings.append({"tag": tag, "in_set": have,
                             "best_outside": by_id[alt].name if alt else None})
    return warnings


# ---- API ----------------------------------------------------------------------------------------

class AnswerIn(BaseModel):
    place_id: str = Field(max_length=40)
    answer: Literal["loved", "fine", "didnt", "not_been"]


class AnswersIn(BaseModel):
    browser_id: UUID
    answers: list[AnswerIn] = Field(min_length=1, max_length=MAX_BATCH)


def create_app(settings: CalibrationSettings | None = None) -> FastAPI:
    settings = settings or get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    make_session = sessionmaker(engine, expire_on_commit=False)
    places = load_places(settings.data_dir / "places.yaml")
    place_ids = {p.id for p in places}
    page = (settings.data_dir / "index.html").read_text(encoding="utf-8").replace(
        "{{CONTACT}}", html.escape(settings.contact, quote=True))
    results_page = (settings.data_dir / "results.html").read_text(encoding="utf-8")

    app = FastAPI(title="London places: quick swipe", docs_url=None, redoc_url=None, openapi_url=None)

    def db():
        with make_session() as s:
            yield s

    def admin(x_admin_token: str | None = Header(default=None)):
        if not settings.admin_token:
            raise HTTPException(404, "not found")
        if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
            raise HTTPException(401, "wrong or missing admin token")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return HTMLResponse(page, headers=HEADERS)

    @app.get("/results", response_class=HTMLResponse)
    def results_view():
        return HTMLResponse(results_page, headers=HEADERS)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/api/places")
    def get_places():
        return {"places": [{"id": p.id, "name": p.name, "area": p.area, "icon": p.icon, "line": p.line}
                           for p in places]}

    @app.post("/api/answers")
    def post_answers(body: AnswersIn, s: Session = Depends(db)):
        unknown = [a.place_id for a in body.answers if a.place_id not in place_ids]
        if unknown:
            raise HTTPException(422, f"unknown place: {unknown[0]}")
        if s.scalar(select(func.count()).select_from(CalibrationAnswer)) >= MAX_ROWS:
            raise HTTPException(503, "the survey is full; thank you")
        browser, today = str(body.browser_id), datetime.now(timezone.utc).date()
        latest = {a.place_id: a.answer for a in body.answers}      # the last answer in a batch wins
        existing = {r.place_id: r for r in s.scalars(select(CalibrationAnswer).where(
            CalibrationAnswer.browser_id == browser, CalibrationAnswer.place_id.in_(latest)))}
        for place, answer in latest.items():
            if place in existing:
                existing[place].answer, existing[place].day = answer, today
            else:
                s.add(CalibrationAnswer(browser_id=browser, place_id=place, answer=answer, day=today))
        try:
            s.commit()
        except IntegrityError:                                     # the same answer sent twice at once
            s.rollback()
        return {"saved": len(latest)}

    @app.delete("/api/answers/{browser_id}")
    def delete_answers(browser_id: UUID, s: Session = Depends(db)):
        n = s.execute(delete(CalibrationAnswer).where(CalibrationAnswer.browser_id == str(browser_id))).rowcount
        s.commit()
        return {"deleted": n}

    def _rows(s: Session) -> list[tuple[str, str, str]]:
        return [(r.browser_id, r.place_id, r.answer) for r in s.scalars(select(CalibrationAnswer))]

    @app.get("/api/results", dependencies=[Depends(admin)])
    def results(n_pick: int = 16, min_answers: int = 10, min_visitors: int = 5, s: Session = Depends(db)):
        return rank_places(_rows(s), places, n_pick=n_pick, min_answers=min_answers, min_visitors=min_visitors)

    @app.get("/api/results.csv", dependencies=[Depends(admin)], response_class=PlainTextResponse)
    def results_csv(n_pick: int = 16, min_answers: int = 10, min_visitors: int = 5, s: Session = Depends(db)):
        ranked = rank_places(_rows(s), places, n_pick=n_pick, min_answers=min_answers, min_visitors=min_visitors)
        out = io.StringIO()
        cols = ["rank", "recommended", "place_id", "name", "answers", "loved", "fine", "didnt", "not_been",
                "familiarity", "mean", "divisiveness", "score", "low_n"]
        w = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(ranked["places"])
        return PlainTextResponse(out.getvalue(), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=swipe-ranking.csv"})

    @app.get("/api/export.csv", dependencies=[Depends(admin)], response_class=PlainTextResponse)
    def export_csv(s: Session = Depends(db)):
        """Every answer, for a backup before the free database expires (30 days after creation)."""
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["browser_id", "place_id", "answer", "day"])
        for r in s.scalars(select(CalibrationAnswer).order_by(CalibrationAnswer.id)):
            w.writerow([r.browser_id, r.place_id, r.answer, r.day.isoformat()])
        return PlainTextResponse(out.getvalue(), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=swipe-answers.csv"})

    return app


def __getattr__(name: str):
    # `uvicorn brain.calibration:app` builds the app on first use, so importing this module
    # (e.g. in tests) doesn't touch a database.
    if name == "app":
        globals()["app"] = create_app()
        return globals()["app"]
    raise AttributeError(name)
