"""Generate the Test A "this or that" day-plan design (10 paired choices).

Bayesian D-efficient design for a binary logit with weak priors (Area 3 note):
coordinate exchange over levels, several random starts, dominance and
minimum-difference checks. Pure Python so it runs anywhere (Python 3.12).

    python validation/conjoint/make_design.py        # writes design.csv next to this file

Attributes and levels confirmed by the founder on 2026-09-28 (D95): the heat factor ("hot hour outside") is replaced by
a 3-level weather factor, "weather at the outdoor stops: mild and dry / cold but dry / rainy".

    python validation/conjoint/make_design.py --report   # also prints the efficiency checks
"""
import csv
import math
import os
import random
import sys

SEED = 20260926
N_TASKS = 10
N_ALTS = 2
N_DRAWS = 64
N_STARTS = 6
MIN_DIFF = 3  # alternatives must differ on at least this many attributes

# name, levels (as shown to participants), prior sign known? (for the dominance check)
ATTRS = [
    ('transfer', ['longest transfer 15 min', 'longest transfer 30 min', 'longest transfer 50 min'], -1),
    # D95: weather at the outdoor stops. Order = known sign for the dominance check (mild best, rainy worst).
    ('weather', ['mild and dry at the outdoor stops', 'cold but dry at the outdoor stops', 'rainy at the outdoor stops'], -1),
    ('pace', ['3 stops, relaxed', '5 stops, packed'], 0),
    ('crowds', ['mostly quiet', 'busy at 2 stops'], -1),
    ('cost', ['£20 per person', '£40 per person', '£60 per person'], -1),
    ('walking', ['about 3 km walking', 'about 8 km walking'], 0),
]
# Coding: transfer dummies (30, 50 vs 15); weather dummies (cold, rain vs mild and dry); pace, crowds, walking dummies;
# cost linear per £10. The weather dummies map onto the Brain's cold_outdoor and rain_outdoor (brain/data/priors.yaml).
PARAMS = ['transfer30', 'transfer50', 'cold', 'rain', 'pace5', 'crowds', 'cost_per_10', 'walk8']
PRIOR_MEAN = [-0.3, -1.0, -0.5, -1.0, 0.0, -0.4, -0.25, 0.0]
PRIOR_SD = [0.5] * len(PARAMS)


def code(levels):
    t, wx, p, c, cost, w = levels
    return [1.0 if t == 1 else 0.0, 1.0 if t == 2 else 0.0, 1.0 if wx == 1 else 0.0, 1.0 if wx == 2 else 0.0,
            float(p), float(c), [2.0, 4.0, 6.0][cost], float(w)]


def det(m):
    m = [row[:] for row in m]
    n = len(m)
    d = 1.0
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(m[r][i]))
        if abs(m[piv][i]) < 1e-12:
            return 0.0
        if piv != i:
            m[i], m[piv] = m[piv], m[i]
            d = -d
        d *= m[i][i]
        for r in range(i + 1, n):
            f = m[r][i] / m[i][i]
            for c in range(i, n):
                m[r][c] -= f * m[i][c]
    return d


def task_info(task, beta):
    """Fisher information contribution of one paired task under binary logit."""
    x = [code(a) for a in task]
    u = [sum(b * v for b, v in zip(beta, xi)) for xi in x]
    mx = max(u)
    e = [math.exp(ui - mx) for ui in u]
    s = sum(e)
    p = [ei / s for ei in e]
    xbar = [sum(p[j] * x[j][k] for j in range(len(x))) for k in range(len(PARAMS))]
    k = len(PARAMS)
    info = [[0.0] * k for _ in range(k)]
    for j in range(len(x)):
        dx = [x[j][a] - xbar[a] for a in range(k)]
        for a in range(k):
            if dx[a] == 0.0:
                continue
            for b in range(k):
                info[a][b] += p[j] * dx[a] * dx[b]
    return info


def d_error(infos_by_draw):
    k = len(PARAMS)
    tot = 0.0
    for per_task in infos_by_draw:
        m = [[sum(t[a][b] for t in per_task) for b in range(k)] for a in range(k)]
        dt = det(m)
        if dt <= 0:
            return float('inf')
        tot += dt ** (-1.0 / k)
    return tot / len(infos_by_draw)


def valid(task):
    a, b = task
    if sum(x != y for x, y in zip(a, b)) < MIN_DIFF:
        return False
    # dominance: one alternative weakly better on every signed attribute and equal on unsigned ones
    better_a = better_b = True
    for (name, _, sign), x, y in zip(ATTRS, a, b):
        if sign == 0:
            if x != y:
                better_a = better_b = False
        else:  # sign -1: lower level index is better
            if x > y:
                better_a = False
            if y > x:
                better_b = False
    return not (better_a or better_b)


def random_task(rng):
    while True:
        t = tuple(tuple(rng.randrange(len(lv)) for (_, lv, _) in ATTRS) for _ in range(N_ALTS))
        if valid(t):
            return t


def search(rng, draws, n_tasks, n_starts, verbose=True):
    """Coordinate exchange from several random starts; returns (best design, its Bayesian D-error)."""
    best, best_err = None, float('inf')
    for start in range(n_starts):
        design = [random_task(rng) for _ in range(n_tasks)]
        infos = [[task_info(t, beta) for t in design] for beta in draws]
        err = d_error(infos)
        improved = True
        while improved:
            improved = False
            for ti in range(n_tasks):
                for ai in range(N_ALTS):
                    for at in range(len(ATTRS)):
                        for lv in range(len(ATTRS[at][1])):
                            cand = [list(alt) for alt in design[ti]]
                            if cand[ai][at] == lv:
                                continue
                            cand[ai][at] = lv
                            cand = tuple(tuple(alt) for alt in cand)
                            if not valid(cand) or cand in design:
                                continue
                            new_infos = [row[:ti] + [task_info(cand, beta)] + row[ti + 1:]
                                         for row, beta in zip(infos, draws)]
                            new_err = d_error(new_infos)
                            if new_err < err - 1e-9:
                                design[ti], infos, err = cand, new_infos, new_err
                                improved = True
        if verbose:
            print(f'start {start + 1}: Bayesian D-error {err:.4f}')
        if err < best_err:
            best, best_err = list(design), err
    return best, best_err


def inverse(m):
    n = len(m)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[piv] = a[piv], a[i]
        d = a[i][i]
        a[i] = [v / d for v in a[i]]
        for r in range(n):
            if r != i and a[r][i] != 0.0:
                f = a[r][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    return [row[n:] for row in a]


def report(best, best_err, draws):
    """Efficiency checks (D95): expected standard errors for the Test A sample, and 10 vs 12 tasks."""
    k = len(PARAMS)
    info = [[sum(t[a][b] for t in (task_info(task, PRIOR_MEAN) for task in best)) for b in range(k)] for a in range(k)]
    for n_people in (1, 12):
        cov = inverse([[v * n_people for v in row] for row in info])
        ses = [math.sqrt(cov[i][i]) for i in range(k)]
        print(f'  expected SE with {n_people:>2} people x {len(best)} tasks (at the prior mean): '
              + ', '.join(f'{p} {se:.2f}' for p, se in zip(PARAMS, ses)))
    rng = random.Random(SEED + 1)
    _, err_more = search(rng, draws, len(best), 20, verbose=False)
    print(f'  the same search from 20 starts: best D-error {err_more:.4f} (this design {best_err:.4f}, '
          f'{100 * err_more / best_err:.0f}% efficient against it)')
    _, err12 = search(random.Random(SEED + 2), draws, 12, N_STARTS, verbose=False)
    print(f'  with 12 tasks instead of 10: D-error {err12:.4f} ({100 * (1 - err12 / best_err):.0f}% lower)')


def main():
    rng = random.Random(SEED)
    draws = [[rng.gauss(m, s) for m, s in zip(PRIOR_MEAN, PRIOR_SD)] for _ in range(N_DRAWS)]
    best, best_err = search(rng, draws, N_TASKS, N_STARTS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'design.csv')
    with open(out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['task', 'plan'] + [a[0] for a in ATTRS] + ['description'])
        for ti, task in enumerate(best, 1):
            for ai, alt in enumerate(task):
                desc = '; '.join(ATTRS[k][1][lv] for k, lv in enumerate(alt))
                w.writerow([ti, 'AB'[ai]] + [ATTRS[k][1][lv] for k, lv in enumerate(alt)] + [desc])
    print(f'best Bayesian D-error {best_err:.4f}; wrote {out}')
    for k, (name, lv, _) in enumerate(ATTRS):
        counts = [sum(1 for t in best for alt in t if alt[k] == i) for i in range(len(lv))]
        print(f'  level balance {name}: {counts}')
    pairs = {}
    for a, b in best:
        key = tuple(sorted((a[1], b[1])))
        pairs[key] = pairs.get(key, 0) + 1
    print('  weather pairs within tasks (level indices):', dict(sorted(pairs.items())))
    if '--report' in sys.argv:
        report(best, best_err, draws)


if __name__ == '__main__':
    main()
