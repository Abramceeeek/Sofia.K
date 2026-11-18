# The planner under realistic CPU: speed, plan quality and what the live server gives today (16 Nov 2026)

Abram's review of the audit, part 4 (12 Nov): "a reproducible performance study using realistic CPU limits… Do not improve speed by quietly returning worse plans… Do not run disruptive load tests against production." Nothing here ran against production. Everything ran on this machine (4 CPUs), with the real Brain under a Linux CPU quota.

## Findings first

1. **Feasibility held everywhere.**
   - 0 failed requests and 0 broken rules (hours, open days, own time, budget) in every scenario, at every CPU level.
   - It is checked from outside the solver with `benchmark_planner.violations`.
   - The greedy seed (m216) guarantees a valid day even when the search gets almost no time.
2. **The search is cut by wall-clock time, so less CPU means quietly worse plans, at the same speed.**
   - Each solve stops at `BRAIN_PLANNER_TIME_LIMIT_S` (1.0 s), and a day request runs several solves (the usual plan, the variety nudge, the portfolio).
   - On less CPU, a request takes about as long (4.8–5 s for a day at 1 or 0.5 CPU), but the solver gets half or a tenth of the work done.
   - **This is exactly what Abram asked not to happen.** It happens today, and the plan doesn't say so.
3. **The live Brain runs on Render's free plan: 0.1 CPU.** At 0.1 CPU, by the planner's own objective (the plan's `value`, the person's utilities less travel penalties):

| Scenario (same person, same day) | 1 CPU | 0.5 CPU | **0.1 CPU (production today)** |
|---|---|---|---|
| A day, 10:00–18:00 | 4.502 | 4.502 | **4.441 (−1%)** |
| A day with one block of own time | 4.480 | **3.221 (−28%)** | **3.221 (−28%)** |
| A day with two blocks of own time | 3.410 | 3.410 | **2.062 (−40%), 3 places, not 4** |
| A relaxed day | 3.697 | 3.697 | 3.697 |
| 8 people planning at once (each a plain day) | 4.441 | 4.441 | **4.124 (−8%)**, each waiting about 60 s |

4. **The current settings leave quality unused even on a full CPU.** With much more search, the two-block day reaches **4.418, not 3.41** (+30%: the solution-limit experiment below). The time limit was tuned for speed (m216), and own-time days are where it bites.
5. **Memory is not the constraint:** about 165–170 MB per server process with London's 49 cards, and 117 MB with 20. Render's 512 MB plans are enough.
6. **Long trips run out of places, not time.**
   - A 14-day trip plans 20 to 22 of its 28 asked-for days.
   - The rest say "A free day: nothing new fits it yet": 49 cards at about four a day last about ten days.
   - This is the catalogue, not the planner (`map-tiles-and-place-data.md`).

## What was run (reproducible)

```text
cd brain
.venv/bin/python scripts/perf_study.py --cpus 1.0 0.5 0.1 --day-runs 10 --trip-runs 3 --out benchmarks/performance/perf_study.json
.venv/bin/python scripts/perf_budget.py benchmarks/performance/search_budget.json
```

- **`perf_study.py`:**
  - It starts `uvicorn brain.api:app` inside a cgroup CPU quota (1.0, 0.5 and 0.1 of one CPU), with the production time limit (1.0 s) and no provider keys.
  - Plans use the straight-line travel estimate, as the Test B pair does.
  - It then sends real requests over HTTP. Each scenario gets its own install, since the Brain allows one phone 30 plans in 10 minutes.
  - It records latency, server CPU-seconds (from `/proc`), memory (VmRSS and VmHWM), the solver's status, places, plan value and rule breaks.
- **Scenarios:**
  - a day;
  - a day with one block of own time, and with two;
  - a relaxed day;
  - trips of 3, 7 and 14 days (14 days is two requests of at most 7, as the apps send);
  - 4 and 8 people at once;
  - a smaller destination (20 cards).
- **Runs:**
  - 10 per day scenario at 1 and 0.5 CPU, and 5 at 0.1 CPU;
  - 3 per trip (2 for 14 days).
  - **p95 is shown only where n ≥ 10, and p99 nowhere:** no scenario had the 100 runs p99 needs.
- **`perf_budget.py`:** the same requests on the full CPU with the time limit at 0.1 to 4 s. This shows what the search budget buys.

## Latency and CPU (median; p95 where n ≥ 10)

| Scenario | 1 CPU | 0.5 CPU | 0.1 CPU |
|---|---|---|---|
| A day | 4.78 s (p95 4.82); 4.7 CPU-s | 4.91 s (p95 4.99); 2.4 CPU-s | 6.59 s (n = 5); 0.66 CPU-s |
| One block of own time | 4.78 s (p95 4.84) | 4.99 s (p95 5.10) | 6.90 s |
| Two blocks of own time | 4.86 s (p95 4.89) | 5.12 s (p95 5.20) | 7.40 s |
| A relaxed day | 4.73 s (p95 4.85) | 4.90 s (p95 5.04) | 6.31 s |
| A 3-day trip | 11.3 s | 11.6 s | 14.1 s |
| A 7-day trip | 25.2 s | 25.5 s | 30.7 s |
| A 14-day trip (two requests) | 44.8 s | 45.4 s | 62.0 s |
| 4 people at once | 6.6 s each | 7.6 s | **25.2 s** |
| 8 people at once | 8.9 s each | 11.1 s | **60.0 s** |
| A day, 20-card destination | 3.11 s | 3.65 s | 4.70 s |
| Server start | 2.5 s | 4.0 s | 21.2 s |

- **The apps wait 90 s on the iPhone, and 90 or 120 s on Android.** At 0.1 CPU, eight people at once comes within a third of that.
- **Render's free server also sleeps after 15 minutes idle**, and waking "takes about one minute" (Render's docs, read 16 Nov). The first person after a quiet spell waits for that too.

## What the search budget buys (full CPU, `perf_budget.py`)

| Time limit per solve | Day | One block | Two blocks | Relaxed | Day latency |
|---|---|---|---|---|---|
| 0.1 s | 4.441 | 3.221 | 3.410 | 3.697 | 1.4 s |
| 0.2 s | 4.441 | 3.221 | 3.410 | 3.697 | 1.7 s |
| 0.5 s | 4.502 | 4.480 | 3.410 | 3.697 | 2.6 s |
| **1.0 s (today)** | 4.502 | 4.480 | 3.410 | 3.697 | 4.7 s |
| 2.0 s | 4.534 | 4.480 | 3.410 | 3.697 | 9.2 s |
| 4.0 s | 4.534 | 4.472 | 3.410 | 3.697 | 18.2 s |

- Quality moves in steps, and the steps differ by kind of day.
- 0.5 s of search on a full CPU matched 1.0 s here, but **it would be wrong to cut the limit on this evidence**: one person and four days.
- **Run to run, the same request can return a different plan.** The wall-clock stop makes results depend on the machine's load (the plain day gave 4.534 in one run and 4.502 in the next, at 1 CPU).

## The proposed fix: a fixed amount of search, with time only as a safety net (not built; for Abram)

**The idea:**
- Stop each solve after a **fixed amount of search**: OR-Tools' `solution_limit`, the number of improving solutions.
- Keep the wall-clock limit only as a **cap**, set well above the normal time.
- If the cap is reached first, the plan is still valid (the seed). It carries a status the app can show: "Planned in a hurry: tap to try again".

That way, **the same request gives the same plan on any machine**, and less CPU costs time, not quality.

**The experiment so far** (full CPU, a 30 s cap; `solution_limit` set by the experiment, not in the Brain):

| `solution_limit` | Day | One block | Two blocks | Relaxed | Day latency |
|---|---|---|---|---|---|
| 50 | 4.502 | 4.480 | 3.410 | 3.697 | 2.2 s |
| 200 | 4.534 | 4.480 | 3.410 | 3.697 | 6.4 s |
| 1000 | 4.534 | 4.472 | **4.418** | 3.697 | 30.6 s |

- **At 50 solutions:** the same quality as today's 1 s limit on a full CPU, in about half the time.
- **On 0.5 CPU,** it should be the same plans in about twice the time. **Not yet confirmed:** the run inside a 0.5 CPU quota is the first step of the work below.
- **Two blocks of own time need far more search** (1000 solutions) to find the better day. A smarter seed for own-time days is likely the cheaper fix than more search (m216's greedy seed fills around the blocks).

**The work** (Claude, about 4 h; after the friends' round, not in its build):
1. Run the 0.5 and 0.1 CPU check.
2. Set the solution limit from `benchmark_planner.py`'s full benchmark (1,188 plans), so that **no plan gets worse than today's on a full CPU** (checked plan by plan).
3. Make the cap explicit, with the "in a hurry" status shown in both apps.
4. Re-run this study.
5. Separately, about 3 h: a better seed for days with own time, judged the same way.

## What it means for the server (`infrastructure-decision.md`)

- **Without the fix:** 1 CPU (`1c-2g`, $25 a month) keeps today's plan quality. 0.5 CPU ($7) loses up to 28% on own-time days. The free plan (0.1 CPU) loses up to 40%, and makes simultaneous requests slow.
- **With the fix:** 0.5 CPU gives today's full-CPU plans, about twice as slowly (an estimate until the check runs). The free plan stays too slow for trips and simultaneous requests.
- **For the friends' round:**
  - The pair's personal plan is a plain day without own time, so it is affected least: −1% at 0.1 CPU.
  - **Trip days and own-time days are affected most.**
  - If the round hasn't started, Abram may want the server upgraded first, so every tester's plans are made on the same machine. If it has, leave it as it is until the round ends (the frozen conditions).

## Limits of this study

- **One machine** (a cloud VM with 4 CPUs) with a CPU quota. That is the same mechanism as Render's, but not Render's hardware. Production's real latency has not been measured: Abram asked that nothing disruptive run against it.
- **One simulated person** (fixed swipes and choices), on one Saturday in December.
- Quality is by the model's own objective, **not by people**. A plan's `value` is what the planner maximises, so "worse" means worse by its own measure.
- **No run reached 100 repetitions, so there is no p99.**
- **Concurrency was 4 and 8 people at once.** Render's free plan also sleeps, which this study doesn't include.

## Files

- **Scripts:**
  - `brain/scripts/perf_study.py`: the study.
  - `brain/scripts/perf_budget.py`: the budget table.
- **Results:**
  - `brain/benchmarks/performance/perf_study.json`;
  - `brain/benchmarks/performance/search_budget.json`.
- **Not committed:** the solution-limit experiment. It patches OR-Tools' parameters in memory and is described above. It becomes part of the fix's tests when that is built.
