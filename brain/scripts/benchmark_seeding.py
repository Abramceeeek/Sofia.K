"""m216: does two-stage planning (a valid day built step by step, then the solver improving it) beat the current
planner on days with personal time? Synthetic travellers only (scripts/benchmark_planner.py's), never a target.

Run from brain/: `.venv/bin/python scripts/benchmark_seeding.py [--workers 4]`

Every traveller × each day with the person's own time (one block near the places, one whose place isn't decided over
lunch, free time in the afternoon, and two blocks) × three catalogue sizes (15, 30 and all 49 ready cards, the smaller
ones a fixed random subset) × two time limits (0.2 s, as on a busy server, and the app's 1 s) × current vs seeded.
Each plan is checked from outside the solver with the benchmark's own rules, and timed.
"""

from __future__ import annotations

import argparse
import multiprocessing
import random
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import benchmark_planner as bp  # noqa: E402
from brain import dayplan  # noqa: E402
from brain.dayplan import Block  # noqa: E402

SEED = 20261107
_NOISE = [False]
SIZES = (15, 30, None)            # None: every ready card
LIMITS = (0.2, 1.0)
TWO_BLOCKS = bp.Scenario("two_blocks", "10:00", "19:00", 4, "sat",
                         mine=(Block("plans", 660, 720, "near"), Block("free", 930, 990)))
DAYS = [s for s in bp.SCENARIOS if s.mine] + [TWO_BLOCKS]


def _cards(size: int | None) -> list:
    cards = bp._C["moments"]
    if size is None or size >= len(cards):
        return cards
    return random.Random(SEED + size).sample(cards, size)


def one(job: tuple[int, int, int, float, bool]) -> dict:
    pi, di, size, limit, seeded = job
    prof, sc = bp.PROFILES[pi], DAYS[di]
    pop, travel = bp._C["pop"], bp._C["travel"]
    brief = bp.brief_for(sc, prof, limit)
    delta = bp.delta_of(pop, prof)
    dayplan.SEEDED_WITH_BLOCKS = seeded and not _NOISE[0]   # --noise: both arms are the current planner
    cards = _cards(size)
    t0 = time.perf_counter()
    plan, _, _, _ = dayplan.personal_plan(pop, bp.known(delta), cards, brief, travel, familiar=False,
                                          popularity=bp._C["popularity"])
    secs = time.perf_counter() - t0
    m = bp.measure(bp.from_planner(plan), brief, pop, pop.b_person(delta), prof)
    return {"profile": prof.name, "day": sc.name, "size": size or len(bp._C["moments"]), "limit": limit,
            "seeded": seeded, "value": m["value"], "violations": m["violations"], "places": m["places"],
            "asked": sc.stops - (1 if sc.lunch and dayplan.spans_lunch(dayplan.parse_hhmm(sc.start),
                                                                        dayplan.parse_hhmm(sc.end)) else 0),
            "travel": m["travel_min"], "free_kept": m["free_kept_share"], "ok": plan.status == "ok", "secs": secs}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/synthetic/seeding.txt"))
    ap.add_argument("--noise", action="store_true", help="plan every day twice with the current planner: the floor")
    args = ap.parse_args(argv)
    _NOISE[0] = args.noise
    bp.load_context(1.0)
    jobs = [(pi, di, size, limit, seeded) for pi, p in enumerate(bp.PROFILES) if p.runnable
            for di in range(len(DAYS)) for size in SIZES for limit in LIMITS for seeded in (False, True)]
    with multiprocessing.get_context("fork").Pool(args.workers) as pool:
        rows = pool.map(one, jobs)
    key = lambda r: (r["profile"], r["day"], r["size"], r["limit"])
    cur = {key(r): r for r in rows if not r["seeded"]}
    new = {key(r): r for r in rows if r["seeded"]}
    out = ["SYNTHETIC TRAVELLERS ONLY. Days with personal time: current planner vs two-stage (seeded).",
           f"{len(cur)} traveller-days, each planned both ways; seed {SEED}; {args.workers} plans solved at once.", ""]
    out.append(f"{'size':>5} {'limit':>5} | {'better':>6} {'same':>5} {'worse':>5} | {'mean gain':>9} "
               f"{'worst':>6} | {'breaks cur/new':>14} | {'places short cur/new':>20} | {'secs cur/new (p90)':>18}")
    for size in sorted({r["size"] for r in rows}):
        for limit in LIMITS:
            ks = [k for k in cur if k[2] == size and k[3] == limit]
            d = [new[k]["value"] - cur[k]["value"] for k in ks]
            br = (sum(bool(cur[k]["violations"]) for k in ks), sum(bool(new[k]["violations"]) for k in ks))
            short = (sum(cur[k]["places"] < cur[k]["asked"] for k in ks), sum(new[k]["places"] < new[k]["asked"]
                                                                               for k in ks))
            p90 = lambda xs: sorted(xs)[int(0.9 * (len(xs) - 1))]
            secs = (p90([cur[k]["secs"] for k in ks]), p90([new[k]["secs"] for k in ks]))
            out.append(f"{size:>5} {limit:>5} | {sum(x > 1e-6 for x in d):>6} {sum(abs(x) <= 1e-6 for x in d):>5} "
                       f"{sum(x < -1e-6 for x in d):>5} | {statistics.mean(d):>+9.3f} {min(d):>+6.2f} | "
                       f"{br[0]:>6}/{br[1]:<7} | {short[0]:>9}/{short[1]:<10} | {secs[0]:>8.2f}/{secs[1]:<9.2f}")
    worse = sorted(((new[k]["value"] - cur[k]["value"], k) for k in cur if new[k]["value"] < cur[k]["value"] - 1e-6))
    out.append("")
    out.append(f"Seeded worse than current: {len(worse)} of {len(cur)}" + (" — the worst: " + "; ".join(
        f"{k[0]}/{k[1]}/{k[2]} cards/{k[3]}s {d:+.2f}" for d, k in worse[:5]) if worse else ""))
    kept = [r["free_kept"] for r in rows if r["free_kept"] is not None]
    out.append(f"Personal time kept, every plan both ways: {sum(k == 1.0 for k in kept)} of {len(kept)}")
    for v in [r for r in rows if r["violations"]][:5]:
        out.append(f"  break: {v['profile']}/{v['day']}/{v['size']}/{v['limit']}s seeded={v['seeded']}: {v['violations']}")
    print("\n".join(out))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
