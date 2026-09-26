"""δ_person: one person's deviation from the population weights (Areas 3 and 17).

Self-contained on purpose: numpy only, no database, no other brain modules. The same maths
can later run on the phone (Area 17), with the server sending b_population, the cutpoints
and the moment features.

Model. For each observation the linear predictor is
    η = λ_source · x · (b_pop + δ)        (δ acts only on the personal features)
with three likelihood blocks sharing δ (Area 3):
    - conjoint choice:  binary logit on x = x_A − x_B, y = 1 if A was chosen;
    - swipe reaction:   ordered logit, 3 levels (didn't enjoy < fine < loved);
    - stop rating:      ordered logit, 5 levels (1-5).
Prior δ ~ N(0, diag(sd²)). Hyperparameters (b_pop, cutpoints, λ) are held fixed, and the
posterior is the Laplace approximation around the MAP, found by Newton's method.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Observation:
    x: np.ndarray                   # full feature vector (all model features, model order)
    y: int                          # binary: 0/1; ordered: 0..K-1
    scale: float = 1.0              # λ for this data source
    cutpoints: tuple[float, ...] | None = None  # None = binary logit


@dataclass(frozen=True)
class DeltaPosterior:
    mean: np.ndarray        # δ̂ on the personal features
    precision: np.ndarray   # −Hessian of the log posterior at δ̂
    iterations: int
    n_obs: int

    def covariance(self) -> np.ndarray:
        return np.linalg.inv(self.precision)

    def sd(self) -> np.ndarray:
        return np.sqrt(np.diag(self.covariance()))

    def to_json(self) -> dict:
        return {"mean": self.mean.tolist(), "precision": self.precision.tolist(),
                "iterations": self.iterations, "n_obs": self.n_obs}

    @staticmethod
    def from_json(d: dict) -> "DeltaPosterior":
        return DeltaPosterior(np.array(d["mean"], dtype=float), np.array(d["precision"], dtype=float),
                              int(d.get("iterations", 0)), int(d.get("n_obs", 0)))


def prior_only(prior_sd: np.ndarray) -> DeltaPosterior:
    return DeltaPosterior(np.zeros(len(prior_sd)), np.diag(1.0 / prior_sd ** 2), 0, 0)


# ---- logistic helpers ---------------------------------------------------------------

def _F(z: float) -> float:
    if z == math.inf:
        return 1.0
    if z == -math.inf:
        return 0.0
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def _f(z: float) -> float:
    if math.isinf(z):
        return 0.0
    p = _F(z)
    return p * (1.0 - p)


def _fprime(z: float) -> float:
    if math.isinf(z):
        return 0.0
    p = _F(z)
    return p * (1.0 - p) * (1.0 - 2.0 * p)


def loglik_terms(eta: float, obs: Observation) -> tuple[float, float, float]:
    """log p(y | η) and its first and second derivatives with respect to η."""
    if obs.cutpoints is None:
        p = _F(eta)
        ll = math.log(max(p if obs.y == 1 else 1.0 - p, 1e-300))
        return ll, obs.y - p, -p * (1.0 - p)
    c = (-math.inf, *obs.cutpoints, math.inf)
    if not 0 <= obs.y < len(c) - 1:
        raise ValueError(f"ordered outcome {obs.y} out of range for {len(c) - 1} levels")
    b = c[obs.y + 1] - eta   # upper threshold
    a = c[obs.y] - eta       # lower threshold
    P = max(_F(b) - _F(a), 1e-300)
    dP = -_f(b) + _f(a)
    d2P = _fprime(b) - _fprime(a)
    d1 = dP / P
    return math.log(P), d1, d2P / P - d1 * d1


def log_posterior(delta: np.ndarray, b_pop: np.ndarray, personal_idx: np.ndarray,
                  prior_sd: np.ndarray, observations: list[Observation]) -> float:
    b = b_pop.copy()
    b[personal_idx] += delta
    lp = -0.5 * float(np.sum((delta / prior_sd) ** 2))
    for o in observations:
        lp += loglik_terms(o.scale * float(o.x @ b), o)[0]
    return lp


def fit_delta(b_pop: np.ndarray, personal_idx: np.ndarray, prior_sd: np.ndarray,
              observations: list[Observation], max_iter: int = 50, tol: float = 1e-9) -> DeltaPosterior:
    """MAP of δ by damped Newton, then the Laplace precision at the MAP."""
    P = len(personal_idx)
    prior_prec = np.diag(1.0 / prior_sd ** 2)
    delta = np.zeros(P)
    if not observations:
        return DeltaPosterior(delta, prior_prec, 0, 0)

    def grad_hess(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        b = b_pop.copy()
        b[personal_idx] += d
        g = -prior_prec @ d
        H = -prior_prec.copy()
        for o in observations:
            xp = o.x[personal_idx]
            _, d1, d2 = loglik_terms(o.scale * float(o.x @ b), o)
            g += o.scale * d1 * xp
            H += (o.scale ** 2) * d2 * np.outer(xp, xp)
        return g, H

    lp = log_posterior(delta, b_pop, personal_idx, prior_sd, observations)
    it = 0
    for it in range(1, max_iter + 1):
        g, H = grad_hess(delta)
        step = np.linalg.solve(H, -g)   # H is negative definite (log-concave likelihoods + Gaussian prior)
        t = 1.0
        while True:
            cand = delta + t * step
            lp_new = log_posterior(cand, b_pop, personal_idx, prior_sd, observations)
            if lp_new >= lp - 1e-12 or t < 1e-6:
                break
            t *= 0.5
        converged = abs(lp_new - lp) < tol and float(np.max(np.abs(t * step))) < 1e-6
        delta, lp = cand, lp_new
        if converged:
            break
    _, H = grad_hess(delta)
    return DeltaPosterior(delta, -H, it, len(observations))


def prob_negative(mean: float, sd: float) -> float:
    """P(β < 0) under the Gaussian approximation."""
    if sd <= 0:
        return 1.0 if mean < 0 else 0.0
    return 0.5 * (1.0 + math.erf((-mean / sd) / math.sqrt(2.0)))
