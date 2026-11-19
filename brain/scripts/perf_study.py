"""Performance study under real CPU limits (audit; Abram, 12 Nov 2026; decisions/performance-study.md).

Run from brain/ with the venv, as root on Linux (it needs cgroups to cap the CPU):
    .venv/bin/python scripts/perf_study.py --cpus 1.0 0.5 0.1 --out benchmarks/performance/perf_study.json

What it does, for each CPU limit:
- starts the real server (`uvicorn brain.api:app`) on a throwaway SQLite database with the ready cards, inside a
  Linux cgroup whose CPU quota is that many processors (0.1 is Render's free plan and its smallest paid database's
  size; 0.5 its Starter web service; 1.0 its Standard), with the planner's production time limit (1.0 s);
- makes one install that answers the short onboarding the same way every time;
- times each scenario from outside the server: a day (10:00-18:00, five stops), a day with the person's own time
  (one block, then two), a relaxed day, trips of 3, 7 and 14 days (14 days is two requests, as the apps do), the same
  day on a catalogue of 20 cards (a smaller destination), and 4 and 8 people asking for a plan at once;
- checks every day plan it gets back against the planner's hard rules from outside the solver (the benchmark's own
  `violations`: inside the day, no overlaps, opening hours and days, no card twice, the day's shape, the budget, the
  person's own time kept), and records the plan's value, so a faster or slower machine can't quietly give worse
  plans unnoticed;
- reads the server's peak memory and the CPU seconds it used from /proc.

Nothing here touches production, a provider or the network: the server runs locally with no keys (sample flights
and stays, the straight-line London travel estimate, no forecast). Percentiles are reported only where the sample
supports them: p95 from 10 requests is the slowest but one, and p99 is never claimed below 100 requests.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "src"))
sys.path.insert(0, str(HERE))

from brain.config import DATA_DIR  # noqa: E402
from brain.dayplan import Block, Brief  # noqa: E402
from brain.moments import Point, load_moments  # noqa: E402

from benchmark_planner import Stop, violations  # noqa: E402

CGROUP_V1 = Path("/sys/fs/cgroup/cpu")
START = {"lat": 51.507819, "lon": -0.126137}
DATE = "2026-12-05"               # a Saturday; the plans use the straight-line estimate, so the date only sets hours
DAY = {"start": START, "start_name": "Charing Cross station", "start_time": "10:00", "end_time": "18:00",
       "stops": 5, "date": DATE, "conditions": {"temp_c": 10.0, "rain_prob": 0.1}}
ONE_BLOCK = [{"kind": "plans", "start": "14:00", "end": "15:30", "location": "near", "meal": False}]
TWO_BLOCKS = ONE_BLOCK + [{"kind": "free", "start": "16:45", "end": "17:15", "location": "unknown", "meal": False}]
SWIPES = [(4, "loved"), (6, "fine"), (11, "didnt_enjoy"), (12, "loved"), (13, "fine"), (14, "loved")]
CHOICES = [(2, "A"), (4, "B"), (6, "A"), (8, "B"), (9, "A")]
STAY = {"lat": 51.5111, "lon": -0.1221}


def mins(t: str) -> int:
    return int(t[:2]) * 60 + int(t[3:5])


def pct(xs: list[float], q: float) -> float:
    s = sorted(xs)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]


def summary(xs: list[float]) -> dict:
    out = {"n": len(xs), "median_s": round(statistics.median(xs), 2), "max_s": round(max(xs), 2)}
    if len(xs) >= 10:
        out["p95_s"] = round(pct(xs, 0.95), 2)
    if len(xs) >= 100:
        out["p99_s"] = round(pct(xs, 0.99), 2)
    return out


class Server:
    """The real server, in its own cgroup with a CPU quota."""

    def __init__(self, cpus: float, data_dir: Path, port: int, workdir: Path):
        self.cpus, self.port = cpus, port
        self.group = CGROUP_V1 / f"odysperf_{int(cpus * 100)}"
        self.group.mkdir(exist_ok=True)
        (self.group / "cpu.cfs_period_us").write_text("100000")
        (self.group / "cpu.cfs_quota_us").write_text(str(int(100000 * cpus)))
        env = {**os.environ, "BRAIN_DATABASE_URL": f"sqlite:///{workdir / f'perf_{port}.db'}",
               "BRAIN_DATA_DIR": str(data_dir), "BRAIN_PLANNER_TIME_LIMIT_S": "1.0"}
        for k in ("DUFFEL_ACCESS_TOKEN", "LITEAPI_KEY", "TFL_APP_KEY", "MET_OFFICE_API_KEY"):
            env.pop(k, None)
        cmd = (f"echo $$ > {self.group / 'cgroup.procs'}; exec {sys.executable} -m uvicorn brain.api:app "
               f"--app-dir {HERE.parents[0] / 'src'} --port {port} --no-access-log --log-level warning")
        t0 = time.perf_counter()
        self.proc = subprocess.Popen(["sh", "-c", cmd], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.base = f"http://127.0.0.1:{port}"
        while True:
            try:
                if httpx.get(self.base + "/v1/health", timeout=5).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.2)
            if time.perf_counter() - t0 > 300:
                raise RuntimeError("the server didn't start")
        self.startup_s = round(time.perf_counter() - t0, 2)

    def cpu_seconds(self) -> float:
        f = Path(f"/proc/{self.proc.pid}/stat").read_text().rsplit(")", 1)[1].split()
        return (int(f[11]) + int(f[12])) / os.sysconf("SC_CLK_TCK")

    def memory_mb(self) -> dict:
        s = Path(f"/proc/{self.proc.pid}/status").read_text()
        kb = lambda k: int(s.split(k + ":")[1].split()[0])
        return {"rss_mb": round(kb("VmRSS") / 1024), "peak_mb": round(kb("VmHWM") / 1024)}

    def stop(self) -> None:
        self.proc.terminate()
        self.proc.wait(timeout=30)
        try:
            self.group.rmdir()
        except OSError:
            pass


def install(base: str, n: int) -> dict:
    r = httpx.post(base + "/v1/installs", json={"consent": {"version": "perf", "research": True}},
                   headers={"X-Forwarded-For": f"198.51.100.{n % 250}"}, timeout=120)
    r.raise_for_status()
    h = {"Authorization": "Bearer " + r.json()["token"]}
    httpx.post(base + "/v1/me/swipes", headers=h, timeout=300,
               json={"items": [{"item": i, "reaction": x} for i, x in SWIPES]}).raise_for_status()
    httpx.post(base + "/v1/me/conjoint", headers=h, timeout=300,
               json={"items": [{"task": t, "choice": c} for t, c in CHOICES]}).raise_for_status()
    return h


def brief_of(req: dict) -> Brief:
    blocks = tuple(Block(b["kind"], mins(b["start"]), mins(b["end"]), b["location"], b["meal"])
                   for b in req.get("mine", []))
    return Brief(start_name=req["start_name"], start=Point(**req["start"]), start_time=req["start_time"],
                 end_time=req["end_time"], stops=req["stops"], weekday="sat", rain_prob=req["conditions"]["rain_prob"],
                 temp_c=req["conditions"]["temp_c"], mine=blocks, relaxed=req.get("relaxed", False))


def check_day(plan: dict, req: dict, by_id: dict) -> dict:
    stops = [Stop(s["moment_id"], mins(s["arrive"]), mins(s["depart"]) if s.get("depart") else
                  mins(s["arrive"]) + 45, s.get("travel_min") or 0) for s in plan["stops"]]
    broken = violations(stops, brief_of(req), by_id, 15.0)
    places = sum(1 for s in plan["stops"] if s.get("rateable"))
    return {"broken": broken, "places": places, "value": plan.get("value"), "status": plan.get("solver_status")}


def timed(fn) -> tuple[float, httpx.Response]:
    t0 = time.perf_counter()
    r = fn()
    return time.perf_counter() - t0, r


def run_level(cpus: float, data_dir: Path, by_id: dict, port: int, n_day: int, n_trip: int, workdir: Path,
              label: str = "London, 49 cards") -> dict:
    srv = Server(cpus, data_dir, port, workdir)
    out = {"cpus": cpus, "catalogue": label, "startup_s": srv.startup_s, "scenarios": {}}
    try:
        h = install(srv.base, 1)
        httpx.post(srv.base + "/v1/me/plans", headers=h, json=DAY, timeout=600)   # warm-up, not counted

        def day_scenario(name: str, req: dict, n: int, k: int) -> None:
            # a fresh install each: the Brain allows one phone 30 plans in 10 minutes (ops.LIMITS["plan"])
            h = install(srv.base, 200 + k)
            c0, lat, checks, codes = srv.cpu_seconds(), [], [], []
            for _ in range(n):
                dt, r = timed(lambda: httpx.post(srv.base + "/v1/me/plans", headers=h, json=req, timeout=600))
                lat.append(dt)
                codes.append(r.status_code)
                if r.status_code == 201:
                    checks.append(check_day(r.json(), req, by_id))
            out["scenarios"][name] = {
                **summary(lat), "failed": sum(c != 201 for c in codes), "failure_codes": sorted({c for c in codes if c != 201}),
                "cpu_s_per_request": round((srv.cpu_seconds() - c0) / n, 2),
                "rule_breaks": sum(len(c["broken"]) for c in checks),
                "places_median": statistics.median(c["places"] for c in checks) if checks else None,
                "value_median": round(statistics.median(c["value"] for c in checks if c["value"] is not None), 3)
                if checks else None,
                "solver_not_ok": sum(c["status"] != "ok" for c in checks)}

        day_scenario("day", DAY, n_day, 1)
        if label.startswith("London"):
            day_scenario("day, one block of own time", {**DAY, "mine": ONE_BLOCK}, n_day, 2)
            day_scenario("day, two blocks of own time", {**DAY, "mine": TWO_BLOCKS}, n_day, 3)
            day_scenario("relaxed day", {**DAY, "relaxed": True, "stops": 4}, n_day, 4)

            def trip(nights: int, n: int) -> None:
                c0, lat, planned, asked, codes = srv.cpu_seconds(), [], [], [], []
                for k in range(n):
                    th = install(srv.base, 10 + nights * 10 + k)
                    body = {"start_date": DATE, "nights": nights, "stay": STAY, "stay_name": "A stay",
                            "day_start": "10:00", "day_end": "18:00", "stops_per_day": 4}
                    total, got, t_all, used = nights + 1, 0, 0.0, []
                    for first in range(0, total, 7):          # the apps ask for at most seven days at a time
                        days = list(range(first, min(total, first + 7)))
                        dt, r = timed(lambda: httpx.post(srv.base + "/v1/me/trips/days", headers=th, timeout=900,
                                                         json={**body, "days": days, "exclude": used}))
                        t_all += dt
                        codes.append(r.status_code)
                        if r.status_code == 201:
                            got += sum(e["plan"] is not None for e in r.json()["days"])
                            used = r.json()["used"]
                    lat.append(t_all)
                    planned.append(got)
                    asked.append(total)
                out["scenarios"][f"trip of {nights + 1} days"] = {
                    **summary(lat), "failed": sum(c != 201 for c in codes), "failure_codes": sorted({c for c in codes if c != 201}),
                    "cpu_s_per_trip": round((srv.cpu_seconds() - c0) / n, 2),
                    "days_planned": f"{sum(planned)} of {sum(asked)}"}

            trip(2, n_trip)
            trip(6, n_trip)
            trip(13, max(1, n_trip - 1))

            for k in (4, 8):
                hs = [install(srv.base, 100 + k * 10 + i) for i in range(k)]
                c0 = srv.cpu_seconds()
                with ThreadPoolExecutor(k) as ex:
                    res = list(ex.map(lambda hh: timed(lambda: httpx.post(srv.base + "/v1/me/plans", headers=hh,
                                                                          json=DAY, timeout=900)), hs))
                lat = [dt for dt, _ in res]
                checks = [check_day(r.json(), DAY, by_id) for _, r in res if r.status_code == 201]
                out["scenarios"][f"{k} people at once"] = {
                    "n": k, "median_s": round(statistics.median(lat), 2), "max_s": round(max(lat), 2),
                    "failed": sum(r.status_code != 201 for _, r in res),
                    "cpu_s_total": round(srv.cpu_seconds() - c0, 2),
                    "rule_breaks": sum(len(c["broken"]) for c in checks),
                    "value_median": round(statistics.median(c["value"] for c in checks), 3) if checks else None}
        out.update(srv.memory_mb())
    finally:
        srv.stop()
    return out


def small_catalogue(workdir: Path, n: int = 20) -> tuple[Path, dict]:
    """A copy of the data with only `n` ready cards (the first by id), as a smaller destination would have."""
    d = workdir / "data_small"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(DATA_DIR, d)
    ready = sorted(m.id for m in load_moments(d / "moments") if m.status == "ready")
    keep = set(ready[:n])
    for f in (d / "moments").glob("*.yaml"):
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        if isinstance(doc, dict) and doc.get("id") not in keep:
            f.unlink()
    return d, {m.id: m for m in load_moments(d / "moments")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cpus", type=float, nargs="+", default=[1.0, 0.5, 0.1])
    ap.add_argument("--day-runs", type=int, default=10)
    ap.add_argument("--trip-runs", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if not (CGROUP_V1 / "cpu.cfs_quota_us").exists():
        print("needs Linux cgroup v1's cpu controller (run as root)", file=sys.stderr)
        return 1
    workdir = Path(tempfile.mkdtemp(prefix="odysperf"))
    by_id = {m.id: m for m in load_moments(DATA_DIR / "moments")}
    small_dir, small_by_id = small_catalogue(workdir)
    results = {"made_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "machine_cpus": os.cpu_count(),
               "planner_time_limit_s": 1.0, "levels": []}
    for i, cpus in enumerate(a.cpus):
        n_day = a.day_runs if cpus >= 0.5 else max(5, a.day_runs // 2)
        results["levels"].append(run_level(cpus, DATA_DIR, by_id, 8800 + i, n_day, a.trip_runs, workdir))
        results["levels"].append(run_level(cpus, small_dir, small_by_id, 8900 + i, n_day, a.trip_runs, workdir,
                                           label="a smaller destination, 20 cards"))
        print(json.dumps(results["levels"][-2:], indent=1), flush=True)
    shutil.rmtree(workdir, ignore_errors=True)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
