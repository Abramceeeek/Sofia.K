"""Database tables (SQLAlchemy 2.0). SQLite locally; Postgres in production via BRAIN_DATABASE_URL.

What is stored is what the app needs and nothing more: no audio (voice is transcribed on the
phone, if used at all), no nationality, no health data, no allergy question (D19).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    """One install of the app. No login: the app holds a random token (App Review 5.1.1(v))."""
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    channel: Mapped[str] = mapped_column(String(32))            # stranger | friends_family (D43)
    src: Mapped[str | None] = mapped_column(String(128))        # recruitment source code
    consent_version: Mapped[str] = mapped_column(String(32))
    consent_ai: Mapped[bool] = mapped_column(Boolean)           # may we send their text to an AI service?
    profile: Mapped[dict] = mapped_column(JSON, default=dict)   # budget band, company, morning/night, ...
    delta: Mapped[dict | None] = mapped_column(JSON)            # DeltaPosterior.to_json()
    population_version: Mapped[str | None] = mapped_column(String(16))

    swipes = relationship("Swipe", cascade="all, delete-orphan", passive_deletes=True)
    choices = relationship("ConjointChoice", cascade="all, delete-orphan", passive_deletes=True)
    answers = relationship("Answer", cascade="all, delete-orphan", passive_deletes=True)
    plans = relationship("Plan", cascade="all, delete-orphan", passive_deletes=True)
    ratings = relationship("Rating", cascade="all, delete-orphan", passive_deletes=True)
    events = relationship("Event", cascade="all, delete-orphan", passive_deletes=True)
    alerts = relationship("SafetyAlert", cascade="all, delete-orphan", passive_deletes=True)
    referral = relationship("Referral", cascade="all, delete-orphan", passive_deletes=True, uselist=False)


class Swipe(Base):
    __tablename__ = "swipes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    item: Mapped[int] = mapped_column(Integer)                  # a locked swipe place, 1-16 (D107)
    reaction: Mapped[str] = mapped_column(String(16))           # loved | fine | didnt_enjoy | havent_been | skip
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ConjointChoice(Base):
    __tablename__ = "conjoint_choices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    task: Mapped[int] = mapped_column(Integer)
    choice: Mapped[str] = mapped_column(String(1))              # A | B | N (no preference, D110)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Answer(Base):
    """Free-text answers (e.g. "the best hour of your last trip"). Text only, never audio."""
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text)
    input_mode: Mapped[str] = mapped_column(String(16))         # typed | voice (for the Test A split)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    kind: Mapped[str] = mapped_column(String(16))               # personal | generic | curated (Wizard of Oz)
    label: Mapped[str | None] = mapped_column(String(8))        # "A" / "B" when offered as a pair (Test B)
    date: Mapped[str | None] = mapped_column(String(10))
    intent: Mapped[dict] = mapped_column(JSON, default=dict)    # trip intent stored per plan (D27)
    stops: Mapped[list] = mapped_column(JSON)
    value: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default="offered")  # offered | chosen | not_chosen
    fit_rating: Mapped[int | None] = mapped_column(Integer)     # "This plan fits me" 1-5 (Test B)
    reason: Mapped[str | None] = mapped_column(Text)


class Rating(Base):
    """One-tap 1-5 after a stop, with the conditions it was experienced in (the key data)."""
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id", ondelete="SET NULL"))
    moment_id: Mapped[str] = mapped_column(String(64))
    rating: Mapped[int] = mapped_column(Integer)
    would_bring: Mapped[bool | None] = mapped_column(Boolean)   # "Would you bring someone here?" (social pull)
    temp_c: Mapped[float | None] = mapped_column(Float)
    rain_prob: Mapped[float | None] = mapped_column(Float)
    travel_min: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Event(Base):
    """App events for Test A measures: screen reached, time taken, completion."""
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    props: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SafetyAlert(Base):
    """Always goes to a person (CLAUDE.md, D46). Never handled by the AI alone."""
    __tablename__ = "safety_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)
    first_reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replied_by: Mapped[str | None] = mapped_column(String(64))


class Referral(Base):
    """D114: a person's share-link code, made the first time they share a moment. Someone who installs through the
    link gets `src = "ref:<code>"` on their own row; nothing else links the two, and no names exist."""
    __tablename__ = "referrals"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class LinkOpen(Base):
    """D114: one opening of a share link's page in a browser (counted by the page's script, so link previews don't
    count). Nothing about the person who opened it: no address, no device, no user id."""
    __tablename__ = "link_opens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(12), index=True)
    moment_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MomentRow(Base):
    """The moment database: the full record as JSON, validated by brain.moments.Moment."""
    __tablename__ = "moments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    record: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


def make_engine(url: str):
    kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    engine = create_engine(url, **kwargs)
    if url.startswith("sqlite"):
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def _fk_on(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")
    return engine


def make_sessionmaker(engine):
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
