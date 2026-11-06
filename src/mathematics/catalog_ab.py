"""Documentation records for Methods 1-22 (Categories A and B).

Every record carries the definition, mathematical foundation, objective,
assumptions, formula, per-variable glossary, manual-calculation steps, data
requirements and limitations. The executable half lives in the corresponding
``src/mathematics/*.py`` module named in ``implementation``.
"""

from __future__ import annotations

from src.mathematics.types import MethodSpec

A = "A - Frequency and Probability"
B = "B - Recency and Occurrence"


def M(mid, name, category, formula, theory, objective, assumptions, variables,
      steps, limitations, data_requirements, implementation, references=""):
    return MethodSpec(
        id=mid, name=name, category=category, formula=formula, theory=theory,
        objective=objective, assumptions=tuple(assumptions),
        variables=tuple(variables), steps=tuple(steps), limitations=limitations,
        data_requirements=data_requirements, implementation=implementation,
        references=references,
    )


METHODS_AB = [
    M("M001", "Absolute Frequency Analysis", A,
      r"n_k = \sum_{t=1}^{N} \mathbf{1}[X_t = k]",
      "In a categorical sequence the vector of counts (n_1..n_K) is a sufficient statistic for the "
      "empirical distribution: no other feature of the sample adds information about relative "
      "category occurrence. Counts therefore anchor every later method, and any claim about a "
      "'hot' number must ultimately be a claim about n_k.",
      "Establish the raw empirical support of every outcome before any modelling.",
      ["Each draw is assigned to exactly one category",
       "Observations are counted within a declared, fixed outcome space"],
      [("n_k", "count of outcome k"), ("X_t", "outcome at observation t"),
       ("N", "number of valid observations"), ("K", "size of the outcome space")],
      ["Scan the chronological series and tally each outcome",
       "Order categories by descending count",
       "Report counts alongside N so proportions can be derived"],
      "Counts are descriptive. A large n_k does not make k more likely next; that inference "
      "requires the distributional tests in M009-M010.",
      "Any non-empty sequence; K is fixed by the market's declared outcome space.",
      "src.mathematics.frequency::run_001"),

    M("M002", "Relative Frequency Analysis", A,
      r"\hat{p}_k = \frac{n_k}{N}, \qquad \sum_{k=1}^{K}\hat{p}_k = 1",
      "Dividing counts by N gives the empirical measure, the maximum-likelihood estimate of the "
      "categorical probabilities. Its sampling variability is governed by the multinomial "
      "distribution, with Var(p_k) = p_k(1-p_k)/N, so deviations must be judged against that "
      "scale rather than by eye.",
      "Convert counts into probabilities and quantify how far the empirical distribution departs "
      "from the theoretical uniform baseline.",
      ["Draws are identically distributed within the estimation window",
       "Multinomial sampling applies"],
      [("p_k", "empirical probability of outcome k"), ("N", "total observations"),
       ("KL", "Kullback-Leibler divergence from uniform")],
      ["Divide each count by N", "Compute the maximum absolute deviation from 1/K",
       "Compute KL divergence and a chi-square-scale deviation"],
      "Relative frequency is a historical average. It is an unbiased estimate of a *stationary* "
      "probability, which the data may not possess.",
      "N >= 10 recommended for the deviations to be interpretable.",
      "src.mathematics.frequency::run_002"),

    M("M003", "Rolling Frequency Analysis", A,
      r"\hat{p}_{k,t} = \frac{1}{W}\sum_{i=t-W+1}^{t}\mathbf{1}[X_i=k]",
      "A moving window makes the empirical measure local in time, trading variance for "
      "adaptivity. If the generating process is stationary the rolling estimate is strictly worse "
      "than the expanding one; if it drifts, the rolling estimate can be better. Which holds is an "
      "empirical question answered by out-of-sample log loss.",
      "Test whether recent-window frequencies predict future draws better than long-run frequencies.",
      ["Window length W is chosen a priori", "The underlying process is locally homogeneous"],
      [("W", "window length in observations"), ("p_k,t", "smoothed probability at time t"),
       ("log loss", "mean negative log predictive density")],
      ["For each W in the configured grid, produce causal predictions",
       "Score every step with log loss",
       "Compare against the expanding-frequency and uniform baselines"],
      "Short windows are noisy (10 categories, W=25 gives about 2.5 observations per category); "
      "long windows cannot adapt. The grid search itself consumes sample.",
      "N > 5W to leave a usable out-of-sample window.",
      "src.mathematics.frequency::run_003"),

    M("M004", "Exponentially Weighted Frequency", A,
      r"w_k(t)=\sum_{i \le t}\lambda^{t-i}\mathbf{1}[X_i=k],\quad \hat{p}_k(t)=\frac{w_k(t)}{\sum_j w_j(t)}",
      "Exponential weighting generalises the hard window of M003 to a soft one: every past "
      "observation contributes, with weight decaying geometrically at rate lambda. The effective "
      "sample size is (1+lambda)/(1-lambda), so lambda=0.95 behaves like a window of about 39 draws "
      "and lambda=0.99 like about 199.",
      "Test whether smooth recency weighting improves forecasts over a fixed window.",
      ["The decay rate is constant over the evaluation window",
       "Recent draws are more informative than distant draws"],
      [("lambda", "per-step decay factor in (0,1)"),
       ("w_k", "accumulated weight for outcome k"),
       ("effective N", "(1+lambda)/(1-lambda)")],
      ["Set the weight vector to zero",
       "At each step multiply all weights by lambda and add one to the observed outcome",
       "Normalise to a probability vector and score causally"],
      "Lambda is a tuning parameter; optimising it on the same data used for scoring inflates "
      "apparent performance, so the grid is scored strictly out of sample.",
      "N >= 10/(1-lambda) for the effective sample to exceed the outcome space.",
      "src.mathematics.frequency::run_004"),

    M("M005", "Bayesian Frequency Estimation", A,
      r"P(\theta \mid D) \propto P(D \mid \theta)P(\theta)",
      "A Dirichlet prior conjugates the categorical likelihood, so the posterior is Dirichlet and "
      "the posterior mean shrinks raw frequencies toward the prior mean. The shrinkage weight is "
      "exactly the ratio of prior to total concentration, which makes the amount of 'belief' in the "
      "prior explicit and auditable.",
      "Estimate outcome probabilities with an explicit prior and attach credible intervals.",
      ["Outcomes are conditionally independent given theta",
       "The prior is Dirichlet with known concentration"],
      [("theta", "probability vector"), ("alpha", "Dirichlet concentration"),
       ("D", "observed data"), ("posterior mean", "(alpha_k+n_k)/(A_0+N)")],
      ["Choose a prior concentration",
       "Add observed counts to the prior parameters",
       "Report posterior means and 95% credible intervals per category"],
      "The prior is a modelling choice. With weak priors the result converges to M002; with strong "
      "priors it can mask real imbalance.",
      "Sufficient data to make the posterior interval narrower than the prior.",
      "src.mathematics.frequency::run_005"),

    M("M006", "Dirichlet-Multinomial Modelling", A,
      r"\theta \mid D \sim \mathrm{Dirichlet}(\alpha_1+n_1,\ldots,\alpha_K+n_K)",
      "The Dirichlet-multinomial is the conjugate pair for over-dispersed categorical counts: "
      "unlike the multinomial it allows correlation between category counts through the shared "
      "concentration. Estimating the concentration from the data reveals whether the observed "
      "dispersion exceeds multinomial noise.",
      "Estimate the concentration parameter and test for over-dispersion.",
      ["Counts arise from a Dirichlet-multinomial, not a plain multinomial",
       "Concentration is constant across the sample"],
      [("alpha_0", "total concentration"), ("n_k", "observed counts"),
       ("over-dispersion", "observed vs multinomial variance ratio")],
      ["Estimate alpha_0 by matching the observed variance of counts",
       "Compute posterior means under the fitted concentration",
       "Compare predicted dispersion against the multinomial prediction"],
      "Moment estimation of alpha_0 is noisy when K is small relative to N.",
      "N considerably larger than K.",
      "src.mathematics.frequency::run_006"),

    M("M007", "Laplace Smoothing", A,
      r"\hat{p}_k = \frac{n_k+\alpha}{N+\alpha K}",
      "Additive smoothing prevents zero probabilities, which would make log loss infinite for an "
      "unseen outcome. It is a Bayes posterior mean under a symmetric Dirichlet prior, and its cost "
      "is a small bias toward uniform. The right alpha is the one that minimises out-of-sample log "
      "loss, not the one that looks neatest.",
      "Quantify the log-loss effect of additive smoothing and choose alpha empirically.",
      ["The same alpha applies to every category",
       "The outcome space is complete and fixed"],
      [("alpha", "pseudo-count per category"), ("K", "number of categories"),
       ("N", "observed count total")],
      ["For each alpha in a grid, produce causal probability vectors",
       "Score each with log loss",
       "Report the alpha that minimises out-of-sample loss"],
      "Smoothing cannot create information; it only avoids pathological scores.",
      "Any N; most valuable when some categories are sparse or unseen.",
      "src.mathematics.frequency::run_007"),

    M("M008", "Entropy Analysis", A,
      r"H(X) = -\sum_{k=1}^{K} p_k \log_2 p_k \le \log_2 K",
      "Entropy measures the average surprise of a distribution and therefore the irreducible "
      "uncertainty in the draw. For K=10 the ceiling is log2(10) = 3.3219 bits; a process at that "
      "ceiling is maximally unpredictable in the marginal sense, and any persistent drop below it "
      "signals exploitable imbalance.",
      "Measure and monitor the uncertainty of the outcome distribution over time.",
      ["The entropy estimate is computed from the empirical distribution",
       "Rolling entropy is comparable across windows"],
      [("H", "Shannon entropy in bits"), ("p_k", "probability of outcome k"),
       ("normalised H", "H / log2(K)")],
      ["Estimate the marginal distribution",
       "Compute entropy and normalised entropy",
       "Compare rolling entropy against a simulated uniform process"],
      "Entropy summarises the marginal only; it is blind to serial dependence, which is why M023 "
      "and M031 are needed as well.",
      "N >= 100 for a stable estimate with K=10.",
      "src.mathematics.frequency::run_008"),

    M("M009", "Chi-Square Goodness-of-Fit", A,
      r"\chi^2 = \sum_{k=1}^{K}\frac{(O_k-E_k)^2}{E_k},\quad df = K-1",
      "The Pearson statistic compares observed counts with the counts a hypothesised distribution "
      "predicts. Under the null and with adequate expected counts it is asymptotically chi-square "
      "with K-1 degrees of freedom. Cramer's V rescales it to a 0-1 effect size, which matters "
      "because with large N a negligible imbalance becomes 'significant'.",
      "Test whether the outcome distribution departs from uniform.",
      ["Observations are independent", "Expected count per category >= 5"],
      [("O_k", "observed count"), ("E_k", "expected count under the null"),
       ("df", "degrees of freedom"), ("V", "Cramer's V effect size")],
      ["Compute expected counts N/K",
       "Sum squared standardised deviations",
       "Compare with the chi-square distribution and report V"],
      "Rejection means 'not exactly uniform', not 'predictable'. With thousands of draws a tiny "
      "deviation is detectable and useless.",
      "Expected count >= 5 in every category.",
      "src.mathematics.frequency::run_009", "Pearson (1900)"),

    M("M010", "Categorical Distribution Testing", A,
      r"\chi^2_{\text{indep}} = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}",
      "Beyond the one-sample fit of M009, categorical inference compares two or more empirical "
      "distributions. Comparing early and late periods (or two markets) uses the contingency "
      "chi-square, with the same expected-count caveat and the same need for an effect size.",
      "Test whether the distribution is stable across sub-periods.",
      ["Sub-periods are independent samples", "Expected cell counts are adequate"],
      [("O_ij", "observed cell count"), ("E_ij", "expected under homogeneity"),
       ("df", "(r-1)(c-1)")],
      ["Split the sample into consecutive halves",
       "Build the period-by-category contingency table",
       "Apply the chi-square test and report Cramer's V"],
      "A significant result indicates non-stationarity, which undermines every pooled estimate in "
      "the platform.",
      "At least 5 expected observations per cell.",
      "src.mathematics.frequency::run_010"),

    M("M011", "Jeffreys Prior Estimation", A,
      r"\theta \sim \mathrm{Dirichlet}(\tfrac{1}{2},\ldots,\tfrac{1}{2})",
      "The Jeffreys prior is the square root of the Fisher information determinant; it is the "
      "default objective prior because it is invariant to reparameterisation. For a categorical "
      "model it is Dirichlet(1/2), which is deliberately less smooth than Laplace's Dirichlet(1).",
      "Compare an information-based prior with the flat and Laplace alternatives.",
      ["Jeffreys prior is the appropriate objective choice"],
      [("alpha=1/2", "Jeffreys concentration per category"),
       ("log loss", "scoring rule used to compare priors")],
      ["Compute the posterior mean under alpha=1/2",
       "Do the same under alpha=1",
       "Compare their causal log loss on the same evaluation window"],
      "The difference between priors vanishes as N grows; it matters only in short samples.",
      "Any N; most relevant when categories are sparse.",
      "src.mathematics.frequency::run_011", "Jeffreys (1946)"),

    M("M012", "Hierarchical Bayesian Probability Modelling", A,
      r"\theta_m \sim \mathrm{Dirichlet}(\alpha_0/K,\ldots),\quad \alpha_0 \sim p(\alpha_0)",
      "Partial pooling lets two markets share information about *how much* their probabilities "
      "deviate from uniform, while keeping each market's own probabilities distinct. The "
      "hyperparameter encodes the typical deviation; each market is then shrunk toward uniform by "
      "an amount determined by its own sample size and by the between-market spread.",
      "Estimate a shared concentration across markets and quantify shrinkage per market.",
      ["Markets share a common concentration but not common probabilities"],
      [("alpha_0", "shared Dirichlet concentration"), ("theta_m", "market m probability vector"),
       ("shrinkage", "weight given to the uniform prior")],
      ["Estimate per-market deviations from uniform",
       "Estimate the between-market variance of those deviations",
       "Derive the implied per-market shrinkage weight"],
      "With two markets the hyperparameter is estimated from two observations, which is extremely "
      "weak evidence; the result is reported as a mechanism demonstration.",
      "At least two markets with comparable outcome spaces.",
      "src.mathematics.frequency::run_012"),

    M("M013", "Last Occurrence Analysis", B,
      r"G_{k,t} = t - \max\{i < t : X_i = k\}",
      "Recency, or the 'due number' heuristic, asserts that a category absent for a long time is "
      "more likely to appear. Mathematically it is a claim that the hazard rate increases with "
      "elapsed time; under a constant-probability process the hazard is flat and recency carries no "
      "information whatsoever.",
      "Measure the elapsed gap for every category and test whether recency predicts the next draw.",
      ["The gap is measured in observation counts, not calendar days",
       "Comparisons use the same evaluation window"],
      [("G_k,t", "gap since outcome k last occurred"), ("t", "current observation index"),
       ("hazard", "probability of occurrence given elapsed time")],
      ["Track the last index of each category",
       "Compute the gap vector at each step",
       "Correlate the gap with the realised next outcome and test against a permuted null"],
      "Apparent effects are usually selection artefacts: the category that has been absent longest "
      "is also the empirically rarest.",
      "N >= 10K to give every category a few occurrences.",
      "src.mathematics.recurrence::run_013"),

    M("M014", "Inter-Occurrence Gap Analysis", B,
      r"G_j = T_j - T_{j-1}",
      "The sequence of waiting times between successive appearances of one category is a "
      "renewal process. If draws are independent with probability p, the gaps are geometric with "
      "mean 1/p and variance (1-p)/p^2. The variance-to-mean ratio is therefore a direct test of "
      "the i.i.d. assumption: it should be near 1-p.",
      "Characterise the waiting-time distribution and test it against the geometric null.",
      ["Successive gaps are the object of study",
       "The probability of the category is constant"],
      [("T_j", "index of the j-th occurrence"), ("G_j", "j-th gap"),
       ("VMR", "variance-to-mean ratio of gaps")],
      ["Extract occurrence indices for the category",
       "Form consecutive differences",
       "Compare the observed dispersion with the geometric prediction"],
      "Gaps to the first and last occurrence are censored; ignoring that biases the mean downward.",
      "At least ~20 occurrences of the category.",
      "src.mathematics.recurrence::run_014"),

    M("M015", "Average Recurrence Interval", B,
      r"\bar{G} = \frac{1}{m}\sum_{j=1}^{m} G_j \approx \frac{1}{\hat{p}}",
      "The mean inter-occurrence gap estimates the reciprocal of the category probability. It is "
      "therefore not new information but a differently-shaped view of M002, useful because the "
      "reciprocal scale makes large deviations visually striking - and dangerous for exactly that "
      "reason.",
      "Estimate mean waiting time per category with a confidence interval.",
      ["Gaps are observed without censoring bias",
       "The category probability is stationary"],
      [("G-bar", "mean gap"), ("m", "number of observed gaps"), ("p_hat", "estimated probability")],
      ["Collect gaps per category", "Take the arithmetic mean",
       "Attach a bootstrap confidence interval"],
      "The mean is sensitive to a single very long gap; the median (M016) is more robust.",
      "Multiple occurrences of each category.",
      "src.mathematics.recurrence::run_015"),

    M("M016", "Median Recurrence Interval", B,
      r"\tilde{G} = \mathrm{median}(G_1,\ldots,G_m)",
      "The median waiting time is robust to the heavy right tail that geometric variables always "
      "have. Comparing median with mean gives an immediate diagnostic: for a geometric variable the "
      "mean exceeds the median, and a large discrepancy flags one dominant gap.",
      "Provide a robust central estimate of waiting time.",
      ["Gaps are comparable across occurrences"],
      [("G-tilde", "median gap"), ("skew", "mean/median ratio")],
      ["Compute gaps", "Take the median", "Compare with the mean to assess skew"],
      "With few occurrences the median is unstable and quantised.",
      "At least ~20 gaps.",
      "src.mathematics.recurrence::run_016"),

    M("M017", "Gap Distribution Modelling", B,
      r"P(G=g) = (1-p)^{g-1}p \quad\text{(geometric)}",
      "Fitting a parametric waiting-time model makes the i.i.d. assumption testable: the geometric "
      "distribution is a sharp prediction of independence, and departures from it - a heavier tail "
      "or an excess of very short gaps - indicate clustering or avoidance that a plain frequency "
      "analysis cannot see.",
      "Fit geometric and negative-binomial waiting-time models and compare their fit.",
      ["Waiting times are modelled as discrete",
       "A single parametric family describes the whole sample"],
      [("p", "geometric success probability"), ("NB", "negative binomial over-dispersion parameter"),
       ("AIC", "information criterion for model comparison")],
      ["Build empirical gap histograms per category",
       "Fit geometric and negative binomial models",
       "Compare by AIC and by the predicted probability of the next gap"],
      "Over-dispersion relative to geometric has many causes besides dependence, including "
      "non-stationarity.",
      "Enough occurrences for the histogram to be non-degenerate.",
      "src.mathematics.recurrence::run_017"),

    M("M018", "Survival Analysis", B,
      r"\hat{S}(t)=\prod_{s \le t}\left(1-\frac{d_s}{n_s}\right)",
      "The Kaplan-Meier estimator handles the censoring that gap analysis ignores: the final "
      "incomplete waiting period is information, and discarding it biases estimates. For a discrete "
      "memoryless process the survival curve is geometric, so plotting the empirical curve against "
      "the geometric prediction is a direct test of memorylessness.",
      "Estimate the survival function of the waiting time with censoring handled.",
      ["Censoring is non-informative", "The hazard is estimable from the at-risk counts"],
      [("S(t)", "survival probability past t"), ("d_s", "occurrences at time s"),
       ("n_s", "number at risk at time s")],
      ["For each category build the at-risk and event counts over the gap axis",
       "Compute the product-limit estimate",
       "Overlay the geometric survival curve implied by the marginal probability"],
      "Censoring from the end of the sample is not random with respect to gap length.",
      "Several occurrences per category.",
      "src.mathematics.recurrence::run_018"),

    M("M019", "Hazard Rate Estimation", B,
      r"h(t) = P(T=t \mid T \ge t) = \frac{d_t}{n_t}",
      "The hazard rate answers the only question the 'due number' idea actually poses: does the "
      "probability of an outcome depend on how long it has been absent? A memoryless process has a "
      "constant hazard equal to the category probability; an increasing hazard means numbers do "
      "become 'more due', a decreasing one means clustering.",
      "Estimate the empirical hazard as a function of elapsed time.",
      ["The at-risk set is correctly defined",
       "Hazards are comparable across elapsed-time bins"],
      [("h(t)", "hazard at elapsed time t"), ("d_t", "events at t"), ("n_t", "at risk at t")],
      ["Bin elapsed time since last occurrence",
       "Count events and exposures in each bin",
       "Divide and compare with the constant-hazard expectation"],
      "Late bins rest on few at-risk observations and are extremely noisy.",
      "Enough occurrences to populate several hazard bins.",
      "src.mathematics.recurrence::run_019"),

    M("M020", "Hot and Cold Frequency Analysis", B,
      r"z_k = \frac{n_k - N/K}{\sqrt{N \cdot \frac{1}{K}(1-\frac{1}{K})}}",
      "Standardising counts converts 'hot' and 'cold' from impressions into z-scores. The critical "
      "question is not whether a category is currently hot but whether hotness persists: a "
      "genuinely biased die produces persistent z-scores, while a fair die produces a rotating cast "
      "of temporarily extreme categories.",
      "Identify statistically extreme categories and test whether extremeness persists.",
      ["Counts are multinomial", "The z-score is a large-sample approximation"],
      [("z_k", "standardised deviation"), ("N", "total observations"), ("K", "categories")],
      ["Compute z per category",
       "Split the sample into consecutive periods",
       "Correlate hotness in one period with hotness in the next"],
      "Z-scores computed on the full sample cannot be used to predict that same sample; the "
      "persistence test uses only forward-looking splits.",
      "Expected count >= 5 per category.",
      "src.mathematics.recurrence::run_020"),

    M("M021", "Rolling Recency Weighting", B,
      r"\hat{p}_k(t; W, \lambda)=\frac{\sum_{i=t-W+1}^{t}\lambda^{t-i}\mathbf{1}[X_i=k]}{\sum_j(\cdot)}",
      "Combining a hard window with exponential decay inside the window gives two independent "
      "controls: how far back to look, and how sharply to discount within that horizon. The pair is "
      "selected on out-of-sample loss, because fitting it in-sample guarantees a spurious optimum.",
      "Tune window length and decay jointly under strict out-of-sample evaluation.",
      ["Both hyperparameters are constant over the evaluation",
       "Selection uses only pre-cutoff data"],
      [("W", "window length"), ("lambda", "within-window decay"),
       ("grid", "candidate (W, lambda) pairs")],
      ["Enumerate the hyperparameter grid",
       "Produce causal predictions for each",
       "Select by out-of-sample log loss and report the full grid"],
      "Grid search over two parameters on a few thousand observations invites selection bias; the "
      "reported loss is the selected one and is therefore optimistic.",
      "N large enough that every grid point has a meaningful evaluation window.",
      "src.mathematics.recurrence::run_021"),

    M("M022", "Change-Point Detection", B,
      r"S_t = \max\left(0, S_{t-1} + (X_t - \mu_0)\right)",
      "A change point is a time at which the data-generating distribution changes. CUSUM "
      "accumulates deviations from a reference mean and alarms when the accumulation exceeds a "
      "threshold; binary segmentation applies the same idea recursively. For these markets the "
      "interesting question is whether any detected structural break is followed by a genuinely "
      "different distribution.",
      "Detect candidate structural breaks and evaluate their consequences.",
      ["The pre-break and post-break segments are internally homogeneous",
       "The reference distribution is correctly specified"],
      [("S_t", "CUSUM statistic"), ("mu_0", "reference level"),
       ("threshold", "alarm level"), ("break", "estimated change location")],
      ["Build an indicator series for the outcome of interest",
       "Run CUSUM and record alarm times",
       "Validate each candidate break by comparing pre- and post-segment distributions"],
      "CUSUM is sensitive to gradual drift, not only to sharp breaks, and with many categories it "
      "generates alarms readily. Multiple testing across categories must be corrected.",
      "Several hundred observations on each side of a candidate break.",
      "src.mathematics.recurrence::run_022", "Page (1954)"),
]
