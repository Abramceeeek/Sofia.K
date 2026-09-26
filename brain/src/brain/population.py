"""The population model: b_population, the prior on δ_person, cutpoints and scales (data/priors.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    label: str
    group: str
    mean: float
    delta_sd: float
    personal: bool
    source: str | None = None


@dataclass(frozen=True)
class PopulationModel:
    version: str
    features: tuple[FeatureSpec, ...]
    scales: dict[str, float]
    cutpoints: dict[str, tuple[float, ...]]

    @property
    def names(self) -> list[str]:
        return [f.name for f in self.features]

    @property
    def b_pop(self) -> np.ndarray:
        return np.array([f.mean for f in self.features], dtype=float)

    @property
    def personal_names(self) -> list[str]:
        return [f.name for f in self.features if f.personal]

    @property
    def personal_idx(self) -> np.ndarray:
        return np.array([i for i, f in enumerate(self.features) if f.personal], dtype=int)

    @property
    def delta_prior_sd(self) -> np.ndarray:
        return np.array([f.delta_sd for f in self.features if f.personal], dtype=float)

    def spec(self, name: str) -> FeatureSpec:
        for f in self.features:
            if f.name == name:
                return f
        raise KeyError(name)

    def vector(self, x: dict[str, float]) -> np.ndarray:
        """Dense x in model order. Unknown names are an error, missing names are 0."""
        unknown = set(x) - set(self.names)
        if unknown:
            raise KeyError(f"features not in the population model: {sorted(unknown)}")
        return np.array([x.get(n, 0.0) for n in self.names], dtype=float)

    def b_person(self, delta: np.ndarray | None) -> np.ndarray:
        """b_person = b_population + δ_person (δ only on the personal features)."""
        b = self.b_pop.copy()
        if delta is not None and len(delta):
            b[self.personal_idx] += delta
        return b


def load_population(path: Path) -> PopulationModel:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    feats = tuple(FeatureSpec(**f) for f in d["features"])
    names = [f.name for f in feats]
    if len(set(names)) != len(names):
        raise ValueError("duplicate feature names in priors")
    for f in feats:
        if f.personal and f.delta_sd <= 0:
            raise ValueError(f"{f.name}: a personal feature needs delta_sd > 0")
    return PopulationModel(
        version=str(d["version"]),
        features=feats,
        scales={k: float(v) for k, v in d["scales"].items()},
        cutpoints={k: tuple(float(c) for c in v) for k, v in d["cutpoints"].items()},
    )
