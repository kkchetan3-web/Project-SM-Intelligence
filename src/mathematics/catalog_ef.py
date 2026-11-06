"""Documentation records for Methods 47-72 (Categories E and F)."""

from __future__ import annotations

from src.mathematics.catalog_ab import M

E = "E - Number Theory and Transformations"
F = "F - Randomness and Statistical Structure"

METHODS_EF = [
    M("M047", "Modular Arithmetic", E,
      r"r = n \bmod m",
      "Reducing outcomes modulo m folds the outcome space into residue classes. For a fair draw "
      "each residue class should receive a predictable share (equal when m divides K, otherwise "
      "differing by at most one observation), so residues give a compact, low-dimensional test of "
      "structure that is more statistically powerful than a full 10-category test.",
      "Test whether residue classes are uniformly represented.",
      ["The underlying integer representation is meaningful",
       "Residue classes are exhaustive and mutually exclusive"],
      [("r", "residue"), ("n", "numeric outcome"), ("m", "modulus")],
      ["Choose moduli (2, 3, 5, 7)",
       "Map each outcome to its residue",
       "Test the residue distribution with exact binomial or chi-square methods"],
      "Modular folding throws away information; a rejection here does not identify which categories "
      "drive the imbalance.",
      "Enough observations for the smallest residue class to have >= 5 expected counts.",
      "src.mathematics.number_theory::run_047"),

    M("M048", "Digital Root Analysis", E,
      r"\mathrm{dr}(n) = 1 + ((n-1) \bmod 9)",
      "The digital root is the iterated digit sum, collapsing any integer to 1-9. It is the "
      "base-10 manifestation of modular arithmetic mod 9, so its distribution is tightly constrained "
      "and easy to test - and any departure from the constraint signals a parsing or data error "
      "rather than a market phenomenon.",
      "Characterise the digital-root distribution and use it as a data-integrity probe.",
      ["Values are stated in base 10", "Digital root is deterministic given the value"],
      [("dr(n)", "digital root in 1-9"), ("n", "integer value")],
      ["Compute the iterated digit sum for each outcome",
       "Tabulate the distribution",
       "Compare with the theoretical distribution implied by the outcome space"],
      "Digital roots of a uniform 0-9 draw are not uniform themselves because 0 maps to 0 and 9 maps "
      "to 9; the theoretical comparison must account for that.",
      "Any non-empty sample.",
      "src.mathematics.number_theory::run_048"),

    M("M049", "Digit Sum Distribution", E,
      r"S = d_1 + d_2 + d_3,\quad d_i \in \{0,\ldots,9\}",
      "For a three-digit panel the digit sum ranges over 0-27 with a triangular-ish distribution "
      "concentrated near the middle, exactly the convolution of three uniform discrete variables. "
      "Comparing the empirical sum distribution with that convolution tests whether panel digits are "
      "independently and uniformly generated.",
      "Test whether panel digit sums match the theoretical convolution.",
      ["Panel digits are independent and uniform under the null",
       "The panel is exactly three digits"],
      [("S", "digit sum 0-27"), ("d_i", "i-th digit of the panel")],
      ["Extract the three digits of every open and close panel",
       "Compute the sum",
       "Compare the empirical distribution with the exact convolution"],
      "Panna conventions can include repeated or 'double' panels that some operators weight "
      "differently; the theoretical baseline assumes plain uniform digits.",
      "Panels must be available for the market.",
      "src.mathematics.number_theory::run_049"),

    M("M050", "Digit Difference Analysis", E,
      r"D = |d_1 - d_2|,\ldots",
      "Differences between digit positions summarise the internal geometry of a panel. Under uniform "
      "independent digits the difference distribution is exactly computable, so systematic deviations "
      "indicate non-uniform or dependent digits.",
      "Test whether inter-digit differences match the independent-uniform prediction.",
      ["Digits are exchangeable under the null", "Panels are three digits"],
      [("D", "absolute difference between positions"), ("d_i", "digit at position i")],
      ["Compute the six pairwise absolute differences per panel",
       "Tabulate their distribution",
       "Compare with the exact theoretical distribution"],
      "Differences are highly dependent within a panel, so the tests are not independent and must be "
      "interpreted jointly.",
      "Panels available.",
      "src.mathematics.number_theory::run_050"),

    M("M051", "Complementary Digit Analysis", E,
      r"d' = 9 - d",
      "The decimal complement maps each digit to its 'partner' summing to nine. Some players treat "
      "complements as related; the statistical claim is a negative autocorrelation in the "
      "complement variable. It is testable and, so far, consistently unsupported.",
      "Test whether complements show elevated or depressed frequency.",
      ["Complement is an involution on 0-9", "The mapping is fixed a priori"],
      [("d'", "complement digit"), ("freq", "empirical frequency of the complement class")],
      ["Replace each digit by 9-d",
       "Compare the frequency of the original and complement classes",
       "Test symmetry with an exact binomial test"],
      "Complement symmetry is expected for any symmetric process, so a non-significant result is the "
      "informative outcome; a significant one usually indicates asymmetry elsewhere.",
      "Any non-empty sample.",
      "src.mathematics.number_theory::run_051"),

    M("M052", "Reversal Relationship Analysis", E,
      r"\mathrm{rev}(d_1d_2d_3) = d_3d_2d_1",
      "Reversal preserves the digit multiset and therefore the ank, changing only the order. If "
      "panels were generated without order structure, a panel and its reversal should appear with "
      "comparable frequency; if the operator ranks panels, one orientation may dominate.",
      "Test whether panel orientation carries a systematic asymmetry.",
      ["Fixed-width strings are preserved through storage",
       "Reversal is its own inverse"],
      [("rev(x)", "reversed digit sequence"), ("orientation", "palindrome / ascending / descending class")],
      ["Reverse each panel as a string",
       "Classify orientation",
       "Test the orientation distribution against the combinatorial expectation"],
      "Palindrome panels are their own reversal and must be counted once; failing to do so inflates "
      "apparent reversal pairs.",
      "Panels available.",
      "src.mathematics.number_theory::run_052"),

    M("M053", "Parity Analysis", E,
      r"P(\text{even}) = \sum_{k \text{ even}} p_k",
      "Parity is the coarsest non-trivial partition of a digit space and therefore the most "
      "statistically powerful: pooling five categories per side gives large expected counts even in "
      "short samples. It is also the natural first target for a binary classifier.",
      "Test the even/odd balance and the persistence of any imbalance.",
      ["Parity is a deterministic function of the outcome",
       "Even and odd classes partition the space"],
      [("p_even", "probability of an even outcome"), ("n_even", "count of even outcomes")],
      ["Map each outcome to its parity",
       "Test the proportion against 0.5",
       "Test run structure and persistence separately"],
      "A significant imbalance over years is more likely to indicate a biased mechanism or a data "
      "artefact than an exploitable edge.",
      "Any non-empty sample.",
      "src.mathematics.number_theory::run_053"),

    M("M054", "Prime and Composite Classification", E,
      r"\mathbb{P} = \{2,3,5,7\},\quad n \in \mathbb{P}?",
      "On the digit space 0-9 the primes are 2, 3, 5 and 7, giving a natural 4/6 partition. The test "
      "is a straightforward binomial comparison, useful as a second coarse partition alongside parity "
      "and mod-5 residues.",
      "Test whether prime-class outcomes occur at their theoretical rate.",
      ["Primality is well defined on integers", "The partition is fixed a priori"],
      [("pi", "theoretical prime share (0.4 on 0-9)"), ("n_prime", "observed prime count")],
      ["Classify each outcome",
       "Compute the observed prime share",
       "Test against 0.4 with an exact binomial test"],
      "0 and 1 are neither prime nor composite, which matters when the outcome space includes them; "
      "the implementation states the convention used.",
      "Any non-empty sample.",
      "src.mathematics.number_theory::run_054"),

    M("M055", "Combinatorial Probability Analysis", E,
      r"|\Omega| = K,\quad P(A) = \frac{|A|}{|\Omega|}",
      "Combinatorial probability derives a distribution from the structure of the sample space rather "
      "than from observation. For a single digit the space is ten equally likely outcomes; for a panel "
      "it is a thousand. These theoretical distributions are the reference against which every "
      "empirical result here is measured.",
      "Derive theoretical distributions and compare them with observation.",
      ["Each elementary outcome is equally likely under the null",
       "The sample space is fully enumerated"],
      [("Omega", "sample space"), ("|A|", "number of favourable outcomes")],
      ["Enumerate the sample space",
       "Count the outcomes satisfying the event",
       "Compare the theoretical probability with the empirical frequency"],
      "The assumed equiprobability is exactly the hypothesis under test, so this method supplies the "
      "null and cannot confirm it.",
      "A fully specified sample space.",
      "src.mathematics.number_theory::run_055"),

    M("M056", "Permutation and Combination Analysis", E,
      r"{}^nP_r=\frac{n!}{(n-r)!},\qquad {}^nC_r=\frac{n!}{r!(n-r)!}",
      "Ordered arrangements and unordered selections generate different counts, which matters when "
      "the panel orientation is or is not treated as meaningful. Repeated digits reduce the count of "
      "distinct permutations, so the multinomial coefficient is the correct tool.",
      "Enumerate arrangement counts and test orientation-sensitive distributions.",
      ["Permutations count order, combinations do not",
       "Repeated digits are handled by the multinomial coefficient"],
      [("nPr", "ordered arrangements"), ("nCr", "unordered selections"),
       ("multinomial", "n!/(n1!n2!n3!)")],
      ["Enumerate digit multisets",
       "Compute the number of distinct arrangements of each",
       "Compare the observed orientation frequencies with the weighted expectation"],
      "Panel providers may rank panels non-uniformly by convention, so a departure from equiprobability "
      "may reflect operator ranking rather than draw physics.",
      "Panels available.",
      "src.mathematics.number_theory::run_056"),

    M("M057", "Numerical Distance Analysis", E,
      r"d_t = |x_t - x_{t-1}|",
      "Absolute change between consecutive outcomes measures how far the process moves each step. For "
      "an i.i.d. uniform digit sequence the distribution of the change is exactly known - it is "
      "triangular on 0-9 - so comparing against that distribution is a sharp test of independence.",
      "Compare the step-size distribution with the independence prediction.",
      ["The numeric encoding has meaning", "Steps are comparable across the sample"],
      [("d_t", "absolute change"), ("distribution", "theoretical triangular law")],
      ["Compute consecutive absolute differences",
       "Tabulate the distribution",
       "Compare with the exact i.i.d. prediction using a chi-square test"],
      "A bounded discrete outcome cannot move by more than K-1, so the distribution is truncated; the "
      "theoretical comparison must respect the boundary.",
      "A meaningful numeric encoding.",
      "src.mathematics.number_theory::run_057"),

    M("M058", "Pairwise Digit Association", E,
      r"\chi^2 = \sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}",
      "Testing whether digit positions are independent inside a panel is a two-way contingency "
      "problem. It matters because a panel generated as a single ranked object will show dependence "
      "between positions, while independently drawn digits will not.",
      "Test the independence of digit positions within panels.",
      ["Panels are three independent digits under the null"],
      [("O_ij", "joint count of digits i and j"), ("E_ij", "product of marginal shares")],
      ["Build the 10x10 joint table for position pairs",
       "Compute the chi-square statistic and Cramer's V",
       "Assess with a permutation null to avoid sparse-cell problems"],
      "With 100 cells and a few thousand panels the chi-square approximation is adequate but the "
      "effect size is what determines whether the dependence is usable.",
      "Panels available, ideally several thousand.",
      "src.mathematics.number_theory::run_058"),

    M("M059", "Hamming Distance Analysis", E,
      r"d_H(x,y)=\sum_{i}\mathbf{1}[x_i \neq y_i]",
      "Hamming distance counts positional disagreements between two equal-length digit strings. For "
      "consecutive panels it measures how much the panel changes, and its distribution under "
      "independence is exactly computable for uniform digits.",
      "Characterise how consecutive panels differ.",
      ["Strings are equal length with fixed positions",
       "Positions are comparable across panels"],
      [("d_H", "number of differing positions"), ("x, y", "two equal-length strings")],
      ["Take consecutive panel pairs",
       "Count differing positions",
       "Compare with the independence prediction"],
      "Hamming distance treats all positions as equally meaningful, which the panel ranking convention "
      "may not support.",
      "Panels available.",
      "src.mathematics.number_theory::run_059"),

    M("M060", "Residue Distribution Analysis", E,
      r"c_k = |\{t : x_t \equiv k \pmod m\}|",
      "Residue classes offer a graded family of partitions: with m=2 you get parity, with m=5 you get "
      "a five-way split, with m=10 the full space. Testing across the family shows whether apparent "
      "structure is consistent at every resolution or appears at exactly one, which is the signature "
      "of a chance finding.",
      "Test residue distributions across a family of moduli and check consistency.",
      ["Residues are exhaustive for each modulus", "Tests across moduli are correlated"],
      [("c_k", "count in residue class k"), ("m", "modulus")],
      ["For each modulus build the class counts",
       "Test each for uniformity",
       "Check whether rejections are consistent across moduli and correct for multiplicity"],
      "The tests are highly dependent across moduli, so naive multiple-testing correction is "
      "conservative while treating them as independent would be anti-conservative.",
      "Any non-empty sample.",
      "src.mathematics.number_theory::run_060"),

    M("M061", "Runs Test", F,
      r"R = 1 + \sum_{t=2}^{N}\mathbf{1}[S_t \neq S_{t-1}]",
      "A run is a maximal stretch of the same binary state. Too few runs indicates clustering, too "
      "many indicates alternation, and the null distribution is approximately normal with known mean "
      "and variance. It is the classic test of serial randomness for a binary sequence.",
      "Test the binary sequence for clustering or alternation.",
      ["The binary categorisation is fixed a priori", "N is large enough for the normal approximation"],
      [("R", "number of runs"), ("n_1, n_2", "counts in each state"),
       ("E[R]", "expected runs under randomness")],
      ["Form the binary sequence",
       "Count runs",
       "Compute the z-statistic against the randomness expectation"],
      "The binary split discards most of the information in a 10-category sequence.",
      "At least ~20 observations in each state.",
      "src.mathematics.randomness::run_061", "Wald & Wolfowitz (1940)"),

    M("M062", "Ljung-Box Test", F,
      r"Q=n(n+2)\sum_{k=1}^{h}\frac{\hat{\rho}_k^2}{n-k}",
      "Ljung-Box jointly tests whether the first h autocorrelations are zero. It is more powerful than "
      "examining each lag separately, and it is the standard residual diagnostic for whether a fitted "
      "model has absorbed the dependence.",
      "Jointly test autocorrelation up to a chosen lag.",
      ["The series is stationary", "The chi-square approximation with h degrees of freedom is adequate"],
      [("Q", "Ljung-Box statistic"), ("rho_k", "lag-k autocorrelation"),
       ("h", "maximum lag tested"), ("n", "series length")],
      ["Choose the lag horizon",
       "Compute autocorrelations",
       "Form Q and compare with the chi-square distribution on h degrees of freedom"],
      "Applied to a categorical indicator the statistic is only approximately chi-square; permutation "
      "calibration is used alongside for safety.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_062", "Ljung & Box (1978)"),

    M("M063", "Permutation Testing", F,
      r"p = \frac{1+\sum_{b=1}^{B}\mathbf{1}[T_b \ge T_{\text{obs}}]}{B+1}",
      "A permutation test builds the null distribution of a statistic by rearranging the observed "
      "values, which is valid whenever the null corresponds to exchangeability. It makes no "
      "distributional assumption, which is exactly what a 10-category discrete process needs.",
      "Obtain valid p-values without distributional assumptions.",
      ["Observations are exchangeable under the null",
       "The statistic is computed identically on permuted data"],
      [("T_obs", "observed statistic"), ("T_b", "statistic on permutation b"),
       ("B", "number of permutations"), ("p", "empirical p-value")],
      ["Compute the observed statistic",
       "Generate B random permutations and recompute",
       "Compute the empirical p-value with the +1 correction"],
      "Permutation destroys only the structure the null asserts; if the series has trend, a plain "
      "permutation is the wrong null.",
      "B large enough to resolve the p-value of interest.",
      "src.mathematics.randomness::run_063"),

    M("M064", "Bootstrap Analysis", F,
      r"\mathrm{CI}_{1-\alpha} = [q_{\alpha/2}(\hat{\theta}^*), q_{1-\alpha/2}(\hat{\theta}^*)]",
      "The bootstrap estimates sampling variability by resampling the observed data. For time series "
      "the naive i.i.d. bootstrap understates variability when observations are dependent, so the "
      "moving-block variant is used throughout this platform.",
      "Attach confidence intervals to frequency and recurrence estimates.",
      ["The resampling scheme reproduces the dependence structure",
       "The statistic is smooth in the data"],
      [("theta*", "bootstrap replicate"), ("B", "number of resamples"), ("block", "block length")],
      ["Choose a resampling scheme (moving block)",
       "Generate B resamples and recompute the statistic",
       "Report percentile confidence intervals"],
      "Block bootstrap requires a block length long enough to span the dependence, which is unknown "
      "and must be varied as a sensitivity check.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_064", "Efron (1979)"),

    M("M065", "Monte Carlo Simulation", F,
      r"\hat{P}(T \ge t) = \frac{1}{M}\sum_{m=1}^{M}\mathbf{1}[T_m \ge t]",
      "Monte Carlo simulation generates data from a fully specified null process and compares the "
      "resulting statistic distribution with the observed value. It is the reference implementation of "
      "'what would randomness look like', and every p-value reported here has a simulation check.",
      "Compare observed statistics with a simulated random process.",
      ["The simulation implements the intended null exactly",
       "The statistic is computed identically on simulated and real data"],
      [("M", "number of simulated sequences"), ("T_m", "statistic from simulation m")],
      ["Specify the null generating process",
       "Simulate M sequences of the same length",
       "Compare the observed statistic with the simulated distribution"],
      "Simulating the wrong null is worse than not simulating; the platform reports the null that was "
      "simulated so the choice can be challenged.",
      "Enough compute for M sequences.",
      "src.mathematics.randomness::run_065"),

    M("M066", "Sample Entropy", F,
      r"SampEn(m,r)=-\ln\frac{A}{B}",
      "Sample entropy measures the probability that two similar patterns of length m remain similar "
      "when extended by one. Low values indicate regularity; high values indicate unpredictability. "
      "For categorical data the tolerance r is replaced by exact matching, which the implementation "
      "handles explicitly.",
      "Quantify sequence regularity without bias from self-matches.",
      ["Pattern length and tolerance are fixed a priori", "The series is long relative to the pattern length"],
      [("m", "embedding dimension"), ("A", "extended matches"), ("B", "matches at length m")],
      ["Form length-m patterns",
       "Count matches with and without extension",
       "Compute the negative log ratio"],
      "Matching in a 10-symbol alphabet is rare, so A and B can be zero, in which case entropy is "
      "undefined rather than infinite; the implementation reports that case honestly.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_066", "Richman & Moorman (2000)"),

    M("M067", "Approximate Entropy", F,
      r"ApEn(m,r)=\Phi^m(r)-\Phi^{m+1}(r)",
      "Approximate entropy is the predecessor of sample entropy. It counts self-matches, which biases "
      "it toward reporting more regularity than exists, but it is retained because the discrepancy "
      "between the two is itself a useful diagnostic.",
      "Measure sequence regularity with the original statistic.",
      ["Pattern length and tolerance are fixed a priori"],
      [("Phi^m", "mean log match fraction at length m"), ("m", "embedding dimension")],
      ["Count matches at length m and m+1 including self-matches",
       "Average the log match fractions",
       "Take the difference"],
      "The self-match bias makes ApEn systematically lower than SampEn; comparing the two reveals "
      "how much of the apparent regularity is an artefact.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_067", "Pincus (1991)"),

    M("M068", "Hurst Exponent Analysis", F,
      r"\mathbb{E}\left[\frac{R(n)}{S(n)}\right] \sim n^{H}",
      "The Hurst exponent describes long-range dependence: H=0.5 is a random walk, H>0.5 persistent, "
      "H<0.5 anti-persistent. Rescaled-range analysis is noisy on short samples, so the estimate is "
      "reported with a simulation-based reference band for the sample size actually available.",
      "Test for long-range dependence and interpret against a simulated null.",
      ["The series is long enough for stable range statistics",
       "The numeric encoding is meaningful"],
      [("H", "Hurst exponent"), ("R(n)", "range of partial sums"), ("S(n)", "standard deviation")],
      ["Form partial sums of deviations from the mean",
       "Compute the rescaled range at several scales",
       "Regress log(R/S) on log(n) and compare H with a simulated band"],
      "R/S analysis is severely biased on short series and can produce H far from 0.5 for pure noise; "
      "the simulated band is not optional.",
      "At least several hundred observations.",
      "src.mathematics.randomness::run_068", "Hurst (1951)"),

    M("M069", "Hidden Markov Models", F,
      r"P(X_{1:T},Z_{1:T}) = \pi_{z_1}b_{z_1}(x_1)\prod_{t=2}^{T}A_{z_{t-1},z_t}b_{z_t}(x_t)",
      "An HMM posits that observed draws are emitted by an unobserved state that itself follows a "
      "Markov chain. It generalises the plain Markov model in M023 and can capture regime switching "
      "that a homogeneous chain cannot - at the cost of identifiability issues and local optima.",
      "Fit latent-regime models and test their out-of-sample value.",
      ["The latent state is discrete and small", "Emissions depend only on the current state"],
      [("Z_t", "latent state"), ("A", "state transition matrix"), ("b", "emission distribution"),
       ("pi", "initial state distribution")],
      ["Fit models with increasing state counts",
       "Initialise from multiple random starts to avoid local optima",
       "Compare out-of-sample log loss against the plain Markov model"],
      "HMM fitting is non-convex; a good in-sample likelihood is weak evidence, and extra states "
      "nearly always improve it.",
      "Several hundred observations per state.",
      "src.mathematics.randomness::run_069", "Baum & Petrie (1966)"),

    M("M070", "Bayesian Change-Point Modelling", F,
      r"P(\tau \mid x_{1:T}) \propto P(x_{1:\tau})P(x_{\tau+1:T})P(\tau)",
      "A Bayesian change-point model places a prior over the location of a structural break and "
      "returns a posterior distribution over break positions rather than a single point. That "
      "honesty about location uncertainty is the main advantage over CUSUM.",
      "Estimate the posterior distribution of change-point locations.",
      ["Segments are independent given the break location", "A conjugate prior is available"],
      [("tau", "change-point index"), ("prior", "geometric or uniform over locations")],
      ["Score every candidate break by the marginal likelihood of the two segments",
       "Combine with the prior",
       "Normalise to a posterior and report the credible set"],
      "Exact posterior computation over T candidate positions is quadratic in T; the implementation "
      "uses a coarse grid and says so.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_070"),

    M("M071", "Wald-Wolfowitz Runs Analysis", F,
      r"E[R] = \frac{2n_1n_2}{n}+1,\quad \mathrm{Var}(R)=\frac{2n_1n_2(2n_1n_2-n)}{n^2(n-1)}",
      "This is the formal statement of the runs test with its exact expectation and variance. It is "
      "implemented separately from M061 so that the two can be cross-checked and so that the evidence "
      "is not double-counted in the summary.",
      "Provide the closed-form runs test and cross-validate M061.",
      ["The binary sequence is exchangeable under the null", "The normal approximation is adequate"],
      [("R", "observed runs"), ("E[R]", "expected runs"), ("n_1, n_2, n", "state counts and total")],
      ["Count runs in the binary sequence",
       "Compute the theoretical mean and variance",
       "Standardise and obtain a p-value"],
      "Reports the same evidence as M061; the platform flags this so the two are not counted as two "
      "independent findings.",
      "At least ~20 observations per state.",
      "src.mathematics.randomness::run_071", "Wald & Wolfowitz (1940)"),

    M("M072", "Block Bootstrap Analysis", F,
      r"\hat{\theta}^*_b \text{ from blocks } (x_{i},x_{i+1},\ldots,x_{i+\ell-1})",
      "The moving-block bootstrap resamples contiguous blocks rather than individual observations, "
      "preserving short-range dependence. Varying the block length is the sensitivity analysis that "
      "shows how much the conclusions depend on the assumed dependence scale.",
      "Estimate uncertainty under dependence and test block-length sensitivity.",
      ["Dependence has a finite range smaller than the block",
       "Blocks are long enough to capture it"],
      [("ell", "block length"), ("theta*", "replicate statistic"), ("B", "resamples")],
      ["Choose a block length",
       "Draw overlapping blocks and concatenate",
       "Recompute the statistic and vary the block length as a check"],
      "If the dependence range exceeds the block length the interval is too narrow, and there is no "
      "direct diagnostic for that from the data alone.",
      "Several hundred observations.",
      "src.mathematics.randomness::run_072", "Kunsch (1989)"),
]
