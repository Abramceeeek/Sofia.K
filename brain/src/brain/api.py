"""The brain's HTTP API, used by the SwiftUI app (the face) and by Abram's admin tools.

Run locally:  uvicorn brain.api:app --app-dir src --reload     (docs at /docs)
"""

from __future__ import annotations

import csv
import hashlib
import re
import secrets
import uuid
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import yaml
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Path, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import dayplan, db, notify, reasons, share, summary, testb, trips, tripdays
from .categories import category_observation, cohort, load_categories
from .aspiration import NONE, load_aspiration
from .config import DATA_DIR, Settings, get_settings
from .features import Conditions
from .moments import Moment, Point, load_moments
from .personal import DeltaPosterior, prior_only
from .popularity import load_popularity
from .population import PopulationModel, load_population
from .schemas import (AnswersIn, CategoriesIn, ChoicesIn, CorrectionsIn, CuratedPlanIn, EventIn, FlightSearchIn, InstallIn,
                      InstallOut, PairFeedbackIn, PairIn, PlanFeedbackIn, PlanRequest, ProfileIn, RatingIn, SafetyIn,
                      SafetyReplyIn, StaySearchIn, SurveyIn, SwipesIn, TripDaysIn)
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


def _tester_code(text: str | None) -> str | None:
    """Build 2: "ucl hiking " → "UCL-HIKING". Letters, digits and hyphens only."""
    code = re.sub(r"[^A-Z0-9-]", "", re.sub(r"\s+", "-", (text or "").strip().upper()))
    return code[:40] or None


MAX_TRIP_DAYS = 7   # D120: days planned in one request (about a second each on the free server)


def mins_between(a: str, b: str) -> int:
    """D122: the length of the person's day in minutes ("10:00", "18:00" → 480), for the trip_days event."""
    return tripdays.mins(b) - tripdays.mins(a)


def _next_saturday(today: date) -> date:
    """The Test B pair is for "a Saturday" (D105): the coming one, or today if it is Saturday. It sets the sunset."""
    return today + timedelta(days=(5 - today.weekday()) % 7)


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
        app.state.swipe_phrases = dayplan.load_swipe_phrases(settings.data_dir / "swipe_items.yaml")   # D117
        app.state.app_items = dayplan.load_app_items(settings.data_dir / "swipe_items.yaml")   # before the plan (D112)
        app.state.app_items_later = dayplan.load_app_items(settings.data_dir / "swipe_items.yaml", later=True)
        app.state.example_day = None   # built on first request, then kept (D112)
        app.state.popularity = load_popularity(settings.data_dir / "popularity.yaml")   # the nudge's table (D113)
        app.state.categories = load_categories(settings.data_dir / "categories.yaml")   # visitors' cards (D116)
        asp = settings.data_dir / "aspiration.yaml"
        app.state.amap = load_aspiration(asp) if asp.exists() else None
        app.state.travel = LondonEstimate()
        codes = settings.data_dir / "tester_codes.yaml"
        with open(codes if codes.exists() else DATA_DIR / "tester_codes.yaml", encoding="utf-8") as f:
            app.state.tester_codes = (yaml.safe_load(f) or {}).get("codes") or {}   # Build 2
        places = settings.data_dir / "airports.yaml"
        airports, dests = trips.load_places(places if places.exists() else DATA_DIR / "airports.yaml")
        app.state.trips = trips.TripSearch(airports, dests, duffel_token=settings.duffel_token,   # D120
                                           liteapi_key=settings.liteapi_key)
        arr = settings.data_dir / "arrivals.yaml"
        app.state.arrivals = tripdays.load_arrivals(arr if arr.exists() else DATA_DIR / "arrivals.yaml")   # D122
        with app.state.Session() as s:   # D116: sync the card files on every start, so a deploy brings new cards
            _reload_moments(s, settings)
            _purge_contacts(s)           # D118: safety contacts never outlive CONTACT_DAYS
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

    def corrected(user: db.User) -> set[str]:
        """D117: the "So far" items the person marked "not right"; those answers stop counting."""
        return {c.item for c in user.corrections}

    def refit(s: Session, user: db.User, p: PopulationModel) -> DeltaPosterior:
        """Rebuild δ_person from everything this person has told us (swipes, choices, ratings)."""
        post = update_person(p, observations(s, user, p))
        user.delta, user.population_version = post.to_json(), p.version
        return post

    def observations(s: Session, user: db.User, p: PopulationModel) -> list:
        ms = moments_by_id(s)
        amap, fields = app.state.amap, person_fields(user)
        fixed = corrected(user)
        obs = []
        for sw in user.swipes:
            if f"place:{sw.item}" in fixed:
                continue
            m = app.state.swipe_items.get(sw.item)
            asp = amap.match(m, fields) if (amap and m is not None) else 0.0
            if m is not None and (o := swipe_observation(p, m, sw.reaction, asp)):
                obs.append(o)
        for ch in user.choices:
            t = app.state.tasks.get(ch.task)
            if t and ch.choice in ("A", "B"):   # "N", no preference (D110), carries no A/B information
                obs.append(conjoint_observation(p, summary.choice_features(t["A"], fixed),
                                                summary.choice_features(t["B"], fixed), chose_a=ch.choice == "A"))
        cats = app.state.categories
        for a in user.categories:                              # D116: visitors' category cards, like place swipes
            if f"kind:{a.key}" in fixed:
                continue
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
        return obs

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
        channel, src = body.channel, body.src
        code = _tester_code(body.code)
        if code:   # Build 2: a known code sets the channel; any code becomes the source unless a share link set it
            channel = app.state.tester_codes.get(code, {}).get("channel", channel)
            if not (src or "").startswith("ref:"):   # the share funnel matches "ref:<code>" exactly (D114)
                src = f"code:{code}"
        user = db.User(id=str(uuid.uuid4()), token_hash=_hash(token), channel=channel, src=src,
                       consent_version=body.consent.version, consent_ai=body.consent.ai_processing, profile={})
        s.add(user)
        if code:
            s.add(db.Event(user_id=user.id, name="tester_code", props={"code": code}))
        s.commit()
        return InstallOut(user_id=user.id, token=token)

    @app.get("/v1/onboarding")
    def onboarding(user: db.User = Depends(current_user), s: Session = Depends(session)):
        ms = moments_by_id(s)
        tasks = [{"task": k, "A": v["A"]["description"], "B": v["B"]["description"],
                  "levels": summary.task_levels(v)}   # D117: for "So far you've picked … every time"
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
        place = lambda n: {"item": n, "name": app.state.swipe_cards[n][0],
                           "reactions": summary.place_reactions(app.state.swipe_phrases.get(n)),   # D117
                           # D119: the cards at the same place; the app shows the first one's photo it has
                           "photo_ids": app.state.swipe_cards[n][1]}
        cats = app.state.categories
        kinds = [] if cats is None else [
            {"key": c.key, "title": c.title, "line": c.line, "example_id": c.example,
             "example_title": ms[c.example].display_title() if c.example in ms else None,
             "reactions": {**summary.place_reactions(c.phrase),                                  # D117
                           "want_yes": f"Noted: you'd like to try {c.phrase}."}}
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
                "conjoint_words": summary.tendency_words(),   # D117
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
        new = body.model_dump(exclude_none=True)
        for key in ("based", "home_city"):   # D116: a later save without them keeps them (the Test B cohort)
            if key not in new and key in (user.profile or {}):
                new[key] = user.profile[key]
        user.profile = new
        refit(s, user, p)   # the inspiring fields change the swipes' aspiration term (D77)
        s.commit()
        return Response(status_code=204)

    def learned(user: db.User) -> list[dict]:
        """D117: "So far, I've learned…", from the person's own answers only (brain.summary)."""
        latest = {}
        for sw in sorted(user.swipes, key=lambda r: r.id):
            latest[sw.item] = sw.reaction
        kinds = {}
        for a in sorted(user.categories, key=lambda r: r.id):
            kinds[a.key] = (a.key, a.reaction, a.want)
        choices = {}
        for ch in sorted(user.choices, key=lambda r: r.id):
            choices[ch.task] = ch.choice
        cats = app.state.categories.items if app.state.categories else {}
        return summary.items(
            feelings=[f for f in (user.profile or {}).get("why_travel", []) if f in reasons.FEELINGS],
            swipes=list(latest.items()),
            places={n: (name, app.state.swipe_phrases.get(n)) for n, (name, _) in app.state.swipe_cards.items()},
            kinds=list(kinds.values()), phrases={k: c.phrase for k, c in cats.items()},
            choices=choices, tasks=app.state.tasks, corrected=corrected(user))

    @app.get("/v1/me/summary")
    def get_summary(user: db.User = Depends(current_user)):
        """D117: shown before the first plan, with "Looks right" and "Change something". No scores."""
        text = app.state.onboarding.get("summary") or {}
        return {**text, "items": learned(user)}

    @app.post("/v1/me/corrections", status_code=204)
    def post_corrections(body: CorrectionsIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                         p: PopulationModel = Depends(pop)):
        """D117: items marked "not right". Each is stored with the words the person saw, and its answer stops counting:
        a feeling leaves the profile; a place, a kind or a this-or-that attribute is left out of the fit."""
        shown = {it["id"]: it["text"] for it in learned(user)}
        unknown = [i for i in body.items if i not in shown]
        if unknown:
            raise HTTPException(422, f"not on the list: {unknown}")
        for item in dict.fromkeys(body.items):
            s.add(db.Correction(user_id=user.id, item=item, text=shown[item]))
            if item.startswith("feeling:"):
                prof = dict(user.profile or {})
                prof["why_travel"] = [f for f in prof.get("why_travel", []) if f != item.split(":", 1)[1]]
                user.profile = prof
        s.flush()
        s.refresh(user)
        refit(s, user, p)
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

    def personal_day(s: Session, user: db.User, p: PopulationModel, brief: dayplan.Brief, ready: list[Moment], *,
                     must_do: str | None = None, familiar: bool = True, keep: list[str] = (), exclude: list[str] = (),
                     blind: bool = False, end_window: tuple[int, int] | None = None,
                     post: DeltaPosterior | None = None, feelings: list[str] | None = None,
                     fallback: bool = True) -> tuple[dayplan.DayPlan, list[dict], dict]:
        """The person's plan as the app shows it: (the solver's plan, the app's stops, the plan's header fields).
        Used by "plan a day" and by the Test B pair (Build 2)."""
        by_id = {m.id: m for m in ready}
        cards_at = app.state.swipe_cards
        fixed = corrected(user)   # D117: answers marked "not right" on "So far" don't count
        swipes = [sw for sw in user.swipes if f"place:{sw.item}" not in fixed]
        kinds = [a for a in user.categories if f"kind:{a.key}" not in fixed]
        loved = [cards_at[sw.item] for sw in swipes if sw.reaction == "loved" and sw.item in cards_at]
        disliked = [cards_at[sw.item] for sw in swipes if sw.reaction == "didnt_enjoy" and sw.item in cards_at]
        post = post or posterior(user, p)

        def run(keep: set[str], exclude: set[str]):
            return dayplan.personal_plan(
                p, post, ready, brief, app.state.travel, must_do=must_do, amap=app.state.amap,
                fields=person_fields(user), end_window=end_window, loved=loved, disliked=disliked, familiar=familiar,
                keep=keep, exclude=exclude,
                popularity=app.state.popularity.shares if app.state.popularity else None)

        failed = lambda pl: pl.status != "ok" or not pl.stops
        plan, stops, _, notes = run(set(keep), set(exclude))
        if keep and failed(plan):      # a swap that can't keep the rest: replan the day without the old stop
            plan, stops, _, notes = run(set(), set(exclude))
        if exclude and fallback and failed(plan):   # "Regenerate" with nothing new left (D112): the best day again
            plan, stops, _, notes = run(set(), set())
        out = [dayplan.app_stop(st, dayplan.stop_point(pst.moment_id, by_id, brief))
               for pst, st in zip(plan.stops, stops)]
        # D115: "why we picked this for you", from the person's own answers; never in the blind comparison
        ms = moments_by_id(s)
        if feelings is None:
            feelings = [f for f in (user.profile or {}).get("why_travel", []) if f in reasons.FEELINGS]
        loved_places = [(*cards_at[sw.item], app.state.swipe_items[sw.item]) for sw in swipes
                        if sw.reaction == "loved" and sw.item in cards_at and sw.item in app.state.swipe_items]
        rated = [(ms[r.moment_id], r.rating) for r in user.ratings if r.moment_id in ms]
        cats = app.state.categories.items if app.state.categories else {}
        loved_kinds = [(cats[a.key].phrase, cats[a.key].moment) for a in kinds
                       if a.reaction == "loved" and a.key in cats]
        wanted = [(cats[a.key].phrase, cats[a.key].moment) for a in kinds
                  if a.reaction == "never_tried" and a.want == "yes" and a.key in cats]
        n_choices = sum(ch.choice in ("A", "B") for ch in user.choices)
        amap, fields = app.state.amap, person_fields(user)
        for st in out:
            base = st["moment_id"].split("#")[0]
            if st["rateable"] and base in by_id:
                st["card"] = card(by_id[base])
                m = by_id[base]
                st["reasons"] = [] if blind else reasons.stop_reasons(
                    p, post.mean, m, loved=loved_places, feelings=feelings, rated=rated,
                    loved_kinds=loved_kinds, wanted=wanted,
                    interests=amap.labels(amap.fields_of(m) & fields) if amap else [], n_choices=n_choices)
            if blind:
                st["chosen_for"], st["why"], st["worth_gbp"] = [], [], None
        head = {"title": brief.day_label, "summary": dayplan.summary_lines(brief, stops),
                "totals": dayplan.plan_totals(stops, app.state.travel), "pace": notes.pace,
                "solver_status": plan.status, "blind": blind,
                "feel_line": None if blind else reasons.feel_line(stops, by_id, feelings),   # D118: their words
                "basis": None if blind else reasons.basis(
                    sum(sw.reaction in ("loved", "fine", "didnt_enjoy", "havent_been") for sw in user.swipes),
                    n_choices, len(rated), len(feelings),
                    sum(a.reaction != "skip" for a in user.categories))}
        return plan, out, head

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
        must_do = body.intent.get("must_do") if body.intent.get("must_do") in {m.id for m in ready} else None
        plan, out, head = personal_day(s, user, p, brief, ready, must_do=must_do, familiar=body.familiar,
                                       keep=body.keep, exclude=body.exclude, blind=body.blind)
        intent = {**body.intent, **({"swapped_out": body.exclude} if body.exclude else {})}
        row = db.Plan(user_id=user.id, kind="personal", date=body.date, intent=intent, stops=out, value=plan.value)
        s.add(row)
        s.commit()
        return {**plan_out(row), **head}

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

    def in_pair(pl: db.Plan) -> bool:
        return bool((pl.intent or {}).get("testb_pair"))

    def hidden(pl: db.Plan) -> bool:
        """Build 2: the pair's plans stay out of the plan list until the person has chosen, so it stays blind."""
        return in_pair(pl) and pl.status == "offered"

    @app.get("/v1/me/plans")
    def my_plans(user: db.User = Depends(current_user)):
        return [plan_out(pl) for pl in sorted(user.plans, key=lambda x: x.id, reverse=True) if not hidden(pl)]

    @app.get("/v1/me/plans/{plan_id}")
    def my_plan(plan_id: int, user: db.User = Depends(current_user), s: Session = Depends(session)):
        pl = s.get(db.Plan, plan_id)
        if pl is None or pl.user_id != user.id or hidden(pl):
            raise HTTPException(404, "no such plan")
        return plan_out(pl)

    @app.post("/v1/me/plans/{plan_id}/feedback", status_code=204)
    def plan_feedback(plan_id: int, body: PlanFeedbackIn, user: db.User = Depends(current_user),
                      s: Session = Depends(session)):
        pl = s.get(db.Plan, plan_id)
        if pl is None or pl.user_id != user.id:
            raise HTTPException(404, "no such plan")
        if in_pair(pl):
            raise HTTPException(409, "the Test B pair takes its answers together: /v1/me/testb/pair/feedback")
        pl.status = "chosen" if body.chosen else "not_chosen"
        pl.fit_rating, pl.reason = body.fit_rating, body.reason
        s.commit()
        return Response(status_code=204)

    # ---- Build 2: the in-app Test B pair (screens 18-19) and the survey (screen 16) -------------------------------

    def pair_rows(user: db.User) -> list[db.Plan]:
        return sorted((pl for pl in user.plans if in_pair(pl)), key=lambda pl: pl.label or "")

    def full_plan(pl: db.Plan) -> dict:
        intent = pl.intent or {}
        return {**plan_out(pl), "intent": {k: v for k, v in intent.items() if k != "view"}, **intent.get("view", {})}

    def pair_view(rows: list[db.Plan]) -> dict:
        """Both plans in the same text format, labelled Plan 1 and Plan 2. Once they've chosen: which was personal,
        and the chosen plan in full (with the reasons, if it was the personal one)."""
        text = app.state.onboarding.get("testb") or {}
        done = rows[0].status != "offered"
        out = {"title": rows[0].intent["view"]["title"], "intro": text.get("intro"), "done": done,
               "plans": [{"id": pl.id, "label": pl.label, "title": f"Plan {pl.label}", "date": None, "blind": True,
                          "summary": pl.intent["view"]["summary"], "totals": pl.intent["view"]["totals"],
                          "feel_line": None, "basis": None, "fit_rating": pl.fit_rating if done else None,
                          "stops": [dayplan.blind_stop(st, pl.label, i) for i, st in enumerate(pl.stops)]}
                         for pl in rows]}
        if done:
            personal = next(pl for pl in rows if pl.kind == "personal")
            chosen = next(pl for pl in rows if pl.status == "chosen")
            other = next(pl for pl in rows if pl is not personal)
            out.update(personal_label=personal.label, chosen_label=chosen.label, chosen=full_plan(chosen),
                       reveal=[text.get("reveal_personal", "").format(personal=personal.label, other=other.label),
                               text.get("reveal_kept", "").format(chosen=chosen.label)])
        return out

    @app.get("/v1/me/testb/pair")
    def get_pair(user: db.User = Depends(current_user)):
        rows = pair_rows(user)
        if not rows:
            raise HTTPException(404, "no pair yet")
        return pair_view(rows)

    @app.post("/v1/me/testb/pair", status_code=201)
    def make_pair(body: PairIn | None = Body(default=None), user: db.User = Depends(current_user),
                  s: Session = Depends(session), p: PopulationModel = Depends(pop)):
        """The blind Test B pair (validation/test-plan.md): the person's plan and the generic plan on the same brief
        (data/testb/, a copy of validation/testb-real/), in a random order stored here (m118). Made once per person;
        asking again returns the same pair. The personal plan uses what they've told us so far, which in the app is
        the short onboarding (m140); the familiar favourite is off, and it ends within 30 min of the generic plan
        (D97). Visitors from abroad don't get it (D116)."""
        if cohort(user.profile) == "visitor":
            raise HTTPException(409, "the Test B pair is for people based in the UK")
        rows = pair_rows(user)
        if rows:
            return pair_view(rows)
        folder = settings.data_dir / "testb"
        folder = folder if (folder / "brief.yaml").exists() else DATA_DIR / "testb"
        day = _next_saturday(datetime.now(ZoneInfo("Europe/London")).date())
        brief = dayplan.load_brief(folder / "brief.yaml")
        brief = replace(brief, sunset=sunset(day) or brief.sunset, time_limit_s=settings.planner_time_limit_s)
        ready = [m for m in moments_by_id(s).values() if m.status == "ready" and m.in_test_b]   # as the CLI (D105)
        gen = testb.generic_stops(folder / "generic.yaml", {m.id: m for m in ready}, dayplan._sunset(brief))
        gen_end = testb.plan_end(gen)
        window = (gen_end - 30, gen_end + 30) if gen_end is not None else None
        plan, mine, head = personal_day(s, user, p, brief, ready, familiar=False, end_window=window)
        generic = [dayplan.generic_app_stop(i, st) for i, st in enumerate(gen)]
        views = {"personal": head,
                 "generic": {"title": brief.day_label, "summary": dayplan.summary_lines(brief, gen),
                             "totals": dayplan.plan_totals(generic, app.state.travel), "blind": False,
                             "feel_line": None, "basis": None}}
        personal_label = secrets.choice("12")
        trip = body.model_dump(exclude_none=True) if body else {}
        for label in "12":   # rows in label order, so the ids don't hint at which is which
            kind = "personal" if label == personal_label else "generic"
            s.add(db.Plan(user_id=user.id, kind=kind, label=label, date=None, stops=mine if kind == "personal" else generic,
                          value=plan.value if kind == "personal" else None,
                          intent={"testb_pair": True, "trip": trip, "sunset": brief.sunset, "view": views[kind]}))
        s.commit()
        s.refresh(user)
        return pair_view(pair_rows(user))

    @app.post("/v1/me/testb/pair/feedback")
    def pair_feedback(body: PairFeedbackIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        rows = pair_rows(user)
        if not rows:
            raise HTTPException(404, "no pair yet")
        if rows[0].status != "offered":
            raise HTTPException(409, "already answered")
        why = (body.why or "").strip() or None
        for pl in rows:
            pl.status = "chosen" if pl.label == body.chosen else "not_chosen"
            pl.fit_rating = body.fit_1 if pl.label == "1" else body.fit_2
            pl.reason = why if pl.label == body.chosen else None
        s.add(db.Event(user_id=user.id, name="testb_pair_feedback",
                       props={"input_mode": body.input_mode, "why_given": why is not None}))
        s.commit()
        return pair_view(rows)

    @app.post("/v1/me/survey", status_code=204)
    def survey(body: SurveyIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        """Screen 16, the Test A survey. Each answer is a row in `answers`, keyed "survey:<question>"."""
        for key, value in body.model_dump(exclude_none=True).items():
            text = str(value).strip()
            if text:
                s.add(db.Answer(user_id=user.id, question=f"survey:{key}", text=text, input_mode="typed"))
        s.commit()
        return Response(status_code=204)

    @app.post("/v1/me/ratings", status_code=201)
    def rate(body: RatingIn, user: db.User = Depends(current_user), s: Session = Depends(session),
             p: PopulationModel = Depends(pop)):
        moment_id = body.moment_id.split("#")[0]   # "m_x#lunch" (a food card as the lunch stop) is card m_x
        generic = moment_id.startswith("generic:")   # Build 2: a stop of the generic Test B plan, if they chose it
        if not generic and s.get(db.MomentRow, moment_id) is None:
            raise HTTPException(404, "no such moment")
        if body.plan_id is not None or generic:
            pl = s.get(db.Plan, body.plan_id) if body.plan_id is not None else None
            if pl is None or pl.user_id != user.id or hidden(pl) or (generic and pl.kind != "generic"):
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
        s.flush()
        contact = (body.contact or "").strip() or None
        if contact:   # D118: only to reply to this message; deleted when resolved
            s.add(db.SafetyContact(alert_id=alert.id, contact=contact))
        s.commit()
        alert.notified = notify.send_alert(settings.alert_webhook_url, alert.id, user.id, body.message, contact)
        s.commit()
        return {"alert_id": alert.id, "message": notify.USER_MESSAGE}

    @app.get("/v1/me/safety")
    def my_safety(user: db.User = Depends(current_user), s: Session = Depends(session)):
        """D118: the person's Help & safety messages and the replies to them, newest first."""
        alerts = s.scalars(select(db.SafetyAlert).where(db.SafetyAlert.user_id == user.id)
                           .order_by(db.SafetyAlert.created_at.desc()))
        return [{"id": a.id, "message": a.message, "created_at": a.created_at.isoformat(),
                 "contact_kept": a.contact is not None,
                 "replies": [{"text": r.text, "created_at": r.created_at.isoformat()} for r in a.replies]}
                for a in alerts]

    # ---- D120: trips: flights and places to stay, filtered here, booked on the provider's own site ------------------

    def _destination(key: str) -> trips.Destination:
        dest = app.state.trips.destinations.get(key)
        if dest is None:
            raise HTTPException(422, "that destination isn't available yet: London first, then UK cities and Europe")
        return dest

    def _trip_event(s: Session, user: db.User, kind: str, source: str, total: int, shown: int, sort: str,
                    used: list[str]) -> None:
        """For the test: what was searched and which filters were used. Never the origin, dates or names."""
        s.add(db.Event(user_id=user.id, name="trip_search",
                       props={"kind": kind, "source": source, "total": total, "shown": shown, "sort": sort,
                              "filters": ",".join(used)}))
        s.commit()

    @app.get("/v1/trips/places")
    def trip_places(q: str = Query(default="", max_length=40), user: db.User = Depends(current_user)):
        """"Flying from": airports and city codes matching what's typed."""
        return [{"code": a.code, "city": a.city, "name": a.name, "country": a.country}
                for a in trips.suggest(app.state.trips.airports, q)]

    @app.get("/v1/trips/destinations")
    def trip_destinations(user: db.User = Depends(current_user)):
        return [{"key": d.key, "name": d.name, "airport": d.airport, "centre": d.centre_name, "day_plans": d.day_plans}
                for d in app.state.trips.destinations.values()]

    @app.post("/v1/trips/flights")
    def trip_flights(body: FlightSearchIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        dest = _destination(body.destination)
        today = datetime.now(timezone.utc).date()
        if body.depart_date < today or body.depart_date > today + timedelta(days=330):
            raise HTTPException(422, "pick a departure date from today to about 11 months ahead")
        if body.return_date is not None and body.return_date < body.depart_date:
            raise HTTPException(422, "the return date is before the departure date")
        origin = body.origin.upper()
        if origin == dest.airport:
            raise HTTPException(422, "that's where the trip goes: pick where you're flying from")
        q = trips.FlightQuery(origin=origin, destination=dest.airport, depart=body.depart_date, ret=body.return_date,
                              adults=body.adults, children=tuple(body.children), cabin=body.cabin)
        f = body.filters
        links = trips.flight_links(q)
        ts = app.state.trips
        try:
            found = ts.flights(q, user.id)
            source = ts.flight_source
        except trips.ProviderError as e:
            if str(e) == "too_many":
                raise HTTPException(429, "That's a lot of searches in an hour. Try again in a few minutes.")
            _trip_event(s, user, "flights", "unavailable", 0, 0, f.sort, [])
            return {"source": "unavailable", "note": "Flights couldn't be searched just now. The links below search "
                    "for real.", "total": 0, "shown": 0, "results": [], "facets": trips.flight_facets([]),
                    "tabs": {}, "links": links, "searched_at": datetime.now(timezone.utc).isoformat()}
        ff = trips.FlightFilters(
            max_stops=f.max_stops, stops=f.stops, out_times=f.out_times, out_depart=f.out_depart,
            in_depart=f.in_depart, max_leg_min=f.max_leg_min, airlines=f.airlines, max_price=f.max_price,
            checked_bag=f.checked_bag, refundable=f.refundable, sort=f.sort)
        shown = trips.filter_flights(found, ff)
        tabs, tags = trips.flight_tops(found, ff)
        used = [k for k, v in f.model_dump(exclude={"sort"}).items() if v not in (None, False, [])]
        _trip_event(s, user, "flights", source, len(found), len(shown), f.sort, used)
        note = {"sample": trips.SAMPLE_NOTE,
                "duffel_test": "Test results from Duffel's made-up airline: not real flights. The links below search "
                               "for real."}.get(source)
        return {"source": source, "note": note, "total": len(found), "shown": len(shown),
                "results": [{**trips.flight_out(x), "tags": tags.get(x.id, [])} for x in shown[:60]],
                "facets": trips.flight_facets(found), "tabs": tabs, "links": links,
                "searched_at": datetime.now(timezone.utc).isoformat()}

    @app.post("/v1/trips/stays")
    def trip_stays(body: StaySearchIn, user: db.User = Depends(current_user), s: Session = Depends(session)):
        dest = _destination(body.destination)
        today = datetime.now(timezone.utc).date()
        nights = (body.checkout - body.checkin).days
        if body.checkin < today or body.checkin > today + timedelta(days=330):
            raise HTTPException(422, "pick a check-in date from today to about 11 months ahead")
        if not 1 <= nights <= 30:
            raise HTTPException(422, "a stay is 1 to 30 nights")
        q = trips.StayQuery(city=dest.name, country_code=dest.country_code, lat=dest.lat, lon=dest.lon,
                            checkin=body.checkin, checkout=body.checkout, adults=body.adults,
                            children=tuple(body.children), rooms=min(body.rooms, body.adults))
        f = body.filters
        links = trips.stay_links(q, max_night=f.max_night)
        ts = app.state.trips
        try:
            found = ts.stays(q, user.id)
            source = ts.stay_source
        except trips.ProviderError as e:
            if str(e) == "too_many":
                raise HTTPException(429, "That's a lot of searches in an hour. Try again in a few minutes.")
            _trip_event(s, user, "stays", "unavailable", 0, 0, f.sort, [])
            return {"source": "unavailable", "note": "Places to stay couldn't be searched just now. The links below "
                    "search for real.", "total": 0, "shown": 0, "results": [], "facets": trips.stay_facets([]),
                    "tabs": {}, "links": links, "centre": dest.centre_name,
                    "searched_at": datetime.now(timezone.utc).isoformat()}
        sf = trips.StayFilters(
            max_night=f.max_night, min_night=f.min_night, min_stars=f.min_stars, min_rating=f.min_rating,
            kinds=f.kinds, refundable=f.refundable, breakfast=f.breakfast, max_km=f.max_km, sort=f.sort)
        shown = trips.filter_stays(found, sf)
        tabs, tags = trips.stay_tops(found, sf)
        used = [k for k, v in f.model_dump(exclude={"sort"}).items() if v not in (None, False, [])]
        _trip_event(s, user, "stays", source, len(found), len(shown), f.sort, used)
        results = []
        for x in shown[:60]:
            d = trips.stay_out(x)
            d["links"] = trips.stay_links(q, stay=x)
            d["tags"] = tags.get(x.id, [])
            results.append(d)
        note = {"sample": trips.SAMPLE_STAY_NOTE, "liteapi_sandbox": trips.SANDBOX_STAY_NOTE}.get(source)
        return {"source": source, "note": note,
                "total": len(found), "shown": len(shown), "results": results, "facets": trips.stay_facets(found),
                "tabs": tabs, "links": links, "centre": dest.centre_name,
                "searched_at": datetime.now(timezone.utc).isoformat()}

    @app.post("/v1/me/trips/days", status_code=201)
    def trip_days(body: TripDaysIn, user: db.User = Depends(current_user), s: Session = Depends(session),
                  p: PopulationModel = Depends(pop)):
        """D120: the days of a trip, each planned like "plan a day", with no moment twice in the trip (D121). Each day
        starts near the chosen stay (else the destination's centre). The trip's feelings shape the plans as stated
        choices, for this trip only (the profile isn't changed). Days come back in order; the first MAX_TRIP_DAYS are
        planned now and the rest with `days`, as the person reaches them.
        D122: each day runs at the person's hours with their places a day (lunch extra); the first day starts where
        they land or arrive (`legs`), with one place on the way if they travel light and land early (`before`); the
        last day ends with the way back to the stay and on to the airport, station or car (tripdays.py)."""
        dest = _destination(body.destination)
        if not dest.day_plans:
            raise HTTPException(422, "day plans aren't ready for that destination yet")
        today = datetime.now(ZoneInfo("Europe/London")).date()
        if body.start_date < today or body.start_date > today + timedelta(days=330):
            raise HTTPException(422, "pick a first day from today to about 11 months ahead")
        total = body.nights + 1
        wanted = sorted(set(body.days)) if body.days else list(range(min(total, MAX_TRIP_DAYS)))
        if any(i >= total for i in wanted) or len(wanted) > MAX_TRIP_DAYS:
            raise HTTPException(422, f"days are 0 to {total - 1}, at most {MAX_TRIP_DAYS} at a time")
        feelings = [f for f in dict.fromkeys(body.feelings) if f in reasons.FEELINGS]
        mine = set((user.profile or {}).get("why_travel", []))
        obs = observations(s, user, p) + [o for f in feelings if f not in mine
                                          if (o := reasons.feeling_observation(p, f))]
        post = update_person(p, obs)
        if tripdays.mins(body.day_end) - tripdays.mins(body.day_start) < 60:
            raise HTTPException(422, "a day needs at least an hour between its start and end")
        start = body.stay or Point(lat=dest.lat, lon=dest.lon)
        start_name = (body.stay_name or "").strip() or dest.centre_name
        # D122: how the trip starts and ends; the older app sends only the flight times
        end_of = lambda e, t: (tripdays.End(e.mode, (e.place or "").upper() or None, e.time) if e
                               else tripdays.End("flight", None, t) if t else None)
        arrive, leave = end_of(body.arrive, body.arrive_time), end_of(body.leave, body.leave_time)
        cfg = app.state.arrivals.get(dest.key)
        est = app.state.travel
        ready = [m for m in moments_by_id(s).values() if m.status == "ready"]
        used = set(body.exclude)
        budget = BUDGET_BAND_GBP.get((user.profile or {}).get("budget_band"))
        out = []

        def fill(part: tripdays.Part, day: date, i: int, label: str, tag: str) -> tuple[dict, list[dict]] | None:
            """Plan one stretch of the day, trying one stop fewer if the planner can't fit them all."""
            for n in dict.fromkeys((part.stops, part.stops - 1)):
                if n < 1:
                    continue
                brief = dayplan.Brief(start_name=part.start_name, start=part.start, start_time=part.start_time,
                                      end_time=part.end_time, stops=n, budget_gbp=budget, day_label=label,
                                      weekday=day.strftime("%a").lower(), time_limit_s=settings.planner_time_limit_s,
                                      sunset=sunset(day), lunch=part.lunch)
                pool = ready if part.toward is None else [   # D122: the place on the way really is on the way
                    m for m in ready if (pt := m.start()) and tripdays.on_the_way(pt, part.start, part.toward)]
                plan, stops, head = personal_day(s, user, p, brief, pool, familiar=False, exclude=sorted(used),
                                                 post=post, feelings=feelings or None, fallback=False)
                if not stops:
                    continue
                used.update(st["moment_id"].split("#")[0] for st in stops if st["rateable"])
                row = db.Plan(user_id=user.id, kind="personal", date=day.isoformat(), stops=stops, value=plan.value,
                              intent={"trip": True, "day": i, "part": tag, "feelings": feelings})
                s.add(row)
                s.flush()
                return {**plan_out(row), **head}, stops
            return None

        for i in wanted:
            day = body.start_date + timedelta(days=i)
            label = f"{day:%A} {day.day} {day:%B}"
            fr = tripdays.frame_day(i, total, cfg, est, stay=start, stay_name=start_name, stay_chosen=body.stay is not None,
                                    day_start=body.day_start, day_end=body.day_end, stops=body.stops_per_day,
                                    arrive=arrive, leave=leave, travel_light=body.travel_light)
            legs = list(fr.legs)
            entry = {"index": i, "date": day.isoformat(), "kind": fr.kind, "plan": None, "before": None,
                     "window": None, "title": fr.title}
            if fr.before and (got := fill(fr.before, day, i, label, "before")):
                entry["before"] = got[0]
                leg = tripdays.to_stay_leg(est, got[1][-1], start, start_name, cfg.check_in_min if cfg else 20)
                legs.append(leg)
                ready_at = tripdays.up5(tripdays.mins(leg.arrive) + (cfg.check_in_min if cfg else 20))
                end = tripdays.mins(fr.main.end_time) if fr.main else tripdays.mins(body.day_end)
                n = tripdays.stops_for(ready_at, end, body.stops_per_day - 1)
                fr.main = tripdays.Part(start, start_name, tripdays.hhmm(ready_at), tripdays.hhmm(end), n) if n else None
            elif fr.before:   # nothing fitted on the way: go to the stay first, as with bags
                fr = tripdays.frame_day(i, total, cfg, est, stay=start, stay_name=start_name,
                                        stay_chosen=body.stay is not None, day_start=body.day_start,
                                        day_end=body.day_end, stops=body.stops_per_day, arrive=arrive, leave=leave,
                                        travel_light=False)
                legs = list(fr.legs)
                entry["title"] = fr.title
            if fr.main:
                entry["window"] = {"start": fr.main.start_time, "end": fr.main.end_time, "stops": fr.main.stops}
                if got := fill(fr.main, day, i, label, "main"):
                    entry["plan"] = got[0]
                    entry["title"] = got[0]["feel_line"] or label
                    if fr.leave_leg:   # the last day: back for the bags, then away
                        legs.append(tripdays.back_leg(est, got[1][-1], start, start_name))
            if not entry["title"]:
                entry["title"] = (entry["before"] or {}).get("feel_line") or "A free day: nothing new fits it yet"
            if fr.leave_leg:
                legs.append(fr.leave_leg)
            entry["legs"] = [leg.out() for leg in legs]
            out.append(entry)
        s.add(db.Event(user_id=user.id, name="trip_days",
                       props={"nights": body.nights, "planned": sum(e["plan"] is not None for e in out),
                              "stay": body.stay is not None, "feelings": ",".join(feelings),
                              # D122: how the person shapes their days (never where or when they travel)
                              "by": arrive.mode if arrive else "none", "light": body.travel_light,
                              "places": body.stops_per_day, "hours": mins_between(body.day_start, body.day_end)}))
        s.commit()
        return {"total_days": total, "days": out, "start": start_name,
                "used": sorted(used)}   # sent back as `exclude` when planning the later days

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
    def open_alerts(s: Session = Depends(session), include_replied: bool = Query(default=False, alias="all")):
        """Alerts with no reply yet (`?all=true`: every alert, with its replies). D118: with the contact, if one is
        still kept."""
        _purge_contacts(s)
        q = select(db.SafetyAlert).order_by(db.SafetyAlert.created_at)
        rows = s.scalars(q if include_replied else q.where(db.SafetyAlert.first_reply_at.is_(None)))
        return [{"id": a.id, "user_id": a.user_id, "message": a.message, "created_at": a.created_at.isoformat(),
                 "notified": a.notified, "contact": a.contact.contact if a.contact else None,
                 "replies": [{"text": r.text, "by": r.replied_by, "created_at": r.created_at.isoformat()}
                             for r in a.replies]} for a in rows]

    @app.post("/v1/admin/safety/{alert_id}/reply", dependencies=[Depends(admin)])
    def mark_replied(alert_id: int, body: SafetyReplyIn, s: Session = Depends(session)):
        a = s.get(db.SafetyAlert, alert_id)
        if a is None:
            raise HTTPException(404, "no such alert")
        if a.first_reply_at is None:
            a.first_reply_at, a.replied_by = datetime.now(timezone.utc), body.replied_by
        if body.text:   # D118: shown to the person under Help & safety
            s.add(db.SafetyReply(alert_id=a.id, text=body.text, replied_by=body.replied_by))
        if body.resolved and a.contact is not None:   # D118: the contact goes as soon as it's sorted
            s.delete(a.contact)
        s.commit()
        created = a.created_at if a.created_at.tzinfo else a.created_at.replace(tzinfo=timezone.utc)
        first = a.first_reply_at if a.first_reply_at.tzinfo else a.first_reply_at.replace(tzinfo=timezone.utc)
        return {"id": a.id, "minutes_to_first_reply": round((first - created).total_seconds() / 60, 1),
                "resolved": body.resolved}

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
            ("category_answers", db.CategoryAnswer), ("corrections", db.Correction),
            ("safety_replies", db.SafetyReply)]} | {   # D118: never the contacts people left
            # D116: visitors from abroad are their own group, left out of the Test B analysis
            "cohorts": {u.id: cohort(u.profile) for u in s.scalars(select(db.User))}}

    return app


CONTACT_DAYS = 30   # D118: a contact left with a safety message is deleted when resolved, and at the latest after this


def _purge_contacts(s: Session) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=CONTACT_DAYS)
    old = [c for c in s.scalars(select(db.SafetyContact))
           if (c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)) < cutoff]
    for c in old:
        s.delete(c)
    s.commit()
    return len(old)


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
