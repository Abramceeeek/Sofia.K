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
import json
import math
import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from .config import DATA_DIR
from .features import conjoint_plan_features
from .aspiration import AspirationMap, load_aspiration
from .moments import Moment, load_moments, parse_windows
from .personal import DeltaPosterior
from .planner import DayPlan, hhmm, parse_hhmm
from .population import PopulationModel, load_population
from .scoring import conjoint_observation, named_weights, swipe_observation, update_person
from .travel import LondonEstimate
# The planning engine lives in dayplan.py (D107), shared with the app's API; re-exported here for the CLI and tests.
from .dayplan import (GENERIC_STOP_MIN, Brief, PlanNotes, _base, _best_line, _cost, _cost_line,  # noqa: F401
                      _header, _leave, _same_place, _sentence, _stop_lines, _sunset, approach_text, clean,
                      dwell_targets, leg_text, load_brief, load_swipe_cards, load_swipe_items, lunch_candidates,
                      pace_of, personal_plan, transport_gbp)

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


def places_by_reaction(p: Participant, swipe_cards: dict[int, tuple[str, list[str]]]):
    """(loved, disliked): the swipe places, each with its card ids."""
    loved = [swipe_cards[i] for i, r in p.swipes if r == "loved" and i in swipe_cards]
    disliked = [swipe_cards[i] for i, r in p.swipes if r == "didnt_enjoy" and i in swipe_cards]
    return loved, disliked


def load_tasks(path: Path) -> dict[int, dict[str, dict]]:
    tasks: dict[int, dict[str, dict]] = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tasks.setdefault(int(r["task"]), {})[r["plan"]] = r
    return tasks






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


# ---- the generic plan and labels -----------------------------------------------------



























OTHER_LABEL = {"A": "B", "B": "A", "1": "2", "2": "1"}
NUMBERED = {"A": "1", "B": "2"}   # --numbered: "Plan 1" / "Plan 2" instead of A / B


def plan_end(stops: list[dict]) -> int | None:
    """When a plan finishes, in minutes: the last stop's departure (or arrival + 45 min for a generic stop)."""
    if not stops:
        return None
    last = stops[-1]
    if last.get("depart"):
        return parse_hhmm(last["depart"])
    return parse_hhmm(last["arrive"]) + GENERIC_STOP_MIN










def generic_stops(path: Path, moments: dict[str, Moment], sunset: int | None = None) -> list[dict]:
    """The generic plan, written once by Abram. Stops are moment ids or free text, same fields.
    D100 fields: `best_window` (when the `best` line is shown), `cost_kind` (food/entry/ticket/hire) and
    `rain_swap` (the "If it rains:" line for an outdoor stop). D102: `lunch: true` marks the meal stop and
    `queue_min` adds an "Allow about N min to queue." line."""
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    out = []
    for s in d["stops"]:
        if "moment_id" in s:
            m = moments[s["moment_id"]]
            s = {"title": m.title, "what": m.experience.what_happens or "", "best": m.best_time.light or "",
                 "best_window": m.best_time.best_window, "best_around_sunset": m.best_time.best_around_sunset,
                 "cost_gbp": m.cost_gbp or 0.0, "cost_kind": m.price_kind(),
                 "approach": approach_text(m, came_from=s.get("from")), **s}
        out.append({"title": s["title"], "arrive": s["arrive"], "depart": s.get("depart"), "travel_min": s.get("travel_min"),
                    "travel_mode": s.get("travel_mode", "walk"), "from": s.get("from", ""),
                    "approach": _sentence(clean(s.get("approach"))), "what": _sentence(clean(s.get("what"))),
                    "best": clean(s.get("best")),
                    "best_windows": ([(sunset + s["best_around_sunset"][0], sunset + s["best_around_sunset"][1])]
                                     if s.get("best_around_sunset") and sunset is not None
                                     else parse_windows(s.get("best_window") or [], s["title"])),
                    "cost_gbp": s.get("cost_gbp") or 0.0, "cost_kind": s.get("cost_kind") or "entry",
                    "rain_swap": _sentence(clean(s.get("rain_swap"))), "lunch": bool(s.get("lunch")),
                    "queue": s.get("queue_min") or 0})
    return out


# ---- rendering (identical for both plans) ------------------------------------------
























def plan_text(label: str, brief: Brief, stops: list[dict]) -> str:
    """A WhatsApp message (WhatsApp shows *text* as bold)."""
    title, *rest = _header(label, brief, stops)
    lines = [f"*{title}*", *rest, ""]
    for i, s in enumerate(stops, 1):
        lines.append(f"*{i}. {s['arrive']}–{_leave(s)}  {s['title']}*")
        lines += _stop_lines(s)
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
    title, *rest = _header(label, brief, stops)
    flow = [Paragraph(escape(title), st["Title"])] + [Paragraph(escape(x), st["Normal"]) for x in rest]
    flow.append(Spacer(1, 6 * mm))
    for i, s in enumerate(stops, 1):
        flow.append(Paragraph(escape(f"{i}. {s['arrive']}–{_leave(s)}  {s['title']}"), st["Heading3"]))
        flow += [Paragraph(escape(x), st["Normal"]) for x in _stop_lines(s)]
        flow.append(Spacer(1, 4 * mm))
    doc.build(flow)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def text_checks(stops: list[dict], n: int = 5) -> list[str]:
    """For the review (D100): lines that aren't full sentences, and arrival and description lines that repeat
    each other (5 or more words in a row)."""
    out = []
    for i, s in enumerate(stops, 1):
        for key in ("approach", "what", "rain_swap"):
            x = s.get(key) or ""
            if x and x[-1] not in ".!?":
                out.append(f"stop {i}: no full stop at the end of the {key} line")
        a, w = _words(s.get("approach") or ""), _words(s.get("what") or "")
        grams = {tuple(a[k:k + n]) for k in range(len(a) - n + 1)}
        if any(tuple(w[k:k + n]) in grams for k in range(len(w) - n + 1)):
            out.append(f"stop {i}: the arrival and description lines repeat each other")
    return out


def review_text(p: Participant, post: DeltaPosterior, plan: DayPlan, stops: list[dict], left_out: list[dict],
                pop: PopulationModel, brief: Brief, must_do: str | None, intent: dict,
                field_labels: list[str] | None = None, notes: PlanNotes | None = None,
                generic: list[dict] | None = None, familiar: bool = False) -> str:
    personal, generic_label = (p.personal_label or "?"), OTHER_LABEL.get(p.personal_label or "", "?")
    notes = notes or PlanNotes()
    out = [f"# {p.pid}: review before sending (for Abram only)", "",
           f"- Channel: {p.channel or 'unknown'}. Personalised plan is **{personal}**, generic is **{generic_label}** (TestB tab).",
           f"- Data used: {len(p.swipes)} swipes, {len(p.choices)} choices ({post.n_obs} informative).",
           f"- Planner status: {plan.status}.",
           f"- Trip intent: {intent or 'none recorded'}. Must-do: {must_do or 'none'}.",
           f"- Inspiring fields (Test A 5.7): {', '.join(field_labels) if field_labels else 'none given'}.",
           f"- Pace (D102): {notes.pace}"
           + (" (longer stays where the day has room)" if notes.pace == "relaxed" else "") + ".",
           f"- Lunch (D102): {notes.lunch}.",
           f"- Familiar favourite (D100, {'on' if familiar else 'off'}): "
           + (next((s['title'] for s in stops if s.get('familiar')), notes.favourite) if notes.favourite
              else "none" if familiar else "rule not used"), "",
           "## Read-back lines (confident weights only)", ""]
    out += [f"- {l}" for l in readback_lines(pop, post, field_labels=field_labels)]
    out += ["", "## Personalised plan: why each stop", ""]
    for s in stops:
        flag = " **check this leg**" if s["travel_mode"] != "walk" or s["travel_min"] > 30 else ""
        if s["predicted"] is None:     # a flexible lunch slot
            out.append(f"- {s['arrive']}–{s['depart']} {s['title']} (flexible lunch slot, D102). "
                       f"Travel {s['travel_min']} min ({s['travel_mode']}){flag}.")
            continue
        why = "; ".join(f"{w['label']} {w['contribution']:+.2f}" for w in s["why"])
        fam = " **Familiar favourite.**" if s.get("familiar") else ""
        meal = " Lunch stop." if s.get("lunch") else ""
        out.append(f"- {s['arrive']}–{s['depart']} {s['title']} (predicted {s['predicted']:+.2f}): {why}. "
                   f"Travel {s['travel_min']} min ({s['travel_mode']}){flag}.{fam}{meal}")
    total = sum(s["cost_gbp"] for s in stops)
    out += ["", f"Food and entry: {_cost(total)}" + (f" against a budget of {_cost(brief.budget_gbp)}" if brief.budget_gbp else "")
            + f"; transport about {_cost(transport_gbp(stops))}.", "",
            "## Places they loved: in the plan or why not (D100)", ""]
    out += [f"- {name}: {why}" for name, why in notes.loves] or ["- none marked as loved"]
    outdoor_no_swap = [s["title"] for s in stops if not s.get("rain_swap")]
    if stops and not any(s.get("rain_swap") for s in stops):
        out.insert(out.index("## Places they loved: in the plan or why not (D100)") - 1,
                   "\n**Rain: no indoor option found near this plan. Add one by hand before sending (D100).**")
    out += ["", "## Places they didn't enjoy", ""]
    out += [f"- {name}: {why}" for name, why in notes.dislikes] or ["- none"]
    out += ["", "## Strong moments left out", ""]
    out += [f"- {m['title']} (predicted {m['predicted']:+.2f})" for m in left_out] or ["- none"]
    checks = [f"personalised {c}" for c in text_checks(stops)] + [f"generic {c}" for c in text_checks(generic or [])]
    out += ["", "## Text checks (D100)", ""] + ([f"- {c}" for c in checks] or ["- none found"])
    out += ["", "## Before sending", "",
            "- [ ] Every Tube/bus leg checked (the times are rough estimates)",
            "- [ ] Opening hours and prices still right on the day",
            "- [ ] Same number of stops and same format as the generic plan",
            "- [ ] Both plans end within 30 min of each other (D97)",
            "- [ ] Each outdoor stop has a rain swap in both plans, or the plan has an indoor stop (D100)",
            "- [ ] Both plans have a lunch stop around midday (D102)",
            "- [ ] Nothing in the text says why a stop was chosen (keeps the test blind)", ""]
    return "\n".join(out)


# ---- overlap across participants (D104) -------------------------------------------

DISSIMILAR_BELOW = 0.3   # GUESS: cosine similarity of two people's standardised δ below this counts as "dissimilar"
MIN_SIGNAL = 0.5         # GUESS: a person whose standardised δ is shorter than this has too little data to compare


def taste_vector(pop: PopulationModel, post: DeltaPosterior) -> list[float]:
    """δ in prior-sd units: how far this person's weights sit from the population's, feature by feature."""
    return [round(float(d / sd), 4) for d, sd in zip(post.mean, pop.delta_prior_sd)]


def save_personal(out: Path, pid: str, stops: list[dict], taste: list[float]) -> None:
    """What the overlap report needs, next to the plans (stop ids and titles; no answers, no names)."""
    rows = [{"id": _base(s["moment_id"]), "title": s["title"]} for s in stops]
    (out / f"{pid}_personal.json").write_text(json.dumps({"pid": pid, "stops": rows, "taste": taste}, indent=1),
                                              encoding="utf-8")


def _cosine(a: list[float], b: list[float]) -> float | None:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    if na < MIN_SIGNAL or nb < MIN_SIGNAL:
        return None
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def overlap_report(out: Path) -> tuple[str, list[str]]:
    """D104: how much different people's personal plans overlap. Flexible lunch slots never count as shared.
    Warns when two dissimilar people share more than half their stops, and lists stops in most plans."""
    people = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(out.glob("*_personal.json"))]
    stops = {p["pid"]: [s for s in p["stops"] if not s["id"].startswith("lunch@")] for p in people}
    title = {s["id"]: s["title"] for p in people for s in p["stops"]}
    lines = ["# Overlap between personal plans (D104, for Abram only)", "",
             f"{len(people)} personal plans. Flexible lunch slots don't count. \"Dissimilar\" means their weights point "
             f"different ways (cosine below {DISSIMILAR_BELOW}); \"too little data\" means we can't tell.", "",
             "## Pairs", "", "| Pair | Shared | Similarity | Shared stops |", "|---|---|---|---|"]
    warnings = []
    for i, a in enumerate(people):
        for b in people[i + 1:]:
            ids_a, ids_b = {s["id"] for s in stops[a["pid"]]}, {s["id"] for s in stops[b["pid"]]}
            shared = sorted(ids_a & ids_b)
            size = min(len(a["stops"]), len(b["stops"])) or 1
            sim = _cosine(a["taste"], b["taste"])
            sim_txt = "too little data" if sim is None else f"{sim:+.2f}" + (" (dissimilar)" if sim < DISSIMILAR_BELOW else "")
            flag = ""
            if len(shared) > size / 2 and sim is not None and sim < DISSIMILAR_BELOW:
                flag = " **WARNING**"
                warnings.append(f"{a['pid']} and {b['pid']} are dissimilar ({sim:+.2f}) but share {len(shared)} of "
                                f"{size} stops: {', '.join(title[x] for x in shared)}")
            lines.append(f"| {a['pid']}–{b['pid']}{flag} | {len(shared)} of {size} | {sim_txt} | "
                         f"{'; '.join(title[x] for x in shared) or '—'} |")
    counts: dict[str, int] = {}
    for p in people:
        for sid in {s["id"] for s in stops[p["pid"]]}:
            counts[sid] = counts.get(sid, 0) + 1
    common = sorted(((n, sid) for sid, n in counts.items() if len(people) >= 3 and n > len(people) / 2), reverse=True)
    lines += ["", "## Stops in more than half the plans", ""]
    lines += [f"- {title[sid]}: {n} of {len(people)} plans" for n, sid in common] or ["- none"]
    if warnings:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in warnings] + [
            "", "Check these by hand before sending: the plans may be driven by the start point and the cards nearby "
                "rather than by the person."]
    return "\n".join(lines) + "\n", warnings


def cmd_overlap(args) -> int:
    report, warnings = overlap_report(Path(args.out))
    (Path(args.out) / "overlap.md").write_text(report, encoding="utf-8")
    for w in warnings:
        print(f"Overlap warning: {w}", file=sys.stderr)
    print(report)
    return 0


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
    kept_out = [m.id for m in moments if not m.in_test_b]
    if kept_out:   # D105: cards the app keeps but Test B doesn't use (e.g. booking plus price)
        print(f"Kept out of Test B ({len(kept_out)}): {', '.join(kept_out)}", file=sys.stderr)
        moments = [m for m in moments if m.in_test_b]
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
    gen = generic_stops(Path(args.generic), {m.id: m for m in moments}, _sunset(brief))
    gen_end = plan_end(gen)
    if gen and not any(s["lunch"] for s in gen):
        print("Warning: the generic plan has no stop marked 'lunch: true'. Personal plans include lunch when the day "
              "spans midday (D102).", file=sys.stderr)
    if gen and gen[0].get("from") and not _same_place(gen[0]["from"], brief.start_name):
        print(f"Warning: the generic plan starts from {gen[0]['from']!r} and the brief from {brief.start_name!r}. "
              f"Use the same start in both (D100).", file=sys.stderr)
    if gen and not gen[-1].get("depart"):
        print(f"Warning: the generic plan's last stop has no 'depart'; assuming {GENERIC_STOP_MIN} min there.",
              file=sys.stderr)
    end_window = (gen_end - 30, gen_end + 30) if gen_end is not None else None   # D97: end within 30 min
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
    swipe_cards = load_swipe_cards(Path(args.data) / "swipe_items.yaml")
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
        loved, disliked = places_by_reaction(p, swipe_cards)
        plan, stops, left_out, notes = personal_plan(pop, post, moments, brief, travel, must_do, amap, fields,
                                                     end_window, loved, disliked, familiar=args.familiar)
        if args.numbered:
            p = replace(p, personal_label=NUMBERED[p.personal_label])
        generic_label = OTHER_LABEL[p.personal_label]
        for label, st in ((p.personal_label, stops), (generic_label, gen)):
            (out / f"{pid}_plan_{label}.txt").write_text(plan_text(label, brief, st), encoding="utf-8")
            if not args.no_pdf:
                plan_pdf(label, brief, st, out / f"{pid}_plan_{label}.pdf")
        review = review_text(p, post, plan, stops, left_out, pop, brief, must_do, intent, labels,
                             notes=notes, generic=gen, familiar=args.familiar)
        p_end = plan_end(stops)
        if p_end is not None and gen_end is not None:
            ok = abs(p_end - gen_end) <= 30
            review = review.replace("## Read-back lines", f"- Ends: personalised {hhmm(p_end)}, generic {hhmm(gen_end)} "
                                    f"({'within 30 min' if ok else '**more than 30 min apart: fix by hand**'}, D97).\n\n"
                                    "## Read-back lines", 1)
        (out / f"{pid}_review.md").write_text(review, encoding="utf-8")
        save_personal(out, pid, stops, taste_vector(pop, post))
        print(f"{pid}: plans {min(p.personal_label, generic_label)} and {max(p.personal_label, generic_label)} written ({plan.status})")
    report, warnings = overlap_report(out)   # D104: across everyone planned so far in this folder
    (out / "overlap.md").write_text(report, encoding="utf-8")
    for w in warnings:
        print(f"Overlap warning: {w}", file=sys.stderr)
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
    pl.add_argument("--numbered", action="store_true", help='label the plans "Plan 1" / "Plan 2" instead of A / B')
    pl.add_argument("--familiar", action="store_true",
                    help="D100 proposal: include exactly one place the person loved, if one fits the day")
    pl.add_argument("--include-drafts", action="store_true",
                    help="dry run: also plan with draft moments (unchecked GUESS values); never send these")
    ov = sub.add_parser("overlap", help="how much the personal plans in a folder overlap (D104)")
    ov.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    return {"weights": cmd_weights, "plans": cmd_plans, "fields": cmd_fields, "overlap": cmd_overlap}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
