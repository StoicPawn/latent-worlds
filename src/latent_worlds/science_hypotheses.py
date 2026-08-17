from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Sequence

import numpy as np


@dataclass(slots=True)
class ModelFit:
    name: str
    predict_fn: Callable[[np.ndarray], np.ndarray]
    mse: float
    complexity: int

    def predict(self, x: np.ndarray | Sequence[float]) -> np.ndarray:
        arr = np.asarray(x, dtype=float)
        if arr.ndim == 1:
            arr = arr[None, :]
        return self.predict_fn(arr)


class HypothesisEnsemble:
    """Competing generic hypotheses for a multivariate physical relation.

    The ensemble intentionally does not contain the simulator's true equation.
    It compares broad function classes over observed feature/outcome pairs.
    """

    def __init__(self, max_samples: int = 180):
        self.max_samples = max_samples
        self.samples: list[tuple[tuple[float, ...], float]] = []
        self._fits: list[ModelFit] = []
        self._centre: np.ndarray | None = None
        self._scale: np.ndarray | None = None

    def add(self, features: Sequence[float] | float, y: float) -> None:
        if isinstance(features, (float, int)):
            features = (float(features),)
        x = tuple(float(v) for v in features)
        if not all(math.isfinite(v) for v in (*x, y)):
            return
        self.samples.append((x, float(y)))
        if len(self.samples) > self.max_samples:
            del self.samples[:-self.max_samples]
        self._refit()

    @property
    def fits(self) -> list[ModelFit]:
        return self._fits

    @property
    def dimension(self) -> int:
        return len(self.samples[0][0]) if self.samples else 0

    def _standardise(self, X: np.ndarray) -> np.ndarray:
        assert self._centre is not None and self._scale is not None
        return (X - self._centre) / self._scale

    def _design(self, Z: np.ndarray, family: str) -> np.ndarray:
        n, d = Z.shape
        cols = [np.ones(n)]
        if family in {"linear", "quadratic_additive", "quadratic_interaction"}:
            cols.extend(Z[:, j] for j in range(d))
        if family in {"quadratic_additive", "quadratic_interaction"}:
            cols.extend(Z[:, j] ** 2 for j in range(d))
        if family == "quadratic_interaction":
            for i in range(d):
                for j in range(i + 1, d):
                    cols.append(Z[:, i] * Z[:, j])
        return np.column_stack(cols)

    def _refit(self) -> None:
        if len(self.samples) < 5:
            self._fits = []
            return
        X = np.asarray([s[0] for s in self.samples], dtype=float)
        y = np.asarray([s[1] for s in self.samples], dtype=float)
        self._centre = np.mean(X, axis=0)
        self._scale = np.maximum(np.std(X, axis=0), 0.5)
        Z = self._standardise(X)
        fits: list[ModelFit] = []

        for family in ("constant", "linear", "quadratic_additive", "quadratic_interaction"):
            D = self._design(Z, family)
            ridge = 2e-5 * np.eye(D.shape[1])
            coef = np.linalg.solve(D.T @ D + ridge, D.T @ y)
            pred = D @ coef
            mse = float(np.mean((y - pred) ** 2))

            def make_fn(c=coef.copy(), fam=family, centre=self._centre.copy(), scale=self._scale.copy()):
                def fn(xx: np.ndarray) -> np.ndarray:
                    zz = (xx - centre) / scale
                    dd = self._design(zz, fam)
                    return dd @ c
                return fn

            fits.append(ModelFit(family, make_fn(), mse, len(coef)))

        # Generic smooth alternative. Centres are selected from observations,
        # not from privileged world knowledge.
        n_centres = min(10, len(X))
        idx = np.linspace(0, len(X) - 1, n_centres, dtype=int)
        centres = Z[idx]
        pairwise = np.sqrt(np.sum((Z[:, None, :] - centres[None, :, :]) ** 2, axis=2))
        nonzero = pairwise[pairwise > 1e-8]
        bandwidth = max(float(np.median(nonzero)) if nonzero.size else 1.0, 0.6)
        Phi = np.column_stack([
            np.ones(len(Z)),
            *[np.exp(-0.5 * np.sum((Z - c) ** 2, axis=1) / bandwidth**2) for c in centres],
        ])
        ridge = 3e-3 * np.eye(Phi.shape[1])
        coef = np.linalg.solve(Phi.T @ Phi + ridge, Phi.T @ y)
        pred = Phi @ coef
        mse = float(np.mean((y - pred) ** 2))

        def rbf_fn(xx: np.ndarray, c=coef.copy(), cs=centres.copy(), bw=bandwidth,
                   centre=self._centre.copy(), scale=self._scale.copy()):
            zz = (xx - centre) / scale
            cols = [np.ones(len(zz))]
            cols.extend(np.exp(-0.5 * np.sum((zz - k) ** 2, axis=1) / bw**2) for k in cs)
            return np.column_stack(cols) @ c

        fits.append(ModelFit("rbf", rbf_fn, mse, len(coef)))
        self._fits = fits

    def weights(self) -> np.ndarray:
        if not self._fits:
            return np.asarray([], dtype=float)
        n = max(len(self.samples), 1)
        scores = np.asarray([
            n * math.log(max(f.mse, 1e-8)) + 1.8 * f.complexity
            for f in self._fits
        ])
        scores -= scores.min()
        w = np.exp(-0.5 * np.clip(scores, 0.0, 80.0))
        return w / max(float(w.sum()), 1e-12)

    def predict(self, features: Sequence[float] | float) -> tuple[float, float]:
        if isinstance(features, (float, int)):
            features = (float(features),)
        x = np.asarray(features, dtype=float)[None, :]
        if not self._fits:
            return 0.5, 1.0
        preds = np.asarray([float(f.predict(x)[0]) for f in self._fits])
        w = self.weights()
        mean = float(np.dot(w, preds))
        disagreement = float(np.sqrt(np.dot(w, (preds - mean) ** 2)))
        uncertainty = disagreement + 1.0 / math.sqrt(max(len(self.samples), 1))
        return mean, uncertainty

    def best_model_name(self) -> str | None:
        if not self._fits:
            return None
        return self._fits[int(np.argmax(self.weights()))].name

    def sampled_spans(self) -> tuple[float, ...]:
        if not self.samples:
            return ()
        X = np.asarray([s[0] for s in self.samples], dtype=float)
        return tuple(float(v) for v in np.ptp(X, axis=0))

    def prediction_rmse(self, X: np.ndarray, truth: np.ndarray) -> float | None:
        if not self._fits:
            return None
        pred = np.asarray([self.predict(row)[0] for row in np.asarray(X, dtype=float)])
        return float(np.sqrt(np.mean((pred - truth) ** 2)))
