"""Shared, cached walk-forward model panel.

Every machine-learning method (73-84) and every ensemble method (85-98) needs the
same out-of-sample predictions. Computing them once per ``(dataset, market,
target)`` and sharing the result makes the 100-method sweep both affordable and
*internally consistent*: method 75 and method 98 are then demonstrably looking at
the same predictions rather than at two slightly different runs.

The cache is keyed by the full configuration fingerprint, so a change to features,
model panel or evaluation window invalidates it rather than silently reusing stale
numbers.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning

from src.backtesting.baselines import make_baselines
from src.backtesting.validation import best_baseline, calibration_report, decide, fold_stability
from src.backtesting.walk_forward import WalkForwardResult, batch_walk_forward, online_walk_forward
from src.core.logging import get_logger
from src.models.market_models import CORE_MODELS, REFIT_SCHEDULE, build
from src.models.close_models import build_frame

log = get_logger(__name__)

_CACHE: dict[tuple, "ModelPanel"] = {}


@dataclass
class ModelPanel:
    market_id: str
    target: str
    dataset: str
    n: int
    dates: pd.DatetimeIndex
    y: np.ndarray
    feature_count: int
    baselines: dict[str, WalkForwardResult]
    models: dict[str, WalkForwardResult] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    min_train: int = 0
    frame: Any = None
    build_seconds: float = 0.0

    # -- convenience -----------------------------------------------------
    @property
    def all_results(self) -> dict[str, WalkForwardResult]:
        return {**self.baselines, **self.models}

    @property
    def baseline_names(self) -> list[str]:
        return list(self.baselines)

    def best_baseline_name(self) -> str:
        return best_baseline(self.baselines)

    def get(self, name: str) -> WalkForwardResult | None:
        return self.all_results.get(name)

    def table(self) -> pd.DataFrame:
        rows = []
        best_base = self.best_baseline_name()
        base_ll = self.baselines[best_base].per_obs_log_loss().mean()
        for name, result in self.all_results.items():
            metrics = result.metrics().as_dict()
            rows.append({
                "model": name,
                "kind": "baseline" if name in self.baselines else "candidate",
                "log_loss": metrics["log_loss"],
                "brier": metrics["brier"],
                "accuracy": metrics["accuracy"],
                "top3": metrics["top3"],
                "ece": metrics["ece"],
                "vs_best_baseline": round(base_ll - metrics["log_loss"], 6),
            })
        return pd.DataFrame(rows).sort_values("log_loss").reset_index(drop=True)

    def verdict_for(self, name: str) -> dict[str, Any]:
        result = self.get(name)
        if result is None:
            return {"promoted": False, "reasons": ["model not available"]}
        verdict = decide(result, self.baselines,
                         min_improvement=0.002, block=5)
        return verdict.as_dict()

    def diagnostics_for(self, name: str) -> dict[str, Any]:
        result = self.get(name)
        if result is None:
            return {}
        base = self.baselines[self.best_baseline_name()]
        return {
            "model_metrics": result.metrics().as_dict(),
            "baseline_metrics": base.metrics().as_dict(),
            "best_baseline": self.best_baseline_name(),
            "calibration": {k: v for k, v in calibration_report(result).items() if k != "table"},
            "stability": fold_stability(result, base),
        }


def get_panel(ctx, *, models: list[str] | None = None) -> ModelPanel:
    """Build (or fetch) the panel for this context's market and target."""
    from src.models.open_models import build_open_frame

    key = (ctx.dataset, ctx.market_id, ctx.target, ctx.config.fingerprint(),
           tuple(models) if models else ("CORE",))
    if key in _CACHE:
        return _CACHE[key]

    import time

    started = time.time()
    frame = build_frame(ctx.config, ctx.market_id, ctx.target, verify=False)
    research = ctx.config.research.get("walk_forward", {})
    min_train = int(research.get("min_train_size", 400))
    n = len(frame.y)
    min_train = min(min_train, max(200, int(n * 0.25)))
    X = np.nan_to_num(frame.X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)

    log.info("building model panel for %s/%s/%s (n=%d, features=%d, min_train=%d)",
             ctx.dataset, ctx.market_id, ctx.target, n, X.shape[1], min_train)

    baselines = online_walk_forward(
        make_baselines(), frame.y, pd.DatetimeIndex(frame.dates), min_train=min_train,
        market_id=ctx.market_id, target=ctx.target, ordinal=(ctx.space == "ank"),
    )

    panel = ModelPanel(
        market_id=ctx.market_id, target=ctx.target, dataset=ctx.dataset, n=n,
        dates=pd.DatetimeIndex(frame.dates), y=frame.y, feature_count=X.shape[1],
        baselines=baselines, min_train=min_train, frame=frame,
    )

    for model_name in (models or CORE_MODELS):
        try:
            with warnings.catch_warnings():
                # Convergence and deprecation noise from sklearn's own optimisers
                # is not actionable here; real failures are recorded in `errors`.
                warnings.filterwarnings("ignore", category=ConvergenceWarning)
                warnings.filterwarnings("ignore", message=".*probability.*deprecated.*")
                result = batch_walk_forward(
                    lambda name=model_name: build(name), X, frame.y,
                    pd.DatetimeIndex(frame.dates), min_train=min_train,
                    refit_every=REFIT_SCHEDULE.get(model_name, 80),
                    model_name=model_name, market_id=ctx.market_id, target=ctx.target,
                    ordinal=(ctx.space == "ank"),
                )
            panel.models[model_name] = result
        except Exception as exc:
            log.warning("model %s failed for %s/%s: %s", model_name, ctx.market_id,
                        ctx.target, exc)
            panel.errors[model_name] = f"{type(exc).__name__}: {exc}"

    panel.build_seconds = round(time.time() - started, 2)
    log.info("panel ready for %s/%s in %.1fs (%d models, %d baselines)",
             ctx.market_id, ctx.target, panel.build_seconds,
             len(panel.models), len(panel.baselines))
    _CACHE[key] = panel
    return panel


def clear_cache() -> None:
    _CACHE.clear()
