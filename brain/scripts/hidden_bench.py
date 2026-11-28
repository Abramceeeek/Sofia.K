"""The hidden-preference bench (batch 9, m364, work C): does the engine recover tastes it was never shown?

Usage:
  python scripts/hidden_bench.py run [--brain-src DIR] --out FILE.json    # one engine, every synthetic traveller
  python scripts/hidden_bench.py report OLD.json NEW.json --out FILE.md  # side by side, with the baselines

**Synthetic travellers, never evidence about people.** Each has a hidden taste (`hidden_truth.py`, which imports
nothing from the Brain), answers onboarding through the app's own API with noise and gaps, and is then judged by the
engine's `GET /v1/me/matches`. The engine's ranking is compared with the hidden truth on the places the traveller
never swiped (held out).

`--brain-src` runs another commit's engine (a worktree's `brain/src`), so the old and new engines meet the same
travellers. The hidden truth always comes from this checkout's data, so both are judged against the same answers.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import hidden_truth as truth  # noqa: E402

N_EACH = 4                  # travellers per archetype (40 in all)
DATE = "2026-12-04"         # a Friday, as the engine bench
TOP = 10
RECOMMENDED = ("must_go", "strong_match", "good_discovery")


def _ranks(xs: list[float]) -> np.ndarray:
    order = np.argsort(xs, kind="stable")
    r = np.empty(len(xs))
    r[order] = np.arange(len(xs))
    return r


def spearman(a: list[float], b: list[float]) -> float:
    if len(a) < 3:
        return float("nan")
    ra, rb = _ranks(a), _ranks(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def run(brain_src: Path, out: Path, first: int = 0) -> None:
    sys.path.insert(0, str(brain_src))
    from fastapi.testclient import TestClient
    import brain.ops as ops
    from brain.api import create_app
    from brain.config import Settings
    data_dir = brain_src.parent / "data"
    ops.LIMITS["install"] = (100000, 3600)   # one install per synthetic traveller, in this in-memory app only
    places, items, shown = truth.load_world(ROOT / "data")
    tmp = tempfile.mkdtemp()
    settings = Settings(database_url=f"sqlite:///{tmp}/hb.db", data_dir=data_dir, admin_token="x",
                        alert_webhook_url=None, planner_time_limit_s=0.5)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=brain_src, text=True).strip()
    except Exception:  # noqa: BLE001
        commit = "unknown"
    rows = []
    with TestClient(create_app(settings)) as c:
        def install():
            r = c.post("/v1/installs", json={"channel": "stranger", "src": "hidden-bench",
                                             "consent": {"version": "2026-09", "research": True,
                                                         "ai_processing": False}})
            return {"Authorization": f"Bearer {r.json()['token']}"}

        def matches(h, kids=()):
            q = f"date={DATE}" + (f"&children={','.join(map(str, kids))}" if kids else "")
            r = c.get(f"/v1/me/matches?{q}", headers=h)
            assert r.status_code == 200, r.text
            return r.json()["matches"]

        pop_rank = [m["place"] for m in matches(install())]   # the population's own ranking: nobody's answers
        for arch in truth.ARCHETYPES:
            for n in range(first, first + N_EACH):
                hid = truth.make_traveller(arch, n, places)
                obs = truth.observe(hid, places, items, shown)
                h = install()
                assert c.put("/v1/me/profile", headers=h, json=obs["profile"]).status_code == 204
                c.post("/v1/me/swipes", headers=h,
                       json={"items": [{"item": i, "reaction": r} for i, r in obs["swipes"].items()]})
                ob = c.get("/v1/onboarding", headers=h).json()
                rng = np.random.default_rng(obs["flip_seed"])
                picks = [{"task": t["task"], "choice": truth.choose(t, obs["prefers"], rng)}
                         for t in ob["conjoint_tasks"]]
                c.post("/v1/me/conjoint", headers=h, json={"items": picks})
                ms = matches(h, obs["children"])
                seen = {cid for i, r in obs["swipes"].items() if r != "havent_been" for cid in items.get(i, [])}
                disliked = {cid for i, r in obs["swipes"].items() if r == "didnt_enjoy" for cid in items.get(i, [])}
                rows.append({
                    "key": hid.key, "archetype": arch, "taste": hid.taste,
                    "truth": {pid: round(hid.enjoy(p), 4) for pid, p in places.items()},
                    "seen": sorted(seen), "disliked": sorted(disliked), "swipes": obs["swipes"],
                    "fields": obs["profile"]["fields"], "prefers": obs["prefers"],
                    "judged": [{"place": m["place"], "class": m["class"], "score": m["score"],
                                "level": (m.get("confidence") or {}).get("level"),
                                "hard": bool(m.get("restrictions")) and not any(
                                    "didn't enjoy" in r or "kinds they" in r for r in m["restrictions"]),
                                "reason": m.get("reason"), "against": m.get("against"),
                                "model_score": m.get("model_score"), "basis": m.get("basis"),
                                "ratio": (m.get("confidence") or {}).get("predictive_ratio"),
                                "coverage": (m.get("confidence") or {}).get("coverage_of_main_appeals"),
                                "why_low": (m.get("confidence") or {}).get("why_low")} for m in ms]})
    out.write_text(json.dumps({"commit": commit, "brain_src": str(brain_src), "date": DATE, "n_each": N_EACH,
                               "first": first,
                               "population_rank": pop_rank, "travellers": rows}, indent=1))
    print(f"{len(rows)} travellers judged by the engine at {commit}; written {out}")


def measures(d: dict, *, ranking: str = "engine", seed: int = 0) -> dict:
    """The recovery measures for one run. `ranking`: the engine's own, the population's, or random."""
    rng = np.random.default_rng(seed)
    rhos, prec, poor_ok, low_top, poor_top, disliked_top, err_by = [], [], [], [], [], [], {}
    tops = {}
    for t in d["travellers"]:
        tr = t["truth"]
        judged = [j for j in t["judged"] if j["place"] in tr]
        # the held-out places: never swiped, and no hard rule (a closed day, an age rule) on them
        held = [j for j in judged if j["place"] not in set(t["seen"]) and not j["hard"]]
        if ranking == "population":
            order = [p for p in d["population_rank"] if p in {j["place"] for j in held}]
        elif ranking == "random":
            order = [j["place"] for j in held]
            rng.shuffle(order)
        else:
            order = [j["place"] for j in held]          # the engine's own order (rank(): class, then score)
        pos = {p: i for i, p in enumerate(order)}
        u = [tr[p] for p in order]
        rhos.append(spearman([-pos[p] for p in order], u))
        q75 = np.quantile(list(tr.values()), 0.75)
        median = np.median(list(tr.values()))
        top = order[:TOP]
        tops[t["key"]] = set(top)
        prec.append(sum(tr[p] >= q75 for p in top) / max(1, len(top)))
        if ranking == "engine":
            cls = {j["place"]: j for j in held}
            poor = [p for p in order if cls[p]["class"] == "poor_match"]
            low = [p for p in order if cls[p]["class"] == "low_confidence"]
            if poor:
                poor_ok.append(sum(tr[p] < median for p in poor) / len(poor))
                poor_top.append(sum(tr[p] >= q75 for p in poor) / len(poor))
            if low:
                low_top.append(sum(tr[p] >= q75 for p in low) / len(low))
            # honest uncertainty: how far the engine's score is from the truth, by its own confidence level
            sc = [cls[p]["score"] for p in order]
            zs = (np.array(sc) - np.mean(sc)) / (np.std(sc) or 1)
            zu = (np.array(u) - np.mean(u)) / (np.std(u) or 1)
            for p, a, b in zip(order, zs, zu):
                err_by.setdefault(cls[p]["level"] or "none", []).append(abs(a - b))
            rec = [j["place"] for j in t["judged"] if j["class"] in RECOMMENDED][:TOP]
            disliked_top.append(int(bool(set(rec) & set(t["disliked"]))))
    # diversity, and whether two travellers' overlap tracks how alike their hidden tastes are
    keys = list(tops)
    by_key = {t["key"]: t for t in d["travellers"]}
    ov, sim = [], []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ov.append(len(tops[a] & tops[b]) / TOP)
            ta, tb = by_key[a]["taste"], by_key[b]["taste"]
            ks = [k for k in ta if k in tb]
            x = np.array([ta[k] for k in ks]) - truth.BASE
            y = np.array([tb[k] for k in ks]) - truth.BASE
            sim.append(float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y))))
    out = {"spearman_mean": float(np.nanmean(rhos)), "spearman_by_archetype": {},
           "top10_precision": float(np.mean(prec)), "overlap_mean": float(np.mean(ov)),
           "overlap_tracks_similarity": float(np.corrcoef(ov, sim)[0, 1]) if len(ov) > 2 else None}
    arch = [t["archetype"] for t in d["travellers"]]
    for a in dict.fromkeys(arch):
        out["spearman_by_archetype"][a] = float(np.nanmean([r for r, x in zip(rhos, arch) if x == a]))
    if ranking == "engine":
        out.update({
            "poor_truly_below_median": float(np.mean(poor_ok)) if poor_ok else None,
            "poor_truly_top_quarter": float(np.mean(poor_top)) if poor_top else None,
            "low_confidence_truly_top_quarter": float(np.mean(low_top)) if low_top else None,
            "error_by_confidence": {k: round(float(np.mean(v)), 3) for k, v in sorted(err_by.items())},
            "n_by_confidence": {k: len(v) for k, v in sorted(err_by.items())},
            "disliked_place_recommended": int(sum(disliked_top)),
            "classes": _class_counts(d)})
    return out


def _class_counts(d: dict) -> dict:
    out: dict[str, int] = {}
    for t in d["travellers"]:
        for j in t["judged"]:
            out[j["class"]] = out.get(j["class"], 0) + 1
    return out


def report(old: Path, new: Path, out: Path) -> None:
    a, b = json.loads(old.read_text()), json.loads(new.read_text())
    ma, mb = measures(a), measures(b)
    pop, rnd = measures(b, ranking="population"), measures(b, ranking="random", seed=7)
    f = lambda v: "–" if v is None else f"{v:.2f}" if isinstance(v, float) else str(v)  # noqa: E731
    L = [f"# Hidden-preference bench: old engine `{a['commit']}` against new `{b['commit']}`", "",
         "**Synthetic travellers only, never evidence about people.** "
         f"{len(b['travellers'])} travellers ({b['n_each']} for each of {len(truth.ARCHETYPES)} archetypes), each "
         "with a hidden taste from `scripts/hidden_truth.py` (it imports nothing from the Brain), answering onboarding "
         "through the app's API with noise and gaps. Measured on the places each one never swiped, with hard rules "
         f"(a closed day, an age rule) left out. Friday {b['date']}. Raw results: the two JSON files beside this one.", "",
         "| Measure | Random | Population only | Old engine | New engine | Better is |", "|---|---|---|---|---|---|",
         f"| Rank correlation with the hidden truth (mean Spearman) | {f(rnd['spearman_mean'])} | "
         f"{f(pop['spearman_mean'])} | {f(ma['spearman_mean'])} | {f(mb['spearman_mean'])} | higher |",
         f"| Top-10 precision (share in the traveller's true top quarter) | {f(rnd['top10_precision'])} | "
         f"{f(pop['top10_precision'])} | {f(ma['top10_precision'])} | {f(mb['top10_precision'])} | higher |",
         f"| Mean top-10 overlap between two travellers | {f(rnd['overlap_mean'])} | {f(pop['overlap_mean'])} | "
         f"{f(ma['overlap_mean'])} | {f(mb['overlap_mean'])} | relevance, not difference |",
         f"| Overlap tracks hidden similarity (correlation) | {f(rnd['overlap_tracks_similarity'])} | – | "
         f"{f(ma['overlap_tracks_similarity'])} | {f(mb['overlap_tracks_similarity'])} | higher |",
         f"| Poor matches truly below the traveller's median | – | – | {f(ma['poor_truly_below_median'])} | "
         f"{f(mb['poor_truly_below_median'])} | higher |",
         f"| Poor matches truly in their top quarter (wrongly called poor) | – | – | "
         f"{f(ma['poor_truly_top_quarter'])} | {f(mb['poor_truly_top_quarter'])} | lower |",
         f"| Low-confidence places truly in their top quarter (base rate 0.25) | – | – | "
         f"{f(ma['low_confidence_truly_top_quarter'])} | {f(mb['low_confidence_truly_top_quarter'])} | near 0.25: "
         "unknown, not bad |",
         f"| Travellers with a place they didn't enjoy in their top 10 recommended | – | – | "
         f"{ma['disliked_place_recommended']} | {mb['disliked_place_recommended']} | 0 |", "",
         "**Honest uncertainty:** the gap between the engine's standardised score and the truth, by its own "
         "confidence level (lower is closer). If confidence means something, low should show the largest gap.", "",
         "| Confidence | Old: gap (n) | New: gap (n) |", "|---|---|---|"]
    for lvl in ("low", "medium", "high"):
        L.append(f"| {lvl} | {f(ma['error_by_confidence'].get(lvl))} ({ma['n_by_confidence'].get(lvl, 0)}) | "
                 f"{f(mb['error_by_confidence'].get(lvl))} ({mb['n_by_confidence'].get(lvl, 0)}) |")
    L += ["", "**By archetype (mean Spearman):**", "", "| Archetype | Population | Old | New |", "|---|---|---|---|"]
    for k in truth.ARCHETYPES:
        L.append(f"| {k} | {f(pop['spearman_by_archetype'].get(k))} | {f(ma['spearman_by_archetype'].get(k))} | "
                 f"{f(mb['spearman_by_archetype'].get(k))} |")
    L += ["", "**Classes over every judgement:**", "", "| Class | Old | New |", "|---|---|---|"]
    for k in ("must_go", "strong_match", "good_discovery", "low_confidence", "poor_match", "not_suitable"):
        L.append(f"| {k} | {ma['classes'].get(k, 0)} | {mb['classes'].get(k, 0)} |")
    L += ["", "**What this can and can't show:**",
          "- The truth is Claude's own construction (kinds and words to hidden attributes, GUESS weights). It's "
          "independent of the engine's code, not of Claude's judgement; a real traveller is the only real test.",
          "- The engine sees only a handful of noisy answers; the place-by-place part of the truth "
          f"(sd {truth.PLACE_SD}) is unrecoverable by design, so no engine should reach 1.",
          "- Hidden tastes the person model has no feature for (art, science, shopping, nightlife, architecture) can "
          "be recovered only through places they loved or disliked."]
    out.write_text("\n".join(L) + "\n")
    print(f"written {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--brain-src", default=str(ROOT / "src"))
    r.add_argument("--out", required=True)
    r.add_argument("--first", type=int, default=0, help="the first traveller number (fresh travellers: 4)")
    p = sub.add_parser("report")
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "run":
        run(Path(a.brain_src).resolve(), Path(a.out), a.first)
    else:
        report(Path(a.old), Path(a.new), Path(a.out))


if __name__ == "__main__":
    main()
