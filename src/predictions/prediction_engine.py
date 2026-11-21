"""Market-specific one-step-ahead forecasting.

Non-negotiable properties of everything this module produces:

* **One market, one target, one date.** A forecast is never a blend of markets.
  Kalyan's forecast uses Kalyan's history (plus, where declared and available,
  the paired market's already-published values).
* **No future information.** Features for the forecast row are built by the same
  ``build_features`` code path used in training, from history only. The row is
  created by appending a sentinel and reading the last feature row, so a leak
  would have been caught by the same causality verifier that guards the backtest.
* **No unearned confidence.** A candidate model is used only if it passed the
  promotion rule in walk-forward validation. If nothing passed - which is the
  case on every dataset examined here - the forecast is issued from the best
  baseline and *labelled as a baseline*, with an explicit statement that no
  predictive edge was demonstrated.
* **No gambling advice.** The output is a probability vector with its measured
  accuracy. It is not a recommendation to stake money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from src.backtesting.validation import best_baseline, decide
from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.models.close_models import same_day_open_available
from src.models.market_models import build as build_model
from src.preprocessing.cleaning import clean_target
from src.preprocessing.feature_engineering import FeatureConfig, build_features
from src.preprocessing.normalization import encode_categorical
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)

OUTCOME_LABELS = [str(i) for i in range(10)]
MIN_FORECAST_HISTORY = 400


@dataclass
class Forecast:
    market_id: str
    target: str
    target_date: str
    cutoff_date: str
    model_name: str
    model_version: str
    mode: str                      # "promoted_model" | "baseline_fallback"
    probs: dict[str, float]
    ranked: list[list[Any]]
    n_history: int
    train_size: int
    feature_version: str
    dataset: str
    baseline_name: str | None
    edge_evidence: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def top(self, k: int = 3) -> list[tuple[str, float]]:
        return [(str(o), float(p)) for o, p in self.ranked[:k]]

    @property
    def uniform_floor_log_loss(self) -> float:
        return float(np.log(10))

    @property
    def has_demonstrated_edge(self) -> bool:
        return self.mode == "promoted_model"


# ---------------------------------------------------------------------------
# calendar helpers
# ---------------------------------------------------------------------------
def latest_result_date(config: Config, market_id: str, target: str) -> date | None:
    result = clean_target(config, market_id, target)
    if result.frame.empty:
        return None
    return pd.Timestamp(result.frame["result_date"].max()).date()


def next_draw_date(config: Config, market_id: str, target: str,
                   after: date | None = None) -> date | None:
    """Next scheduled draw date. These markets draw Mon-Sat (no Sunday)."""
    base = after or latest_result_date(config, market_id, target)
    if base is None:
        return None
    nxt = base + timedelta(days=1)
    while nxt.weekday() == 6:  # Sunday
        nxt += timedelta(days=1)
    return nxt


# ---------------------------------------------------------------------------
# model selection
# ---------------------------------------------------------------------------
def select_model(config: Config, market_id: str, target: str, *,
                 panel: Any | None = None) -> dict[str, Any]:
    """Apply the promotion rule and choose what, if anything, may be used."""
    from src.mathematics.engine import build_context
    from src.mathematics.model_panel import get_panel

    if panel is None:
        ctx = build_context(config, market_id, target)
        panel = get_panel(ctx)

    base_name = panel.best_baseline_name()
    base_ll = panel.baselines[base_name].per_obs_log_loss().mean()

    evaluated: list[dict[str, Any]] = []
    for name, result in panel.models.items():
        verdict = decide(result, panel.baselines, min_improvement=0.002, block=5)
        evaluated.append({
            "model": name,
            "log_loss": float(result.per_obs_log_loss().mean()),
            "promoted": verdict.promoted,
            "reasons": verdict.reasons,
        })
    evaluated.sort(key=lambda r: r["log_loss"])
    promoted = [r for r in evaluated if r["promoted"]]

    if promoted:
        chosen = promoted[0]
        return {
            "mode": "promoted_model", "model": chosen["model"],
            "baseline": base_name, "baseline_log_loss": float(base_ll),
            "candidates": evaluated, "verdict": chosen,
        }
    return {
        "mode": "baseline_fallback", "model": base_name,
        "baseline": base_name, "baseline_log_loss": float(base_ll),
        "candidates": evaluated,
        "verdict": {"promoted": False, "reasons": [
            "no candidate model passed the promotion rule against the best baseline "
            f"({base_name}, log loss {base_ll:.5f})"]},
    }


# ---------------------------------------------------------------------------
# feature row for the next draw
# ---------------------------------------------------------------------------
def build_extended(config: Config, market_id: str, target: str, *,
                   next_open: int | None = None,
                   next_foreign_open: int | None = None,
                   target_date: date | None = None) -> dict[str, Any]:
    """Build the feature matrix for ``n`` observed draws plus one forecast row.

    Both parts come from a single call to ``build_features`` on the extended
    history, so the training matrix and the forecast row are guaranteed to have
    identical columns - a mismatch would otherwise silently corrupt the forecast.

    Availability rules for the extra row:

    * own same-day Open is used only if the caller supplies it (it is published
      after these features would be computed otherwise);
    * a foreign same-day Open is used only if the caller supplies it and the
      configuration declares the precedence.

    ``target_date`` overrides the sentinel date (default: the automatic next
    draw). It matters for calendar features (day-of-week, day-of-year) and for
    the label; a holiday or a suspension is the usual reason to pass one.

    Any channel that is not available is *removed from the whole matrix*, not
    imputed, so training and forecasting stay consistent.
    """
    from src.models.open_models import (
        _aligned_series,
        _cross_market_arrays,
        same_day_foreign_open,
    )

    result = clean_target(config, market_id, target)
    dates = pd.DatetimeIndex(result.frame["result_date"])
    y = encode_categorical(result.frame["y"].tolist(), list(range(10)))
    next_date = target_date or next_draw_date(config, market_id, target)
    dates_ext = dates.append(pd.DatetimeIndex([pd.Timestamp(next_date)]))
    y_ext = np.concatenate([y, [0]])  # sentinel; build_features never reads y[t]

    open_values = None
    if target == "close" and same_day_open_available(config, market_id) and next_open is not None:
        series = _aligned_series(config, market_id, "open", dates_ext).astype(float)
        open_values = series.to_numpy(dtype=float)
        open_values[-1] = float(next_open)

    cross_open, cross_close = _cross_market_arrays(config, market_id, target, dates_ext)
    foreign_today, partner = same_day_foreign_open(config, market_id, dates_ext)
    if foreign_today is not None:
        if next_foreign_open is None:
            foreign_today = None
        else:
            foreign_today = foreign_today.copy()
            foreign_today[-1] = float(next_foreign_open)

    cfg = FeatureConfig(include_same_day_open=open_values is not None)
    X = build_features(y_ext, cfg, same_day_open=open_values, cross_open=cross_open,
                       cross_close=cross_close, dates=dates_ext,
                       cross_open_today=foreign_today)
    X_clean = np.nan_to_num(X.to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    return {
        "X_train": X_clean[:-1], "X_next": X_clean[[-1]], "X_full": X_clean,
        "y": y, "dates": dates, "dates_ext": dates_ext,
        "next_date": next_date, "columns": list(X.columns),
        "feature_version": cfg.feature_version,
        "channels": {
            "same_day_open": open_values is not None,
            "same_day_foreign_open": foreign_today is not None,
            "foreign_partner": partner if foreign_today is not None else None,
        },
    }


def _align(probs: np.ndarray, classes: np.ndarray) -> np.ndarray:
    """Scatter a model's probability columns onto the full 0-9 outcome space.

    A model refitted on a subset that never observed some outcome returns fewer
    columns. Scattering onto a zero vector preserves the model's own beliefs and
    leaves the unseen outcomes at zero probability - which is honest, and unlike
    a default-filled vector it does not silently renormalise the observed
    probabilities downwards.
    """
    out = np.zeros(10)
    for i, cls in enumerate(np.asarray(classes).astype(int)):
        if 0 <= cls < 10 and i < len(probs):
            out[cls] = float(probs[i])
    total = out.sum()
    return out / total if total > 0 else np.full(10, 0.1)


def generate(config: Config, market_id: str, target: str, *,
             panel: Any | None = None,
             next_open: int | None = None,
             next_foreign_open: int | None = None,
             target_date: date | None = None,
             persist: bool = True) -> Forecast:
    """Produce the next-draw probability vector for one market and one target."""
    config.market(market_id)  # validates the id
    if target not in ("open", "close"):
        raise ValueError(f"unsupported target '{target}' (expected 'open' or 'close')")

    last = latest_result_date(config, market_id, target)
    if last is None:
        raise ValueError(f"market '{market_id}' has no {target} history to forecast from")
    result = clean_target(config, market_id, target)
    n_history = len(result.frame)
    if n_history < MIN_FORECAST_HISTORY:
        raise ValueError(
            f"market '{market_id}' {target}: only {n_history} observations; "
            f"at least {MIN_FORECAST_HISTORY} are required before forecasting")

    selection = select_model(config, market_id, target, panel=panel)
    model_name = selection["model"]
    auto_next = next_draw_date(config, market_id, target, after=last)
    if target_date is not None:
        if target_date <= last:
            raise ValueError(
                f"target date {target_date.isoformat()} is not after the last result "
                f"({last.isoformat()}); nothing to forecast")
        forecast_date = target_date
        notes = [
            f"history through {last.isoformat()} ({n_history} draws); "
            f"forecast for {forecast_date.isoformat()} "
            f"(explicit target date; the automatic next draw is {auto_next.isoformat()})",
        ]
    else:
        forecast_date = auto_next
        notes = [
            f"history through {last.isoformat()} ({n_history} draws); "
            f"forecast for {forecast_date.isoformat()}",
        ]

    if selection["mode"] == "promoted_model":
        built = build_extended(config, market_id, target, next_open=next_open,
                               next_foreign_open=next_foreign_open,
                               target_date=forecast_date)
        model = build_model(model_name)
        model.fit(built["X_train"], built["y"])
        raw = np.asarray(model.predict_proba(built["X_next"]))[0]
        probs = _align(raw, getattr(model, "classes_", np.arange(10)))
        meta = {"feature_version": built["feature_version"],
                "n_features": int(built["X_train"].shape[1])}
        mode = "promoted_model"
    else:
        # Baseline path: replay the full history through the same online object
        # that produced the walk-forward forecasts, then read its next-draw
        # distribution. No refitting and no feature use - that is the point.
        from src.backtesting.baselines import make_baselines

        y_hist = encode_categorical(result.frame["y"].tolist(), list(range(10)))
        baseline = next(b for b in make_baselines() if b.name == model_name)
        baseline.reset(10)
        for value in y_hist:
            baseline.update(int(value))
        probs = np.asarray(baseline.predict(), dtype=float)
        probs = probs / probs.sum() if probs.sum() > 0 else np.full(10, 0.1)
        meta = {"feature_version": FeatureConfig().feature_version, "n_features": 0}
        mode = "baseline_fallback"
        notes.append(
            "no candidate model beat the best baseline out of sample, so this forecast is the "
            "baseline distribution; it carries no demonstrated predictive edge")
        if next_open is not None:
            notes.append("supplied same-day Open was not used: the selected forecaster is a "
                         "baseline that does not consume features")

    notes.extend(excluded_channel_notes(config, market_id, target, next_open,
                                        next_foreign_open))

    ranked = sorted(((OUTCOME_LABELS[i], float(probs[i])) for i in range(10)),
                    key=lambda t: -t[1])
    forecast = Forecast(
        market_id=market_id, target=target,
        target_date=forecast_date.isoformat(), cutoff_date=last.isoformat(),
        model_name=model_name,
        model_version=f"{model_name}-{meta['feature_version']}-{config.fingerprint()[:8]}",
        mode=mode, probs={lbl: float(probs[i]) for i, lbl in enumerate(OUTCOME_LABELS)},
        ranked=[[lbl, float(p)] for lbl, p in ranked],
        n_history=n_history, train_size=n_history,
        feature_version=meta["feature_version"], dataset=config.dataset.name,
        baseline_name=selection["baseline"],
        edge_evidence={"selection": selection}, notes=notes,
    )

    if persist:
        persist_forecast(config, forecast)
    return forecast


def excluded_channel_notes(config: Config, market_id: str, target: str,
                              next_open: int | None,
                             next_foreign_open: int | None) -> list[str]:
    """Explain any channel that was excluded because it is not yet published."""
    notes: list[str] = []
    if target == "close" and same_day_open_available(config, market_id) and next_open is None:
        notes.append(
            "same-day Open not supplied, so Open-derived features were excluded from this "
            "forecast; supply it once the Open is published (--open-ank) to use them")
    if target == "close":
        for partner, target_market in config.cross_open_precedence:
            if target_market != market_id:
                continue
            if next_foreign_open is None:
                notes.append(
                    f"same-day {partner} Open not supplied, so the declared cross-market channel "
                    f"was excluded; it is only usable once {partner} has published (--foreign-open-ank)")
            break
    return notes


def persist_forecast(config: Config, forecast: Forecast, *, model_id: int | None = None) -> int:
    db = MarketDatabase(config, forecast.market_id)
    if not db.manager.exists(forecast.market_id):
        log.warning("database for %s does not exist; forecast not persisted", forecast.market_id)
        return 0
    return db.save_predictions([{
        "target": forecast.target, "target_date": forecast.target_date,
        "model_id": model_id, "model_version": forecast.model_version,
        "cutoff_date": forecast.cutoff_date, "train_size": forecast.train_size,
        "feature_version": forecast.feature_version,
        "probs": forecast.probs,
        "ranked": forecast.ranked,
        "created_at": forecast.created_at,
    }])


def generate_all_targets(config: Config, market_id: str, **kwargs: Any) -> list[Forecast]:
    """Forecast every target the market publishes an outcome space for."""
    forecasts = []
    for target in ("open", "close"):
        try:
            forecasts.append(generate(config, market_id, target, **kwargs))
        except Exception as exc:
            log.warning("forecast failed for %s/%s: %s", market_id, target, exc)
    return forecasts


def best_baseline_for(config: Config, market_id: str, target: str) -> str:
    from src.mathematics.engine import build_context
    from src.mathematics.model_panel import get_panel

    panel = get_panel(build_context(config, market_id, target))
    return best_baseline(panel.baselines)
