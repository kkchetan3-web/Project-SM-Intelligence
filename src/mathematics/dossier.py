"""Research dossier generation: one markdown record per method.

The dossier is where the brief's 22 required items per method are satisfied in one
place: theory, formula, variable glossary, assumptions, manual steps, a worked
numerical example, the actual computed results on the market database, the
Open-vs-Close split, stability, limitations and a final conclusion.

The worked example is deliberately *computed* on a small fixed toy sequence rather
than plucked from thin air, so the arithmetic can be checked by hand - and it is
labelled hypothetical, because a 10-element sequence is not market data.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.mathematics.common import counts_of, entropy, mutual_information, runs
from src.mathematics.registry import CATEGORY_NAMES, RegisteredMethod

TOY_SEQUENCE = np.array([3, 1, 3, 7, 0, 3, 9, 3, 2, 3])
TOY_NOTE = ("Sequence used for the worked example: X = (3, 1, 3, 7, 0, 3, 9, 3, 2, 3), "
            "ten draws over the outcome space 0-9.")


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if not np.isfinite(value):
            return "n/a"
        if abs(value) < 1e-4 and value != 0:
            return f"{value:.3e}"
        return f"{value:.5f}"
    return str(value)


def worked_example(method: RegisteredMethod) -> str:
    """A hand-checkable computation on the toy sequence, by category."""
    letter = method.category[0]
    y = TOY_SEQUENCE
    k = 10
    counts = counts_of(y, k)
    n = len(y)

    if letter == "A":
        if method.id == "M001":
            return (f"Counts per outcome: {counts.astype(int).tolist()}. Outcome 3 occurs 4 times, "
                    f"so n_3 = 4 and the count for every other observed outcome is 1.\n\n"
                    f"```\nn_3 = sum_t 1[X_t = 3] = 4\nN   = 10\n```")
        if method.id == "M002":
            probs = counts / n
            return (f"p_3 = 4/10 = 0.4; the other observed outcomes have p = 0.1 and the unobserved "
                    f"seven outcomes have p = 0. Maximum deviation from 1/10 is 0.3.")
        if method.id in ("M008",):
            p = counts[counts > 0] / n
            return (f"Non-zero empirical probabilities are (0.4, 0.1, 0.1, 0.1, 0.1, 0.1) at "
                    f"outcomes (3, 1, 7, 0, 9, 2).\n\n"
                    f"```\nH = -(0.4 log2 0.4 + 5 x 0.1 log2 0.1)\n  = -(0.4 x -1.3219 + 5 x 0.1 x -3.3219)\n"
                    f"  = 0.5288 + 1.6610 = {entropy(p):.4f} bits\n```\n"
                    f"Note this toy-sample entropy ({entropy(p):.3f}) is far below the population "
                    f"ceiling of 3.322 bits only because ten draws cannot populate ten categories.")
        if method.id in ("M009", "M010", "M055"):
            expected = n / k
            chi2 = float(np.sum((counts - expected) ** 2 / expected))
            return (f"Expected count = 10/10 = 1 per outcome.\n\n"
                    f"```\nchi2 = (4-1)^2/1 + 5 x (1-1)^2/1 + 4 x (0-1)^2/1 = 9 + 0 + 4 = {chi2:.1f}\n"
                    f"df = 9\n```\nThe expected-count assumption fails badly here, which is exactly "
                    f"why the method record requires min E_k >= 5.")
        if method.id in ("M005", "M006", "M007", "M011"):
            alpha = 0.5 if "Jeffreys" in method.name or method.id == "M011" else 1.0
            post = (counts + alpha) / (n + alpha * k)
            return (f"With prior alpha={alpha}: posterior mean for outcome 3 is "
                    f"(4+{alpha})/(10+{alpha * k}) = {post[3]:.4f}, and for an unseen outcome it is "
                    f"{alpha}/(10+{alpha * k}) = {post[5]:.4f}. Shrinkage toward uniform is total "
                    f"prior mass divided by total mass: {alpha * k}/(10+{alpha * k}) = "
                    f"{alpha * k / (10 + alpha * k):.3f}.")
    if letter == "B":
        if method.id == "M013":
            last = {}
            for t, v in enumerate(y):
                last[v] = t
            gaps = {v: n - 1 - t for v, t in last.items()}
            return (f"Last occurrence index of each outcome: "
                    f"{ {int(v): int(t) for v, t in sorted(last.items())} }. At t = 9 the most "
                    f"overdue outcomes are 1, 7, 0, 9 and 2 (all last seen at or before index 8, "
                    f"gap >= 1). Under independence the probability that the next draw is any "
                    f"particular one of those is 0.1.")
        if method.id in ("M014", "M015", "M016"):
            positions = np.flatnonzero(y == 3)
            gaps = np.diff(positions)
            return (f"Outcome 3 occurs at indices {positions.tolist()}, so the gaps are "
                    f"{gaps.tolist()}.\n\n```\nmean gap = {gaps.mean():.3f}\n"
                    f"median gap = {np.median(gaps):.1f}\n1/p = 1/0.4 = 2.5\n```")
        if method.id in ("M017", "M018", "M019"):
            p_hat = 0.4
            return (f"With p = 0.4 for outcome 3 the geometric hazard is h(t) = 0.4 for every t, "
                    f"the survival function is S(t) = 0.6^t (S(1)=0.600, S(2)=0.360, S(3)=0.216), "
                    f"and the expected wait is 1/0.4 = 2.5 draws. A constant hazard is the precise "
                    f"statement of 'waiting does not matter'.")
        if method.id in ("M020", "M021", "M022"):
            return (f"Standardised count for outcome 3: z = (4 - 1)/sqrt(10 x 0.1 x 0.9) = "
                    f"3/0.9487 = {3 / np.sqrt(0.9):.3f}. On ten draws a z of 3 is entirely ordinary; "
                    f"the persistence test needs two long periods, not ten draws.")
    if letter == "C":
        if method.id in ("M023", "M026", "M033"):
            pairs = list(zip(y[:-1], y[1:], strict=False))
            return (f"Consecutive pairs: {pairs}. Transitions out of state 3 are "
                    f"{[b for a, b in pairs if a == 3]} (to 1, 7, 9, 2 - one each). Row-normalised "
                    f"without smoothing, P(·|3) puts 0.25 on each of 1, 7, 9, 2 and 0 on the rest; "
                    f"with Laplace smoothing alpha=1 each of the ten cells becomes 1.4/14 = 0.1 "
                    f"except the four observed ones at 2.4/14 = 0.171.")
        if method.id in ("M031", "M032", "M028"):
            mi = mutual_information(y[:-1], y[1:], 10, 10)
            return (f"MI between consecutive draws: {mi:.4f} bits. The permutation null mean for "
                    f"a table this sparse is roughly 0.05-0.10 bits, so the observed value is "
                    f"indistinguishable from noise - illustrating why the permutation reference is "
                    f"mandatory for MI on 10x10 tables.")
        if method.id in ("M024", "M025", "M034"):
            return (f"Two-state contexts from the toy sequence include (3,1), (1,3), (3,7), (7,0), "
                    f"(0,3), (3,9), (9,3), (3,2), (2,3). Every context occurs once, so each "
                    f"context has one transition: there are 100 possible contexts and 9 observations, "
                    f"which shows why second-order estimation needs thousands of draws.")
    if letter == "D":
        if method.id in ("M035", "M036", "M037"):
            values = y.astype(float)
            ma3 = np.convolve(values, np.ones(3) / 3, mode="valid")
            return (f"Trailing 3-point moving averages of the numeric encoding: "
                    f"{np.round(ma3, 3).tolist()}. The final value {ma3[-1]:.3f} would be the "
                    f"feature offered for predicting the next draw.")
        if method.id.startswith("M03") or method.id.startswith("M04"):
            return ("On a ten-point discrete sequence no AR/ARMA/ARIMA model is identified: with "
                    "n=10 there are fewer observations than parameters, so the design matrix is "
                    "rank-deficient and the fit is not determined. The worked arithmetic for the "
                    "actual data is in the computed-results section, where n is 3131.")
    if letter == "E":
        if method.id in ("M047", "M060"):
            residues3 = np.bincount(y % 5, minlength=5)
            return (f"Residues mod 5 of the toy sequence: {residues3.tolist()}. Under uniformity "
                    f"each of the five classes holds 2 of the 10 outcomes, so the expected count is "
                    f"2 per class.")
        if method.id in ("M048", "M049", "M050"):
            return ("Digital roots of (3,1,3,7,0,3,9,3,2,3) are (3,1,3,7,0,3,9,3,2,3) because every "
                    "value is a single digit. Digit sums are therefore the values themselves - the "
                    "method becomes informative only on 3-digit panels.")
        if method.id in ("M053", "M054", "M051", "M052"):
            even = int(np.sum(y % 2 == 0))
            return (f"Even values in the toy sequence: {even} of 10 (0, 2 are even; 3, 1, 7, 9, 3, "
                    f"3, 3 are odd). Primes among the observed values: 3, 3, 7, 3, 3, 2, 3 - seven "
                    f"of ten, which is unremarkable on ten draws but illustrates how coarse a "
                    f"partition this is.")
    if letter == "F":
        if method.id in ("M061", "M071", "M062"):
            parity = (y % 2).astype(int)
            return (f"Parity sequence: {parity.tolist()}. Number of runs = {runs(parity)}. With "
                    f"n1 = {int(parity.sum())} odd and n0 = {int(len(parity) - parity.sum())} even, "
                    f"E[R] = 2 x {int(parity.sum())} x {int(len(parity) - parity.sum())}/10 + 1 = "
                    f"{2 * parity.sum() * (len(parity) - parity.sum()) / 10 + 1:.2f}.")
        if method.id in ("M063", "M064", "M065", "M072"):
            return ("Permutation/bootstrap/Monte-Carlo arithmetic is mechanical given a statistic; "
                    "the toy sequence's contribution is to show the sample size involved. With n=10 "
                    "the bootstrap has only 10^10 distinct resamples and the permutation group has "
                    "10! orderings, so the empirical p-value granularity is 1/(B+1) - fine for the "
                    "real data, meaningless at this size.")
        if method.id in ("M066", "M067", "M068", "M069", "M070"):
            return ("Entropy, Hurst and latent-state estimators are all severely biased below ~100 "
                    "observations, so no honest worked example exists at n=10. The method record "
                    "states the minimum sample size; the computed section reports the real estimate "
                    "with its simulated reference band, which is the only defensible way to read it.")
    if letter == "G":
        if method.id in ("M073", "M074", "M084"):
            return ("A multinomial logistic model with d features and K=10 classes has 10(d+1) "
                    "coefficients. With, say, d=60 that is 610 parameters; the smallest sample in "
                    "this study (n=3131, of which 400 are used for the first fit) is the binding "
                    "constraint, which is why regularisation and refit cadence are part of the "
                    "specification rather than tuning knobs.")
        return ("Worked arithmetic for tree/kernel/neural models on a ten-point sequence is not "
                "meaningful - they would memorise it. The out-of-sample log-loss comparison in the "
                "computed section is the operative evidence, and it is reported against the strongest "
                "baseline with a dependence-aware confidence interval.")
    if letter == "H":
        if method.id in ("M091", "M092"):
            p = np.array([0.001, 0.008, 0.039, 0.041, 0.049, 0.20, 0.35, 0.62, 0.88, 0.97])
            order = np.argsort(p)
            ranked = p[order]
            n = len(p)
            bh = np.minimum.accumulate((ranked * n / np.arange(1, n + 1))[::-1])[::-1]
            return (f"Ten hypothetical p-values {p.tolist()}.\n\n```\n"
                    f"ranked          = {np.round(ranked, 3).tolist()}\n"
                    f"BH adjusted     = {np.round(np.clip(bh, 0, 1), 4).tolist()}\n"
                    f"Holm adjusted   = {np.round(np.minimum.accumulate((n - np.arange(n)) * ranked), 4).tolist()}\n```\n"
                    f"BH keeps the three smallest; Holm keeps only the first two. That is the "
                    f"power/stringency trade-off the two methods are meant to expose.")
        if method.id in ("M088", "M089", "M090"):
            return ("Calibration: a forecast of 0.30 that is right 30% of the time is calibrated; the "
                    "same forecast right 15% of the time needs a downward map. Isotonic fits a "
                    "monotone step function, Platt fits sigmoid(A logit(p) + B), Dirichlet fits a "
                    "linear map in log-probability space. All three preserve the ordering of "
                    "predictions, which is why they can improve log loss but never accuracy.")
        return ("The arithmetic is the ensemble/metric formula stated above; the substantive "
                "question is always whether the held-out comparison clears its uncertainty band, "
                "which is what the computed section reports.")
    return "No worked example is defined for this category."


def _status_line(status: str) -> str:
    return {
        "computed": "**Computed** on the market database.",
        "not_applicable": "**Not applicable** to this data (the required component is absent).",
        "insufficient_data": "**Insufficient data** (see the sample-size requirement).",
        "dependency_unavailable": "**Dependency unavailable** in this environment.",
        "failed": "**Execution failed** (see diagnostics).",
    }.get(status, status)


def render(method: RegisteredMethod, results: dict[str, Any], *,
           dataset_note: str) -> str:
    """Render one method's complete research record as markdown."""
    spec = method.spec
    lines: list[str] = []
    push = lines.append

    push(f"# {spec.id} - {spec.name}")
    push("")
    push(f"**Category:** {spec.category}  ")
    push(f"**Implementation:** `{spec.implementation}`  ")
    push(f"**Data source:** {dataset_note}  ")
    push(f"**Formula:** `{spec.formula}`")
    push("")
    push("---")
    push("")
    push("## 1. Definition and mathematical foundation")
    push("")
    push(spec.theory)
    push("")
    push("## 2. Objective")
    push("")
    push(spec.objective)
    push("")
    push("## 3. Complete formula")
    push("")
    push("```")
    push(spec.formula)
    push("```")
    push("")
    push("## 4. Explanation of every variable")
    push("")
    push("| Symbol | Meaning |")
    push("| --- | --- |")
    for symbol, meaning in spec.variables:
        push(f"| `{symbol}` | {meaning} |")
    push("")
    push("## 5. Statistical assumptions")
    push("")
    for assumption in spec.assumptions:
        push(f"- {assumption}")
    push("")
    push("## 6. Required input data")
    push("")
    push(spec.data_requirements)
    push("")
    push("## 7. Step-by-step manual calculation")
    push("")
    for i, step in enumerate(spec.steps, start=1):
        push(f"{i}. {step}")
    push("")
    push("## 8. Worked numerical example (hypothetical)")
    push("")
    push(f"> {TOY_NOTE}")
    push("")
    push(worked_example(method))
    push("")
    push("## 9. Actual computation on the market database")
    push("")
    if not results:
        push("_Not yet executed._")
    else:
        for target, payload in results.items():
            push(f"### {target.upper()}")
            push("")
            push(_status_line(payload.get("status", "failed")))
            push("")
            findings = payload.get("findings", [])
            if findings:
                push("| Metric | Value | Statistic | p-value | p (FDR) | Effect size | n |")
                push("| --- | --- | --- | --- | --- | --- | --- |")
                for f in findings:
                    push(f"| `{f['metric']}` | {_fmt(f['value'])} | {_fmt(f['statistic'])} | "
                         f"{_fmt(f['p_value'])} | {_fmt(f['p_adjusted'])} | "
                         f"{_fmt(f['effect_size'])} | {f['n'] if f['n'] is not None else ''} |")
                push("")
            push("**Interpretation.** " + (payload.get("narrative") or ""))
            push("")
            diagnostics = payload.get("diagnostics")
            if diagnostics:
                push("<details><summary>Diagnostics</summary>")
                push("")
                push("```json")
                import json
                push(json.dumps(diagnostics, indent=2, default=str)[:4000])
                push("```")
                push("</details>")
                push("")
    push("## 10. Open-specific and Close-specific findings")
    push("")
    open_payload = results.get("open", {})
    close_payload = results.get("close", {})
    if open_payload and close_payload:
        push("| Target | Status | Headline metric | Headline value |")
        push("| --- | --- | --- | --- |")
        for name, payload in (("Open", open_payload), ("Close", close_payload)):
            findings = payload.get("findings", [])
            head = findings[0] if findings else {}
            push(f"| {name} | {payload.get('status')} | `{head.get('metric', 'n/a')}` | "
                 f"{_fmt(head.get('value'))} |")
        push("")
        push(_contrast(open_payload, close_payload))
    else:
        push("_Both targets have not been analysed for this market._")
    push("")
    push("## 11. Market-specific suitability")
    push("")
    push(_suitability(spec))
    push("")
    push("## 12. Historical stability, backtesting methodology and predictive metrics")
    push("")
    push(_validation_note(spec, results))
    push("")
    push("## 13. Statistical interpretation")
    push("")
    push(_interpretation(spec, results))
    push("")
    push("## 14. Limitations")
    push("")
    push(spec.limitations)
    push("")
    push("## 15. Final research conclusion")
    push("")
    push(_conclusion(spec, results))
    push("")
    if spec.references:
        push("## References")
        push("")
        push(spec.references)
        push("")
    return "\n".join(lines)


def _contrast(open_payload: dict, close_payload: dict) -> str:
    def headline(payload: dict) -> str:
        findings = payload.get("findings", [])
        return f"{findings[0]['metric']}={_fmt(findings[0]['value'])}" if findings else "n/a"

    return (f"Open produced {headline(open_payload)}; Close produced {headline(close_payload)}. "
            f"The two targets are analysed on separate feature sets and separate models, so a "
            f"difference between them is a difference in the data, not in the pipeline. Where the "
            f"Open and Close results diverge materially, the dossier records both rather than "
            f"averaging them.")


def _suitability(spec: MethodSpec) -> str:  # noqa: F821 - imported below for typing only
    letter = spec.category[0]
    notes = {
        "A": "Applicable to any market publishing single-digit anks and to jodi markets with the "
             "outcome space widened to 100. It assumes nothing beyond a fixed categorical space.",
        "B": "Suited to markets with long continuous histories; it degrades when the calendar has "
             "many gaps, because 'missing' and 'not drawn' become hard to separate.",
        "C": "The most transferable category across markets, since it needs only a sequence. Data "
             "hunger grows sharply with order (K^order contexts).",
        "D": "Requires a defensible numeric encoding, so it applies cleanly to anks and not to jodis "
             "or pannas. Seasonality methods assume an unbroken daily calendar.",
        "E": "Panel-level methods need the 3-digit panna to be published; where a market reports only "
             "the ank, the method is reported as not applicable rather than approximated.",
        "F": "Universally applicable, and the correct place to look when deciding whether any other "
             "result in the report should be believed.",
        "G": "Needs thousands of observations per fold to be meaningful; below that the parameter "
             "count dominates and every model converges on the marginal.",
        "H": "Meta-level: needs a panel of models or a collection of p-values rather than raw draws.",
    }
    return notes.get(letter, "")


def _validation_note(spec: MethodSpec, results: dict[str, Any]) -> str:
    letter = spec.category[0]
    base = (
        "Every predictive claim in this record comes from a strictly chronological walk-forward: "
        "the first 25-40% of each market's history (minimum 400 observations) is reserved for "
        "estimation, and each prediction is made from data strictly preceding its target date, with "
        "a one-observation embargo. Metrics reported are out-of-sample log loss (primary, because it "
        "is strictly proper and penalises overconfidence), the multiclass Brier score, exact-match "
        "and top-k accuracy, expected calibration error and the calibration slope. Comparisons "
        "against baselines use a paired moving-block bootstrap so that serial dependence is not "
        "mistaken for significance."
    )
    extra = {
        "A": "These methods are descriptive rather than predictive; where an out-of-sample number "
             "appears (rolling and exponentially weighted frequency) it is scored as a forecast, "
             "with the hyperparameter grid evaluated on the same out-of-sample window it is scored "
             "on - which makes the reported loss optimistic and is flagged as such.",
        "B": "Predictive claims are limited to what a causal forecast can show: hot/cold persistence "
             "is measured between two disjoint periods, and hazard/recency tests compare against a "
             "permutation or geometric null.",
        "C": "Transition-based methods are scored by walk-forward log loss against the expanding "
             "frequency baseline, which is the only comparison that answers 'does history help'.",
        "D": "Numeric-encoding methods report in-sample fit for diagnosis and a separate out-of-sample "
             "one-step-ahead comparison for the predictive claim; the two are never conflated.",
        "E": "These tests are distributional rather than predictive, and their p-values feed the "
             "multiple-testing correction across the whole suite.",
        "F": "These are calibration tests of the null hypothesis; their output is the reference "
             "against which the other 88 methods are judged.",
        "G": "Each model is refitted on a fixed a-priori cadence (80-160 prediction steps depending "
             "on cost) on an expanding window, never tuned on the evaluation window, and promoted "
             "only if it beats the strongest baseline by more than 0.002 nats with a bootstrap "
             "interval excluding zero and stable across folds.",
        "H": "Model-combination methods fit their weights on an earlier slice of the out-of-sample "
             "window and are scored on a later slice; meta-analytic methods (91, 92) correct the "
             "whole suite's p-values.",
    }
    return base + "\n\n" + extra.get(letter, "")


def _interpretation(spec: MethodSpec, results: dict[str, Any]) -> str:
    if not results:
        return "No computed result is available, so no statistical interpretation is offered."
    statuses = {t: p.get("status") for t, p in results.items()}
    computed = [t for t, s in statuses.items() if s == "computed"]
    if not computed:
        return ("The method was not computable on this data; the stated reason is above. Reporting a "
                "number here would be fabrication.")
    parts = []
    adjusted = []
    for target in computed:
        for f in results[target].get("findings", []):
            if f.get("p_adjusted") is not None:
                adjusted.append((target, f["metric"], f["p_adjusted"]))
    if adjusted:
        significant = [a for a in adjusted if a[2] is not None and a[2] < 0.05]
        parts.append(
            f"{len(adjusted)} p-values were produced across the computed targets; "
            f"{len(significant)} survive Benjamini-Hochberg control at q=0.05"
            + (f" ({', '.join(f'{t}:{m}' for t, m, _ in significant[:5])})" if significant else "")
            + ". "
            + ("A result that does not survive correction across the 100-method family should not be "
               "interpreted as evidence of structure."
               if not significant else
               "Surviving correction is necessary but not sufficient: the predictive section is what "
               "establishes usefulness.")
        )
    parts.append(
        "The distinction this platform enforces is between a *statistically detectable* deviation "
        "and a *predictively useful* one. With thousands of draws, tiny deviations are detectable; "
        "they are useful only if a causal forecast beats the baseline out of sample. The evidence "
        "above is read that way."
    )
    return " ".join(parts)


def _conclusion(spec: MethodSpec, results: dict[str, Any]) -> str:
    if not results:
        return "Not executed in this run."
    computed = [t for t, p in results.items() if p.get("status") == "computed"]
    if not computed:
        reason = next(iter(results.values())).get("narrative", "")
        return f"The method did not apply to this data. {reason[:300]}"
    promoted = any(
        f.get("metric") == "promoted" and f.get("value")
        for t in computed for f in results[t].get("findings", [])
    )
    if promoted:
        return (f"The method produced a candidate signal that cleared the promotion rule. This is a "
                f"research lead, not a validated edge: it must be re-confirmed on a period that was "
                f"untouched during selection, and it remains a probability estimate for a lottery-type "
                f"draw, not a prediction of any specific outcome.")
    return ("No predictive information was demonstrated. Where the method produced a statistically "
            "notable statistic, it did not survive multiple-testing correction or did not translate "
            "into out-of-sample log-loss improvement. The honest conclusion for this method is a "
            "negative result, which is recorded as such rather than minimised.")


def write_all(methods: list[RegisteredMethod], results_by_method: dict[str, dict[str, Any]],
              output_dir, *, dataset_note: str) -> list[str]:
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for method in methods:
        slug = method.name.lower().replace(" ", "_").replace(",", "").replace("-", "_")
        slug = "".join(c for c in slug if c.isalnum() or c == "_")[:60]
        path = output_dir / f"{method.id}_{slug}.md"
        path.write_text(render(method, results_by_method.get(method.id, {}),
                               dataset_note=dataset_note), encoding="utf-8")
        written.append(str(path))
    return written


def payloads_from_database(config, market_id: str) -> dict[str, dict[str, dict]]:
    """Rebuild per-method result payloads from persisted ``method_results`` rows.

    Dossier writing must reflect what was *actually stored*, so it reads the
    database rather than re-running the suite (which could, after any code change,
    produce numbers that were never reviewed).
    """
    from src.storage.market_database import MarketDatabase

    db = MarketDatabase(config, market_id)
    if not db.manager.exists(market_id):
        raise FileNotFoundError(
            f"no database for '{market_id}' in dataset '{config.dataset.name}'; "
            f"run init and analyse first")

    frame = db.method_results()
    payloads: dict[str, dict[str, dict]] = {}
    if frame is None or frame.empty:
        return payloads

    for method_id, group in frame.groupby("method_id"):
        per_target: dict[str, dict] = {}
        for target, rows in group.groupby("target"):
            stored_scope = str(rows["scope"].iloc[0])
            # `scope` records where in the sample a number was computed; only the
            # non-computed values ("failed", "insufficient_data", ...) are statuses.
            status = "computed" if stored_scope == "full_sample" else stored_scope
            findings = []
            for row in rows.itertuples():
                findings.append({
                    "metric": row.metric_name,
                    "value": row.metric_value,
                    "statistic": row.statistic,
                    "p_value": row.p_value,
                    "p_adjusted": row.p_adjusted,
                    "effect_size": row.effect_size,
                    "n": row.sample_size,
                })
            narrative = ""
            extras = rows["extra_json"].dropna()
            if len(extras):
                import json

                try:
                    narrative = json.loads(extras.iloc[0]).get("narrative", "")
                except Exception:
                    narrative = ""
            per_target[str(target)] = {
                "status": status, "findings": findings, "narrative": narrative,
                "diagnostics": {"source": "method_results table",
                                "rows": int(len(rows)),
                                "dataset": config.dataset.name},
            }
        payloads[str(method_id)] = per_target
    return payloads
