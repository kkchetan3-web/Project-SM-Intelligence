"""The research engine: run the method suite, store it, document it.

Execution order matters. Methods 1-90 and 93-100 run first; their p-values are
then collected and fed into the two meta-analyses (91, 92). Finally every p-value
in the run receives a Benjamini-Hochberg adjustment, which is what makes the
report's headline claim - "nothing survives correction" - a computed statement
rather than an assertion.

Results are written to ``method_results`` in the market's own database. The
engine never writes to another market's database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.backtesting.validation import fdr_correct
from src.core.configuration import Config
from src.core.logging import get_logger
from src.core.provenance import utcnow
from src.mathematics import registry
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_FAILED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_NOT_APPLICABLE,
    STATUS_UNAVAILABLE,
    MethodContext,
    MethodOutput,
)
from src.preprocessing.cleaning import clean_target
from src.preprocessing.normalization import encode_categorical, support_for
from src.storage.market_database import MarketDatabase

log = get_logger(__name__)


#: Metrics whose p-value is *not* a test of the null hypothesis "no structure".
#: Feeding them into a multiple-testing correction is a category error: a bootstrap
#: p-value for "this difference is not exactly zero" is ~0 whenever the difference is
#: reliably non-zero, which says nothing about predictability. They stay in the
#: database with their raw p-value and an explicit exclusion reason, and they are
#: judged instead by the promotion rule.
FDR_EXCLUDED_PATTERNS: tuple[tuple[str, str], ...] = (
    ("difference", "magnitude comparison (how much), not a test of whether structure exists"),
    ("improvement", "magnitude comparison (how much), not a test of whether structure exists"),
    ("change", "magnitude comparison (how much), not a test of whether structure exists"),
    ("vs_baseline", "magnitude comparison against a baseline, judged by the promotion rule"),
    ("vs_base_rate", "magnitude comparison against a base rate, judged by the promotion rule"),
    ("adf_", "unit-root test: stationarity of a bounded series is not evidence of predictability"),
    ("ks_p_value", "Kolmogorov-Smirnov assumes a continuous law; invalid for discrete draws"),
    ("smallest_p_value", "a summary of other p-values, not an independent test"),
)


def fdr_eligibility(method_id: str, finding: Any) -> tuple[bool, str | None]:
    """Whether a finding's p-value belongs in the multiple-testing family."""
    extra = getattr(finding, "extra", None) or {}
    if extra.get("test_valid") is False:
        return False, str(extra.get("test_invalid_reason") or "test assumptions not met")
    name = (finding.metric_name or "").lower()
    for pattern, reason in FDR_EXCLUDED_PATTERNS:
        if pattern in name:
            return False, reason
    return True, None


@dataclass
class SuiteResult:
    market_id: str
    target: str
    dataset: str
    run_id: str
    contexts: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, MethodOutput] = field(default_factory=dict)
    p_adjusted: dict[tuple[str, str], float] = field(default_factory=dict)
    p_excluded: dict[tuple[str, str], str] = field(default_factory=dict)
    seconds: float = 0.0
    failures: list[dict[str, str]] = field(default_factory=list)

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for output in self.outputs.values():
            counts[output.status] = counts.get(output.status, 0) + 1
        return counts

    @property
    def n_computed(self) -> int:
        return sum(1 for o in self.outputs.values() if o.status == STATUS_COMPUTED)

    def findings_frame(self) -> pd.DataFrame:
        rows = []
        for method_id, output in self.outputs.items():
            spec = registry.get(method_id).spec
            for f in output.findings:
                rows.append({
                    "method_id": method_id, "method": spec.name, "category": spec.category,
                    "status": output.status, "target": self.target,
                    "metric": f.metric_name, "value": f.metric_value,
                    "statistic": f.statistic, "p_value": f.p_value,
                    "p_adjusted": self.p_adjusted.get((method_id, f.metric_name), f.p_value),
                    "effect_size": f.effect_size, "n": f.sample_size,
                })
        return pd.DataFrame(rows)

    def summary(self) -> dict[str, Any]:
        frame = self.findings_frame()
        p_col = frame["p_adjusted"].dropna() if not frame.empty else pd.Series(dtype=float)
        return {
            "market_id": self.market_id, "target": self.target, "dataset": self.dataset,
            "run_id": self.run_id, "methods_run": len(self.outputs),
            "methods_computed": self.n_computed,
            "status_counts": self.status_counts(),
            "n_findings": int(len(frame)),
            "n_p_values": int(len(p_col)),
            "n_p_below_05_raw": int((frame["p_value"].dropna() < 0.05).sum()) if not frame.empty else 0,
            "n_p_below_05_adjusted": int((p_col < 0.05).sum()) if len(p_col) else 0,
            "seconds": round(self.seconds, 1),
            "failures": self.failures,
        }


def build_context(config: Config, market_id: str, target: str,
                  *, dataset_override: str | None = None) -> MethodContext:
    market = config.market(market_id)
    spec = market.target(target)
    clean = clean_target(config, market_id, target)
    if clean.frame.empty:
        raise ValueError(f"market '{market_id}' has no usable '{target}' records")

    labels = [str(v) for v in support_for(spec.space)]
    if spec.space == "ank":
        codes = clean.frame["y"].astype(int).to_numpy()
    else:
        codes = encode_categorical(clean.frame["y"].astype(str).tolist(), labels)

    return MethodContext(
        config=config, market_id=market.market_id, market=market, target=target,
        space=spec.space, k=len(labels), y=codes, labels=labels,
        dates=pd.DatetimeIndex(clean.frame["result_date"]),
        results=clean.frame, series=clean.frame.set_index("result_date")["y"],
        params=config.research.get("methods", {}),
        seed=config.seed(), dataset=dataset_override or config.dataset.name,
    )


def run_suite(config: Config, market_id: str, target: str, *,
              skip: tuple[str, ...] = (), only: tuple[str, ...] | None = None,
              persist: bool = True, verbose: bool = False) -> SuiteResult:
    """Execute the method suite for one market and target."""
    import time

    started = time.time()
    ctx = build_context(config, market_id, target)
    run_id = f"{config.fingerprint()}-{market_id}-{target}"
    result = SuiteResult(market_id=market_id, target=target, dataset=config.dataset.name,
                         run_id=run_id, contexts={"primary": ctx})

    method_ids = list(only) if only else registry.ORDERED_METHOD_IDS
    primary = [m for m in method_ids if m not in registry.META_METHODS]
    meta = [m for m in method_ids if m in registry.META_METHODS]

    log.info("running %d methods for %s/%s (%s, n=%d)",
             len(primary) + len(meta), market_id, target, config.dataset.name, ctx.n)

    for method_id in primary:
        if method_id in skip:
            continue
        entry = registry.get(method_id)
        try:
            output = entry.run(ctx)
        except Exception as exc:  # a method must never take down the suite
            log.warning("%s failed: %s: %s", method_id, type(exc).__name__, exc)
            output = MethodOutput(status=STATUS_FAILED,
                                  narrative=f"{type(exc).__name__}: {exc}")
            result.failures.append({"method": method_id, "error": f"{type(exc).__name__}: {exc}"})
        result.outputs[method_id] = output
        if verbose:
            log.info("%s %-42s %-18s (%d findings)", method_id, entry.name,
                     output.status, len(output.findings))

    # Collect p-values for the meta-analyses - eligible ones only, so that the
    # meta-analysis is correcting a coherent family rather than everything.
    p_values: list[tuple[str, float]] = []
    for method_id, output in result.outputs.items():
        for f in output.findings:
            if f.p_value is None or not np.isfinite(f.p_value):
                continue
            eligible, reason = fdr_eligibility(method_id, f)
            if eligible:
                p_values.append((f"{method_id}:{f.metric_name}", float(f.p_value)))
            else:
                result.p_excluded[(method_id, f.metric_name)] = str(reason)
    ctx.extras["all_p_values"] = p_values

    for method_id in meta:
        entry = registry.get(method_id)
        try:
            output = entry.run(ctx)
        except Exception as exc:
            log.warning("%s failed: %s", method_id, exc)
            output = MethodOutput(status=STATUS_FAILED, narrative=f"{type(exc).__name__}: {exc}")
            result.failures.append({"method": method_id, "error": str(exc)})
        result.outputs[method_id] = output

    # FDR adjustment over the eligible family only.
    eligible_findings: list[tuple[str, Any]] = []
    for method_id, output in result.outputs.items():
        for f in output.findings:
            if f.p_value is None or not np.isfinite(f.p_value):
                continue
            ok, reason = fdr_eligibility(method_id, f)
            if ok:
                eligible_findings.append((method_id, f))
            else:
                result.p_excluded.setdefault((method_id, f.metric_name), str(reason))
    if eligible_findings:
        corrected = fdr_correct([f.p_value for _, f in eligible_findings], "benjamini_hochberg",
                                float(config.research.get("multiple_testing", {}).get("alpha", 0.05)))
        for (method_id, f), adjusted in zip(eligible_findings, corrected["adjusted"], strict=True):
            result.p_adjusted[(method_id, f.metric_name)] = float(adjusted)

    result.seconds = time.time() - started
    if persist:
        _persist(config, result)
    log.info("suite %s/%s done in %.1fs: %s", market_id, target,
             result.seconds, result.status_counts())
    return result


def _persist(config: Config, result: SuiteResult) -> None:
    db = MarketDatabase(config, result.market_id)
    rows = []
    for method_id, output in result.outputs.items():
        spec = registry.get(method_id).spec
        if not output.findings:
            rows.append({
                "method_id": method_id, "method_name": spec.name, "category": spec.category,
                "market_id": result.market_id, "target": result.target,
                "scope": output.status, "metric_name": "no_metric",
                "metric_value": None, "extra": {"narrative": output.narrative[:800]},
                "run_id": result.run_id,
            })
            continue
        for f in output.findings:
            row = f.as_row(spec, result.contexts["primary"])
            row["scope"] = output.status if output.status != STATUS_COMPUTED else "full_sample"
            row["p_adjusted"] = result.p_adjusted.get((method_id, f.metric_name))
            extra = {**(f.extra or {}),
                     "narrative": output.narrative[:1200],
                     "dataset": result.dataset}
            reason = result.p_excluded.get((method_id, f.metric_name))
            if reason:
                extra["fdr_excluded"] = reason
            row["extra"] = extra
            row["run_id"] = result.run_id
            rows.append(row)
    db.save_method_results(rows)


def stage_research_frames(result: SuiteResult, config: Config) -> dict[str, pd.DataFrame]:
    """Persist the causal feature matrix used by the models for traceability."""
    from src.models.close_models import build_frame

    frame = build_frame(config, result.market_id, result.target, verify=True)
    db = MarketDatabase(config, result.market_id)
    n_rows = db.save_features(frame.X.assign(result_date=frame.dates),
                              result.target, frame.feature_version)
    return {"feature_rows": n_rows, "causality": frame.causality,
            "n_features": frame.X.shape[1]}


def targeted_rerun(config: Config, market_id: str, target: str,
                   method_ids: tuple[str, ...]) -> SuiteResult:
    """Re-run a subset - used by the CLI's single-method inspection."""
    return run_suite(config, market_id, target, only=method_ids, persist=True, verbose=True)
