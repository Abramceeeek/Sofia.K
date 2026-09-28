"""Test B: the two blind plans for each participant, generated from the hand-run Test A (D65, D68).

Input is Abram's filled-in results sheet (`validation/raw/results.xlsx`, never committed):
- the Swipes tab: item number and reaction 1-4;
- the Choices tab: task and A/B;
- the TestB tab: the pre-randomised label of the personalised plan;
- the Participants tab: launch channel, and the inspiring fields in column AG (Test A 5.7, optional, D77).

For each participant it fits δ_person from the swipes and choices (the same Laplace update the
app will use). It then plans the day with the shared brief, and writes:
- both plans in an identical format, as a WhatsApp message and a PDF, labelled A/B from the sheet;
- a review sheet for Abram only: why each stop was chosen, what was left out, and any legs to check.

The sent plans never say *why* a stop was chosen, because that would reveal which plan is
personalised and break the blind test.

    python -m brain.testb weights --results ../validation/raw/results.xlsx
    python -m brain.testb plans --results ../validation/raw/results.xlsx \\
        --brief ../validation/raw/testb/brief.yaml --generic ../validation/raw/testb/generic.yaml \\
        --out ../validation/raw/testb/out
    python -m brain.testb fields        # which aspiration fields have enough ready moments (D77)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import DATA_DIR
from .features import Conditions, conjoint_plan_features, moment_features
from .aspiration import AspirationMap, load_aspiration
from .moments import Moment, Point, load_moments
from .personal import DeltaPosterior
from .planner import DayPlan, LegWeights, candidate_for, hhmm, parse_hhmm, plan_day
from .population import PopulationModel, load_population
from .scoring import conjoint_observation, contributions, named_weights, swipe_observation, update_person
from .travel import LondonEstimate

REACTIONS = {1: "loved", 2: "fine", 3: "didnt_enjoy", 4: "havent_been"}
FIRST_DATA_ROW = 6   # rows 1-3 notes, row 4 the example (ignored), row 5 headers


# ---- inputs -------------------------------------------------------------------------

@dataclass
class Participant:
    pid: str
    channel: str | None = None
    swipes: list[tuple[int, str]] = field(default_factory=list)   # (item number, reaction)
    choices: list[tuple[int, str]] = field(default_factory=list)  # (task, "A"/"B")
    personal_label: str | None = None                             # "A" or "B"
    fields_raw: str | None = None                                 # Test A 5.7, optional (D77)


def _rows(ws, ncols: int):
    for row in ws.iter_rows(min_row=FIRST_DATA_ROW, max_col=ncols, values_only=True):
        if row and row[0] not in (None, ""):
            yield row


def load_results(path: Path) -> dict[str, Participant]:
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    people: dict[str, Participant] = {}

    def get(pid) -> Participant:
        pid = str(pid).strip()
        return people.setdefault(pid, Participant(pid))

    for row in _rows(wb["Participants"], 33):
        p = get(row[0])
        p.channel = str(row[19]).strip() if row[19] else None
        p.fields_raw = str(row[32]).strip() if len(row) > 32 and row[32] not in (None, "") else None   # column AG
    for pid, item, _name, reaction, *_ in _rows(wb["Swipes"], 5):
        if item is not None and reaction is not None:
            get(pid).swipes.append((int(item), REACTIONS[int(reaction)]))
    for pid, task, choice in _rows(wb["Choices"], 3):
        if task is not None and choice:
            get(pid).choices.append((int(task), str(choice).strip().upper()))
    for pid, label, *_ in _rows(wb["TestB"], 2):
        if label:
            get(pid).personal_label = str(label).strip().upper()
    # participants with no Test A data yet are dropped
    return {k: v for k, v in people.items() if v.swipes or v.choices}


def load_swipe_items(path: Path) -> dict[int, Moment]:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    out = {}
    for num, it in d["items"].items():
        out[int(num)] = Moment.model_validate({
            "id": it.get("moment_id") or f"swipe_{int(num):02d}", "title": it["name"],
            "place": {"name": it["name"]}, "features": {"place": it["place"], "moment": it["moment"]},
            "cost_gbp": it.get("cost_gbp"), "source": "swipe-item"})
    return out


def load_tasks(path: Path) -> dict[int, dict[str, dict]]:
    tasks: dict[int, dict[str, dict]] = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tasks.setdefault(int(r["task"]), {})[r["plan"]] = r
    return tasks


@dataclass
class Brief:
    """The same brief for both plans (test-plan.md): same day, times, number of stops and budget."""
    start_name: str
    start: Point
    start_time: str
    end_time: str
    stops: int
    budget_gbp: float | None = None
    day_label: str = "A day out in London"
    weekday: str | None = None     # "mon".."sun": cards closed that day are left out
    temp_c: float | None = None
    rain_prob: float | None = None
    time_limit_s: float = 2.0


def load_brief(path: Path) -> Brief:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    d["start"] = Point(**d["start"])
    return Brief(**d)


# ---- fitting ------------------------------------------------------------------------

def person_fields(amap: AspirationMap | None, p: Participant) -> frozenset[str]:
    """The fields a participant picked (Test A 5.7). Unknown entries are reported, not guessed."""
    if amap is None or not p.fields_raw:
        return frozenset()
    fields, unknown = amap.parse(p.fields_raw)
    if unknown:
        print(f"{p.pid}: unknown inspiring field(s) {unknown} in Participants column AG; ignored", file=sys.stderr)
    return fields


def fit_participant(pop: PopulationModel, p: Participant, swipe_items: dict[int, Moment],
                    tasks: dict[int, dict[str, dict]], amap: AspirationMap | None = None) -> DeltaPosterior:
    fields = person_fields(amap, p)
    obs = []
    for item, reaction in p.swipes:
        m = swipe_items.get(item)
        asp = amap.match(m, fields) if (amap and m is not None) else 0.0
        if m is not None and (o := swipe_observation(pop, m, reaction, asp)):
            obs.append(o)
    for task, choice in p.choices:
        if task in tasks and choice in ("A", "B"):
            obs.append(conjoint_observation(pop, conjoint_plan_features(tasks[task]["A"]),
                                            conjoint_plan_features(tasks[task]["B"]), chose_a=choice == "A"))
    return update_person(pop, obs)


def readback_lines(pop: PopulationModel, post: DeltaPosterior, top: int = 6,
                   field_labels: list[str] | None = None) -> list[str]:
    """Confident weights only, as plain lines Abram can turn into the read-back message.

    The aspiration weight is left out of that list: its prior alone looks "confident", and it only
    matters for people who picked a field, so it is read back from their answer instead (D77).
    """
    ws = [w for w in named_weights(pop, post) if w.confident and w.name != "aspiration_match"]
    ws.sort(key=lambda w: abs(w.weight), reverse=True)
    lines = []
    if field_labels:
        asp = next(w for w in named_weights(pop, post) if w.name == "aspiration_match")
        lines.append(f"Said these fields inspire them: {', '.join(field_labels)} "
                     f"(moments tied to them get weight {asp.weight:+.2f})")
    for w in ws[:top]:
        if w.direction in ("stronger", "weaker"):   # sign-constrained, e.g. cost (D88)
            more = "more" if w.direction == "stronger" else "less"
            lines.append(f"{w.label}: seems to matter {more} to them than to most people "
                         f"(weight {w.weight:+.2f}; population {w.population:+.2f})")
            continue
        verb = "seems to put them off" if w.direction == "dislikes" else "seems to appeal to them"
        # A weight whose sd has barely moved from the prior is the population's view, not theirs (e.g. rain, D95)
        prior_only = w.sd is not None and w.sd >= 0.9 * pop.spec(w.name).delta_sd
        note = " (mostly the population prior, not their answers)" if prior_only else ""
        lines.append(f"{w.label}: {verb} (weight {w.weight:+.2f}, P(negative) {w.p_negative:.2f}){note}")
    if len(lines) == (1 if field_labels else 0):
        lines.append("No confident weights yet: use the persona and the open answers for the read-back.")
    return lines


# ---- planning -----------------------------------------------------------------------

def personal_plan(pop: PopulationModel, post: DeltaPosterior, moments: list[Moment], brief: Brief,
                  travel: LondonEstimate, must_do: str | None = None, amap: AspirationMap | None = None,
                  fields: frozenset[str] = frozenset()) -> tuple[DayPlan, list[dict], list[dict]]:
    b = pop.b_person(post.mean)
    cond = Conditions(brief.temp_c, brief.rain_prob)
    usable = [m for m in moments if m.plannable() and m.open_on(brief.weekday)]
    if brief.rain_prob is not None and brief.rain_prob >= 0.5:
        usable = [m for m in usable if m.best_time.weather != ["dry"]]
    by_id = {m.id: m for m in usable}
    asp = {m.id: (amap.match(m, fields) if amap else 0.0) for m in usable}
    cands = [candidate_for(m, float(pop.vector(moment_features(m, cond, aspiration_match=asp[m.id])) @ b))
             for m in usable]
    idx = {n: i for i, n in enumerate(pop.names)}
    legs = LegWeights(b[idx["transfer_15_30"]], b[idx["transfer_30_plus"]], b[idx["packed_pace"]])
    plan = plan_day(cands, brief.start, parse_hhmm(brief.start_time), parse_hhmm(brief.end_time), travel, legs,
                    floor=pop.cutpoints["rating"][1], max_stops=brief.stops, min_stops=brief.stops,
                    budget_gbp=brief.budget_gbp, must_include={must_do} if must_do else set(),
                    time_limit_s=brief.time_limit_s)
    stops, prev_point, prev_name = [], brief.start, brief.start_name
    for st in plan.stops:
        m = by_id[st.moment_id]
        mode = travel.mode(prev_point, m.start())
        stops.append({
            "title": m.title, "arrive": hhmm(st.arrive_min), "depart": hhmm(st.depart_min),
            "travel_min": st.travel_min, "travel_mode": mode, "from": prev_name,
            "approach": approach_text(m),
            "what": clean(m.experience.what_happens), "best": clean(m.best_time.light),
            "cost_gbp": m.cost_gbp or 0.0,
            # review only, never sent:
            "moment_id": m.id, "predicted": st.utility,
            "why": contributions(pop, b, moment_features(m, cond, st.travel_min, asp[m.id])),
        })
        prev_point, prev_name = m.end(), m.leave_name()
    utilities = sorted(((c.utility, c.moment_id) for c in cands), reverse=True)
    visited = {s["moment_id"] for s in stops}
    left_out = [{"moment_id": mid, "title": by_id[mid].title, "predicted": round(u, 3)}
                for u, mid in utilities if mid not in visited][:3]
    return plan, stops, left_out


def approach_text(m: Moment) -> str:
    """How to arrive, in one line. If the path already says where from, don't repeat "From X."."""
    path = clean(m.approach.path)
    if m.approach.from_ and not path.lower().startswith("from "):
        return clean(f"From {m.approach.from_}. {path}")
    return path or clean(m.approach.from_ and f"From {m.approach.from_}.")


def generic_stops(path: Path, moments: dict[str, Moment]) -> list[dict]:
    """The generic plan, written once by Abram. Stops are moment ids or free text, same fields."""
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    out = []
    for s in d["stops"]:
        if "moment_id" in s:
            m = moments[s["moment_id"]]
            s = {"title": m.title, "what": m.experience.what_happens or "", "best": m.best_time.light or "",
                 "cost_gbp": m.cost_gbp or 0.0,
                 "approach": " ".join(x for x in (m.approach.from_ and f"From {m.approach.from_}.", m.approach.path) if x),
                 **s}
        out.append({"title": s["title"], "arrive": s["arrive"], "travel_min": s.get("travel_min"),
                    "travel_mode": s.get("travel_mode", "walk"), "from": s.get("from", ""),
                    "approach": clean(s.get("approach")), "what": clean(s.get("what")), "best": clean(s.get("best")),
                    "cost_gbp": s.get("cost_gbp") or 0.0})
    return out


# ---- rendering (identical for both plans) ------------------------------------------

_MARKER = re.compile(r"\s*\((?:GUESS|CHECKED|FOUNDER|UNVERIFIED)\b[^)]*\)")


def clean(text: str | None) -> str:
    """Participant-facing text: drop the cards' internal notes, e.g. "(GUESS)" or "(CHECKED: ...)"."""
    return _MARKER.sub("", text or "").strip()

def _travel_line(s: dict) -> str:
    if s.get("travel_min") is None:
        return ""
    how = "on foot" if s["travel_mode"] == "walk" else "by Tube or bus"
    src = f" from {s['from']}" if s.get("from") else ""
    return f"Getting there: about {int(s['travel_min'])} min {how}{src}."


def _cost(c: float) -> str:
    return "free" if not c else f"£{c:,.0f}" if float(c).is_integer() else f"£{c:,.2f}"


def _summary(brief: Brief, stops: list[dict]) -> str:
    total = sum(s["cost_gbp"] for s in stops)
    money = f"entry costs about {_cost(total)} per person" if total else "no entry costs"
    return f"{brief.start_time}–{brief.end_time} · {len(stops)} stops · {money}"


def plan_text(label: str, brief: Brief, stops: list[dict]) -> str:
    """A WhatsApp message (WhatsApp shows *text* as bold)."""
    lines = [f"*Plan {label}: {brief.day_label}*", _summary(brief, stops), ""]
    for i, s in enumerate(stops, 1):
        lines.append(f"*{i}. {s['arrive']}  {s['title']}*")
        for part in (_travel_line(s), s.get("approach"), s.get("what"),
                     s.get("best") and f"Best: {s['best']}", f"Cost: {_cost(s['cost_gbp'])}"):
            if part:
                lines.append(part)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def plan_pdf(label: str, brief: Brief, stops: list[dict], path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    st = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm, title=f"Plan {label}")
    flow = [Paragraph(escape(f"Plan {label}: {brief.day_label}"), st["Title"]),
            Paragraph(escape(_summary(brief, stops)), st["Normal"]), Spacer(1, 6 * mm)]
    for i, s in enumerate(stops, 1):
        flow.append(Paragraph(escape(f"{i}. {s['arrive']}  {s['title']}"), st["Heading3"]))
        for part in (_travel_line(s), s.get("approach"), s.get("what"),
                     s.get("best") and f"Best: {s['best']}", f"Cost: {_cost(s['cost_gbp'])}"):
            if part:
                flow.append(Paragraph(escape(part), st["Normal"]))
        flow.append(Spacer(1, 4 * mm))
    doc.build(flow)


def review_text(p: Participant, post: DeltaPosterior, plan: DayPlan, stops: list[dict], left_out: list[dict],
                pop: PopulationModel, brief: Brief, must_do: str | None, intent: dict,
                field_labels: list[str] | None = None) -> str:
    personal, generic = (p.personal_label or "?"), ("B" if p.personal_label == "A" else "A")
    out = [f"# {p.pid}: review before sending (for Abram only)", "",
           f"- Channel: {p.channel or 'unknown'}. Personalised plan is **{personal}**, generic is **{generic}** (TestB tab).",
           f"- Data used: {len(p.swipes)} swipes, {len(p.choices)} choices ({post.n_obs} informative).",
           f"- Planner status: {plan.status}.",
           f"- Trip intent: {intent or 'none recorded'}. Must-do: {must_do or 'none'}.",
           f"- Inspiring fields (Test A 5.7): {', '.join(field_labels) if field_labels else 'none given'}.", "",
           "## Read-back lines (confident weights only)", ""]
    out += [f"- {l}" for l in readback_lines(pop, post, field_labels=field_labels)]
    out += ["", "## Personalised plan: why each stop", ""]
    total = 0.0
    for s in stops:
        total += s["cost_gbp"]
        why = "; ".join(f"{w['label']} {w['contribution']:+.2f}" for w in s["why"])
        flag = " **check this leg**" if s["travel_mode"] != "walk" or s["travel_min"] > 30 else ""
        out.append(f"- {s['arrive']} {s['title']} (predicted {s['predicted']:+.2f}): {why}. "
                   f"Travel {s['travel_min']} min ({s['travel_mode']}){flag}")
    out += ["", f"Total cost: {_cost(total)}" + (f" against a budget of {_cost(brief.budget_gbp)}." if brief.budget_gbp else "."),
            "", "## Strong moments left out", ""]
    out += [f"- {m['title']} (predicted {m['predicted']:+.2f})" for m in left_out] or ["- none"]
    out += ["", "## Before sending", "",
            "- [ ] Every Tube/bus leg checked (the times are rough estimates)",
            "- [ ] Opening hours and prices still right on the day",
            "- [ ] Same number of stops and same format as the generic plan",
            "- [ ] Nothing in the text says why a stop was chosen (keeps the test blind)", ""]
    return "\n".join(out)


# ---- CLI ----------------------------------------------------------------------------

def _load_common(data_dir: Path):
    pop = load_population(data_dir / "priors.yaml")
    return (pop, load_swipe_items(data_dir / "swipe_items.yaml"), load_tasks(data_dir / "conjoint_design.csv"),
            load_moments(data_dir / "moments"))


def _load_aspiration(data_dir: Path) -> AspirationMap | None:
    path = data_dir / "aspiration.yaml"
    return load_aspiration(path) if path.exists() else None


def coverage_lines(amap: AspirationMap, moments: list[Moment]) -> list[str]:
    lines = []
    for r in amap.coverage(moments):
        flag = "  <-- FLAG: fewer than %d ready" % amap.min_ready if r["flag"] else ""
        lines.append(f"{r['label']:18s} ready {r['ready']} (in {r['ready_groups']} variant groups), "
                     f"drafts {r['drafts']}{flag}")
    return lines


def cmd_fields(args) -> int:
    """Which aspiration fields have enough checked moments (D77)."""
    data = Path(args.data)
    amap = _load_aspiration(data)
    if amap is None:
        print("No data/aspiration.yaml", file=sys.stderr)
        return 2
    for line in coverage_lines(amap, load_moments(data / "moments")):
        print(line)
    return 0


def cmd_weights(args) -> int:
    pop, items, tasks, _ = _load_common(Path(args.data))
    amap = _load_aspiration(Path(args.data))
    people = load_results(Path(args.results))
    for pid in sorted(people):
        if args.ids and pid not in args.ids:
            continue
        post = fit_participant(pop, people[pid], items, tasks, amap)
        labels = amap.labels(person_fields(amap, people[pid])) if amap else []
        print(f"{pid} ({people[pid].channel or 'channel?'}, {post.n_obs} informative answers)")
        for line in readback_lines(pop, post, field_labels=labels):
            print(f"  - {line}")
    return 0


def cmd_plans(args) -> int:
    pop, items, tasks, moments = _load_common(Path(args.data))
    # Test B plans go to real people, so only cards Abram has checked (status: ready) are used, unless
    # --include-drafts is given for a dry run. Drafts can hold Claude's GUESS values (D72).
    drafts_skipped = [m.id for m in moments if m.status != "ready" and m.plannable()]
    if not args.include_drafts:
        moments = [m for m in moments if m.status == "ready"]
        if drafts_skipped:
            print(f"Skipping {len(drafts_skipped)} draft moments (set status: ready once checked, "
                  f"or use --include-drafts for a dry run): {', '.join(drafts_skipped)}", file=sys.stderr)
    elif drafts_skipped:
        print(f"DRY RUN: using {len(drafts_skipped)} unchecked draft moments. Don't send these plans.", file=sys.stderr)
    plannable = [m for m in moments if m.plannable()]
    amap = _load_aspiration(Path(args.data))
    if amap:
        flagged = [l for l in coverage_lines(amap, moments) if "FLAG" in l]
        if flagged:
            print("Aspiration fields with too few ready moments (people who picked them get little from it):\n  "
                  + "\n  ".join(flagged), file=sys.stderr)
    brief = load_brief(Path(args.brief))
    if len(plannable) < brief.stops:
        drafts = {m.id: m.missing_for_planning()[:3] for m in moments if not m.plannable()}
        print(f"Only {len(plannable)} plannable moments; the brief needs at least {brief.stops}. "
              f"Fill in data/moments (Area 2 schema). Drafts: {drafts}", file=sys.stderr)
        return 2
    people = load_results(Path(args.results))
    intents = {}
    if args.intent:
        with open(args.intent, encoding="utf-8") as f:
            intents = yaml.safe_load(f) or {}
    gen = generic_stops(Path(args.generic), {m.id: m for m in moments})
    if len(gen) != brief.stops:
        print(f"Warning: the generic plan has {len(gen)} stops and the brief asks for {brief.stops}.", file=sys.stderr)
    for field_ in ("approach", "what"):
        missing = [s["title"] for s in gen if not s.get(field_)]
        if missing:
            print(f"Warning: generic stops without '{field_}' ({missing}). Personalised stops have it, "
                  f"so the difference could give the plans away.", file=sys.stderr)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    travel = LondonEstimate()
    for pid in sorted(people):
        if args.ids and pid not in args.ids:
            continue
        p = people[pid]
        if p.personal_label not in ("A", "B"):
            print(f"{pid}: no A/B label on the TestB tab, skipped", file=sys.stderr)
            continue
        intent = intents.get(pid, {}) or {}
        must_do = intent.get("must_do")
        post = fit_participant(pop, p, items, tasks, amap)
        fields = person_fields(amap, p)
        labels = amap.labels(fields) if amap else []
        plan, stops, left_out = personal_plan(pop, post, moments, brief, travel, must_do, amap, fields)
        generic_label = "B" if p.personal_label == "A" else "A"
        for label, st in ((p.personal_label, stops), (generic_label, gen)):
            (out / f"{pid}_plan_{label}.txt").write_text(plan_text(label, brief, st), encoding="utf-8")
            if not args.no_pdf:
                plan_pdf(label, brief, st, out / f"{pid}_plan_{label}.pdf")
        (out / f"{pid}_review.md").write_text(
            review_text(p, post, plan, stops, left_out, pop, brief, must_do, intent, labels), encoding="utf-8")
        print(f"{pid}: plans A and B written ({plan.status})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m brain.testb", description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", default=str(DATA_DIR), help="brain data folder (priors, swipe items, moments)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("weights", help="read-back lines for each participant")
    w.add_argument("--results", required=True)
    w.add_argument("--ids", type=lambda s: set(s.split(",")))
    sub.add_parser("fields", help="aspiration fields: ready moments per field, flagged below the minimum (D77)")
    pl = sub.add_parser("plans", help="write both plans and a review sheet for each participant")
    pl.add_argument("--results", required=True)
    pl.add_argument("--brief", required=True)
    pl.add_argument("--generic", required=True)
    pl.add_argument("--intent")
    pl.add_argument("--out", required=True)
    pl.add_argument("--ids", type=lambda s: set(s.split(",")))
    pl.add_argument("--no-pdf", action="store_true")
    pl.add_argument("--include-drafts", action="store_true",
                    help="dry run: also plan with draft moments (unchecked GUESS values); never send these")
    args = ap.parse_args(argv)
    return {"weights": cmd_weights, "plans": cmd_plans, "fields": cmd_fields}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
