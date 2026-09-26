"""The brain's HTTP API, used by the SwiftUI app (the face) and by Abram's admin tools.

Run locally:  uvicorn brain.api:app --app-dir src --reload     (docs at /docs)
"""

from __future__ import annotations

import csv
import hashlib
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import db, notify
from .config import Settings, get_settings
from .features import Conditions, conjoint_plan_features, moment_features
from .moments import Moment, load_moments
from .personal import DeltaPosterior, prior_only
from .planner import Candidate, LegWeights, hhmm, parse_hhmm, plan_day
from .population import PopulationModel, load_population
from .schemas import (AnswersIn, ChoicesIn, CuratedPlanIn, EventIn, InstallIn, InstallOut, PlanFeedbackIn,
                      PlanRequest, ProfileIn, RatingIn, SafetyIn, SafetyReplyIn, SwipesIn)
from .scoring import (conjoint_observation, contributions, named_weights, rating_observation,
                      swipe_observation, update_person)
from .travel import WalkingEstimate


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = db.make_engine(settings.database_url)
        app.state.Session = db.make_sessionmaker(engine)
        app.state.pop = load_population(settings.data_dir / "priors.yaml")
        with open(settings.data_dir / "onboarding.yaml", encoding="utf-8") as f:
            app.state.onboarding = yaml.safe_load(f)
        rows = list(csv.DictReader(open(settings.data_dir / "conjoint_design.csv", encoding="utf-8")))
        tasks: dict[int, dict] = {}
        for r in rows:
            tasks.setdefault(int(r["task"]), {})[r["plan"]] = r
        app.state.tasks = tasks
        with app.state.Session() as s:   # load the moment files into an empty database
            if s.scalar(select(db.MomentRow.id).limit(1)) is None:
                _reload_moments(s, settings)
        yield
        engine.dispose()

    app = FastAPI(title="Brain: moment planner API", version="0.1.0", lifespan=lifespan)

    # ---- dependencies -------------------------------------------------------------
    def session():
        with app.state.Session() as s:
            yield s

    def pop() -> PopulationModel:
        return app.state.pop

    def current_user(authorization: str = Header(default=""), s: Session = Depends(session)) -> db.User:
        token = authorization.removeprefix("Bearer ").strip()
        user = s.scalar(select(db.User).where(db.User.token_hash == _hash(token))) if token else None
        if user is None:
            raise HTTPException(401, "unknown install token")
        return user

    def admin(authorization: str = Header(default="")) -> None:
        token = authorization.removeprefix("Bearer ").strip()
        if not settings.admin_token or not secrets.compare_digest(token, settings.admin_token):
            raise HTTPException(403, "admin only")

    # ---- helpers ------------------------------------------------------------------
    def moments_by_id(s: Session) -> dict[str, Moment]:
        return {r.id: Moment.model_validate(r.record) for r in s.scalars(select(db.MomentRow))}

    def posterior(user: db.User, p: PopulationModel) -> DeltaPosterior:
        if user.delta and user.population_version == p.version:
            return DeltaPosterior.from_json(user.delta)
        return prior_only(p.delta_prior_sd)

    def refit(s: Session, user: db.User, p: PopulationModel) -> DeltaPosterior:
        """Rebuild δ_person from everything this person has told us (swipes, choices, ratings)."""
        ms = moments_by_id(s)
        obs = []
        for sw in user.swipes:
            if sw.moment_id in ms and (o := swipe_observation(p, ms[sw.moment_id], sw.reaction)):
                obs.append(o)
        for ch in user.choices:
            t = app.state.tasks.get(ch.task)
            if t:
                obs.append(conjoint_observation(p, conjoint_plan_features(t["A"]),
                                                conjoint_plan_features(t["B"]), chose_a=ch.choice == "A"))
        for r in user.ratings:
            if r.moment_id in ms:
                obs.append(rating_observation(p, ms[r.moment_id], r.rating,
                                              Conditions(r.temp_c, r.rain_prob), r.travel_min))
        post = update_person(p, obs)
        user.delta, user.population_version = post.to_json(), p.version
        return post

    def card(m: Moment) -> dict:
        start = m.start()
        return {
            "id": m.id, "title": m.title, "status": m.status, "place": m.place.model_dump(),
            "approach": {"from": m.approach.from_, "path": m.approach.path, "step_free": m.approach.step_free,
                         "start_point": start.model_dump() if start else None},
            "what_happens": m.experience.what_happens, "best_time": m.best_time.model_dump(),
            "cost_gbp": m.cost_gbp, "shot_card": m.shot_card.model_dump() if m.shot_card else None,
            "plannable": m.plannable(),
        }

    def plan_out(plan: db.Plan) -> dict:
        return {"id": plan.id, "kind": plan.kind, "label": plan.label, "date": plan.date, "intent": plan.intent,
                "stops": plan.stops, "value": plan.value, "status": plan.status,
                "fit_rating": plan.fit_rating, "created_at": plan.created_at.isoformat()}

    # ---- public -------------------------------------------------------------------
    @app.get("/v1/health")
    def health():
        return {"ok": True, "population_version": app.state.pop.version}

    @app.post("/v1/installs", response_model=InstallOut, status_code=201)
    def register(body: InstallIn, s: Session = Depends(session)):
        if not body.consent.research:
            raise HTTPException(400, "consent is needed to take part")
        token = secrets.token_urlsafe(32)
        user = db.User(id=str(uuid.uuid4()), token_hash=_hash(token), channel=body.channel, src=body.src,
                       consent_version=body.consent.version, consent_ai=body.consent.ai_processing, profile={})
        s.add(user)
        s.commit()
        return InstallOut(user_id=user.id, token=token)

    @app.get("/v1/onboarding")
    def onboarding(user: db.User = Depends(current_user), s: Session = Depends(session)):
        ms = moments_by_id(s)
        tasks = [{"task": k, "A": v["A"]["description"], "B": v["B"]["description"]}
                 for k, v in sorted(app.state.tasks.items())]
        return {**app.state.onboarding, "swipe_cards": [card(m) for m in ms.values() if m.swipe],
                "conjoint_tasks": tasks}

    @app.post("/v1/me/swipes", status_code=204)
    def post_swipes(body: SwipesIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                    p: PopulationModel = Depends(pop)):
        for it in body.items:
            s.add(db.Swipe(user_id=user.id, moment_id=it.moment_id, reaction=it.reaction))
        s.flush()
        s.refresh(user)
        refit(s, user, p)
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/conjoint", status_code=204)
    def post_choices(body: ChoicesIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                     p: PopulationModel = Depends(pop)):
        for it in body.items:
            if it.task not in app.state.tasks:
                raise HTTPException(422, f"unknown task {it.task}")
            s.add(db.ConjointChoice(user_id=user.id, task=it.task, choice=it.choice))
        s.flush()
        s.refresh(user)
        refit(s, user, p)
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/answers", status_code=204)
    def post_answers(body: AnswersIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        for it in body.items:
            s.add(db.Answer(user_id=user.id, question=it.question, text=it.text, input_mode=it.input_mode))
        s.commit()
        return Response(status_code=204)

    @app.put("/v1/me/profile", status_code=204)
    def put_profile(body: ProfileIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        user.profile = body.model_dump(exclude_none=True)
        s.commit()
        return Response(status_code=204)

    @app.get("/v1/me/weights")
    def weights(user: db.User = Depends(current_user), p: PopulationModel = Depends(pop)):
        post = posterior(user, p)
        return {"n_observations": post.n_obs, "population_version": p.version,
                "weights": [w.__dict__ for w in named_weights(p, post)]}

    @app.get("/v1/moments")
    def list_moments(plannable_only: bool = False, _: db.User = Depends(current_user),
                     s: Session = Depends(session)):
        return [card(m) for m in moments_by_id(s).values() if m.plannable() or not plannable_only]

    @app.get("/v1/moments/{moment_id}")
    def get_moment(moment_id: str, _: db.User = Depends(current_user), s: Session = Depends(session)):
        row = s.get(db.MomentRow, moment_id)
        if row is None:
            raise HTTPException(404, "no such moment")
        return card(Moment.model_validate(row.record))

    @app.post("/v1/me/plans", status_code=201)
    def make_plan(body: PlanRequest, user: db.User = Depends(current_user), s: Session = Depends(session),
                  p: PopulationModel = Depends(pop)):
        b = p.b_person(posterior(user, p).mean)
        cond = Conditions(body.conditions.temp_c, body.conditions.rain_prob) if body.conditions else Conditions()
        ms = {k: m for k, m in moments_by_id(s).items() if m.plannable()}
        if cond.rain_prob is not None and cond.rain_prob >= 0.5:
            ms = {k: m for k, m in ms.items() if m.best_time.weather != ["dry"]}
        cands = [Candidate(m.id, m.start(), m.end(), int(round(m.duration_min())), tuple(m.windows()),
                           float(p.vector(moment_features(m, cond)) @ b)) for m in ms.values()]
        idx = {n: i for i, n in enumerate(p.names)}
        legs = LegWeights(b[idx["transfer_15_30"]], b[idx["transfer_30_plus"]], b[idx["packed_pace"]])
        result = plan_day(cands, body.start, parse_hhmm(body.start_time), parse_hhmm(body.end_time),
                          WalkingEstimate(), legs, floor=p.cutpoints["rating"][1], max_stops=body.max_stops,
                          peak_end=body.peak_end, time_limit_s=settings.planner_time_limit_s)
        stops = []
        for st in result.stops:
            m = ms[st.moment_id]
            why = contributions(p, b, moment_features(m, cond, st.travel_min))
            stops.append({**card(m), "moment_id": m.id, "arrive": hhmm(st.arrive_min), "depart": hhmm(st.depart_min),
                          "travel_min": st.travel_min, "predicted": st.utility, "why": why})
        plan = db.Plan(user_id=user.id, kind="personal", date=body.date, intent=body.intent, stops=stops,
                       value=result.value)
        s.add(plan)
        s.commit()
        return {**plan_out(plan), "peak_moment_id": result.peak_moment_id,
                "end_bonus_applied": result.end_bonus_applied, "solver_status": result.status}

    @app.get("/v1/me/plans")
    def my_plans(user: db.User = Depends(current_user)):
        return [plan_out(pl) for pl in sorted(user.plans, key=lambda x: x.id, reverse=True)]

    @app.get("/v1/me/plans/{plan_id}")
    def my_plan(plan_id: int, user: db.User = Depends(current_user), s: Session = Depends(session)):
        pl = s.get(db.Plan, plan_id)
        if pl is None or pl.user_id != user.id:
            raise HTTPException(404, "no such plan")
        return plan_out(pl)

    @app.post("/v1/me/plans/{plan_id}/feedback", status_code=204)
    def plan_feedback(plan_id: int, body: PlanFeedbackIn, user: db.User = Depends(current_user),
                      s: Session = Depends(session)):
        pl = s.get(db.Plan, plan_id)
        if pl is None or pl.user_id != user.id:
            raise HTTPException(404, "no such plan")
        pl.status = "chosen" if body.chosen else "not_chosen"
        pl.fit_rating, pl.reason = body.fit_rating, body.reason
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/ratings", status_code=201)
    def rate(body: RatingIn, user: db.User = Depends(current_user), s: Session = Depends(session),
             p: PopulationModel = Depends(pop)):
        if s.get(db.MomentRow, body.moment_id) is None:
            raise HTTPException(404, "no such moment")
        if body.plan_id is not None:
            pl = s.get(db.Plan, body.plan_id)
            if pl is None or pl.user_id != user.id:
                raise HTTPException(404, "no such plan")
        c = body.conditions
        s.add(db.Rating(user_id=user.id, plan_id=body.plan_id, moment_id=body.moment_id, rating=body.rating,
                        would_bring=body.would_bring, temp_c=c.temp_c if c else None,
                        rain_prob=c.rain_prob if c else None, travel_min=body.travel_min))
        s.flush()
        s.refresh(user)
        post = refit(s, user, p)
        s.commit()
        return {"n_observations": post.n_obs}

    @app.post("/v1/me/events", status_code=204)
    def event(body: EventIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        s.add(db.Event(user_id=user.id, name=body.name, props=body.props))
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/safety", status_code=201)
    def safety(body: SafetyIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        alert = db.SafetyAlert(user_id=user.id, message=body.message)
        s.add(alert)
        s.commit()
        alert.notified = notify.send_alert(settings.alert_webhook_url, alert.id, user.id, body.message)
        s.commit()
        return {"alert_id": alert.id, "message": notify.USER_MESSAGE}

    @app.delete("/v1/me", status_code=204)
    def delete_me(user: db.User = Depends(current_user), s: Session = Depends(session)):
        """Delete everything about this install (App Review 5.1.1(v); UK GDPR erasure)."""
        s.delete(user)
        s.commit()
        return Response(status_code=204)

    # ---- admin (Abram) ------------------------------------------------------------
    @app.post("/v1/admin/moments/reload", dependencies=[Depends(admin)])
    def reload_moments(s: Session = Depends(session)):
        return _reload_moments(s, settings)

    @app.get("/v1/admin/safety", dependencies=[Depends(admin)])
    def open_alerts(s: Session = Depends(session)):
        rows = s.scalars(select(db.SafetyAlert).where(db.SafetyAlert.first_reply_at.is_(None))
                         .order_by(db.SafetyAlert.created_at))
        return [{"id": a.id, "user_id": a.user_id, "message": a.message, "created_at": a.created_at.isoformat(),
                 "notified": a.notified} for a in rows]

    @app.post("/v1/admin/safety/{alert_id}/reply", dependencies=[Depends(admin)])
    def mark_replied(alert_id: int, body: SafetyReplyIn, s: Session = Depends(session)):
        a = s.get(db.SafetyAlert, alert_id)
        if a is None:
            raise HTTPException(404, "no such alert")
        a.first_reply_at, a.replied_by = datetime.now(timezone.utc), body.replied_by
        s.commit()
        created = a.created_at if a.created_at.tzinfo else a.created_at.replace(tzinfo=timezone.utc)
        return {"id": a.id, "minutes_to_first_reply": round((a.first_reply_at - created).total_seconds() / 60, 1)}

    @app.post("/v1/admin/users/{user_id}/plans", status_code=201, dependencies=[Depends(admin)])
    def push_curated_plan(user_id: str, body: CuratedPlanIn, s: Session = Depends(session)):
        """Phase 3 Wizard of Oz: Abram writes the plan, the app shows it like any other."""
        if s.get(db.User, user_id) is None:
            raise HTTPException(404, "no such user")
        ms = moments_by_id(s)
        missing = [st.moment_id for st in body.stops if st.moment_id not in ms]
        if missing:
            raise HTTPException(422, f"unknown moments: {missing}")
        stops = [{**card(ms[st.moment_id]), "moment_id": st.moment_id, "arrive": st.arrive} for st in body.stops]
        plan = db.Plan(user_id=user_id, kind=body.kind, label=body.label, date=body.date, intent=body.intent,
                       stops=stops)
        s.add(plan)
        s.commit()
        return plan_out(plan)

    @app.get("/v1/admin/export", dependencies=[Depends(admin)])
    def export(s: Session = Depends(session)):
        """Everything needed for the Phase 3 read-out, keyed by user id (no names are stored)."""
        def rows(model):
            return [{c.name: (v.isoformat() if isinstance(v := getattr(r, c.name), datetime) else v)
                     for c in model.__table__.columns if c.name != "token_hash"}
                    for r in s.scalars(select(model))]
        return {name: rows(model) for name, model in [
            ("users", db.User), ("swipes", db.Swipe), ("conjoint_choices", db.ConjointChoice),
            ("answers", db.Answer), ("plans", db.Plan), ("ratings", db.Rating), ("events", db.Event),
            ("safety_alerts", db.SafetyAlert)]}

    return app


def _reload_moments(s: Session, settings: Settings) -> dict:
    moments = load_moments(settings.data_dir / "moments")
    for m in moments:
        row = s.get(db.MomentRow, m.id)
        record = m.model_dump(by_alias=True)
        if row is None:
            s.add(db.MomentRow(id=m.id, record=record))
        else:
            row.record = record
    s.commit()
    return {"loaded": len(moments), "plannable": sum(m.plannable() for m in moments),
            "drafts": {m.id: m.missing_for_planning() for m in moments if not m.plannable()}}


app = create_app()
