"""The brain's HTTP API, used by the SwiftUI app (the face) and by Abram's admin tools.

Run locally:  uvicorn brain.api:app --app-dir src --reload     (docs at /docs)
"""

from __future__ import annotations

import csv
import hashlib
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone

import yaml
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Path, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import dayplan, db, notify, reasons, share
from .categories import category_observation, cohort, load_categories
from .aspiration import NONE, load_aspiration
from .config import Settings, get_settings
from .features import Conditions, conjoint_plan_features
from .moments import Moment, Point, load_moments
from .personal import DeltaPosterior, prior_only
from .popularity import load_popularity
from .population import PopulationModel, load_population
from .schemas import (AnswersIn, CategoriesIn, ChoicesIn, CuratedPlanIn, EventIn, InstallIn, InstallOut, PlanFeedbackIn,
                      PlanRequest, ProfileIn, RatingIn, SafetyIn, SafetyReplyIn, SwipesIn)
from .scoring import conjoint_observation, named_weights, rating_observation, swipe_observation, update_person
from .sun import sunset
from .travel import LondonEstimate

# D107 (GUESS): the most a person spends on a day out, from the "about you" budget band; null means no limit
BUDGET_BAND_GBP = {"under_20": 20.0, "20_40": 40.0, "40_70": 70.0, "70_plus": None}
EXAMPLE_SHOT_CARD = "m_waterloo_bridge_sunset"   # the Test A example (D106), shown on the photos screen
# D112: the example day shown before consent. Not personal (population weights only), and a Sunday, so it overlaps
# little with the Test B pair (a Saturday afternoon). m151: it leaves out the generic plan's places (National Gallery,
# Borough Market, the Royal Festival Hall as its rain swap) and every moment in 15% or more of simulated Test B
# personal plans (m153: 200 people, the short onboarding, the loved-place and end-time rules), so nobody meets a
# Test B stop here first and can tell which plan is which
EXAMPLE_DAY = dict(start_name="Charing Cross station", start=(51.507819, -0.126137), start_time="10:30",
                   end_time="14:30", stops=3, weekday="sun", day_label="An example Sunday",
                   exclude=("m_national_gallery", "m_borough_market_graze", "m_rfh_foyers_rest",
                            "m_bm_great_court", "m_garden_at_120", "m_to_river_somerset", "m_waterloo_bridge_sunset",
                            "m_st_dunstan_garden", "m_national_portrait_gallery", "m_greenwich_wolfe_view",
                            "m_millennium_bridge_dome", "m_alderman_stairs_sunset", "m_park_break_embankment",
                            "m_beigel_bake_late",
                            # D116: the shopping moments, so the first thing people see isn't two shops
                            "m_burlington_arcade", "m_liberty_timber_galleries", "m_leadenhall_market",
                            "a_old_spitalfields_market", "a_portobello_saturday"))


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
        # the 16 locked swipe places (D107): their tags for the δ update, and the cards at each place for planning
        app.state.swipe_items = dayplan.load_swipe_items(settings.data_dir / "swipe_items.yaml")
        app.state.swipe_cards = dayplan.load_swipe_cards(settings.data_dir / "swipe_items.yaml")
        app.state.app_items = dayplan.load_app_items(settings.data_dir / "swipe_items.yaml")   # before the plan (D112)
        app.state.app_items_later = dayplan.load_app_items(settings.data_dir / "swipe_items.yaml", later=True)
        app.state.example_day = None   # built on first request, then kept (D112)
        app.state.popularity = load_popularity(settings.data_dir / "popularity.yaml")   # the nudge's table (D113)
        app.state.categories = load_categories(settings.data_dir / "categories.yaml")   # visitors' cards (D116)
        asp = settings.data_dir / "aspiration.yaml"
        app.state.amap = load_aspiration(asp) if asp.exists() else None
        app.state.travel = LondonEstimate()
        with app.state.Session() as s:   # D116: sync the card files on every start, so a deploy brings new cards
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

    def person_fields(user: db.User) -> frozenset[str]:
        """The inspiring fields the person picked (D77), as aspiration.yaml codes."""
        return frozenset(f for f in (user.profile or {}).get("fields", []) if f != NONE)

    def refit(s: Session, user: db.User, p: PopulationModel) -> DeltaPosterior:
        """Rebuild δ_person from everything this person has told us (swipes, choices, ratings)."""
        ms = moments_by_id(s)
        amap, fields = app.state.amap, person_fields(user)
        obs = []
        for sw in user.swipes:
            m = app.state.swipe_items.get(sw.item)
            asp = amap.match(m, fields) if (amap and m is not None) else 0.0
            if m is not None and (o := swipe_observation(p, m, sw.reaction, asp)):
                obs.append(o)
        for ch in user.choices:
            t = app.state.tasks.get(ch.task)
            if t and ch.choice in ("A", "B"):   # "N", no preference (D110), carries no A/B information
                obs.append(conjoint_observation(p, conjoint_plan_features(t["A"]),
                                                conjoint_plan_features(t["B"]), chose_a=ch.choice == "A"))
        cats = app.state.categories
        for a in user.categories:                              # D116: visitors' category cards, like place swipes
            if cats and a.key in cats.items and (o := category_observation(p, cats.items[a.key], a.reaction, a.want)):
                obs.append(o)
        for f in (user.profile or {}).get("why_travel", []):   # D115: feelings on screen 5, as stated choices
            if (o := reasons.feeling_observation(p, f)):
                obs.append(o)
        for r in user.ratings:
            if r.moment_id in ms:
                m = ms[r.moment_id]
                obs.append(rating_observation(p, m, r.rating, Conditions(r.temp_c, r.rain_prob), r.travel_min,
                                              amap.match(m, fields) if amap else 0.0))
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

    @app.get("/privacy", response_class=HTMLResponse)
    def privacy():
        """The app's privacy notice (D109), linked from the app and from TestFlight."""
        return HTMLResponse((settings.data_dir / "privacy_app.html").read_text(encoding="utf-8"))

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
        amap = app.state.amap
        fields = None if amap is None else {
            "question": amap.question, "note": amap.note,
            "options": [{"key": f.code, "label": f.label} for f in amap.fields.values()]}
        example = ms.get(EXAMPLE_SHOT_CARD)
        conj = app.state.onboarding.get("conjoint") or {}
        upfront = conj.get("upfront") or [t["task"] for t in tasks]
        later = conj.get("later") or []
        by_task = {t["task"]: t for t in tasks}
        place = lambda n: {"item": n, "name": app.state.swipe_cards[n][0]}
        cats = app.state.categories
        kinds = [] if cats is None else [
            {"key": c.key, "title": c.title, "line": c.line, "example_id": c.example,
             "example_title": ms[c.example].display_title() if c.example in ms else None}
            for c in cats.items.values()]
        return {**app.state.onboarding,
                # D116: visitors from abroad get kinds of place instead of the London places
                "category_cards": kinds,
                "categories": None if cats is None else {"prompt": cats.prompt, "note": cats.note,
                                                          "want_prompt": cats.want_prompt},
                # D112: asked before the first plan, and the rest in "Improve future plans"
                "swipe_places": [place(n) for n in app.state.app_items],
                "swipe_places_later": [place(n) for n in app.state.app_items_later],
                "conjoint_tasks": [by_task[k] for k in upfront if k in by_task],
                "conjoint_tasks_later": [by_task[k] for k in later if k in by_task],
                "fields": fields,
                "example_shot_card": card(example) if example and example.shot_card else None}

    @app.post("/v1/me/swipes", status_code=204)
    def post_swipes(body: SwipesIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                    p: PopulationModel = Depends(pop)):
        for it in body.items:
            if it.item not in app.state.swipe_items:
                raise HTTPException(422, f"unknown swipe place {it.item}")
            s.add(db.Swipe(user_id=user.id, item=it.item, reaction=it.reaction))
        s.flush()
        s.refresh(user)
        refit(s, user, p)
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/categories", status_code=204)
    def post_categories(body: CategoriesIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                        p: PopulationModel = Depends(pop)):
        """D116: a visitor's answers to the category cards."""
        cats = app.state.categories
        for it in body.items:
            if cats is None or it.key not in cats.items:
                raise HTTPException(422, f"unknown category {it.key}")
            s.add(db.CategoryAnswer(user_id=user.id, key=it.key, reaction=it.reaction,
                                    want=it.want if it.reaction == "never_tried" else None))
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
    def put_profile(body: ProfileIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                    p: PopulationModel = Depends(pop)):
        amap = app.state.amap
        if amap is not None and (bad := [f for f in body.fields if f not in amap.fields]):
            raise HTTPException(422, f"unknown fields {bad}")
        user.profile = body.model_dump(exclude_none=True)
        refit(s, user, p)   # the inspiring fields change the swipes' aspiration term (D77)
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
        """The person's plan, from the same engine as the Test B plans (brain.dayplan, D107)."""
        day = date.fromisoformat(body.date) if body.date else None
        budget = body.budget_gbp if body.budget_gbp is not None else \
            BUDGET_BAND_GBP.get((user.profile or {}).get("budget_band"))
        c = body.conditions
        brief = dayplan.Brief(
            start_name=body.start_name, start=body.start, start_time=body.start_time, end_time=body.end_time,
            stops=body.stops, budget_gbp=budget,
            day_label=f"{day:%A} {day.day} {day:%B}" if day else "A day out in London",
            weekday=day.strftime("%a").lower() if day else None,
            temp_c=c.temp_c if c else None, rain_prob=c.rain_prob if c else None,
            time_limit_s=settings.planner_time_limit_s, sunset=sunset(day) if day else None)
        ready = [m for m in moments_by_id(s).values() if m.status == "ready"]   # checked cards only (D72)
        by_id = {m.id: m for m in ready}
        cards_at = app.state.swipe_cards
        loved = [cards_at[sw.item] for sw in user.swipes if sw.reaction == "loved" and sw.item in cards_at]
        disliked = [cards_at[sw.item] for sw in user.swipes if sw.reaction == "didnt_enjoy" and sw.item in cards_at]
        must_do = body.intent.get("must_do") if body.intent.get("must_do") in by_id else None
        post = posterior(user, p)

        def run(keep: set[str], exclude: set[str]):
            return dayplan.personal_plan(
                p, post, ready, brief, app.state.travel, must_do=must_do, amap=app.state.amap,
                fields=person_fields(user), loved=loved, disliked=disliked, familiar=body.familiar,
                keep=keep, exclude=exclude,
                popularity=app.state.popularity.shares if app.state.popularity else None)

        failed = lambda pl: pl.status != "ok" or not pl.stops
        plan, stops, _, notes = run(set(body.keep), set(body.exclude))
        if body.keep and failed(plan):      # a swap that can't keep the rest: replan the day without the old stop
            plan, stops, _, notes = run(set(), set(body.exclude))
        if body.exclude and failed(plan):   # "Regenerate plan" with nothing new left (D112): the best day again
            plan, stops, _, notes = run(set(), set())
        out = [dayplan.app_stop(st, dayplan.stop_point(pst.moment_id, by_id, brief))
               for pst, st in zip(plan.stops, stops)]
        # D115: "why we picked this for you", from the person's own answers; never in the blind comparison
        ms = moments_by_id(s)
        feelings = [f for f in (user.profile or {}).get("why_travel", []) if f in reasons.FEELINGS]
        loved_places = [(*cards_at[sw.item], app.state.swipe_items[sw.item]) for sw in user.swipes
                        if sw.reaction == "loved" and sw.item in cards_at and sw.item in app.state.swipe_items]
        rated = [(ms[r.moment_id], r.rating) for r in user.ratings if r.moment_id in ms]
        cats = app.state.categories.items if app.state.categories else {}
        loved_kinds = [(cats[a.key].phrase, cats[a.key].moment) for a in user.categories
                       if a.reaction == "loved" and a.key in cats]
        wanted = [(cats[a.key].phrase, cats[a.key].moment) for a in user.categories
                  if a.reaction == "never_tried" and a.want == "yes" and a.key in cats]
        n_choices = sum(ch.choice in ("A", "B") for ch in user.choices)
        amap, fields = app.state.amap, person_fields(user)
        for st in out:
            base = st["moment_id"].split("#")[0]
            if st["rateable"] and base in by_id:
                st["card"] = card(by_id[base])
                m = by_id[base]
                st["reasons"] = [] if body.blind else reasons.stop_reasons(
                    p, post.mean, m, loved=loved_places, feelings=feelings, rated=rated,
                    loved_kinds=loved_kinds, wanted=wanted,
                    interests=amap.labels(amap.fields_of(m) & fields) if amap else [], n_choices=n_choices)
            if body.blind:
                st["chosen_for"], st["why"], st["worth_gbp"] = [], [], None
        intent = {**body.intent, **({"swapped_out": body.exclude} if body.exclude else {})}
        row = db.Plan(user_id=user.id, kind="personal", date=body.date, intent=intent, stops=out, value=plan.value)
        s.add(row)
        s.commit()
        return {**plan_out(row), "title": brief.day_label, "summary": dayplan.summary_lines(brief, stops),
                "totals": dayplan.plan_totals(stops, app.state.travel), "pace": notes.pace,
                "solver_status": plan.status, "blind": body.blind,
                "feel_line": None if body.blind else reasons.feel_line(stops, by_id),
                "basis": None if body.blind else reasons.basis(
                    sum(sw.reaction in ("loved", "fine", "didnt_enjoy", "havent_been") for sw in user.swipes),
                    n_choices, len(rated), len(feelings),
                    sum(a.reaction != "skip" for a in user.categories))}

    @app.get("/v1/example-day")
    def example_day(s: Session = Depends(session), p: PopulationModel = Depends(pop)):
        """A non-personal example day, shown before consent (D112). No install token: nothing about the person is
        used or stored. Built once from the population weights, then kept; the app ships a copy of it."""
        if app.state.example_day is None:
            e = EXAMPLE_DAY
            brief = dayplan.Brief(start_name=e["start_name"], start=Point(lat=e["start"][0], lon=e["start"][1]),
                                  start_time=e["start_time"], end_time=e["end_time"], stops=e["stops"],
                                  budget_gbp=None, day_label=e["day_label"], weekday=e["weekday"],
                                  temp_c=None, rain_prob=None, time_limit_s=settings.planner_time_limit_s)
            ready = [m for m in moments_by_id(s).values() if m.status == "ready"]
            by_id = {m.id: m for m in ready}
            plan, stops, _, _ = dayplan.personal_plan(p, prior_only(p.delta_prior_sd), ready, brief, app.state.travel,
                                                      familiar=False, exclude=frozenset(e["exclude"]))
            out = [dayplan.app_stop(st, dayplan.stop_point(pst.moment_id, by_id, brief))
                   for pst, st in zip(plan.stops, stops)]
            for st in out:
                st["chosen_for"], st["why"], st["worth_gbp"] = [], [], None   # nothing personal to explain
                if st["rateable"] and st["moment_id"] in by_id:
                    st["card"] = card(by_id[st["moment_id"]])
            app.state.example_day = {"id": 0, "title": brief.day_label, "date": None, "stops": out,
                                     "feel_line": reasons.feel_line(stops, by_id),   # D115: from the cards, not a person
                                     "summary": dayplan.summary_lines(brief, stops),
                                     "totals": dayplan.plan_totals(stops, app.state.travel)}
        return app.state.example_day

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
        moment_id = body.moment_id.split("#")[0]   # "m_x#lunch" (a food card as the lunch stop) is card m_x
        if s.get(db.MomentRow, moment_id) is None:
            raise HTTPException(404, "no such moment")
        if body.plan_id is not None:
            pl = s.get(db.Plan, body.plan_id)
            if pl is None or pl.user_id != user.id:
                raise HTTPException(404, "no such plan")
        c = body.conditions
        s.add(db.Rating(user_id=user.id, plan_id=body.plan_id, moment_id=moment_id, rating=body.rating,
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

    # ---- sharing a rated moment (D114) -----------------------------------------------------
    @app.get("/v1/me/referral")
    def my_referral(user: db.User = Depends(current_user), s: Session = Depends(session)):
        """The person's share code (made on first use); the app builds the link as <base>/r/<code>?m=<moment>."""
        return {"code": share.code_for(s, user), "text": share.SHARE_TEXT}

    @app.get("/r/{code}", response_class=HTMLResponse)
    def share_page(code: str = Path(pattern=share.CODE_PATTERN), m: str | None = Query(default=None, max_length=64),
                   s: Session = Depends(session)):
        """The page a share link opens. Opening it here counts nothing (link previews fetch it too); its script does."""
        known = s.scalar(select(db.Referral).where(db.Referral.code == code)) is not None
        row = s.get(db.MomentRow, m) if m else None
        moment = Moment.model_validate(row.record) if row else None
        ok = moment is not None and moment.status == "ready"
        return HTMLResponse(share.page(code, known, moment.display_title() if ok else None, m if ok else None,
                                       settings.testflight_url))

    @app.post("/r/{code}/open", status_code=204)
    def share_opened(code: str = Path(pattern=share.CODE_PATTERN), body: dict | None = Body(default=None),
                     s: Session = Depends(session)):
        m = (body or {}).get("m")
        m = m if isinstance(m, str) and s.get(db.MomentRow, m) is not None else None
        share.record_open(s, code, m)
        return Response(status_code=204)

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

    @app.get("/v1/admin/referrals", dependencies=[Depends(admin)])
    def referrals(s: Session = Depends(session)):
        """D114: the share funnel for Test C's K: shared → opened → installed → onboarded → first plan."""
        return share.funnel(s)

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
            ("safety_alerts", db.SafetyAlert), ("referrals", db.Referral), ("link_opens", db.LinkOpen),
            ("category_answers", db.CategoryAnswer)]} | {
            # D116: visitors from abroad are their own group, left out of the Test B analysis
            "cohorts": {u.id: cohort(u.profile) for u in s.scalars(select(db.User))}}

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
