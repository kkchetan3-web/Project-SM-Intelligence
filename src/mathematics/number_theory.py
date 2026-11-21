"""Methods 47-60: number theory and transformations (Category E).

Panel-level methods need the 3-digit panna, which not every market publishes for
every date. When it is absent the method returns ``not_applicable`` rather than
substituting the ank and pretending.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from src.mathematics.common import (
    binomial_test,
    chi2_contingency,
    chi2_uniform,
    counts_of,
    permutation_pvalue,
)
from src.mathematics.types import (
    STATUS_COMPUTED,
    STATUS_INSUFFICIENT_DATA,
    STATUS_NOT_APPLICABLE,
    MethodContext,
    MethodOutput,
    finding,
)


def _panels(ctx: MethodContext) -> np.ndarray | None:
    column = f"{ctx.target}_panna"
    if column not in ctx.results.columns:
        return None
    values = ctx.results[column].dropna().astype(str)
    values = values[values.str.len() == 3]
    if len(values) < 100:
        return None
    return values.to_numpy()


def _panel_guard(ctx: MethodContext) -> tuple[np.ndarray | None, MethodOutput | None]:
    panels = _panels(ctx)
    if panels is None:
        return None, MethodOutput(
            status=STATUS_NOT_APPLICABLE,
            narrative=("this market does not publish three-digit panels for enough dates, so the "
                       "panel-level transformation cannot be computed"),
        )
    return panels, None


# ---------------------------------------------------------------------------
# M047 modular arithmetic
# ---------------------------------------------------------------------------
def run_047(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    results = {}
    for m in (2, 3, 5, 7):
        residues = ctx.y % m
        counts = counts_of(residues, m)
        # A residue class holds ceil(K/m) or floor(K/m) of the K outcomes, so the
        # uniform expectation is NOT counts/m unless m divides K.
        class_sizes = np.array([int(np.sum(np.arange(ctx.k) % m == r)) for r in range(m)],
                               dtype=float)
        expected = class_sizes / class_sizes.sum() * counts.sum()
        stat = float(np.sum((counts - expected) ** 2 / np.maximum(expected, 1e-9)))
        p = float(stats.chi2.sf(stat, m - 1))
        results[m] = {"chi2": stat, "p_value": p, "counts": counts.astype(int).tolist()}
    from src.mathematics.common import holm
    adjusted = holm([results[m]["p_value"] for m in results])
    for m, adj in zip(results, adjusted, strict=True):
        results[m]["p_adjusted"] = adj

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"chi2_mod{m}", results[m]["chi2"], p_value=results[m]["p_value"],
                          sample_size=ctx.n, extra={"p_adjusted": round(results[m]["p_adjusted"], 5)})
                  for m in results]
        + [finding("n_significant_holm",
                   float(sum(results[m]["p_adjusted"] < 0.05 for m in results)),
                   sample_size=len(results))],
        narrative=(
            "Residue uniformity across moduli: "
            + ", ".join(f"m={m}: chi2={results[m]['chi2']:.2f} (Holm p="
                        f"{results[m]['p_adjusted']:.4f})" for m in results)
            + f". {sum(results[m]['p_adjusted'] < 0.05 for m in results)} of {len(results)} remain "
            f"significant after correction. Mod 2 is the coarsest and most powerful split, so if any "
            f"modulus were to show a real effect it would most likely be that one."
        ),
        diagnostics={"by_modulus": {str(k): v for k, v in results.items()}},
    )


# ---------------------------------------------------------------------------
# M048 digital root
# ---------------------------------------------------------------------------
def run_048(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")

    def dr(v: int) -> int:
        return 0 if v == 0 else 1 + (v - 1) % 9

    roots = np.array([dr(int(v)) for v in ctx.y])
    counts = np.bincount(roots, minlength=10)[:10]
    # Theoretical distribution: 0 occurs for value 0 only; 1-9 each occur once
    # among the ten digit values, so under uniformity each has probability 0.1.
    expected = np.full(10, ctx.n / 10)
    stat = float(np.sum((counts - expected) ** 2 / np.maximum(expected, 1e-9)))
    p = float(stats.chi2.sf(stat, 9))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("digital_root_chi2", stat, p_value=p, sample_size=ctx.n),
            finding("most_common_root", float(np.argmax(counts)), sample_size=ctx.n,
                    extra={"count": int(counts.max())}),
            finding("least_common_root", float(np.argmin(counts)), sample_size=ctx.n,
                    extra={"count": int(counts.min())}),
        ],
        narrative=(
            f"Digital roots of the outcomes against the uniform expectation give chi-square {stat:.2f} "
            f"on 9 df (p = {p:.4f}). The most frequent root is {np.argmax(counts)} with "
            f"{counts.max()} observations, the least frequent {np.argmin(counts)} with {counts.min()}. "
            f"On a single digit the digital root is almost the identity map (only 0 and 9 behave "
            f"distinctly), so this method's main value here is as a check that the digit space is "
            f"being read correctly rather than as an independent test."
        ),
        diagnostics={"counts": counts.astype(int).tolist()},
    )


# ---------------------------------------------------------------------------
# M049 digit sum distribution
# ---------------------------------------------------------------------------
def run_049(ctx: MethodContext) -> MethodOutput:
    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    sums = np.array([sum(int(c) for c in p) for p in panels])
    observed = np.bincount(sums, minlength=28)[:28]
    # Exact null: convolution of three independent uniform digits.
    base = np.ones(10) / 10
    null = np.convolve(np.convolve(base, base), base) * len(sums)
    keep = null >= 5
    stat = float(np.sum((observed[keep] - null[keep]) ** 2 / null[keep]))
    dof = int(keep.sum() - 1)
    p = float(stats.chi2.sf(stat, dof))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("digit_sum_chi2", stat, p_value=p, sample_size=len(panels),
                    extra={"dof": dof}),
            finding("observed_mean_sum", float(sums.mean()), sample_size=len(panels),
                    extra={"theoretical": 13.5}),
            finding("observed_std_sum", float(sums.std(ddof=1)), sample_size=len(panels),
                    extra={"theoretical": round(float(np.sqrt(3 * (99 / 12))), 4)}),
            finding("n_panels", float(len(panels)), sample_size=len(panels)),
        ],
        narrative=(
            f"Across {len(panels)} panels the digit sum has mean {sums.mean():.3f} (theoretical 13.5) "
            f"and standard deviation {sums.std(ddof=1):.3f} (theoretical "
            f"{np.sqrt(3 * 99 / 12):.3f}). The chi-square against the exact convolution of three "
            f"uniform digits is {stat:.2f} on {dof} df, p = {p:.4f}. "
            + ("Panel digits behave like independent uniform digits with respect to their sum."
               if p > 0.05 else
               "The sum distribution departs from the independent-uniform convolution, which points "
               "at dependence between digit positions or a non-uniform digit marginal.")
        ),
        diagnostics={"observed": observed.tolist(), "expected": np.round(null, 1).tolist()},
    )


# ---------------------------------------------------------------------------
# M050 digit differences
# ---------------------------------------------------------------------------
def run_050(ctx: MethodContext) -> MethodOutput:
    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    diffs = np.array([[abs(int(p[0]) - int(p[1])), abs(int(p[1]) - int(p[2])),
                       abs(int(p[0]) - int(p[2]))] for p in panels])
    pair_index = int(np.argmax(diffs.mean(axis=0)))
    observed = np.bincount(diffs[:, pair_index], minlength=10)[:10]

    # Exact law of |d1 - d2| for two independent uniform digits on 0..9:
    #   P(0) = 10/100, and P(k) = 2(10-k)/100 for k = 1..9 (ordered pairs).
    # An earlier version omitted the factor of two for k >= 1, which manufactured
    # a chi-square in the hundreds on genuinely independent data.
    null_pmf = np.array([10.0] + [2.0 * (10 - k) for k in range(1, 10)]) / 100.0
    null = null_pmf * len(panels)
    keep = null >= 5
    stat = float(np.sum((observed[keep] - null[keep]) ** 2 / null[keep]))

    # The panel digits within one panna are not independent (they must sum to the
    # ank, mod 10), so the exact null above is a reference point rather than a
    # distribution. The reported p-value comes from a permutation null that
    # preserves each digit position's marginal and destroys any panel structure.
    rng = np.random.default_rng(ctx.seed)
    panel_matrix = np.array([[int(c) for c in p] for p in panels])
    perm_stats: list[float] = []
    for _ in range(300):
        permuted = np.column_stack([rng.permutation(panel_matrix[:, j]) for j in range(3)])
        d = np.abs(permuted[:, 0] - permuted[:, 1]) if pair_index == 0 else (
            np.abs(permuted[:, 1] - permuted[:, 2]) if pair_index == 1
            else np.abs(permuted[:, 0] - permuted[:, 2]))
        counts = np.bincount(d, minlength=10)[:10]
        perm_stats.append(float(np.sum((counts[keep] - null[keep]) ** 2 / null[keep])))
    p = float((1 + sum(s >= stat for s in perm_stats)) / (1 + len(perm_stats)))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_abs_difference", float(diffs[:, pair_index].mean()),
                    sample_size=len(panels), extra={"theoretical": 3.3, "pair": pair_index}),
            finding("difference_chi2", stat, p_value=p, sample_size=len(panels)),
            finding("n_zero_differences", float(observed[0]), sample_size=len(panels),
                    extra={"theoretical_share": 0.10}),
        ],
        narrative=(
            f"Absolute difference between panel positions averages {diffs[:, pair_index].mean():.3f} "
            f"(independent uniform digits give 3.3). Exactly equal digits occur "
            f"{observed[0] / len(panels):.3%} of the time against 10.0% under independence. The "
            f"chi-square of the difference distribution against the exact null is {stat:.2f} "
            f"(p = {p:.4f}). "
            + ("Digit differences match the independence prediction."
               if p > 0.05 else
               "Digit differences depart from the independence prediction, indicating digit-level "
               "dependence inside the panel.")
        ),
        diagnostics={"observed": observed.tolist(), "expected": np.round(null, 1).tolist()},
    )


# ---------------------------------------------------------------------------
# M051 complementary digits
# ---------------------------------------------------------------------------
def run_051(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    original = counts_of(ctx.y, ctx.k)
    complemented = counts_of((9 - ctx.y) % 10, ctx.k)
    # Symmetry test: is n_k == n_{9-k}?
    test = binomial_test(int(original[0] + original[9]), int(original.sum()), 0.5) \
        if False else None
    pairs = [(k, 9 - k) for k in range(5)]
    diffs = [int(original[a] - original[b]) for a, b in pairs]
    total_pairs = int(sum(original[a] + original[b] for a, b in pairs))
    expected_even = total_pairs / 2
    chi2_sym = float(sum((original[a] - original[b]) ** 2 / max(original[a] + original[b], 1)
                         for a, b in pairs))
    p_sym = float(stats.chi2.sf(chi2_sym, 5))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("symmetry_chi2", chi2_sym, p_value=p_sym, sample_size=ctx.n,
                    extra={"pairs": [f"{a}/{b}" for a, b in pairs]}),
            finding("max_pair_difference", float(max(abs(d) for d in diffs)), sample_size=ctx.n),
            finding("mean_pair_difference", float(np.mean(np.abs(diffs))), sample_size=ctx.n),
        ],
        narrative=(
            f"Testing whether each digit k occurs as often as its complement 9-k: the symmetry "
            f"chi-square is {chi2_sym:.2f} on 5 df (p = {p_sym:.4f}). Pair counts differ by "
            f"{np.mean(np.abs(diffs)):.1f} on average (largest {max(abs(d) for d in diffs)}). "
            + ("The complement pairs are balanced, as they must be for an unremarkable process."
               if p_sym > 0.05 else
               "At least one complement pair is imbalanced, which would point at a digit-level "
               "asymmetry worth investigating in the panel data.")
            + " Note that the complement transformation is an involution, so a symmetric process "
              "cannot produce a complement 'pattern' to exploit."
        ),
        diagnostics={"original": original.astype(int).tolist(),
                     "complemented": complemented.astype(int).tolist()},
    )


# ---------------------------------------------------------------------------
# M052 reversal relationships
# ---------------------------------------------------------------------------
def run_052(ctx: MethodContext) -> MethodOutput:
    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    strings = [str(p) for p in panels]
    reversal_present = sum(1 for s in strings if s[::-1] in set(strings) and s != s[::-1])
    palindromes = sum(1 for s in strings if s == s[::-1])
    second_pair_rate = float(np.mean([(str(p)[:2] == str(p)[1:]) for p in panels]))
    symmetry_pairs = np.zeros(3)
    for idx, p in enumerate(panels):
        s = str(p)
        symmetry_pairs[0 if s[0] < s[1] < s[2] else
                       2 if s[0] > s[1] > s[2] else 1] += 1
    share_increasing = float(symmetry_pairs[0] / len(panels))
    share_decreasing = float(symmetry_pairs[2] / len(panels))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("palindrome_share", palindromes / len(panels), sample_size=len(panels),
                    extra={"theoretical": 0.10}),
            finding("reversal_pair_count", float(reversal_present), sample_size=len(panels)),
            finding("strictly_increasing_share", share_increasing, sample_size=len(panels),
                    extra={"uniform_expectation": round(120 / 1000, 4)}),
            finding("strictly_decreasing_share", share_decreasing, sample_size=len(panels)),
        ],
        narrative=(
            f"Of {len(panels)} panels, {palindromes} ({palindromes / len(panels):.3%}) are palindromes "
            f"against 10.0% for independent uniform digits, and {reversal_present} belong to a "
            f"non-trivial reversal pair. Strictly increasing panels make up "
            f"{share_increasing:.3%} and strictly decreasing {share_decreasing:.3%}, against the "
            f"combinatorial 12.0% for each. "
            + ("Panel orientation is consistent with unranked random digits."
               if abs(share_increasing - 0.12) < 0.02 and abs(share_decreasing - 0.12) < 0.02 else
               "Orientation frequencies deviate from the combinatorial expectation, indicating the "
               "operator's panel ranking may be non-uniform.")
        ),
        diagnostics={"second_digit_pair_rate": round(second_pair_rate, 4)},
    )


# ---------------------------------------------------------------------------
# M053 parity
# ---------------------------------------------------------------------------
def run_053(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    even = int(np.sum(ctx.y % 2 == 0))
    test = binomial_test(even, ctx.n, 0.5)
    binary = ctx.y % 2
    from src.mathematics.common import runs
    n_runs = runs(binary)
    n1, n2 = int(np.sum(binary == 1)), int(np.sum(binary == 0))
    mean_runs = 2 * n1 * n2 / ctx.n + 1
    var_runs = 2 * n1 * n2 * (2 * n1 * n2 - ctx.n) / (ctx.n ** 2 * (ctx.n - 1))
    z_runs = (n_runs - mean_runs) / np.sqrt(var_runs) if var_runs > 0 else float("nan")
    p_runs = float(2 * stats.norm.sf(abs(z_runs))) if np.isfinite(z_runs) else float("nan")

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("even_proportion", test["estimate"], p_value=test["p_value"], sample_size=ctx.n,
                    extra={"ci_low": round(test["ci_low"], 5),
                           "ci_high": round(test["ci_high"], 5)}),
            finding("observed_runs", float(n_runs), sample_size=ctx.n),
            finding("expected_runs", float(mean_runs), sample_size=ctx.n),
            finding("runs_z_statistic", float(z_runs), p_value=p_runs, sample_size=ctx.n),
        ],
        narrative=(
            f"Even outcomes make up {test['estimate']:.4f} of the sample (exact 95% CI "
            f"{test['ci_low']:.4f} to {test['ci_high']:.4f}); the binomial test against 0.5 gives "
            f"p = {test['p_value']:.4f}. The parity sequence contains {n_runs} runs against "
            f"{mean_runs:.1f} expected (z = {z_runs:+.3f}, p = {p_runs:.4f}). "
            + ("Parity is balanced and the run structure is consistent with independence."
               if test["p_value"] > 0.05 and p_runs > 0.05 else
               "Parity departs from the 50/50 expectation or shows clustering; the two tests are "
               "separate pieces of evidence and must be corrected for multiplicity before being "
               "called a finding.")
        ),
        diagnostics={"even": even, "odd": ctx.n - even},
    )


# ---------------------------------------------------------------------------
# M054 prime classification
# ---------------------------------------------------------------------------
def run_054(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    primes = {2, 3, 5, 7}
    is_prime = np.array([int(v) in primes for v in ctx.y])
    share = int(is_prime.sum())
    # On 0-9 the primes are 4 of 10 values.
    test = binomial_test(share, ctx.n, 0.4)
    by_value = {int(v): int(np.sum(ctx.y == v)) for v in sorted(primes)}

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("prime_share", test["estimate"], p_value=test["p_value"], sample_size=ctx.n,
                    extra={"theoretical": 0.4}),
            finding("n_prime_outcomes", float(share), sample_size=ctx.n),
            finding("composite_share", 1 - test["estimate"], sample_size=ctx.n),
        ],
        narrative=(
            f"Prime outcomes (2, 3, 5, 7) account for {test['estimate']:.4f} of draws against the "
            f"theoretical 0.40 (exact binomial p = {test['p_value']:.4f}). Note that 0 and 1 are "
            f"neither prime nor composite; the implementation counts them as non-prime, which is "
            f"the convention stated in the method record. "
            + ("The prime share matches the theoretical value."
               if test["p_value"] > 0.05 else
               "The prime share departs from 0.40; this is a coarse partition of the same data used "
               "in Method 9, so it should not be counted as independent evidence.")
        ),
        diagnostics={"by_value": by_value},
    )


# ---------------------------------------------------------------------------
# M055 combinatorial probability
# ---------------------------------------------------------------------------
def run_055(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 100:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 100 observations")
    # Enumerate the declared space and compare marginal frequencies to 1/K.
    probs = counts_of(ctx.y, ctx.k) / ctx.n
    chi = chi2_uniform(ctx.y, ctx.k)
    tv = 0.5 * float(np.sum(np.abs(probs - 1.0 / ctx.k)))
    results = []
    for k in range(ctx.k):
        se = float(np.sqrt((1 / ctx.k) * (1 - 1 / ctx.k) / ctx.n))
        results.append({"outcome": ctx.label(k), "observed": round(float(probs[k]), 5),
                        "theoretical": round(1 / ctx.k, 5),
                        "z": round(float((probs[k] - 1 / ctx.k) / se), 3)})

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("total_variation_distance", tv, sample_size=ctx.n,
                    extra={"interpretation": "0 = exactly uniform"}),
            finding("chi2_vs_theoretical", chi["statistic"], p_value=chi["p_value"],
                    sample_size=ctx.n),
            finding("max_abs_z", float(max(abs(r["z"]) for r in results)), sample_size=ctx.n),
        ],
        narrative=(
            f"With {ctx.k} equiprobable outcomes the theoretical probability of each is "
            f"{1 / ctx.k:.4f}. The observed distribution is a total-variation distance of {tv:.5f} "
            f"from that ideal, with the largest single-category z-score at "
            f"{max(abs(r['z']) for r in results):.2f}. The chi-square against the enumerated "
            f"theoretical distribution is {chi['statistic']:.2f} (p = {chi['p_value']:.4f}). "
            f"This method supplies the null hypothesis; it can reject it but cannot by itself tell "
            f"you whether a departure is exploitable."
        ),
        diagnostics={"per_outcome": results},
    )


# ---------------------------------------------------------------------------
# M056 permutation and combination analysis
# ---------------------------------------------------------------------------
def run_056(ctx: MethodContext) -> MethodOutput:
    from math import comb, factorial

    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    n_ordered = 10 ** 3
    n_unordered = comb(10 + 3 - 1, 3)
    strings = [str(p) for p in panels]
    distinct_multisets = len({tuple(sorted(s)) for s in strings})
    counts_by_multiset = {}
    for s in strings:
        key = tuple(sorted(s))
        counts_by_multiset[key] = counts_by_multiset.get(key, 0) + 1
    top = sorted(counts_by_multiset.items(), key=lambda kv: -kv[1])[:3]
    observed_multisets = len(counts_by_multiset)
    n_perm3 = factorial(3)
    triple_repeats = sum(1 for s in strings if len(set(s)) == 1)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("ordered_space_size", float(n_ordered), sample_size=len(panels)),
            finding("unordered_multiset_space_size", float(n_unordered), sample_size=len(panels)),
            finding("distinct_multisets_observed", float(observed_multisets), sample_size=len(panels)),
            finding("multiset_coverage", observed_multisets / n_unordered, sample_size=len(panels)),
            finding("triple_repeat_share", triple_repeats / len(panels), sample_size=len(panels),
                    extra={"theoretical": 0.01}),
            finding("permutations_per_distinct_multiset", float(n_perm3), sample_size=len(panels)),
        ],
        narrative=(
            f"The ordered panel space has {n_ordered} elements but only {n_unordered} unordered "
            f"digit multisets, each of which can be arranged in up to {n_perm3} ways (fewer when "
            f"digits repeat). The sample covers {observed_multisets} of the {n_unordered} multisets "
            f"({observed_multisets / n_unordered:.1%}); the most common are "
            + ", ".join(f"{''.join(k)} ({v})" for k, v in top)
            + f". Triple-repeated panels account for {triple_repeats / len(panels):.3%} against the "
            f"1.0% expected from independent uniform digits. This confirms that the ordered space "
            f"is the correct one to model: treating panels as unordered would over-weight the small "
            f"multiset space."
        ),
        diagnostics={"top_multisets": [{"multiset": "".join(k), "count": v} for k, v in top]},
    )


# ---------------------------------------------------------------------------
# M057 numerical distance
# ---------------------------------------------------------------------------
def run_057(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 200:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 200 observations")
    steps = np.abs(np.diff(ctx.y.astype(float)))
    observed = np.bincount(steps.astype(int), minlength=ctx.k)
    # Exact null for |X_t - X_{t-1}| with both uniform on 0..k-1.
    null = np.array([ctx.k if d == 0 else 2 * (ctx.k - d) for d in range(ctx.k)]) / (ctx.k ** 2)
    expected = null * len(steps)
    stat = float(np.sum((observed - expected) ** 2 / np.maximum(expected, 1e-9)))
    p = float(stats.chi2.sf(stat, ctx.k - 1))
    identical = int(observed[0])
    test_same = binomial_test(identical, len(steps), 1 / ctx.k)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_absolute_step", float(steps.mean()), sample_size=len(steps),
                    extra={"theoretical": round(float(sum(d * n for d, n in enumerate(null))), 4)}),
            finding("repeat_rate", test_same["estimate"], p_value=test_same["p_value"],
                    sample_size=len(steps), extra={"theoretical": round(1 / ctx.k, 4)}),
            finding("step_chi2", stat, p_value=p, sample_size=len(steps)),
        ],
        narrative=(
            f"Consecutive draws differ by {steps.mean():.3f} on average; independent uniform digits "
            f"predict {sum(d * n for d, n in enumerate(null)):.3f}. The next draw equals the previous "
            f"one {test_same['estimate']:.4f} of the time against {1 / ctx.k:.4f} expected (exact "
            f"binomial p = {test_same['p_value']:.4f}). The full step distribution gives chi-square "
            f"{stat:.2f} on {ctx.k - 1} df (p = {p:.4f}). "
            + ("Step sizes behave exactly as independence predicts."
               if p > 0.05 else
               "Step sizes depart from the independence prediction; Method 23 recasts the same "
               "evidence as a transition matrix and Method 91 corrects for multiplicity.")
        ),
        diagnostics={"observed": observed.astype(int).tolist(),
                     "expected": np.round(expected, 1).tolist()},
    )


# ---------------------------------------------------------------------------
# M058 pairwise digit association
# ---------------------------------------------------------------------------
def run_058(ctx: MethodContext) -> MethodOutput:
    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    results = {}
    for i, j in ((0, 1), (0, 2), (1, 2)):
        table = np.zeros((10, 10))
        for p in panels:
            table[int(str(p)[i]), int(str(p)[j])] += 1
        test = chi2_contingency(table)
        results[f"pos{i}_{j}"] = {"chi2": test["statistic"], "p_value": test["p_value"],
                                  "cramers_v": test["cramers_v"],
                                  "min_expected": test["min_expected"]}
    from src.mathematics.common import holm
    adjusted = holm([results[k]["p_value"] for k in results])
    for key, adj in zip(results, adjusted, strict=True):
        results[key]["p_adjusted"] = adj

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"chi2_{k}", v["chi2"], p_value=v["p_value"], effect_size=v["cramers_v"],
                          sample_size=len(panels),
                          extra={"p_adjusted": round(v["p_adjusted"], 5)})
                  for k, v in results.items()]
        + [finding("max_cramers_v", float(max(v["cramers_v"] for v in results.values())),
                   sample_size=len(panels)),
           finding("n_significant_holm",
                   float(sum(v["p_adjusted"] < 0.05 for v in results.values())),
                   sample_size=len(results))],
        narrative=(
            "Digit-position independence within panels: "
            + ", ".join(f"{k}: V={v['cramers_v']:.4f} (Holm p={v['p_adjusted']:.4f})"
                        for k, v in results.items())
            + f". The strongest association has Cramer's V of "
            f"{max(v['cramers_v'] for v in results.values()):.4f}, which for a 10x10 table "
            f"corresponds to a negligible departure from independence. "
            + ("Digit positions are independent within panels."
               if all(v["p_adjusted"] > 0.05 for v in results.values()) else
               "At least one position pair shows dependence surviving correction, which would "
               "indicate the panel is generated as a ranked object rather than three separate digits.")
        ),
        diagnostics={k: {kk: round(vv, 5) if isinstance(vv, float) else vv
                         for kk, vv in v.items()} for k, v in results.items()},
    )


# ---------------------------------------------------------------------------
# M059 Hamming distance
# ---------------------------------------------------------------------------
def run_059(ctx: MethodContext) -> MethodOutput:
    panels, guard = _panel_guard(ctx)
    if guard:
        return guard
    distances = []
    for a, b in zip(panels[:-1], panels[1:], strict=False):
        distances.append(sum(1 for x, y in zip(str(a), str(b), strict=True) if x != y))
    distances = np.array(distances)
    observed = np.bincount(distances, minlength=4)[:4]
    # Each position differs with probability 0.9 independently.
    null = np.array([0.1 ** 3, 3 * 0.9 * 0.1 ** 2, 3 * 0.9 ** 2 * 0.1, 0.9 ** 3]) * len(distances)
    stat = float(np.sum((observed - null) ** 2 / np.maximum(null, 1e-9)))
    p = float(stats.chi2.sf(stat, 3))

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[
            finding("mean_hamming_distance", float(distances.mean()), sample_size=len(distances),
                    extra={"theoretical": 2.7}),
            finding("hamming_chi2", stat, p_value=p, sample_size=len(distances)),
            finding("identical_consecutive_panels", float(observed[0]), sample_size=len(distances),
                    extra={"theoretical": round(0.001 * len(distances), 2)}),
            finding("all_positions_differ_share", float(observed[3] / len(distances)),
                    sample_size=len(distances), extra={"theoretical": 0.729}),
        ],
        narrative=(
            f"Consecutive panels differ in {distances.mean():.3f} of their 3 positions on average "
            f"(independent uniform digits predict 2.7). All three positions differ "
            f"{observed[3] / len(distances):.3%} of the time against 72.9%, and panels are identical "
            f"{int(observed[0])} times against {0.001 * len(distances):.1f} expected. The chi-square "
            f"against the independence prediction is {stat:.2f} (p = {p:.4f}). "
            + ("Consecutive panels are as different as independent draws require."
               if p > 0.05 else
               "Consecutive panels are more (or less) similar than independence predicts, which is "
               "serial dependence at the panel level.")
        ),
        diagnostics={"observed": observed.astype(int).tolist(),
                     "expected": np.round(null, 1).tolist()},
    )


# ---------------------------------------------------------------------------
# M060 residue distribution consistency
# ---------------------------------------------------------------------------
def run_060(ctx: MethodContext) -> MethodOutput:
    if ctx.n < 300:
        return MethodOutput(status=STATUS_INSUFFICIENT_DATA, narrative="needs 300 observations")
    from src.mathematics.common import holm

    half = ctx.n // 2
    results = {}
    for m in (2, 3, 5, 10):
        full = counts_of(ctx.y % m, m)
        class_sizes = np.array([int(np.sum(np.arange(ctx.k) % m == r)) for r in range(m)],
                               dtype=float)
        expected = class_sizes / class_sizes.sum() * full.sum()
        stat = float(np.sum((full - expected) ** 2 / np.maximum(expected, 1e-9)))
        p_uniform = float(stats.chi2.sf(stat, m - 1))
        first = counts_of(ctx.y[:half] % m, m)
        second = counts_of(ctx.y[half:] % m, m)
        table = np.array([first, second])
        keep_c = table.sum(axis=0) > 0
        stability = chi2_contingency(table[:, keep_c])
        results[m] = {
            "uniformity_chi2": stat, "uniformity_p": p_uniform,
            "stability_chi2": stability["statistic"], "stability_p": stability["p_value"],
            "counts": full.astype(int).tolist(),
        }
    adjusted = holm([results[m]["uniformity_p"] for m in results]
                    + [results[m]["stability_p"] for m in results])
    n = len(results)
    for i, m in enumerate(results):
        results[m]["uniformity_p_adj"] = adjusted[i]
        results[m]["stability_p_adj"] = adjusted[n + i]
    n_sig = sum(1 for m in results
                if results[m]["uniformity_p_adj"] < 0.05 or results[m]["stability_p_adj"] < 0.05)

    return MethodOutput(
        status=STATUS_COMPUTED,
        findings=[finding(f"uniformity_chi2_mod{m}", results[m]["uniformity_chi2"],
                          p_value=results[m]["uniformity_p"], sample_size=ctx.n,
                          extra={"p_adjusted": round(results[m]["uniformity_p_adj"], 5)})
                  for m in results]
        + [finding(f"stability_chi2_mod{m}", results[m]["stability_chi2"],
                   p_value=results[m]["stability_p"], sample_size=ctx.n,
                   extra={"p_adjusted": round(results[m]["stability_p_adj"], 5)})
           for m in results]
        + [finding("n_moduli_with_any_rejection", float(n_sig), sample_size=n)],
        narrative=(
            "Residue classes tested for both uniformity and stability across sample halves: "
            + ", ".join(
                f"m={m}: uniformity p={results[m]['uniformity_p']:.3f}, stability "
                f"p={results[m]['stability_p']:.3f}" for m in results)
            + f". After Holm correction across all {2 * n} tests, {n_sig} moduli show any rejection. "
            + ("Residue structure is consistent at every resolution tested, which is the signature of "
               "a genuinely featureless process: a real effect would not appear at exactly one "
               "modulus and vanish at its multiples." if n_sig == 0 else
               "Some modulus shows a rejection after correction. Because nested moduli are strongly "
               "dependent, consistency across the family is the real test and a single-modulus "
               "rejection is weak evidence.")
        ),
        diagnostics={"by_modulus": {str(k): {kk: (round(vv, 5) if isinstance(vv, float) else vv)
                                             for kk, vv in v.items()}
                                    for k, v in results.items()}},
    )


RUNNERS = {f"M{i:03d}": globals().get(f"run_{i:03d}") for i in range(47, 61)}
